#!/usr/bin/env bash
# Study 2 mock smoke: end-to-end run of the LLM orchestrator with the
# deterministic MockProvider. Makes zero API calls and spends zero dollars.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run universe25-llm estimate --config configs/llm_smoke.toml
echo
uv run universe25-llm smoke --config configs/llm_smoke.toml
