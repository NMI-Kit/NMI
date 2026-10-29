"""The prompt in Hebrew and in English (task 17): the translated files keep the structure of the Arabic ones, and every number.

The Arabic files are the original and are never changed by the translations. Run:
    python -B -m unittest discover -s tests/offline
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))

import build_kit  # noqa: E402

CURRICULUM = ROOT / 'curriculum' / 'math'
KIT = ROOT / 'kit'
LANGUAGES = ('he', 'en')
ARABIC_LETTER = re.compile(r'[؀-ۿ]')
HEBREW_LETTER = re.compile(r'[֐-׿]')


def read(path):
    return path.read_text(encoding='utf-8').replace('\r\n', '\n')


def numbers(text):
    return re.findall(r'\d+(?:[.,]\d+)?', text)


def without_grades(text):
    """the Arabic says a grade with a word, English may say "grade 10" with a digit"""
    text = re.sub(r'\b[Gg]rades?\s+\d+(?:\s+and\s+\d+)?', 'grade', text)
    return re.sub(r'\b(?:degree|power)\s+\d+\b', 'degree', text)


def level_kind(line):
    if line.strip() == '':
        return 'blank'
    m = re.match(r'^(#{1,4}) (m\d+-\d+-\d+)?', line)
    if m:
        return f'{m.group(1)}{" " + m.group(2) if m.group(2) else ""}'
    m = re.match(r'^(\s*)- \*\*', line)
    if m:
        return f'{len(m.group(1))}-bold'
    m = re.match(r'^(\s*)- ', line)
    if m:
        return f'{len(m.group(1))}-dash'
    return 'text'


def level_files():
    return sorted(CURRICULUM.glob('grade*/[345]units.md'))


def translated(path, language):
    return path.with_name(path.name[:-3] + f'.{language}.md')


class TranslatedFilesTests(unittest.TestCase):
    def test_there_are_nine_levels_nine_example_files_and_a_patterns_file_in_each_language(self):
        self.assertEqual(len(level_files()), 9)
        for language in LANGUAGES:
            for path in level_files():
                self.assertTrue(translated(path, language).is_file(), translated(path, language))
                examples = path.parent / 'examples' / path.name
                self.assertTrue(translated(examples, language).is_file(), translated(examples, language))
            self.assertTrue((CURRICULUM / f'bagrut_patterns.{language}.md').is_file())
            self.assertTrue((KIT / f'base_prompt.{language}.txt').is_file())
            self.assertTrue((KIT / f'prompt_texts.{language}.json').is_file())
        self.assertTrue((CURRICULUM / 'glossary.md').is_file())

    def test_the_translated_files_do_not_match_the_patterns_of_the_arabic_ones(self):
        # the lab version and the builder read *units.md: the translated names (3units.he.md) are not picked up by them
        names = {p.name for p in CURRICULUM.glob('grade10/*units.md')}
        self.assertEqual(names, {'3units.md', '4units.md', '5units.md'})
        self.assertEqual({p.name for p in CURRICULUM.glob('grade10/*units.he.md')}, {'3units.he.md', '4units.he.md', '5units.he.md'})

    def test_each_level_has_the_same_headings_bullets_and_numbers_as_the_arabic_file(self):
        for path in level_files():
            arabic = read(path).rstrip('\n').split('\n')
            for language in LANGUAGES:
                other = read(translated(path, language)).rstrip('\n').split('\n')
                where = f'{path.relative_to(CURRICULUM)} {language}'
                self.assertEqual([level_kind(x) for x in other], [level_kind(x) for x in arabic], where)
                body = lambda lines: '\n'.join(x for x in lines if not x.startswith('#'))
                expected = numbers(body(arabic))
                got = numbers(without_grades(body(other)) if language == 'en' else body(other))
                self.assertEqual(got, expected, where)

    def test_every_example_has_the_same_numbers_in_the_same_order_and_the_same_parts(self):
        count = 0
        for path in level_files():
            examples = path.parent / 'examples' / path.name

            def blocks(file):
                parts = re.split(r'^## (m\d+-\d+-\d+)[^\n]*\n', read(file), flags=re.M)
                return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]

            arabic = blocks(examples)
            for language in LANGUAGES:
                other = blocks(translated(examples, language))
                where = f'{examples.relative_to(CURRICULUM)} {language}'
                self.assertEqual([i for i, _ in other], [i for i, _ in arabic], where)
                for (topic, ar_text), (_, tr_text) in zip(arabic, other):
                    shown = without_grades(tr_text) if language == 'en' else tr_text
                    self.assertEqual(numbers(shown), numbers(ar_text), f'{where} {topic}')
                    self.assertEqual(len(re.findall(r'^\*\*', tr_text, re.M)), len(re.findall(r'^\*\*', ar_text, re.M)), f'{where} {topic}')
                    self.assertEqual(len(tr_text.split('\n\n')), len(ar_text.split('\n\n')), f'{where} {topic}')
                    count += 1
        self.assertEqual(count, 202)  # 101 examples in two languages

    def test_the_patterns_have_the_same_sections_tables_and_numbers(self):
        arabic = read(CURRICULUM / 'bagrut_patterns.md')
        arabic = arabic[arabic.index('## قواعد عامة'):].replace('البجروت', 'الامتحان').replace('بجروت', 'امتحان')
        for language in LANGUAGES:
            other = read(CURRICULUM / f'bagrut_patterns.{language}.md')
            other = other[other.index('## '):]
            kinds = lambda text: [re.sub(r'^(#{1,4}) .*', r'\1', line) if line.startswith('#') else
                                  ('row%d' % line.count('|') if line.startswith('|') else
                                   ('blank' if not line.strip() else re.match(r'^(\s*)(- |\d+\. )?', line).group(0).strip()[:2] + str(len(line) - len(line.lstrip()))))
                                  for line in text.rstrip('\n').split('\n')]
            self.assertEqual(kinds(other), kinds(arabic), language)
            self.assertEqual(numbers(without_grades(other) if language == 'en' else other), numbers(arabic), language)

    def test_the_base_prompt_has_the_same_lines_headings_and_bullets(self):
        arabic = read(KIT / 'base_prompt.txt').strip().split('\n')

        def kind(line):
            if not line.strip():
                return 'blank'
            if line.startswith('== '):
                return 'heading'
            return 'sub' if re.match(r'^\s+\S', line) else ('dash' if line.startswith('- ') else 'text')

        for language in LANGUAGES:
            other = read(KIT / f'base_prompt.{language}.txt').strip().split('\n')
            self.assertEqual(len(other), len(arabic), language)
            self.assertEqual([kind(x) for x in other], [kind(x) for x in arabic], language)
            self.assertEqual(numbers(other[0]), numbers(arabic[0]))
            # the same numbers in the rules: 5 lines, 3 times, 100, ... (the order of the numbers is the order of the lines)
            # (the template line of the grade says [10 / 11 / 12] in Arabic and the letters of the grades in Hebrew)
            skip = lambda lines: [x for x in lines if not re.match(r'^(الصف|כיתה|Grade): \[', x)]
            self.assertEqual(numbers('\n'.join(skip(other))), numbers('\n'.join(skip(arabic))), language)

    def test_no_arabic_letter_in_the_translated_files_and_the_hebrew_only_in_parentheses_of_the_english(self):
        files = [KIT / f'base_prompt.{lang}.txt' for lang in LANGUAGES] + [KIT / f'prompt_texts.{lang}.json' for lang in LANGUAGES]
        files += [CURRICULUM / f'bagrut_patterns.{lang}.md' for lang in LANGUAGES]
        for path in level_files():
            for lang in LANGUAGES:
                files += [translated(path, lang), translated(path.parent / 'examples' / path.name, lang)]
        for path in files:
            text = read(path)
            self.assertIsNone(ARABIC_LETTER.search(text), path.name)
        for path in files:
            if path.name.endswith('.en.md') or path.name.endswith('.en.txt') or path.name.endswith('.en.json'):
                text = read(path)
                # a Hebrew term in an English file is in parentheses (or is the "שאלון" / "יח"ל" of a title): never a whole Hebrew sentence
                for run in re.findall(r'[^\n]*', text):
                    outside = re.sub(r'\([^()]*[֐-׿][^()]*\)', '', run)
                    outside = outside.replace('יח"ל', '').replace('תשפ"ז', '')
                    self.assertIsNone(HEBREW_LETTER.search(outside), f'{path.name}: {run[:80]}')

    def test_the_glossary_has_the_three_languages_and_the_terms_of_the_translations(self):
        text = read(CURRICULUM / 'glossary.md')
        rows = [line for line in text.split('\n') if line.startswith('| ') and not line.startswith('| Arabic') and not line.startswith('|---')]
        self.assertGreater(len(rows), 150)
        for row in rows:
            cells = [c.strip() for c in row.strip('|').split('|')]
            self.assertEqual(len(cells), 3, row)
            self.assertRegex(cells[0], r'[؀-ۿ]|sin', row)
            self.assertRegex(cells[1], r'[֐-׿]|sin', row)
            self.assertTrue(re.search(r'[A-Za-z]', cells[2]), row)
        # a few terms of the Ministry that the translations use
        for term in ('הסתברות', 'התפלגות נורמלית', 'משפט הסינוסים', 'חשבון דיפרנציאלי', 'שכיח', 'סטיית תקן', 'מקום גאומטרי'):
            self.assertIn(term, text)
            self.assertIn(term, read(CURRICULUM / 'grade10' / '4units.he.md') + read(CURRICULUM / 'grade11' / '5units.he.md') + read(CURRICULUM / 'grade12' / '5units.he.md')
                          + read(CURRICULUM / 'grade10' / '5units.he.md') + read(CURRICULUM / 'grade11' / '4units.he.md'))


class DataJsonLanguagesTests(unittest.TestCase):
    def test_data_json_has_the_two_languages_and_the_arabic_part_is_what_it_was(self):
        data = build_kit.build()
        self.assertEqual(list(data), ['version', 'base_prompt', 'subjects', 'langs'])
        self.assertEqual(list(data['langs']), ['he', 'en'])
        for language in LANGUAGES:
            built = data['langs'][language]
            self.assertEqual(list(built), ['base_prompt', 'texts', 'subjects'])
            math = built['subjects'][0]
            self.assertEqual([g['id'] for g in math['grades']], [10, 11, 12])
            self.assertEqual(sum(len(level['topics']) for g in math['grades'] for level in g['levels']), 101)
            for g in math['grades']:
                for level in g['levels']:
                    for topic in level['topics']:
                        self.assertIsNotNone(topic['example'], topic['id'])
                        self.assertIsNone(ARABIC_LETTER.search(topic['title_full'] + topic['text'] + topic['example']), topic['id'])
        he, en = data['langs']['he']['subjects'][0], data['langs']['en']['subjects'][0]
        self.assertEqual((he['name'], en['name']), ('מתמטיקה', 'Math'))
        self.assertEqual([g['name'] for g in he['grades']], ['י׳', 'י״א', 'י״ב'])
        self.assertEqual([g['name'] for g in en['grades']], ['10', '11', '12'])
        topic = en['grades'][0]['levels'][0]['topics'][6]
        self.assertEqual((topic['id'], topic['title'], topic['title_full']), ('m10-3-07', 'Distance, speed and time', 'Distance, speed and time (מסלולים)'))
        topic = he['grades'][0]['levels'][0]['topics'][6]
        self.assertEqual((topic['id'], topic['title'], topic['title_full']), ('m10-3-07', 'מסלולים', 'מסלולים'))

    def test_the_build_stops_when_a_translation_does_not_have_the_same_topics(self):
        import shutil
        import tempfile
        cache = ROOT / '.cache' / 'offline'
        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as folder:
            root = Path(folder) / 'curriculum'
            shutil.copytree(ROOT / 'curriculum', root)
            target = root / 'math' / 'grade10' / '3units.he.md'
            target.write_text(read(target).replace('#### m10-3-02 ייצוגים סטטיסטיים', '#### m10-3-99 ייצוגים סטטיסטיים'), encoding='utf-8')
            with self.assertRaises(ValueError):
                build_kit.build(root, KIT / 'base_prompt.txt')

    def test_a_missing_translation_stops_the_build(self):
        # task 19: a missing translation file stops the build (before, the language was left out without a word)
        import shutil
        import tempfile
        cache = ROOT / '.cache' / 'offline'
        cache.mkdir(parents=True, exist_ok=True)
        for missing in ('grade12/5units.en.md', 'grade10/examples/3units.he.md', 'bagrut_patterns.en.md'):
            with tempfile.TemporaryDirectory(dir=cache) as folder:
                root = Path(folder) / 'curriculum'
                shutil.copytree(ROOT / 'curriculum', root)
                (root / 'math' / missing).unlink()
                with self.assertRaisesRegex(ValueError, 'translation is missing'):
                    build_kit.build(root, KIT / 'base_prompt.txt')

    def test_the_text_tables_of_hebrew_and_english_have_the_same_keys_and_no_arabic(self):
        import json
        he = json.loads(read(KIT / 'prompt_texts.he.json'))
        en = json.loads(read(KIT / 'prompt_texts.en.json'))
        self.assertEqual(list(he), list(en))
        self.assertEqual(len(he['logRule']), 6)
        self.assertEqual((he['logRule'][1], en['logRule'][1]), ('NMI-LOG', 'NMI-LOG'))
        self.assertTrue(he['logRule'][4].startswith('טעויות:') and en['logRule'][4].startswith('Mistakes:'))
        # the heading the warm-up sentence points to is the heading of the mistakes section, in each language
        self.assertIn(he['secMistakes'].strip('= '), he['warmupStart'])
        self.assertIn(en['secMistakes'].strip('= '), en['warmupStart'])
        self.assertIn(he['secMistakes'].strip('= '), read(KIT / 'base_prompt.he.txt'))
        self.assertIn(en['secMistakes'].strip('= '), read(KIT / 'base_prompt.en.txt'))
        # the names of the sections that the code looks for are headings of the translated base prompt
        for language, table in (('he', he), ('en', en)):
            base = read(KIT / f'base_prompt.{language}.txt')
            for name in table['names'].values():
                self.assertIn(f'== {name} ==', base, f'{language}: {name}')
            self.assertIn(table['examHeading'], read(CURRICULUM / 'grade10' / ('3units.he.md' if language == 'he' else '3units.en.md')))
        self.assertIsNone(ARABIC_LETTER.search(read(KIT / 'prompt_texts.he.json') + read(KIT / 'prompt_texts.en.json')))


if __name__ == '__main__':
    unittest.main()
