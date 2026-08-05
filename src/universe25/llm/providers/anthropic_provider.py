"""Anthropic adapter (real HTTP; guarded; never exercised by tests).

Follows current Claude API guidance (claude-api skill, 2026-08): structured
outputs via output_config.format json_schema; thinking disabled or adaptive via
the thinking parameter; sampling parameters are not sent unless explicitly
configured (current models reject them with a 400). Every call path passes
through the BudgetGuard — construction without a guard, or a call with an
unarmed guard, raises before any HTTP request is built.
"""

from __future__ import annotations

import os
import time

from ..budget import BudgetGuard, BudgetNotConfirmedError
from .base import LLMRequest, LLMResponse, MissingAPIKeyError


class AnthropicProvider:
    name = "anthropic"
    is_real = True

    def __init__(self, guard: BudgetGuard | None, api_key: str | None = None):
        if guard is None:
            raise BudgetNotConfirmedError(
                "AnthropicProvider requires a BudgetGuard; refusing to construct"
            )
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise MissingAPIKeyError(
                "ANTHROPIC_API_KEY is not set; real Anthropic calls are impossible"
            )
        self.guard = guard
        # Imported lazily so the mock-only paths never require the SDK at runtime.
        import anthropic

        self._client = anthropic.Anthropic(api_key=key)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.guard.precall()

        output_config: dict = {
            "format": {"type": "json_schema", "schema": request.api_schema},
        }
        if request.effort:
            output_config["effort"] = request.effort

        kwargs: dict = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.user}],
            "output_config": output_config,
        }
        if request.thinking == "disabled":
            kwargs["thinking"] = {"type": "disabled"}
        elif request.thinking == "adaptive":
            kwargs["thinking"] = {"type": "adaptive"}
        if request.temperature is not None:
            # Rejected (400) on current Anthropic models; passed through only if
            # explicitly configured for an older model.
            kwargs["temperature"] = request.temperature

        start = time.perf_counter()
        response = self._client.messages.create(**kwargs)
        latency_ms = (time.perf_counter() - start) * 1000.0

        if response.stop_reason == "refusal":
            text = ""
        else:
            text = next((b.text for b in response.content if b.type == "text"), "")
        in_tok = int(response.usage.input_tokens)
        out_tok = int(response.usage.output_tokens)
        self.guard.charge(in_tok, out_tok)
        return LLMResponse(
            text=text,
            model=response.model,
            provider=self.name,
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency_ms,
            request_id=getattr(response, "_request_id", None),
            raw=response,
        )
