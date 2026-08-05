# SPEC — Transparent ABM for "When Resources Are Abundant but Roles Are Scarce"

Version 0.1. This document translates the starter kit's Prompt 1 (with the fixes recorded in
`VALIDATION.md`) into explicit state variables, transition rules, invariants, and formulas.
Unresolved scientific choices are flagged inline as `[D#]` and collected in `DECISIONS.md`.

## 1. Design summary

Balanced 2×2 factorial. Unit of analysis: the independently seeded **run** (one 8-agent society,
`n_rounds` rounds). Factors:

| Factor | Level 0 | Level 1 |
|---|---|---|
| `resources` | **constrained** — stochastic endowment, survival cost binds | **abundant** — endowment nonbinding |
| `role_access` | **concentrated** — one fixed agent holds the binding-decision role all run | **broad** — the role rotates round-robin over all agents |

Runs are **seed-paired**: one pair index yields identical trait draws, decider-seat draw, and
rotation order across all four cells, differing only in treatment. Pairing is a variance-reduction
device; analysis still aggregates at run level.

## 2. Epistemic scope (what this model can and cannot claim)

Study 1 is **mechanism mapping**, not hypothesis confirmation (VALIDATION C2). Its claims:

- *Sufficiency:* with the documented behavioral assumptions, role-access concentration generates
  participation/output decline, amplified under abundance.
- *Necessity:* with mechanism-blind agents (`random`, `material_only` policies) the role-access
  effect vanishes (enforced by tests).
- *Infrastructure:* variance estimates and power curves for the preregistered Study 2.

## 3. State variables

Per agent i: traits (fixed at t=0) `coop, status, explore, recip_sens, withdraw_threshold`;
state `balance, efficacy e∈[0,1], withdrawn (bool), low_e_streak`.
Per round t: `endowments, decider_id, proposals, adopted (proposal|None), multiplier m,
contributions x_i, project value V, payouts`.
Per run: treatment cell, seeds, event log, ledger (for conservation checks).

## 4. Treatments (environment-only; behavioral code is shared and identical)

- **Roles.** Exactly one binding-decision role per round in both arms (per-round role scarcity is
  identical; the factor is *access*, VALIDATION C4). Concentrated: `decider = seat_perm[0]` every
  round, where `seat_perm` is drawn once per pair from the pairing stream. Broad:
  `decider = rotation[t mod 8]`, rotation drawn from the same stream. The decider's choice
  **changes environment state**: an adopted proposal sets the project multiplier `m = m_coord`
  (1.5); with no adoption `m = m_base` (1.0). Authority is thus consequential, not nominal.
- **Resources.** Constrained: endowment_i,t ~ Uniform(e_lo=0.8, e_hi=2.4), calibrated so expected
  income (endowment + payout) ≈ expected spend — balances hover near zero, stakes keep binding,
  survival (s=2.0) occasionally fails. Abundant: endowment = 1000 (never binds). Costs (participation 0.25,
  contribution ≤ cap K=2) identical across cells. Balances carry over within a run.

## 5. Round sequence and behavioral rules (identical across cells)

1. **Endowment & survival.** balance += endowment; if balance < s → inactive this round (observes,
   no actions); else balance −= s.
2. **Public phase.** Active agents participate (submit a proposal: project type ∈ {0,1,2}) with
   probability σ(z), z = α + β_e·(e−0.5) + β_c·(coop−0.5) + β_x·(explore−0.5) + β_r·(recip−0.5)
   + β_s·1[resources=constrained] + δ_w·1[withdrawn], requiring balance ≥ cost. **[D4]** β_s
   (`survival_attention_bonus`) is the named H4-mechanism carrier; mandatory sensitivity run at 0.
3. **Binding decision.** Decider adopts its own proposal if it made one, else a seeded-uniform
   choice among submissions, else none. **[D5]**
4. **Contribution.** Active agents give x_i = min(K·η_i, balance), η_i = clip(coop + recip_sens·
   (recip−0.5) − 0.5·1[withdrawn] + ε, 0, 1), ε ~ N(0, 0.08). V = m·Σx; each agent receives V/8.
5. **State update.** Realized impact_i = 1[decider] + 1[author of adopted]. Efficacy: impact>0 →
   e += λ_up·(1−e); participated without impact → e −= λ_down·e; else e −= λ_idle·e.
   λ_up=0.5, λ_down=0.08, λ_idle=0.02. **[D7]** Withdrawal: e < withdraw_threshold for
   `withdraw_patience`=3 consecutive rounds → withdrawn; recovers when e ≥ threshold.
   recip_t = mean(x)/K.
6. **Shock (secondary).** Rounds [R/2, R/2+2]: m halved. Resilience = post/pre output ratio.

Agent policies: `heterogeneous` (above), `random` (participation p=0.5, uniform contribution),
`material_only` (β_e=0, no withdrawal) — the latter two are falsification controls (C2).

## 6. Outcomes (run-level)

Primary:
- `participation_rate` = participations / active-agent opportunities.
- `output_norm` = Σx / Σ affordable-max over active agent-rounds (willingness, not budget; C3).
- `influence_gini`, `influence_nhhi` over Σ_t impact_i — **manipulation check, not hypothesis** (C1).

Secondary: raw output, contribution Gini, inactivity rate, withdrawal rate, proposal diversity
(entropy over proposal types), behavioral entropy H over action profiles {inactive, silent-freeride,
silent-contribute, participate-freeride, participate-contribute} with N_eff = e^H, conflict/sanction
events (not in v0.1 — see D9), resilience ratio. All-zero vectors → concentration 0 + logged flag (M3).

## 7. Hypothesis structure (revised per VALIDATION C1/M1)

- **Preregistered primary: H4 (interaction).** The role-access effect on participation and
  output_norm is larger under abundance than under constraint (two-sided test; a null or opposite
  interaction is a publishable revision of the theory).
- **Co-primary main effects: H1, H2.** Broad access → higher participation (H1) and output (H2).
- **Manipulation check (was H3):** influence concentration must be higher in concentrated cells.
- **Exploratory (was H5):** mechanism decomposition via `efficacy_sensitivity`/`material_only`
  sweeps in Study 1; structured reports in Study 2 as secondary only.

## 8. Invariants (enforced by tests)

1. Same full seed → byte-identical event logs.
2. Trait draws and seat permutations identical across the 4 cells of a pair; unchanged when the
   dynamics seed changes (independent streams via `numpy SeedSequence.spawn`).
3. Conservation (constrained): Σ spend ≤ Σ endowed + Σ payouts, per agent and in aggregate.
4. Behavioral code paths identical across cells (treatments only enter through environment state).
5. Metric bounds: Gini ∈ [0,1), nHHI ∈ [0,1], entropy ∈ [0, ln 5], rates ∈ [0,1].
6. Falsification: `random` and `material_only` societies show |role-access effect| ≈ 0 on
   participation.
7. Adopted proposals change m (authority is real).

## 9. Analysis & power

Cell means → contrasts (role-access effect within each resource level, resource effect,
difference-in-differences interaction) with percentile bootstrap CIs, resampling **runs** within
cells (B=2000, seeded). Never agent-turns. Power: parametric simulation from pilot cell means/SDs
over a grid of runs/cell, reporting power for the *interaction* explicitly (M2) plus main effects;
paired-design variant uses within-pair differences.

## 10. Scope guards

- N is fixed at 8: this experiment addresses P↓ (participation) and H↓ (diversity) only; the full
  collapse signature (N↑, H↓, P↓) belongs to the replication-paper follow-up.
- No claims about consciousness, suffering, or human societies. Behavioral language only.
- "Collapse" is not used for any observed pattern unless a preregistered threshold is met.
