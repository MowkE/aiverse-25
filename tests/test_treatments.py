"""Treatment hygiene: traits precede treatment, authority is consequential,
and treatments enter only through the environment (SPEC §8, invariants 2, 4, 7)."""

import numpy as np
import pandas as pd

from universe25.config import CELLS, RunConfig
from universe25.environment import decider_schedule, simulate_run

CFG = RunConfig(n_rounds=20)


def test_traits_identical_across_all_cells_of_a_pair():
    traits = {}
    for resources, access in CELLS:
        result = simulate_run(CFG, resources, access, pair=0, master_seed=42)
        traits[(resources, access)] = result.traits.drop(columns=["run_id"])
    baseline = traits[CELLS[0]]
    for cell in CELLS[1:]:
        pd.testing.assert_frame_equal(baseline, traits[cell])


def test_concentrated_schedule_is_a_single_seat():
    rng = np.random.default_rng(0)
    schedule = decider_schedule("concentrated", 8, 40, rng)
    assert len(np.unique(schedule)) == 1


def test_broad_schedule_rotates_through_all_seats():
    rng = np.random.default_rng(0)
    schedule = decider_schedule("broad", 8, 40, rng)
    assert set(schedule[:8]) == set(range(8))
    assert np.array_equal(schedule[:8], schedule[8:16])


def test_decider_seat_matched_across_cells_within_pair():
    seats = []
    for resources in ("constrained", "abundant"):
        result = simulate_run(CFG, resources, "concentrated", pair=3, master_seed=42)
        deciders = result.events.loc[result.events["is_decider"], "agent_id"].unique()
        seats.append(set(deciders))
    assert seats[0] == seats[1]


def test_authority_changes_environment_state():
    """Adopted proposals must move the multiplier (labels are not a manipulation)."""
    result = simulate_run(CFG, "abundant", "broad", pair=0, master_seed=7)
    ev = result.events[~result.events["in_shock"]]
    adopted = ev[ev["adopted_author"] >= 0]["multiplier"]
    not_adopted = ev[ev["adopted_author"] < 0]["multiplier"]
    assert (adopted == CFG.economy.m_coord).all()
    if len(not_adopted):
        assert (not_adopted == CFG.economy.m_base).all()


def test_impact_only_from_realized_authority():
    result = simulate_run(CFG, "abundant", "concentrated", pair=1, master_seed=9)
    ev = result.events
    got_impact = ev[ev["impact"] > 0]
    assert ((got_impact["is_decider"]) | (got_impact["own_adopted"])).all()
