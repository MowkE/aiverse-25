#!/usr/bin/env bash
# End-to-end smoke: batch -> validate -> analyze -> figures.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run universe25 run-batch --config configs/smoke.toml
uv run universe25 validate --summary outputs/smoke/run_summary.csv
uv run universe25 analyze --summary outputs/smoke/run_summary.csv --boot 1000
uv run universe25 figures --summary outputs/smoke/run_summary.csv --out outputs/smoke/figures
