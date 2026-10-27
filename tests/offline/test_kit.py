"""Offline tests of the NMI kit data: tools/build_kit.py, kit/data.json and the example bank.

No network, no API. The prompt itself is tested in tests/kit/prompt.test.cjs and the page in tests/kit/kit.spec.cjs.
"""
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests' / 'kit'))

import build_kit  # noqa: E402
import example_solutions  # noqa: E402

CURRICULUM = ROOT / 'curriculum'
EXAMPLES = CURRICULUM / 'math' / 'grade10' / 'examples'
LEVEL_IDS = {3: 14, 4: 11, 5: 13}  # topics per level of grade 10


def read(path):
    return Path(path).read_text(encoding='utf-8')


class ExampleBankTests(unittest.TestCase):
    GRADES = (10, 11, 12)

    def setUp(self):
        self.bank = {}
        self.topics = {}
        for grade in self.GRADES:
            for units in (3, 4, 5):
                folder = CURRICULUM / 'math' / f'grade{grade}'
                self.bank[(grade, units)] = build_kit.parse_examples(folder / 'examples' / f'{units}units.md')
                self.topics[(grade, units)] = build_kit.parse_topics(read(folder / f'{units}units.md'))
        self.examples = {units: self.bank[(10, units)] for units in (3, 4, 5)}  # the grade 10 bank, by units

    def every_example(self):
        for (grade, units), found in self.bank.items():
            for topic_id, text in found.items():
                yield grade, units, topic_id, text

    def test_every_topic_of_grades_10_11_12_has_exactly_one_example_and_nothing_else_does(self):
        expected = {(10, 3): 14, (10, 4): 11, (10, 5): 13, (11, 3): 11, (11, 4): 15, (11, 5): 9, (12, 3): 5, (12, 4): 14, (12, 5): 9}
        for (grade, units), count in expected.items():
            ids = [t['id'] for t in self.topics[(grade, units)]]
            self.assertEqual(len(ids), count, (grade, units))
            self.assertEqual(list(self.bank[(grade, units)]), ids, (grade, units))  # same ids, same order
            text = read(CURRICULUM / 'math' / f'grade{grade}' / 'examples' / f'{units}units.md')
            headings = re.findall(r'^## (m\d+-\d-\d\d) ', text, re.M)
            self.assertEqual(headings, ids, (grade, units))  # one section per topic, no duplicates
        self.assertEqual(sum(expected.values()), 101)

    def test_each_example_has_a_story_sections_alef_beth_jim_and_an_explain_section(self):
        for grade, units, topic_id, text in self.every_example():
            self.assertTrue(text.startswith('**القصة:**'), topic_id)
            for label in ('**القسم أ', '**القسم ب', '**القسم ج'):
                self.assertIn(label, text, topic_id)
            self.assertRegex(text, r'\*\*القسم [أبجد] \(\d+ علامات?\) - علّل:\*\*', topic_id)
            sections = re.findall(r'\*\*القسم ([أبجد])', text)
            self.assertIn(len(sections), (3, 4), topic_id)
            self.assertEqual(sections, list('أبجد')[:len(sections)], topic_id)
            self.assertNotIn('ملف', text, topic_id)
            self.assertNotRegex(text, r'm\d+-\d', topic_id)  # no topic ids inside an example
            self.assertTrue(topic_id.startswith(f'm{grade}-{units}-'), topic_id)

    def test_every_example_has_a_sympy_solution_with_all_facts_true_and_its_numbers_in_the_text(self):
        wanted = {t['id'] for topics in self.topics.values() for t in topics}
        self.assertEqual(set(example_solutions.SOLUTIONS), wanted)
        checked = 0
        for grade, units, topic_id, text in self.every_example():
            result = example_solutions.SOLUTIONS[topic_id]()
            self.assertTrue(result['facts'], topic_id)
            self.assertTrue(all(fact is True or bool(fact) for fact in result['facts']), (topic_id, [i for i, f in enumerate(result['facts']) if not f]))
            for number in result['numbers']:
                self.assertIn(number, text, f'{topic_id}: {number}')
            checked += 1
        self.assertEqual(checked, 101)

    def test_a_wrong_number_is_caught(self):
        # the check really fails when a story number is changed: 120 students became 130
        text = self.examples[3]['m10-3-01']
        altered = text.replace('120', '130')
        numbers = example_solutions.SOLUTIONS['m10-3-01']()['numbers']
        self.assertTrue(all(n in text for n in numbers))
        self.assertFalse(all(n in altered for n in numbers))
        # and in a grade 11 example: the 10% growth of the village became 12%
        text = self.bank[(11, 3)]['m11-3-01']
        self.assertFalse(all(n in text.replace('10%', '12%') for n in example_solutions.SOLUTIONS['m11-3-01']()['numbers']))

    def test_a_story_that_goes_below_zero_says_why(self):
        # a sale, a price, a length, a weight or a number of people is never negative: a story with a negative domain
        # (-2 <= x, x = -1) must be about something that can be (a temperature, a profit or loss, a screen coordinate,
        # a time before a starting point), and must not be about the things that cannot
        cannot_be_negative = ('مبيعات', 'سعر', 'أسعار', 'عدد الطلاب', 'طول', 'وزن', 'أشخاص')
        can_be_negative = ('درجة الحرارة', 'خسارة', 'الإحداثيات ممكن تكون سالبة', 'نقطة الأصل', 'بالنسبة لنص الشاشة', 'قبل', 'بدون قصة')
        checked = 0
        for grade, units, topic_id, text in self.every_example():
            story = text.split('\n\n')[0]
            negative = re.search(r'(?<![\w.])-\d+(?:\.\d+)? ≤ x|x = -\d', text) or re.search(r'القيم السالبة', story)
            if not negative:
                continue
            checked += 1
            self.assertTrue(any(word in story for word in can_be_negative), f'{topic_id}: says nothing about why it is below zero')
            self.assertFalse(any(word in story for word in cannot_be_negative), f'{topic_id}: a negative domain for something that is never negative')
        self.assertGreaterEqual(checked, 3)

    def test_the_quantities_of_a_story_are_never_negative_where_they_cannot_be(self):
        # the sympy files compute the values of the quantities; here the ones that are counts, prices or sizes must be >= 0
        import example_solutions_11 as g11  # the grade 11 bank
        import example_solutions_12 as g12  # the grade 12 bank
        self.assertTrue(all((v ** 3 - 6 * v ** 2 + 9 * v + 1) >= 0 for v in range(0, 5)))  # m11-5-02: the water in a tank
        self.assertTrue(all((2 + 2 * g11.sp.sin(g11.sp.pi * v / 6)) >= 0 for v in range(0, 13)))  # m11-5-01: the height of the tide
        self.assertTrue(all(10 + g11.sp.sin(v) + g11.sp.cos(v) > 0 for v in (0, 1, 2, 3)))  # m11-5-06: the height of a wave
        self.assertTrue(all(80 * g12.R(1, 2) ** g12.R(v, 5) > 0 for v in range(0, 60)))  # m12-4-09: a mass

    def test_the_examples_that_were_changed_for_their_story_say_what_the_values_are(self):
        expected = {
            (4, 'm10-4-02'): 'من لحظة الرمي لحد ما بتوقع على الأرض',
            (4, 'm10-4-04'): 'فالإحداثيات ممكن تكون سالبة',
            (4, 'm10-4-08'): 'والسالب قبل العامود',
            (5, 'm10-5-02'): 'والسالب خسارة',
            (5, 'm10-5-04'): 'فالإحداثيات ممكن تكون سالبة',
            (5, 'm10-5-06'): 'درجة الحرارة بالدرجات المئوية',
            (5, 'm10-5-08'): 'القيم السالبة تحت نص الشاشة',
            (5, 'm10-5-13'): 'سؤال بدون قصة',
        }
        for (units, topic_id), phrase in expected.items():
            self.assertIn(phrase, self.examples[units][topic_id], topic_id)
        # the sales story of the derivative example is gone: sales are never negative
        self.assertNotIn('مبيعات تطبيق', self.examples[5]['m10-5-06'])
        self.assertIn('-2 ≤ x ≤ 4', self.examples[5]['m10-5-06'])
        values = example_solutions.SOLUTIONS['m10-5-06']()
        self.assertTrue(all(values['facts']))

    def test_the_examples_are_new_stories_not_copies_of_a_real_exam(self):
        for grade, units, topic_id, text in self.every_example():
            self.assertNotRegex(text, r'035\d{3}|3[5]\d{3}', topic_id)  # no exam form numbers inside an example
        for grade in self.GRADES:
            for units in (3, 4, 5):
                text = read(CURRICULUM / 'math' / f'grade{grade}' / 'examples' / f'{units}units.md')
                self.assertIn('مش منسوخة من أي امتحان', text)
                self.assertIn('sympy', text)

    def test_the_examples_of_each_level_are_of_the_right_shape_for_the_level(self):
        # 3 units: stories from daily life; 5 units: functions, geometry and proofs, some without a story
        for (grade, units), found in self.bank.items():
            self.assertTrue(all('**القصة:**' in text for text in found.values()), (grade, units))
        three = ' '.join(self.bank[(12, 3)].values())
        for word in ('أكياس سكر', 'مخبز', 'خزان'):
            self.assertIn(word, three)
        five = ' '.join(self.bank[(12, 5)].values())
        for word in ('قطع ناقص', 'z³ = 8', 'مجموعة S'):
            self.assertIn(word, five)


class BuildKitTests(unittest.TestCase):
    def test_data_json_is_up_to_date(self):
        self.assertEqual(read(build_kit.OUTPUT), build_kit.render(build_kit.build()))
        self.assertEqual(build_kit.main(['--check']), 0)

    def test_the_build_is_deterministic(self):
        self.assertEqual(build_kit.render(build_kit.build()), build_kit.render(build_kit.build()))

    def test_subjects_grades_and_levels_come_from_the_folders(self):
        data = build_kit.build()
        self.assertEqual([s['id'] for s in data['subjects']], ['math'])
        math = data['subjects'][0]
        self.assertEqual(math['name'], 'رياضيات')
        self.assertEqual([(g['id'], g['name']) for g in math['grades']], [(10, 'العاشر'), (11, 'الحادي عشر'), (12, 'الثاني عشر')])
        for grade in math['grades']:
            self.assertEqual([l['units'] for l in grade['levels']], [3, 4, 5])
        counts = {(g['id'], l['units']): len(l['topics']) for g in math['grades'] for l in g['levels']}
        self.assertEqual(counts, {(10, 3): 14, (10, 4): 11, (10, 5): 13, (11, 3): 11, (11, 4): 15, (11, 5): 9,
                                  (12, 3): 5, (12, 4): 14, (12, 5): 9})
        self.assertEqual(data['base_prompt'], read(ROOT / 'kit' / 'base_prompt.txt').strip())

    def test_a_level_without_examples_is_marked_experimental(self):
        math = build_kit.build()['subjects'][0]
        flags = {(g['id'], l['units']): l['experimental'] for g in math['grades'] for l in g['levels']}
        self.assertEqual(set(flags.values()), {False})  # all nine levels have their example bank
        for grade in math['grades']:
            for level in grade['levels']:
                for topic in level['topics']:
                    self.assertIsNotNone(topic['example'], topic['id'])
        # a level that misses one example, or all of them, is marked again (tested on a copy of the folder)
        cache = ROOT / '.cache' / 'offline'
        cache.mkdir(parents=True, exist_ok=True)
        import shutil
        with tempfile.TemporaryDirectory(dir=cache) as folder:
            root = Path(folder) / 'curriculum'
            shutil.copytree(CURRICULUM, root, ignore=shutil.ignore_patterns('NMI_KIT_TASK*.md'))
            examples = root / 'math' / 'grade11' / 'examples' / '3units.md'
            text = read(examples)
            examples.write_text(text.replace('## m11-3-11 مراجعة وتدريب، مع إكمال مواضيع العاشر حسب الحاجة', '## m11-3-99 مش من المنهاج'), encoding='utf-8')
            (root / 'math' / 'grade12' / 'examples' / '4units.md').unlink()
            data = build_kit.build(root, ROOT / 'kit' / 'base_prompt.txt')
        flags = {(g['id'], l['units']): l['experimental'] for g in data['subjects'][0]['grades'] for l in g['levels']}
        self.assertTrue(flags[(11, 3)])
        self.assertTrue(flags[(12, 4)])
        self.assertEqual(sum(flags.values()), 2)

    def test_topics_have_ids_titles_without_hebrew_and_their_text(self):
        math = build_kit.build()['subjects'][0]
        level = math['grades'][0]['levels'][0]
        first = level['topics'][0]
        self.assertEqual((first['id'], first['title'], first['group']), ('m10-3-01', 'استنتاج من معلومات', 'عنقود العلوم والمجتمع'))
        self.assertIn('הסקת מסקנות', first['title_full'])
        self.assertNotRegex(first['title'], r'[֐-׿]')
        self.assertTrue(first['text'].startswith('- **المحتوى:**'))
        for grade in math['grades']:
            for lv in grade['levels']:
                for topic in lv['topics']:
                    self.assertNotRegex(topic['text'], r'^#', topic['id'])
                    self.assertTrue(topic['title'], topic['id'])
        self.assertIn('## تعليمات للمدرّس عن هذا الدليل', level['notes'])
        self.assertIn('## الامتحان', level['notes'])
        self.assertNotIn('المواضيع بالترتيب', level['notes'])
        self.assertNotIn('m10-3-01', level['notes'])

    def test_only_the_form_sections_of_the_level_go_into_the_patterns(self):
        patterns = build_kit.build()['subjects'][0]['patterns']
        self.assertEqual(sorted(patterns['levels']), ['3', '4', '5'])
        self.assertEqual([len(patterns['levels'][k]) for k in '345'], [3, 2, 2])
        self.assertEqual([s['grade'] for s in patterns['levels']['3']], ['العاشر', None, 'الثاني عشر'])
        self.assertTrue(patterns['general'].startswith('## قواعد عامة'))
        self.assertTrue(patterns['howto'].startswith('## كيف المدرّس يكتب سؤال'))
        self.assertTrue(patterns['forms'].startswith('## أرقام الاستمارات'))
        joined = '\n'.join(s['text'] for k in '345' for s in patterns['levels'][k])
        for form in ('35172', '35371', '35372', '35471', '35472', '35571', '35572'):
            self.assertIn(form, joined)
        self.assertNotIn('ملف', json.dumps(patterns, ensure_ascii=False))

    def test_a_new_subject_folder_is_picked_up_without_code(self):
        cache = ROOT / '.cache' / 'offline'
        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as folder:
            root = Path(folder)
            (root / 'physics' / 'grade10').mkdir(parents=True)
            (root / 'physics' / 'grade10' / '4units.md').write_text(
                '# فيزياء، الصف العاشر، 4 وحدات\n\n## الامتحان\n\nنص\n\n## المواضيع بالترتيب\n\n### m10-4-01 الحركة (תנועה)\n- **المحتوى:** سرعة.\n',
                encoding='utf-8')
            (root / 'notes').mkdir()  # a folder without grades is not a subject
            base = root / 'base.txt'
            base.write_text('x', encoding='utf-8')
            data = build_kit.build(root, base)
        self.assertEqual([s['id'] for s in data['subjects']], ['physics'])
        subject = data['subjects'][0]
        self.assertEqual(subject['name'], 'فيزياء')
        self.assertIsNone(subject['patterns'])
        level = subject['grades'][0]['levels'][0]
        self.assertEqual((level['units'], level['experimental']), (4, True))
        self.assertEqual(level['topics'][0]['title'], 'الحركة')


class CurriculumAdditionTests(unittest.TestCase):
    """The lines added from the ministry documents: content lines for empty topics, the 3-unit out-of-curriculum section."""

    def topic(self, grade, units, topic_id):
        level = next(l for l in next(g for g in build_kit.build()['subjects'][0]['grades'] if g['id'] == grade)['levels'] if l['units'] == units)
        return next(t for t in level['topics'] if t['id'] == topic_id)

    def test_the_three_3_unit_files_say_what_is_outside_the_curriculum(self):
        for grade in (10, 11, 12):
            text = read(CURRICULUM / 'math' / f'grade{grade}' / '3units.md')
            self.assertEqual(text.count('## خارج منهاج 3 وحدات'), 1, grade)
            self.assertLess(text.index('## الامتحان'), text.index('## خارج منهاج 3 وحدات'))
            self.assertLess(text.index('## خارج منهاج 3 وحدات'), text.index('## المواضيع بالترتيب'))
            self.assertIn('المتواليات، وحساب المثلثات بالفراغ، والتفاضل والتكامل، والهندسة التحليلية للدائرة (حسب وثيقة المنهاج الجديد).', text)
            self.assertIn('إذا الطالب سأل عنها، قله بصراحة إنها مش من منهاج 3 وحدات.', text)
        for grade in (10, 11, 12):
            for units in (4, 5):
                self.assertNotIn('خارج منهاج 3 وحدات', read(CURRICULUM / 'math' / f'grade{grade}' / f'{units}units.md'))
        notes = build_kit.build()['subjects'][0]['grades'][0]['levels'][0]['notes']
        self.assertIn('## خارج منهاج 3 وحدات', notes)  # it reaches the prompt with the other notes

    def test_empty_topics_got_their_content_line(self):
        expected = {
            (10, 3, 'm10-3-05'): 'مسائل بتجمع الإحصاء والاحتمال من المواضيع اللي قبل.',
            (10, 3, 'm10-3-09'): 'تغطية مساحة ببلاط، وحساب عدد البلاطات والتكلفة (الوثيقة بتذكر الاسم بس، والشكل من امتحان 35172).',
            (10, 3, 'm10-3-10'): 'مسائل بتجمع كل مواضيع عنقود المستوى والفراغ.',
            (11, 3, 'm11-3-01'): 'مسائل نمو واضمحلال: كمية بتزيد أو بتنقص بنسبة ثابتة مع الزمن.',
            (11, 3, 'm11-3-09'): 'مسائل نمو واضمحلال: كمية بتزيد أو بتنقص بنسبة ثابتة مع الزمن.',
            (11, 3, 'm11-3-04'): 'نسبة وتناسب، ومقياس رسم للخرائط والرسومات، وتحويل وحدات.',
            (11, 3, 'm11-3-10'): 'الانحراف المعياري على بيانات مالية.',
            (12, 3, 'm12-3-01'): 'تقدير احتمالات بالتوزيع الطبيعي، والعلامة المعيارية (ציון תקן).',
            (12, 3, 'm12-3-03'): 'البرمجة الخطية (الوثيقة بتذكر الاسم بس).',
            (12, 3, 'm12-3-05'): 'المستقيم بس، بدون الدائرة.',
            (12, 4, 'm12-4-06'): 'تمثيل جبري للمتجه بنظام محاور بالفراغ، وعمليات بالتمثيل الجبري.',
            (12, 4, 'm12-4-07'): 'الضرب السلّمي بالطريقة الجبرية.',
            (12, 4, 'm12-4-08'): 'أسئلة بتجمع الطريقتين الهندسية والجبرية.',
        }
        for (grade, units, topic_id), line in expected.items():
            text = self.topic(grade, units, topic_id)['text']
            self.assertIn('- **المحتوى:** ' + line, text.splitlines(), topic_id)

    def test_unconfirmed_lines_say_so_and_old_lines_stay(self):
        text = self.topic(11, 3, 'm11-3-02')['text']
        self.assertIn('- **ممكن (مش مؤكد):** الربيعيات والعشيريات (רבעונים ועשירונים)، موجودين بوثيقة المنهاج ومش بالتوصيات.', text.splitlines())
        self.assertIn('- **المحتوى:** الانحراف المعياري، ودمج مقاييس المركز والتشتت لاستنتاجات.', text)  # the old lines are still there
        self.assertIn('- **أخطاء شائعة:** الاعتماد على المعدل لحاله لمقارنة مجموعتين.', text)
        self.assertIn('- **أخطاء شائعة:** خلط بين نسبة النمو (5%) والمعامل (1.05).', self.topic(11, 3, 'm11-3-01')['text'])

    def test_the_three_conic_sections_have_the_details_of_the_curriculum_document(self):
        text = self.topic(12, 5, 'm12-5-05')['text']
        for part in ('- **تفاصيل حسب وثيقة المنهاج:**',
                     '  - **القطع المكافئ (פרבולה):** محل هندسي، معادلة قانونية، خصائص، أوضاع نسبية مع مستقيم ودائرة، مماس بنقطة عليه.',
                     '  - **القطع الناقص (אליפסה):** محل هندسي (تعريفين)، معادلة قانونية، خصائص، أوضاع نسبية مع مستقيم ودائرة مركزها على أحد المحاور.',
                     '  - **القطع الزائد (היפרבולה):** محل هندسي، معادلة قانونية، خصائص، أوضاع نسبية مع مستقيم ودائرة مركزها على أحد المحاور، وإيجاد محلات هندسية.',
                     '- **القطع المكافئ (פרבולה):** تعريف كمحل هندسي، معادلة قانونية، خصائص، أوضاع نسبية مع مستقيمات ودوائر، مماس.'):
            self.assertIn(part, text.splitlines())

    def test_sources_has_the_curriculum_document_and_the_unsure_point(self):
        sources = read(CURRICULUM / 'SOURCES.md')
        self.assertIn('https://meyda.education.gov.il/files/Pop/0files/matmatika/Chativa-Elyona/new-curriculum.pdf', sources)
        links, unsure = sources.split('## الروابط')[1].split('## أوراق القوانين')[0], sources.split('## نقاط لازم تتأكد منها مع الأستاذ')[1]
        self.assertIn('new-curriculum.pdf', links)
        self.assertIn('- الربيعيات والعشيريات بـ 3 وحدات الحادي عشر مش مؤكدة.', unsure.splitlines())
        self.assertIn('- 4 وحدات (35471 و35472) وباقي الملفات: ما بتتغيّر (متطابقة مع جدول 2025).', unsure)  # old lines stay


class KitFilesTests(unittest.TestCase):
    def test_the_files_pages_needs_are_all_there(self):
        for name in ('index.html', 'style.css', 'app.js', 'prompt.js', 'data.json', 'base_prompt.txt', 'manifest.webmanifest',
                     'icon.svg', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png'):
            self.assertTrue((ROOT / 'kit' / name).is_file(), name)
        for name, size in (('icon-192.png', 192), ('icon-512.png', 512), ('icon-maskable-512.png', 512), ('apple-touch-icon.png', 180)):
            header = (ROOT / 'kit' / name).read_bytes()[:24]
            self.assertEqual(header[:8], b'\x89PNG\r\n\x1a\n', name)
            self.assertEqual((int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big')), (size, size), name)

    def test_manifest_is_arabic_rtl_black_and_white_and_needs_no_service_worker(self):
        manifest = json.loads(read(ROOT / 'kit' / 'manifest.webmanifest'))
        self.assertEqual((manifest['lang'], manifest['dir'], manifest['display']), ('ar', 'rtl', 'standalone'))
        self.assertEqual((manifest['background_color'], manifest['theme_color']), ('#ffffff', '#000000'))
        for icon in manifest['icons']:
            self.assertTrue((ROOT / 'kit' / icon['src']).is_file(), icon['src'])
        self.assertEqual({i['sizes'] for i in manifest['icons'] if i['type'] == 'image/png'}, {'192x192', '512x512'})
        self.assertFalse(list((ROOT / 'kit').glob('*sw*.js')))
        self.assertNotIn('serviceWorker', read(ROOT / 'kit' / 'app.js'))

    def test_the_page_is_self_contained_and_uses_only_the_official_app_links(self):
        html = read(ROOT / 'kit' / 'index.html')
        self.assertIn('<html lang="ar" dir="rtl">', html)
        self.assertIn('width=device-width', html)
        for reference in re.findall(r'(?:src|href)="([^"]+)"', html):
            self.assertFalse(reference.startswith(('http:', 'https:', '//')), reference)  # no CDN, no web font
        app = read(ROOT / 'kit' / 'app.js')
        self.assertEqual(sorted(re.findall(r"https://[^'\"]+", app)),
                         sorted(['https://chatgpt.com/', 'https://claude.ai/new', 'https://gemini.google.com/app', 'https://meyda.education.gov.il/bagptr/']))
        # the Android buttons use Chrome intents of the three official apps, with the official site as the fallback
        # ChatGPT variant B, Claude variant A and Gemini variant C of kit/applinks.html: the ones that opened the app on a real phone
        self.assertEqual(sorted(re.findall(r"package: '([a-z.]+)'", app)), ['com.anthropic.claude', 'com.openai.chatgpt'])
        self.assertIn("name: 'Gemini', url: 'https://gemini.google.com/app', host: 'gemini.google.com', path: 'app', suffix: '', package: null", app)
        self.assertIn("name: 'ChatGPT', url: 'https://chatgpt.com/', host: 'chatgpt.com', path: '?model=auto', suffix: '?model=auto', package: 'com.openai.chatgpt'", app)
        self.assertIn("name: 'Claude', url: 'https://claude.ai/new', host: 'claude.ai', path: 'new', suffix: '', package: 'com.anthropic.claude'", app)
        self.assertIn("(app.package ? 'package=' + app.package + ';' : '')", app)
        self.assertNotIn('com.google.android.apps.bard', app)  # Gemini has no package any more
        page = read(ROOT / 'kit' / 'applinks.html')
        self.assertIn('com.google.android.apps.bard', page)  # the test page keeps all its variants
        self.assertEqual(app.count("'intent://'"), 1)
        self.assertIn('S.browser_fallback_url=', app)
        for scheme in ('chatgpt://', 'claude://', 'gemini://', 'googlechrome://', 'market://'):
            self.assertNotIn(scheme, app)  # no private or unofficial scheme
        self.assertNotIn('type="file"', html)
        self.assertNotIn("type: 'file'", app)  # nothing is uploaded to the site
        for name in ('style.css', 'app.js', 'prompt.js'):
            self.assertNotIn('tokens.css', read(ROOT / 'kit' / name))

    def test_the_prompt_files_say_bagrut_once_and_the_curriculum_folder_is_not_touched(self):
        base = read(ROOT / 'kit' / 'base_prompt.txt')
        self.assertEqual(base.count('البجروت'), 1)
        self.assertIn('- ما تحكي عن البجروت إلا إذا الطالب سأل عنه.', base.splitlines())
        self.assertNotIn('بجروت', base.replace('البجروت', ''))  # no other form of the word
        self.assertEqual(json.loads(read(build_kit.OUTPUT))['base_prompt'], base.strip())
        # the guide keeps its name: the wording is changed only in the prompt that is built (kit/prompt.js)
        patterns = read(CURRICULUM / 'math' / 'bagrut_patterns.md')
        self.assertIn('## قواعد عامة لكل سؤال بجروت', patterns)
        self.assertIn('## كيف المدرّس يكتب سؤال تدريب بنمط البجروت', patterns)
        js = read(ROOT / 'kit' / 'prompt.js')
        for part in ('function asExam', "replace(/البجروت/g, 'الامتحان')", "WRITES_QUESTIONS = { practice: true, mock: true }",
                     "part.split('\\n')[0].trim() !== '## الامتحان'"):
            self.assertIn(part, js)

    def test_part_b_to_e_texts_are_in_the_page_and_the_prompt(self):
        app, prompt, texts = read(ROOT / 'kit' / 'app.js'), read(ROOT / 'kit' / 'prompt.js'), read(ROOT / 'kit' / 'i18n.js')
        for part in ('لديّ امتحان قديم أو ورقة عمل من معلّمي', 'الأفضل: يضع البرومبت داخل التطبيق مباشرة.', '💡 لماذا نفتح محادثة جديدة لكل مادة أو موضوع جديد؟',
                     '📎 الصق البرومبت، ثم اضغط + في التطبيق', 'ملاحظة للمدرّس (اختياري)', 'نسخنا البرومبت. الصقه في التطبيق.'):
            self.assertIn(part, texts)
        self.assertIn('navigator.userAgent', app)
        for part in ('الطالب رفعلك صورة أو ملف لامتحان قديم أو ورقة عمل من أستاذه.', "'== ملاحظة من الطالب =='", 'اتبع هالملاحظة بطريقة الشرح والأمثلة والتركيز.',
                     'const MAX_NOTE = 200;', 'إذا الطالب ما رفع الملف، اطلبه منه أول.'):
            self.assertIn(part, prompt)
        guide = read(ROOT / 'docs' / 'KIT.md')
        for part in ('ملف الأستاذ', 'ملاحظة للمدرّس', 'أندرويد', 'محادثة جديدة'):
            self.assertIn(part, guide)

    def test_on_ios_the_app_buttons_are_normal_links_and_nothing_else_changed(self):
        app = read(ROOT / 'kit' / 'app.js')
        for part in ('function isIOS()', '/iPhone|iPad|iPod/.test(navigator.userAgent', "navigator.platform === 'MacIntel'", 'navigator.maxTouchPoints > 1',
                     'function copyInsideClick(text)', "target: ios ? null : '_blank'", 'onclick: ios ? function () { copyInsideClick(built.text); }'):
            self.assertIn(part, app)
        # on iOS nothing stops the click or opens a window: copyInsideClick has no preventDefault and no window.open
        inside = app[app.index('function copyInsideClick(text)'):app.index('/* On Android and on a computer')]
        self.assertNotIn('preventDefault', inside)
        self.assertNotIn('window.open', inside)
        self.assertIn('navigator.clipboard.writeText(text)', inside)
        self.assertIn('legacyCopy(text)', inside)
        # Android and the computer keep their way: stop the click, copy, then open
        self.assertIn("if (isAndroid()) { window.open(address, '_self'); return; }", app)
        self.assertIn("var tab = window.open(address, '_blank');", app)
        # still no private scheme, only the official https addresses
        for scheme in ('chatgpt://', 'claude://', 'gemini://', 'googlechrome://', 'x-apple'):
            self.assertNotIn(scheme, app)

    def test_the_base_prompt_has_the_marks_the_hint_ladder_and_the_no_hint_rule(self):
        base = read(ROOT / 'kit' / 'base_prompt.txt')
        lines = base.splitlines()
        self.assertIn('   - ما تعطي تلميح مع قسم جديد، حتى جملة مثل "فكّر بـ..." أو "تذكّر إن..." هي تلميح. التلميح بس بعد ما الطالب يحاول ويغلط، أو لما يطلب.', lines)
        self.assertIn('   - العلامة لازم تعكس الحل الحقيقي: إذا الطالب حل لحاله من أول مرة، علامة القسم كاملة. إذا احتاج تلميح صغير، نقّص ربع العلامة. '
                      'إذا احتاج تلميح كبير، نقّص النص. إذا حليت الخطوة قدامه، ما بياخد علامة عليها. قله بجملة وحدة ليش نقصت. بالملخص اكتب العلامة الحقيقية.', lines)
        self.assertIn("- غلطة أولى بنفس القسم: قول وين الغلط بالضبط، وتلميح صغير: سؤال أو جملة بتوجّهه، بدون ما تكتب المعادلة أو تعوّض الأرقام عنه. "
                      "مثال: 'عوّض نقطة A بمعادلتك، هل بتطلع صح؟'", lines)
        self.assertNotIn('ارجع للقصة', base)
        # the rules are in the practice mode (3), before the mock exam (4)
        practice = base[base.index('3) تدرّب:'):base.index('4) امتحان تجريبي:')]
        self.assertIn('العلامة لازم تعكس الحل الحقيقي', practice)
        self.assertIn('ما تعطي تلميح مع قسم جديد', practice)
        self.assertEqual(json.loads(read(build_kit.OUTPUT))['base_prompt'], base.strip())
        self.assertIn('TARGET_NOTE', read(ROOT / 'kit' / 'prompt.js'))

    def test_the_app_link_test_page_is_not_part_of_the_kit_and_uses_official_hosts_only(self):
        page = read(ROOT / 'kit' / 'applinks.html')
        self.assertIn('<title>فحص فتح التطبيقات</title>', page)
        self.assertIn('اضغط كل زر. إذا فتح التطبيق، اكتب الحرف. إذا فتح الموقع، ارجع وجرّب اللي بعده.', page)
        self.assertIn('href="style.css"', page)
        self.assertEqual(sorted(re.findall(r'data-variant="([a-z-]+)"', page)),
                         sorted(['chatgpt-a', 'chatgpt-b', 'chatgpt-c', 'chatgpt-d', 'gemini-a', 'gemini-b', 'gemini-c', 'gemini-d', 'claude-a']))
        hrefs = re.findall(r'<a class="linkbtn" href="([^"]+)"', page)
        self.assertEqual(len(hrefs), 9)
        for href in hrefs:
            self.assertRegex(href, r'^(https://(chatgpt\.com|gemini\.google\.com)/|intent://(chatgpt\.com|gemini\.google\.com|claude\.ai)/)')
            for scheme in ('chatgpt://', 'claude://', 'gemini://', 'googlechrome://', 'market://', 'javascript:'):
                self.assertNotIn(scheme, href)
            if href.startswith('intent://'):
                self.assertRegex(href, r';S\.browser_fallback_url=https%3A%2F%2F(chatgpt\.com|gemini\.google\.com|claude\.ai)%2F')
                self.assertTrue(href.endswith(';end'))
        # the exact address is printed under every button
        for href in hrefs:
            self.assertIn(f'<code>{href}</code>', page)
        # a plain page: no script, no network, nothing stored
        for word in ('<script', 'fetch(', 'localStorage', 'XMLHttpRequest'):
            self.assertNotIn(word, page, word)
        # it is not linked from the kit, and not part of the app
        for name in ('index.html', 'app.js', 'prompt.js', 'log.js', 'manifest.webmanifest'):
            self.assertNotIn('applinks', read(ROOT / 'kit' / name), name)
        # it is published with the site, because the workflow copies the whole kit folder to the root of the site folder
        self.assertIn('cp -r kit/. _site/', read(ROOT / '.github' / 'workflows' / 'kit-pages.yml'))

    def test_the_page_is_in_three_languages_and_the_texts_are_in_one_dictionary(self):
        html, app, texts, prompt = (read(ROOT / 'kit' / name) for name in ('index.html', 'app.js', 'i18n.js', 'prompt.js'))
        self.assertIn('<html lang="ar" dir="rtl">', html)  # the default of the file; the page sets lang and dir from the language
        self.assertIn('<nav id="langs"', html)
        self.assertEqual(re.findall(r'data-lang="(\w+)"', html), ['ar', 'he', 'en'])
        for label in ('عربي', 'עברית', 'English'):
            self.assertIn(f'>{label}</button>', html)
        self.assertIn("document.documentElement.setAttribute('dir', I.DIR[state.lang])", app)
        self.assertIn("document.documentElement.setAttribute('lang', state.lang)", app)
        self.assertIn('I.loadLang(storage()) || I.detect(navigator.language)', app)
        for part in ("const DIR = { ar: 'rtl', he: 'rtl', en: 'ltr' };", "const STORAGE_KEY = 'nmi-lang-v1';", "primary === 'he' || primary === 'iw'", "primary === 'en'"):
            self.assertIn(part, texts)
        # the page code has no text of its own; only the log token stays
        for line in app.splitlines():
            code = re.sub(r"//.*$", '', line) if not line.strip().startswith('/*') else ''
            self.assertNotRegex(re.sub(r"/\*.*?\*/", '', code), r"'[^']*[\u0600-\u06ff][^']*'", line)
        # the prompt line for the student's language is in prompt.js and nothing else of the prompt is translated
        self.assertIn("const STUDENT_LANGUAGE = { he: 'עברית', en: 'English' };", prompt)
        # the only Hebrew words in the prompt code: the name of the language, and the two phrases of the student in the language block
        hebrew_free = prompt.replace("{ he: 'עברית', en: 'English' }", '').replace('לא הבנתי', '').replace('סיימתי', '')
        # ... and the first and last lines of the prompt of a page in Hebrew (the English ones are English)
        for line in ('חשוב: כל התשובות שלך לתלמיד יהיו בעברית בלבד, מההודעה הראשונה. ההוראות למטה כתובות בערבית רק כי תוכנית הלימודים כתובה בערבית.', 'התחל עכשיו, בעברית בלבד.'):
            self.assertIn(line, prompt)
            hebrew_free = hebrew_free.replace(line, '')
        self.assertEqual(len(re.findall(r'[\u0590-\u05ff]+', hebrew_free)), 0)
        # the data keeps the Hebrew heading of the clusters, for the pages in Hebrew and English
        data = json.loads(read(build_kit.OUTPUT))
        topic = data['subjects'][0]['grades'][0]['levels'][0]['topics'][0]
        self.assertEqual((topic['group'], topic['group_full']), ('عنقود العلوم والمجتمع', 'عنقود العلوم والمجتمع (אשכול מדע וחברה)'))
        self.assertIsNone(data['subjects'][0]['grades'][0]['levels'][1]['topics'][0]['group_full'])  # 4 units has no clusters
        # the curriculum files themselves are not changed by this
        self.assertNotIn('group_full', read(CURRICULUM / 'math' / 'grade10' / '3units.md'))

    def test_the_log_stays_on_the_device_and_the_page_loads_it(self):
        html, app, log, prompt, texts = (read(ROOT / 'kit' / name) for name in ('index.html', 'app.js', 'log.js', 'prompt.js', 'i18n.js'))
        self.assertIn('<script src="log.js"></script>', html)
        self.assertIn('id="log-link"', html)
        self.assertLess(html.index('i18n.js'), html.index('prompt.js'))  # the texts first, then the prompt, the log and the page
        self.assertLess(html.index('prompt.js'), html.index('log.js'))
        self.assertLess(html.index('log.js'), html.index('app.js'))
        # nothing the student pastes leaves the browser: the only request of the page is the data file
        self.assertEqual(app.count('fetch('), 1)
        self.assertIn("fetch('data.json')", app)
        for word in ('fetch(', 'XMLHttpRequest', 'sendBeacon', 'WebSocket', 'navigator.share', 'window.open', 'eval(', 'innerHTML'):
            self.assertNotIn(word, log, word)
            self.assertNotIn(word, texts, word)
        self.assertNotIn('innerHTML', app)  # the log and the notes are shown as text, never as HTML
        for part in ('السجل محفوظ على هذا الجهاز فقط. لا يصلنا منه شيء.', 'الصق ملخّص الجلسة', 'ذكّرني بأخطائي القديمة', 'امسح الكل', 'لماذا سجلّي؟ (اختياري، لكنه مفضّل)',
                     'المحادثة الجديدة لا تتذكّر أخطاءك. سجلّي يحفظها، ويجعل المدرّس يفحصك عليها في المرة القادمة.', 'في آخر الجلسة اكتب للمدرّس: خلصت',
                     'انسخ الملخّص الذي يبدأ بـ NMI-LOG', 'الصقه هنا واضغط «احفظ»', 'هذا ليس ملخّصًا من المدرّس. انسخ الملخّص الذي يبدأ بـ NMI-LOG.',
                     'هذا المتصفح لا يستطيع الحفظ. لن يُحفظ السجل.'):
            self.assertIn(part, texts)
        # the log has codes, not texts
        for part in ("'not_a_summary'", "'no_storage'", "'need_level'"):
            self.assertIn(part, log)
        # every storage call of the log is inside a try
        self.assertEqual(log.count('try {'), log.count('catch ('))
        self.assertGreaterEqual(log.count("try {"), 5)
        for part in ('NMI-LOG', 'المواضيع: ...', 'ضبط: ...', 'غلط: ... (كل غلطة بجملة قصيرة: شو الغلط وبأي موضوع)', 'إذا بدك، انسخ هاد والصقه بالعدّة بصفحة سجلّي. مش إجباري، بس بيخلّيني أفحصك على غلطاتك بالمرة الجاية.',
                     'خلال الجلسة، افحصه على هالغلطات بسؤال واحد على الأقل. ما تذكرها إلا إذا إلها علاقة بالسؤال.', '== غلطات من جلسات قبل ==',
                     'الطالب اختار: ', 'ابدأ بأول وحدة بس. كل رد بوضع واحد بس. لما تخلص الوضع، اسأله إذا جاهز للي بعده، وما تنتقل قبل ما يجاوب.'):
            self.assertIn(part, prompt)

    def test_the_node_tests_of_the_kit_are_all_in_the_package_script(self):
        script = json.loads(read(ROOT / 'package.json'))['scripts']['test:kit']
        for name in ('tests/kit/prompt.test.cjs', 'tests/kit/log.test.cjs', 'playwright.kit.config.cjs'):
            self.assertIn(name, script)
        for path in sorted((ROOT / 'tests' / 'kit').glob('*.test.cjs')):
            self.assertIn(f'tests/kit/{path.name}', script)

    def test_the_pages_workflow_publishes_only_the_kit_and_the_static_demo_and_checks_the_data(self):
        workflow = read(ROOT / '.github' / 'workflows' / 'kit-pages.yml')
        self.assertRegex(workflow, r'path: _site\s')  # a small site folder, not a folder of the repository
        self.assertIn('python3 tools/build_kit.py --check', workflow)
        self.assertIn('actions/deploy-pages@v4', workflow)
        self.assertRegex(workflow, r'pages: write')
        self.assertNotRegex(workflow, r'path: \.\s')  # never the whole repository
        self.assertNotRegex(workflow, r'path: (kit|preview)\s')
        self.assertNotIn('secrets.', workflow)  # no key of any kind
        self.assertIn('workflow_dispatch', workflow)
        # a change of the demo publishes it too
        self.assertIn("- 'preview/**'", workflow)
        self.assertIn("- 'kit/**'", workflow)

    def test_the_lab_demo_is_published_under_lab_with_the_nine_static_files_only(self):
        workflow = read(ROOT / '.github' / 'workflows' / 'kit-pages.yml')
        spec = importlib.util.spec_from_file_location('serve_preview', ROOT / 'tools' / 'serve_preview.py')
        serve_preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(serve_preview)
        allowed = set(serve_preview.ALLOWED)
        self.assertEqual(len(allowed), 9)
        # the files the workflow copies are exactly the files the local preview server allows
        copied = set()
        for names, folder in re.findall(r'for f in ([^;]+); do cp "preview/(assets/)?\$f"', workflow):
            copied.update(folder + name for name in names.split())
        self.assertEqual(copied, allowed)
        self.assertIn('cp -r kit/. _site/', workflow)
        self.assertEqual(len(re.findall(r'cp -r', workflow)), 1)  # nothing else is copied as a folder
        for name in allowed:
            self.assertTrue((ROOT / 'preview' / name).is_file(), name)
        # the guard of the workflow: the exact list of files, and the words that must never be there
        for part in ('diff lab-expected.txt lab-files.txt', 'sk-ant', 'ANTHROPIC_API_KEY', 'local_web', 'live\\.js', 'live\\.css', '.local-data', 'fetch\\('):
            self.assertIn(part, workflow)
        for name in ('live.js', 'live.css', 'local_web.py'):
            self.assertNotIn(f'preview/{name}', workflow)
            self.assertNotIn(f'_site/lab/{name}', workflow)
        # the demo itself: no network, no key, no live server in the files that are published
        for name in sorted(allowed):
            text = read(ROOT / 'preview' / name)
            for word in ('fetch(', 'XMLHttpRequest', 'WebSocket', 'sendBeacon', 'EventSource', 'sk-ant', 'ANTHROPIC_API_KEY', 'live.js', 'live.css', 'local_web', '.local-data'):
                self.assertNotIn(word, text, f'{name}: {word}')
        page = read(ROOT / 'preview' / 'index.html')
        self.assertIn("connect-src 'none'", page)
        self.assertNotIn('nmi-live-server', page)  # the live page is Flask only
        # the one line of the demo, in English and Arabic, and the link in the README
        for part in ('Demo of the first NMI version, with made-up replies. The real version talked to the Claude API on my computer.',
                     'نسخة عرض من أول نسخة من NMI، بردود جاهزة. النسخة الحقيقية كانت تحكي مع Claude على كمبيوتري.'):
            self.assertEqual(page.count(part), 1, part)
        self.assertIn('Best on a computer.', page)
        self.assertIn('الأفضل على كمبيوتر.', page)
        # phones: only the published copy gets a desktop width, so that the whole page shows zoomed out; the source keeps its own viewport
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', page)
        self.assertNotIn('width=1280', page)
        self.assertIn("sed -i 's|<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">|<meta name=\"viewport\" content=\"width=1280\">|' _site/lab/index.html", workflow)
        self.assertIn("grep -c '<meta name=\"viewport\" content=\"width=1280\">' _site/lab/index.html", workflow)  # the deploy fails if the line is not found
        self.assertIn("grep -q 'device-width' _site/lab/index.html", workflow)
        self.assertLess(workflow.index('width=1280'), workflow.index('diff lab-expected.txt lab-files.txt'))
        # the only line that changes the page is the viewport one (the other lines only look: grep, or the list of files)
        changing = [line for line in workflow.splitlines() if '_site/lab/index.html' in line and re.search(r'\bsed\b|\bcp\b|>\s*_site', line)]
        self.assertEqual(len(changing), 1, changing)
        readme = read(ROOT / 'README.md')
        self.assertIn('You can try the demo online: https://nmi-kit.github.io/NMI/lab/', readme)
        self.assertLess(readme.index('## The lab version'), readme.index('https://nmi-kit.github.io/NMI/lab/'))
        self.assertLess(readme.index('https://nmi-kit.github.io/NMI/lab/'), readme.index('![Lab version 1]'))

    def test_the_readme_says_what_the_product_really_is(self):
        readme = read(ROOT / 'README.md')
        for part in ('The real version is not online, because it needs a server and a paid API key. A demo with made-up replies is online, and these screenshots are from it.',
                     "The page is in Arabic, Hebrew and English. The prompt tells the AI to answer in the student's language, with the Hebrew math terms.",
                     'Adding a subject means adding its curriculum files and its own base prompt; the rest of the code stays the same.',
                     '- The Hebrew and English page texts were written with AI and checked by me, not by a professional translator.',
                     '- The lab demo was built for computers; on a phone it shows zoomed out.',
                     'kit/applinks.html    a test page for opening the apps on Android (not linked)',
                     'preview/             the lab demo, published under /lab/',
                     '(index.html, app.js, prompt.js, log.js, i18n.js, data.json)'):
            self.assertIn(part, readme)
        for old in ('It is not online, because', 'Adding a subject means adding curriculum files, not code.'):
            self.assertNotIn(old, readme)
        # the 24 topics: the number in the README is the real one
        data = json.loads(read(build_kit.OUTPUT))
        topics = [topic for subject in data['subjects'] for grade in subject['grades'] for level in grade['levels'] for topic in level['topics']]
        self.assertEqual(len(topics), 101)
        without_hebrew = [topic for topic in topics if not re.search(r'\([^)]*[\u0590-\u05ff][^)]*\)', topic.get('title_full') or '')]
        self.assertEqual(without_hebrew, [])  # every topic has a Hebrew name now, and an English one
        self.assertEqual([topic['id'] for topic in topics if not topic.get('title_en')], [])
        self.assertNotIn('have no Hebrew name', readme)  # the honest-limit line of the 24 topics is gone

    def test_the_base_prompt_has_the_teaching_methods_after_the_hint_ladder_and_the_spaced_review_line(self):
        base = read(ROOT / 'kit' / 'base_prompt.txt').replace('\r\n', '\n')
        self.assertEqual(base.count('== طريقة التعليم =='), 1)
        self.assertLess(base.index('== سلّم التلميحات'), base.index('== طريقة التعليم =='))
        self.assertLess(base.index('== طريقة التعليم =='), base.index('== صور الحلول =='))
        section = base[base.index('== طريقة التعليم =='):base.index('== صور الحلول ==')].strip().split('\n')
        self.assertEqual(len(section), 12)  # the heading and 11 lines
        for start in ('- شرح قصير، وبعدين شغل:', '- من وين جاي القانون:', '- من راسك أول:', '- بأول الجلسة:', '- اخلط:', '- اسأل "ليش؟":',
                      '- الغلط جزء من التعلّم:', '- سهل للكل، وتحدّي بالآخر:', '- طرق تانية:', '- حل طالب تاني:', '- لما يحكي "صعب":'):
            self.assertEqual(len([line for line in section if line.startswith(start)]), 1, start)
        self.assertIn('   - المراجعة الموزّعة: كل موضوع بيرجع بالجدول لمراجعة قصيرة بعد يوم، و3 أيام، وأسبوع.', base)
        self.assertLess(base.index('5) خطة:'), base.index('المراجعة الموزّعة'))
        self.assertLess(base.index('المراجعة الموزّعة'), base.index('== سلّم التلميحات'))
        self.assertEqual(json.loads(read(build_kit.OUTPUT))['base_prompt'], base.strip())
        # the code leaves the section out only for a plan alone
        prompt = read(ROOT / 'kit' / 'prompt.js')
        self.assertIn("if (s.name === TEACHING_SECTION && !hasTeachingMethods(modes)) return;", prompt)
        self.assertIn("const TEACHING_SECTION = 'طريقة التعليم';", prompt)
        # the README does not claim to teach like the universities
        readme = read(ROOT / 'README.md')
        self.assertIn('teaching methods inspired by research at Oxford (tutorials), MIT (active learning), Stanford (Jo Boaler) and Harvard (Peer Instruction)', readme)
        self.assertNotRegex(readme, r'(?i)teaches? like (oxford|mit|stanford|harvard)')

    def test_a_shared_link_shows_what_the_site_does(self):
        html = read(ROOT / 'kit' / 'index.html')
        for tag in ('<meta property="og:type" content="website">', '<meta property="og:site_name" content="NMI">', '<meta property="og:title" content="NMI">',
                    '<meta name="twitter:card" content="summary">', '<meta name="twitter:title" content="NMI">'):
            self.assertIn(tag, html)
        description = re.findall(r'<meta (?:property="og:description"|name="twitter:description") content="([^"]+)">', html)
        self.assertEqual(len(description), 2)
        self.assertEqual(description[0], description[1])
        self.assertIn('ChatGPT', description[0])
        self.assertNotIn('\n', description[0])  # one line
        # the image is the existing icon (a PNG: the apps that show previews do not read an SVG), with its full address
        images = re.findall(r'<meta (?:property="og:image"|name="twitter:image") content="([^"]+)">', html)
        self.assertEqual(images, ['https://nmi-kit.github.io/NMI/icon-512.png'] * 2)
        self.assertTrue((ROOT / 'kit' / 'icon-512.png').is_file())
        # the description of the page for the people who read the source is still the one of the page
        self.assertIn('<meta name="description" content="جهّز نصًّا فيه منهاجك', html)
        # the page still has no other address of its own than the official ones
        self.assertEqual(len(re.findall(r'https://', html)), 2)

    def test_the_ministry_link_is_the_archive_of_past_exams_and_the_readme_describes_the_example_correctly(self):
        app = read(ROOT / 'kit' / 'app.js')
        self.assertIn("var MINISTRY = 'https://meyda.education.gov.il/bagptr/';", app)
        readme = read(ROOT / 'README.md')
        self.assertIn('one example question in the shape of the exam', readme)
        self.assertNotIn('one example question per topic', readme)

    def test_the_back_button_of_the_phone_and_the_two_taps_to_delete_are_in_the_page(self):
        app, texts = read(ROOT / 'kit' / 'app.js'), read(ROOT / 'kit' / 'i18n.js')
        for part in ('history.pushState(entry()', 'history.replaceState(entry()', "window.addEventListener('popstate'", 'history.back()', 'var CONFIRM_MS = 5000;', 'function twoStepButton('):
            self.assertIn(part, app)
        self.assertNotIn('confirm(', app)  # no dialog of the browser
        self.assertNotIn('alert(', app)
        for part in ('متأكد؟ اضغط مرة أخرى للمسح', 'בטוחים? לחצו שוב למחיקה', 'Sure? Tap again to delete'):
            self.assertIn(part, texts)

    def test_the_deploy_guide_names_the_exact_buttons(self):
        guide = read(ROOT / 'docs' / 'KIT.md')
        for part in ('**Settings**', '**Pages**', '**GitHub Actions**', '**Run workflow**', 'https://nmi-kit.github.io/NMI/'):
            self.assertIn(part, guide)

    def test_claude_md_has_the_current_direction(self):
        text = read(ROOT / 'CLAUDE.md')
        self.assertIn('## الاتجاه الحالي', text)
        section = text[text.index('## الاتجاه الحالي'):]
        for part in ('عدّة NMI', '`kit/`', '30/10/2026', 'ChatGPT وClaude وGemini', 'مختبر', 'tools/build_kit.py'):
            self.assertIn(part, section)
        self.assertIn('## قواعد التعديل', text)  # the editing rules stay


if __name__ == '__main__':
    unittest.main()
