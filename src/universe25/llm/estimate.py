"""Cost estimation: renders the real templates so estimates track edits."""

from __future__ import annotations

from ..config import RESOURCE_LEVELS
from .config import LLMBatchConfig, LLMRunConfig
from .pricing import (
    CANDIDATE_MODELS,
    OUTPUT_TOKENS_BY_PHASE,
    PhaseEstimate,
    RunEstimate,
    estimate_tokens,
)
from .prompts import example_prompts


def estimate_run(cfg: LLMRunConfig) -> RunEstimate:
    """Upper-bound per-run estimate (all agents active every round)."""
    per_phase_in: dict[str, int] = {}
    for resources in RESOURCE_LEVELS:
        for phase, (system, user) in example_prompts(cfg, resources).items():
            tokens = estimate_tokens(system) + estimate_tokens(user)
            per_phase_in[phase] = max(per_phase_in.get(phase, 0), tokens)

    n, rounds = cfg.n_agents, cfg.n_rounds
    if cfg.report_rounds == "none":
        report_calls = 0
    elif cfg.report_rounds == "last":
        report_calls = n
    else:
        report_calls = n * rounds

    phases = (
        PhaseEstimate("public", n * rounds, per_phase_in["public"],
                      OUTPUT_TOKENS_BY_PHASE["public"]),
        PhaseEstimate("decision", rounds, per_phase_in["decision"],
                      OUTPUT_TOKENS_BY_PHASE["decision"]),
        PhaseEstimate("contribution", n * rounds, per_phase_in["contribution"],
                      OUTPUT_TOKENS_BY_PHASE["contribution"]),
        PhaseEstimate("report", report_calls, per_phase_in["report"],
                      OUTPUT_TOKENS_BY_PHASE["report"]),
    )
    return RunEstimate(phases)


def format_estimate(cfg: LLMBatchConfig) -> str:
    est = estimate_run(cfg.run)
    n_runs = cfg.n_pairs * 4
    lines = [
        (
            f"Per-run upper bound ({cfg.run.n_agents} agents x {cfg.run.n_rounds} rounds, "
            f"report_rounds={cfg.run.report_rounds}):"
        ),
        f"  {'phase':<13}{'calls':>7}{'in tok/call':>13}{'out tok/call':>14}",
    ]
    for p in est.phases:
        lines.append(
            f"  {p.phase:<13}{p.calls:>7}{p.input_tokens_per_call:>13}"
            f"{p.output_tokens_per_call:>14}"
        )
    lines.append(
        f"  total: {est.calls} calls, ~{est.input_tokens:,} input tokens, "
        f"~{est.output_tokens:,} output tokens per run (incl. retry allowance)"
    )
    lines.append(f"Batch: {n_runs} runs ({cfg.n_pairs} pairs x 4 cells)")
    lines.append("Estimated cost (see universe25/llm/pricing.py for the price table):")
    models = [cfg.run.model] + [m for m in CANDIDATE_MODELS if m != cfg.run.model]
    for model in models:
        try:
            per_run = est.cost(model)
        except KeyError:
            continue
        marker = "  <- configured model" if model == cfg.run.model else ""
        lines.append(
            f"  {model:<22} ${per_run:>8.2f} per run   ${per_run * n_runs:>10.2f} "
            f"per batch{marker}"
        )
    return "\n".join(lines)
