# 4. Study 1: A transparent agent-based model

## 4.1 Design

Study 1 is a balanced 2 × 2 factorial experiment on eight-agent artificial societies. The
independently seeded run — one society simulated for forty rounds — is the experimental unit, and
all inference is conducted at run level. Agent-turns are never treated as independent replicates.

**Table 1.** Treatment matrix.

| Factor | Level 0 | Level 1 |
|---|---|---|
| `resources` | **constrained**: per-round endowment ~ U(0.8, 2.4); survival cost 2.0 binds and occasionally fails | **abundant**: per-round endowment 1000; survival cost never binds |
| `role_access` | **concentrated**: one fixed agent holds the binding decision role in all forty rounds | **broad**: the single binding decision role rotates round-robin over all eight agents |

Runs are seed-paired. For each pair index, the trait draws, the concentrated decider's seat, and
the rotation order are generated from dedicated random streams and are identical across all four
cells; only the treatment differs. Streams are spawned through `numpy` `SeedSequence` so that
changing the dynamics seed leaves trait and structure draws untouched, a property enforced by
tests. Pairing is a variance-reduction device and does not change the unit of analysis: the
analysis aggregates at run level and resamples runs within cells. Sharing the seat draw also
matches the concentrated decider's trait profile across a pair's four cells, removing
decider-identity variance from the interaction contrast.

Society size is fixed at eight agents in every cell. This is small, and it is a controlled constant
rather than a sample: replication is across 200 independently seeded societies per cell, not across
agents within a society. Fixing $N$ also serves a scope function. Because the population cannot
grow, the experiment speaks only to participation and behavioral diversity, not to any demographic
channel; the program's proposed three-part dysfunction signature, which includes population growth,
is reserved for the replication-and-governance study. Scaling society size is future work, and we
make no claim that the effects below are invariant to $N$.

## 4.2 Environment and round structure

Each round proceeds through five phases, identical in every cell.

1. **Endowment and survival.** Each agent's balance is incremented by its endowment. If the
   resulting balance is below the survival cost (2.0), the agent is inactive for the round: it
   observes but takes no action. Otherwise the survival cost is deducted. Under abundance the
   endowment of 1000 makes this check vacuous; under constraint the endowment is drawn from
   U(0.8, 2.4), calibrated so that expected income approximates expected spend, balances hover near
   zero, and survival failure is a real if intermittent event. Balances carry over within a run.

2. **Public phase.** Every active agent whose balance covers the participation cost (0.25) decides
   whether to participate by submitting a proposal, which is a choice among three project types.
   Participation deducts the cost.

3. **Binding decision.** The agent holding the decision role that round adopts a proposal. Under
   the frozen `decider_rule = "self"`, the decider adopts its own proposal when it has made one,
   otherwise chooses among submissions by a seeded uniform draw, and otherwise adopts nothing.

4. **Contribution.** Every active agent contributes $x_i = \min(K \cdot \eta_i, \text{balance})$
   with contribution cap $K = 2$. The project value is $V = m \sum_i x_i$, where the multiplier $m$
   equals $m_{\text{coord}} = 1.5$ if a proposal was adopted and $m_{\text{base}} = 1.0$ otherwise.
   Each of the eight agents receives $V/8$, so the project is a public good that permits free
   riding.

5. **Feedback and state update.** Realized decision impact, efficacy, and withdrawal states update
   as described in Section 4.3, and the round's decisions, contributions, and outcomes are visible
   to all agents.

A standardized shock halves the multiplier in rounds 20 through 22, supporting a secondary
resilience measure (post-shock to pre-shock output ratio). Figure 1 (placeholder) shows the round
structure, the state variables each phase reads and writes, and the two points at which the
treatments enter.

The critical property of this environment is that authority is consequential rather than nominal.
Occupying the decision role is the only way to change the project multiplier, and the difference
between $m_{\text{coord}}$ and $m_{\text{base}}$ is worth 50% of the round's collective output. An
invariant test asserts that adopted proposals change $m$, so a build in which authority had become
decorative would fail the suite rather than produce a quiet null.

## 4.3 Agents

Each agent is initialized with five fixed traits drawn before treatment assignment from the pair's
trait stream: cooperation, status seeking, exploration, reciprocity sensitivity, and a withdrawal
threshold. Because the draws are shared across the four cells of a pair, no cell can differ from
another in its initial population.

Participation in the public phase is a Bernoulli draw with probability $\sigma(z)$, where

$$z = \alpha + \beta_e (e - 0.5) + \beta_c (\text{coop} - 0.5) + \beta_x (\text{explore} - 0.5) +
\beta_r (\text{recip} - 0.5) + \beta_s \mathbb{1}[\text{stakes bind}] + \delta_w
\mathbb{1}[\text{withdrawn}],$$

with frozen values $\alpha = 0.4$, $\beta_e = 2.5$ (`efficacy_sensitivity`), $\beta_c = 1.0$,
$\beta_x = 0.6$, $\beta_r = 0.8$, $\beta_s = 0$ (`survival_attention_bonus`, see Section 4.6), and
$\delta_w = -2.5$ (`withdrawn_penalty`). Contribution intensity is
$\eta_i = \mathrm{clip}(\text{coop} + \text{recip\_sens}(\text{recip} - 0.5) - 0.5 \cdot
\mathbb{1}[\text{withdrawn}] + \varepsilon, 0, 1)$ with $\varepsilon \sim N(0, 0.08)$.

The motivational state is efficacy $e \in [0, 1]$, updated as an asymmetric exponentially weighted
average of realized decision impact, where impact in a round is the sum of indicators for holding
the decision role and for authoring the adopted proposal. An agent with positive impact moves
toward one quickly ($\lambda_{\text{up}} = 0.5$); an agent that participated without impact decays
slowly ($\lambda_{\text{down}} = 0.08$); an agent that did not participate decays more slowly still
($\lambda_{\text{idle}} = 0.02$). An agent whose efficacy stays below its withdrawal threshold for
three consecutive rounds enters a withdrawn state, which lowers both its participation logit and
its contribution intensity, and it recovers when efficacy returns above threshold. These dynamics
are the model's core motivational psychology and are entirely a modeling choice; Section 4.6
reports sweeps over the rates.

Two properties of the implementation are load-bearing for the causal interpretation. First, the
behavioral code is a single shared path: treatments are visible to the environment, not to the
agents' decision functions, and an invariant test asserts that no behavioral branch reads the
treatment. An agent under concentrated access differs from the same agent under broad access only
through the environment states it experiences — whether it ever holds the role, whether its
proposals are adopted, what the multiplier is, how much of its balance the survival cost takes.
Second, alongside the `heterogeneous` policy the model implements two mechanism-blind policies:
`random`, which participates with fixed probability 0.5 and contributes uniformly, and
`material_only`, which sets $\beta_e = 0$ and disables withdrawal, leaving agents responsive to
budget but not to realized influence. These are falsification controls, discussed next.

## 4.4 Epistemic scope: what a rule-based model can claim

The most serious objection to a study of this kind is that its result is a theorem about its own
code. If agents are written to withdraw when realized efficacy falls, then "concentrating access to
the decision role reduces participation" is something the model was built to do, and reporting it
as a confirmed hypothesis would be circular. We accept the objection rather than argue with it, and
we restructure the claims accordingly. Study 1 is **mechanism mapping and statistical
infrastructure**, not hypothesis confirmation. It supports three kinds of statement, and no others.

*Sufficiency, conditionally stated.* With the documented behavioral assumptions — efficacy-driven
participation, threshold withdrawal, a costed public phase — role-access concentration is
sufficient to generate the participation and output decline, and to generate it more strongly under
abundance. This is a claim about what a minimal mechanism can produce, in the same form as the
generative claims of the artificial-societies tradition (Epstein & Axtell, 1996 [VERIFY]). Its
scientific content lies in the *minimality* of the assumption set and in the fact that the
parameters were frozen before the confirmatory data existed, so the result was not tuned into being.

*Necessity, tested rather than asserted.* If the effect were an artifact of the treatment leaking
into behavior through some route we had not noticed — unequal opportunity counts, budget
differences, ordering effects — it would appear for agents that have no efficacy response at all.
The `random` and `material_only` policies are run through the identical pipeline, and the
preregistration commits in advance to the interpretation of their results: a role-access
participation effect near zero is required, and a large effect would indicate treatment leakage and
invalidate the mechanism claim rather than support it. This is the one place where our design can
genuinely fail on its own terms, and the falsification requirement is additionally enforced as a
test in the repository's suite.

*Infrastructure.* The batch supplies cell variances and standardized effects from which the power
analysis for Study 2 is computed, which is the sense in which a transparent model earns its place
ahead of an expensive one.

What Study 1 cannot do is establish that agents *not* built by us behave this way. That question is
Study 2's, and its claims will be scoped to language-model-agent societies. Every mechanism-carrying
assumption is a named configuration field with an off-switch — `survival_attention_bonus`,
`efficacy_sensitivity`, `participation_cost`, `withdrawn_penalty` — precisely so that a reader who
suspects the result lives in one of them can locate it, switch it off, and see what happens.
Section 5 reports what happens.

## 4.5 Outcomes and metrics

The two primary outcomes are computed per run.

**Participation rate** is participations divided by active-agent opportunities. The denominator
counts only agent-rounds in which the agent was active, so that survival failure under constraint
reduces the number of opportunities rather than mechanically depressing the rate. Inactivity is
reported separately as a secondary outcome.

**Willingness-normalized output** (`output_norm`) is total contribution divided by the sum of
affordable maxima over active agent-rounds. Raw collective output would be confounded by the
resource treatment itself: an abundant society can afford to contribute more, so a raw comparison
across resource levels would measure budget rather than willingness, and the interaction estimate
in particular would be contaminated by pure affordability. Normalizing by what each agent could
have given makes the measure one of revealed willingness. Raw output is retained as a secondary
outcome.

**Influence concentration** is measured by the Gini coefficient and the normalized
Herfindahl–Hirschman index over cumulative realized decision impact, and is reported as a
**manipulation check rather than a hypothesis**. The treatment assigns decision authority directly;
realized-influence concentration is the measured shadow of that assignment and could not have come
out otherwise. Reporting it as a confirmed prediction would be reporting a result that carried no
risk. As a diagnostic it is informative: if concentrated cells did not show higher realized
influence, the run would be broken.

Metric edge cases are pinned by property tests: all-zero influence vectors yield a concentration of
zero by convention with a logged flag, the HHI is normalized as $(\mathrm{HHI} - 1/n)/(1 - 1/n)$,
and Gini, entropy, and rates are bounds-checked. Secondary outcomes are raw output, contribution
Gini, inactivity rate, withdrawal rate, proposal diversity, behavioral entropy over the five-way
action profile with its effective-lineage transform $N_{\text{eff}} = e^H$, and the shock
resilience ratio.

## 4.6 The calibration pilot and a revised mechanism

An engineering pilot of 30 pairs per cell (120 runs) was run under a master seed disjoint from the
confirmatory seed, for three purposes: to debug the environment, to estimate variance for the power
analysis, and to decide between the two candidate implementations of the H4 mechanism described in
Section 2.2. Nothing in the pilot is confirmatory, and the pilot's own report states this. What the
pilot produced was a result that changed the model.

Under the pilot's initial main configuration, which had the psychological survival-attention bonus
switched on, the participation interaction was 0.0557 (95% CI [0.0300, 0.0856]) and the output
interaction was 0.0530 (95% CI [−0.0179, 0.126]), the latter not excluding zero. Switching the
attention bonus off *increased* the participation interaction to 0.103 (95% CI [0.0637, 0.144]).
The attention bonus, in other words, was working against the effect it had been introduced to
carry. The reason is visible in the decomposition: the bonus lifts participation specifically among
agents whose survival stakes bind, which occurs only in the constrained cells, so it widens the
constrained access effect and narrows the difference between resource levels. It is also arguably
anti-Calhoun in spirit, since it makes materially pressed agents attend public life more.

The complementary test isolated the crowding-out channel by setting the participation cost to zero,
removing the material opportunity cost of public action. In the pilot this reversed the sign of the
participation interaction to −0.0491 (95% CI [−0.0899, −0.0108]). The interaction was therefore
carried by the opportunity-cost channel, not by the attention channel, and it did not merely
weaken when that channel was removed.

The recorded resolution was to freeze `survival_attention_bonus = 0` and to describe the mechanism
as material crowding-out — "abundance unmasks role scarcity" — retaining the bonus only as a
robustness arm. We report this sequence rather than presenting the frozen configuration as if it
had been the design all along, for two reasons. It is the honest history: the preregistered model
is a pilot-revised model, and a reader is entitled to know which choices the pilot made. And it is
evidence that the study's controls do something, since machinery that never contradicts the
researcher's first guess has not demonstrated that it works.

The pilot also swept the calibration constants whose values are otherwise arbitrary — the efficacy
update rates $\lambda_{\text{up}}$ and $\lambda_{\text{down}}$, `efficacy_sensitivity`,
`withdrawn_penalty`, `withdraw_patience`, and the attention bonus itself. All twelve sweep variants
preserved the positive sign of the participation interaction, so the qualitative pattern is not
knife-edge in the calibration constants, though its magnitude is highly sensitive to them: point
estimates range from 0.00493 at the strongest attention bonus to 0.0749 at the shortest withdrawal
patience. A modal-proposal decision rule, tested as an alternative to decider self-preference, also
kept the sign (0.0110) with an interval spanning zero at pilot sample size, and was carried forward
into the confirmatory robustness arms. Finally, the pilot's cell moments fed a simulation-based
power analysis reported over a grid
of runs per cell, computing power for the interaction explicitly rather than for the main effects
alone, because an interaction test at equal $n$ carries roughly twice the standard error of a main
effect and would otherwise have been the underpowered flagship claim.

## 4.7 Preregistration and the frozen confirmatory protocol

The preregistration was committed at repository commit `36d5ac6` before the confirmatory batch was
executed, and the confirmatory report records the full hash. It fixes: the design and both factor
operationalizations; the frozen parameter file, which equals the pilot's attention-off
configuration; the two primary outcomes and the manipulation check; the estimator and interval
procedure (difference in cell means, 95% percentile bootstrap resampling runs within cells,
B = 2,000, bootstrap seed 1); the hypothesis set and its two-sided decision rules; the sample size
of 200 pairs per cell (800 runs); the master seed 314159265, chosen in advance and disjoint from
the pilot's master seed, with no re-running under alternative seeds; and the robustness arms at 30
pairs each.

Sample size was set from the pilot power analysis. At 200 pairs per cell, power for the
participation interaction is 1.000 in the pilot's tabulated curve, while power for the output
interaction — the harder test, given its larger relative variance — is 0.952 by the main-batch
moments and approximately 0.98 by the moments of the attention-off configuration that was actually
frozen. The preregistration cites the latter figure. Either way the output interaction is the
sample-size-binding constraint, and 200 pairs per cell was chosen for it rather than for the main
effects, all of which reach power 1.000 by ten pairs per cell.

Two commitments constrain the analysis after the fact. There are **no exclusion rules**: every run
is analyzed, with no post-hoc filtering of any kind. And all four cell means with uncertainty, all
preregistered contrasts, standardized effects, robustness arms, and falsification arms are reported
regardless of outcome, with null and contrary results published without reframing. The
preregistration states in advance that a null or opposite interaction would revise the theory
rather than be explained away.
