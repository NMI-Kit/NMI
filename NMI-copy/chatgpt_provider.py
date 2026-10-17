"""Bridge ask_ai's parse contract to official ChatGPT-plan structured streaming."""
import time
from types import SimpleNamespace

import httpx2 as httpx
from openai import OpenAI

from ai_test import InvalidAIResponse
from chatgpt_auth import RESOURCE


class PlanError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def error_code(code):
    return {
        "subscription_sharing_usage_limit_exceeded": "plan_limit",
        "subscription_sharing_usage_unavailable": "plan_unavailable",
        "subscription_sharing_user_unavailable": "plan_unavailable",
        "subscription_sharing_user_not_eligible": "plan_eligibility",
        "subscription_sharing_unsupported_capability": "model",
        "subscription_sharing_route_not_supported": "plan_eligibility",
        "chatpass_v2_scope_not_authorized": "consent",
        "chatpass_v2_invalid_authorization_context": "consent",
        "subscription_sharing_invalid_user": "signin",
    }.get(code, "plan_unavailable")


class ChatGPTProvider:
    def __init__(self, token, model, *, sdk=None, clock=time.monotonic):
        self.model, self.clock = model, clock
        self.sdk = sdk or OpenAI(api_key=token, base_url=RESOURCE, max_retries=0, timeout=35,
                                http_client=httpx.Client(trust_env=False, timeout=35))
        self.responses = self

    def parse(self, *, model, instructions, input, text_format, **options):
        if model != self.model or not isinstance(input, list):
            raise PlanError("model")
        # Explicit allowlist: max_output_tokens and other API-only options never reach this route.
        started, size, completed = self.clock(), 0, False
        try:
            with self.sdk.responses.stream(model=model, instructions=instructions, input=input,
                    text_format=text_format, store=False) as stream:
                # SDK stream() sets stream=true in the actual HTTP body.
                for event in stream:
                    if self.clock() - started > 90:
                        raise TimeoutError()
                    if event.type == "response.output_text.delta":
                        size += len(event.delta)
                        if size > 32000:
                            raise InvalidAIResponse()
                    elif event.type == "response.failed":
                        detail = getattr(event.response, "error", None)
                        raise PlanError(error_code(getattr(detail, "code", None)))
                    elif event.type in {"response.incomplete", "response.refusal.delta", "response.refusal.done"}:
                        raise InvalidAIResponse()
                    elif event.type == "error":
                        raise PlanError(error_code(getattr(event, "code", None)))
                    elif event.type == "response.completed":
                        completed = True
                if not completed:
                    raise InvalidAIResponse()
                final = stream.get_final_response()
                if final.status != "completed" or final.output_parsed is None:
                    raise InvalidAIResponse()
                # Existing ask_ai revalidates the result and all assessment fields.
                return SimpleNamespace(status="completed", output_parsed=final.output_parsed)
        except (InvalidAIResponse, PlanError, TimeoutError):
            raise
        except Exception as error:
            from openai import APIStatusError, APITimeoutError
            from pydantic import ValidationError
            if isinstance(error, APITimeoutError):
                raise TimeoutError() from None
            if isinstance(error, ValidationError):
                raise InvalidAIResponse() from None
            if isinstance(error, APIStatusError):
                body = error.body if isinstance(error.body, dict) else {}
                detail = body.get("error", body)
                code = detail.get("code") if isinstance(detail, dict) else None
                mapped = error_code(code)
                if not code:
                    mapped = {401: "signin", 403: "plan_eligibility", 400: "model",
                              404: "model", 429: "plan_limit"}.get(error.status_code, mapped)
                raise PlanError(mapped) from None
            raise PlanError("plan_unavailable") from None

    def close(self):
        self.sdk.close()
