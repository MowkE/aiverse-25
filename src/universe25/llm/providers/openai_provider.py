"""OpenAI adapter (real HTTP via httpx; guarded; never exercised by tests).

Uses the chat-completions endpoint with response_format json_schema (strict).
Every call path passes through the BudgetGuard, exactly as the Anthropic
adapter. Pricing entries for OpenAI models in pricing.PRICES are placeholders
and must be verified before real use.
"""

from __future__ import annotations

import os
import time

from ..budget import BudgetGuard, BudgetNotConfirmedError
from .base import LLMRequest, LLMResponse, MissingAPIKeyError

_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    name = "openai"
    is_real = True

    def __init__(self, guard: BudgetGuard | None, api_key: str | None = None):
        if guard is None:
            raise BudgetNotConfirmedError(
                "OpenAIProvider requires a BudgetGuard; refusing to construct"
            )
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise MissingAPIKeyError(
                "OPENAI_API_KEY is not set; real OpenAI calls are impossible"
            )
        self.guard = guard
        self._key = key
        import httpx

        self._client = httpx.Client(timeout=120.0)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.guard.precall()

        body: dict = {
            "model": request.model,
            "max_completion_tokens": request.max_tokens,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": request.schema_name,
                    "schema": request.api_schema,
                    "strict": True,
                },
            },
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature

        start = time.perf_counter()
        resp = self._client.post(
            _API_URL,
            headers={
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        latency_ms = (time.perf_counter() - start) * 1000.0
        resp.raise_for_status()
        payload = resp.json()

        text = payload["choices"][0]["message"].get("content") or ""
        usage = payload.get("usage", {})
        in_tok = int(usage.get("prompt_tokens", 0))
        out_tok = int(usage.get("completion_tokens", 0))
        self.guard.charge(in_tok, out_tok)
        return LLMResponse(
            text=text,
            model=str(payload.get("model", request.model)),
            provider=self.name,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            request_id=resp.headers.get("x-request-id"),
            raw=payload,
        )
