"""Test-only server: deterministic fake provider; outbound networking forbidden."""
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from local_web import create_app


def reply(**kwargs):
    text = kwargs['input'][-1]['content']
    if text == '__timeout__':
        raise TimeoutError('SYNTHETIC_PRIVATE_PROVIDER_DETAIL')
    ar = 'Preferred language: ar' in kwargs['instructions']
    result = dict(reply=('لنفكّر معًا. ما ناتج 2 + 2؟' if ar else 'Let us think together. What is 2 + 2?'),
                  is_attempt=False, subject=None, topic=None, skill=None, correct=None, hint_used=None, mistake_type=None)
    if text == '4':
        result.update(reply='Synthetic correct answer.', is_attempt=True, subject='mathematics',topic='arithmetic',skill='addition',correct=True,hint_used=False)
    if text == 'Show safe text':
        result['reply']='<img src=x onerror=alert(1)> Synthetic inert reply'
    return SimpleNamespace(output_parsed=result,status='completed')


if __name__=='__main__':
    base = ROOT / '.cache/local-browser'
    base.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as temporary:
        with patch.object(socket.socket,'connect',side_effect=AssertionError('Outbound network forbidden')):
            app=create_app(data_path=Path(temporary)/'browser.sqlite3',access_token='synthetic-local-unlock-not-a-real-secret',
                           enabled=True,model='mock-only',max_calls=20,port=8767,allow_api=True,
                           client_factory=lambda:SimpleNamespace(responses=SimpleNamespace(parse=reply),close=lambda:None))
            app.run(host='127.0.0.1',port=8767,debug=False,use_reloader=False,load_dotenv=False)
