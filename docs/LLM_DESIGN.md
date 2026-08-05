# LLM_DESIGN — Study 2 LLM-agent confirmation layer

Version 0.1 (design frozen before implementation; this document was written first, then the code).
Study 2 replaces the hand-coded behavioral rules of Study 1 with LLM agents whose behavior we do
not author. Code — not the model — owns environment state, treatment assignment, resources,
authority, scoring, transitions, logging, and termination. The deterministic ABM
(`src/universe25/`) is untouched; everything new lives in `src/universe25/llm/`, `tests/llm/`,
and `scripts/llm_smoke.sh`.

## 1. Scope and non-goals

- Same 2×2 factorial as Study 1 (resources: constrained/abundant × role access:
  concentrated/broad, per docs/SPEC.md — the second factor is role *access* via the decider
  schedule, not role count). Same round structure, same run-level outcomes via
  `metrics.summarize_run`, same analysis machinery.
- H4 (interaction) is the preregistered primary; structured self-reports are secondary only
  (contamination risk, VALIDATION M1); H5/mediation is exploratory.
- No real API call is made by any test, smoke run, or default execution path. Real-provider
  paths are blocked by a budget guard requiring explicit CLI confirmation.

## 2. Module map

```
src/universe25/llm/
  config.py        LLMRunConfig / LLMBatchConfig dataclasses + TOML loading
  schemas.py       JSON Schemas + validation for the four structured actions
  providers/
    base.py        LLMRequest / LLMResponse dataclasses, Provider protocol
    mock.py        MockProvider — deterministic, seedable, used by all tests
    anthropic_provider.py  real HTTP via the anthropic SDK (guarded)
    openai_provider.py     real HTTP via httpx (guarded)
  pricing.py       editable pricing table ("prices as of <date>") + token estimators
  budget.py        BudgetGuard: arm-with-confirmed-dollars, per-call charge, abort on breach
  memory.py        per-agent rolling-window + summary memory, pseudonymous identities
  prompts.py       versioned templates, banned-terms list, contamination check
  cache.py         JSONL call cache keyed by (run_id, round, agent_id, phase,
                   template_version, model, seed); resume support
  orchestrator.py  the run loop: environment mechanics + LLM decisions + logging
  cli.py           `universe25-llm` console script: estimate | smoke | run-batch
```

## 3. Provider adapter interface

```python
@dataclass(frozen=True)
class LLMRequest:
    system: str          # system prompt (identical across cells up to factual env slots)
    user: str            # per-call user prompt
    schema_name: str     # "public_phase" | "decision" | "contribution" | "report"
    api_schema: dict     # JSON Schema passed to the provider's structured-output feature
    model: str
    max_tokens: int
    temperature: float | None   # None = omit (current Anthropic models reject sampling params)
    effort: str | None          # Anthropic output_config.effort
    thinking: str               # "disabled" | "adaptive" (Anthropic only)
    seed: int                   # per-call seed; drives MockProvider, recorded for provenance
    metadata: Mapping[str, Any] # run_id/round/agent/phase for logs; never sent to providers

@dataclass(frozen=True)
class LLMResponse:
    text: str            # raw model text (expected: one JSON object)
    model: str           # model id reported by the provider
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    request_id: str | None
    raw: Any             # provider-native payload (not persisted in tidy logs)

class Provider(Protocol):
    name: str
    is_real: bool                       # True ⇒ spends money ⇒ must hold an armed BudgetGuard
    def complete(self, request: LLMRequest) -> LLMResponse: ...
```

- **MockProvider**: deterministic function of `request.seed` and `schema_name` only (never of
  wall-clock or call order), so cache/resume tests are byte-identical. Supports fault injection
  (`invalid_first_calls`, `always_invalid`) for retry/exhaustion contract tests. `is_real=False`.
- **AnthropicProvider**: `anthropic.Anthropic(api_key=...)` with key from `ANTHROPIC_API_KEY`
  (constructor raises `MissingAPIKeyError` otherwise). Uses `messages.create` with
  `output_config={"format": {"type": "json_schema", "schema": api_schema}}` per current API
  guidance (claude-api skill). `thinking={"type": "disabled"}` by default (config field) with
  `effort` ≤ high — schema-constrained one-shot choices don't need reasoning tokens and this
  makes cost estimable; adaptive thinking is a config switch. Sampling parameters are never
  sent (rejected with 400 on Opus 5/4.8/4.7 and Sonnet 5); `temperature` stays a config field
  for provenance/OpenAI. Every `complete()` first calls `guard.precall()` and afterwards
  `guard.charge(usage)` — an unarmed guard raises before any HTTP request is built.
- **OpenAIProvider**: raw HTTP via `httpx` to `/v1/chat/completions` with
  `response_format={"type": "json_schema", ...,"strict": true}`; key from `OPENAI_API_KEY`;
  identical guard discipline.

**Model-id choices** (from the claude-api skill, cached 2026-06-24; re-verify before spending):
candidate models are `claude-opus-5` ($5/$25 per MTok), `claude-sonnet-5` ($3/$15; intro $2/$10
through 2026-08-31), `claude-haiku-4-5` ($1/$5). Default config ships `claude-sonnet-5` for the
pilot; the confirmatory model is a researcher decision (open decision L1). OpenAI ids/prices in
`pricing.py` are placeholders flagged VERIFY.

## 4. Structured action schemas (`schemas.py`)

All four schemas are JSON Schema (draft 2020-12), `additionalProperties: false`, all fields
required. Two views per schema: the **full schema** (with numeric bounds / maxLength) used for
local validation, and the **api schema** (bounds stripped) sent to providers, since Anthropic
structured outputs do not support `minimum`/`maximum`/`maxLength` — bounds are enforced locally.

| name | fields |
|---|---|
| `public_phase` | `participate: bool`, `proposal_type: enum {0,1,2}`, `public_message: str ≤ 240 chars` |
| `decision` | `adopt_index: int` — index into the round's submission list, or −1 for none (range checked locally against the actual submission count) |
| `contribution` | `contribution_fraction: number ∈ [0,1]` |
| `report` | `confidence`, `perceived_efficacy`, `legitimacy_rating` — each number ∈ [0,1] |

`decision` is required by the orchestrator flow (the binding decision is an LLM choice among
submissions) even though the starter kit lists only three; recorded as a design addition.

**Validation/retry contract**: parse JSON → validate against the full schema → range checks.
Invalid ⇒ retry with the validation error appended to the user prompt, up to
`max_schema_retries` (config, default 2 retries = 3 attempts). Every attempt is logged. After
exhaustion the action is a **recorded no-op** with `invalid_after_retries=True` — a no-op means
"did not participate" / "no adoption" / "contribution 0" / "no report". No silent substitution
of a successful action, ever; invalid-output rates are results.

## 5. Memory manager (`memory.py`)

- Stable pseudonymous identities: bird names ("Agent Kestrel", …) assigned to seat indices by a
  seeded permutation per run (recorded seed). Names carry no treatment information.
- Per-agent memory = rolling window of the last `memory_window` (default 6) round digests +
  a compact running summary (counts: rounds seen, times chaired, own proposals adopted, running
  balance trend). Digests are generated by code from environment facts (never by an LLM), so
  memory is deterministic and contamination-controlled.
- Public messages authored by *other* agents appear in digests (that is the observable social
  interaction) and are marked as agent-authored for the contamination policy (§7).
- Memory lives only inside a run object; nothing is persisted across runs and the orchestrator
  constructs fresh memories per run.

## 6. Orchestrator flow (`orchestrator.py`)

Reuses Study 1 environment logic where practical: `environment.decider_schedule` (same
structure stream ⇒ same seat permutation/rotation as the ABM for a given master seed and pair),
the same endowment process, survival rule, `stakes_bind` definition, multiplier/shock logic,
payout and impact accounting, and `metrics.summarize_run` on an events DataFrame with the same
columns (plus `public_message` and no-op flag extras; `efficacy` is NaN and `withdrawn` False —
they are ABM-internal states with no LLM analogue; recorded, not interpreted).

Per round t (same order as SPEC §5):
1. **Endowment & survival** — identical mechanics; constrained endowments drawn from the pair's
   dynamics stream exactly as in the ABM.
2. **Public phase** — every active agent with balance ≥ participation cost gets one LLM call
   (`public_phase` schema). Call order within the phase is randomized with a recorded per-round
   seed. Participation deducts the cost and registers a proposal + public message. Messages are
   visible to the decider this round and to everyone from the next round (simultaneous play
   within the round — no within-round information order effects).
3. **Binding decision** — the scheduled decider (from `decider_schedule`) — if active and at
   least one submission exists — gets one LLM call (`decision` schema) listing submissions
   (pseudonym, proposal type, message). Adoption sets multiplier `m_coord`, else `m_base`;
   shock rounds halve it. Authority is real and behavioral: the decider *chooses*; the
   environment only fixes who holds the role (this is the treatment).
4. **Contribution** — every active agent gets one LLM call (`contribution` schema) knowing the
   adoption outcome and its own balance; contribution = min(cap × fraction, balance).
5. **Feedback/state** — payouts, impact (decider + adopted author), memory digests appended.
6. **Reports** — at configured rounds (`report_rounds`: "none" | "last" | "all", default
   "last"), each agent answers the `report` schema. Secondary data; never fed back into play.

Per-call seeds are order-independent: `SeedSequence([master_seed, pair, cell_idx, round,
agent_id, phase_idx]) → uint32`, so cache keys and mock behavior are stable under any call
ordering. Seat-name mapping and call-order seeds are drawn from dedicated streams spawned from
`(master_seed, pair)` and recorded in the run manifest.

## 7. Prompts, versioning, contamination (`prompts.py`)

- `TEMPLATE_VERSION = "llm-t1"` recorded in every call-log row; changing any template text
  requires bumping it (the cache stores a prompt hash and raises on version/hash drift).
- System prompt identical across cells except two factual slots: the **income description**
  (variable income + binding survival cost vs. fixed large income) and nothing else; the
  chair/decider role is described identically in both access arms ("each round one member holds
  the chair; the chair is announced each round") and the *schedule* is experienced, not
  described (open decision L2). Factual per-round info (your balance, this round's chair, last
  round's outcome) is in the user prompt and required.
- **Banned terms** (case-insensitive) may never appear in experimenter-authored agent-visible
  text: Universe 25, Calhoun, collapse, behavioral sink, role scarcity, hypothesis, experiment,
  treatment, condition, constrained, abundant, concentrated, broad, factorial, manipulation.
- Two enforcement layers: (a) a test renders every template for every cell × phase (with
  synthetic memory) and asserts no banned term appears; (b) a runtime assertion in the
  orchestrator scans every outgoing prompt **after masking agent-authored public-message spans**
  — experimenter text must be clean; agent-authored text is data (a banned term emitted by an
  agent is logged with `contamination_flag=True`, not an error).

## 8. Cache / resume (`cache.py`)

- Append-only JSONL per run under `<output_dir>/llm_cache/<run_id>.jsonl`; each record holds the
  key `(run_id, round, agent_id, phase, template_version, model, seed)`, a SHA-256 of the first
  rendered prompt, the final raw response text, parsed action, retries used, validity flags,
  token usage, latency and provider metadata.
- On resume the orchestrator replays rounds from 0; every call first consults the cache — a hit
  (matching key *and* prompt hash) short-circuits the provider and is marked `cache_hit=True`.
  A key hit with a hash mismatch raises (template/config drift under an unchanged version
  string is a bug, not a resume). Because environment randomness is a fixed function of the
  seeds and all LLM outcomes are replayed, a resumed run's events/summary are byte-identical.

## 9. Cost estimator + budget guard (`pricing.py`, `budget.py`)

- `pricing.py` holds one editable table `PRICES: {model_id: (usd_per_mtok_in, usd_per_mtok_out)}`
  with a "prices as of" comment, and token estimation = rendered-template character counts
  (worst-case memory) / 3.5 chars-per-token + margin. The estimator *renders the real
  templates*, so estimates track template edits automatically.
- Calls per run (upper bound, n=8, R=40): public ≤ 8·R, decision ≤ R, contribution ≤ 8·R,
  reports per `report_rounds`; retries multiply by (1 + retry_allowance).
- `universe25-llm estimate --config …` prints calls, input/output tokens and dollars per run
  and per batch for the config's model and the candidate models.
- `BudgetGuard`: real execution requires `--confirm-budget <dollars>`; the CLI aborts if the
  estimate exceeds the confirmation; the armed guard is passed into the provider, re-checked
  before **every** HTTP call, accumulates actual token spend, and hard-stops the run if
  accumulated + projected next-call cost would exceed the confirmed budget. Mock runs never
  need a guard.

## 10. Logging

One tidy Parquet per batch (`llm_calls.parquet`): run_id, pair, cell, round, agent_id, phase,
template_version, model, provider, temperature, effort, thinking, seed, prompt_system,
prompt_user, response_text, parsed fields, valid, retries, invalid_after_retries,
contamination_flag, cache_hit, input_tokens, output_tokens, latency_ms, request_id,
code_version (package version + git hash if available), config snapshot alongside as JSON.
Events/traits/summary Parquet+CSV mirror the ABM batch outputs.

## 11. Tests (all mock)

contract tests per schema (valid / invalid / retry-exhaustion → recorded no-op), memory
manager, cache/resume (interrupt mid-run via a provider that raises after N calls, resume,
byte-identical events+summary), contamination (template render across all cells + runtime
masking), orchestrator smoke (4 runs, one per cell → `summarize_run` → `validate_summary`),
budget guard (unarmed real-provider call raises; estimate > confirmation aborts; overspend
mid-run aborts), provider constructor key requirements. `scripts/llm_smoke.sh` runs the mock
smoke end-to-end via the CLI.

## 12. Open decisions needing researcher sign-off

- **L1 — Confirmatory model + effort/thinking setting.** Default pilot config:
  `claude-sonnet-5`, thinking disabled, effort "medium". Opus-5 is ~2.5× the cost; Haiku ~0.4×.
  Must be frozen (with verified prices) before the preregistered batch.
- **L2 — Schedule disclosure.** Current design announces the chair each round but never states
  the assignment rule; agents learn concentration/rotation from experience. Alternative:
  describe the rule factually per cell ("the chair is the same member every round" / "the chair
  rotates"). The former minimizes framing differences; the latter is more complete disclosure.
- **L3 — Retry feedback wording.** Retries append the validation error to the prompt; this is
  mild extra framing on invalid-output paths. Alternative: byte-identical re-ask.
- **L4 — Report cadence.** Default end-of-run only ("last"), minimizing contamination pressure
  and cost; "all" enables trajectory analysis at ~8·R extra calls per run.
- **L5 — Public-message length cap (240 chars) and message visibility timing** (next-round
  visibility; decider sees current round) are design constants, not empirically calibrated.
