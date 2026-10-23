"""Offline tests of the NMI kit data: tools/build_kit.py, kit/data.json and the example bank.

No network, no API. The prompt itself is tested in tests/kit/prompt.test.cjs and the page in tests/kit/kit.spec.cjs.
"""
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
                         sorted(['https://chatgpt.com/', 'https://claude.ai/new', 'https://gemini.google.com/app', 'https://meyda.education.gov.il/']))
        # the Android buttons use Chrome intents of the three official apps, with the official site as the fallback
        self.assertEqual(sorted(re.findall(r"package: '([a-z.]+)'", app)), ['com.anthropic.claude', 'com.google.android.apps.bard', 'com.openai.chatgpt'])
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
        app, prompt = read(ROOT / 'kit' / 'app.js'), read(ROOT / 'kit' / 'prompt.js')
        for part in ('عندي امتحان قديم أو ورقة عمل من أستاذي', 'الأحسن: بيحط البرومبت جوا التطبيق مباشرة.',
                     '💡 ليش كل مادة أو موضوع جديد بمحادثة جديدة؟', '📎 الصق البرومبت، وبعدين اضغط + بالتطبيق',
                     'ملاحظة للمدرّس (اختياري)', 'انسخنا البرومبت. الصقه بالتطبيق.', 'navigator.userAgent'):
            self.assertIn(part, app)
        for part in ('الطالب رفعلك صورة أو ملف لامتحان قديم أو ورقة عمل من أستاذه.',
                     'إذا الطالب ما رفع الملف، اطلبه منه أول.', "'== ملاحظة من الطالب =='", 'اتبع هالملاحظة بطريقة الشرح والأمثلة والتركيز.',
                     'const MAX_NOTE = 200;'):
            self.assertIn(part, prompt)
        guide = read(ROOT / 'docs' / 'KIT.md')
        for part in ('ملف الأستاذ', 'ملاحظة للمدرّس', 'أندرويد', 'محادثة جديدة'):
            self.assertIn(part, guide)

    def test_the_pages_workflow_publishes_only_the_kit_folder_and_checks_the_data(self):
        workflow = read(ROOT / '.github' / 'workflows' / 'kit-pages.yml')
        self.assertRegex(workflow, r'path: kit\s')
        self.assertIn('python3 tools/build_kit.py --check', workflow)
        self.assertIn('actions/deploy-pages@v4', workflow)
        self.assertRegex(workflow, r'pages: write')
        self.assertNotRegex(workflow, r'path: \.\s')  # never the whole repository
        self.assertNotIn('secrets.', workflow)  # no key of any kind
        self.assertIn('workflow_dispatch', workflow)

    def test_the_deploy_guide_names_the_exact_buttons(self):
        guide = read(ROOT / 'docs' / 'KIT.md')
        for part in ('**Settings**', '**Pages**', '**GitHub Actions**', '**Run workflow**', 'https://m0502223641-coder.github.io/NMI/'):
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
