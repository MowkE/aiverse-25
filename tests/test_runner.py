"""End-to-end batch execution and output artifacts."""

import json

import pandas as pd

from universe25.config import BatchConfig, RunConfig
from universe25.runner import run_batch
from universe25.validate import validate_summary


def test_batch_outputs_and_balance(tmp_path):
    cfg = BatchConfig(master_seed=11, n_pairs=2, run=RunConfig(n_rounds=12))
    summary = run_batch(cfg, output_dir=tmp_path)

    assert len(summary) == 8
    assert summary.groupby(["resources", "access"]).size().nunique() == 1

    for name in ("events.parquet", "traits.parquet", "run_summary.csv",
                 "run_summary.parquet", "config.json"):
        assert (tmp_path / name).exists(), name

    events = pd.read_parquet(tmp_path / "events.parquet")
    assert set(events["run_id"].unique()) == set(summary["run_id"])

    with open(tmp_path / "config.json") as f:
        recorded = json.load(f)
    assert recorded["master_seed"] == 11
    assert recorded["run"]["behavior"]["policy"] == "heterogeneous"


def test_full_smoke_batch_is_valid(tmp_path):
    cfg = BatchConfig(master_seed=20260805, n_pairs=3, run=RunConfig(n_rounds=40))
    summary = run_batch(cfg, output_dir=tmp_path)
    assert validate_summary(summary) == []
