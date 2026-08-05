"""Deterministic, seedable mock provider used by all tests and smoke runs.

Responses are a pure function of (request.seed, request.schema_name) plus the
fault-injection counters, never of wall-clock or call order, so cache/resume
tests are byte-identical. Fault injection produces invalid outputs on demand
for retry/exhaustion contract tests.
"""

from __future__ import annotations

import json

import numpy as np

from ..pricing import estimate_tokens
from .base import LLMRequest, LLMResponse

_WORDS = (
    "let us pool a bit more this round",
    "i suggest we back option {p}",
    "keeping some reserve, but option {p} seems workable",
    "happy to follow the chair on this",
    "option {p} worked before, i will support it",
    "count me in for option {p}",
)


class MockProvider:
    name = "mock"
    is_real = False

    def __init__(
        self,
        participate_p: float = 0.65,
        adopt_p: float = 0.9,
        invalid_first_calls: int = 0,
        always_invalid: bool = False,
        raise_after_calls: int | None = None,
    ):
        self.participate_p = participate_p
        self.adopt_p = adopt_p
        self.invalid_first_calls = invalid_first_calls
        self.always_invalid = always_invalid
        self.raise_after_calls = raise_after_calls
        self.calls = 0

    def _payload(self, request: LLMRequest) -> dict:
        rng = np.random.default_rng(np.random.SeedSequence([request.seed & 0xFFFFFFFF]))
        if request.schema_name == "public_phase":
            proposal = int(rng.integers(0, 3))
            msg = _WORDS[int(rng.integers(0, len(_WORDS)))].format(p=proposal)
            return {
                "participate": bool(rng.random() < self.participate_p),
                "proposal_type": proposal,
                "public_message": msg,
            }
        if request.schema_name == "decision":
            n_sub = int(request.metadata.get("n_submissions", 1))
            if rng.random() < self.adopt_p and n_sub > 0:
                return {"adopt_index": int(rng.integers(0, n_sub))}
            return {"adopt_index": -1}
        if request.schema_name == "contribution":
            return {"contribution_fraction": float(np.round(rng.uniform(0.15, 0.95), 3))}
        if request.schema_name == "report":
            return {
                "confidence": float(np.round(rng.uniform(0.2, 0.95), 3)),
                "perceived_efficacy": float(np.round(rng.uniform(0.1, 0.9), 3)),
                "legitimacy_rating": float(np.round(rng.uniform(0.2, 0.95), 3)),
            }
        raise ValueError(f"unknown schema {request.schema_name!r}")

    def complete(self, request: LLMRequest) -> LLMResponse:
        if self.raise_after_calls is not None and self.calls >= self.raise_after_calls:
            raise ConnectionError("mock provider interrupted (raise_after_calls)")
        self.calls += 1
        if self.always_invalid or self.calls <= self.invalid_first_calls:
            text = "this is not the JSON you are looking for"
        else:
            text = json.dumps(self._payload(request), sort_keys=True)
        return LLMResponse(
            text=text,
            model=request.model,
            provider=self.name,
            input_tokens=estimate_tokens(request.system) + estimate_tokens(request.user),
            output_tokens=estimate_tokens(text),
            latency_ms=0.0,
            request_id=None,
            raw=None,
        )
