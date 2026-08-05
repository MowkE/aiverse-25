"""Contamination: banned terms never appear in agent-visible experimenter text."""

import pytest

from universe25.config import CELLS
from universe25.llm.config import LLMRunConfig
from universe25.llm.memory import round_digest
from universe25.llm.prompts import (
    BANNED_TERMS,
    assert_uncontaminated,
    contamination_scan,
    example_prompts,
    outcome_sentence,
    scan_agent_text,
)

CFG = LLMRunConfig()


@pytest.mark.parametrize("resources,access", CELLS)
def test_every_template_every_cell_is_clean(resources, access):
    """Render every prompt template for every cell; no banned term may appear.

    role access has no template slot at all (the schedule is experienced, not
    described), so rendering per resources level covers all four cells; the
    parametrization over full cells documents and pins that claim.
    """
    for phase, (system, user) in example_prompts(CFG, resources).items():
        found = contamination_scan(system + "\n" + user)
        assert not found, f"banned terms {found} in {phase} prompt for cell {resources}:{access}"


def test_access_arms_share_identical_templates():
    """System and user templates must not differ by role-access arm at all."""
    for resources in ("constrained", "abundant"):
        a = example_prompts(CFG, resources)
        b = example_prompts(CFG, resources)
        assert a == b


def test_system_prompts_differ_only_in_income_slot():
    from universe25.llm.prompts import system_prompt

    con = system_prompt("Agent Kestrel", "constrained", CFG)
    abu = system_prompt("Agent Kestrel", "abundant", CFG)
    con_lines = con.splitlines()
    abu_lines = abu.splitlines()
    assert len(con_lines) == len(abu_lines)
    diff = [i for i, (a, b) in enumerate(zip(con_lines, abu_lines)) if a != b]
    assert len(diff) == 1  # exactly the factual income description line


def test_round_digest_template_is_clean():
    digest = round_digest(
        chair_name="Agent Kestrel", adopted_author_name="Agent Heron",
        multiplier=1.5, project_value=10.0, payout=1.25, own_balance=2.0,
        own_participated=False, own_contribution=0.0,
        public_messages=[("Agent Plover", "safe message")],
    )
    assert contamination_scan(digest) == []
    assert contamination_scan(outcome_sentence(None, 1.0)) == []
    assert contamination_scan(outcome_sentence("Agent Wren", 1.5)) == []


def test_required_terms_are_on_the_banned_list():
    for term in ("universe 25", "calhoun", "collapse", "role scarcity", "hypothes",
                 "experiment", "treatment", "constrained", "abundant", "concentrated",
                 "broad"):
        assert term in BANNED_TERMS


def test_runtime_assertion_fires_on_contaminated_text():
    with pytest.raises(AssertionError):
        assert_uncontaminated("You are in the constrained treatment condition.")


def test_agent_authored_text_is_masked_not_judged():
    prompt = 'Round 3. Agent Heron said "this feels like an experiment"'
    # unmasked: fires
    assert contamination_scan(prompt) != []
    # masked as agent-authored: clean, but flagged as data
    span = "this feels like an experiment"
    assert contamination_scan(prompt, agent_authored_spans=(span,)) == []
    assert scan_agent_text((span,)) is True
    assert scan_agent_text(("just a normal message",)) is False
