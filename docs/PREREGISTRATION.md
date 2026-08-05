# Preregistration — Study 1 (Transparent ABM)

**Title:** When Resources Are Abundant but Roles Are Scarce: A Factorial Experiment in Artificial
Societies — Study 1 confirmatory ABM batch.
**Date frozen:** 2026-08-05, before the confirmatory batch was executed.
**Code state:** the git commit containing this document. The confirmatory report records the hash.

## 1. Scope of claims

Study 1 is a transparent rule-based ABM. Its confirmatory value is limited to: (a) demonstrating
that the documented mechanism (material crowding-out + efficacy-dependent participation) is
sufficient to generate the predicted pattern under frozen parameters chosen without reference to
confirmatory data; (b) establishing effect sizes and variance for Study 2 (LLM agents), which is
the empirical test. No claim about consciousness, suffering, human societies, or "collapse" is
made. The word "collapse" is not used for any observed pattern.

## 2. Design

Balanced 2×2 factorial; the independently seeded run is the experimental unit.

- Factor 1 `resources`: constrained (endowment ~ U(0.8, 2.4), survival cost 2.0 binds) vs
  abundant (endowment 1000, never binds).
- Factor 2 `role_access`: concentrated (one fixed agent holds the binding-decision role) vs
  broad (role rotates round-robin).
- 8 agents, 40 rounds, mid-run shock rounds 20–22 (multiplier ×0.5).
- Seed-paired runs: each pair index is simulated in all four cells with shared trait/structure/
  dynamics streams.

## 3. Frozen parameters

Exactly the values in `configs/confirmatory.toml` at the freeze commit, which equal the pilot's
`d4_attention_off` configuration: the H4 mechanism is material crowding-out;
`survival_attention_bonus = 0`; `decider_rule = "self"`; behavior policy `heterogeneous`;
all calibration constants as in `BehaviorConfig`/`EconomyConfig` defaults at the freeze commit.

## 4. Sample size and seed policy

- **200 pairs per cell** (800 runs). Pilot-based parametric power at n=200: >0.99 for the
  participation interaction, ≈0.98 for the output interaction (see
  `outputs/pilot/power_curve_calhoun_default.csv`).
- **Master seed 314159265**, fixed here before execution, disjoint from the pilot master seed
  (20260805); every run's streams derive deterministically from (master_seed, pair) via
  `numpy SeedSequence`. No re-running with alternative seeds.

## 5. Outcomes

Primary: `participation_rate`; `output_norm` (willingness-normalized). Manipulation check:
`influence_gini` / `influence_nhhi` (must be higher in concentrated cells; if not, the batch is
diagnostically invalid and reported as such). Secondary (reported, not tested): raw output,
contribution Gini, inactivity, withdrawal, proposal diversity, behavioral entropy/N_eff,
resilience ratio.

## 6. Hypotheses and decision rules

Estimator: difference in cell means; 95% percentile bootstrap CIs, resampling runs within cells,
B = 2000, bootstrap seed 1. Two-sided decision rules; α equivalent = CI exclusion of zero.

- **H4 (preregistered primary, interaction):** the role-access effect on each primary outcome is
  larger under abundance: DiD = (broad − concentrated | abundant) − (broad − concentrated |
  constrained) > 0. Supported if CI excludes 0 above; theory-revising if CI excludes 0 below;
  inconclusive otherwise. Published in all three cases.
- **H1 (co-primary main effect):** broad access → higher participation within each resource level.
- **H2 (co-primary main effect):** broad access → higher output_norm within each resource level.
- **Manipulation check (formerly H3):** concentrated cells show higher influence concentration.
- **Exploratory (formerly H5):** mechanism decomposition via the robustness arms below; no
  confirmatory test.

## 7. Exclusion rules

None. Every run in the batch is analyzed. There is no post-hoc filtering of any kind.

## 8. Robustness arms (reported alongside, not confirmatory)

Same master seed, 30 pairs each: `survival_attention_bonus = 0.8`; `decider_rule = "modal"`;
`participation_cost = 0`; falsification policies `random` and `material_only` (expected:
role-access participation effect ≈ 0; a large effect indicates treatment leakage and invalidates
the mechanism claim).

## 9. Reporting commitments

All four cell means with uncertainty; all preregistered contrasts with CIs; standardized effects;
robustness and falsification tables; null and contrary results published without reframing;
figures and tables regenerable from recorded seeds and configs by
`uv run python scripts/confirmatory.py`.
