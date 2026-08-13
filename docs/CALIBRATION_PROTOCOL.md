# Ceiling-Effect Calibration Protocol (pre-pilot, Study 2)

Motivation: D16. With real LLM agents the abundant arm reached 0.90–0.99 participation, leaving
no headroom for the role-access contrast. Study 2's economy must be recalibrated **before** its
preregistration is frozen. This protocol is written before any calibration run and fixes the
selection rule in advance so parameters cannot be chosen to manufacture the hypothesized effect.

## What is varied (and what is not)

Varied — economy only, under abundant-arm focus:
- `abundant_endowment`: 3 levels — {1000 (current), 20, 8}
- `participation_cost`: 4 levels — {0.25 (current), 1.0, 2.0, 4.0}
- `role_access`: both levels (concentrated, broad)
- 2–3 runs per cell, 10 rounds, distinct seeds; Haiku via the clean CLI pathway **only if**
  the isolation checklist in docs/CLI_ISOLATION.md fully passes; otherwise defer to the paid
  pilot and fold this grid into it.

Held fixed: all Study 1 parameters; all Study 2 prompts/templates (template_version llm-t1);
schemas; outcome definitions; constrained-cell economy (checked, not tuned, at the selected
cost level).

## Blinding

The selection rule below was committed before any calibration outcome existed (this document,
git history). Analysis of calibration output is restricted to the gate quantities named in the
rule; no access-effect contrast may be computed per configuration until after the configuration
is selected. The person/agent running the grid records participation rates only.

## Pre-committed selection rule

Select the configuration with the **lowest participation cost** such that, averaged over its
runs:
1. Abundant/broad participation ∈ [0.50, 0.80];
2. Constrained participation (both access levels, at that cost) ≥ 0.10;
3. Participation variance is non-degenerate in both access conditions (no cell pinned at 0 or 1
   across all runs);
4. The abundant arm remains materially non-binding for survival (no survival failures in
   abundant cells);
5. Participation is not irrational everywhere (expected round payout at full cooperation exceeds
   the participation cost in at least the broad arm).

Ties broken toward the endowment level closest to the current 1000 (least intervention). If no
configuration satisfies all gates, the grid is extended one step at a time (documented by
amendment here) — never by post-hoc relaxation of the gates.

## Outputs

`outputs/calibration/` batch per configuration; a calibration report table (config × gate
checks × pass/fail); the selected configuration recorded in DECISIONS.md and frozen into the
Study 2 preregistration. Calibration data is design evidence, not outcome evidence: it never
enters hypothesis tests.

## Cost

Grid = 3 × 4 × 2 × (2–3 runs) = 48–72 runs of 10 rounds (~150 calls each). Subscription
pathway: $0 (quota permitting). Paid fallback at gpt-5-mini: ≈ $4–8 typical.
