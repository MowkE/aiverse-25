"""Memory manager: rolling window, counters, pseudonyms, no cross-run reuse."""

import numpy as np

from universe25.llm.memory import (
    PSEUDONYMS,
    AgentMemory,
    assign_pseudonyms,
    round_digest,
)


def test_pseudonyms_seeded_and_treatment_free():
    rng_a = np.random.default_rng(np.random.SeedSequence([1, 0, 1001]))
    rng_b = np.random.default_rng(np.random.SeedSequence([1, 0, 1001]))
    names_a = assign_pseudonyms(8, rng_a)
    names_b = assign_pseudonyms(8, rng_b)
    assert names_a == names_b  # deterministic in the seed
    assert len(set(names_a)) == 8
    for name in names_a:
        assert name.startswith("Agent ")
        assert name.removeprefix("Agent ") in PSEUDONYMS

    rng_c = np.random.default_rng(np.random.SeedSequence([2, 0, 1001]))
    assert assign_pseudonyms(8, rng_c) != names_a  # varies with the seed


def test_rolling_window_keeps_last_k():
    mem = AgentMemory(name="Agent Wren", window=3)
    for t in range(10):
        mem.record_round(t, f"digest-{t}", was_chair=False, own_adopted=False,
                         participated=True)
    assert len(mem.digests) == 3
    assert mem.digests == ["Round 8: digest-7", "Round 9: digest-8", "Round 10: digest-9"]
    assert mem.rounds_seen == 10
    assert mem.participation_count == 10


def test_summary_counters():
    mem = AgentMemory(name="Agent Tern", window=5)
    assert "first round" in mem.summary()
    mem.record_round(0, "d", was_chair=True, own_adopted=True, participated=True)
    mem.record_round(1, "d", was_chair=False, own_adopted=False, participated=False)
    s = mem.summary()
    assert "2 completed rounds" in s
    assert "chaired 1 rounds" in s
    assert "adopted 1 times" in s


def test_render_contains_summary_and_digests():
    mem = AgentMemory(name="Agent Swift", window=2)
    mem.record_round(0, "alpha", was_chair=False, own_adopted=False, participated=True)
    text = mem.render()
    assert "Recent rounds:" in text
    assert "alpha" in text


def test_round_digest_is_factual_and_agent_specific():
    digest = round_digest(
        chair_name="Agent Kestrel",
        adopted_author_name="Agent Heron",
        multiplier=1.5,
        project_value=12.0,
        payout=1.5,
        own_balance=3.25,
        own_participated=True,
        own_contribution=1.0,
        public_messages=[("Agent Heron", "let us pool a bit more this round")],
    )
    assert "Agent Kestrel chaired" in digest
    assert "Agent Heron's suggestion was adopted" in digest
    assert "you spoke up" in digest
    assert 'said "let us pool a bit more this round"' in digest


def test_memory_never_crosses_runs():
    """Fresh AgentMemory objects start empty — the orchestrator builds new ones
    per run; this pins the constructor default that makes that safe."""
    assert AgentMemory(name="Agent Finch").digests == []
    assert AgentMemory(name="Agent Finch").rounds_seen == 0
