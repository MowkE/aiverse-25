# DECISIONS — unresolved scientific choices and recorded deviations

## D13 — Post-freeze FP clamp in normalized_hhi (RECORDED 2026-08-05, integrity-verified)
During Study 2 development, property testing found `normalized_hhi` can return −6.9e−17 on
exactly-equal vectors (floating-point error violating the nHHI ∈ [0,1] invariant). Fixed with a
`max(0.0, …)` clamp. Because this touches Study 1 code after the freeze, the frozen confirmatory
batch was regenerated under the clamped code and diffed against `data/confirmatory_run_summary.csv`:
**byte-identical**. The preregistered results are unaffected; the clamp is a numerical-hygiene fix,
not an analysis change.

Choices the model had to make that science has not yet settled. Each is either **flagged** (needs
your sign-off before the preregistered run) or **recorded** (a deviation from the source docs with
rationale). Nothing here is hidden in code: every item maps to a config field.

## D1 — Calibration constants are placeholders (FLAGGED)
λ_up/λ_down/λ_idle, logit coefficients, endowment bounds, costs, cap K, withdrawal patience: all
chosen to produce plausible dynamics, not fitted to anything. The engineering pilot exists to
select them; they must be frozen before preregistration. Config: `[behavior]`, `[economy]`.

## D2 — Authority operationalized as role *access* via rotation (RECORDED)
Rotation (not majority vote) is the primary "broad" arm: it holds the decision mechanism fixed and
varies only occupancy (VALIDATION C4/M4). Voting is a robustness variant to implement later, never
pooled. A role-*count* sweep (1/2/4 simultaneous consequential roles at fixed resources) is the
recommended follow-up experiment per the vision doc's marginalia.

## D3 — H3 demoted to manipulation check; H4 promoted to preregistered primary (RECORDED)
See VALIDATION C1/M2. The paper's headline test is the interaction.

## D4 — H4 mechanism channel (RESOLVED 2026-08-05, revised by pilot evidence)
The researcher's directive: use whichever channel is most similar to Calhoun's Universe 25.
The pilot decomposition then showed the two candidate implementations behave very differently:

- **Material crowding-out** (participation costs a constrained agent's scarce budget): produces a
  strong positive interaction (+0.103 [0.064, 0.144] with the attention bonus off), and removing
  it (`participation_cost = 0`) flips the interaction negative (−0.049). This channel is the
  direct analogue of Calhoun's mechanism — under scarcity, survival tasks compete with social
  life, so role structure matters less; abundance removes that competition and role scarcity
  becomes the binding constraint.
- **Psychological survival-attention bonus** (+participation logit when stakes bind): worked
  *against* the interaction (main config with bonus on: +0.056; off: +0.103), because it
  asymmetrically rescues engaged agents in constrained cells and widens the constrained access
  effect. It is also arguably anti-Calhoun (it makes poor agents attend public life *more*).

**Resolution:** `survival_attention_bonus = 0` is the frozen default; H4 is carried by material
crowding-out via the participation cost. The bonus is retained as a knob for the robustness arm
(`configs/sensitivity_survival_attention_on.toml`). The status-competition alternative remains
deferred to v0.2.

## D5 — Decider self-preference (FLAGGED)
Deciders adopt their own proposal when available (pure self-preference). Alternatives: modal
proposal, quality-weighted, status-weighted. Self-preference maximizes the realized-influence gap
between arms and is the harshest test for the broad arm; but it entangles "concentration of
authority" with "selfish use of authority." Consider a `decider_rule` sweep in the pilot.

## D6 — H5 mediation demoted to exploratory (RECORDED)
Circular in Study 1, contamination-prone in Study 2 (VALIDATION M1).

## D7 — Efficacy dynamics are asymmetric EWMA (FLAGGED)
Fast reinforcement on impact, slow erosion otherwise. This is the model's core motivational
psychology and is entirely a modeling choice; pilot should sweep λ values and show the
qualitative pattern is not knife-edge.

## D8 — TOML instead of YAML for configs (RECORDED)
`tomllib` is stdlib; one fewer dependency; identical expressiveness for flat experiment configs.

## D9 — Conflict/sanction events not in v0.1 (RECORDED)
The starter kit lists conflict as a secondary outcome; v0.1 has no sanction action, so the metric
would be degenerate. Either add a costly-punishment action in v0.2 or drop the outcome from the
preregistration.

## D10 — No agent death or population change (RECORDED)
Survival failure = inactive round, not removal. Keeps N fixed (the flagship's scope guard) and
avoids conflating role scarcity with demographic turnover.

## D12 — Two constrained-side channels feed the interaction (RESOLVED 2026-08-05 by pilot)
The pilot ran the decomposition. Result: material crowding-out (the participation cost binding
under scarcity) is the dominant and only positive channel; the attention bonus pushed the other
way. See D4 for numbers and the resulting frozen default. The paper must describe the interaction
as opportunity-cost-driven ("abundance unmasks role scarcity"), not as a motivational-attention
effect.

## D11 — Per-pair seat permutation shared across cells (RECORDED)
The concentrated decider's trait profile is matched across the 4 cells of a pair, removing
decider-identity variance from the interaction contrast.
