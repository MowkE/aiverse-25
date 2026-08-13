"""Configuration for Study 2 LLM runs (TOML, mirroring universe25.config)."""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..config import EconomyConfig, ShockConfig

PROVIDERS = ("mock", "anthropic", "openai", "claude-cli")
PHASES = ("public", "decision", "contribution", "report")
REPORT_MODES = ("none", "last", "all")
THINKING_MODES = ("disabled", "adaptive")


@dataclass(frozen=True)
class LLMRunConfig:
    n_agents: int = 8
    n_rounds: int = 40
    provider: str = "mock"
    # Model id from pricing.PRICES; candidate ids recorded in docs/LLM_DESIGN.md.
    model: str = "claude-sonnet-5"
    temperature: float | None = None  # None = omit (current Anthropic models reject it)
    effort: str = "medium"
    thinking: str = "disabled"
    template_version: str = "llm-t1"
    max_schema_retries: int = 2  # retries after the first attempt
    max_tokens: int = 400
    memory_window: int = 6
    message_max_chars: int = 240
    report_rounds: str = "last"
    economy: EconomyConfig = field(default_factory=EconomyConfig)
    shock: ShockConfig = field(default_factory=ShockConfig)


@dataclass(frozen=True)
class LLMBatchConfig:
    master_seed: int = 20260805
    n_pairs: int = 1
    output_dir: str = "outputs/llm_smoke"
    cache_dir: str = ""  # default: <output_dir>/llm_cache
    run: LLMRunConfig = field(default_factory=LLMRunConfig)

    def resolved_cache_dir(self) -> str:
        return self.cache_dir or str(Path(self.output_dir) / "llm_cache")


def load_llm_batch_config(path: str | Path) -> LLMBatchConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    run_raw = raw.pop("run", {})
    economy = EconomyConfig(**run_raw.pop("economy", {}))
    shock = ShockConfig(**run_raw.pop("shock", {}))
    run = LLMRunConfig(economy=economy, shock=shock, **run_raw)
    if run.provider not in PROVIDERS:
        raise ValueError(f"unknown provider {run.provider!r}; expected one of {PROVIDERS}")
    if run.report_rounds not in REPORT_MODES:
        raise ValueError(f"report_rounds {run.report_rounds!r} not in {REPORT_MODES}")
    if run.thinking not in THINKING_MODES:
        raise ValueError(f"thinking {run.thinking!r} not in {THINKING_MODES}")
    return LLMBatchConfig(run=run, **raw)


def llm_config_to_dict(cfg: LLMBatchConfig) -> dict:
    return asdict(cfg)
