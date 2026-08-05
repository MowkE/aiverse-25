"""Agent traits and behavioral rules (SPEC §5).

Behavioral code is treatment-blind: nothing here may branch on the treatment
cell. Treatments reach agents only through environment state (budgets, realized
influence, observed reciprocity). The single exception, the survival-attention
term, responds to whether material stakes bind (an environment fact), and is
the named H4 mechanism carrier (DECISIONS D4).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import BehaviorConfig


@dataclass(frozen=True)
class Traits:
    coop: np.ndarray
    status: np.ndarray
    explore: np.ndarray
    recip_sens: np.ndarray
    withdraw_threshold: np.ndarray
    pref_type: np.ndarray


def draw_traits(rng: np.random.Generator, n_agents: int) -> Traits:
    """Drawn before treatment assignment, from the dedicated traits stream."""
    return Traits(
        coop=rng.uniform(0.2, 0.9, n_agents),
        status=rng.uniform(0.1, 0.9, n_agents),
        explore=rng.uniform(0.1, 0.9, n_agents),
        recip_sens=rng.uniform(0.2, 0.8, n_agents),
        withdraw_threshold=rng.uniform(0.15, 0.45, n_agents),
        pref_type=rng.integers(0, 3, n_agents),
    )


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + np.exp(-z))


def participation_probability(
    cfg: BehaviorConfig,
    traits: Traits,
    i: int,
    efficacy: float,
    withdrawn: bool,
    recip: float,
    stakes_bind: bool,
) -> float:
    if cfg.policy == "random":
        return cfg.random_participation_p
    efficacy_sensitivity = 0.0 if cfg.policy == "material_only" else cfg.efficacy_sensitivity
    z = (
        cfg.alpha
        + efficacy_sensitivity * (efficacy - 0.5)
        + cfg.coop_weight * (traits.coop[i] - 0.5)
        + cfg.explore_weight * (traits.explore[i] - 0.5)
        + cfg.recip_weight * (recip - 0.5)
        + (cfg.survival_attention_bonus if stakes_bind else 0.0)
    )
    if withdrawn and cfg.policy == "heterogeneous":
        z += cfg.withdrawn_penalty
    return float(_sigmoid(z))


def choose_proposal_type(
    cfg: BehaviorConfig, traits: Traits, i: int, rng: np.random.Generator
) -> int:
    if cfg.policy == "random":
        return int(rng.integers(0, 3))
    if rng.random() < 0.5 * traits.explore[i]:
        return int(rng.integers(0, 3))
    return int(traits.pref_type[i])


def contribution_fraction(
    cfg: BehaviorConfig,
    traits: Traits,
    i: int,
    withdrawn: bool,
    recip: float,
    rng: np.random.Generator,
) -> float:
    if cfg.policy == "random":
        return float(rng.uniform(0.0, 1.0))
    eta = (
        traits.coop[i]
        + traits.recip_sens[i] * (recip - 0.5)
        + rng.normal(0.0, cfg.contribution_noise)
    )
    if withdrawn and cfg.policy == "heterogeneous":
        eta -= 0.5
    return float(np.clip(eta, 0.0, 1.0))


def update_efficacy(cfg: BehaviorConfig, efficacy: float, impact: float, participated: bool) -> float:
    if impact > 0:
        return efficacy + cfg.lambda_up * (1.0 - efficacy)
    if participated:
        return efficacy * (1.0 - cfg.lambda_down)
    return efficacy * (1.0 - cfg.lambda_idle)
