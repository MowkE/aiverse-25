# Stress Test & Validation Report

Scope: the flagship design in `Universe_25_AI_Research_Starter_Kit.md`, cross-checked against the
full 164-page vision document (including its internal "Claude explained" marginalia). Verdict
first, then issues ranked by severity, each with the fix applied and where the fix lives.

## Verdict

**The core idea is sound, novel, and testable — with repairs.** The research question ("does
scarcity of meaningful roles cause dysfunction independently of material scarcity?") is a real,
falsifiable question that separates two constructs that both Calhoun-inspired discourse and
multi-agent-AI discourse routinely conflate. The 2×2 factorial is the right instrument. The
run-as-unit, preregistration, and treatment-hygiene commitments in the starter kit are unusually
disciplined for this genre. The decisive weaknesses were: one hypothesis that is true by
construction, an ABM framed as able to test hypotheses it actually encodes, an outcome metric that
would be confounded by the resource manipulation itself, and an authority manipulation whose
construct is "role *access* inequality," not "role scarcity." All are fixable and are fixed below.

---

## Critical issues (would have invalidated results)

### C1. H3 is true by construction — a manipulation check disguised as a hypothesis
H3 says "concentrated meaningful authority increases influence concentration." The treatment
*directly assigns* concentrated decision authority; realized-influence concentration is the
measured shadow of the assignment. Testing it as a hypothesis would let the paper claim a
"confirmed prediction" that could not have failed.
**Fix:** H3 reclassified as the **manipulation check** (it must hold, or the run is diagnostically
broken). Primary hypotheses are now H1 (participation) and H2 (output); the preregistered primary
is the *interaction* H4. → `SPEC.md §7`, `DECISIONS.md D3`.

### C2. A rule-based ABM cannot "test" hypotheses whose mechanism is hand-coded
If agents are programmed to withdraw when realized efficacy falls, then "concentrated authority
reduces participation" is a theorem about the code, not a finding. The starter kit gestures at
"mechanism identification" but still lists H1–H5 as things Study 1 tests.
**Fix:** Study 1 is reframed as **mechanism mapping + statistical infrastructure**: it establishes
(a) which minimal behavioral assumptions are *sufficient* to generate the collapse signature,
(b) that the effect *disappears* for mechanism-blind agents (falsification controls: `random` and
`material_only` policies, enforced by tests), and (c) variance estimates for power analysis.
Only Study 2 (LLM agents, whose behavior is not authored by us) is an empirical test, and its
claims are limited to LLM-agent societies. Every mechanism-carrying assumption is a named config
parameter with an off-switch (`survival_attention_bonus`, `efficacy_sensitivity`).
→ `SPEC.md §2, §8`, falsification tests in `tests/test_falsification.py`.

### C3. Raw collective output is confounded by the resource treatment
Abundant societies can mechanically afford more contribution; a raw-output comparison across
resource cells measures budget, not willingness. The interaction estimate (H4) would be
contaminated by pure affordability.
**Fix:** primary output metric is **willingness-normalized output**: contributed / affordable-
maximum, computed per agent-round over active agents. Raw output retained as secondary.
→ `SPEC.md §6`, `metrics.py`.

### C4. The authority factor operationalizes role *access*, not role *count*
With one binding decider per round in both arms (fixed vs rotating), per-round role scarcity is
identical (1 of 8); what varies is the concentration of role occupancy across agents over time.
That is a legitimate and clean manipulation — but it must be named correctly, and it is not the
PDF marginalia's recommended first experiment (fix resources and population, vary the *number* of
consequential roles, R/N). Mislabeling would invite a construct-validity rejection.
**Fix:** the factor is named **role access (concentrated vs. broad)** throughout the spec; a
role-count arm (1 vs 2 vs 4 simultaneous consequential roles) is specified as the immediate
follow-up config, not bolted onto the 2×2. → `SPEC.md §4`, `DECISIONS.md D2`.

---

## Major issues (would have weakened the paper)

### M1. H5 (mediation) is circular in Study 1 and contamination-prone in Study 2
In the ABM, "perceived efficacy" is a state variable we update — mediation analysis on it is
decorative. In the LLM study, self-reported efficacy is exactly the self-report channel the
vision document's own contamination critique says not to trust.
**Fix:** H5 demoted to exploratory. In Study 1 it becomes a *mechanism decomposition* (effect
vanishes when `efficacy_sensitivity = 0` — demonstrated, not estimated). In Study 2, structured
efficacy/legitimacy reports are collected but analyzed as secondary, with a framing-sensitivity
check. → `SPEC.md §7`, `DECISIONS.md D6`.

### M2. Interaction tests need ~4× the sample of main-effect tests
H4 — the theoretically distinctive claim — is an interaction, with roughly twice the standard
error of a main effect at equal n. A power analysis tuned to H1 would leave H4 underpowered,
i.e., the flagship's headline claim would be the one most likely to null spuriously.
**Fix:** the power script computes power for the interaction explicitly and reports the runs/cell
needed for 90% power on H4, not just H1/H2. Seed-paired runs (same trait draw across all 4 cells)
are used as a variance-reduction design. → `power.py`, `SPEC.md §9`.

### M3. Metric edge cases were unspecified
Gini/HHI are undefined or misleading on all-zero influence vectors, tiny-n Gini is biased, and
"participation rate" was undefined when agents are inactive (survival failure).
**Fix:** all-zero vectors → concentration 0 by convention with a logged flag; normalized HHI
((HHI − 1/n)/(1 − 1/n)); participation denominators count only active-agent opportunities;
inactivity reported separately. Property tests pin bounds and known values. → `metrics.py`,
`tests/test_metrics.py`.

### M4. "Distributed = rotation or broadly shared" is two different manipulations
Rotation keeps the decision *mechanism* identical (single decider) and varies occupancy; majority
vote changes the aggregation mechanism itself — a hidden second factor.
**Fix:** rotation is the primary operationalization; voting is a preregistered robustness variant,
never pooled with rotation. → `DECISIONS.md D2`.

### M5. The survival-engagement channel (H4's engine) was implicit
H4's rationale — abundance removes survival tasks that keep agents consequentially active — must
live somewhere in a rule-based model. Hiding it in behavioral equations would be exactly the
"encoding the hypothesis" failure the starter kit forbids.
**Fix:** it is an explicit, named, sweepable parameter (`survival_attention_bonus`), documented as
the H4 mechanism carrier, with the full 2×2 rerun at zero as a mandatory sensitivity analysis.
→ `SPEC.md §5.3`, `DECISIONS.md D4`.

## Minor issues

- **Survival could never bind** with a fixed per-round endowment ≥ survival cost. Fixed: constrained
  endowment is stochastic (uniform), so survival risk is real and project returns are materially
  valuable as a buffer. → `SPEC.md §5.1`.
- **Collapse-signature mismatch:** the program's signature (N↑, H↓, P↓) includes population growth,
  but the flagship fixes N=8. The flagship can only speak to H↓ and P↓; stated explicitly to
  prevent overclaim. → `SPEC.md §10`.
- **Concentrated-decider identity:** the concentrated decider's seat is drawn per run-pair from a
  dedicated stream (identical across the 4 cells of a pair), so decider trait profiles are matched
  across cells. → `SPEC.md §4`.
- **YAML dependency swapped for TOML** (stdlib `tomllib`): one fewer dependency, same expressiveness
  for these configs. → `DECISIONS.md D8`.

## What was validated as strong (kept unchanged)

- Run-as-experimental-unit, seed discipline, traits-before-treatment, preregistration-then-freeze
  workflow, publish-nulls commitment.
- The two-study architecture (transparent ABM + LLM confirmation) — correct division of labor once
  the claims are scoped per C2.
- The starter kit's validity-threat list — comprehensive; the vision doc's contamination critique
  (LLM agents have read Calhoun; measure structure, not self-report; adversarial framing checks)
  is adopted wholesale into the Study 2 requirements.
- The falsifiability posture on H4 (a null/opposite interaction revises the theory).

## Cross-check: where the starter kit ignored the vision doc's own best advice

1. The marginalia's "one experiment to run first" is a role-count sweep at fixed resources; the
   starter kit built an access-concentration factor instead. Addressed via C4 (correct naming now;
   role-count arm specified as follow-up).
2. The marginalia demands "131.1" (status/role scarcity beats material scarcity) as *the single*
   preregistered primary hypothesis; the starter kit listed five co-equal hypotheses. Addressed via
   C1/M1 (primary = H4 interaction; H1/H2 co-primary outcomes; rest exploratory).
3. The marginalia's warning that self-reports are contamination was contradicted by H5's mediation
   design. Addressed via M1.
