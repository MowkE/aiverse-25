"""Orchestrator: mock smoke through the existing metrics/validate machinery,
retry-exhaustion no-ops, treatment mechanics, and logging completeness."""

import numpy as np
import pytest

from universe25.config import CELLS, RunConfig
from universe25.environment import decider_schedule, simulate_run
from universe25.llm.config import LLMBatchConfig, LLMRunConfig
from universe25.llm.orchestrator import run_llm_batch, simulate_llm_run
from universe25.llm.providers import MockProvider
from universe25.metrics import summarize_run
from universe25.rng import spawn_pair_streams
from universe25.validate import validate_summary

SEED = 314159
SHORT = LLMRunConfig(n_rounds=8, report_rounds="last")


@pytest.fixture(scope="module")
def smoke_batch(tmp_path_factory):
    out = tmp_path_factory.mktemp("llm_smoke_out")
    cfg = LLMBatchConfig(master_seed=SEED, n_pairs=1, output_dir=str(out),
                         run=LLMRunConfig(n_rounds=40, report_rounds="last"))
    summary = run_llm_batch(cfg, MockProvider(), output_dir=str(out))
    return cfg, out, summary


def test_smoke_four_runs_one_per_cell(smoke_batch):
    _, _, summary = smoke_batch
    assert len(summary) == 4
    cells = set(zip(summary["resources"], summary["access"]))
    assert cells == set(CELLS)


def test_smoke_passes_existing_validation_machinery(smoke_batch):
    _, _, summary = smoke_batch
    assert validate_summary(summary) == []


def test_smoke_outputs_written(smoke_batch):
    _, out, _ = smoke_batch
    for name in ("events.parquet", "llm_calls.parquet", "reports.parquet",
                 "run_summary.csv", "run_summary.parquet", "config.json",
                 "manifest.json"):
        assert (out / name).exists(), name
    assert list((out / "llm_cache").glob("*.jsonl"))


def test_events_have_abm_columns(smoke_batch):
    import pandas as pd

    _, out, _ = smoke_batch
    llm_events = pd.read_parquet(out / "events.parquet")
    abm_events = simulate_run(RunConfig(n_rounds=2), "constrained", "broad", 0, SEED).events
    missing = set(abm_events.columns) - set(llm_events.columns)
    assert missing == set(), f"LLM events missing ABM columns: {missing}"
    # summarize_run works directly on a single LLM run's events
    one = llm_events[llm_events["run_id"] == llm_events["run_id"].iloc[0]]
    summary = summarize_run(one)
    assert 0.0 <= summary["participation_rate"] <= 1.0


def test_decider_schedule_matches_abm(tmp_path):
    """Same master seed + pair => same seat permutation/rotation as Study 1."""
    result = simulate_llm_run(SHORT, "constrained", "concentrated", 3, SEED,
                              MockProvider(), tmp_path, "v-test")
    streams = spawn_pair_streams(SEED, 3)
    expected = decider_schedule("concentrated", SHORT.n_agents, SHORT.n_rounds,
                                streams.structure)
    got = (
        result.events[result.events["is_decider"]]
        .sort_values("round")["agent_id"].to_numpy()
    )
    assert np.array_equal(got, expected)


def test_concentrated_has_single_decider_broad_rotates(tmp_path):
    conc = simulate_llm_run(SHORT, "abundant", "concentrated", 0, SEED,
                            MockProvider(), tmp_path / "c", "v-test")
    deciders = conc.events[conc.events["is_decider"]]["agent_id"].unique()
    assert len(deciders) == 1
    rot = simulate_llm_run(SHORT, "abundant", "broad", 0, SEED,
                           MockProvider(), tmp_path / "b", "v-test")
    rot_deciders = rot.events[rot.events["is_decider"]]["agent_id"].unique()
    assert len(rot_deciders) == SHORT.n_agents


def test_adoption_changes_multiplier(tmp_path):
    """Authority is real: adopted rounds carry m_coord, others m_base."""
    result = simulate_llm_run(SHORT, "abundant", "broad", 1, SEED,
                              MockProvider(), tmp_path, "v-test")
    ev = result.events[~result.events["in_shock"]]
    adopted = ev[ev["adopted_author"] >= 0]["multiplier"]
    not_adopted = ev[ev["adopted_author"] < 0]["multiplier"]
    if len(adopted):
        assert (adopted == SHORT.economy.m_coord).all()
    if len(not_adopted):
        assert (not_adopted == SHORT.economy.m_base).all()


def test_retry_exhaustion_records_noops_never_substitutes(tmp_path):
    provider = MockProvider(always_invalid=True)
    cfg = LLMRunConfig(n_rounds=3, max_schema_retries=2, report_rounds="last")
    result = simulate_llm_run(cfg, "abundant", "broad", 0, SEED, provider,
                              tmp_path, "v-test")
    calls = result.calls
    assert (~calls["valid"]).all()
    assert calls["invalid_after_retries"].all()
    assert (calls["retries"] == cfg.max_schema_retries).all()
    # no-ops recorded as data: nobody participates, contributes, or adopts
    ev = result.events
    assert not ev["participated"].any()
    assert (ev["contribution"] == 0).all()
    assert (ev["adopted_author"] == -1).all()
    assert ev["public_noop"].any() and ev["contribution_noop"].any()
    # reports invalid too, values NaN
    assert (~result.reports["valid"]).all()
    assert result.reports["confidence"].isna().all()
    # provider was actually asked max_retries + 1 times per resolved call
    assert provider.calls == len(calls) * (cfg.max_schema_retries + 1)


def test_partial_invalidity_only_noops_failed_calls(tmp_path):
    provider = MockProvider(invalid_first_calls=5)
    cfg = LLMRunConfig(n_rounds=4, max_schema_retries=0, report_rounds="none")
    result = simulate_llm_run(cfg, "abundant", "broad", 0, SEED, provider,
                              tmp_path, "v-test")
    calls = result.calls
    assert (~calls["valid"]).sum() == 5
    assert calls["valid"].sum() == len(calls) - 5
    assert result.events["participated"].any()  # later valid calls still act


def test_call_log_is_complete_and_versioned(tmp_path):
    result = simulate_llm_run(SHORT, "constrained", "broad", 0, SEED,
                              MockProvider(), tmp_path, "v-test")
    calls = result.calls
    expected_cols = {
        "run_id", "pair", "resources", "access", "round", "agent_id", "phase",
        "template_version", "model", "provider", "temperature", "effort",
        "thinking", "seed", "prompt_system", "prompt_user", "response_text",
        "valid", "retries", "invalid_after_retries", "contamination_flag",
        "cache_hit", "input_tokens", "output_tokens", "latency_ms",
        "request_id", "code_version",
    }
    assert expected_cols <= set(calls.columns)
    assert (calls["template_version"] == SHORT.template_version).all()
    assert (calls["code_version"] == "v-test").all()
    assert (calls["prompt_system"].str.len() > 0).all()
    assert set(calls["phase"].unique()) <= {"public", "decision", "contribution", "report"}


def test_template_version_mismatch_refuses_to_run(tmp_path):
    cfg = LLMRunConfig(template_version="llm-t999")
    with pytest.raises(ValueError, match="template_version"):
        simulate_llm_run(cfg, "abundant", "broad", 0, SEED, MockProvider(),
                         tmp_path, "v-test")


def test_reports_secondary_all_agents(tmp_path):
    result = simulate_llm_run(SHORT, "abundant", "concentrated", 0, SEED,
                              MockProvider(), tmp_path, "v-test")
    assert len(result.reports) == SHORT.n_agents  # report_rounds="last"
    assert result.reports["round"].unique().tolist() == [SHORT.n_rounds - 1]
    valid = result.reports[result.reports["valid"]]
    for col in ("confidence", "perceived_efficacy", "legitimacy_rating"):
        assert valid[col].between(0, 1).all()
