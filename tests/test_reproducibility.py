"""Determinism and seed-stream independence (SPEC §8, invariants 1-2)."""

import pandas as pd

from universe25.agents import draw_traits
from universe25.config import RunConfig
from universe25.environment import simulate_run
from universe25.rng import spawn_pair_streams

CFG = RunConfig(n_rounds=15)


def test_same_seed_identical_events():
    a = simulate_run(CFG, "constrained", "broad", pair=0, master_seed=123)
    b = simulate_run(CFG, "constrained", "broad", pair=0, master_seed=123)
    pd.testing.assert_frame_equal(a.events, b.events)


def test_different_master_seed_differs():
    a = simulate_run(CFG, "constrained", "broad", pair=0, master_seed=123)
    b = simulate_run(CFG, "constrained", "broad", pair=0, master_seed=124)
    assert not a.events.equals(b.events)


def test_traits_stream_independent_of_dynamics_consumption():
    """Cells consume different amounts of dynamics randomness; the traits
    stream must be unaffected (tested via a fresh spawn per cell)."""
    t1 = draw_traits(spawn_pair_streams(99, 0).traits, 8)
    streams = spawn_pair_streams(99, 0)
    streams.dynamics.random(10_000)
    t2 = draw_traits(streams.traits, 8)
    assert (t1.coop == t2.coop).all()
    assert (t1.withdraw_threshold == t2.withdraw_threshold).all()


def test_pairs_are_independent():
    a = simulate_run(CFG, "abundant", "broad", pair=0, master_seed=123)
    b = simulate_run(CFG, "abundant", "broad", pair=1, master_seed=123)
    assert not a.traits.drop(columns=["run_id"]).equals(b.traits.drop(columns=["run_id"]))
