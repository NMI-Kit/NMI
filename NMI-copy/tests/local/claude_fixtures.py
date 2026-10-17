"""Synthetic HTTP/SSE fixtures exercise the installed SDK without networking."""
import asyncio
import json
import socket
import os
import anthropic
import httpx2 as httpx

MODEL = 'claude-sonnet-5-5'
TEST_ENV = {'SystemRoot': os.environ.get('SystemRoot', r'C:\Windows'),
            'ANTHROPIC_CONFIG_DIR': 'synthetic-unused-config-directory'}
_connect = socket.socket.connect


def local_connect(sock, address):
    # Windows asyncio creates a loopback socketpair for its internal wakeup pipe.
    if isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1'):
        return _connect(sock, address)
    raise AssertionError('No outbound network in Claude tests')


def learning(**values):
    return dict(reply='Synthetic Claude reply', is_attempt=False, subject=None,
                topic=None, skill=None, correct=None, hint_used=None, mistake_type=None) | values


def events(value, *, terminal='end_turn'):
    raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    messages = [
        ('message_start', {'message': dict(id='msg_synthetic', type='message', role='assistant',
            model=MODEL, content=[], stop_reason=None, stop_sequence=None,
            usage=dict(input_tokens=120, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0))}),
        ('content_block_start', {'index': 0, 'content_block': {'type': 'text', 'text': ''}}),
        ('content_block_delta', {'index': 0, 'delta': {'type': 'text_delta', 'text': raw}}),
        ('content_block_stop', {'index': 0}),
    ]
    if terminal != 'disconnected':
        messages += [('message_delta', {'delta': {'stop_reason': terminal, 'stop_sequence': None},
                                        'usage': {'output_tokens': 80}}), ('message_stop', {})]
    return ''.join('event: '+kind+'\ndata: '+json.dumps({'type': kind, **data}, ensure_ascii=False)+'\n\n'
                   for kind, data in messages)


class SyntheticClaude:
    def __init__(self, value=None, *, terminal='end_turn', status=200, delay=0, supported=True):
        self.value = learning() if value is None else value
        self.terminal, self.status, self.delay, self.supported = terminal, status, delay, supported
        self.calls = []

    async def handle(self, request):
        self.calls.append((request.method, request.url.path, json.loads(request.content) if request.content else None))
        if request.method == 'GET' and request.url.path == '/v1/models/'+MODEL:
            return httpx.Response(200, json=dict(id=MODEL, type='model', display_name='Synthetic Sonnet',
                created_at='2026-09-28T00:00:00Z', lifecycle='active',
                capabilities={'structured_outputs': {'supported': self.supported}}))
        if request.method != 'POST' or request.url.path != '/v1/messages':
            raise AssertionError('Unexpected synthetic endpoint')
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.status != 200:
            return httpx.Response(self.status, json={'type': 'error', 'error':
                {'type': 'api_error', 'message': 'SYNTHETIC_PRIVATE_ERROR'}})
        value = self.value(request) if callable(self.value) else self.value
        return httpx.Response(200, headers={'content-type': 'text/event-stream'},
                              content=events(value, terminal=self.terminal).encode())

    def client(self):
        return anthropic.AsyncAnthropic(api_key='synthetic-fixture-not-a-key', max_retries=0,
            base_url='https://api.anthropic.com', open_telemetry=False,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(self.handle), trust_env=False))

    @property
    def posts(self):
        return [body for method, _, body in self.calls if method == 'POST']


class SlowStream(httpx.AsyncByteStream):
    """Send a valid initial SSE event, then stall without completing the message."""
    closed = False

    async def __aiter__(self):
        yield events(learning()).split('\n\n',1)[0].encode()+b'\n\n'
        await asyncio.sleep(5)

    async def aclose(self): self.closed = True
