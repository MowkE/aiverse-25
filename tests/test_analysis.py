"""Analysis-layer correctness on synthetic data with known truth."""

import numpy as np
import pandas as pd
import pytest

from universe25.analysis import bootstrap_contrasts, contrasts_point
from universe25.validate import validate_summary


def _synthetic_summary(n_per_cell=40, seed=0):
    """Known truth: access effect 0.1 under constraint, 0.3 under abundance
    (interaction = 0.2); nHHI higher in concentrated cells."""
    rng = np.random.default_rng(seed)
    means = {
        ("constrained", "concentrated"): 0.50,
        ("constrained", "broad"): 0.60,
        ("abundant", "concentrated"): 0.40,
        ("abundant", "broad"): 0.70,
    }
    rows = []
    for (resources, access), mu in means.items():
        for k in range(n_per_cell):
            rows.append({
                "run_id": f"s{len(rows)}",
                "resources": resources,
                "access": access,
                "participation_rate": rng.normal(mu, 0.05),
                "output_norm": rng.normal(mu, 0.05),
                "influence_gini": 0.8 if access == "concentrated" else 0.2,
                "influence_nhhi": 0.9 if access == "concentrated" else 0.1,
                "contribution_gini": 0.3,
                "inactivity_rate": 0.0,
                "withdrawal_rate": 0.1,
                "proposal_diversity": 0.9,
                "behavior_entropy": 1.0,
            })
    return pd.DataFrame(rows)


def test_point_contrasts_recover_truth():
    summary = _synthetic_summary(n_per_cell=400)
    c = contrasts_point(summary, "participation_rate")
    assert c["access_effect_constrained"] == pytest.approx(0.10, abs=0.02)
    assert c["access_effect_abundant"] == pytest.approx(0.30, abs=0.02)
    assert c["interaction"] == pytest.approx(0.20, abs=0.03)


def test_bootstrap_ci_covers_truth_and_excludes_zero():
    summary = _synthetic_summary()
    table = bootstrap_contrasts(summary, "participation_rate", n_boot=500, seed=1)
    inter = table[table["contrast"] == "interaction"].iloc[0]
    assert inter["ci_lo"] < 0.20 < inter["ci_hi"]
    assert inter["excludes_zero"]


def test_validate_summary_passes_on_good_data():
    assert validate_summary(_synthetic_summary()) == []


def test_validate_summary_catches_broken_manipulation():
    summary = _synthetic_summary()
    summary["influence_nhhi"] = 0.5
    failures = validate_summary(summary)
    assert any("manipulation check" in f for f in failures)
