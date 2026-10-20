"""Offline Claude integration: no credentials, student files, or remote transport."""
import asyncio
from contextlib import ExitStack, closing, redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from claude_provider import ClaudeProvider, ClaudeError, check_model, sdk_client
from learning_result import LearningResult
from ai_test import InvalidAIResponse
import ai_test
from local_web import create_app
from local_store import LocalStore
from claude_fixtures import SyntheticClaude, MODEL, learning, local_connect, TEST_ENV, SlowStream

ORIGIN = 'http://127.0.0.1:8766'
CAPABILITY = 'synthetic-local-unlock-not-a-real-secret'


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict('os.environ', TEST_ENV, clear=True))
        self.stack.enter_context(patch.object(socket.socket, 'connect', local_connect))

    def parse(self, fixture, **kwargs):
        provider = ClaudeProvider(MODEL, sdk_factory=fixture.client, **kwargs)
        result = provider.parse(model=MODEL, instructions='Synthetic tutor instructions',
            input=[{'role':'user','content':'Explain fractions'}], text_format=LearningResult)
        return result, provider

    def test_cache_prefix_becomes_a_cached_block_and_falls_back_to_a_string(self):
        fixture = SyntheticClaude()
        provider = ClaudeProvider(MODEL, sdk_factory=fixture.client)
        messages = [{'role': 'user', 'content': 'Explain fractions'}]
        joined = 'STABLE' + chr(10) * 2 + 'VARIABLE'
        provider.parse(model=MODEL, instructions=joined, cache_prefix='STABLE', input=messages, text_format=LearningResult)
        self.assertEqual(fixture.posts[-1]['system'], [
            {'type': 'text', 'text': 'STABLE', 'cache_control': {'type': 'ephemeral'}},
            {'type': 'text', 'text': 'VARIABLE'}])
        for prefix in (None, '', 'OTHER', joined, 7):
            with self.subTest(prefix=prefix):
                provider.parse(model=MODEL, instructions=joined, cache_prefix=prefix, input=messages, text_format=LearningResult)
                self.assertEqual(fixture.posts[-1]['system'], joined)

    def test_effort_comes_from_the_environment_and_defaults_to_medium(self):
        for env, kwargs, expected in ((None, {}, 'medium'), ('', {}, 'medium'), ('low', {}, 'low'), (' High ', {}, 'high'),
                                      ('medium', {'effort': 'low'}, 'low'), (None, {'effort': 'high'}, 'high')):
            with self.subTest(env=env, kwargs=kwargs), patch.dict('os.environ', {} if env is None else {'NMI_CLAUDE_EFFORT': env}):
                fixture = SyntheticClaude()
                self.parse(fixture, **kwargs)
                self.assertEqual(fixture.posts[0]['output_config']['effort'], expected)
                self.assertEqual(fixture.posts[0]['thinking'], {'type': 'between_tools'})

    def test_an_unknown_effort_stops_before_any_request(self):
        for bad in ('max', 'turbo', '1', 'low medium'):
            with self.subTest(effort=bad), patch.dict('os.environ', {'NMI_CLAUDE_EFFORT': bad}):
                fixture = SyntheticClaude()
                with self.assertRaises(ClaudeError) as caught:
                    self.parse(fixture)
                self.assertEqual(caught.exception.code, 'claude_request')
                self.assertEqual((fixture.calls, fixture.posts), ([], []))

    def test_explanation_and_question_go_through_the_real_sdk_and_are_normalised(self):
        value = dict(explanation='الخطأ بالمشتقة؟ شوف.', question='شو مشتقة 5x؟ وشو f\'(2)؟', is_attempt=False, subject=None,
                     topic=None, skill=None, correct=None, hint_used=None, mistake_type=None)
        fixture = SyntheticClaude(value)
        result, _ = self.parse(fixture)
        self.assertEqual(result.output_parsed.reply, 'الخطأ بالمشتقة. شوف.\n\nوشو f\'(2)؟')
        schema = fixture.posts[0]['output_config']['format']['schema']
        self.assertTrue({'explanation', 'question'} <= set(schema['properties']))
        self.assertNotIn('reply', schema['properties'])
        self.assertIn('NO question marks', schema['properties']['explanation']['description'])
        self.assertIn('ONE small next step', schema['properties']['question']['description'])

    def test_old_single_reply_answers_and_incomplete_answers(self):
        result, _ = self.parse(SyntheticClaude(learning(reply='تمام. شو الخطوة؟')))
        self.assertEqual(result.output_parsed.reply, 'تمام.\n\nشو الخطوة؟')
        for broken in (dict(learning(), reply=None), {'is_attempt': False}, {'is_attempt': False, 'explanation': 'x'}):
            with self.subTest(broken=broken), self.assertRaises(InvalidAIResponse):
                self.parse(SyntheticClaude(broken))

    def test_official_sdk_structured_stream_and_usage(self):
        fixture = SyntheticClaude()
        result, provider = self.parse(fixture)
        self.assertIsInstance(result.output_parsed, LearningResult)
        self.assertEqual(result.output_parsed.reply, learning()['reply'])
        body = fixture.posts[0]
        self.assertEqual(len(fixture.posts), 1)
        self.assertEqual(body['model'], MODEL); self.assertTrue(body['stream'])
        self.assertEqual(body['system'], 'Synthetic tutor instructions')
        self.assertEqual(body['max_tokens'], 1800)
        self.assertEqual(body['output_config']['format']['type'], 'json_schema')
        self.assertEqual(body['thinking'], {'type':'between_tools'})
        self.assertEqual(body['output_config']['effort'], 'medium')
        self.assertNotIn('store', body)
        self.assertEqual(provider.usage['input_tokens'], 120)
        self.assertEqual(provider.usage['output_tokens'], 80)
        self.assertTrue(provider.usage['complete'])

    def test_invalid_and_interrupted_responses(self):
        cases = [(learning(is_attempt=True), 'end_turn'), ('{invalid', 'end_turn'),
                 (learning(is_attempt='true'), 'end_turn'),
                 (learning(), 'disconnected'), (learning(), 'max_tokens'), (learning(), 'refusal'),
                 (learning(is_attempt=True, subject='physics', topic='x', skill='x', correct='yes', hint_used=False), 'end_turn')]
        for value, terminal in cases:
            with self.subTest(terminal=terminal, value_type=type(value).__name__):
                with self.assertRaises(InvalidAIResponse):
                    self.parse(SyntheticClaude(value, terminal=terminal))

    def test_errors_sanitized_and_never_retried(self):
        for status, code in [(400,'claude_request'),(401,'claude_key'),(402,'claude_credit'),
                             (403,'claude_access'),(404,'claude_model'),(429,'claude_limit'),(500,'claude_unavailable'),(529,'claude_unavailable')]:
            fixture = SyntheticClaude(status=status)
            with self.subTest(status=status), self.assertRaises(ClaudeError) as error:
                self.parse(fixture)
            self.assertEqual(str(error.exception), code)
            self.assertEqual(len(fixture.posts), 1)

    def test_total_deadline_cancels_request(self):
        fixture = SyntheticClaude(delay=1)
        with self.assertRaises(ClaudeError) as error:
            self.parse(fixture, deadline=.05)
        self.assertEqual(error.exception.code, 'timeout')
        self.assertEqual(len(fixture.posts), 1)

    def test_total_deadline_also_cancels_stalled_stream(self):
        import httpx2 as httpx
        fixture=SyntheticClaude(); original=fixture.handle; stream=SlowStream()
        async def handle(request):
            if request.method=='GET': return await original(request)
            return httpx.Response(200,headers={'content-type':'text/event-stream'},stream=stream)
        fixture.handle=handle
        provider=ClaudeProvider(MODEL,sdk_factory=fixture.client,deadline=.1)
        with self.assertRaises(ClaudeError) as error:
            provider.parse(model=MODEL,instructions='Synthetic',input=[{'role':'user','content':'Test'}],text_format=LearningResult)
        self.assertEqual(error.exception.code,'timeout');self.assertTrue(stream.closed)
        self.assertEqual(provider.usage['input_tokens'],120);self.assertFalse(provider.usage['complete'])

    def test_model_check_is_metadata_only_and_incompatible_fails_before_post(self):
        fixture = SyntheticClaude()
        self.assertEqual(check_model(MODEL, sdk_factory=fixture.client)['model'], MODEL)
        self.assertEqual(fixture.posts, [])
        fixture.supported = False
        with self.assertRaises(ClaudeError) as error: self.parse(fixture)
        self.assertEqual(error.exception.code, 'claude_model'); self.assertEqual(fixture.posts, [])

    def test_client_configuration_and_missing_key(self):
        with self.assertRaises(ClaudeError) as error: sdk_client()
        self.assertEqual(error.exception.code, 'claude_key')
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY':'synthetic-not-real',
                                     'ANTHROPIC_BASE_URL':'https://untrusted.invalid'} | TEST_ENV, clear=True):
            client = sdk_client()
            self.assertEqual(str(client.base_url), 'https://api.anthropic.com')
            self.assertEqual(client.max_retries, 0)
            self.assertEqual(client.timeout.connect, 5)
            self.assertEqual(client.timeout.read, 30)
            asyncio.run(client.close())
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY':'synthetic-not-real', 'ANTHROPIC_CUSTOM_HEADERS':'ignored'}, clear=True):
            with self.assertRaises(ClaudeError): sdk_client()


class ClaudeWebTests(unittest.TestCase):
    def setUp(self):
        base = ROOT/'.cache/claude-tests'; base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base); self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name)/'synthetic.sqlite3'
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict('os.environ', TEST_ENV, clear=True))
        self.stack.enter_context(patch.object(socket.socket, 'connect', local_connect))
        for name in ('load_history','load_progress','save_history','record_attempt'):
            self.stack.enter_context(patch.object(ai_test, name, side_effect=AssertionError('CLI student JSON forbidden')))
        self.fixture = SyntheticClaude()
        self.factory = Mock(side_effect=lambda model:ClaudeProvider(model, sdk_factory=self.fixture.client))
        self.setup_app()
        self.assertEqual(self.post('/api/profile', {'country':'IL','grade':10,'subject':'math','units':4}).status_code, 200)

    def setup_app(self, **options):
        args = dict(data_path=self.db, access_token=CAPABILITY, enabled=True,
            allow_claude=True, claude_model=MODEL, claude_factory=self.factory, max_calls=20)
        self.app = create_app(**(args | options)); self.client = self.app.test_client()
        self.client.get('/api/session/preflight', base_url=ORIGIN)
        self.csrf = self.post('/api/session', {'token':CAPABILITY}).json['csrf']

    def post(self, route, body, **headers):
        return self.client.post(route, json=body, base_url=ORIGIN,
            headers={'Origin':ORIGIN,'X-NMI-CSRF':getattr(self,'csrf',''),'X-NMI-Language':'en'} | headers)

    def state(self): return self.client.get('/api/state', base_url=ORIGIN).json
    def body(self, **values):
        return dict(request_id=str(uuid4()), language='en', intent='question', message='Why is the sky blue?') | values
    def chat(self, **values): return self.post('/api/chat', self.body(**values))

    def test_multiturn_context_usage_persistence_and_no_fallback(self):
        self.assertEqual(self.chat().status_code, 200)
        self.assertEqual(self.chat(language='ar', intent='confusion', message='مش فاهم، اشرح بمثال أبسط').status_code, 200)
        body = self.fixture.posts[-1]
        self.assertEqual(len(body['messages']), 3)
        self.assertIn('مش فاهم', body['messages'][-1]['content'])
        # The real SDK request: a cached stable block (rules, then curriculum), then an uncached variable block.
        stable, variable = body['system']
        self.assertEqual(stable['cache_control'], {'type': 'ephemeral'})
        self.assertNotIn('cache_control', variable)
        self.assertTrue(stable['text'].startswith(ai_test.rules_for_subject('math')))
        self.assertIn('# STUDENT CURRICULUM', stable['text'])
        self.assertNotIn('# STUDENT INFORMATION', stable['text'])
        self.assertIn('# STUDENT INFORMATION', variable['text'])
        self.assertTrue(variable['text'].endswith(ai_test.FINAL_CHECK))
        first = self.fixture.posts[-2]['system']
        self.assertEqual(first[0], stable)  # the cached block is identical across requests
        before = self.state(); self.assertEqual(len(before['history']),4); self.assertEqual(before['attempts'],[])
        self.setup_app(); after = self.state()
        for name in ('history','attempts','profile','last_usage'): self.assertEqual(after[name],before[name])

    def test_valid_correct_and_incorrect_attempts(self):
        self.chat()
        for correct in (True,False):
            self.fixture.value = learning(is_attempt=True,subject='physics',topic='motion',skill='velocity',
                correct=correct,hint_used=False,mistake_type=None if correct else 'direction')
            self.assertEqual(self.chat(intent='answer').status_code,200)
        self.assertEqual([a['correct'] for a in self.state()['attempts']],[True,False])

    def test_question_hint_confusion_never_score(self):
        self.chat()
        self.fixture.value = learning(is_attempt=True,subject='physics',topic='motion',skill='velocity',correct=False,hint_used=False)
        for intent in ('question','hint','confusion'):
            self.assertEqual(self.chat(intent=intent).status_code,200)
        self.assertEqual(self.state()['attempts'],[])

    def test_invalid_stream_preserves_progress_history_and_partial_usage(self):
        self.chat(); before=self.state()
        self.fixture.terminal='disconnected'
        body=self.body(); response=self.post('/api/chat',body)
        self.assertEqual(response.json['error'],'response')
        after=self.state()
        for name in ('profile','history','attempts'): self.assertEqual(after[name],before[name])
        self.assertFalse(after['last_usage']['complete'])
        self.assertEqual(self.post('/api/chat',body).json['error'],'response')
        self.assertEqual(len(self.fixture.posts),2)

    def test_duplicate_receipt_does_not_charge_twice(self):
        body=self.body(); first=self.post('/api/chat',body)
        second=self.post('/api/chat',body)
        self.assertTrue(second.json['replayed']); self.assertEqual(first.json['usage'],second.json['usage'])
        receipt=self.client.get('/api/requests/'+body['request_id'],base_url=ORIGIN).json
        self.assertEqual(receipt['usage'],first.json['usage'])
        self.assertEqual(len(self.fixture.posts),1)

    def test_both_gates_model_and_budget(self):
        for options, code in [({'enabled':False},'locked'),({'allow_claude':False},'claude_locked'),({'claude_model':''},'claude_model')]:
            self.setup_app(**options)
            self.assertEqual(self.chat().json['error'],code)
        self.factory.assert_not_called()
        self.setup_app(max_calls=1)
        self.assertEqual(self.chat().status_code,200);self.assertEqual(self.chat().json['error'],'limit')
        self.assertEqual(len(self.fixture.posts),1)

    def test_security_student_cannot_change_provider_model_or_use_other_session(self):
        self.assertEqual(self.post('/api/chat',self.body(model=MODEL)).status_code,400)
        self.assertEqual(self.post('/api/chat',self.body(),**{'Origin':'https://evil.invalid'}).status_code,403)
        self.assertEqual(self.post('/api/chat',self.body(),**{'X-NMI-CSRF':'wrong'}).status_code,403)
        self.assertEqual(self.app.test_client().get('/api/state',base_url=ORIGIN).status_code,401)
        self.factory.assert_not_called()

    def test_error_is_localized_and_private_detail_not_returned_or_logged(self):
        self.fixture.status=401; output=io.StringIO()
        with redirect_stderr(output), redirect_stdout(output):
            response=self.post('/api/chat',self.body(language='ar'),**{'X-NMI-Language':'ar'})
        self.assertEqual(response.json['error'],'claude_key')
        self.assertRegex(response.json['message'],r'[\u0600-\u06ff]')
        self.assertNotIn('SYNTHETIC_PRIVATE_ERROR',response.get_data(as_text=True)+output.getvalue())
        self.assertEqual(self.state()['history'],[])

    def test_storage_failure_rolls_back_reply_progress_and_success_usage(self):
        self.chat(); before=self.state()
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("CREATE TRIGGER fail_commit BEFORE UPDATE OF status ON requests WHEN NEW.status='done' BEGIN SELECT RAISE(ABORT,'synthetic disk failure'); END")
        self.assertEqual(self.chat().json['error'],'storage')
        for name in ('history','attempts','profile'): self.assertEqual(self.state()[name],before[name])

    def test_additive_usage_migration_preserves_existing_records(self):
        self.chat(); before=self.state()
        with closing(sqlite3.connect(self.db)) as db, db: db.execute('DROP TABLE request_usage')
        migrated=LocalStore(self.db)
        for name in ('history','attempts','profile'):self.assertEqual(migrated.load()[name],before[name])
        self.assertIsNone(migrated.usage())

    def test_corrupt_store_is_preserved_and_no_request_is_sent(self):
        with closing(sqlite3.connect(self.db)) as db, db: db.execute("UPDATE state SET payload='{broken'")
        self.assertEqual(self.chat().json['error'],'storage'); self.factory.assert_not_called()
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT payload FROM state').fetchone()[0],'{broken')

    def test_missing_key_returns_clear_error_without_inference(self):
        self.factory.side_effect=lambda model:ClaudeProvider(model)
        self.assertEqual(self.chat().json['error'],'claude_key')
        self.assertEqual(self.state()['history'],[]);self.assertEqual(self.fixture.posts,[])

    def test_launcher_defaults_and_isolated_acceptance(self):
        from tools.run_claude import build_app
        directory=Path(self.temp.name)/'launcher'
        app=build_app(directory,CAPABILITY,acceptance=True,environ={})
        store=app.extensions['nmi_store']
        self.assertEqual(store.load()['profile'],{'country':'IL','grade':10,'subject':'math','units':4})
        self.assertEqual(store.load()['history'],[])
        client=app.test_client();client.get('/api/session/preflight',base_url=ORIGIN)
        response=client.post('/api/session',json={'token':CAPABILITY},base_url=ORIGIN,headers={'Origin':ORIGIN})
        self.assertEqual(response.status_code,200)
        value=client.get('/api/state',base_url=ORIGIN).json
        self.assertFalse(value['enabled']);self.assertFalse(value['claude_enabled'])
        self.assertEqual(value['remaining'],1)
        with self.assertRaises(ValueError):build_app(directory,CAPABILITY,acceptance=True,environ={})
        self.assertEqual(store.load()['profile'],{'country':'IL','grade':10,'subject':'math','units':4})


if __name__ == '__main__': unittest.main()
