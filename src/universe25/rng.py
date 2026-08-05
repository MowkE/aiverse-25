"""Deterministic seed-stream management (SPEC §8, invariants 1-2).

Each (master_seed, pair) yields three independent streams shared by all four
treatment cells of the pair: traits, structure (seat permutation / rotation
order), and dynamics. Sharing the dynamics stream across cells is deliberate
common-random-numbers pairing; treatments enter only through the environment.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PairStreams:
    traits: np.random.Generator
    structure: np.random.Generator
    dynamics: np.random.Generator


def spawn_pair_streams(master_seed: int, pair: int) -> PairStreams:
    ss = np.random.SeedSequence([master_seed, pair])
    traits_ss, structure_ss, dynamics_ss = ss.spawn(3)
    return PairStreams(
        traits=np.random.default_rng(traits_ss),
        structure=np.random.default_rng(structure_ss),
        dynamics=np.random.default_rng(dynamics_ss),
    )
