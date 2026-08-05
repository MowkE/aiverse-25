"""Budget guard: unconfirmed spends are blocked; overspend halts a run."""

import pytest

from universe25.llm.budget import (
    BudgetExceededError,
    BudgetGuard,
    BudgetNotConfirmedError,
)
from universe25.llm.config import LLMRunConfig
from universe25.llm.estimate import estimate_run
from universe25.llm.pricing import PRICES, cost_usd


def test_unarmed_guard_blocks_precall_and_estimate():
    guard = BudgetGuard(model="claude-sonnet-5")
    with pytest.raises(BudgetNotConfirmedError):
        guard.precall()
    with pytest.raises(BudgetNotConfirmedError):
        guard.authorize_estimate(1.0)


def test_estimate_above_confirmation_aborts():
    guard = BudgetGuard(model="claude-sonnet-5")
    guard.arm(5.0)
    guard.authorize_estimate(4.99)
    with pytest.raises(BudgetExceededError):
        guard.authorize_estimate(5.01)


def test_arm_rejects_nonpositive_budget():
    guard = BudgetGuard(model="claude-sonnet-5")
    with pytest.raises(BudgetNotConfirmedError):
        guard.arm(0.0)


def test_overspend_halts_midrun():
    guard = BudgetGuard(model="claude-sonnet-5")
    guard.arm(0.0001)
    guard.precall()
    guard.charge(input_tokens=10_000, output_tokens=10_000)
    with pytest.raises(BudgetExceededError):
        guard.precall()


def test_charge_accumulates_at_table_prices():
    guard = BudgetGuard(model="claude-sonnet-5")
    guard.arm(100.0)
    cost = guard.charge(1_000_000, 1_000_000)
    p_in, p_out = PRICES["claude-sonnet-5"]
    assert cost == pytest.approx(p_in + p_out)
    assert guard.spent_usd == pytest.approx(p_in + p_out)
    assert guard.calls_made == 1


def test_unknown_model_has_no_price():
    with pytest.raises(KeyError):
        cost_usd("model-that-does-not-exist", 1, 1)


def test_run_estimate_shape():
    cfg = LLMRunConfig()
    est = estimate_run(cfg)
    # 8 agents x 40 rounds: public + contribution 320 each, decision 40, report 8
    by_phase = {p.phase: p.calls for p in est.phases}
    assert by_phase == {"public": 320, "decision": 40, "contribution": 320, "report": 8}
    assert est.calls == 688
    assert est.input_tokens > 0 and est.output_tokens > 0
    for model in ("claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"):
        assert est.cost(model) > 0
