"""Phase 1 regressions: no real credentials, sockets, student data or inference."""
from contextlib import ExitStack
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from local_web import create_app, ChatError
from tools.run_chatgpt import (build_test_app, build_conversation_app, owner_command,
                              report_saved_state, parse_options, exclusive_store)

ORIGIN = 'http://127.0.0.1:8766'
TOKEN = 'synthetic-private-session-capability'


class SessionReceiptTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'.cache/local-tests';base.mkdir(parents=True,exist_ok=True)
        temporary=tempfile.TemporaryDirectory(dir=base);self.addCleanup(temporary.cleanup)
        self.path=Path(temporary.name)
        stack=ExitStack();self.addCleanup(stack.close)
        stack.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('No network')))
        stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('No network')))
        self.auth=Mock(selected_model='',last_error='')
        self.auth.public_state.return_value=dict(connected=False,sharing=False,error='')
        self.auth.load_models.return_value=[dict(slug='synthetic-model',display_name='Synthetic')]
        self.auth.select_model.side_effect=self.select
        value=dict(reply='Synthetic answer',is_attempt=False,subject=None,topic=None,skill=None,correct=None,hint_used=None,mistake_type=None)
        self.client_ai=SimpleNamespace(responses=SimpleNamespace(parse=Mock(return_value=SimpleNamespace(status='completed',output_parsed=value))),close=Mock())
        self.api=Mock(side_effect=AssertionError('No API fallback'))
        self.plan=Mock(return_value=self.client_ai)
        self.app=self.make_app();self.client=self.app.test_client();self.csrf=''

    def select(self,model):
        if model!='synthetic-model':
            from chatgpt_auth import AuthError
            raise AuthError('model')
        self.auth.selected_model=model

    def make_app(self,**changes):
        return create_app(**(dict(data_path=self.path/(uuid4().hex+'.sqlite3'),access_token=TOKEN,
                    signin_enabled=True,enabled=False,chatgpt_auth=self.auth,client_factory=self.api,
                    plan_factory=self.plan)|changes))

    def get(self,path,client=None):return (client or self.client).get(path,base_url=ORIGIN)
    def post(self,path,body,client=None):return (client or self.client).post(path,json=body,base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':self.csrf})
    def unlock(self):
        self.get('/api/session/preflight')
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.post('/api/profile',{'country':'US','grade':10})
    def connect(self):self.auth.public_state.return_value=dict(connected=True,sharing=True,error='')
    def body(self,**changes):return dict(request_id=str(uuid4()),message='ما معنى الكسر؟',language='ar',intent='question',provider='chatgpt')|changes

    def test_blocked_cookie_does_not_consume_owner_claim(self):
        blocked=self.app.test_client(use_cookies=False)
        self.assertFalse(self.get('/api/session/preflight',blocked).json['cookie_ready'])
        self.assertFalse(self.get('/api/session/preflight',blocked).json['cookie_ready'])
        self.assertEqual(self.post('/api/session',{'token':TOKEN},blocked).json['error'],'cookies')
        self.assertEqual(self.get('/api/state',blocked).status_code,401)
        self.unlock();self.assertEqual(self.get('/api/state').status_code,200)

    def test_preflight_is_nonauthorizing_and_second_browser_stays_denied(self):
        self.assertFalse(self.get('/api/session/preflight').json['cookie_ready'])
        self.assertTrue(self.get('/api/session/preflight').json['cookie_ready'])
        self.assertEqual(self.get('/api/state').status_code,401)
        self.unlock()
        other=self.app.test_client();self.get('/api/session/preflight',other)
        self.assertEqual(self.post('/api/session',{'token':TOKEN},other).status_code,403)

    def test_read_only_receipts_require_owner_and_do_not_call_provider(self):
        rid=str(uuid4());url='/api/requests/'+rid
        self.assertEqual(self.get(url).status_code,401);self.unlock()
        self.assertEqual(self.get(url).json,{'status':'missing'})
        store=self.app.extensions['nmi_store'];store.begin(rid,'synthetic')
        self.assertEqual(self.get(url).json,{'status':'pending'})
        store.fail(rid,'timeout');self.assertEqual(self.get(url).json['error'],'timeout')
        self.assertEqual(self.get('/api/requests/not-a-uuid').status_code,400)
        self.api.assert_not_called();self.plan.assert_not_called()

    def test_arm_requires_grant_valid_model_and_disabled_paid_api(self):
        control=self.app.extensions['nmi_control']
        with self.assertRaises(ChatError):control.arm_chatgpt('synthetic-model')
        self.connect()
        from chatgpt_auth import AuthError
        with self.assertRaises(AuthError):control.arm_chatgpt('unauthorized')
        self.assertFalse(control.status()['enabled'])
        for changes in ({'allow_api':True},{'signin_enabled':False},{'enabled':True}):
            with self.assertRaises(ChatError):self.make_app(**changes).extensions['nmi_control'].arm_chatgpt('synthetic-model')
        self.api.assert_not_called();self.plan.assert_not_called()

    def test_one_request_mode_accepts_any_question_and_saves_receipt(self):
        self.unlock();self.connect();control=self.app.extensions['nmi_control']
        self.assertEqual(control.models()[0]['slug'],'synthetic-model')
        self.assertEqual(control.arm_chatgpt('synthetic-model'),{'enabled':True,'remaining':1})
        with self.assertRaises(ChatError):control.arm_chatgpt('synthetic-model')
        self.plan.assert_not_called()
        body=self.body(message='How do fractions work?',language='en')
        self.assertEqual(self.post('/api/chat',body).status_code,200)
        receipt=self.get('/api/requests/'+body['request_id']).json
        self.assertEqual(receipt,{'status':'done','reply':'Synthetic answer'})
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')
        self.assertTrue(self.post('/api/chat',body).json['replayed'])
        self.assertEqual(self.client_ai.responses.parse.call_count,1)
        self.assertEqual(len(self.get('/api/state').json['history']),2)
        self.assertEqual(self.get('/api/state').json['attempts'],[])
        self.api.assert_not_called()
        public=str(self.get('/api/state').json)
        self.assertNotIn('synthetic-model',public)

    def test_failed_stream_consumes_budget_without_history_and_cannot_rearm(self):
        self.unlock();self.connect();control=self.app.extensions['nmi_control']
        control.arm_chatgpt('synthetic-model')
        self.client_ai.responses.parse.side_effect=TimeoutError()
        body=self.body();self.assertEqual(self.post('/api/chat',body).json['error'],'timeout')
        self.assertEqual(self.get('/api/requests/'+body['request_id']).json['status'],'failed')
        self.assertEqual(self.get('/api/state').json['history'],[])
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')
        with self.assertRaises(ChatError):control.arm_chatgpt('synthetic-model')
        self.assertEqual(self.client_ai.responses.parse.call_count,1)

    def test_test_launcher_starts_off_preserves_existing_database_and_reports_counts(self):
        app=build_test_app(self.path/'harness',TOKEN)
        control=app.extensions['nmi_control'].status()
        self.assertFalse(control['enabled']);self.assertFalse(control['api_enabled'])
        self.assertEqual(report_saved_state(app),{'history_messages':0,'attempts':0,'receipts':{}})
        self.assertIsNone(owner_command(app,'quit'))
        self.assertFalse(owner_command(app,'status')['connection']['enabled'])
        with self.assertRaises(ValueError):build_test_app(self.path/'harness',TOKEN)

    def test_owner_can_enable_multiple_turns_but_browser_cannot_enable_or_select_model(self):
        self.app=self.make_app(max_calls=3);self.client=self.app.test_client()
        self.unlock();self.connect()
        self.assertEqual(owner_command(self.app,'enable synthetic-model'),{'enabled':True,'remaining':3})
        for message,language,intent in [('Explain a fraction.','en','question'),
                ('مش فاهم، أعطني مثالًا آخر.','ar','confusion'),('What about the denominator?','en','question')]:
            self.assertEqual(self.post('/api/chat',self.body(message=message,language=language,intent=intent)).status_code,200)
        self.assertEqual(self.client_ai.responses.parse.call_count,3)
        self.assertEqual(len(self.get('/api/state').json['history']),6)
        self.assertEqual(self.get('/api/state').json['attempts'],[])
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')
        with self.assertRaises(ChatError):owner_command(self.app,'enable synthetic-model')
        self.assertEqual(self.post('/api/chatgpt/model',{'model':'synthetic-model'}).status_code,403)
        self.assertEqual(self.post('/api/provider',{'provider':'api'}).status_code,403)
        self.api.assert_not_called()

    def test_conversation_launcher_preserves_profile_and_history_on_restart(self):
        directory=self.path/'persistent'
        with patch('tools.run_chatgpt.ChatGPTAuth',return_value=self.auth):
            first=build_conversation_app(directory,TOKEN)
            self.assertEqual(first.extensions['nmi_store'].load(),{'profile':None,'history':[],'attempts':[]})
            store=first.extensions['nmi_store']
            store.set_profile({'country':'QA','grade':11})
            saved=store.load()
            saved['history']=[{'role':'user','content':'Synthetic question'},
                              {'role':'assistant','content':'Synthetic response'}]
            saved['attempts']=[dict(subject='physics',topic='motion',skill='speed',correct=True,hint_used=False,mistake_type=None)]
            store.begin('fixture','fixture');store.commit('fixture',saved,'Synthetic response')
            restarted=build_conversation_app(directory,TOKEN,max_calls=25)
            self.assertEqual(restarted.extensions['nmi_store'].load(),saved)
            status=owner_command(restarted,'status')['connection']
            self.assertFalse(status['enabled']);self.assertFalse(status['api_enabled'])
            self.assertEqual(status['remaining'],25)
            self.assertTrue(status['signin_enabled'])
        self.api.assert_not_called();self.plan.assert_not_called()

    def test_launcher_options_and_store_lock(self):
        self.assertEqual(parse_options([]).max_calls,20)
        self.assertEqual(parse_options(['--max-calls','45']).max_calls,45)
        self.assertEqual(parse_options(['--acceptance']).max_calls,1)
        for invalid in (True,0,101,'20'):
            with self.assertRaises(ValueError):self.make_app(max_calls=invalid)
        with exclusive_store(self.path/'locked'):
            with self.assertRaises(SystemExit):
                with exclusive_store(self.path/'locked'):self.fail('Second writer acquired the store')
        with exclusive_store(self.path/'locked'):pass


if __name__=='__main__':unittest.main()
