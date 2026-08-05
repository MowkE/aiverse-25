"""Run orchestrator for Study 2 (docs/LLM_DESIGN.md §6).

Code owns environment state, treatment assignment, resources, authority,
scoring, transitions, logging, and termination. LLM agents only choose:
public-phase action, the decider's adoption choice, contribution fraction,
and (secondary) structured reports. Environment mechanics reuse Study 1
components: decider_schedule, the endowment process, survival, stakes_bind,
multiplier/shock, payouts, impact, and metrics.summarize_run on an events
DataFrame with the ABM's columns.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import CELLS
from ..environment import decider_schedule, run_id_for
from ..metrics import summarize_run
from ..rng import spawn_pair_streams
from .cache import CachedCall, CallCache, call_key, prompt_hash
from .config import LLMBatchConfig, LLMRunConfig, llm_config_to_dict
from .memory import AgentMemory, assign_pseudonyms, round_digest
from .prompts import (
    TEMPLATE_VERSION,
    assert_uncontaminated,
    contribution_prompt,
    decision_prompt,
    outcome_sentence,
    public_phase_prompt,
    report_prompt,
    scan_agent_text,
    system_prompt,
)
from .providers.base import LLMRequest, Provider
from .schemas import (
    contribution_schema,
    decision_schema,
    public_phase_schema,
    report_schema,
    to_api_schema,
    validate_action,
)

PHASE_INDEX = {"public": 0, "decision": 1, "contribution": 2, "report": 3}
SCHEMA_NAME = {
    "public": "public_phase",
    "decision": "decision",
    "contribution": "contribution",
    "report": "report",
}
CELL_INDEX = {cell: i for i, cell in enumerate(CELLS)}
# Salts for LLM-specific seed streams (recorded; disjoint from spawn_pair_streams).
NAMES_SALT = 1001
ORDER_SALT = 1002

RETRY_SUFFIX = (
    "\n\nYour previous reply was not in the requested format ({error}). "
    "Reply again with exactly one JSON object in the requested format and nothing else."
)


def per_call_seed(
    master_seed: int, pair: int, cell_idx: int, round_index: int, agent_id: int, phase: str
) -> int:
    ss = np.random.SeedSequence(
        [master_seed, pair, cell_idx, round_index, agent_id, PHASE_INDEX[phase]]
    )
    return int(ss.generate_state(1)[0])


def code_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        pkg = version("universe25-abm")
    except (ImportError, PackageNotFoundError):  # pragma: no cover
        pkg = "unknown"
    try:
        git = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
            cwd=Path(__file__).resolve().parent,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        git = ""
    return f"{pkg}+{git}" if git else pkg


@dataclass(frozen=True)
class LLMRunResult:
    events: pd.DataFrame
    calls: pd.DataFrame
    reports: pd.DataFrame
    pseudonyms: list[str]


class _CallEngine:
    """Cache-aware, retry-aware, contamination-checked call resolution."""

    def __init__(
        self,
        cfg: LLMRunConfig,
        provider: Provider,
        cache: CallCache,
        run_meta: dict,
        log_rows: list[dict],
        version_string: str,
    ):
        self.cfg = cfg
        self.provider = provider
        self.cache = cache
        self.run_meta = run_meta
        self.log_rows = log_rows
        self.version_string = version_string

    def resolve(
        self,
        phase: str,
        round_index: int,
        agent_id: int,
        system: str,
        user: str,
        full_schema: dict,
        metadata: dict,
        agent_spans: tuple[str, ...] = (),
    ) -> CachedCall:
        cfg = self.cfg
        # Runtime contamination assertion on experimenter-authored text; text
        # authored by agents (quoted public messages) is masked, not judged.
        assert_uncontaminated(system + "\n" + user, agent_spans)

        seed = per_call_seed(
            self.run_meta["master_seed"], self.run_meta["pair"],
            self.run_meta["cell_idx"], round_index, agent_id, phase,
        )
        key = call_key(
            self.run_meta["run_id"], round_index, agent_id, phase,
            cfg.template_version, cfg.model, seed,
        )
        h = prompt_hash(system, user)
        cached = self.cache.lookup(key, h)
        if cached is not None:
            self._log(cached, phase, round_index, agent_id, system, user, cache_hit=True)
            return cached

        api_schema = to_api_schema(full_schema)
        retries = 0
        parsed: dict | None = None
        valid = False
        text = ""
        in_tok = out_tok = 0
        latency = 0.0
        request_id: str | None = None
        error: str | None = None
        for attempt in range(cfg.max_schema_retries + 1):
            user_attempt = user if attempt == 0 else user + RETRY_SUFFIX.format(error=error)
            request = LLMRequest(
                system=system,
                user=user_attempt,
                schema_name=SCHEMA_NAME[phase],
                api_schema=api_schema,
                model=cfg.model,
                max_tokens=cfg.max_tokens,
                temperature=cfg.temperature,
                effort=cfg.effort,
                thinking=cfg.thinking,
                seed=seed,
                metadata=metadata,
            )
            response = self.provider.complete(request)
            text = response.text
            in_tok += response.input_tokens
            out_tok += response.output_tokens
            latency += response.latency_ms
            request_id = response.request_id
            outcome = validate_action(text, full_schema)
            retries = attempt
            if outcome.valid:
                parsed, valid = outcome.parsed, True
                break
            error = outcome.error

        rec = CachedCall(
            key=key,
            prompt_sha256=h,
            response_text=text,
            parsed=parsed,
            valid=valid,
            retries=retries,
            invalid_after_retries=not valid,
            contamination_flag=scan_agent_text((text, *agent_spans)),
            input_tokens=in_tok,
            output_tokens=out_tok,
            latency_ms=latency,
            provider=self.provider.name,
            model=cfg.model,
            request_id=request_id,
        )
        self.cache.store(rec)
        self._log(rec, phase, round_index, agent_id, system, user, cache_hit=False)
        return rec

    def _log(
        self, rec: CachedCall, phase: str, round_index: int, agent_id: int,
        system: str, user: str, cache_hit: bool,
    ) -> None:
        self.log_rows.append({
            "run_id": self.run_meta["run_id"],
            "pair": self.run_meta["pair"],
            "resources": self.run_meta["resources"],
            "access": self.run_meta["access"],
            "round": round_index,
            "agent_id": agent_id,
            "phase": phase,
            "template_version": self.cfg.template_version,
            "model": rec.model,
            "provider": rec.provider,
            "temperature": self.cfg.temperature,
            "effort": self.cfg.effort,
            "thinking": self.cfg.thinking,
            "seed": int(rec.key.rsplit("|", 1)[-1]),
            "prompt_system": system,
            "prompt_user": user,
            "response_text": rec.response_text,
            "valid": rec.valid,
            "retries": rec.retries,
            "invalid_after_retries": rec.invalid_after_retries,
            "contamination_flag": rec.contamination_flag,
            "cache_hit": cache_hit,
            "input_tokens": rec.input_tokens,
            "output_tokens": rec.output_tokens,
            "latency_ms": rec.latency_ms,
            "request_id": rec.request_id,
            "code_version": self.version_string,
        })


def simulate_llm_run(
    cfg: LLMRunConfig,
    resources: str,
    access: str,
    pair: int,
    master_seed: int,
    provider: Provider,
    cache_dir: str | Path,
    version_string: str | None = None,
) -> LLMRunResult:
    if cfg.template_version != TEMPLATE_VERSION:
        raise ValueError(
            f"config template_version {cfg.template_version!r} does not match the code's "
            f"TEMPLATE_VERSION {TEMPLATE_VERSION!r}"
        )
    n, rounds = cfg.n_agents, cfg.n_rounds
    eco = cfg.economy
    rid = run_id_for(pair, resources, access)
    version_string = version_string or code_version()

    streams = spawn_pair_streams(master_seed, pair)
    schedule = decider_schedule(access, n, rounds, streams.structure)
    rng = streams.dynamics

    names_rng = np.random.default_rng(np.random.SeedSequence([master_seed, pair, NAMES_SALT]))
    order_rng = np.random.default_rng(np.random.SeedSequence([master_seed, pair, ORDER_SALT]))
    names = assign_pseudonyms(n, names_rng)

    cache = CallCache(cache_dir, rid)
    log_rows: list[dict] = []
    run_meta = {
        "run_id": rid, "pair": pair, "master_seed": master_seed,
        "cell_idx": CELL_INDEX[(resources, access)],
        "resources": resources, "access": access,
    }
    engine = _CallEngine(cfg, provider, cache, run_meta, log_rows, version_string)

    systems = [system_prompt(names[i], resources, cfg) for i in range(n)]
    memories = [AgentMemory(name=names[i], window=cfg.memory_window) for i in range(n)]

    balance = np.zeros(n)
    shock_start = rounds // 2
    shock_end = shock_start + cfg.shock.duration if cfg.shock.enabled else shock_start

    event_rows: list[dict] = []
    report_rows: list[dict] = []

    for t in range(rounds):
        if resources == "constrained":
            endowments = rng.uniform(eco.endow_lo, eco.endow_hi, n)
        else:
            endowments = np.full(n, eco.abundant_endowment)
        balance += endowments

        active = balance >= eco.survival_cost
        balance[active] -= eco.survival_cost
        stakes_bind = balance < (eco.survival_cost + eco.participation_cost + eco.contribution_cap)

        decider = int(schedule[t])
        chair_name = names[decider]
        shock_factor = cfg.shock.multiplier_factor if shock_start <= t < shock_end else 1.0

        # --- public phase (randomized call order, recorded stream) -----------
        participated = np.zeros(n, dtype=bool)
        proposal_type = np.full(n, -1, dtype=int)
        public_noop = np.zeros(n, dtype=bool)
        messages: dict[int, str] = {}
        public_order = [int(i) for i in order_rng.permutation(n)]
        for i in public_order:
            if not active[i] or balance[i] < eco.participation_cost:
                continue
            mem_text = memories[i].render()
            spans = tuple(m for _, m in _memory_spans(memories[i]))
            user = public_phase_prompt(t, float(balance[i]), chair_name, mem_text, cfg)
            rec = engine.resolve(
                "public", t, i, systems[i], user,
                public_phase_schema(cfg.message_max_chars),
                metadata={}, agent_spans=spans,
            )
            if rec.valid:
                assert rec.parsed is not None
                if rec.parsed["participate"]:
                    participated[i] = True
                    balance[i] -= eco.participation_cost
                    proposal_type[i] = int(rec.parsed["proposal_type"])
                    messages[i] = str(rec.parsed["public_message"])
            else:
                public_noop[i] = True  # recorded no-op: did not participate

        # Submissions listed in agent-index order (call order never leaks in).
        submissions = [
            (i, proposal_type[i], messages.get(i, "")) for i in range(n) if participated[i]
        ]

        # --- binding decision -------------------------------------------------
        adopted_author = -1
        decision_noop = False
        if active[decider] and submissions:
            listing = [(names[i], int(p), m) for i, p, m in submissions]
            mem_text = memories[decider].render()
            spans = tuple(m for _, m in _memory_spans(memories[decider]))
            spans = spans + tuple(m for _, _, m in listing if m)
            user = decision_prompt(
                t, float(balance[decider]), listing,
                eco.m_coord * shock_factor, eco.m_base * shock_factor, mem_text,
            )
            rec = engine.resolve(
                "decision", t, decider, systems[decider], user,
                decision_schema(len(submissions)),
                metadata={"n_submissions": len(submissions)}, agent_spans=spans,
            )
            if rec.valid:
                assert rec.parsed is not None
                k = int(rec.parsed["adopt_index"])
                if k >= 0:
                    adopted_author = submissions[k][0]
            else:
                decision_noop = True  # recorded no-op: nothing adopted

        multiplier = (eco.m_coord if adopted_author >= 0 else eco.m_base) * shock_factor
        adopted_name = names[adopted_author] if adopted_author >= 0 else None

        # --- contribution -----------------------------------------------------
        contribution = np.zeros(n)
        affordable = np.zeros(n)
        contribution_noop = np.zeros(n, dtype=bool)
        outcome_text = outcome_sentence(adopted_name, multiplier)
        contribution_order = [int(i) for i in order_rng.permutation(n)]
        for i in contribution_order:
            if not active[i]:
                continue
            affordable[i] = min(eco.contribution_cap, balance[i])
            mem_text = memories[i].render()
            spans = tuple(m for _, m in _memory_spans(memories[i]))
            user = contribution_prompt(t, float(balance[i]), outcome_text, mem_text, cfg)
            rec = engine.resolve(
                "contribution", t, i, systems[i], user, contribution_schema(),
                metadata={}, agent_spans=spans,
            )
            if rec.valid:
                assert rec.parsed is not None
                frac = float(rec.parsed["contribution_fraction"])
                contribution[i] = min(eco.contribution_cap * frac, balance[i])
                balance[i] -= contribution[i]
            else:
                contribution_noop[i] = True  # recorded no-op: gave 0

        value = multiplier * contribution.sum()
        payout = value / n
        balance += payout

        impact = np.zeros(n)
        if active[decider]:
            impact[decider] += 1.0
        if adopted_author >= 0:
            impact[adopted_author] += 1.0

        # --- memory + events --------------------------------------------------
        for i in range(n):
            other_msgs = [(names[j], m) for j, m in sorted(messages.items()) if j != i]
            digest = round_digest(
                chair_name=chair_name,
                adopted_author_name=adopted_name,
                multiplier=multiplier,
                project_value=float(value),
                payout=float(payout),
                own_balance=float(balance[i]),
                own_participated=bool(participated[i]),
                own_contribution=float(contribution[i]),
                public_messages=other_msgs,
            )
            memories[i].record_round(
                t, digest,
                was_chair=(i == decider),
                own_adopted=(i == adopted_author),
                participated=bool(participated[i]),
            )
            event_rows.append({
                "run_id": rid, "pair": pair, "master_seed": master_seed,
                "resources": resources, "access": access, "round": t, "agent_id": i,
                "endowment": float(endowments[i]), "active": bool(active[i]),
                "stakes_bind": bool(stakes_bind[i]),
                "participated": bool(participated[i]),
                "proposal_type": int(proposal_type[i]),
                "is_decider": bool(decider == i),
                "adopted_author": adopted_author,
                "own_adopted": bool(adopted_author == i),
                "multiplier": float(multiplier),
                "contribution": float(contribution[i]),
                "affordable_max": float(affordable[i]),
                "payout": float(payout),
                "impact": float(impact[i]),
                "efficacy": float("nan"),  # ABM-internal state; no LLM analogue
                "withdrawn": False,        # ABM-internal state; no LLM analogue
                "balance_end": float(balance[i]),
                "in_shock": bool(shock_start <= t < shock_end),
                "public_message": messages.get(i, ""),
                "public_noop": bool(public_noop[i]),
                "decision_noop": bool(decision_noop and i == decider),
                "contribution_noop": bool(contribution_noop[i]),
            })

        # --- reports (secondary; never fed back into play) --------------------
        want_report = cfg.report_rounds == "all" or (
            cfg.report_rounds == "last" and t == rounds - 1
        )
        if want_report:
            for i in range(n):
                mem_text = memories[i].render()
                spans = tuple(m for _, m in _memory_spans(memories[i]))
                rec = engine.resolve(
                    "report", t, i, systems[i], report_prompt(mem_text), report_schema(),
                    metadata={}, agent_spans=spans,
                )
                row = {
                    "run_id": rid, "pair": pair, "resources": resources, "access": access,
                    "round": t, "agent_id": i, "valid": rec.valid,
                    "confidence": np.nan, "perceived_efficacy": np.nan,
                    "legitimacy_rating": np.nan,
                }
                if rec.valid and rec.parsed is not None:
                    row.update({
                        "confidence": float(rec.parsed["confidence"]),
                        "perceived_efficacy": float(rec.parsed["perceived_efficacy"]),
                        "legitimacy_rating": float(rec.parsed["legitimacy_rating"]),
                    })
                report_rows.append(row)

    return LLMRunResult(
        events=pd.DataFrame(event_rows),
        calls=pd.DataFrame(log_rows),
        reports=pd.DataFrame(report_rows),
        pseudonyms=names,
    )


def _memory_spans(memory: AgentMemory) -> list[tuple[str, str]]:
    """Agent-authored substrings inside memory digests, for contamination masking.

    Digests quote other agents' public messages verbatim; those quoted spans are
    the only agent-authored text inside experimenter-rendered prompts. We mask
    the full digest lines (cheap and safe: digests are code-generated from a
    fixed template that the template-level contamination test already covers).
    """
    return [("digest", d) for d in memory.digests]


def run_llm_batch(
    cfg: LLMBatchConfig,
    provider: Provider,
    output_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Balanced batch: every pair index simulated in all four cells."""
    out = Path(output_dir if output_dir is not None else cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cache_dir = cfg.resolved_cache_dir() if output_dir is None else str(out / "llm_cache")
    version_string = code_version()

    all_events, all_calls, all_reports, summaries = [], [], [], []
    manifest: dict[str, dict] = {}
    for pair in range(cfg.n_pairs):
        for resources, access in CELLS:
            result = simulate_llm_run(
                cfg.run, resources, access, pair, cfg.master_seed,
                provider, cache_dir, version_string,
            )
            all_events.append(result.events)
            all_calls.append(result.calls)
            if len(result.reports):
                all_reports.append(result.reports)
            summaries.append(summarize_run(result.events))
            rid = run_id_for(pair, resources, access)
            manifest[rid] = {
                "pseudonyms": result.pseudonyms,
                "names_seed": [cfg.master_seed, pair, NAMES_SALT],
                "order_seed": [cfg.master_seed, pair, ORDER_SALT],
            }

    events = pd.concat(all_events, ignore_index=True)
    calls = pd.concat(all_calls, ignore_index=True)
    summary = pd.DataFrame(summaries)

    events.to_parquet(out / "events.parquet", index=False)
    calls.to_parquet(out / "llm_calls.parquet", index=False)
    if all_reports:
        pd.concat(all_reports, ignore_index=True).to_parquet(
            out / "reports.parquet", index=False
        )
    summary.to_csv(out / "run_summary.csv", index=False)
    summary.to_parquet(out / "run_summary.parquet", index=False)
    with open(out / "config.json", "w") as f:
        json.dump(llm_config_to_dict(cfg), f, indent=2)
    with open(out / "manifest.json", "w") as f:
        json.dump({"code_version": version_string, "runs": manifest}, f, indent=2)
    return summary
