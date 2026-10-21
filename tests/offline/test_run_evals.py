"""Eval runner contracts with fake models: no paid request, no network, no persistent storage."""
import io
import contextlib
import json
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests' / 'evals'))
from claude_provider import ClaudeError
from learning_result import LearningResult
from tools import run_evals as ev
import hard_solutions
from local_web import valid_profile

MODEL = 'claude-fake-tutor'
JUDGE_MODEL = 'claude-fake-judge'
GOOD_ENV = {'NMI_ENABLE_AI': '1', 'NMI_ENABLE_ANTHROPIC_PAID': '1',
            'NMI_CLAUDE_MODEL': MODEL, 'NMI_EVAL_JUDGE_MODEL': JUDGE_MODEL}
USAGE = {'input_tokens': 100, 'output_tokens': 40, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 10}


def case(**changes):
    value = {'id': 'x-1', 'category': 'wrong_sign',
             'profile': {'grade': 10, 'country': 'Israel', 'units': 3, 'language': 'ar', 'subject': 'math'},
             'conversation': [{'role': 'user', 'content': 'تمرين'},
                              {'role': 'assistant', 'content': '5 - 2x = 11'},
                              {'role': 'user', 'content': 'x = 3'}],
             'intent': 'answer', 'expected_behavior': 'يحدد الخطأ ولا يعطي الحل',
             'math': {'expected': ['-3'], 'mode': 'must_withhold'},
             'expect_attempt': {'recorded': True, 'correct': False}}
    return value | changes


def tutor_returning(reply, **fields):
    result = LearningResult(reply=reply, **(dict(is_attempt=True, subject='mathematics', topic='linear equations',
                                                 skill='division by a negative', correct=False, hint_used=False,
                                                 mistake_type='sign') | fields))
    client = SimpleNamespace(model=MODEL, usage=dict(USAGE, provider='claude', complete=True),
                             responses=None, close=Mock())
    client.responses = SimpleNamespace(parse=Mock(return_value=SimpleNamespace(output_parsed=result, status='completed')))
    return client


def judge_returning(score=9, reasons='ممتاز', tags=()):
    return Mock(return_value=(ev.JudgeVerdict(score=score, reason=reasons, weaknesses=list(tags)), dict(USAGE)))


class CaseFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = ev.load_cases()

    def test_twenty_five_arabic_math_cases_mostly_three_units(self):
        base = [c for c in self.cases if 'tier' not in c]
        self.assertEqual(len(base), 25)
        self.assertEqual(len(self.cases), 60)  # 25 basic + 27 hard + 3 conversation + 5 mode
        self.assertEqual(len({c['id'] for c in self.cases}), 60)
        units = [c['profile']['units'] for c in base]
        self.assertGreater(units.count(3), len(units) / 2)
        self.assertTrue(set(units) <= {3, 4, 5} and 5 in units)
        for c in base:
            self.assertEqual(c['profile']['grade'], 10)
        for c in self.cases:
            self.assertEqual(c['profile']['language'], 'ar')
            self.assertEqual(c['profile']['subject'], 'math')
            self.assertEqual(c['profile']['country'], 'Israel')
            self.assertRegex(' '.join(m['content'] for m in c['conversation']), r'[؀-ۿ]')

    def test_required_fields_and_alternating_conversation(self):
        for c in self.cases:
            with self.subTest(case=c['id']):
                self.assertTrue({'id', 'category', 'profile', 'conversation', 'intent', 'expected_behavior',
                                 'math', 'expect_attempt'} <= set(c))
                roles = [m['role'] for m in c['conversation']]
                self.assertEqual(roles[0], 'user')
                self.assertEqual(roles[-1], 'user')
                self.assertTrue(all(a != b for a, b in zip(roles, roles[1:])))
                self.assertIn(c['intent'], {'question', 'answer', 'hint', 'confusion'})

    def test_every_requested_scenario_is_covered(self):
        self.assertTrue({'wrong_sign', 'wrong_fractions', 'confusion_twice', 'dialect_typos', 'out_of_scope',
                         'ready_solution', 'valid_odd_method', 'missing_info', 'instruction_override',
                         'precise_calc'} <= {c['category'] for c in self.cases})
        twice = [c for c in self.cases if c['category'] == 'confusion_twice']
        for c in twice:
            self.assertEqual(sum(m['content'].count('مش فاهم') + m['content'].count('لسا مش') for m in c['conversation']
                                 if m['role'] == 'user') >= 2, True)

    def test_expected_math_is_valid_sympy_and_consistent_with_attempt(self):
        for c in self.cases:
            spec = c['math']
            if spec is None:
                continue
            with self.subTest(case=c['id']):
                self.assertIn(spec['mode'], {'must_withhold', 'must_state'})
                self.assertTrue(all(ev.to_expr(value) is not None for value in spec['expected']))
        wrong = next(c for c in self.cases if c['id'] == 'm10-sign-01')
        self.assertTrue(ev.same(ev.to_expr('x'), ev.to_expr('x')))
        self.assertFalse(ev.same(ev.to_expr(wrong['math']['expected'][0]), ev.to_expr('3')))

    def test_reference_answers_are_mathematically_right(self):
        sympy = ev._sympy()[0]
        x = sympy.Symbol('x')
        self.assertEqual(sympy.solve(5 - 2 * x - 11, x), [-3])
        self.assertEqual(sympy.simplify(3 * x - (2 * x - 5) - (x + 5)), 0)
        self.assertEqual((x ** 2 - 4 * x).subs(x, -2), 12)
        self.assertEqual(sympy.Rational(1, 2) + sympy.Rational(1, 3), sympy.Rational(5, 6))
        self.assertEqual(sympy.Rational(3, 5) / sympy.Rational(9, 10), sympy.Rational(2, 3))
        self.assertEqual(sympy.simplify((x ** 2 - 9) / (x - 3) - (x + 3)), 0)
        self.assertEqual(sympy.solve(3 * x + 4 - 16, x), [4])
        self.assertEqual(sympy.solve(4 * (x - 2) + 3 - (2 * x + 9), x), [7])
        self.assertEqual(sympy.solve(-2 * (x + 3) - (4 * x - 18), x), [2])
        self.assertEqual(sympy.solve(3 * x + 6 - 15, x), [3])
        self.assertEqual(12 / sympy.Rational(3, 4), 16)
        self.assertEqual(sympy.solve(5 * x - 3 - 12, x), [3])
        self.assertEqual(sympy.sqrt(72), 6 * sympy.sqrt(2))
        self.assertEqual(sympy.sqrt(48) + sympy.sqrt(12), 6 * sympy.sqrt(3))
        self.assertEqual(sympy.Rational(2, 3) + sympy.Rational(3, 4), sympy.Rational(17, 12))
        self.assertEqual(sympy.expand((sympy.sqrt(3) + 1) ** 2), 4 + 2 * sympy.sqrt(3))


LEVELS = [(grade, units) for grade in (10, 11, 12) for units in (3, 4, 5)]


class HardCaseTests(unittest.TestCase):
    """27 hard cases: 3 per grade x units, topics from the curriculum files, answers checked by sympy."""

    @classmethod
    def setUpClass(cls):
        cls.cases = [c for c in ev.load_cases() if c.get('tier') == 'hard']

    def test_three_cases_for_each_grade_and_units_with_one_of_each_kind(self):
        self.assertEqual(len(self.cases), 27)
        for grade, units in LEVELS:
            with self.subTest(grade=grade, units=units):
                level = [c for c in self.cases if (c['profile']['grade'], c['profile']['units']) == (grade, units)]
                self.assertEqual(sorted(c['category'] for c in level), ['hard_multistep', 'hard_trap', 'hard_why'])
                self.assertEqual([c['id'] for c in level], [f'h{grade}u{units}-{n}' for n in (1, 2, 3)])

    def test_topic_id_exists_in_the_matching_curriculum_file(self):
        for c in self.cases:
            with self.subTest(case=c['id']):
                grade, units = c['profile']['grade'], c['profile']['units']
                text = (ROOT / 'curriculum' / 'math' / f'grade{grade}' / f'{units}units.md').read_text(encoding='utf-8')
                self.assertRegex(c['topic'], rf'^m{grade}-{units}-\d\d$')
                self.assertIn(c['topic'] + ' ', text)
                self.assertIn(c['topic'], c['provenance'])

    def test_kinds_set_the_intent_and_attempt_expectation(self):
        # h12u4-3 has no numeric answer (the correct result is "no minimum"); sympy facts cover it instead.
        no_numeric_answer = {'h12u4-3'}
        for c in self.cases:
            with self.subTest(case=c['id']):
                roles = [m['role'] for m in c['conversation']]
                if c['category'] == 'hard_why':
                    self.assertEqual((c['intent'], c['expect_attempt']), ('question', {'recorded': False}))
                else:
                    self.assertEqual((c['intent'], c['expect_attempt']), ('answer', {'recorded': True, 'correct': False}))
                    self.assertEqual(roles, ['user', 'assistant', 'user'])
                    if c['id'] in no_numeric_answer:
                        self.assertIsNone(c['math'])
                    else:
                        self.assertEqual(c['math']['mode'], 'must_withhold')
                self.assertGreater(len(c['expected_behavior']), 80)

    def test_h10u5_2_allows_the_general_solution_because_the_curriculum_has_it(self):
        case = next(c for c in self.cases if c['id'] == 'h10u5-2')
        text = (ROOT / 'curriculum' / 'math' / 'grade10' / '5units.md').read_text(encoding='utf-8')
        self.assertIn('الحل العام', text.split('m10-5-11')[1].split('###')[0])
        self.assertIn('الحل العام', case['expected_behavior'])
        self.assertIn('مسموح', case['expected_behavior'])
        self.assertNotIn('ولا يدخل بالحل العام', case['expected_behavior'])

    def test_every_solution_has_a_case_and_answers_match_sympy(self):
        self.assertEqual(set(hard_solutions.SOLUTIONS), {c['id'] for c in self.cases})
        for c in self.cases:
            with self.subTest(case=c['id']):
                solved = hard_solutions.SOLUTIONS[c['id']]()
                for number, fact in enumerate(solved['facts']):
                    self.assertTrue(bool(fact), f'fact {number} is false')
                expected = (c['math'] or {}).get('expected', [])
                self.assertEqual(len(expected), len(solved['answers']))
                for text, answer in zip(expected, solved['answers']):
                    self.assertTrue(ev.same(ev.to_expr(text), answer), f'{text} != {answer}')

    def test_the_conversation_itself_never_contains_the_withheld_answer(self):
        # Otherwise the tutor repeating the student's own correct step would be scored as a leak.
        for c in self.cases:
            if c['math']:
                for message in c['conversation']:
                    with self.subTest(case=c['id'], role=message['role']):
                        self.assertFalse(ev.check_math(message['content'], c['math'])['revealed'])

    def test_a_reply_that_reveals_each_reference_answer_is_caught(self):
        for c in self.cases:
            if c['math']:
                with self.subTest(case=c['id']):
                    reply = 'الجواب: ' + c['math']['expected'][0].replace('sqrt', '√').replace('*', '')
                    self.assertTrue(ev.check_math(reply, c['math'])['revealed'], reply)


EGYPTIAN_REPLY = 'هنبدأ بمعادلات الدرجة الأولى. إيه رأيك نشوف مثال؟ عشان كده لازم نفهم الفكرة'
PALESTINIAN_REPLY = 'أهلين! خلّينا نبدأ بمعادلة بسيطة. شو بتتوقع يكون x لو 2x = 10؟'


class ConversationCaseTests(unittest.TestCase):
    """Three cases from the owner's own session: dialect, moving from 3 to 5 units, a consistent quadratic example."""

    @classmethod
    def setUpClass(cls):
        cls.cases = {c['id']: c for c in ev.load_cases() if c.get('tier') == 'conversation'}

    def test_the_three_cases_and_their_profiles(self):
        self.assertEqual(set(self.cases), {'conv-dialect-01', 'conv-target-01', 'conv-quadratic-01'})
        for c in self.cases.values():
            with self.subTest(case=c['id']):
                self.assertEqual([m['role'] for m in c['conversation']], ['user'])
                self.assertRegex(c['conversation'][0]['content'], '[\u0600-\u06FF]')
                self.assertEqual((c['intent'], c['expect_attempt'], c['math']), ('question', {'recorded': False}, None))
                self.assertIn('سؤال واحد', c['expected_behavior'])
                self.assertIn('فلسطيني', c['expected_behavior'])
                self.assertIn('محادثة المالك', c['provenance'])
                # The profile is one the website itself would accept, so its curriculum file really loads.
                server_profile = {'country': 'IL', 'grade': c['profile']['grade'], 'subject': 'math', 'units': c['profile']['units']}
                if 'target_units' in c['profile']:
                    server_profile['target_units'] = c['profile']['target_units']
                self.assertTrue(valid_profile(server_profile), server_profile)
        self.assertEqual(self.cases['conv-dialect-01']['profile']['units'], 3)
        self.assertEqual((self.cases['conv-target-01']['profile']['units'], self.cases['conv-target-01']['profile']['target_units']), (3, 5))

    def test_dialect_case_forbids_egyptian_words_only_as_whole_words(self):
        case = self.cases['conv-dialect-01']
        found = ev.check_text(EGYPTIAN_REPLY, case)
        self.assertEqual(set(found['forbidden']), {'هنبدأ', 'إيه', 'عشان كده', 'كده'})  # كده is a word of its own too
        self.assertFalse(found['ok'])
        self.assertTrue(ev.check_text(PALESTINIAN_REPLY, case)['ok'])
        # Egyptian "this" (ده, دي) as a word is caught, but not inside Palestinian words such as هاد or الدي...
        self.assertEqual(ev.check_text('شو ده؟ وكمان دي', case)['forbidden'], ['ده', 'دي'])
        self.assertEqual(ev.check_text('هاد منيح، وبعدين هاي كمان. بيده وعدّي والدين', case)['forbidden'], [])

    def test_target_case_needs_three_topics_of_the_target_file_and_no_missing_curriculum_claim(self):
        case = self.cases['conv-target-01']
        five = (ROOT / 'curriculum' / 'math' / 'grade10' / '5units.md').read_text(encoding='utf-8')
        three = (ROOT / 'curriculum' / 'math' / 'grade10' / '3units.md').read_text(encoding='utf-8')
        words = case['must_mention']['any_of']
        self.assertEqual(case['must_mention']['at_least'], 3)
        for word in words:  # every keyword is a topic of the 5-unit file that the 3-unit file does not have
            self.assertIn(word, five)
            self.assertNotIn(word, three)
        plan = 'خطة: أولاً الهندسة التحليلية، بعدين دوال القوة والتحويلات، وبعدها التفاضل. بأي موضوع بدك تبدأ؟'
        self.assertEqual(ev.check_text(plan, case)['mentioned'], ['التحليلية', 'دوال القوة', 'التحويلات', 'التفاضل'])
        self.assertTrue(ev.check_text(plan, case)['ok'])
        thin = ev.check_text('لازم تتعلم التفاضل ودالة الجذر. شو بدك تبدأ؟', case)
        self.assertEqual((len(thin['mentioned']), thin['plan_ok'], thin['ok']), (2, False, False))
        denied = ev.check_text('للأسف ما عندي منهاج لـ 5 وحدات. التفاضل والدائرة وتاليس مهمين', case)
        self.assertEqual(denied['forbidden'], ['ما عندي منهاج'])
        self.assertFalse(denied['ok'])

    def test_sympy_facts_for_the_quadratic_example(self):
        for number, fact in enumerate(hard_solutions.CONVERSATION_SOLUTIONS['conv-quadratic-01']()['facts']):
            self.assertTrue(bool(fact), f'fact {number} is false')

    def test_the_tutor_receives_the_target_level_and_the_dialect_rule_for_these_cases(self):
        client = tutor_returning(PALESTINIAN_REPLY, is_attempt=False, subject=None, topic=None, skill=None,
                                 correct=None, hint_used=None, mistake_type=None)
        result = ev.evaluate_case(self.cases['conv-target-01'], MODEL, lambda m: client, judge_returning(9))
        kwargs = client.responses.parse.call_args.kwargs
        self.assertIn('رياضيات، الصف العاشر، 3 وحدات', kwargs['cache_prefix'])
        self.assertIn('# TARGET LEVEL CURRICULUM (5 units)', kwargs['cache_prefix'])
        self.assertIn('رياضيات، الصف العاشر، 5 وحدات', kwargs['cache_prefix'])
        self.assertIn('LANGUAGE AND DIALECT', kwargs['instructions'])
        self.assertFalse(result['passed'])  # the Palestinian reply names no topic of the 5-unit file
        self.assertIn('missing_plan', result['weaknesses'])

    def test_egyptian_reply_fails_even_with_a_perfect_judge_score_and_shows_in_the_report(self):
        client = tutor_returning(EGYPTIAN_REPLY, is_attempt=False, subject=None, topic=None, skill=None,
                                 correct=None, hint_used=None, mistake_type=None)
        judge = judge_returning(10)
        result = ev.evaluate_case(self.cases['conv-dialect-01'], MODEL, lambda m: client, judge)
        self.assertFalse(result['passed'])
        self.assertIn('forbidden_phrase', result['weaknesses'])
        self.assertIn('forbidden phrases: هنبدأ', judge.call_args.args[2])
        meta = {'date': '2026-10-20', 'model': MODEL, 'judge_model': JUDGE_MODEL, 'curriculum': 'اختبار'}
        self.assertIn('عبارات ممنوعة: هنبدأ', ev.render_report(meta, [result]))
        self.assertNotIn('forbidden_phrase', ev.JUDGE_TAGS)  # found by code, not by the judge
        good = tutor_returning(PALESTINIAN_REPLY, is_attempt=False, subject=None, topic=None, skill=None,
                               correct=None, hint_used=None, mistake_type=None)
        self.assertTrue(ev.evaluate_case(self.cases['conv-dialect-01'], MODEL, lambda m: good, judge_returning(9))['passed'])

    def test_target_units_reach_ask_ai_through_the_runner(self):
        self.assertEqual(ev.curriculum_options({'units': 3, 'subject': 'math', 'target_units': 5}),
                         {'subject': 'math', 'units': 3, 'target_units': 5})
        self.assertEqual(ev.curriculum_options({'units': 3, 'subject': 'math'}), {'subject': 'math', 'units': 3})


SECTIONS = ['## الفكرة ببساطة', '## المصطلحات', '## مثال من الحياة', '## مثالين محلولين خطوة خطوة', '## الغلطة الشائعة', '## كيف بييجي بالبجروت']
EXPLAIN_REPLY = """## الفكرة ببساطة
الميل بيقلك قديش بتتغيّر y لما x بتزيد واحد.

## المصطلحات
- **المتغير**: رقم بيتغيّر
- **الثابت**: رقم ما بيتغيّر
- **الميل**: معدل التغيّر

## مثال من الحياة
كل ساعة شغل بتزيد 40 شيكل.

## مثالين محلولين خطوة خطوة
1. من (0, 5) إلى (2, 9): الفرق بـ y هو 4
2. الفرق بـ x هو 2

$$ m = 4 / 2 = 2 $$

## الغلطة الشائعة
قلب ترتيب الطرح.

## كيف بييجي بالبجروت
بالنموذج الخطي m10-3-12.

شو رأيك نجرب مثال تاني؟"""
PLAN_REPLY = """افترضت إنه عندك 8 أسابيع.

| الأسبوع | الموضوع | شو بتعمل |
|---|---|---|
| 1 | m10-3-01 استنتاج من معلومات | قراءة رسوم |
| 2 | m10-3-02 تمثيلات إحصائية | جداول |
| 3 | m10-3-03 الإحصاء | معدل ووسيط |
| 4 | m10-3-04 الاحتمال | فضاء عينة |
| 5 | m10-3-06 محيطات | فيثاغورس |
| 6 | m10-3-08 مساحات | مثلثات |
| 7 | m10-3-12 النموذج الخطي | الميل |
| 8 | m10-3-13 مسائل كلامية | ربح وخسارة |

استمارة العاشر 35173 وبجروت نهاية الحادي عشر 35371.

كم أسبوع باقي عندك فعلاً؟"""


class ModeCaseTests(unittest.TestCase):
    """Five cases for the explain and plan modes; the judge is told the mode and code checks the headings and length."""

    @classmethod
    def setUpClass(cls):
        cls.cases = {c['id']: c for c in ev.load_cases() if c.get('tier') == 'mode'}

    def test_the_five_cases_with_the_requested_messages(self):
        messages = {cid: c['conversation'][0]['content'] for cid, c in self.cases.items()}
        self.assertEqual(messages, {
            'mode-explain-quadratic-01': 'مش فاهم الدالة التربيعية', 'mode-explain-linear-01': 'مش فاهم الدالة الخطية',
            'mode-explain-slope-01': 'شو يعني ميل ولشو منستعمله', 'mode-explain-constant-y-01': 'شو يعني رقم ثابت وشو هو y',
            'mode-plan-01': 'بدي خطة للبجروت'})
        for case in self.cases.values():
            with self.subTest(case=case['id']):
                self.assertEqual((case['profile']['grade'], case['profile']['units'], case['profile']['subject']), (10, 3, 'math'))
                self.assertEqual((case['intent'], case['expect_attempt'], case['math']), ('question', {'recorded': False}, None))
                self.assertIn(case['mode'], {'explain', 'plan'})
                self.assertIn('بالظبط', case['forbidden_phrases'])
                self.assertIn('فلسطينية', case['expected_behavior'])
                self.assertIn('سؤال واحد', case['expected_behavior'])
                self.assertTrue(valid_profile({'country': 'IL', 'grade': 10, 'subject': 'math', 'units': 3}))
        self.assertEqual([c['mode'] for cid, c in self.cases.items()], ['explain'] * 4 + ['plan'])

    def test_every_dialect_list_forbids_the_egyptian_bil_zabt(self):
        for case in ev.load_cases():
            if case.get('forbidden_phrases') and 'هنبدأ' in case['forbidden_phrases']:
                with self.subTest(case=case['id']):
                    self.assertIn('بالظبط', case['forbidden_phrases'])

    def test_explain_cases_need_all_six_headings_and_at_most_the_word_limit(self):
        case = self.cases['mode-explain-slope-01']
        self.assertEqual(case['max_words'], 520)  # 400 words and the Markdown signs
        good = ev.check_text(EXPLAIN_REPLY, case)
        self.assertTrue(good['ok'], good)
        self.assertEqual(len(good['checks'][0]['mentioned']), 6)
        self.assertEqual([check['ok'] for check in good['checks']], [True, True])  # headings, and m10-3-12
        missing = ev.check_text(EXPLAIN_REPLY.replace('## الغلطة الشائعة', '## ملاحظة'), case)
        self.assertEqual((missing['plan_ok'], missing['ok']), (False, False))
        self.assertNotIn('الغلطة الشائعة', missing['checks'][0]['mentioned'])
        no_topic = ev.check_text(EXPLAIN_REPLY.replace('m10-3-12', 'm10-9-99').replace('النموذج الخطي', 'x'), case)
        self.assertEqual([check['ok'] for check in no_topic['checks']], [True, False])
        long_reply = EXPLAIN_REPLY + ' كلمة' * 600
        long = ev.check_text(long_reply, case)
        self.assertEqual((long['short_enough'], long['ok']), (False, False))
        self.assertGreater(long['words'], 520)
        self.assertLessEqual(good['words'], 520)

    def test_plan_case_needs_topic_ids_exam_number_and_weeks(self):
        case = self.cases['mode-plan-01']
        good = ev.check_text(PLAN_REPLY, case)
        self.assertTrue(good['ok'], good)
        self.assertEqual([len(check['mentioned']) for check in good['checks']], [8, 2, 2])
        thin = ev.check_text('خطة: الأسبوع الأول m10-3-01، التاني m10-3-02.', case)
        self.assertEqual([check['ok'] for check in thin['checks']], [False, False, True])
        no_exam = ev.check_text(PLAN_REPLY.replace('35173', '').replace('35371', ''), case)
        self.assertEqual([check['ok'] for check in no_exam['checks']], [True, False, True])
        self.assertFalse(ev.check_text(PLAN_REPLY + ' بالظبط', case)['ok'])

    def test_a_valid_curriculum_id_exists_for_every_topic_the_plan_must_name(self):
        text = (ROOT / 'curriculum' / 'math' / 'grade10' / '3units.md').read_text(encoding='utf-8')
        for word in self.cases['mode-plan-01']['must_mention'][0]['any_of']:
            self.assertIn(f'#### {word} ', text)
        self.assertIn('35173', text)
        self.assertIn('35371', text)
        for word in self.cases['mode-explain-slope-01']['must_mention'][0]['any_of']:
            self.assertIn(word if word != 'محلولين' else 'محلولين', ' '.join(SECTIONS))

    def explain_client(self, reply, chosen):
        client = tutor_returning(reply, is_attempt=False, subject=None, topic=None, skill=None,
                                 correct=None, hint_used=None, mistake_type=None)
        client.last_result = SimpleNamespace(mode=chosen)
        return client

    def test_the_chosen_mode_must_match_and_the_judge_is_told_both(self):
        case = self.cases['mode-explain-slope-01']
        judge = judge_returning(9)
        ok = ev.evaluate_case(case, MODEL, lambda m: self.explain_client(EXPLAIN_REPLY, 'explain'), judge)
        self.assertTrue(ok['passed'], ok)
        self.assertEqual(ok['mode'], {'expected': 'explain', 'chosen': 'explain', 'ok': True})
        self.assertIn('The tutor chose the mode: explain (the case expects: explain).', judge.call_args.args[2])
        self.assertIn(f"The reply has {ok['text_checks']['words']} words (limit 520).", judge.call_args.args[2])
        wrong = ev.evaluate_case(case, MODEL, lambda m: self.explain_client(EXPLAIN_REPLY, 'practice'), judge_returning(10))
        self.assertFalse(wrong['passed'])
        self.assertIn('wrong_mode', wrong['weaknesses'])
        # An unknown chosen mode (a fake client without last_result) is not held against the tutor.
        unknown = ev.evaluate_case(case, MODEL, lambda m: tutor_returning(EXPLAIN_REPLY, is_attempt=False, subject=None, topic=None,
                                                                          skill=None, correct=None, hint_used=None, mistake_type=None),
                                   judge_returning(9))
        self.assertTrue(unknown['passed'])
        self.assertEqual(unknown['mode'], {'expected': 'explain', 'chosen': None, 'ok': True})

    def test_missing_headings_or_length_fail_the_case_even_with_a_perfect_judge_score(self):
        case = self.cases['mode-explain-slope-01']
        thin = ev.evaluate_case(case, MODEL, lambda m: self.explain_client('الميل هو معدل التغيّر. شو رأيك نجرب؟', 'explain'), judge_returning(10))
        self.assertFalse(thin['passed'])
        self.assertIn('missing_parts', thin['weaknesses'])
        long = ev.evaluate_case(case, MODEL, lambda m: self.explain_client(EXPLAIN_REPLY + ' كلمة' * 600, 'explain'), judge_returning(10))
        self.assertFalse(long['passed'])
        self.assertIn('too_long', long['weaknesses'])
        for tag in ('missing_parts', 'wrong_mode', 'too_long', 'missing_plan', 'forbidden_phrase'):
            self.assertNotIn(tag, ev.JUDGE_TAGS)
            self.assertIn(tag, ev.WEAKNESSES)
        meta = {'date': '2026-10-21', 'model': MODEL, 'judge_model': JUDGE_MODEL, 'curriculum': 'اختبار'}
        report = ev.render_report(meta, [thin, long])
        self.assertIn('كلمة والحد 520', report)
        self.assertIn('ذكر', report)

    def test_the_judge_prompt_and_rules_treat_a_long_explanation_as_correct(self):
        case = self.cases['mode-explain-linear-01']
        prompt = ev.judge_prompt(case, 'رد', 'facts')
        self.assertIn('<mode_expected>explain</mode_expected>', prompt)
        self.assertNotIn('<mode_expected>', ev.judge_prompt(case | {'mode': None}, 'رد', 'facts'))
        system = ev.JUDGE_SYSTEM
        for part in ("Every reply has a mode (explain, practice or plan)", "mode the case expects",
                     "A long, complete, well-ordered Markdown explanation of up to about 400 words",
                     "is CORRECT", "Never lower the score for", "length, headings, bullets, tables or the number of ideas",
                     'never use "bad_pacing" for it', "ignore that limit", "honest about the curriculum",
                     "numbers different from the student's", "split into weeks", "form number from the file"):
            self.assertIn(part, system)
        self.assertTrue(system.endswith(ev.tutor_rules))  # the judge still reads the approved rules, including the modes
        self.assertIn('# TEACHING MODES', system)

    def test_the_chosen_mode_comes_from_the_real_provider(self):
        from claude_provider import ClaudeProvider
        self.assertIsNone(ClaudeProvider(MODEL).last_result)


class MathCheckTests(unittest.TestCase):
    def test_leaked_answer_is_detected_in_arabic_variable_and_digits(self):
        spec = {'expected': ['4'], 'mode': 'must_withhold'}
        self.assertTrue(ev.check_math('الحل: س = ٤', spec)['revealed'])
        self.assertFalse(ev.check_math('أول خطوة: 3س = 16 - 4. شو ناتج 16 - 4؟', spec)['revealed'])

    def test_equivalent_forms_and_radicals(self):
        self.assertTrue(ev.check_math('x = -3', {'expected': ['-3'], 'mode': 'must_withhold'})['revealed'])
        self.assertTrue(ev.check_math('الناتج 10/12 + 7/12 = 17/12', {'expected': ['17/12'], 'mode': 'must_state'})['stated'])
        self.assertTrue(ev.check_math('√72 = 6√2', {'expected': ['6*sqrt(2)'], 'mode': 'must_state'})['stated'])
        self.assertTrue(ev.check_math('إذاً 12/2 = 6 وبالتالي 6√3', {'expected': ['6*sqrt(3)'], 'mode': 'must_withhold'})['revealed'])
        self.assertFalse(ev.check_math('نجمع الجذور بعد التبسيط 4√3 + 2√3', {'expected': ['6*sqrt(3)'], 'mode': 'must_withhold'})['revealed'])
        self.assertTrue(ev.check_math('= x + 3', {'expected': ['x+3'], 'mode': 'must_withhold'})['revealed'])
        self.assertTrue(ev.check_math('نعم الجواب \\frac{17}{12} صحيح', {'expected': ['17/12'], 'mode': 'must_state'})['stated'])

    def test_percent_signs_and_letter_glued_numbers_are_not_false_equations(self):
        # Exact tutor replies from report-grade11.md (h11u3-1: "3 = 60") and report-grade12.md (h12u5-1: "2 = -2").
        growth_reply = ("الخطأ هون إنك جمعت النسب: 20% × 3 = 60%. هاد الحل بيصير صح بس لو النقصان 20% من السعر الأصلي كل سنة (نقصان ثابت). "
                        "بس بمسألة اضمحلال، النقصان 20% كل سنة بيكون من سعر السنة اللي قبلها، والسعر بعد كل سنة بيصير أصغر، فالنقصان بالشيكل بيصغر كمان. "
                        "عشان هيك النسب ما بتنجمع، وبنضرب بمعامل الاضمحلال بدل الجمع. تلميح: إذا النقصان 20%، كم % من السعر بيضل بعد سنة وحدة. "
                        "والمعامل بيطلع من هاد الرقم.\n\nبعد السنة الأولى بس، كم بيصير سعر السيارة؟")
        complex_reply = ("في عندك خطأ حسابي واحد بالخطوة الأولى. الفكرة عندك صحيحة: كتبت العدد بالصورة القطبية، ورفعته للقوة بضرب الزاوية، وهاي طريقة ممتازة. "
                         "الخطأ: لما رفعت المعامل 2 للقوة 6 ضربته بدل ما ترفعه. نظرية دي موافر بتقول إنو الزاوية بتنضرب بالقوة، بس الطول بينرفع للقوة. "
                         "أما الجزء التاني (1 − i)⁴ = −4 فهو سليم، وانتبهت إنو (1 − i)² = −2i، وهاي خطوة ذكية.\n\n"
                         "بعد ما تصحح هالخطوة، شو بتصير قيمة 2⁶ اللي بتطلع بدل الرقم 2 في الناتج؟")
        cases = ((growth_reply, ['25600', '24400'], '20% × 3 سنين = 60%'),
                 (complex_reply, ['-16', '64'], '(1 − i)² = −2i'))
        for reply, expected, quoted in cases:
            for known in ([], [quoted]):
                with self.subTest(reply=reply[:20], known=bool(known)):
                    result = ev.check_math(reply, {'expected': expected, 'mode': 'must_withhold'}, known)
                    self.assertEqual(result['arithmetic_errors'], [])
                    self.assertTrue(result['ok'])
        # Numbers glued to letters belong to a longer expression, even a correct statement of one.
        for text in ('BC² = 7² + 8² − 2·7·8 = 57', 'z = 1 + i√3 و z² = −2 + 2i√3', 'الحد 2·7·8·cos 60° كبير'):
            with self.subTest(text=text):
                self.assertEqual(ev.check_math(text, None)['arithmetic_errors'], [])
        # A real false equation next to them, with or without a percent sign elsewhere, is still caught.
        self.assertEqual(ev.check_math('z = 2i و 2 + 2 = 5 ونسبة 20% × 3 = 60%', None)['arithmetic_errors'], ['2 + 2 = 5'])
        # A leaked percentage answer is still a leak.
        spec = {'expected': ['65'], 'mode': 'must_withhold'}
        self.assertTrue(ev.check_math('الجواب 65%', spec)['revealed'])
        self.assertTrue(ev.check_math('x = 65%', spec)['revealed'])
        self.assertFalse(ev.check_math('نسبة الربح 20% × 3', spec)['revealed'])

    def test_negative_leaked_answer_after_a_keyword_is_detected(self):
        spec = {'expected': ['-16'], 'mode': 'must_withhold'}
        self.assertTrue(ev.check_math('الجواب: −16', spec)['revealed'])
        self.assertTrue(ev.check_math('الناتج يساوي -16', spec)['revealed'])
        self.assertFalse(ev.check_math('الناتج 16', spec)['revealed'])

    def test_function_calls_and_rejected_claims_are_not_false_equations(self):
        # Exact tutor replies from the h10u4-1 and h10u5-1 reports that were wrongly marked as arithmetic errors.
        derivative_reply = ("شغلك منظّم وخطواتك واضحة، وحساب f(2) = 6 صحيح 👏 بس في خطأ بالمشتقة: كتبت f'(x) = 3x² − 6x + 5x، "
                            "يعني اشتقّيت الحدّ الأخير 5x وبقي 5x. مشتقة 5x بتطلع عدد ثابت، مش 5x. لاحظ كيف اشتقّيت 3x² وطلع 6x، "
                            "وكيف اشتقّيت x³ وطلع 3x². بما إن باقي طريقتك (معادلة المماس وإيجاد التقاطع مع محور x) سليمة، "
                            "أول ما تصلّح المشتقة بتتغيّر الأرقام بس. جرّب: شو مشتقة 5x، وبعدين شو بتصير f'(2)؟")
        cosine_reply = ("محاولة منيحة، وبدأت صح: كتبت القانون صح وعوّضت الأضلاع والزاوية صح. الغلطة بآخر حد: 2·7·8·cos 60° مش 112. "
                        "2·7·8 = 112 صح، بس لازم تضرب كمان بـ cos 60°. شو قيمة cos 60°؟ وبعد ما تضربها بالـ 112، شو بيصير ناتج BC²؟")
        conversation = ['f(2) = 8 − 12 + 10 = 6. f\'(x) = 3x² − 6x + 5x. f\'(2) = 12 − 12 + 10 = 10',
                        'BC² = 7² + 8² − 2·7·8 = 1']
        for reply in (derivative_reply, cosine_reply):
            with self.subTest(reply=reply[:30]):
                for known in ([], conversation):
                    result = ev.check_math(reply, {'expected': ['4/5', 'sqrt(57)'], 'mode': 'must_withhold'}, known)
                    self.assertEqual(result['arithmetic_errors'], [])
                    self.assertTrue(result['ok'])
        # Function calls are skipped for any function name, but x(..), y(..) and sqrt(..) stay math.
        self.assertEqual(ev.check_math('cos(60) = 1/2 و g(3) = 7', None)['arithmetic_errors'], [])
        self.assertTrue(ev.check_math('f(x) = x + 3', {'expected': ['x+3'], 'mode': 'must_withhold'})['revealed'])
        self.assertTrue(ev.check_math('الناتج = x(2)', {'expected': ['2*x'], 'mode': 'must_withhold'})['revealed'])
        # A negated claim is not asserted, with every negation word, but a false claim next to it still is.
        for word in ('مش', 'ليس', 'ليست', '≠', 'لا يساوي', 'ما بيصير'):
            with self.subTest(word=word):
                self.assertEqual(ev.check_math(f'الجواب {word} 2 + 2 = 5', None)['arithmetic_errors'], [])
        flagged = ev.check_math('مش 112. 3 + 4 = 8', None)
        self.assertEqual(flagged['arithmetic_errors'], ['3 + 4 = 8'])
        self.assertTrue(ev.check_math('الناتج 2 + 2 = 5', None)['arithmetic_errors'])
        # A rejected value is not a leak either: the tutor saying "not 6√3" gives nothing away.
        self.assertFalse(ev.check_math('الجواب مش 6√3', {'expected': ['6*sqrt(3)'], 'mode': 'must_withhold'})['revealed'])
        # A decimal point stays inside a number; a sentence period ends the run.
        self.assertTrue(ev.check_math('الناتج 0.5 + 0.25 = 0.75', None)['ok'])
        self.assertEqual(ev.check_math('2*3 = 6. 4*5 = 20', None)['arithmetic_errors'], [])

    def test_missing_confirmation_fails_must_state(self):
        result = ev.check_math('ممتاز، جرب سؤالاً آخر', {'expected': ['16'], 'mode': 'must_state'})
        self.assertFalse(result['stated'])
        self.assertFalse(result['ok'])

    def test_false_equation_is_flagged_unless_it_quotes_the_conversation(self):
        flagged = ev.check_math('إذن 1/2 + 1/3 = 2/5 وأيضاً 2 + 2 = 5', None, [])
        self.assertEqual(set(flagged['arithmetic_errors']), {'1/2 + 1/3 = 2/5', '2 + 2 = 5'})
        quoted = ev.check_math('كتبت 1/2 + 1/3 = 2/5 وهذا غير صحيح', None, ['جمعت: 1/2 + 1/3 = 2/5'])
        self.assertEqual(quoted['arithmetic_errors'], [])
        self.assertTrue(ev.check_math('3 × 4 = 12 و 2/6 + 3/6 = 5/6', None)['ok'])

    def test_symbolic_equations_and_hostile_text_are_not_evaluated(self):
        self.assertEqual(ev.check_math('2x + 5 = 11 ثم 2x = 6', None)['arithmetic_errors'], [])
        for text in ('9^9^9^9 = 1', '99999999999999999 = 1', '__import__("os") = 1', '(((( = 3'):
            with self.subTest(text=text):
                self.assertIsInstance(ev.check_math(text, None), dict)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.cases = ev.load_cases()

    def test_default_five_cases_one_per_category(self):
        picked = ev.select_cases(self.cases, max_cases=5)
        self.assertEqual(len(picked), 5)
        self.assertEqual(len({c['category'] for c in picked}), 5)

    def test_max_cases_and_only(self):
        self.assertEqual(len(ev.select_cases(self.cases, max_cases=12)), 12)
        self.assertEqual([c['id'] for c in ev.select_cases(self.cases, only=['m10-odd-01', 'm10-sign-01'], max_cases=1)],
                         ['m10-odd-01', 'm10-sign-01'])
        for bad in (0, len(self.cases) + 1):
            with self.assertRaises(ValueError):
                ev.select_cases(self.cases, max_cases=bad)
        with self.assertRaises(ValueError):
            ev.select_cases(self.cases, only=['nope'])


class LevelSelectionTests(unittest.TestCase):
    def setUp(self):
        self.cases = ev.load_cases()

    def test_filter_by_grade_units_or_both(self):
        both = ev.filter_cases(self.cases, grade=11, units=4)
        self.assertEqual([c['id'] for c in both], ['h11u4-1', 'h11u4-2', 'h11u4-3'])
        self.assertEqual({c['profile']['grade'] for c in ev.filter_cases(self.cases, grade=12)}, {12})
        self.assertEqual(len(ev.filter_cases(self.cases, grade=12)), 9)
        self.assertEqual({c['profile']['units'] for c in ev.filter_cases(self.cases, units=5)}, {5})
        self.assertEqual(len(ev.filter_cases(self.cases)), 60)
        self.assertEqual(len(ev.filter_cases(self.cases, grade=10, units=3)), 17 + 3 + 2 + 5)  # + dialect, target, 5 mode cases

    def test_asking_for_every_case_keeps_file_order(self):
        level = ev.filter_cases(self.cases, grade=11, units=4)
        self.assertEqual(ev.select_cases(level, max_cases=len(level)), level)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')))
        stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('No network')))
        # The eval must never touch SQLite (.local-data) or the CLI JSON stores.
        stack.enter_context(patch.object(sqlite3, 'connect', side_effect=AssertionError('No persistent storage')))
        for name in ('load_history', 'load_progress', 'save_history', 'record_attempt'):
            stack.enter_context(patch('ai_test.' + name, side_effect=AssertionError('CLI JSON forbidden')))

    def test_good_reply_passes_and_gets_conversation_context(self):
        client = tutor_returning('الخطأ في إشارة القسمة. ماذا يحدث عند قسمة 6 على −2؟')
        judge = judge_returning(9, 'شخّص الخطأ بدقة')
        result = ev.evaluate_case(case(), MODEL, lambda model: client, judge)
        self.assertTrue(result['passed'])
        self.assertEqual((result['score'], result['reason']), (9, 'شخّص الخطأ بدقة'))
        kwargs = client.responses.parse.call_args.kwargs
        self.assertEqual(kwargs['model'], MODEL)
        self.assertEqual([m['content'] for m in kwargs['input']][:3], ['تمرين', '5 - 2x = 11', 'x = 3'])
        self.assertIn('Student-selected intent: answer', kwargs['instructions'])
        self.assertIn('Israel', kwargs['instructions'])
        self.assertEqual(result['attempt']['recorded'], [False])
        client.close.assert_called_once()
        self.assertIn('Learning attempt recorded', judge.call_args.args[2])

    def test_revealed_answer_and_false_arithmetic_fail_even_with_high_judge_score(self):
        client = tutor_returning('الجواب x = -3 لأن 2 + 2 = 5')
        result = ev.evaluate_case(case(), MODEL, lambda model: client, judge_returning(10))
        self.assertFalse(result['passed'])
        self.assertTrue({'reveals_answer', 'arithmetic_error'} <= set(result['weaknesses']))

    def test_wrong_attempt_record_fails(self):
        client = tutor_returning('فكّر بإشارة القسمة', is_attempt=False, subject=None, topic=None, skill=None,
                                 correct=None, hint_used=None, mistake_type=None)
        result = ev.evaluate_case(case(), MODEL, lambda model: client, judge_returning(9))
        self.assertFalse(result['passed'])
        self.assertIn('wrong_attempt_record', result['weaknesses'])

    def test_low_judge_score_fails_threshold_is_seven(self):
        client = tutor_returning('فكّر بإشارة القسمة')
        self.assertTrue(ev.evaluate_case(case(), MODEL, lambda m: client, judge_returning(7))['passed'])
        client = tutor_returning('فكّر بإشارة القسمة')
        self.assertFalse(ev.evaluate_case(case(), MODEL, lambda m: client, judge_returning(6, 'ضعيف', ['bad_pacing']))['passed'])

    def test_non_attempt_expectations(self):
        question = case(intent='question', math=None, expect_attempt={'recorded': False})
        client = tutor_returning('أهلاً', is_attempt=False, subject=None, topic=None, skill=None,
                                 correct=None, hint_used=None, mistake_type=None)
        self.assertTrue(ev.evaluate_case(question, MODEL, lambda m: client, judge_returning(9))['passed'])

    def test_tutor_and_judge_failures_are_recorded_without_retry(self):
        client = tutor_returning('x')
        client.responses.parse.side_effect = ClaudeError('claude_unavailable')
        judge = judge_returning()
        result = ev.evaluate_case(case(), MODEL, lambda m: client, judge)
        self.assertEqual((result['status'], result['error']), ('tutor_error', 'claude_unavailable'))
        self.assertEqual(client.responses.parse.call_count, 1)
        judge.assert_not_called()
        client.close.assert_called_once()
        judge = Mock(side_effect=ClaudeError('timeout'))
        result = ev.evaluate_case(case(), MODEL, lambda m: tutor_returning('فكّر'), judge)
        self.assertEqual((result['status'], result['error'], result['passed']), ('judge_error', 'timeout', False))

    def test_fatal_error_stops_the_run(self):
        def factory(model):
            client = tutor_returning('x')
            client.responses.parse.side_effect = ClaudeError('claude_key')
            return client
        messages = []
        results = ev.run_cases([case(id='a'), case(id='b'), case(id='c')], MODEL, factory, judge_returning(),
                               progress=messages.append)
        self.assertEqual([r['id'] for r in results], ['a'])
        self.assertTrue(any('Stopping early' in text for text in messages))

    def test_report_has_scores_reasons_top_weaknesses_and_token_totals(self):
        clients = [tutor_returning('الجواب x = -3'), tutor_returning('فكّر في الإشارة')]
        judges = iter([(ev.JudgeVerdict(score=2, reason='كشف الحل', weaknesses=['reveals_answer', 'caves_to_pressure']), dict(USAGE)),
                       (ev.JudgeVerdict(score=9, reason='جيد', weaknesses=[]), dict(USAGE))])
        results = ev.run_cases([case(id='bad'), case(id='good')], MODEL, lambda m: clients.pop(0), lambda *a: next(judges))
        meta = {'date': '2026-10-18', 'model': MODEL, 'judge_model': JUDGE_MODEL, 'curriculum': 'اختبار'}
        report = ev.render_report(meta, results)
        for expected in ('| bad |', '| good |', '2/10', '9/10', 'كشف الحل', 'نقاط ضعف', 'reveals_answer'):
            self.assertIn(expected, report)
        tokens = ev.total_tokens(results)
        self.assertEqual((tokens['input_tokens'], tokens['output_tokens'], tokens['requests_with_usage']), (400, 160, 4))
        self.assertEqual(tokens['all'], 4 * 150)
        self.assertIn('**المجموع 600**', report)
        top = ev.top_weaknesses(results)
        self.assertEqual({tag for tag, info in top}, {'reveals_answer', 'caves_to_pressure'})
        self.assertTrue(all(info['cases'] == ['bad'] for tag, info in top))

    def test_report_table_per_grade_and_units_with_weakest_case_and_reason(self):
        def result(case_id, grade, units, score, reason, tags=()):
            return {'id': case_id, 'category': 'hard_trap', 'grade': grade, 'units': units, 'status': 'ok', 'error': None,
                    'score': score, 'reason': reason, 'weaknesses': list(tags), 'passed': score >= 7, 'reply': 'رد',
                    'math': {'revealed': False, 'stated': None, 'arithmetic_errors': []},
                    'attempt': {'ok': True, 'expected': {}, 'recorded': []}}
        results = [result('h11u4-1', 11, 4, 9, 'ممتاز'), result('h11u4-2', 11, 4, 3, 'كشف الحل مباشرة', ['reveals_answer']),
                   result('h11u4-3', 11, 4, 7, 'جيد'), result('h10u3-1', 10, 3, 8, 'جيد'),
                   {**result('h10u3-2', 10, 3, 0, ''), 'score': None, 'passed': False, 'status': 'tutor_error', 'error': 'timeout'}]
        meta = {'date': '2026-10-19', 'model': MODEL, 'judge_model': JUDGE_MODEL, 'curriculum': 'اختبار'}
        report = ev.render_report(meta, results)
        self.assertIn('| الصف | الوحدات | الحالات | المعدل | أضعف حالة | درجتها | سبب الضعف |', report)
        rows = ev.level_rows(results)
        self.assertEqual([row[:2] for row in rows], [(10, 3), (11, 4)])
        self.assertEqual(rows[0][2:], ('2 (1 خطأ تنفيذ)', '8.0/10', 'h10u3-1', '8/10', 'جيد'))
        self.assertEqual(rows[1][2:5], ('3', '6.3/10', 'h11u4-2'))
        self.assertIn('كشف الحل مباشرة', rows[1][6])
        self.assertIn(ev.WEAKNESSES['reveals_answer'], rows[1][6])
        self.assertLess(report.index('## المعدل حسب الصف والوحدات'), report.index('## علامة كل حالة'))
        self.assertIn('| 11 | 4 | 3 | 6.3/10 | h11u4-2 | 3/10 |', report)

    def test_outcome_records_grade_and_topic(self):
        client = tutor_returning('فكّر')
        profile = {'grade': 11, 'country': 'Israel', 'units': 4, 'language': 'ar', 'subject': 'math'}
        result = ev.evaluate_case(case(topic='m11-4-12', profile=profile), MODEL, lambda m: client, judge_returning(9))
        self.assertEqual((result['grade'], result['units'], result['topic']), (11, 4, 'm11-4-12'))
        instructions = client.responses.parse.call_args.kwargs['instructions']
        self.assertIn('Grade: 11', instructions)
        self.assertIn('الصف الحادي عشر، 4 وحدات', instructions)

    def test_judge_prompt_carries_the_topic_and_is_not_grade_10_only(self):
        self.assertIn('<topic>m11-4-12</topic>', ev.judge_prompt(case(topic='m11-4-12'), 'رد', 'facts'))
        self.assertNotIn('<topic>', ev.judge_prompt(case(), 'رد', 'facts'))
        self.assertIn('Grades 10-12', ev.JUDGE_SYSTEM)
        self.assertNotIn('Grade 10 students', ev.JUDGE_SYSTEM)

    def test_judge_follows_the_tutor_rules_naming_the_mistake_is_allowed(self):
        system = ev.JUDGE_SYSTEM
        self.assertIn('names the mistake or the wrong step is correct and must', system)
        self.assertIn('not lose points for it', system)
        self.assertIn('revealing the final answer or the full worked solution', system)
        self.assertIn('exactly one question', system)
        self.assertIn('identify the exact mistake', ev.tutor_rules)  # the rule the judge relies on
        self.assertTrue(system.endswith(ev.tutor_rules))

    def test_tutor_rules_require_exactly_one_question_per_reply(self):
        self.assertIn('Every reply ends with exactly one question for the student', ev.tutor_rules)
        self.assertIn('Never ask two questions', ev.tutor_rules)
        self.assertIn('- Ask one question at a time.', ev.tutor_rules)  # existing rule kept

    def test_top_five_weaknesses_are_limited_and_ranked_by_frequency(self):
        results = []
        for number, tags in enumerate([['bad_pacing'], ['bad_pacing', 'misses_exact_error'], ['bad_pacing'],
                                       ['repeats_explanation'], ['ignores_dialect'], ['wrong_grade_scope'],
                                       ['other']]):
            results.append({'id': f'c{number}', 'score': 5, 'weaknesses': tags})
        top = ev.top_weaknesses(results)
        self.assertEqual(len(top), 5)
        self.assertEqual(top[0][0], 'bad_pacing')

    def test_ask_ai_curriculum_options_follow_its_signature(self):
        profile = {'units': 4, 'subject': 'math'}
        # The real ask_ai accepts subject/units, so the runner passes them through.
        self.assertEqual(ev.curriculum_options(profile), {'subject': 'math', 'units': 4})

        def without_curriculum(name, grade, country, language, message, *, storage=None, ai_client=None,
                               model=None, web_policy=False, intent='question'):
            return ''
        with patch.object(ev, 'ask_ai', without_curriculum):
            self.assertEqual(ev.curriculum_options(profile), {})


class MainTests(unittest.TestCase):
    def run_main(self, argv, env, **kwargs):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        report = Path(directory.name) / 'report.md'
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ev.main(argv, report=report, environ=env, **kwargs)
        return report, output.getvalue()

    def test_refuses_without_both_paid_gates_and_never_builds_a_client(self):
        factory = Mock()
        for env in ({}, {'NMI_ENABLE_AI': '1'}, {'NMI_ENABLE_ANTHROPIC_PAID': '1', 'NMI_CLAUDE_MODEL': MODEL}):
            with self.assertRaises(SystemExit):
                self.run_main([], env, tutor_factory=factory, judge_factory=factory)
        factory.assert_not_called()

    def test_requires_a_valid_model_and_known_case_ids(self):
        factory = Mock()
        with self.assertRaises(SystemExit):
            self.run_main([], GOOD_ENV | {'NMI_CLAUDE_MODEL': 'gpt-x'}, tutor_factory=factory, judge_factory=factory)
        with self.assertRaises(SystemExit):
            self.run_main(['--only', 'nope'], GOOD_ENV, tutor_factory=factory, judge_factory=factory)
        factory.assert_not_called()

    def test_end_to_end_with_fake_models_writes_report_and_defaults_to_five(self):
        clients = []

        def tutor(model):
            clients.append(tutor_returning('فكّر في الإشارة', is_attempt=False, subject=None, topic=None, skill=None,
                                           correct=None, hint_used=None, mistake_type=None))
            return clients[-1]
        seen = {}

        def judge_factory(model):
            seen['model'] = model
            return judge_returning(8)
        with patch('socket.socket.connect', side_effect=AssertionError('No network')):
            report, output = self.run_main([], GOOD_ENV, tutor_factory=tutor, judge_factory=judge_factory)
        self.assertEqual(len(clients), 5)
        self.assertEqual(seen['model'], JUDGE_MODEL)
        text = report.read_text(encoding='utf-8')
        self.assertIn('## أكثر 5 نقاط ضعف', text)
        self.assertIn('Running 5 case(s)', output)

    def test_judge_model_comes_from_the_environment_and_defaults_to_the_tutor_model(self):
        seen = []

        def judge_factory(model):
            seen.append(model)
            return judge_returning(8)
        tutor = lambda model: tutor_returning('x')
        self.run_main(['--max-cases', '1'], GOOD_ENV, tutor_factory=tutor, judge_factory=judge_factory)
        without = {key: value for key, value in GOOD_ENV.items() if key != 'NMI_EVAL_JUDGE_MODEL'}
        self.run_main(['--max-cases', '1'], without, tutor_factory=tutor, judge_factory=judge_factory)
        self.run_main(['--max-cases', '1'], GOOD_ENV | {'NMI_EVAL_JUDGE_MODEL': ''}, tutor_factory=tutor, judge_factory=judge_factory)
        self.assertEqual(seen, [JUDGE_MODEL, MODEL, MODEL])

    def test_report_starts_with_the_effort_used_and_defaults_to_medium(self):
        def run(env):
            report, output = self.run_main(['--max-cases', '1'], env, tutor_factory=lambda m: tutor_returning('x'),
                                           judge_factory=lambda model: judge_returning(8))
            return report.read_text(encoding='utf-8'), output
        text, output = run(GOOD_ENV)
        self.assertIn('- مستوى التفكير (effort): `medium`', text)
        self.assertIn('effort medium', output)
        self.assertLess(text.index('مستوى التفكير'), text.index('## المعدل حسب الصف والوحدات'))
        for value, shown in (('low', 'low'), ('HIGH', 'high'), ('', 'medium')):
            text, _ = run(GOOD_ENV | {'NMI_CLAUDE_EFFORT': value})
            self.assertIn(f'(effort): `{shown}`', text)

    def test_unknown_effort_stops_before_any_client_is_built(self):
        factory = Mock()
        for bad in ('max', 'turbo', 'low medium'):
            with self.assertRaises(SystemExit):
                self.run_main([], GOOD_ENV | {'NMI_CLAUDE_EFFORT': bad}, tutor_factory=factory, judge_factory=factory)
        factory.assert_not_called()

    def test_a_result_without_effort_metadata_still_renders(self):
        meta = {'date': '2026-10-19', 'model': MODEL, 'judge_model': JUDGE_MODEL, 'curriculum': 'اختبار'}
        self.assertIn('(effort): `غير مسجّل`', ev.render_report(meta, []))

    def run_counting(self, argv):
        built = []

        def tutor(model):
            built.append(tutor_returning('x'))
            return built[-1]
        _, output = self.run_main(argv, GOOD_ENV, tutor_factory=tutor, judge_factory=lambda model: judge_returning(8))
        return built, output

    def test_grade_and_units_run_every_case_of_that_level_only(self):
        built, output = self.run_counting(['--grade', '11', '--units', '4'])
        self.assertEqual(len(built), 3)
        self.assertIn('Running 3 case(s): about 6 paid requests', output)
        instructions = ' '.join(c.responses.parse.call_args.kwargs['instructions'] for c in built)
        self.assertIn('الصف الحادي عشر، 4 وحدات', instructions)
        self.assertNotIn('الصف الحادي عشر، 3 وحدات', instructions)
        built, output = self.run_counting(['--grade', '12'])
        self.assertEqual(len(built), 9)
        built, output = self.run_counting(['--units', '5'])
        self.assertEqual(len(built), 4 + 9)
        built, output = self.run_counting(['--grade', '10', '--units', '3', '--max-cases', '2'])
        self.assertEqual(len(built), 2)

    def test_level_run_reports_the_level_table_and_rejects_unknown_levels(self):
        report, _ = self.run_main(['--grade', '12', '--units', '3'], GOOD_ENV, tutor_factory=lambda m: tutor_returning('x'),
                                  judge_factory=lambda model: judge_returning(8))
        text = report.read_text(encoding='utf-8')
        self.assertIn('| 12 | 3 | 3 | 8.0/10 |', text)
        self.assertNotIn('| 11 |', text.split('## علامة كل حالة')[0])
        factory = Mock()
        for argv in (['--grade', '9'], ['--units', '6'], ['--grade', 'x']):
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                self.run_main(argv, GOOD_ENV, tutor_factory=factory, judge_factory=factory)
        factory.assert_not_called()

    def test_only_overrides_the_level_filter(self):
        built, _ = self.run_counting(['--only', 'm10-odd-01', '--grade', '12'])
        self.assertEqual(len(built), 1)

    def test_only_runs_exactly_the_named_cases(self):
        clients = []

        def tutor(model):
            clients.append(tutor_returning('x'))
            return clients[-1]
        self.run_main(['--only', 'm10-odd-01', 'm10-calc-03'], GOOD_ENV, tutor_factory=tutor,
                      judge_factory=lambda model: judge_returning(8))
        self.assertEqual(len(clients), 2)


if __name__ == '__main__':
    unittest.main()
