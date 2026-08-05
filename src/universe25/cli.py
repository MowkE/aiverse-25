"""Command-line interface. See README for reproduction commands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .analysis import full_report
from .config import CELLS, RunConfig, load_batch_config
from .power import power_report
from .runner import run_batch, run_one
from .validate import validate_summary


def _parse_cell(text: str) -> tuple[str, str]:
    resources, _, access = text.partition(":")
    if (resources, access) not in CELLS:
        valid = ", ".join(f"{r}:{a}" for r, a in CELLS)
        raise argparse.ArgumentTypeError(f"cell must be one of: {valid}")
    return resources, access


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="universe25")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("run-one", help="single run, printed summary")
    p1.add_argument("--cell", type=_parse_cell, required=True, help="resources:access, e.g. abundant:concentrated")
    p1.add_argument("--seed", type=int, default=0)
    p1.add_argument("--pair", type=int, default=0)
    p1.add_argument("--rounds", type=int, default=40)

    p2 = sub.add_parser("run-batch", help="balanced batch from a TOML config")
    p2.add_argument("--config", required=True)
    p2.add_argument("--out", default=None)

    p3 = sub.add_parser("validate", help="metric bounds and invariants on a summary")
    p3.add_argument("--summary", required=True)

    p4 = sub.add_parser("analyze", help="cell means, contrasts, interaction, bootstrap CIs")
    p4.add_argument("--summary", required=True)
    p4.add_argument("--boot", type=int, default=2000)

    p5 = sub.add_parser("figures", help="figures from batch outputs")
    p5.add_argument("--summary", required=True)
    p5.add_argument("--out", default="outputs/figures")

    p6 = sub.add_parser("power", help="simulation-based power analysis from a pilot summary")
    p6.add_argument("--summary", required=True)
    p6.add_argument("--sims", type=int, default=1000)

    args = parser.parse_args(argv)

    if args.command == "run-one":
        resources, access = args.cell
        cfg = RunConfig(n_rounds=args.rounds)
        _, summary = run_one(cfg, resources, access, args.pair, args.seed)
        for key, value in summary.items():
            print(f"{key}: {value}")
        return 0

    if args.command == "run-batch":
        cfg = load_batch_config(args.config)
        summary = run_batch(cfg, output_dir=args.out)
        out = Path(args.out if args.out else cfg.output_dir)
        print(f"{len(summary)} runs -> {out}")
        print(summary.groupby(["resources", "access"])[["participation_rate", "output_norm"]].mean())
        return 0

    if args.command == "validate":
        failures = validate_summary(pd.read_csv(args.summary))
        if failures:
            for f in failures:
                print(f"FAIL: {f}")
            return 1
        print("PASS: all metric bounds and invariants hold")
        return 0

    if args.command == "analyze":
        summary = pd.read_csv(args.summary)
        report = full_report(summary, n_boot=args.boot)
        pd.set_option("display.width", 160)
        for name, table in report.items():
            print(f"\n== {name} ==")
            print(table.to_string(index=False))
        return 0

    if args.command == "figures":
        summary_path = Path(args.summary)
        summary = pd.read_csv(summary_path)
        events = pd.read_parquet(summary_path.parent / "events.parquet")
        from .figures import make_all_figures

        paths = make_all_figures(summary, events, args.out)
        for p in paths:
            print(p)
        return 0

    if args.command == "power":
        summary = pd.read_csv(args.summary)
        print(power_report(summary, n_sims=args.sims).to_string(index=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
