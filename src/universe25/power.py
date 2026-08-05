"""Simulation-based power analysis (SPEC §9, VALIDATION M2).

Parametric: draws synthetic run-level outcomes from pilot cell means/SDs and
estimates power for (a) the access main effect within abundance (Welch t) and
(b) the interaction (z on the difference-in-differences), across a grid of
runs/cell. Interactions need roughly 4x the sample of main effects at equal
effect size — this script exists so that number is computed, not assumed.
Pilot effect sizes inform planning only; they confirm nothing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .config import ACCESS_LEVELS, RESOURCE_LEVELS


def pilot_moments(summary: pd.DataFrame, outcome: str) -> dict[tuple[str, str], tuple[float, float]]:
    out = {}
    for r in RESOURCE_LEVELS:
        for a in ACCESS_LEVELS:
            vals = summary.loc[
                (summary["resources"] == r) & (summary["access"] == a), outcome
            ].to_numpy(dtype=float)
            out[(r, a)] = (float(vals.mean()), float(vals.std(ddof=1)))
    return out


def power_curve(
    moments: dict[tuple[str, str], tuple[float, float]],
    outcome: str,
    grid: tuple[int, ...] = (10, 20, 30, 50, 75, 100, 150, 200),
    n_sims: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for n in grid:
        hits_main = 0
        hits_inter = 0
        for _ in range(n_sims):
            draws = {
                key: rng.normal(mu, sd, n) for key, (mu, sd) in moments.items()
            }
            a = draws[("abundant", "broad")]
            b = draws[("abundant", "concentrated")]
            _, p_main = stats.ttest_ind(a, b, equal_var=False)
            if p_main < alpha:
                hits_main += 1

            did = (
                a.mean() - b.mean()
                - (draws[("constrained", "broad")].mean() - draws[("constrained", "concentrated")].mean())
            )
            se = np.sqrt(sum(d.var(ddof=1) / n for d in draws.values()))
            if se > 0 and 2 * stats.norm.sf(abs(did / se)) < alpha:
                hits_inter += 1
        rows.append({
            "outcome": outcome,
            "runs_per_cell": n,
            "power_access_main_abundant": hits_main / n_sims,
            "power_interaction": hits_inter / n_sims,
        })
    return pd.DataFrame(rows)


def power_report(summary: pd.DataFrame, outcomes: tuple[str, ...] = ("participation_rate", "output_norm"), **kw) -> pd.DataFrame:
    return pd.concat(
        [power_curve(pilot_moments(summary, o), o, **kw) for o in outcomes],
        ignore_index=True,
    )
