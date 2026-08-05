"""Cache/resume: interrupt mid-run, resume, byte-identical result; drift guard."""

import json

import pandas as pd
import pytest

from universe25.llm.cache import CachedCall, CacheDriftError, CallCache, call_key, prompt_hash
from universe25.llm.config import LLMRunConfig
from universe25.llm.orchestrator import simulate_llm_run
from universe25.llm.providers import MockProvider

CFG = LLMRunConfig(n_rounds=6, report_rounds="last")
SEED = 424242


def _record(key: str, h: str) -> CachedCall:
    return CachedCall(
        key=key, prompt_sha256=h, response_text='{"contribution_fraction": 0.5}',
        parsed={"contribution_fraction": 0.5}, valid=True, retries=0,
        invalid_after_retries=False, contamination_flag=False,
        input_tokens=10, output_tokens=5, latency_ms=1.0,
        provider="mock", model="m", request_id=None,
    )


def test_cache_roundtrip_and_hit_counting(tmp_path):
    cache = CallCache(tmp_path, "run-x")
    key = call_key("run-x", 0, 1, "contribution", "llm-t1", "m", 7)
    h = prompt_hash("sys", "user")
    assert cache.lookup(key, h) is None
    cache.store(_record(key, h))

    reloaded = CallCache(tmp_path, "run-x")
    assert len(reloaded) == 1
    rec = reloaded.lookup(key, h)
    assert rec is not None and rec.parsed == {"contribution_fraction": 0.5}
    assert reloaded.hits == 1


def test_cache_raises_on_prompt_drift(tmp_path):
    cache = CallCache(tmp_path, "run-x")
    key = call_key("run-x", 0, 1, "contribution", "llm-t1", "m", 7)
    cache.store(_record(key, prompt_hash("sys", "user")))
    with pytest.raises(CacheDriftError):
        cache.lookup(key, prompt_hash("sys", "DIFFERENT PROMPT"))


def test_interrupt_resume_is_byte_identical(tmp_path):
    """A run killed mid-flight resumes from cache and reproduces a clean run."""
    clean_dir = tmp_path / "clean"
    resume_dir = tmp_path / "resume"

    clean = simulate_llm_run(
        CFG, "constrained", "broad", 0, SEED, MockProvider(), clean_dir, "v-test"
    )

    # Interrupt: the provider dies after 40 calls, mid-run.
    dying = MockProvider(raise_after_calls=40)
    with pytest.raises(ConnectionError):
        simulate_llm_run(CFG, "constrained", "broad", 0, SEED, dying, resume_dir, "v-test")
    partial = CallCache(resume_dir, "p0000-constrained-broad")
    assert 0 < len(partial) <= 40

    # Resume with a healthy provider: completed observations come from cache.
    resumed = simulate_llm_run(
        CFG, "constrained", "broad", 0, SEED, MockProvider(), resume_dir, "v-test"
    )

    pd.testing.assert_frame_equal(clean.events, resumed.events)
    pd.testing.assert_frame_equal(clean.reports, resumed.reports)
    assert clean.events.to_csv(index=False) == resumed.events.to_csv(index=False)

    # Cache hits are recorded on the resumed run's call log.
    assert resumed.calls["cache_hit"].sum() > 0
    # Everything except cache-hit provenance matches the clean run's log.
    cols = [c for c in clean.calls.columns if c != "cache_hit"]
    pd.testing.assert_frame_equal(clean.calls[cols], resumed.calls[cols])


def test_full_rerun_is_all_cache_hits(tmp_path):
    first = simulate_llm_run(
        CFG, "abundant", "concentrated", 0, SEED, MockProvider(), tmp_path, "v-test"
    )
    assert not first.calls["cache_hit"].any()
    second = simulate_llm_run(
        CFG, "abundant", "concentrated", 0, SEED, MockProvider(), tmp_path, "v-test"
    )
    assert second.calls["cache_hit"].all()
    pd.testing.assert_frame_equal(first.events, second.events)


def test_cache_file_is_jsonl_with_expected_key_fields(tmp_path):
    simulate_llm_run(
        CFG, "abundant", "broad", 0, SEED, MockProvider(), tmp_path, "v-test"
    )
    path = tmp_path / "p0000-abundant-broad.jsonl"
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        first_line = json.loads(f.readline())
    key_parts = first_line["key"].split("|")
    assert key_parts[0] == "p0000-abundant-broad"          # run_id
    assert key_parts[3] in {"public", "decision", "contribution", "report"}
    assert key_parts[4] == CFG.template_version
    assert key_parts[5] == CFG.model
