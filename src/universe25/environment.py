"""Round loop and treatment implementation (SPEC §4-5).

Treatments are implemented here and only here, as environment differences:
resources set the endowment process; role access sets the decider schedule.
Agents never observe treatment labels — material salience (`stakes_bind`) is
derived from the agent's own budget slack, not from the cell name.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import agents as ag
from .config import RunConfig
from .rng import PairStreams, spawn_pair_streams

EPS = 1e-9


@dataclass(frozen=True)
class RunResult:
    events: pd.DataFrame
    traits: pd.DataFrame


def run_id_for(pair: int, resources: str, access: str) -> str:
    return f"p{pair:04d}-{resources}-{access}"


def decider_schedule(
    access: str, n_agents: int, n_rounds: int, structure_rng: np.random.Generator
) -> np.ndarray:
    """Seat permutation drawn from the structure stream, shared across the
    cells of a pair so decider trait profiles are matched (DECISIONS D11)."""
    perm = structure_rng.permutation(n_agents)
    if access == "concentrated":
        return np.full(n_rounds, perm[0], dtype=int)
    return np.array([perm[t % n_agents] for t in range(n_rounds)], dtype=int)


def simulate_run(
    cfg: RunConfig,
    resources: str,
    access: str,
    pair: int,
    master_seed: int,
    streams: PairStreams | None = None,
) -> RunResult:
    if streams is None:
        streams = spawn_pair_streams(master_seed, pair)
    n, rounds = cfg.n_agents, cfg.n_rounds
    eco, beh = cfg.economy, cfg.behavior

    traits = ag.draw_traits(streams.traits, n)
    schedule = decider_schedule(access, n, rounds, streams.structure)
    rng = streams.dynamics

    balance = np.zeros(n)
    efficacy = np.full(n, 0.5)
    withdrawn = np.zeros(n, dtype=bool)
    low_e_streak = np.zeros(n, dtype=int)
    recip = 0.5

    shock_start = rounds // 2
    shock_end = shock_start + cfg.shock.duration if cfg.shock.enabled else shock_start

    rows: list[dict] = []
    rid = run_id_for(pair, resources, access)

    for t in range(rounds):
        if resources == "constrained":
            endowments = rng.uniform(eco.endow_lo, eco.endow_hi, n)
        else:
            endowments = np.full(n, eco.abundant_endowment)
        balance += endowments

        active = balance >= eco.survival_cost
        balance[active] -= eco.survival_cost

        # Material salience derived from own budget slack, not the cell label.
        stakes_bind = balance < (eco.survival_cost + eco.participation_cost + eco.contribution_cap)

        participated = np.zeros(n, dtype=bool)
        proposal_type = np.full(n, -1, dtype=int)
        for i in range(n):
            if not active[i] or balance[i] < eco.participation_cost:
                continue
            p = ag.participation_probability(
                beh, traits, i, float(efficacy[i]), bool(withdrawn[i]),
                recip, bool(stakes_bind[i]),
            )
            if rng.random() < p:
                participated[i] = True
                balance[i] -= eco.participation_cost
                proposal_type[i] = ag.choose_proposal_type(beh, traits, i, rng)

        decider = int(schedule[t])
        adopted_author = -1
        if active[decider]:
            if participated[decider]:
                adopted_author = decider
            else:
                submitters = np.flatnonzero(participated)
                if submitters.size > 0:
                    adopted_author = int(rng.choice(submitters))

        multiplier = eco.m_coord if adopted_author >= 0 else eco.m_base
        if shock_start <= t < shock_end:
            multiplier *= cfg.shock.multiplier_factor

        contribution = np.zeros(n)
        affordable = np.zeros(n)
        for i in range(n):
            if not active[i]:
                continue
            affordable[i] = min(eco.contribution_cap, balance[i])
            frac = ag.contribution_fraction(beh, traits, i, bool(withdrawn[i]), recip, rng)
            contribution[i] = min(eco.contribution_cap * frac, balance[i])
            balance[i] -= contribution[i]

        value = multiplier * contribution.sum()
        payout = value / n
        balance += payout

        impact = np.zeros(n)
        if active[decider]:
            impact[decider] += 1.0
        if adopted_author >= 0:
            impact[adopted_author] += 1.0

        for i in range(n):
            new_e = ag.update_efficacy(beh, float(efficacy[i]), float(impact[i]), bool(participated[i]))
            efficacy[i] = new_e
            if new_e < traits.withdraw_threshold[i]:
                low_e_streak[i] += 1
                if low_e_streak[i] >= beh.withdraw_patience:
                    withdrawn[i] = True
            else:
                low_e_streak[i] = 0
                withdrawn[i] = False

        recip = float(contribution.sum() / (cfg.n_agents * eco.contribution_cap))

        for i in range(n):
            rows.append({
                "run_id": rid, "pair": pair, "master_seed": master_seed,
                "resources": resources, "access": access, "round": t, "agent_id": i,
                "endowment": float(endowments[i]), "active": bool(active[i]),
                "stakes_bind": bool(stakes_bind[i]),
                "participated": bool(participated[i]),
                "proposal_type": int(proposal_type[i]),
                "is_decider": bool(decider == i),
                "adopted_author": adopted_author,
                "own_adopted": bool(adopted_author == i),
                "multiplier": float(multiplier),
                "contribution": float(contribution[i]),
                "affordable_max": float(affordable[i]),
                "payout": float(payout),
                "impact": float(impact[i]),
                "efficacy": float(efficacy[i]),
                "withdrawn": bool(withdrawn[i]),
                "balance_end": float(balance[i]),
                "in_shock": bool(shock_start <= t < shock_end),
            })

    events = pd.DataFrame(rows)
    traits_df = pd.DataFrame({
        "run_id": rid, "agent_id": np.arange(n),
        "coop": traits.coop, "status": traits.status, "explore": traits.explore,
        "recip_sens": traits.recip_sens, "withdraw_threshold": traits.withdraw_threshold,
        "pref_type": traits.pref_type,
    })
    return RunResult(events=events, traits=traits_df)
