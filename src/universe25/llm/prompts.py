"""Versioned prompt templates + contamination policy (docs/LLM_DESIGN.md §7).

System prompts are identical across cells except the factual income slot.
The chair role is described identically in both access arms; the schedule is
experienced, not described (open decision L2). Nothing here may mention the
study framing: see BANNED_TERMS and the contamination test/runtime scan.

TEMPLATE_VERSION must be bumped whenever any agent-visible text changes; the
call cache stores a prompt hash and refuses to resume across silent drift.
"""

from __future__ import annotations

from ..config import EconomyConfig
from .config import LLMRunConfig

TEMPLATE_VERSION = "llm-t1"

# Case-insensitive substrings that may never appear in experimenter-authored
# agent-visible text (study framing, treatment labels, expected behavior).
BANNED_TERMS = (
    "universe 25",
    "universe25",
    "calhoun",
    "collapse",
    "behavioral sink",
    "role scarcity",
    "scarcity",
    "hypothes",
    "experiment",
    "treatment",
    "condition",
    "constrained",
    "abundant",
    "abundance",
    "concentrated",
    "concentration",
    "broad",
    "factorial",
    "manipulat",
)


def income_description(resources: str, eco: EconomyConfig) -> str:
    """The only cell-dependent slot in the system prompt (factual income facts)."""
    if resources == "constrained":
        return (
            f"Each round you receive an income drawn between {eco.endow_lo:.1f} and "
            f"{eco.endow_hi:.1f} units; the exact amount varies from round to round."
        )
    return f"Each round you receive a fixed income of {eco.abundant_endowment:.0f} units."


def system_prompt(name: str, resources: str, cfg: LLMRunConfig) -> str:
    eco = cfg.economy
    return f"""You are {name}, one of {cfg.n_agents} members of a small group that meets for a series of rounds.

Income and staying active:
{income_description(resources, eco)}
Staying active costs {eco.survival_cost:.1f} units per round, deducted automatically. If your balance is below {eco.survival_cost:.1f} at the start of a round, you sit that round out: you cannot speak, decide, or give that round, but you keep your balance and rejoin once you can afford it.

Speaking up:
Each round, active members may speak up. Speaking up costs {eco.participation_cost:.2f} units and lets you suggest one of three joint projects (option 0, 1, or 2) together with a short public message (at most {cfg.message_max_chars} characters), visible to all members exactly as you write it.

The chair:
Each round exactly one member holds the chair; the chair for the round is announced. The chair decides which submitted suggestion, if any, the group adopts. This matters: if a suggestion is adopted, every unit given to the joint fund that round is multiplied at a higher rate than if none is adopted.

Giving:
After the chair's decision, each active member chooses how much to give to the joint fund, up to {eco.contribution_cap:.1f} units (and at most your balance). The multiplied fund is shared equally among all {cfg.n_agents} members, whether or not they gave.

Always reply with a single JSON object in exactly the requested format, and nothing else."""


def public_phase_prompt(
    round_index: int,
    balance: float,
    chair_name: str,
    memory_text: str,
    cfg: LLMRunConfig,
) -> str:
    eco = cfg.economy
    return f"""Round {round_index + 1}. Your balance: {balance:.2f} units. This round's chair: {chair_name}.

{memory_text}

Decide whether to speak up this round (cost {eco.participation_cost:.2f} units). If you speak up, pick the project option you suggest (0, 1, or 2) and write your public message (at most {cfg.message_max_chars} characters). If you do not speak up, set participate to false, set proposal_type to the option you would favor anyway, and set public_message to an empty string.

Reply with JSON: {{"participate": true or false, "proposal_type": 0 or 1 or 2, "public_message": "..."}}"""


def decision_prompt(
    round_index: int,
    balance: float,
    submissions: list[tuple[str, int, str]],
    rate_adopt: float,
    rate_none: float,
    memory_text: str,
) -> str:
    lines = [
        f"[{i}] {who}: option {ptype} — \"{msg}\""
        for i, (who, ptype, msg) in enumerate(submissions)
    ]
    listing = "\n".join(lines)
    return f"""Round {round_index + 1}. You hold the chair this round. Your balance: {balance:.2f} units.

{memory_text}

Suggestions submitted this round:
{listing}

As chair, choose which suggestion the group adopts. Adopting any suggestion sets this round's rate on the joint fund to {rate_adopt:.2f}; adopting none leaves it at {rate_none:.2f}.

Reply with JSON: {{"adopt_index": k}} where k is one of the bracketed numbers above, or -1 to adopt none."""


def contribution_prompt(
    round_index: int,
    balance: float,
    outcome_sentence: str,
    memory_text: str,
    cfg: LLMRunConfig,
) -> str:
    eco = cfg.economy
    return f"""Round {round_index + 1}. Your balance: {balance:.2f} units.
{outcome_sentence}

{memory_text}

Choose what fraction of the maximum {eco.contribution_cap:.1f} units you give to the joint fund this round (you can never give more than your balance).

Reply with JSON: {{"contribution_fraction": x}} where x is a number between 0 and 1."""


def outcome_sentence(adopted_author_name: str | None, multiplier: float) -> str:
    if adopted_author_name is None:
        return f"The chair adopted no suggestion; this round's rate on the joint fund is {multiplier:.2f}."
    return (
        f"The chair adopted {adopted_author_name}'s suggestion; "
        f"this round's rate on the joint fund is {multiplier:.2f}."
    )


def report_prompt(memory_text: str) -> str:
    return f"""Please answer three questions about your time in this group so far.

{memory_text}

- confidence: how well do you feel you understand how this group works?
- perceived_efficacy: how much have your own actions influenced what the group does?
- legitimacy_rating: how fair do you consider the way this group makes its decisions?

Reply with JSON: {{"confidence": x, "perceived_efficacy": y, "legitimacy_rating": z}}, each a number between 0 and 1."""


# --- contamination scanning ---------------------------------------------------


def contamination_scan(text: str, agent_authored_spans: tuple[str, ...] = ()) -> list[str]:
    """Return banned terms present in experimenter-authored text.

    Agent-authored spans (public messages quoted into prompts) are masked out
    before scanning: they are data, not experimenter framing. A banned term in
    an agent-authored span is flagged separately by the orchestrator.
    """
    masked = text
    for span in agent_authored_spans:
        if span:
            masked = masked.replace(span, "")
    low = masked.lower()
    return [term for term in BANNED_TERMS if term in low]


def scan_agent_text(spans: tuple[str, ...]) -> bool:
    """True if any agent-authored span contains a banned term (logged as data)."""
    joined = " ".join(spans).lower()
    return any(term in joined for term in BANNED_TERMS)


def assert_uncontaminated(text: str, agent_authored_spans: tuple[str, ...] = ()) -> None:
    found = contamination_scan(text, agent_authored_spans)
    if found:
        raise AssertionError(
            f"banned terms in experimenter-authored agent-visible text: {found}"
        )


# --- worst-case example renders (contamination test + cost estimator) ---------


def example_prompts(cfg: LLMRunConfig, resources: str) -> dict[str, tuple[str, str]]:
    """Worst-case (longest plausible) render of every template for one cell."""
    filler_msg = "x" * cfg.message_max_chars
    memory_lines = [
        (
            "Across 39 completed rounds you spoke up 39 times, chaired 39 rounds, "
            "and had your own suggestion adopted 39 times."
        ),
        "Recent rounds:",
    ]
    digest = (
        "Agent Kestrel chaired; Agent Sparrow's suggestion was adopted; the pooled fund "
        "paid 24.00 (rate 1.50), 3.00 to each member; you spoke up and gave 2.00; "
        "your balance is now 999.99. Messages: "
        + "; ".join(f'Agent Heron said "{filler_msg}"' for _ in range(cfg.n_agents - 1))
    )
    memory_lines.extend(f"Round {r}: {digest}" for r in range(1, cfg.memory_window + 1))
    memory_text = "\n".join(memory_lines)

    sys = system_prompt("Agent Kestrel", resources, cfg)
    submissions = [("Agent Heron", 2, filler_msg) for _ in range(cfg.n_agents)]
    return {
        "public": (sys, public_phase_prompt(39, 9999.99, "Agent Tern", memory_text, cfg)),
        "decision": (
            sys,
            decision_prompt(39, 9999.99, submissions, cfg.economy.m_coord, cfg.economy.m_base,
                            memory_text),
        ),
        "contribution": (
            sys,
            contribution_prompt(
                39, 9999.99,
                outcome_sentence("Agent Sparrow", cfg.economy.m_coord),
                memory_text, cfg,
            ),
        ),
        "report": (sys, report_prompt(memory_text)),
    }
