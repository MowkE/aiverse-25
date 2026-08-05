"""Configuration dataclasses and TOML loading (see docs/DECISIONS.md D8)."""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

RESOURCE_LEVELS = ("constrained", "abundant")
ACCESS_LEVELS = ("concentrated", "broad")
CELLS = tuple((r, a) for r in RESOURCE_LEVELS for a in ACCESS_LEVELS)

POLICIES = ("heterogeneous", "random", "material_only")


@dataclass(frozen=True)
class EconomyConfig:
    # Constrained endowment is calibrated so that expected income (endowment +
    # public-good payout) roughly matches expected spend: balances hover near
    # zero, material stakes keep binding, and survival occasionally fails.
    survival_cost: float = 2.0
    endow_lo: float = 0.8
    endow_hi: float = 2.4
    abundant_endowment: float = 1000.0
    participation_cost: float = 0.25
    contribution_cap: float = 2.0
    m_base: float = 1.0
    m_coord: float = 1.5


@dataclass(frozen=True)
class BehaviorConfig:
    policy: str = "heterogeneous"
    alpha: float = 0.4
    efficacy_sensitivity: float = 2.5
    coop_weight: float = 1.0
    explore_weight: float = 0.6
    recip_weight: float = 0.8
    # DECISIONS D4 (pilot-revised): the H4 mechanism is material crowding-out —
    # constrained agents sometimes cannot afford public participation, the direct
    # analogue of survival tasks competing with social life in Universe 25. This
    # optional psychological bonus (+participation when stakes bind) turned out to
    # work AGAINST that channel in the pilot, so the Calhoun-faithful default is 0.
    survival_attention_bonus: float = 0.0
    withdrawn_penalty: float = -2.5
    lambda_up: float = 0.5
    lambda_down: float = 0.08
    lambda_idle: float = 0.02
    withdraw_patience: int = 3
    contribution_noise: float = 0.08
    random_participation_p: float = 0.5


@dataclass(frozen=True)
class ShockConfig:
    enabled: bool = True
    duration: int = 3
    multiplier_factor: float = 0.5


DECIDER_RULES = ("self", "modal")


@dataclass(frozen=True)
class RunConfig:
    n_agents: int = 8
    n_rounds: int = 40
    # Institution rule, not agent behavior: how the decider selects among
    # submitted proposals (DECISIONS D5). "self" = own proposal first;
    # "modal" = most common proposal type (benevolent variant).
    decider_rule: str = "self"
    economy: EconomyConfig = field(default_factory=EconomyConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    shock: ShockConfig = field(default_factory=ShockConfig)


@dataclass(frozen=True)
class BatchConfig:
    master_seed: int = 20260805
    n_pairs: int = 30
    output_dir: str = "outputs/batch"
    run: RunConfig = field(default_factory=RunConfig)


def _build(cls, data: dict):
    return cls(**data)


def load_batch_config(path: str | Path) -> BatchConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)
    run_raw = raw.pop("run", {})
    economy = _build(EconomyConfig, run_raw.pop("economy", {}))
    behavior = _build(BehaviorConfig, run_raw.pop("behavior", {}))
    shock = _build(ShockConfig, run_raw.pop("shock", {}))
    if behavior.policy not in POLICIES:
        raise ValueError(f"unknown policy {behavior.policy!r}; expected one of {POLICIES}")
    run = RunConfig(economy=economy, behavior=behavior, shock=shock, **run_raw)
    if run.decider_rule not in DECIDER_RULES:
        raise ValueError(f"unknown decider_rule {run.decider_rule!r}; expected one of {DECIDER_RULES}")
    return BatchConfig(run=run, **raw)


def config_to_dict(cfg: BatchConfig) -> dict:
    return asdict(cfg)


def with_policy(cfg: RunConfig, policy: str) -> RunConfig:
    return replace(cfg, behavior=replace(cfg.behavior, policy=policy))
