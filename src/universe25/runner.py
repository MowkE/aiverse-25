"""Single-run and balanced-batch execution with full provenance recording."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import CELLS, BatchConfig, RunConfig, config_to_dict
from .environment import RunResult, simulate_run
from .metrics import summarize_run
from .rng import spawn_pair_streams


def run_one(cfg: RunConfig, resources: str, access: str, pair: int, master_seed: int) -> tuple[RunResult, dict]:
    result = simulate_run(cfg, resources, access, pair, master_seed)
    return result, summarize_run(result.events)


def run_batch(cfg: BatchConfig, output_dir: str | Path | None = None) -> pd.DataFrame:
    """Balanced batch: every pair index is simulated in all four cells with
    shared trait/structure/dynamics streams (common random numbers)."""
    out = Path(output_dir if output_dir is not None else cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    all_events: list[pd.DataFrame] = []
    all_traits: list[pd.DataFrame] = []
    summaries: list[dict] = []
    for pair in range(cfg.n_pairs):
        for resources, access in CELLS:
            streams = spawn_pair_streams(cfg.master_seed, pair)
            result = simulate_run(cfg.run, resources, access, pair, cfg.master_seed, streams=streams)
            all_events.append(result.events)
            all_traits.append(result.traits)
            summaries.append(summarize_run(result.events))

    events = pd.concat(all_events, ignore_index=True)
    traits = pd.concat(all_traits, ignore_index=True)
    summary = pd.DataFrame(summaries)

    events.to_parquet(out / "events.parquet", index=False)
    traits.to_parquet(out / "traits.parquet", index=False)
    summary.to_csv(out / "run_summary.csv", index=False)
    summary.to_parquet(out / "run_summary.parquet", index=False)
    with open(out / "config.json", "w") as f:
        json.dump(config_to_dict(cfg), f, indent=2)
    return summary
