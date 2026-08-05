"""Resource accounting: conservation, non-negative balances, and the
constrained/abundant contrast being real (SPEC §8, invariant 3)."""

import numpy as np

from universe25.config import RunConfig
from universe25.environment import simulate_run

CFG = RunConfig(n_rounds=40)


def _spend_ledger(events, eco):
    """Reconstructs per-agent flows; returns (inflow, outflow, final_balance)."""
    inflow = events.groupby("agent_id").apply(
        lambda g: g["endowment"].sum() + g["payout"].sum(), include_groups=False
    )
    outflow = events.groupby("agent_id").apply(
        lambda g: (
            (g["active"] * eco.survival_cost).sum()
            + (g["participated"] * eco.participation_cost).sum()
            + g["contribution"].sum()
        ),
        include_groups=False,
    )
    final = events.sort_values("round").groupby("agent_id")["balance_end"].last()
    return inflow, outflow, final


def test_conservation_constrained():
    result = simulate_run(CFG, "constrained", "concentrated", pair=0, master_seed=5)
    inflow, outflow, final = _spend_ledger(result.events, CFG.economy)
    np.testing.assert_allclose(final.values, (inflow - outflow).values, atol=1e-8)
    assert (outflow <= inflow + 1e-8).all()


def test_balance_never_negative():
    for resources in ("constrained", "abundant"):
        result = simulate_run(CFG, resources, "broad", pair=1, master_seed=6)
        assert (result.events["balance_end"] >= -1e-9).all()


def test_abundant_agents_never_inactive():
    result = simulate_run(CFG, "abundant", "concentrated", pair=2, master_seed=7)
    assert result.events["active"].all()


def test_constrained_budgets_actually_bind():
    """The stakes flag must separate the two resource conditions."""
    con = simulate_run(CFG, "constrained", "broad", pair=3, master_seed=8)
    abu = simulate_run(CFG, "abundant", "broad", pair=3, master_seed=8)
    assert con.events["stakes_bind"].mean() > 0.5
    assert abu.events["stakes_bind"].mean() == 0.0
