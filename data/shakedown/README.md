# Shakedown Archive — 2026-08-13

> **EXPLORATORY ENGINEERING SHAKEDOWN. NOT PREREGISTERED. NOT CONFIRMATORY EVIDENCE.**
> Four societies = **four experimental units**, regardless of the 600 underlying model calls.
> Directional patterns below must not be described as strong evidence for any hypothesis
> (DECISIONS.md D15, D16).

## What this is

The first execution of the Study 2 orchestrator against a real language model, funded by the
researcher's Claude subscription at $0 marginal cost. Purpose: integration testing, schema-
compliance measurement, and qualitative behavior preview — never analysis data.

## Provenance

| Field | Value |
|---|---|
| Model | claude-haiku-4-5 via Claude Code CLI (headless `claude -p`) |
| Claude Code version | 2.1.229 |
| Code version | 0.1.0+2a0d537 (see manifest.json) |
| Config | config.toml (master seed 813202601; 1 pair × 4 cells × 10 rounds; template llm-t1) |
| Provider | `claude-cli` (src/universe25/llm/providers/claude_cli.py) |
| Known contamination | CLI injects ~24K tokens/call of uncontrolled harness scaffolding around our prompts — the disqualifying property (D15) |
| Interruptions | 1 timeout crash (logs/crash1_timeout.log), 1 manual stop during quota throttle (logs/crash2_manual_stop.log); both resumed byte-exactly from llm_cache/ |

## Engineering scorecard (the shakedown's actual purpose): PASS

600/600 calls valid on first attempt · 0 retries · 0 invalid-after-retries · 0 contamination
flags · 15.2M input / 1.54M output tokens · cache/resume proven twice in live failures ·
`universe25 validate` PASS on the run summary (manipulation check included).

## Four-society descriptive table (n = 1 run per cell, 10 rounds)

| Cell | Participation | Output (norm.) | Influence nHHI |
|---|---|---|---|
| abundant / broad | 0.988 | 0.860 | 0.057 |
| abundant / concentrated | 0.900 | 0.891 | 0.794 |
| constrained / broad | 0.200 | 0.322 | 0.044 |
| constrained / concentrated | 0.153 | 0.067 | 0.811 |

Qualitative notes: agents produced enthusiastic cooperative messages while contributing little in
constrained cells (talk-vs-action gap); the role-access manipulation clearly bites (nHHI).

## The finding that matters: ceiling effect (D16)

Real LLM agents respond to the material condition far more strongly than the ABM's rule agents:
abundant cells sit at ~0.90–0.99 participation, leaving almost no headroom for the access effect.
Without recalibration of the participation-cost/resource relationship, Study 2's primary contrast
could be masked. See docs/CALIBRATION_PROTOCOL.md for the response.

## Files

`llm_cache/*.jsonl` — all 600 calls (validity, retries, tokens, latency, parsed actions,
prompt SHA-256). `events.parquet`, `llm_calls.parquet`, `reports.parquet`, `run_summary.*` —
orchestrator outputs. `manifest.json` — seeds, pseudonyms, code version. `config.json` —
resolved config. `logs/` — interruption and completion logs.
