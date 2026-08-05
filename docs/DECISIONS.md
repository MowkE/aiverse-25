# DECISIONS — unresolved scientific choices and recorded deviations

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

## D4 — `survival_attention_bonus` carries the H4 mechanism (FLAGGED)
The claim "material stakes keep agents publicly engaged" is a behavioral assumption, made explicit
and sweepable. Mandatory sensitivity analysis at 0. If you believe abundance should amplify
dysfunction through a different channel (e.g., status salience), that is a different model —
decide before freezing.

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

## D12 — Two constrained-side channels feed the interaction (FLAGGED)
With the leaner constrained economy (endowment mean below spend), the H4 interaction can arise
through (a) the survival-attention bonus and (b) affordability censoring — poor agents sometimes
cannot pay the participation cost, compressing the access effect under constraint mechanically.
Both are theory-consistent ("survival crowds out public life"), but the pilot must decompose them:
run `survival_attention_bonus = 0` (isolates censoring) and an ample-but-binding endowment variant
(isolates attention). Report both in the paper; do not attribute the whole interaction to the
motivational channel.

## D11 — Per-pair seat permutation shared across cells (RECORDED)
The concentrated decider's trait profile is matched across the 4 cells of a pair, removing
decider-identity variance from the interaction contrast.
