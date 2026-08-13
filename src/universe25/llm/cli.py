"""`universe25-llm` command line: estimate | smoke (mock) | run-batch (guarded).

No subcommand ever spends money without --confirm-budget: `estimate` makes no
calls, `smoke` forces the mock provider, and `run-batch` with a real provider
aborts unless the estimate fits inside an explicitly confirmed dollar budget.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

from ..validate import validate_summary
from .budget import BudgetError, BudgetGuard
from .config import load_llm_batch_config
from .estimate import estimate_run, format_estimate
from .orchestrator import run_llm_batch
from .providers import MockProvider, make_provider


def _print_cell_means(summary) -> None:
    print(
        summary.groupby(["resources", "access"])[
            ["participation_rate", "output_norm", "influence_nhhi"]
        ].mean()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="universe25-llm")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("estimate", help="print calls/tokens/dollars per run and per batch")
    p1.add_argument("--config", required=True)

    p2 = sub.add_parser("smoke", help="mock end-to-end smoke batch (never calls an API)")
    p2.add_argument("--config", default="configs/llm_smoke.toml")
    p2.add_argument("--out", default=None)

    p3 = sub.add_parser("run-batch", help="run a batch; real providers require --confirm-budget")
    p3.add_argument("--config", required=True)
    p3.add_argument("--out", default=None)
    p3.add_argument(
        "--confirm-budget", type=float, default=None, metavar="DOLLARS",
        help="explicit spending confirmation; aborts if the estimate exceeds it",
    )

    args = parser.parse_args(argv)

    if args.command == "estimate":
        cfg = load_llm_batch_config(args.config)
        print(format_estimate(cfg))
        return 0

    if args.command == "smoke":
        cfg = load_llm_batch_config(args.config)
        if cfg.run.provider != "mock":
            cfg = dataclasses.replace(cfg, run=dataclasses.replace(cfg.run, provider="mock"))
        provider = MockProvider()
        summary = run_llm_batch(cfg, provider, output_dir=args.out)
        out = Path(args.out if args.out else cfg.output_dir)
        print(f"{len(summary)} mock runs -> {out} (no API calls were made)")
        _print_cell_means(summary)
        failures = validate_summary(summary)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print("PASS: all metric bounds and invariants hold")
        return 0

    if args.command == "run-batch":
        cfg = load_llm_batch_config(args.config)
        if cfg.run.provider == "mock":
            summary = run_llm_batch(cfg, MockProvider(), output_dir=args.out)
            print(f"{len(summary)} mock runs complete (no API calls were made)")
            _print_cell_means(summary)
            return 0

        est = estimate_run(cfg.run)
        batch_cost = est.cost(cfg.run.model) * cfg.n_pairs * 4
        if cfg.run.provider == "claude-cli":
            # Subscription-funded shakedown: zero marginal dollars, but still
            # gated behind an explicit --confirm-budget acknowledgement.
            batch_cost = 0.0
            print(
                "NOTE: claude-cli is a subscription-funded SHAKEDOWN provider. "
                "Marginal cost $0; results are excluded from preregistered "
                "analyses (DECISIONS D15)."
            )
        print(format_estimate(cfg))
        guard = BudgetGuard(model=cfg.run.model)
        try:
            if args.confirm_budget is None:
                guard.authorize_estimate(batch_cost)  # raises BudgetNotConfirmedError
            guard.arm(args.confirm_budget)
            guard.authorize_estimate(batch_cost)
            provider = make_provider(cfg.run.provider, cfg.run.model, guard)
            summary = run_llm_batch(cfg, provider, output_dir=args.out)
        except BudgetError as exc:
            print(f"ABORT: {exc}", file=sys.stderr)
            return 2
        print(
            f"{len(summary)} runs complete; spent ~${guard.spent_usd:.2f} "
            f"of confirmed ${guard.confirmed_budget_usd:.2f} "
            f"({guard.calls_made} paid calls)"
        )
        _print_cell_means(summary)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
