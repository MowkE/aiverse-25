"""Provider-agnostic request/response types and the Provider protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


class MissingAPIKeyError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMRequest:
    system: str
    user: str
    schema_name: str
    api_schema: dict
    model: str
    max_tokens: int = 400
    temperature: float | None = None
    effort: str | None = None
    thinking: str = "disabled"
    seed: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    request_id: str | None = None
    raw: Any = None


@runtime_checkable
class Provider(Protocol):
    name: str
    is_real: bool

    def complete(self, request: LLMRequest) -> LLMResponse: ...
