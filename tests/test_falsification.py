"""Falsification controls (VALIDATION C2, SPEC §8 invariant 6).

The role-access effect on participation must vanish for agents whose rules
cannot carry the efficacy mechanism. If these tests fail, the treatment is
leaking into behavior through a channel other than the documented one.
"""

import numpy as np
import pytest

from universe25.config import RunConfig, with_policy
from universe25.environment import simulate_run
from universe25.metrics import summarize_run

N_PAIRS = 12


def _access_effect_on_participation(cfg: RunConfig, resources: str) -> float:
    diffs = []
    for pair in range(N_PAIRS):
        rates = {}
        for access in ("broad", "concentrated"):
            result = simulate_run(cfg, resources, access, pair=pair, master_seed=777)
            rates[access] = summarize_run(result.events)["participation_rate"]
        diffs.append(rates["broad"] - rates["concentrated"])
    return float(np.mean(diffs))


@pytest.mark.parametrize("policy", ["random", "material_only"])
def test_mechanism_blind_agents_show_no_access_effect(policy):
    cfg = with_policy(RunConfig(n_rounds=40), policy)
    effect = _access_effect_on_participation(cfg, "abundant")
    assert abs(effect) < 0.03, (
        f"{policy} agents show a role-access participation effect of {effect:.4f}; "
        "treatment is leaking into behavior outside the efficacy channel"
    )


def test_heterogeneous_agents_do_show_the_effect():
    """Sanity: the documented mechanism generates the pattern it claims to."""
    cfg = RunConfig(n_rounds=40)
    effect = _access_effect_on_participation(cfg, "abundant")
    assert effect > 0.05, (
        f"expected broad access to raise participation under abundance; got {effect:.4f}"
    )
