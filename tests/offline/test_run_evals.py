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
from claude_provider import ClaudeError
from learning_result import LearningResult
from tools import run_evals as ev

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
        self.assertEqual(len(self.cases), 25)
        self.assertEqual(len({c['id'] for c in self.cases}), 25)
        units = [c['profile']['units'] for c in self.cases]
        self.assertGreater(units.count(3), len(units) / 2)
        self.assertTrue(set(units) <= {3, 4, 5} and 5 in units)
        for c in self.cases:
            self.assertEqual(c['profile']['grade'], 10)
            self.assertEqual(c['profile']['language'], 'ar')
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
        for bad in (0, 26):
            with self.assertRaises(ValueError):
                ev.select_cases(self.cases, max_cases=bad)
        with self.assertRaises(ValueError):
            ev.select_cases(self.cases, only=['nope'])


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
        self.assertEqual(ev.curriculum_options(profile), {})

        def future(name, grade, country, language, message, *, storage=None, ai_client=None, model=None,
                   web_policy=False, intent='question', subject=None, units=None):
            return ''
        with patch.object(ev, 'ask_ai', future):
            self.assertEqual(ev.curriculum_options(profile), {'subject': 'math', 'units': 4})


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
