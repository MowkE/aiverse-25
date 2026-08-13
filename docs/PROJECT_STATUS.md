# Universe 25 AI — Project Status Handoff

Updated 2026-08-13. Written as a self-contained briefing for any collaborator or AI assistant
directing this project. Repo: `sociologyxai/universe25-abm` (git, local only, 12 commits).

## Project in one paragraph

Research program testing whether AI-agent societies become dysfunctional when *roles* are scarce
even though *resources* are abundant (Calhoun's Universe 25 translated to artificial agents).
Flagship paper: "When Resources Are Abundant but Roles Are Scarce: A Factorial Experiment in
Artificial Societies." Two studies: Study 1 = preregistered rule-based ABM (COMPLETE, all
hypotheses supported); Study 2 = LLM-agent confirmation (infrastructure complete, real runs
pending). Paper drafted except Study 2 results.

## Completed

1. **Design stress test** (`docs/VALIDATION.md`): 4 critical + 5 major flaws in the original
   starter-kit design found and fixed — headline fixes: H3 reclassified as manipulation check
   (was true by construction); ABM reframed as mechanism-mapping with falsification controls
   (`random` / `material_only` agent policies must show null effects — enforced by tests);
   output metric willingness-normalized to remove affordability confound; authority factor
   renamed role *access* (concentrated vs broad/rotating decider).
2. **Study 1 ABM** (`src/universe25/`): deterministic 2×2 factorial (resources constrained/
   abundant × role access concentrated/broad), 8 agents, 40 rounds, seed-paired runs, run-level
   inference. 127 tests incl. property tests; CI config; CLI (`universe25 run-batch|analyze|...`).
3. **Engineering pilot** (~800 runs, `outputs/pilot/PILOT_REPORT.md`): revised the H4 mechanism —
   material crowding-out (participation cost binding under scarcity) carries the interaction;
   the psychological "survival attention bonus" fought it and is now 0 (docs/DECISIONS.md D4, D12).
4. **Preregistration + frozen confirmatory batch** (`docs/PREREGISTRATION.md`, freeze commit
   36d5ac6; `docs/CONFIRMATORY_REPORT.md`; data in `data/confirmatory_run_summary.csv`):
   200 pairs/cell (800 runs), master seed 314159265, no exclusions. **All preregistered verdicts
   SUPPORTED**: H4 participation interaction +0.107 [0.096, 0.119]; H4 output +0.084 [0.055,
   0.113]; H1 access effects +23.3/+34.0 points (constrained/abundant); H2 +21.8/+30.2;
   manipulation check PASS (influence Gini ~0.82 concentrated vs ~0.12 broad); falsification
   arms PASS. Robustness: benevolent (modal) decider still −20 pts (structure, not selfishness);
   free-participation arm shows crowding-out carries ~71% of the interaction.
5. **Study 2 LLM infrastructure** (`src/universe25/llm/`, docs/LLM_DESIGN.md, LLM_EXPERIMENT.md):
   provider-agnostic (mock / Anthropic / OpenAI / claude-cli), structured action schemas,
   per-run memory, JSONL cache with byte-identical resume, contamination controls (banned-terms
   tests — agents never see condition names or hypotheses), cost estimator + hard budget guard
   (no real call without explicit `--confirm-budget`). $0 spent to date.
6. **Subscription-funded shakedown** (D15, in progress): real Claude Haiku 4.5 agents via the
   Claude Code CLI at $0 marginal cost. 226/~600 calls done: **100% first-try schema validity,
   0 retries, 0 contamination flags**. Qualitative preview (no scientific weight): participation
   18% concentrated vs 27% broad; agents write enthusiastic cooperative messages while
   contributing ~3% — a talk-vs-action gap. Excluded from paper per D15 (CLI injects ~24K
   uncontrolled tokens/call). Currently resuming to finish the two abundant-cell societies.
7. **Paper** (`paper/`): CONFIG.md, OUTLINE.md (approved), full ~10.6K-word draft in
   `paper/draft/` (9 sections; §6 Study 2 results = placeholder). Every external citation sits
   in an unverified ledger — none enters a final draft without `/ars-citation-check` + DOI.
8. **Key decisions log**: `docs/DECISIONS.md` D1–D15 (D13: post-freeze FP clamp verified
   byte-identical; D14: Study 2 defaults; D15: shakedown exclusion).

## Money and provider status

- Anthropic API credits: none. Claude subscription: used only for the $0 shakedown.
- **Provider of record for real Study 2 data: OpenAI API** (researcher holds ~$1,000 credits;
  decision L1 in D14). Prices verified 2026-08-13 in `src/universe25/llm/pricing.py`.
- Measured cost model (per 40-round run, typical): gpt-5-mini ~$0.21, gpt-5 ~$1.07. Full
  remaining program (4-run smoke + 20-run pilot + 120-run confirmatory): **~$25–30 all-mini;
  ~$135 with gpt-5 confirmatory; ~$500 with gpt-5.6-sol**. Budget guard enforces a ~4× worst-case
  ceiling. Meta credits held in reserve for optional cross-company robustness.

## Remaining pipeline (in order)

1. Finish shakedown (running; engineering-only).
2. **OpenAI smoke**: 4 runs, ~$1 (needs `OPENAI_API_KEY` in env; command:
   `uv run universe25-llm run-batch --config configs/llm_smoke.toml --confirm-budget <dollars>`
   with provider switched to openai). First real-API integration test.
3. **LLM pilot** (~20 runs, ~$4–20): variance estimates → power analysis → freeze Study 2
   preregistration (model choice, prompts/template version, sample size, decision rules).
4. **Frozen confirmatory LLM batch** (~60–120 runs, ~$25–130).
5. Fill paper §6; trim ~400 words to hit 9–10K band; run `/ars-reviewer` simulated peer review;
   `/ars-citation-check` (verify Calhoun 1962/1973, Hirsch 1976, Merton 1968, Hirschman 1970,
   Epstein & Axtell 1996, Schelling 1971, Axelrod 1997, Ostrom 1990, Olson 1965, Park et al.
   2023, Piatti et al. 2024, Ashery et al. 2025, Grimm et al. 2020, Nosek et al. 2018);
   `/ars-disclosure` AI-usage statement; `/ars-format-convert` → LaTeX/PDF; preprint (SocArXiv/
   arXiv), then JASSS-tier submission.

## Standing constraints

Run-level inference only; treatments touch environment only (behavioral code identical across
cells, tested); nothing called "collapse"; no fabricated citations; shakedown data never enters
analyses; every scientific deviation logged in DECISIONS.md; all batches reproducible from
recorded seeds/configs. Environment note: venv must live outside iCloud
(`export UV_PROJECT_ENVIRONMENT=~/.venvs/universe25-abm`).
