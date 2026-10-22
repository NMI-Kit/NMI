"""Offline Flask -> ask_ai -> SQLite integration. Never reads credentials or CLI data."""
import contextlib
import copy
import io
import json
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import ai_test
from claude_provider import ClaudeError
from local_web import create_app

ORIGIN = 'http://127.0.0.1:8766'
TOKEN = 'synthetic-local-unlock-not-a-real-secret'
MODEL = 'claude-synthetic-model'


def parsed(**values):
    return dict(reply='Synthetic tutor response', is_attempt=False, subject=None,
                topic=None, skill=None, correct=None, hint_used=None, mistake_type=None) | values


class LocalWebTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.cache/local-tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.cache/local-tests')
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'test.sqlite3'
        self.ai = SimpleNamespace(responses=SimpleNamespace(parse=Mock(return_value=SimpleNamespace(output_parsed=parsed(), status='completed'))), close=Mock())
        self.factory = Mock(return_value=self.ai)
        self.stack = contextlib.ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')))
        self.stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('No network')))
        # Explicitly ensure no fallback into any shared JSON persistence function.
        for name in ('load_history','load_progress','save_history','record_attempt'):
            self.stack.enter_context(patch.object(ai_test, name, side_effect=AssertionError('Shared JSON forbidden')))
        self.app = self.make_app(); self.client = self.app.test_client()
        self.csrf = self.post('/api/session', {'token':TOKEN}).json['csrf']
        self.assertEqual(self.post('/api/profile', {'country':'IL','grade':10,'subject':'math','units':4}).status_code, 200)

    def make_app(self, **kwargs):
        return create_app(data_path=self.db, access_token=TOKEN, enabled=True, claude_model=MODEL,
                          allow_claude=True, max_calls=20, claude_factory=self.factory, **kwargs)

    def post(self, route, body, **options):
        if route == '/api/session':
            self.client.get('/api/session/preflight', base_url=ORIGIN)
        headers={'Origin':ORIGIN, 'X-NMI-CSRF':getattr(self,'csrf',''), 'X-NMI-Language':'en'} | options.pop('headers',{})
        return self.client.post(route, json=body, base_url=ORIGIN, headers=headers, **options)

    def state(self):
        return self.client.get('/api/state', base_url=ORIGIN).json

    def body(self, **extra):
        return dict(request_id=str(uuid4()), message='Synthetic question', language='en', intent='question') | extra

    def chat(self, result=None, **extra):
        self.ai.responses.parse.return_value=SimpleNamespace(output_parsed=result if result is not None else parsed(), status='completed')
        return self.post('/api/chat', self.body(**extra))

    def test_question_history_and_context_no_attempt(self):
        response=self.chat()
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(self.state()['history']),2); self.assertEqual(self.state()['attempts'],[])
        args=self.ai.responses.parse.call_args.kwargs
        self.assertIs(args['text_format'], ai_test.LearningResult)
        self.assertFalse(args['store']); self.assertEqual(args['max_output_tokens'],3200)
        self.assertIn(ai_test.rules_for_subject('math'),args['instructions'])
        self.assertTrue(args['instructions'].startswith(args['cache_prefix']))
        self.assertTrue(args['instructions'].endswith(ai_test.FINAL_CHECK))
        self.assertIn('رياضيات، الصف العاشر، 4 وحدات',args['cache_prefix'])

    def test_correct_incorrect_and_persistence_restart(self):
        self.chat()
        for correct in (True,False):
            self.assertEqual(self.chat(parsed(is_attempt=True,subject='physics',topic='motion',skill='velocity',correct=correct,hint_used=False,mistake_type=None if correct else 'direction'),intent='answer').status_code,200)
        old=self.state(); self.assertEqual(len(old['attempts']),2)
        self.app=self.make_app(); self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.assertEqual(self.state()['history'],old['history']); self.assertEqual(self.state()['attempts'],old['attempts'])

    def test_question_hint_confusion_and_unsupported_cannot_record(self):
        self.chat()
        for intent in ('question','hint','confusion'):
            self.chat(parsed(is_attempt=True,subject='physics',topic='motion',skill='velocity',correct=False,hint_used=False),intent=intent)
        for subject in ('history','english'):
            self.chat(parsed(is_attempt=True,subject=subject,topic='sample',skill='sample',correct=False,hint_used=False),intent='answer')
        self.assertEqual(self.state()['attempts'],[]); self.assertEqual(len(self.state()['history']),12)

    def test_first_answer_without_exercise_cannot_record(self):
        self.chat(parsed(is_attempt=True,subject='mathematics',topic='fractions',skill='sum',correct=True,hint_used=False),intent='answer')
        self.assertEqual(self.state()['attempts'],[])

    def test_invalid_parsed_and_incomplete_preserve_data(self):
        self.chat(); before=self.state()
        cases=[None, parsed(reply=' '), parsed(is_attempt='true'), parsed(is_attempt=True),parsed(is_attempt=True,subject='physics',topic='x',skill='x',correct='yes',hint_used=False)]
        for value in cases:
            self.ai.responses.parse.return_value=SimpleNamespace(output_parsed=value,status='completed')
            r=self.post('/api/chat',self.body())
            self.assertEqual(r.json['error'],'response')
            self.assertEqual(self.state()['history'],before['history']);self.assertEqual(self.state()['attempts'],before['attempts'])
        # New app resets only the call-rate counter, not previous conversation.
        self.app=self.make_app();self.client=self.app.test_client();self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.ai.responses.parse.return_value=SimpleNamespace(output_parsed=parsed(),status='incomplete')
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'response')

    def test_failures_localized_sanitized_and_no_persistence(self):
        cases=[(TimeoutError('PRIVATE_SENTINEL'),'timeout'),
               (ClaudeError('claude_key'),'claude_key'),
               (ClaudeError('claude_model'),'claude_model'),
               (RuntimeError('PRIVATE_SENTINEL'),'unavailable')]
        for error,code in cases:
            self.ai.responses.parse.side_effect=error
            output=io.StringIO()
            with contextlib.redirect_stderr(output),contextlib.redirect_stdout(output):
                response=self.post('/api/chat',self.body(language='ar'),headers={'X-NMI-Language':'ar'})
            self.assertEqual(response.json['error'],code)
            self.assertRegex(response.json['message'],r'[؀-ۿ]')
            self.assertNotIn('PRIVATE_SENTINEL',response.get_data(as_text=True)+output.getvalue())
            self.assertEqual(self.state()['history'],[])

    def test_duplicate_id_and_changed_payload(self):
        body=self.body()
        self.assertEqual(self.post('/api/chat',body).status_code,200)
        self.assertTrue(self.post('/api/chat',body).json['replayed'])
        self.assertEqual(self.ai.responses.parse.call_count,1)
        self.assertEqual(self.post('/api/chat',body|{'message':'changed'}).status_code,409)
        self.assertEqual(len(self.state()['history']),2)

    def test_failed_id_never_retries_paid_request(self):
        body=self.body();self.ai.responses.parse.side_effect=TimeoutError()
        self.assertEqual(self.post('/api/chat',body).json['error'],'timeout')
        self.assertEqual(self.post('/api/chat',body).json['error'],'timeout')
        self.assertEqual(self.ai.responses.parse.call_count,1)

    def test_transaction_rollback_between_history_and_receipt(self):
        self.chat(); before=self.state()
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:
            db.execute("CREATE TRIGGER fail_commit BEFORE UPDATE OF status ON requests WHEN NEW.status='done' BEGIN SELECT RAISE(ABORT,'synthetic disk failure'); END")
        response=self.chat(parsed(is_attempt=True,subject='physics',topic='motion',skill='velocity',correct=True,hint_used=False),intent='answer')
        self.assertEqual(response.json['error'],'storage')
        self.assertEqual(self.state()['history'],before['history']);self.assertEqual(self.state()['attempts'],before['attempts'])

    def test_corrupt_payload_not_overwritten(self):
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:db.execute("UPDATE state SET payload='{truncated'")
        self.assertEqual(self.client.get('/api/state',base_url=ORIGIN).json['error'],'storage')
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'storage')
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:self.assertEqual(db.execute('SELECT payload FROM state').fetchone()[0],'{truncated')
        self.factory.assert_not_called()

    def test_origin_csrf_session_host_and_file_protection(self):
        self.assertEqual(self.post('/api/chat',self.body(),headers={'Origin':'https://evil.invalid'}).status_code,403)
        self.assertEqual(self.post('/api/chat',self.body(),headers={'X-NMI-CSRF':'wrong'}).status_code,403)
        stranger=self.app.test_client()
        self.assertEqual(stranger.get('/api/state',base_url=ORIGIN).status_code,401)
        self.assertEqual(stranger.post('/api/session',json={'token':TOKEN},base_url=ORIGIN,headers={'Origin':ORIGIN}).status_code,403)
        self.assertEqual(self.client.get('/api/state',base_url='http://evil.invalid').status_code,400)
        for path in ('/student.json','/.env','/.local-data/tutor.sqlite3','/../ai_test.py'):
            self.assertEqual(self.client.get(path,base_url=ORIGIN).status_code,404)
        self.assertEqual(self.client.get('/api/state',base_url=ORIGIN,headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
        self.factory.assert_not_called()

    def test_input_bounds_and_immutable_profile(self):
        for body in ([],{},self.body(message=' '),self.body(message='x'*4001),self.body(language='fr'),self.body(intent='grade'),self.body(student_id='other'),self.body(request_id='../a')):
            self.assertEqual(self.post('/api/chat',body).status_code,400)
        for value in ({'country':'US','grade':8},{'country':'XX','grade':10},{'country':[],'grade':10},{'country':'US','grade':True}):
            self.assertEqual(self.post('/api/profile',value).status_code,400)
        # A profile can be edited at any time; it is not immutable any more (see test_profile_edit_keeps_the_conversation).
        self.assertEqual(self.post('/api/profile',{'country':'US','grade':11}).status_code,200)
        self.assertEqual(self.state()['profile'],{'country':'US','grade':11})
        self.assertFalse(self.state()['profile_ready'])
        self.assertEqual(self.client.post('/api/chat',data='x'*21000,base_url=ORIGIN,headers={'Origin':ORIGIN,'Content-Type':'application/json','X-NMI-CSRF':self.csrf}).status_code,413)
        self.factory.assert_not_called()

    def test_headers_and_cookie(self):
        response=self.client.get('/',base_url=ORIGIN)
        self.assertIn("connect-src 'self'",response.headers['Content-Security-Policy'])
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertNotIn('Access-Control-Allow-Origin',response.headers)
        cookie=self.client.get_cookie(self.app.config['SESSION_COOKIE_NAME'],domain='127.0.0.1')
        self.assertTrue(cookie.http_only);self.assertEqual(cookie.same_site,'Strict')

    def test_disabled_and_call_budget(self):
        other=Path(self.temp.name)/'locked.sqlite3'
        app=create_app(data_path=other,access_token=TOKEN,claude_factory=self.factory)
        self.client=app.test_client();self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'locked');self.factory.assert_not_called()
        app=create_app(data_path=other,access_token=TOKEN,enabled=True,claude_model=MODEL,allow_claude=True,claude_factory=self.factory)
        self.client=app.test_client();self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf'];self.post('/api/profile',{'country':'IL','grade':10,'units':3})
        self.assertEqual(self.chat().status_code,200)
        self.assertEqual(self.chat().json['error'],'limit');self.assertEqual(self.ai.responses.parse.call_count,1)

    def test_interrupted_request_marked_uncertain_on_restart(self):
        body=self.body()
        import hashlib
        self.app.extensions['nmi_store'].begin(body['request_id'],hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest())
        self.app=self.make_app();self.client=self.app.test_client();self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.assertEqual(self.post('/api/chat',body).json['error'],'uncertain');self.factory.assert_not_called()

    def test_concurrent_send_rejected_without_second_call(self):
        started=threading.Event();release=threading.Event()
        def slow(**kwargs):
            started.set();release.wait(3)
            return SimpleNamespace(output_parsed=parsed(),status='completed')
        self.ai.responses.parse.side_effect=slow
        first=self.app.test_client()
        cookie=self.client.get_cookie(self.app.config['SESSION_COOKIE_NAME'],domain='127.0.0.1')
        first.set_cookie(self.app.config['SESSION_COOKIE_NAME'],cookie.value,domain='127.0.0.1')
        responses=[]
        worker=threading.Thread(target=lambda:responses.append(first.post('/api/chat',json=self.body(),base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':self.csrf})))
        worker.start();self.assertTrue(started.wait(2))
        try:self.assertEqual(self.post('/api/chat',self.body()).json['error'],'busy')
        finally:release.set();worker.join(4)
        self.assertEqual(responses[0].status_code,200);self.assertEqual(self.ai.responses.parse.call_count,1)

    def test_session_expiry_and_wrong_shaped_store(self):
        self.app.config['PERMANENT_SESSION_LIFETIME']=-1
        self.assertEqual(self.client.get('/api/state',base_url=ORIGIN).status_code,401)
        self.app.config['PERMANENT_SESSION_LIFETIME']=28800
        for value in ('[]','{"profile":{},"history":"wrong","attempts":[]}'):
            with contextlib.closing(sqlite3.connect(self.db)) as db, db:db.execute('UPDATE state SET payload=?',(value,))
            self.assertEqual(self.client.get('/api/state',base_url=ORIGIN).json['error'],'storage')
        self.factory.assert_not_called()

    def test_all_country_grade_pairs_and_tampered_session(self):
        from local_web import COUNTRIES,valid_profile
        self.assertEqual(len(COUNTRIES),11);self.assertEqual(COUNTRIES['IL'],'Israel')
        for country in COUNTRIES:
            for grade in (9,10,11,12):
                # Israel has curriculum files only for grades 10-12; every other country is unchanged.
                self.assertEqual(valid_profile(dict(country=country,grade=grade)),not(country=='IL' and grade==9))
        self.client.set_cookie(self.app.config['SESSION_COOKIE_NAME'],'tampered',domain='127.0.0.1')
        self.assertEqual(self.client.get('/api/state',base_url=ORIGIN).status_code,401)

    def test_profile_units_validation_and_old_profiles(self):
        from local_web import valid_profile
        self.assertTrue(valid_profile(dict(country='US',grade=10)))
        for units in (3,4,5):self.assertTrue(valid_profile(dict(country='IL',grade=10,units=units)))
        for units in (2,6,'4',True,None,4.0):self.assertFalse(valid_profile(dict(country='IL',grade=10,units=units)))
        self.assertFalse(valid_profile(dict(country='US',grade=10,units=4)))
        self.assertFalse(valid_profile(dict(country='IL',grade=10,units=4,extra=1)))

    def test_options_are_built_from_curriculum_folders(self):
        import curriculum
        from local_web import curriculum_options,valid_profile
        self.assertEqual(curriculum_options(),{'math':{'10':[3,4,5],'11':[3,4,5],'12':[3,4,5]}})
        self.assertEqual(self.state()['curriculum'],{'country':'IL','options':curriculum_options()})
        root=Path(self.temp.name)/'tree'
        (root/'math/grade10').mkdir(parents=True);(root/'math/grade10/4units.md').write_text('x',encoding='utf-8')
        (root/'math/grade11').mkdir();(root/'math/grade11/3units.md').write_text('x',encoding='utf-8')
        (root/'math/grade11/notes.md').write_text('x',encoding='utf-8');(root/'SOURCES.md').write_text('x',encoding='utf-8')
        (root/'physics/grade10').mkdir(parents=True);(root/'physics/grade10/5units.md').write_text('x',encoding='utf-8')
        (root/'math/grade12').mkdir()  # no unit files, so it is not an option
        with patch.object(curriculum,'CURRICULUM_DIR',root):
            self.assertEqual(curriculum_options(),{'math':{'10':[4],'11':[3]},'physics':{'10':[5]}})
            self.assertTrue(valid_profile(dict(country='IL',grade=10,units=4)))
            self.assertTrue(valid_profile(dict(country='IL',grade=10,subject='physics',units=5)))
            for bad in (dict(grade=10,units=3),dict(grade=12),dict(grade=11,units=4),dict(grade=10,subject='physics',units=4),dict(grade=10,subject='chemistry'),dict(grade=10,subject=3)):
                self.assertFalse(valid_profile(dict(country='IL')|bad),bad)
            self.assertEqual(self.post('/api/profile',{'country':'IL','grade':12}).status_code,400)

    def test_server_rejects_choices_without_a_file(self):
        self.db=Path(self.temp.name)/'reject.sqlite3'
        self.app=self.make_app();self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        for bad in ({'grade':9},{'grade':10,'units':6},{'grade':10,'subject':'physics'},{'grade':10,'subject':'math','units':'3'},{'grade':13}):
            self.assertEqual(self.post('/api/profile',{'country':'IL'}|bad).status_code,400,bad)
        self.assertEqual(self.post('/api/profile',{'country':'US','grade':10,'subject':'math'}).status_code,400)
        self.assertIsNone(self.state()['profile'])
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':11,'subject':'math','units':5}).status_code,200)
        self.assertEqual(self.chat().status_code,200)
        self.assertIn('رياضيات، الصف الحادي عشر، 5 وحدات',self.ai.responses.parse.call_args.kwargs['instructions'])

    def test_israel_units_profile_loads_curriculum_file(self):
        self.db=Path(self.temp.name)/'israel.sqlite3'
        self.app=self.make_app();self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':4}).status_code,200)
        self.assertEqual(self.state()['profile'],{'country':'IL','grade':10,'units':4})
        self.assertEqual(self.chat().status_code,200)
        instructions=self.ai.responses.parse.call_args.kwargs['instructions']
        self.assertIn('4 وحدات',instructions);self.assertNotIn('Do not invent curriculum requirements',instructions)
        self.assertIn('Country: Israel',instructions)

    def test_israel_profile_without_units_still_works(self):
        self.db=Path(self.temp.name)/'israel-old.sqlite3'
        self.app=self.make_app();self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        # An older Israel profile without units is still valid and readable, but it cannot chat until it is completed.
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10}).status_code,200)
        state=self.state();self.assertEqual(state['profile'],{'country':'IL','grade':10});self.assertFalse(state['profile_ready'])
        refused=self.chat();self.assertEqual((refused.status_code,refused.json['error']),(409,'profile_incomplete'))
        self.ai.responses.parse.assert_not_called();self.factory.assert_not_called()
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':3}).status_code,200)
        self.assertEqual(self.chat().status_code,200)
        self.assertIn('رياضيات، الصف العاشر، 3 وحدات',self.ai.responses.parse.call_args.kwargs['instructions'])

    def fresh_server(self, name):
        self.db=Path(self.temp.name)/name
        self.app=self.make_app();self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']

    def test_no_profile_means_no_chat_and_not_ready(self):
        self.fresh_server('empty.sqlite3')
        state=self.state();self.assertIsNone(state['profile']);self.assertFalse(state['profile_ready'])
        refused=self.chat();self.assertEqual((refused.status_code,refused.json['error']),(409,'profile'))
        self.ai.responses.parse.assert_not_called();self.factory.assert_not_called()

    def test_a_profile_without_a_curriculum_country_must_be_completed_before_chatting(self):
        self.fresh_server('us.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'US','grade':9}).status_code,200)  # the old saved shape
        self.assertFalse(self.state()['profile_ready'])
        refused=self.chat()
        self.assertEqual((refused.status_code,refused.json['error']),(409,'profile_incomplete'))
        self.assertIn('الدولة والصف والوحدات',self.post('/api/chat',self.body(),headers={'X-NMI-Language':'ar'}).json['message'])
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':3}).status_code,200)
        self.assertTrue(self.state()['profile_ready'])
        self.assertEqual(self.chat().status_code,200)

    def test_profile_edit_keeps_the_conversation_and_the_next_message_loads_the_new_curriculum(self):
        self.fresh_server('edit.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':3}).status_code,200)
        self.assertEqual(self.chat().status_code,200)
        self.assertIn('رياضيات، الصف العاشر، 3 وحدات',self.ai.responses.parse.call_args.kwargs['cache_prefix'])
        before=self.state()
        self.assertEqual(len(before['history']),2)
        # Edit: another level and a target. Same endpoint, no 409 any more.
        edited={'country':'IL','grade':10,'subject':'math','units':3,'target_units':5}
        self.assertEqual(self.post('/api/profile',edited).status_code,200)
        after=self.state()
        self.assertEqual(after['profile'],edited);self.assertTrue(after['profile_ready'])
        self.assertEqual((after['history'],after['attempts']),(before['history'],before['attempts']))
        self.assertEqual(self.chat().status_code,200)
        prefix=self.ai.responses.parse.call_args.kwargs['cache_prefix']
        self.assertIn('رياضيات، الصف العاشر، 3 وحدات',prefix);self.assertIn('رياضيات، الصف العاشر، 5 وحدات',prefix)
        self.assertIn('# TARGET LEVEL CURRICULUM (5 units)',prefix)
        # Move to another level and drop the target: only the new curriculum is loaded.
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':11,'subject':'math','units':4}).status_code,200)
        self.assertEqual(self.chat().status_code,200)
        prefix=self.ai.responses.parse.call_args.kwargs['cache_prefix']
        self.assertIn('رياضيات، الصف الحادي عشر، 4 وحدات',prefix);self.assertNotIn('TARGET LEVEL',prefix);self.assertNotIn('3 وحدات (3',prefix)
        self.assertEqual(len(self.state()['history']),6)
        self.factory.assert_called()

    def test_profile_edit_is_refused_while_a_request_runs(self):
        self.fresh_server('busy.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':3}).status_code,200)
        started=threading.Event();release=threading.Event()
        def slow(**kwargs):
            started.set();release.wait(3)
            return SimpleNamespace(output_parsed=parsed(),status='completed')
        self.ai.responses.parse.side_effect=slow
        first=self.app.test_client()
        cookie=self.client.get_cookie(self.app.config['SESSION_COOKIE_NAME'],domain='127.0.0.1')
        first.set_cookie(self.app.config['SESSION_COOKIE_NAME'],cookie.value,domain='127.0.0.1')
        worker=threading.Thread(target=lambda:first.post('/api/chat',json=self.body(),base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':self.csrf}))
        worker.start();self.assertTrue(started.wait(2))
        try:
            self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':4}).json['error'],'busy')
        finally:release.set();worker.join(4)
        self.assertEqual(self.state()['profile']['units'],3)  # nothing changed mid-request

    def test_profile_edit_never_overwrites_unreadable_data(self):
        self.fresh_server('unreadable.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':3}).status_code,200)
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:db.execute('UPDATE state SET payload=?',('[]',))
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'units':4}).json['error'],'storage')
        with contextlib.closing(sqlite3.connect(self.db)) as db:self.assertEqual(db.execute('SELECT payload FROM state').fetchone()[0],'[]')

    def test_target_units_validation(self):
        from local_web import valid_profile
        base={'country':'IL','grade':10,'subject':'math','units':3}
        for target in (4,5):self.assertTrue(valid_profile(base|{'target_units':target}))
        self.assertTrue(valid_profile({'country':'IL','grade':10,'units':4,'target_units':5}))
        for bad in (3,2,6,'5',True,None,5.0):self.assertFalse(valid_profile(base|{'target_units':bad}),bad)
        self.assertFalse(valid_profile({'country':'IL','grade':10,'units':5,'target_units':4}))  # not higher
        self.assertFalse(valid_profile({'country':'IL','grade':10,'target_units':5}))  # no current level
        self.assertFalse(valid_profile({'country':'US','grade':10,'target_units':5}))
        for body in (base|{'target_units':3},base|{'target_units':9}):
            self.assertEqual(self.post('/api/profile',body).status_code,400)
        self.assertEqual(self.post('/api/profile',base|{'target_units':5}).status_code,200)

    KEY = 'القسم أ: y = 120 + 40x و y = 70x. القسم ب: x = 4 شهور والتكلفة 280 ₪.'

    def bagrut(self, **values):
        return parsed(mode='bagrut', explanation='نادي رياضي بيعرض اشتراكين.', question='**القسم أ:** اكتب المعادلتين') | values

    def test_the_hidden_answer_key_is_saved_but_never_reaches_the_browser(self):
        self.fresh_server('answer-key.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':3}).status_code,200)
        rid=str(uuid4())
        response=self.chat(self.bagrut(answer_key=self.KEY),request_id=rid)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['reply'],'نادي رياضي بيعرض اشتراكين.\n\n**القسم أ:** اكتب المعادلتين')
        # not in the chat answer, the state, the receipt or the saved conversation shown to the page
        state=self.state()
        receipt=self.client.get(f'/api/requests/{rid}',base_url=ORIGIN).json
        for shown in (json.dumps(response.json,ensure_ascii=False),json.dumps(state,ensure_ascii=False),json.dumps(receipt,ensure_ascii=False)):
            self.assertNotIn('x = 4',shown);self.assertNotIn('280',shown);self.assertNotIn(self.KEY,shown)
        self.assertNotIn('answer_key',state)
        self.assertEqual(set(state)&{'answer_key'},set())
        # but it is saved, with the conversation, for the tutor
        store=self.app.extensions['nmi_store']
        self.assertEqual(store.load()['answer_key'],self.KEY)
        with contextlib.closing(sqlite3.connect(self.db)) as db:self.assertIn('answer_key',db.execute('SELECT payload FROM state').fetchone()[0])
        # the next message gives it to the tutor, in the part that is not cached
        self.assertEqual(self.chat(self.bagrut(explanation='صح.',question='**القسم ب:** جد بعد كم شهر',answer_key=None)).status_code,200)
        call=self.ai.responses.parse.call_args.kwargs
        self.assertIn(self.KEY,call['instructions'][len(call['cache_prefix']):])
        self.assertNotIn(self.KEY,call['cache_prefix'])
        self.assertNotIn(self.KEY,json.dumps(self.state(),ensure_ascii=False))
        # editing the profile keeps the open question's key, still hidden
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':4}).status_code,200)
        self.assertEqual(store.load()['answer_key'],self.KEY)
        self.assertNotIn('answer_key',self.state())

    def test_a_bagrut_reply_without_any_key_or_with_the_key_in_the_text_is_refused_and_nothing_is_saved(self):
        self.fresh_server('answer-key-refused.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':3}).status_code,200)
        for result in (self.bagrut(),self.bagrut(explanation='الجواب x = 4 شهور',answer_key='x = 4 شهور')):
            with self.subTest(result=result['explanation']):
                response=self.chat(result)
                self.assertEqual((response.status_code,response.json['error']),(503,'response'))
                state=self.state()
                self.assertEqual((state['history'],state['attempts']),([],[]))
                self.assertIsNone(self.app.extensions['nmi_store'].load().get('answer_key'))

    def test_the_answer_key_field_is_checked_when_the_store_is_read(self):
        self.fresh_server('answer-key-shape.sqlite3')
        self.assertEqual(self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':3}).status_code,200)
        state=self.app.extensions['nmi_store'].load()
        for bad in (5,['x'],'x'*12001):
            with contextlib.closing(sqlite3.connect(self.db)) as db, db:
                db.execute('UPDATE state SET payload=?',(json.dumps(state|{'answer_key':bad}),))
            self.assertEqual(self.client.get('/api/state',base_url=ORIGIN).json['error'],'storage')
        for fine in (None,'مفتاح'):
            with contextlib.closing(sqlite3.connect(self.db)) as db, db:
                db.execute('UPDATE state SET payload=?',(json.dumps(state|{'answer_key':fine}),))
            self.assertNotIn('answer_key',self.client.get('/api/state',base_url=ORIGIN).json)

    def test_rate_limit_and_identical_text_distinct_requests(self):
        for _ in range(6):self.assertEqual(self.chat().status_code,200)
        self.assertEqual(self.chat().json['error'],'limit')
        self.assertEqual(self.ai.responses.parse.call_count,6)
        self.assertEqual(len(self.state()['history']),12)

    def test_second_launcher_stops_before_opening_database(self):
        import msvcrt
        import local_web
        base=Path(self.temp.name)
        directory=base/'.local-data';directory.mkdir()
        with (directory/'server.lock').open('w+b') as lock:
            lock.write(b'0');lock.flush();lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
            with patch.object(local_web,'ROOT',base),patch.object(local_web,'create_app') as factory:
                with self.assertRaises(SystemExit):local_web.main()
                factory.assert_not_called()
        self.assertFalse((directory/'tutor.sqlite3').exists())


if __name__=='__main__':unittest.main()
