"""Batch-output validation: metric bounds and design invariants (SPEC §8)."""

from __future__ import annotations

import numpy as np
import pandas as pd

BOUNDS = {
    "participation_rate": (0.0, 1.0),
    "output_norm": (0.0, 1.0),
    "influence_gini": (0.0, 1.0),
    "influence_nhhi": (0.0, 1.0),
    "contribution_gini": (0.0, 1.0),
    "inactivity_rate": (0.0, 1.0),
    "withdrawal_rate": (0.0, 1.0),
    "proposal_diversity": (0.0, float(np.log(3)) + 1e-9),
    "behavior_entropy": (0.0, float(np.log(5)) + 1e-9),
}


def validate_summary(summary: pd.DataFrame) -> list[str]:
    """Returns a list of failures; empty means valid."""
    failures: list[str] = []
    for col, (lo, hi) in BOUNDS.items():
        if col not in summary.columns:
            failures.append(f"missing column: {col}")
            continue
        vals = summary[col].dropna()
        if ((vals < lo - 1e-12) | (vals > hi + 1e-12)).any():
            failures.append(f"{col} outside [{lo}, {hi}]")

    counts = summary.groupby(["resources", "access"]).size()
    if counts.nunique() != 1:
        failures.append(f"unbalanced cells: {counts.to_dict()}")

    if summary.duplicated(subset=["run_id"]).any():
        failures.append("duplicate run_id values")

    conc = summary[summary["access"] == "concentrated"]["influence_nhhi"].mean()
    broad = summary[summary["access"] == "broad"]["influence_nhhi"].mean()
    if not conc > broad:
        failures.append(
            f"manipulation check failed: concentrated nHHI ({conc:.3f}) "
            f"not greater than broad ({broad:.3f})"
        )
    return failures
