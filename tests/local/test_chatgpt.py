"""Real JWT signatures and SDK SSE parsing, entirely synthetic and socket-denied."""
import contextlib
import copy
import hashlib
import io
import json
import logging
from pathlib import Path
import socket
import sys
import tempfile
import time
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
import httpx2 as httpx
from openai import OpenAI
from pydantic import ValidationError
from chatgpt_auth import ChatGPTAuth, AuthError, DIRECT, ISSUER, TOKEN, JWKS, DISCOVERY, RESOURCE
from chatgpt_provider import ChatGPTProvider, PlanError
from learning_result import LearningResult
from ai_test import InvalidAIResponse
from local_web import create_app

ORIGIN = 'http://127.0.0.1:8766'
LOCAL_TOKEN = 'synthetic-local-capability-00000000'
CID = 'oaiapp_synthetic'


def learning(**changes):
    return dict(reply='Synthetic reply', is_attempt=False, subject=None, topic=None, skill=None,
                correct=None, hint_used=None, mistake_type=None) | changes


class AuthFixture:
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(cls.key.public_key())) | {'kid':'synthetic', 'alg':'RS256', 'use':'sig'}

    def setUp(self):
        base = ROOT / '.cache/oauth-tests'
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')))
        self.stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('No network')))
        self.transport = Mock()
        self.clock = [time.time()]
        self.path = Path(self.temp.name) / 'registration.json'
        self.auth = ChatGPTAuth(self.path, ORIGIN + '/auth/callback', transport=self.transport, clock=lambda:self.clock[0])
        self.overrides = {}
        self.scopes = 'openid resource.invoke ' + DIRECT
        self.transport.request.side_effect = self.request

    def request(self, method, url, **kwargs):
        if url == JWKS:
            return {'keys':[self.jwk]}
        if url == DISCOVERY:
            return {'issuer':ISSUER, 'revocation_endpoint':ISSUER+'/api/accounts/oauth/revoke'}
        if url.endswith('/revoke'):
            return {}
        if url == RESOURCE + '/models':
            return {'models':[{'slug':'synthetic-model','display_name':'Synthetic model','visibility':'list'},
                              {'slug':'hidden','display_name':'Hidden','visibility':'hide'}]}
        if url == TOKEN:
            payload = dict(access_token='SYNTHETIC_ACCESS', refresh_token='SYNTHETIC_REFRESH', token_type='Bearer', expires_in=3600, scope=self.scopes)
            if kwargs['data']['grant_type'] == 'authorization_code':
                claims = dict(iss=ISSUER, aud=CID, sub='synthetic-subject', nonce=self.nonce, exp=int(time.time())+300, iat=int(time.time())) | self.overrides
                payload['id_token'] = jwt.encode(claims,self.key,algorithm='RS256',headers={'kid':'synthetic'})
            else:
                payload.update(access_token='SYNTHETIC_ROTATED_ACCESS',refresh_token='SYNTHETIC_ROTATED_REFRESH')
            return payload
        raise AssertionError('Unexpected synthetic route')

    def start(self):
        params = {k:v[0] for k,v in parse_qs(urlsplit(self.auth.start()).query).items()}
        self.nonce = params['nonce']
        return params

    def finish(self, params):
        self.auth.finish(dict(state=params['state'], code='synthetic-code', client_id=CID))

    def login(self):
        self.finish(self.start())


class AuthTests(AuthFixture, unittest.TestCase):
    def test_pkce_scopes_host_and_exact_callback(self):
        params = self.start()
        self.assertEqual(params['client_id'],'dynamic_agent_client')
        self.assertEqual(params['agent_name_hint'],'NMI')
        self.assertEqual(params['code_challenge_method'],'S256')
        import base64
        expected=base64.urlsafe_b64encode(hashlib.sha256(self.auth.pending['verifier'].encode()).digest()).rstrip(b'=').decode()
        self.assertEqual(params['code_challenge'],expected)
        self.assertEqual(params['redirect_uri'],ORIGIN+'/auth/callback')
        self.assertIn(DIRECT,params['scope'])
        self.assertNotIn('id_token_hint',params)
        self.finish(params)
        exchange=[c.kwargs['data'] for c in self.transport.request.call_args_list if c.args[1]==TOKEN][0]
        self.assertEqual(exchange['client_id'],CID)
        self.assertEqual(exchange['redirect_uri'],params['redirect_uri'])
        self.assertNotIn('client_secret',exchange)

    def test_success_and_no_credentials_on_disk_or_public_state(self):
        self.login()
        self.assertTrue(self.auth.public_state()['sharing'])
        self.assertEqual(self.auth.access_token(),'SYNTHETIC_ACCESS')
        content=self.path.read_text()+json.dumps(self.auth.public_state())
        for forbidden in ('SYNTHETIC_ACCESS','SYNTHETIC_REFRESH','id_token','access_token','refresh_token'):
            self.assertNotIn(forbidden,content)

    def test_wrong_state_expiry_denial_and_replay(self):
        params=self.start()
        with self.assertRaises(AuthError):self.auth.finish(dict(state='wrong',code='x',client_id=CID))
        self.transport.request.assert_not_called()
        self.clock[0]+=301
        with self.assertRaises(AuthError):self.finish(params)
        self.transport.request.assert_not_called()
        params=self.start()
        with self.assertRaises(AuthError):self.auth.finish(dict(state=params['state'],error='access_denied'))
        with self.assertRaises(AuthError):self.finish(params)
        self.transport.request.assert_not_called()

    def test_signature_issuer_audience_expiration_nonce_and_azp(self):
        cases=[{'iss':'https://evil.invalid'}, {'aud':'other'}, {'exp':int(time.time())-1},
               {'nonce':'wrong'}, {'nbf':int(time.time())+600}, {'azp':'other'}, {'sub':''}]
        for changes in cases:
            with self.subTest(fields=list(changes)):
                self.overrides=changes
                params=self.start()
                with self.assertRaises(AuthError):self.finish(params)
                self.assertIsNone(self.auth.credentials)
        params=self.start()
        encoded=jwt.encode(dict(iss=ISSUER,aud=CID,sub='a',nonce=self.nonce,exp=int(time.time())+300,iat=int(time.time())), 'synthetic-secret-for-HS256-test-only', algorithm='HS256',headers={'kid':'synthetic'})
        with self.assertRaises(AuthError):self.auth._verify(encoded,CID,self.nonce)
        foreign=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        encoded=jwt.encode(dict(iss=ISSUER,aud=CID,sub='a',nonce=self.nonce,exp=int(time.time())+300,iat=int(time.time())),foreign,algorithm='RS256',headers={'kid':'synthetic'})
        with self.assertRaises(AuthError):self.auth._verify(encoded,CID,self.nonce)

    def test_missing_scope_cannot_infer_and_reconsent(self):
        self.scopes='openid'
        self.login()
        self.assertTrue(self.auth.public_state()['connected'])
        self.assertFalse(self.auth.public_state()['sharing'])
        with self.assertRaises(AuthError):self.auth.access_token()
        params=self.start()
        self.assertEqual(params['prompt'],'consent')
        self.assertEqual(params['client_id'],CID)
        self.assertNotIn('agent_name_hint',params)

    def test_restart_reuses_registration_but_not_tokens(self):
        self.login();before=json.loads(self.path.read_text())
        self.auth=ChatGPTAuth(self.path,ORIGIN+'/auth/callback',transport=self.transport)
        params=self.start()
        self.assertEqual(params['client_id'],CID)
        self.assertEqual(params['ext_agent_host_id'],before['host_id'])
        self.assertIsNone(self.auth.credentials)

    def test_different_account_and_client_are_rejected(self):
        self.login();old=self.auth.credentials.copy()
        params=self.start()
        with self.assertRaises(AuthError):self.auth.finish(dict(state=params['state'],code='x',client_id='oaiapp_other'))
        self.assertEqual(self.auth.credentials,old)
        params=self.start();self.overrides={'sub':'other-subject'}
        with self.assertRaises(AuthError):self.finish(params)
        self.assertEqual(self.auth.credentials,old)
        self.assertEqual(json.loads(self.path.read_text())['subject'],'synthetic-subject')

    def test_corrupt_registration_is_preserved(self):
        self.path.write_text('{corrupt')
        with self.assertRaises(AuthError):self.start()
        self.assertEqual(self.path.read_text(),'{corrupt')
        self.transport.request.assert_not_called()

    def test_refresh_rotation_and_no_scope_or_dynamic_client(self):
        self.login();self.clock[0]+=3590
        self.assertEqual(self.auth.access_token(),'SYNTHETIC_ROTATED_ACCESS')
        self.assertEqual(self.auth.credentials['refresh_token'],'SYNTHETIC_ROTATED_REFRESH')
        data=self.transport.request.call_args.kwargs['data']
        self.assertEqual(data['client_id'],CID)
        self.assertEqual(data['grant_type'],'refresh_token')
        self.assertNotIn('scope',data)
        self.assertNotIn('SYNTHETIC_ROTATED',self.path.read_text())

    def test_refresh_terminal_vs_temporary_failure(self):
        self.login();self.clock[0]+=3590
        self.transport.request.side_effect=AuthError('oauth')
        with self.assertRaises(AuthError):self.auth.access_token()
        self.assertIsNotNone(self.auth.credentials)
        self.transport.request.side_effect=AuthError('signin')
        with self.assertRaises(AuthError):self.auth.access_token()
        self.assertIsNone(self.auth.credentials)

    def test_refresh_permission_removed_disables_usage(self):
        self.login();self.clock[0]+=3590;self.scopes='openid'
        with self.assertRaises(AuthError) as error:self.auth.access_token()
        self.assertEqual(error.exception.code,'consent')
        self.assertFalse(self.auth.public_state()['sharing'])
        self.assertEqual(self.auth.credentials['refresh_token'],'SYNTHETIC_ROTATED_REFRESH')

    def test_models_visibility_and_allowlist(self):
        self.login();models=self.auth.load_models()
        self.assertEqual(len(models),1)
        with self.assertRaises(AuthError):self.auth.select_model('hidden')
        self.auth.select_model('synthetic-model')
        self.assertEqual(self.auth.selected_model,'synthetic-model')

    def test_signout_revokes_and_keeps_binding(self):
        self.login();before=self.path.read_text()
        self.assertTrue(self.auth.sign_out())
        self.assertIsNone(self.auth.credentials)
        self.assertEqual(self.path.read_text(),before)
        self.assertEqual(self.transport.request.call_args.kwargs['data']['token_type_hint'],'refresh_token')

    def test_failed_revocation_still_forgets_local_tokens(self):
        self.login();self.transport.request.side_effect=AuthError()
        self.assertFalse(self.auth.sign_out())
        self.assertIsNone(self.auth.credentials)
        self.assertEqual(self.auth.public_state()['error'],'revocation')

    def test_missing_identity_claims_and_unknown_signing_key(self):
        claims=dict(iss=ISSUER,aud=CID,sub='synthetic',exp=int(time.time())+300,iat=int(time.time()),nonce='synthetic-nonce')
        for missing in ('iss','aud','sub','exp','iat','nonce'):
            bad=claims.copy();bad.pop(missing)
            encoded=jwt.encode(bad,self.key,algorithm='RS256',headers={'kid':'synthetic'})
            with self.assertRaises(AuthError):self.auth._verify(encoded,CID,'synthetic-nonce')
        encoded=jwt.encode(claims,self.key,algorithm='RS256',headers={'kid':'unknown'})
        with self.assertRaises(AuthError):self.auth._verify(encoded,CID,'synthetic-nonce')

    def test_concurrent_refresh_is_serialized(self):
        import concurrent.futures
        self.login();self.clock[0]+=3590
        before=self.transport.request.call_count
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.auth.access_token(),range(2)))
        self.assertEqual(results,['SYNTHETIC_ROTATED_ACCESS']*2)
        self.assertEqual(self.transport.request.call_count-before,1)

    def test_identity_only_grant_without_access_token_is_connected_but_disabled(self):
        params=self.start()
        original=self.request
        def identity_only(method,url,**kwargs):
            data=original(method,url,**kwargs)
            if url==TOKEN:return {'id_token':data['id_token'],'scope':'openid profile email'}
            return data
        self.transport.request.side_effect=identity_only
        self.finish(params)
        self.assertTrue(self.auth.public_state()['connected'])
        self.assertFalse(self.auth.public_state()['sharing'])
        with self.assertRaises(AuthError):self.auth.access_token()

    def test_revocation_discovery_cannot_redirect_credentials(self):
        self.login()
        self.transport.request.return_value={'issuer':ISSUER,'revocation_endpoint':'https://evil.invalid/revoke'}
        self.transport.request.side_effect=None
        self.assertFalse(self.auth.sign_out())
        self.assertEqual(self.transport.request.call_args.args,('GET',DISCOVERY))

    def test_invalid_callback_configuration(self):
        for uri in ('https://127.0.0.1:8766/auth/callback','http://localhost:8766/auth/callback','http://127.0.0.1:8766/wrong','http://127.0.0.1:8766/auth/callback?x=1'):
            with self.assertRaises(ValueError):ChatGPTAuth(self.path,uri)


def stream_sdk(value=None, terminal='completed', refusal=False, error_code=None, status=200, capture=None):
    value=learning() if value is None else value
    base=dict(id='resp_synthetic',object='response',created_at=0,model='synthetic-model',status='in_progress',output=[],error=None,incomplete_details=None,instructions=None,metadata={},parallel_tool_calls=False,temperature=None,tool_choice='auto',tools=[],top_p=None)
    content={'type':'refusal','refusal':'Synthetic refusal'} if refusal else {'type':'output_text','text':json.dumps(value),'annotations':[]}
    final=base | dict(status=terminal,output=[dict(id='msg_synthetic',type='message',role='assistant',status='completed',content=[content])])
    if error_code:final['error']={'code':error_code,'message':'SYNTHETIC_PRIVATE_DETAIL'}
    events=[dict(type='response.created',sequence_number=0,response=base)]
    if terminal!='disconnected':events.append(dict(type='response.'+terminal,sequence_number=1,response=final))
    def transport(request):
        if capture is not None:capture.append(json.loads(request.content))
        if status!=200:return httpx.Response(status,json={'error':{'code':error_code,'message':'SYNTHETIC_PRIVATE_DETAIL'}})
        return httpx.Response(200,headers={'Content-Type':'text/event-stream'},content=''.join('data: '+json.dumps(e)+'\n\n' for e in events))
    return OpenAI(api_key='SYNTHETIC_ACCESS',base_url=RESOURCE,max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(transport),trust_env=False))


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.stack=contextlib.ExitStack();self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('No network')))

    def run_stream(self, **kwargs):
        sdk=stream_sdk(**kwargs);provider=ChatGPTProvider('synthetic','synthetic-model',sdk=sdk)
        self.addCleanup(provider.close)
        return provider.parse(model='synthetic-model',instructions='Preserved synthetic rules',input=[{'role':'user','content':'Synthetic'}],text_format=LearningResult,max_output_tokens=1800)

    def test_wire_contract_and_valid_assessments(self):
        bodies=[]
        self.assertFalse(self.run_stream(capture=bodies).output_parsed.is_attempt)
        body=bodies[0]
        self.assertTrue(body['stream']);self.assertFalse(body['store'])
        self.assertNotIn('max_output_tokens',body)
        self.assertEqual(body['text']['format']['type'],'json_schema')
        for correct in (True,False):
            result=self.run_stream(value=learning(is_attempt=True,subject='physics',topic='motion',skill='speed',correct=correct,hint_used=False))
            self.assertEqual(result.output_parsed.correct,correct)

    def test_invalid_incomplete_interrupted_and_refused(self):
        for kwargs in ({'value':learning(is_attempt=True)}, {'terminal':'incomplete'}, {'terminal':'disconnected'}, {'refusal':True}):
            with self.subTest(case=kwargs),self.assertRaises(InvalidAIResponse):self.run_stream(**kwargs)

    def test_usage_and_admission_errors_are_sanitized(self):
        for status,terminal,code,expected in [(200,'failed','subscription_sharing_usage_limit_exceeded','plan_limit'),(403,'completed','subscription_sharing_user_not_eligible','plan_eligibility'),(503,'completed','subscription_sharing_usage_unavailable','plan_unavailable'),(400,'completed','subscription_sharing_unsupported_capability','model')]:
            with self.assertRaises(PlanError) as result:self.run_stream(status=status,terminal=terminal,error_code=code)
            self.assertEqual(result.exception.code,expected)
            self.assertNotIn('SYNTHETIC_PRIVATE',str(result.exception))


class FlaskPlanTests(AuthFixture, unittest.TestCase):
    # Run actual OAuth service and real SDK parser through Flask, with synthetic transports.
    def setUp(self):
        super().setUp()
        import ai_test
        for name in ('load_history','load_progress','record_attempt','save_history'):
            self.stack.enter_context(patch.object(ai_test,name,side_effect=AssertionError('CLI data forbidden')))
        self.value=learning();self.terminal='completed';self.sdk_calls=[]
        def factory(token,model):
            self.assertEqual(token,'SYNTHETIC_ACCESS')
            return ChatGPTProvider(token,model,sdk=stream_sdk(self.value,terminal=self.terminal,capture=self.sdk_calls))
        self.api_factory=Mock(side_effect=AssertionError('No paid fallback'))
        self.plan_factory=factory
        self.app=create_app(data_path=Path(self.temp.name)/'state.sqlite3',access_token=LOCAL_TOKEN,enabled=True,
                            signin_enabled=True,chatgpt_auth=self.auth,plan_factory=factory,max_calls=20,
                            client_factory=self.api_factory,plan_model='synthetic-model')
        self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':LOCAL_TOKEN}).json['csrf']
        self.post('/api/profile',{'country':'QA','grade':11})

    def post(self,path,body):
        if path == '/api/session':
            self.client.get('/api/session/preflight', base_url=ORIGIN)
        return self.client.post(path,json=body,base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':getattr(self,'csrf','')})

    def state(self):return self.client.get('/api/state',base_url=ORIGIN).json

    def connect(self):
        self.post('/api/provider',{'provider':'chatgpt'})
        response=self.post('/api/chatgpt/start',{})
        params={k:v[0] for k,v in parse_qs(urlsplit(response.json['url']).query).items()}
        self.nonce=params['nonce']
        callback=self.client.get('/auth/callback',query_string={'state':params['state'],'code':'synthetic','client_id':CID},base_url=ORIGIN,headers={'Sec-Fetch-Site':'cross-site'})
        self.assertEqual(callback.status_code,303)
        self.assertEqual(self.post('/api/chatgpt/models',{}).status_code,200)
        self.assertEqual(self.post('/api/chatgpt/model',{'model':'synthetic-model'}).status_code,403)

    def message(self,**extra):return dict(request_id=str(uuid4()),message='Synthetic question',language='en',intent='question',provider='chatgpt')|extra

    def test_complete_stream_persistence_and_no_paid_fallback(self):
        self.connect();body=self.message()
        self.assertEqual(self.post('/api/chat',body).status_code,200)
        self.assertTrue(self.post('/api/chat',body).json['replayed'])
        self.assertEqual(len(self.sdk_calls),1)
        self.assertEqual(len(self.state()['history']),2)
        self.assertEqual(self.state()['attempts'],[])
        self.value=learning(is_attempt=True,subject='mathematics',topic='fractions',skill='sum',correct=False,hint_used=False,mistake_type='synthetic')
        self.assertEqual(self.post('/api/chat',self.message(intent='answer')).status_code,200)
        self.assertEqual(len(self.state()['attempts']),1)
        self.api_factory.assert_not_called()

    def test_invalid_stream_preserves_previous_state_and_receipt(self):
        self.connect();self.post('/api/chat',self.message());before=self.state()
        for terminal in ('failed','incomplete','disconnected'):
            self.terminal=terminal;body=self.message()
            self.assertEqual(self.post('/api/chat',body).status_code,503)
            self.assertEqual(self.post('/api/chat',body).status_code,409)
            self.assertEqual(self.state()['history'],before['history'])
            self.assertEqual(self.state()['attempts'],before['attempts'])
        self.api_factory.assert_not_called()

    def test_arabic_english_followups_use_saved_context_and_resume_after_restart(self):
        self.connect()
        history=[]
        messages=[('ما معنى الكسر؟','ar','question'),
                  ('مش فاهم، ممكن مثال أصغر؟','ar','question'),
                  ('Why do plants need light?','en','question'),
                  ('Could you explain that another way?','en','confusion')]
        for number,(message,language,intent) in enumerate(messages):
            reply=f'Synthetic contextual reply {number}'
            self.value=learning(reply=reply)
            result=self.post('/api/chat',self.message(message=message,language=language,intent=intent))
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.json['reply'],reply)
            request=self.sdk_calls[-1]
            self.assertEqual(request['input'],history+[{'role':'user','content':message}])
            self.assertIn('Infer the likely subject, topic and immediate learning need',request['instructions'])
            self.assertIn('مش فاهم',request['instructions'])
            self.assertIn('Do not repeat the same explanation.',request['instructions'])
            self.assertTrue(request['stream']);self.assertFalse(request['store'])
            self.assertEqual(request['text']['format']['type'],'json_schema')
            history.extend([{'role':'user','content':message},{'role':'assistant','content':reply}])
            self.assertEqual(self.state()['history'],history)
            self.assertEqual(self.state()['attempts'],[])

        # A mistaken model assessment must not score a question or confusion.
        self.value=learning(reply='Synthetic alternative example',is_attempt=True,
            subject='mathematics',topic='fractions',skill='sum',correct=False,hint_used=False)
        self.assertEqual(self.post('/api/chat',self.message(message='مش فاهم',language='ar',intent='confusion')).status_code,200)
        before=self.state()
        self.assertEqual(before['attempts'],[])
        self.terminal='disconnected'
        self.assertEqual(self.post('/api/chat',self.message(message='Another follow-up')).status_code,503)
        self.assertEqual(self.state()['history'],before['history'])

        # Restart against this temporary fixture only. OAuth is mocked and owner
        # enable remains necessary; no startup request or automatic retry occurs.
        self.app=create_app(data_path=Path(self.temp.name)/'state.sqlite3',access_token=LOCAL_TOKEN,
            enabled=False,signin_enabled=True,chatgpt_auth=self.auth,plan_factory=self.plan_factory,
            client_factory=self.api_factory,max_calls=20)
        self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':LOCAL_TOKEN}).json['csrf']
        self.assertFalse(self.state()['enabled'])
        self.assertEqual(self.state()['history'],before['history'])
        self.app.extensions['nmi_control'].arm_chatgpt('synthetic-model')
        self.terminal='completed';self.value=learning(reply='Synthetic resumed reply')
        self.assertEqual(self.post('/api/chat',self.message(message='Continue from our last example')).status_code,200)
        self.assertEqual(self.sdk_calls[-1]['input'][:-1],before['history'])
        self.assertEqual(self.state()['attempts'],before['attempts'])
        self.api_factory.assert_not_called()

    def test_oauth_routes_require_owner_csrf_and_explicit_gate(self):
        for path in ('/api/chatgpt/start','/api/chatgpt/models','/api/chatgpt/model','/api/chatgpt/signout','/api/provider'):
            response=self.client.post(path,json={},base_url=ORIGIN,headers={'Origin':ORIGIN})
            self.assertEqual(response.status_code,403)
        stranger=self.app.test_client()
        self.assertEqual(stranger.post('/api/chatgpt/start',json={},base_url=ORIGIN,headers={'Origin':ORIGIN}).status_code,401)
        self.transport.request.assert_not_called()
        self.assertEqual(self.client.get('/auth/callback?state=wrong&code=synthetic',base_url=ORIGIN).status_code,303)
        self.transport.request.assert_not_called()

    def test_disabled_launch_and_unknown_model_never_call_provider(self):
        app=create_app(data_path=Path(self.temp.name)/'disabled.sqlite3',access_token=LOCAL_TOKEN,chatgpt_auth=self.auth)
        c=app.test_client();c.get('/api/session/preflight',base_url=ORIGIN)
        r=c.post('/api/session',json={'token':LOCAL_TOKEN},base_url=ORIGIN,headers={'Origin':ORIGIN})
        r=c.post('/api/chatgpt/start',json={},base_url=ORIGIN,headers={'Origin':ORIGIN,'X-NMI-CSRF':r.json['csrf']})
        self.assertEqual(r.status_code,503);self.transport.request.assert_not_called()
        self.connect()
        self.assertEqual(self.post('/api/chatgpt/model',{'model':'not-authorized'}).status_code,403)
        self.assertEqual(len(self.sdk_calls),0)

    def test_public_routes_and_logs_never_contain_credentials(self):
        output=io.StringIO();handler=logging.StreamHandler(output);logging.getLogger().addHandler(handler)
        self.addCleanup(logging.getLogger().removeHandler,handler)
        self.connect()
        text=json.dumps(self.state())+self.client.get('/',base_url=ORIGIN).get_data(as_text=True)+output.getvalue()
        for secret in ('SYNTHETIC_ACCESS','SYNTHETIC_REFRESH','synthetic-code','synthetic-subject'):
            self.assertNotIn(secret,text)
        self.assertEqual(self.client.get('/state.chatgpt-registration.json',base_url=ORIGIN).status_code,404)

    def test_paid_api_disabled_and_model_not_returned_to_student(self):
        self.connect()
        self.assertEqual(self.post('/api/provider',{'provider':'api'}).status_code,403)
        self.assertEqual(self.state()['provider'],'chatgpt')
        self.assertFalse(self.state()['api_enabled'])
        self.assertTrue(self.state()['chatgpt']['ready'])
        self.assertNotIn('models',self.state()['chatgpt'])
        self.assertNotIn('model',self.state()['chatgpt'])
        self.assertEqual(self.post('/api/chat',self.message(provider='api')).status_code,409)
        self.api_factory.assert_not_called()

    def test_revoked_catalog_model_never_infers(self):
        self.connect()
        original=self.request
        self.transport.request.side_effect=lambda method,url,**kw: {'models':[]} if url==RESOURCE+'/models' else original(method,url,**kw)
        self.assertEqual(self.post('/api/chat',self.message()).json['error'],'model')
        self.assertEqual(self.sdk_calls,[])
        self.assertEqual(self.state()['history'],[])
        self.api_factory.assert_not_called()

    def test_exactly_one_plan_inference_and_duplicate_replay(self):
        self.app=create_app(data_path=Path(self.temp.name)/'one.sqlite3',access_token=LOCAL_TOKEN,
            enabled=True,signin_enabled=True,chatgpt_auth=self.auth,plan_factory=self.plan_factory,
            client_factory=self.api_factory,plan_model='synthetic-model')
        self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':LOCAL_TOKEN}).json['csrf']
        self.post('/api/profile',{'country':'QA','grade':11})
        self.connect();body=self.message()
        self.assertEqual(self.post('/api/chat',body).status_code,200)
        self.assertTrue(self.post('/api/chat',body).json['replayed'])
        self.assertEqual(self.post('/api/chat',self.message()).json['error'],'limit')
        self.assertEqual(len(self.sdk_calls),1)
        self.assertEqual(len(self.state()['history']),2)
        self.api_factory.assert_not_called()

    def test_missing_owner_model_blocks_inference(self):
        self.app=create_app(data_path=Path(self.temp.name)/'missing-model.sqlite3',access_token=LOCAL_TOKEN,
            enabled=True,signin_enabled=True,chatgpt_auth=self.auth,client_factory=self.api_factory,
            plan_factory=self.plan_factory)
        self.client=self.app.test_client()
        self.csrf=self.post('/api/session',{'token':LOCAL_TOKEN}).json['csrf']
        self.post('/api/profile',{'country':'QA','grade':11})
        self.assertEqual(self.post('/api/chat',self.message()).json['error'],'model')
        self.transport.request.assert_not_called();self.assertEqual(self.sdk_calls,[])


if __name__=='__main__':unittest.main()
