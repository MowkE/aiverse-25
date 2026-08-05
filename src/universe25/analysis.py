"""Run-level analysis: cell means, contrasts, interaction, clustered bootstrap.

The run is the experimental unit; the bootstrap resamples runs within cells
(never agent-turns). The interaction is the preregistered primary (SPEC §7):
  DiD = (broad - concentrated | abundant) - (broad - concentrated | constrained)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ACCESS_LEVELS, RESOURCE_LEVELS

PRIMARY_OUTCOMES = ("participation_rate", "output_norm")
MANIPULATION_CHECKS = ("influence_gini", "influence_nhhi")


def cell_means(summary: pd.DataFrame, outcome: str) -> pd.DataFrame:
    return (
        summary.groupby(["resources", "access"])[outcome]
        .agg(["mean", "std", "count"])
        .reset_index()
    )


def _cell_values(summary: pd.DataFrame, resources: str, access: str, outcome: str) -> np.ndarray:
    mask = (summary["resources"] == resources) & (summary["access"] == access)
    return summary.loc[mask, outcome].to_numpy(dtype=float)


def contrasts_point(summary: pd.DataFrame, outcome: str) -> dict[str, float]:
    v = {
        (r, a): _cell_values(summary, r, a, outcome).mean()
        for r in RESOURCE_LEVELS
        for a in ACCESS_LEVELS
    }
    access_constrained = v[("constrained", "broad")] - v[("constrained", "concentrated")]
    access_abundant = v[("abundant", "broad")] - v[("abundant", "concentrated")]
    resource_effect = (
        (v[("abundant", "broad")] + v[("abundant", "concentrated")]) / 2
        - (v[("constrained", "broad")] + v[("constrained", "concentrated")]) / 2
    )
    return {
        "access_effect_constrained": access_constrained,
        "access_effect_abundant": access_abundant,
        "resource_effect": resource_effect,
        "interaction": access_abundant - access_constrained,
    }


def bootstrap_contrasts(
    summary: pd.DataFrame, outcome: str, n_boot: int = 2000, seed: int = 0
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cells = {
        (r, a): _cell_values(summary, r, a, outcome)
        for r in RESOURCE_LEVELS
        for a in ACCESS_LEVELS
    }
    names = ["access_effect_constrained", "access_effect_abundant", "resource_effect", "interaction"]
    draws = {name: np.empty(n_boot) for name in names}
    for b in range(n_boot):
        m = {
            key: vals[rng.integers(0, vals.size, vals.size)].mean()
            for key, vals in cells.items()
        }
        ac = m[("constrained", "broad")] - m[("constrained", "concentrated")]
        aa = m[("abundant", "broad")] - m[("abundant", "concentrated")]
        re_ = (
            (m[("abundant", "broad")] + m[("abundant", "concentrated")]) / 2
            - (m[("constrained", "broad")] + m[("constrained", "concentrated")]) / 2
        )
        draws["access_effect_constrained"][b] = ac
        draws["access_effect_abundant"][b] = aa
        draws["resource_effect"][b] = re_
        draws["interaction"][b] = aa - ac

    point = contrasts_point(summary, outcome)
    rows = []
    for name in names:
        lo, hi = np.percentile(draws[name], [2.5, 97.5])
        rows.append({
            "outcome": outcome,
            "contrast": name,
            "estimate": point[name],
            "ci_lo": float(lo),
            "ci_hi": float(hi),
            "excludes_zero": bool(lo > 0 or hi < 0),
        })
    return pd.DataFrame(rows)


def standardized_effects(summary: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Cohen's d for the access effect within each resource level (pooled SD)."""
    rows = []
    for r in RESOURCE_LEVELS:
        a = _cell_values(summary, r, "broad", outcome)
        b = _cell_values(summary, r, "concentrated", outcome)
        pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
        d = (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan
        rows.append({"outcome": outcome, "resources": r, "cohens_d_access": float(d)})
    return pd.DataFrame(rows)


def full_report(summary: pd.DataFrame, n_boot: int = 2000, seed: int = 0) -> dict[str, pd.DataFrame]:
    outcomes = list(PRIMARY_OUTCOMES) + list(MANIPULATION_CHECKS)
    return {
        "cell_means": pd.concat(
            [cell_means(summary, o).assign(outcome=o) for o in outcomes], ignore_index=True
        ),
        "contrasts": pd.concat(
            [bootstrap_contrasts(summary, o, n_boot, seed) for o in outcomes], ignore_index=True
        ),
        "standardized": pd.concat(
            [standardized_effects(summary, o) for o in PRIMARY_OUTCOMES], ignore_index=True
        ),
    }
