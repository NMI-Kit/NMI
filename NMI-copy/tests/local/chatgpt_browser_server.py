"""Browser fixture only. Real JWT verification + SDK parser, never a remote request."""
from pathlib import Path
import json
import socket
import sys
import tempfile
import time
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from chatgpt_auth import ChatGPTAuth, ISSUER, JWKS, TOKEN, DISCOVERY, RESOURCE, DIRECT
from chatgpt_provider import ChatGPTProvider
from local_web import create_app
from test_chatgpt import stream_sdk, learning
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa


class SyntheticTransport:
    def __init__(self):
        self.key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        self.nonce=''

    def request(self, method, url, **kwargs):
        if url == JWKS:
            return {'keys':[json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))|{'kid':'synthetic','alg':'RS256'}]}
        if url == TOKEN:
            claims=dict(iss=ISSUER,aud='oaiapp_browser',sub='synthetic-browser-user',nonce=self.nonce,exp=int(time.time())+300,iat=int(time.time()))
            return dict(id_token=jwt.encode(claims,self.key,algorithm='RS256',headers={'kid':'synthetic'}),access_token='SYNTHETIC_BROWSER_ACCESS',refresh_token='SYNTHETIC_BROWSER_REFRESH',expires_in=3600,token_type='Bearer',scope='openid resource.invoke '+DIRECT)
        if url == RESOURCE+'/models':
            return {'models':[dict(slug='synthetic-model',display_name='Synthetic model',visibility='list')]}
        if url == DISCOVERY:
            return {'issuer':ISSUER,'revocation_endpoint':ISSUER+'/api/accounts/oauth/revoke'}
        if url.endswith('/revoke'):return {}
        raise AssertionError('Unknown synthetic endpoint')


class BrowserAuth(ChatGPTAuth):
    def start(self):
        url=super().start()
        self.transport.nonce=parse_qs(urlsplit(url).query)['nonce'][0]
        return url


if __name__=='__main__':
    base=ROOT/'.cache/chatgpt-browser';base.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as temporary:
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No outbound network')):
            auth=BrowserAuth(Path(temporary)/'registration.json','http://127.0.0.1:8768/auth/callback',transport=SyntheticTransport())
            def plan(token,model):
                from types import SimpleNamespace
                providers=[]
                def parse(**kwargs):
                    text=kwargs['input'][-1]['content']
                    sdk=stream_sdk(learning(reply='Synthetic response to: '+text),
                                   terminal='disconnected' if text=='__interrupted__' else 'completed')
                    provider=ChatGPTProvider(token,model,sdk=sdk)
                    providers.append(provider)
                    return provider.parse(**kwargs)
                return SimpleNamespace(responses=SimpleNamespace(parse=parse),
                    close=lambda:[provider.close() for provider in providers])
            def forbid_api():raise AssertionError('No API billing fallback')
            app=create_app(data_path=Path(temporary)/'state.sqlite3',access_token='synthetic-local-unlock-not-a-real-secret',enabled=True,signin_enabled=True,chatgpt_auth=auth,plan_factory=plan,client_factory=forbid_api,max_calls=8,port=8768,plan_model='synthetic-model')
            app.run(host='127.0.0.1',port=8768,debug=False,use_reloader=False,load_dotenv=False)
