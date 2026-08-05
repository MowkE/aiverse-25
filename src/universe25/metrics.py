"""Run-level outcome metrics (SPEC §6) with explicit edge-case conventions:
all-zero vectors yield concentration 0 with a logged flag (VALIDATION M3)."""

from __future__ import annotations

import numpy as np
import pandas as pd

EPS = 1e-9

ACTION_PROFILES = (
    "inactive",
    "silent-freeride",
    "silent-contribute",
    "participate-freeride",
    "participate-contribute",
)


def gini(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if x.size == 0 or np.any(x < 0):
        raise ValueError("gini requires a nonempty nonnegative vector")
    total = x.sum()
    if total < EPS:
        return 0.0
    diff_sum = np.abs(x[:, None] - x[None, :]).sum()
    return float(diff_sum / (2.0 * x.size * total))


def normalized_hhi(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if x.size == 0 or np.any(x < 0):
        raise ValueError("normalized_hhi requires a nonempty nonnegative vector")
    n = x.size
    if n == 1:
        return 1.0
    total = x.sum()
    if total < EPS:
        return 0.0
    shares = x / total
    hhi = float((shares**2).sum())
    return (hhi - 1.0 / n) / (1.0 - 1.0 / n)


def entropy(counts: np.ndarray) -> float:
    counts = np.asarray(counts, dtype=float)
    total = counts.sum()
    if total < EPS:
        return 0.0
    p = counts[counts > 0] / total
    p = p[p > 0]  # guard against underflow to exactly 0 after normalization
    return float(-(p * np.log(p)).sum())


def action_profile(row: pd.Series) -> str:
    if not row["active"]:
        return "inactive"
    contributes = row["contribution"] > EPS
    if row["participated"]:
        return "participate-contribute" if contributes else "participate-freeride"
    return "silent-contribute" if contributes else "silent-freeride"


def summarize_run(events: pd.DataFrame) -> dict:
    first = events.iloc[0]
    act = events[events["active"]]

    eligible = len(act)
    participation_rate = float(act["participated"].mean()) if eligible else 0.0

    affordable_total = float(act["affordable_max"].sum())
    contributed_total = float(act["contribution"].sum())
    output_norm = contributed_total / affordable_total if affordable_total > EPS else 0.0

    impact_by_agent = events.groupby("agent_id")["impact"].sum().to_numpy()
    influence_zero = bool(impact_by_agent.sum() < EPS)
    contrib_by_agent = events.groupby("agent_id")["contribution"].sum().to_numpy()

    proposals = events.loc[events["proposal_type"] >= 0, "proposal_type"]
    proposal_counts = proposals.value_counts().reindex(range(3), fill_value=0).to_numpy()

    profiles = events.apply(action_profile, axis=1)
    profile_counts = profiles.value_counts().reindex(ACTION_PROFILES, fill_value=0).to_numpy()
    behavior_entropy = entropy(profile_counts)

    resilience = np.nan
    if events["in_shock"].any():
        shock_rounds = events.loc[events["in_shock"], "round"]
        s0, s1 = int(shock_rounds.min()), int(shock_rounds.max())
        pre_win = events[(events["round"] >= s0 - 5) & (events["round"] < s0)]
        post_win = events[(events["round"] > s1) & (events["round"] <= s1 + 5)]
        pre_out = pre_win["contribution"].sum()
        post_out = post_win["contribution"].sum()
        resilience = float(post_out / pre_out) if pre_out > EPS else np.nan

    return {
        "run_id": first["run_id"],
        "pair": int(first["pair"]),
        "master_seed": int(first["master_seed"]),
        "resources": first["resources"],
        "access": first["access"],
        "participation_rate": participation_rate,
        "output_norm": float(output_norm),
        "output_raw": contributed_total,
        "influence_gini": gini(impact_by_agent),
        "influence_nhhi": normalized_hhi(impact_by_agent),
        "influence_all_zero": influence_zero,
        "contribution_gini": gini(contrib_by_agent),
        "inactivity_rate": float(1.0 - events["active"].mean()),
        "withdrawal_rate": float(events["withdrawn"].mean()),
        "proposal_diversity": entropy(proposal_counts),
        "behavior_entropy": behavior_entropy,
        "behavior_n_eff": float(np.exp(behavior_entropy)),
        "resilience": resilience,
    }
