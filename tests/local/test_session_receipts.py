"""Session claim, receipts and single-store regressions: no real credentials, sockets or inference."""
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
from local_web import create_app
from tools.run_claude import exclusive_store

ORIGIN = 'http://127.0.0.1:8766'
TOKEN = 'synthetic-private-session-capability'
MODEL = 'claude-synthetic-model'


class SessionReceiptTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'.cache/local-tests';base.mkdir(parents=True,exist_ok=True)
        temporary=tempfile.TemporaryDirectory(dir=base);self.addCleanup(temporary.cleanup)
        self.path=Path(temporary.name)
        stack=ExitStack();self.addCleanup(stack.close)
        stack.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('No network')))
        stack.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('No network')))
        value=dict(reply='Synthetic answer',is_attempt=False,subject=None,topic=None,skill=None,correct=None,hint_used=None,mistake_type=None)
        self.client_ai=SimpleNamespace(responses=SimpleNamespace(parse=Mock(return_value=SimpleNamespace(status='completed',output_parsed=value))),close=Mock())
        self.factory=Mock(return_value=self.client_ai)
        self.app=self.make_app();self.client=self.app.test_client();self.csrf=''

    def make_app(self,**changes):
        return create_app(**(dict(data_path=self.path/(uuid4().hex+'.sqlite3'),access_token=TOKEN,
                    enabled=True,allow_claude=True,claude_model=MODEL,claude_factory=self.factory)|changes))

    def get(self,path,client=None):return (client or self.client).get(path,base_url=ORIGIN)
    def post(self,path,body,client=None):return (client or self.client).post(path,json=body,base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':self.csrf})
    def unlock(self):
        self.get('/api/session/preflight')
        self.csrf=self.post('/api/session',{'token':TOKEN}).json['csrf']
        self.post('/api/profile',{'country':'IL','grade':10,'subject':'math','units':4})
    def body(self,**changes):return dict(request_id=str(uuid4()),message='ما معنى الكسر؟',language='ar',intent='question')|changes

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
        self.factory.assert_not_called()

    def test_single_request_saves_receipt_and_budget_blocks_the_next(self):
        self.app=self.make_app(max_calls=1);self.client=self.app.test_client()
        self.unlock()
        body=self.body(message='How do fractions work?',language='en')
        self.assertEqual(self.post('/api/chat',body).status_code,200)
        receipt=self.get('/api/requests/'+body['request_id']).json
        self.assertEqual(receipt,{'status':'done','reply':'Synthetic answer'})
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')
        self.assertTrue(self.post('/api/chat',body).json['replayed'])
        self.assertEqual(self.client_ai.responses.parse.call_count,1)
        self.assertEqual(len(self.get('/api/state').json['history']),2)
        self.assertEqual(self.get('/api/state').json['attempts'],[])

    def test_failed_request_consumes_budget_without_history(self):
        self.app=self.make_app(max_calls=1);self.client=self.app.test_client()
        self.unlock()
        self.client_ai.responses.parse.side_effect=TimeoutError()
        body=self.body();self.assertEqual(self.post('/api/chat',body).json['error'],'timeout')
        self.assertEqual(self.get('/api/requests/'+body['request_id']).json['status'],'failed')
        self.assertEqual(self.get('/api/state').json['history'],[])
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')
        self.assertEqual(self.client_ai.responses.parse.call_count,1)

    def test_multiple_turns_within_budget(self):
        self.app=self.make_app(max_calls=3);self.client=self.app.test_client()
        self.unlock()
        for message,language,intent in [('Explain a fraction.','en','question'),
                ('مش فاهم، أعطني مثالًا آخر.','ar','confusion'),('What about the denominator?','en','question')]:
            self.assertEqual(self.post('/api/chat',self.body(message=message,language=language,intent=intent)).status_code,200)
        self.assertEqual(self.client_ai.responses.parse.call_count,3)
        self.assertEqual(len(self.get('/api/state').json['history']),6)
        self.assertEqual(self.get('/api/state').json['attempts'],[])
        self.assertEqual(self.post('/api/chat',self.body()).json['error'],'limit')

    def test_profile_and_history_survive_restart(self):
        path=self.path/'persistent.sqlite3'
        first=self.make_app(data_path=path)
        store=first.extensions['nmi_store']
        self.assertEqual(store.load(),{'profile':None,'history':[],'attempts':[]})
        store.set_profile({'country':'QA','grade':11})
        saved=store.load()
        saved['history']=[{'role':'user','content':'Synthetic question'},
                          {'role':'assistant','content':'Synthetic response'}]
        store.begin('fixture','fixture');store.commit('fixture',saved,'Synthetic response')
        restarted=self.make_app(data_path=path)
        self.assertEqual(restarted.extensions['nmi_store'].load(),saved)
        self.factory.assert_not_called()

    def test_attempt_limit_validation_and_store_lock(self):
        for invalid in (True,0,101,'20'):
            with self.assertRaises(ValueError):self.make_app(max_calls=invalid)
        with exclusive_store(self.path/'locked'):
            with self.assertRaises(SystemExit):
                with exclusive_store(self.path/'locked'):self.fail('Second writer acquired the store')
        with exclusive_store(self.path/'locked'):pass


if __name__=='__main__':unittest.main()
