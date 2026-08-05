# LLM_EXPERIMENT — running Study 2

How to run the Study 2 LLM-agent confirmation layer: mock smoke, engineering
pilot, and (later) the frozen confirmatory batch. Design and interfaces:
[docs/LLM_DESIGN.md](LLM_DESIGN.md).

> **No real API call has been made yet.** As of this document's commit, every
> execution of this code — all tests, CI, and the smoke runs — used the
> deterministic MockProvider. No API keys exist in this environment, the
> Anthropic/OpenAI adapters have never been exercised against the network, and
> zero dollars have been spent. Prices in `src/universe25/llm/pricing.py` must
> be re-verified before the first paid call.

## 1. Mock smoke (free, deterministic, run this first)

```bash
./scripts/llm_smoke.sh
# equivalently:
uv run universe25-llm estimate --config configs/llm_smoke.toml
uv run universe25-llm smoke --config configs/llm_smoke.toml
```

Runs 1 pair × 4 cells with the MockProvider, writes
`outputs/llm_smoke/{events,llm_calls,reports,run_summary}.{parquet,csv}` plus
`config.json`, `manifest.json` (recorded seeds and pseudonym mappings) and the
call cache under `outputs/llm_smoke/llm_cache/`, prints cell means, and runs
the same `validate_summary` machinery as Study 1. The full test suite
(`uv run pytest`) covers schemas, memory, cache/resume, contamination,
orchestrator smoke, and the budget guard — all mock.

## 2. Cost estimation (free)

```bash
uv run universe25-llm estimate --config configs/llm_pilot.toml
```

Prints calls per run, input/output tokens per call by phase, and dollars per
run and per batch for the configured model and the candidate models. The
estimate is a deliberate **upper bound**: it renders the real templates with
worst-case memory (every peer writing maximum-length messages every round).
Mock-measured typical runs come in ~3–4× cheaper; budget to the upper bound.

## 3. Engineering pilot (spends money; explicitly guarded)

Pre-requisites: an `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) in the
environment, verified prices in `pricing.py`, and researcher sign-off on the
open decisions in LLM_DESIGN.md §12 (model, effort/thinking, schedule
disclosure, report cadence).

```bash
uv run universe25-llm estimate  --config configs/llm_pilot.toml   # read this first
uv run universe25-llm run-batch --config configs/llm_pilot.toml --confirm-budget <dollars>
```

Without `--confirm-budget` the command aborts before any call. It also aborts
if the estimate exceeds the confirmed amount, and the armed guard re-checks
accumulated spend before every single HTTP request, halting the batch if the
confirmation would be breached mid-run. An interrupted batch resumes from the
call cache without re-calling completed observations:
re-run the same command; cache hits are recorded in `llm_calls.parquet`.

Analyze with the Study 1 tooling (run-level, never agent-turns):

```bash
uv run universe25 validate --summary outputs/llm_pilot/run_summary.csv
uv run universe25 analyze  --summary outputs/llm_pilot/run_summary.csv
```

## 4. Frozen confirmatory batch (later; not yet specified)

Before the confirmatory batch: freeze the model id, temperature/effort/
thinking, `template_version`, all config constants, and a fresh master seed in
a new `configs/llm_confirmatory.toml`; register the analysis plan (H4
interaction primary, H1/H2 co-primary, influence concentration as manipulation
check, invalid-output and failure rates reported as results, self-reports
secondary); commit; record the freeze hash; only then run with
`--confirm-budget`. The comparison to Study 1 is sign-and-uncertainty of the
treatment contrasts — agreement validates the construct mapping for LLM-agent
societies only, nothing more.

## 5. Reproducibility statement

- Every run derives all randomness from `(master_seed, pair)` via
  `numpy SeedSequence`: environment streams are shared with Study 1
  (`spawn_pair_streams`), and LLM-layer streams (pseudonym assignment, call
  order) plus per-call seeds use recorded salts (`manifest.json`).
- Every call is logged with exact prompts, raw response, parsed action, model
  id, provider metadata, token usage, latency, retry count, template version,
  and code version (`llm_calls.parquet`), and persisted in the JSONL call
  cache keyed by `(run_id, round, agent_id, phase, template_version, model,
  seed)`.
- Replaying a completed run from its cache reproduces byte-identical events
  and summaries (enforced by `tests/llm/test_cache_resume.py`). Mock runs are
  fully deterministic end-to-end. Real-model responses are not deterministic
  across providers' backends; reproducibility for paid runs means replay-from-
  cache, which the cache guarantees (template/config drift under an unchanged
  version string raises instead of silently diverging).
- Agent-visible text never names the study, treatments, or expected behavior
  (enforced by `tests/llm/test_contamination.py` and a runtime assertion);
  agent-authored text containing such terms is flagged as data
  (`contamination_flag`), not suppressed.
