"""Pricing table and token estimation for the cost estimator / budget guard.

PRICES is the single editable source of truth for per-model dollar rates.

Prices as of 2026-08-05, taken from the claude-api skill's model table (cache
date 2026-06-24) — re-verify at https://platform.claude.com/docs/en/pricing
before spending real credits. Claude Sonnet 5 has introductory pricing
($2/$10 per MTok) through 2026-08-31; the standard rate ($3/$15) is recorded
here so estimates are conservative. OpenAI rows are placeholders and MUST be
verified before any real OpenAI run.
"""

from __future__ import annotations

from dataclasses import dataclass

# model id -> (usd per 1M input tokens, usd per 1M output tokens)
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5": (3.00, 15.00),  # intro $2/$10 through 2026-08-31
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-fable-5": (10.00, 50.00),
    # OpenAI prices verified 2026-08-13 against developers.openai.com/api/docs/pricing.
    "gpt-5": (1.25, 10.00),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5.6-sol": (5.00, 30.00),
    "gpt-5.6-terra": (2.00, 12.00),
    "gpt-5.6-luna": (0.20, 1.20),
}

CANDIDATE_MODELS = ("claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5")

# Rough chars-per-token divisor for English prose + JSON (conservative).
CHARS_PER_TOKEN = 3.5

# Expected structured-output sizes per phase (tokens), including JSON overhead.
OUTPUT_TOKENS_BY_PHASE = {
    "public": 90,
    "decision": 25,
    "contribution": 25,
    "report": 45,
}

# Multiplier covering schema-retry re-asks and estimation slack.
RETRY_ALLOWANCE = 1.15


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / CHARS_PER_TOKEN) + 1)


def price_for(model: str) -> tuple[float, float]:
    if model not in PRICES:
        raise KeyError(
            f"model {model!r} has no pricing entry; add it to universe25.llm.pricing.PRICES"
        )
    return PRICES[model]


def cost_usd(model: str, input_tokens: float, output_tokens: float) -> float:
    p_in, p_out = price_for(model)
    return input_tokens * p_in / 1e6 + output_tokens * p_out / 1e6


@dataclass(frozen=True)
class PhaseEstimate:
    phase: str
    calls: int
    input_tokens_per_call: int
    output_tokens_per_call: int

    @property
    def input_tokens(self) -> int:
        return self.calls * self.input_tokens_per_call

    @property
    def output_tokens(self) -> int:
        return self.calls * self.output_tokens_per_call


@dataclass(frozen=True)
class RunEstimate:
    """Upper-bound per-run call/token estimate (all agents active every round)."""

    phases: tuple[PhaseEstimate, ...]

    @property
    def calls(self) -> int:
        return sum(p.calls for p in self.phases)

    @property
    def input_tokens(self) -> int:
        return int(sum(p.input_tokens for p in self.phases) * RETRY_ALLOWANCE)

    @property
    def output_tokens(self) -> int:
        return int(sum(p.output_tokens for p in self.phases) * RETRY_ALLOWANCE)

    def cost(self, model: str) -> float:
        return cost_usd(model, self.input_tokens, self.output_tokens)
