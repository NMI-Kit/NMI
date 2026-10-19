"""Official Claude Messages adapter; no credential access or network on import."""
import asyncio
import json
import logging
import os
import re
from types import SimpleNamespace

import anthropic
import httpx2 as httpx
from pydantic import ValidationError

from ai_test import InvalidAIResponse
from learning_result import LearningResult, has_reply_text

ENDPOINT = 'https://api.anthropic.com'
EFFORTS = ('low', 'medium', 'high')
USAGE_FIELDS = ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')


class ClaudeError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def valid_model(model):
    return isinstance(model, str) and re.fullmatch(r'claude-[a-z0-9][a-z0-9.-]{1,90}', model) is not None


def sdk_client():
    # Called only by the server after explicit inference approval, or by the
    # owner's explicit non-inference model-check command. Never print the value.
    for name in ('anthropic', 'anthropic._base_client', 'httpx2', 'httpcore2'):
        logging.getLogger(name).disabled = True
    key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if not key:
        raise ClaudeError('claude_key')
    if 'ANTHROPIC_CUSTOM_HEADERS' in os.environ or 'ANTHROPIC_AUTH_TOKEN' in os.environ:
        raise ClaudeError('claude_request')
    timeout = httpx.Timeout(30, connect=5, write=10, pool=5)
    return anthropic.AsyncAnthropic(api_key=key, auth_token=None, webhook_key='', base_url=ENDPOINT,
        max_retries=0, timeout=timeout, open_telemetry=False,
        http_client=httpx.AsyncClient(trust_env=False, follow_redirects=False, timeout=timeout))


def safe_error(error):
    if isinstance(error, (TimeoutError, anthropic.APITimeoutError)):
        return ClaudeError('timeout')
    if isinstance(error, anthropic.APIStatusError):
        code = {400: 'claude_request', 401: 'claude_key', 402: 'claude_credit',
                403: 'claude_access', 404: 'claude_model', 429: 'claude_limit',
                529: 'claude_unavailable'}.get(error.status_code, 'claude_unavailable')
        # Only inspect the error type for classification. Never propagate its text.
        detail = error.body if isinstance(error.body, dict) else {}
        detail = detail.get('error', detail)
        if isinstance(detail, dict) and detail.get('type') == 'billing_error':
            code = 'claude_credit'
        return ClaudeError(code)
    return ClaudeError('claude_unavailable')


async def verify_model(sdk, model):
    info = await sdk.models.retrieve(model)
    support = getattr(getattr(info, 'capabilities', None), 'structured_outputs', None)
    if (info.id != model or getattr(info, 'lifecycle', None) == 'retired'
            or getattr(support, 'supported', None) is not True):
        raise ClaudeError('claude_model')
    return info


def system_blocks(instructions, cache_prefix):
    """Split the system prompt into a cached stable block and an uncached variable block.

    `cache_prefix` must be the exact start of `instructions` followed by a blank line; otherwise
    the prompt is sent as one plain string with no caching.
    """
    head = cache_prefix + '\n\n' if isinstance(cache_prefix, str) and cache_prefix else None
    if head is None or not instructions.startswith(head) or not instructions[len(head):].strip():
        return instructions
    return [{'type': 'text', 'text': cache_prefix, 'cache_control': {'type': 'ephemeral'}},
            {'type': 'text', 'text': instructions[len(head):]}]


class ClaudeProvider:
    """Adapt ask_ai.responses.parse while retaining NMI's result/storage contracts."""
    def __init__(self, model, *, sdk_factory=sdk_client, deadline=90, max_tokens=1800, effort=None):
        if not valid_model(model):
            raise ClaudeError('claude_model')
        # Reasoning effort: NMI_CLAUDE_EFFORT (owner-set), default low. An unknown value stops before any request.
        self.effort = (effort or os.environ.get('NMI_CLAUDE_EFFORT') or 'low').strip().lower()
        if self.effort not in EFFORTS:
            raise ClaudeError('claude_request')
        if not 0 < deadline <= 90 or type(max_tokens) is not int or not 256 <= max_tokens <= 4096:
            raise ValueError('Invalid Claude request limits')
        self.model, self.sdk_factory = model, sdk_factory
        self.deadline, self.max_tokens = deadline, max_tokens
        self.responses, self.usage = self, None

    def capture_usage(self, value, *, complete=False):
        self.usage = {'provider': 'claude', 'complete': complete}
        for field in USAGE_FIELDS:
            number = getattr(value, field, None)
            self.usage[field] = number if type(number) is int and number >= 0 else None

    def parse(self, *, model, instructions, input, text_format, cache_prefix=None, **options):
        if model != self.model or text_format is not LearningResult or not isinstance(input, list):
            raise ClaudeError('claude_request')
        self.usage = None
        try:
            return asyncio.run(self._parse(system_blocks(instructions, cache_prefix), input))
        except (ClaudeError, InvalidAIResponse):
            raise
        except (ValidationError, json.JSONDecodeError):
            raise InvalidAIResponse() from None
        except Exception as error:
            raise safe_error(error) from None

    async def _parse(self, system, messages):
        # A cancellation deadline covers model lookup, headers and the entire
        # stream, including a slow/trickling response. No background retry thread.
        async with asyncio.timeout(self.deadline):
            async with self.sdk_factory() as sdk:
                await verify_model(sdk, self.model)
                settings = {}
                if self.model == 'claude-sonnet-5-5':
                    settings = {'thinking': {'type': 'between_tools'}, 'output_config': {'effort': self.effort}}
                async with sdk.messages.stream(model=self.model, system=system,
                        messages=messages, max_tokens=self.max_tokens, output_format=LearningResult,
                        **settings) as stream:
                    stopped, size = False, 0
                    async for event in stream:
                        if event.type == 'message_start':
                            self.capture_usage(event.message.usage)
                        elif event.type == 'message_delta':
                            self.capture_usage(stream.current_message_snapshot.usage)
                        elif event.type == 'content_block_delta':
                            delta = getattr(event.delta, 'text', '') or getattr(event.delta, 'thinking', '')
                            size += len(delta)
                            if size > 32000:
                                raise InvalidAIResponse()
                        elif event.type == 'message_stop':
                            stopped = True
                        elif event.type == 'error':
                            raise ClaudeError('claude_unavailable')
                    if not stopped:
                        raise InvalidAIResponse()
                    final = await stream.get_final_message()
                    self.capture_usage(final.usage, complete=True)
                    if final.stop_reason != 'end_turn' or final.parsed_output is None:
                        raise InvalidAIResponse()
                    blocks = [block for block in final.content if block.type == 'text']
                    if len(blocks) != 1:
                        raise InvalidAIResponse()
                    raw = json.loads(blocks[0].text)
                    if (not isinstance(raw, dict) or type(raw.get('is_attempt')) is not bool
                            or not has_reply_text(raw)):
                        raise InvalidAIResponse()
                    result = LearningResult.model_validate(raw)
                    return SimpleNamespace(status='completed', output_parsed=result)

    def close(self):
        # Async context managers close both stream and client before parse returns.
        pass


def check_model(model, *, sdk_factory=sdk_client):
    """Explicit owner-only metadata request. Never invokes the Messages API."""
    if not valid_model(model):
        raise ClaudeError('claude_model')
    async def check():
        async with asyncio.timeout(20):
            async with sdk_factory() as sdk:
                info = await verify_model(sdk, model)
                return {'model': info.id, 'structured_outputs': True}
    try:
        return asyncio.run(check())
    except ClaudeError:
        raise
    except Exception as error:
        raise safe_error(error) from None
