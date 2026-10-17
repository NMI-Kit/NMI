"""Private-launch regressions: temporary data, no OAuth or AI network access."""
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from local_web import create_app

ORIGIN = 'http://127.0.0.1:8766'
TOKEN = 'synthetic-local-unlock-not-a-real-secret'


class UnlockTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / '.cache/local-tests'
        base.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name)
        guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('Offline only'))
        guard.start(); self.addCleanup(guard.stop)
        self.factory = Mock(side_effect=AssertionError('Inference forbidden'))
        self.app = self.make_app()
        self.client = self.app.test_client()

    def make_app(self, **kw):
        return create_app(**(dict(data_path=self.path/'state.sqlite3', access_token=TOKEN,
                          signin_enabled=True, enabled=False, client_factory=self.factory) | kw))

    def claim(self, client=None, token=TOKEN):
        (client or self.client).get('/api/session/preflight', base_url=ORIGIN)
        return (client or self.client).post('/api/session', json={'token':token},
                                           base_url=ORIGIN, headers={'Origin':ORIGIN})

    def test_launch_flags_and_signin_ready_without_profile(self):
        html = self.client.get('/', base_url=ORIGIN).get_data(as_text=True)
        self.assertIn('name="nmi-chatgpt-signin" content="1"', html)
        self.assertIn('name="nmi-inference" content="0"', html)
        self.assertNotIn(TOKEN, html)
        self.assertEqual(self.claim().status_code, 200)
        state = self.client.get('/api/state', base_url=ORIGIN).json
        self.assertTrue(state['signin_enabled']); self.assertFalse(state['enabled'])
        self.assertEqual(state['provider'], 'chatgpt')
        self.assertIsNone(state['profile']); self.assertEqual(state['history'], [])
        self.assertEqual(state['attempts'], [])
        self.factory.assert_not_called()

    def test_bad_links_and_other_browser_still_denied(self):
        for value in ('short', 'ع'*32, 'x'*101, 'wrong-but-valid-length-token', None, []):
            self.assertEqual(self.claim(token=value).status_code, 403)
        self.assertEqual(self.claim().status_code, 200)
        self.assertEqual(self.claim().status_code, 200)
        self.assertEqual(self.claim(self.app.test_client()).status_code, 403)

    def test_ports_have_separate_cookies(self):
        self.claim()
        other = self.make_app(port=8767, data_path=self.path/'other.sqlite3')
        other_name = other.config['SESSION_COOKIE_NAME']
        self.assertNotEqual(self.app.config['SESSION_COOKIE_NAME'], other_name)
        self.client.set_cookie(other_name, 'other-port-cookie', domain='127.0.0.1')
        self.client.set_cookie('nmi_local_session', 'legacy-cookie', domain='127.0.0.1')
        self.assertEqual(self.client.get('/api/state', base_url=ORIGIN).status_code, 200)

    def test_restart_requires_new_link_and_replaces_stale_cookie(self):
        self.claim()
        cookie = self.client.get_cookie(self.app.config['SESSION_COOKIE_NAME'], domain='127.0.0.1')
        self.app = self.make_app(access_token='new-synthetic-launch-capability')
        self.client = self.app.test_client()
        self.client.set_cookie(self.app.config['SESSION_COOKIE_NAME'], cookie.value, domain='127.0.0.1')
        self.assertEqual(self.client.get('/api/state', base_url=ORIGIN).status_code, 401)
        self.assertEqual(self.claim().status_code, 403)
        self.assertEqual(self.claim(token='new-synthetic-launch-capability').status_code, 200)
        self.assertEqual(self.client.get('/api/state', base_url=ORIGIN).status_code, 200)

    def test_api_default_retained_without_signin(self):
        self.app = self.make_app(signin_enabled=False)
        self.client = self.app.test_client(); self.claim()
        self.assertEqual(self.client.get('/api/state', base_url=ORIGIN).json['provider'], 'api')

    def test_signin_enabled_does_not_enable_inference(self):
        csrf = self.claim().json['csrf']
        headers = {'Origin':ORIGIN, 'X-NMI-CSRF':csrf}
        self.client.post('/api/profile', json={'country':'US','grade':10}, base_url=ORIGIN, headers=headers)
        body = dict(request_id=str(uuid4()), message='Synthetic question', language='en', intent='question', provider='chatgpt')
        with patch.object(self.app.extensions['nmi_chatgpt'], 'load_models', side_effect=AssertionError('No model request')):
            response = self.client.post('/api/chat', json=body, base_url=ORIGIN, headers=headers)
        self.assertEqual(response.json['error'], 'locked')
        state = self.client.get('/api/state', base_url=ORIGIN).json
        self.assertEqual(state['history'], []); self.assertEqual(state['attempts'], [])
        self.factory.assert_not_called()
