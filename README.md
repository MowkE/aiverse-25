# universe25-abm

Transparent, deterministic agent-based model for the flagship experiment of the Universe 25 AI
research program: **"When Resources Are Abundant but Roles Are Scarce: A Factorial Experiment in
Artificial Societies."**

A balanced 2×2 factorial (material resources: constrained/abundant × role access:
concentrated/broad) over 8-agent societies. The independently seeded run is the experimental unit.
No LLMs, no external APIs — this is Study 1: mechanism mapping and statistical infrastructure.

Read these before touching anything:

- [docs/SPEC.md](docs/SPEC.md) — state variables, transition rules, invariants, hypothesis structure
- [docs/DECISIONS.md](docs/DECISIONS.md) — unresolved scientific choices needing sign-off
- [docs/VALIDATION.md](docs/VALIDATION.md) — stress-test findings and the fixes applied
- [docs/SELF_PROMPT.md](docs/SELF_PROMPT.md) — the prompt this build was executed under

## Setup

Requires Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Note: if this repo lives inside iCloud Drive, consider `export UV_PROJECT_ENVIRONMENT=~/.venvs/universe25-abm`
before `uv sync` to keep the virtualenv out of cloud sync.

## Reproduction commands

```bash
# All checks
uv run pytest

# One run, printed summary
uv run universe25 run-one --cell abundant:concentrated --seed 7

# Balanced smoke batch (4 cells x 3 paired seeds), writes outputs/smoke/
uv run universe25 run-batch --config configs/smoke.toml

# Full batch
uv run universe25 run-batch --config configs/default.toml

# Metric validation on a batch output
uv run universe25 validate --summary outputs/smoke/run_summary.csv

# Cell means, contrasts, interaction, bootstrap CIs
uv run universe25 analyze --summary outputs/smoke/run_summary.csv

# Figures
uv run universe25 figures --summary outputs/smoke/run_summary.csv --out outputs/smoke/figures

# Simulation-based power analysis from a pilot summary
uv run universe25 power --summary outputs/pilot/run_summary.csv
```

Outputs: tidy event log (Parquet: `run_id, seed, cell, round, agent_id, action, value…`) and a
run-level summary (CSV + Parquet). Every seed and resolved config is recorded alongside outputs.

## Guardrails

- Treatments change the environment only; behavioral code is identical across cells (tested).
- Agent-turns are never treated as independent replicates; all inference is run-level.
- `random` and `material_only` agent policies are falsification controls: the role-access effect
  must vanish for them (tested).
- No pattern is called "collapse" anywhere in this codebase.
