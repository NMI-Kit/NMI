"""Isolated browser fixture: SDK parsing is real, every Claude HTTP reply is mocked."""
from pathlib import Path
import json
import socket
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from claude_provider import ClaudeProvider
from claude_fixtures import SyntheticClaude, MODEL, learning, local_connect, TEST_ENV
from local_web import create_app
import ai_test


def provider(model):
    fixture=SyntheticClaude(delay=.3)
    async def handle(request):
        if request.method=='POST':
            body=json.loads(request.content)
            text=body['messages'][-1]['content']
            fixture.value=learning(reply='Synthetic Claude reply: '+text)
            if text=='__interrupted__': fixture.terminal='disconnected'
            if text=='__unauthorized__': fixture.status=401
        return await original(request)
    original=fixture.handle
    fixture.handle=handle
    return ClaudeProvider(model,sdk_factory=fixture.client)


def forbidden(*args,**kwargs): raise AssertionError('Non-Claude provider or shared JSON forbidden')


if __name__=='__main__':
    from contextlib import ExitStack
    base=ROOT/'.cache/claude-browser';base.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as temporary, ExitStack() as stack:
        stack.enter_context(patch.dict('os.environ',TEST_ENV,clear=True))
        stack.enter_context(patch.object(socket.socket,'connect',local_connect))
        for name in ('load_history','load_progress','save_history','record_attempt'):
            stack.enter_context(patch.object(ai_test,name,side_effect=forbidden))
        app=create_app(data_path=Path(temporary)/'synthetic.sqlite3',access_token='synthetic-local-unlock-not-a-real-secret',
            provider='claude',claude_model=MODEL,claude_factory=provider,enabled=True,allow_claude=True,
            allow_api=False,signin_enabled=False,client_factory=forbidden,plan_factory=forbidden,max_calls=10,port=8771)
        app.run(host='127.0.0.1',port=8771,debug=False,use_reloader=False,load_dotenv=False)
