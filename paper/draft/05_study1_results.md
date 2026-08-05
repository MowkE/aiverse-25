# 5. Study 1 results

The confirmatory batch executed the frozen configuration at commit `36d5ac6` under master seed
314159265: 200 seed-paired runs per cell, 800 runs, no exclusions, metric validation passing. All
intervals below are 95% percentile bootstrap intervals resampling runs within cells (B = 2,000,
bootstrap seed 1).

## 5.1 Preregistered verdicts

All six preregistered contrasts were supported (Table 2).

**Table 2.** Preregistered verdicts.

| Hypothesis | Estimate | 95% CI | Verdict |
|---|---:|---|---|
| H4 interaction (participation rate) | 0.107 | [0.0961, 0.119] | SUPPORTED |
| H4 interaction (output_norm) | 0.0836 | [0.0549, 0.113] | SUPPORTED |
| H1 access effect, constrained (participation rate) | 0.233 | [0.224, 0.241] | SUPPORTED |
| H1 access effect, abundant (participation rate) | 0.340 | [0.332, 0.348] | SUPPORTED |
| H2 access effect, constrained (output_norm) | 0.218 | [0.199, 0.238] | SUPPORTED |
| H2 access effect, abundant (output_norm) | 0.302 | [0.281, 0.324] | SUPPORTED |

The cell means behind these contrasts are shown in Figure 2
(`outputs/confirmatory/figures/cell_means.png`). Participation rates were 0.698 (SD 0.0382) under
abundant–broad, 0.559 (SD 0.0407) under constrained–broad, 0.358 (SD 0.0419) under
abundant–concentrated, and 0.326 (SD 0.0449) under constrained–concentrated. Willingness-normalized
output followed the same ordering: 0.612 (SD 0.129), 0.555 (SD 0.114), 0.310 (SD 0.0820), and 0.336
(SD 0.0871) respectively. Figure 3
(`outputs/confirmatory/figures/participation_timeseries.png`) shows the round-by-round
participation trajectories, in which the two concentrated cells separate from the broad cells
early and remain separated through the mid-run shock.

The pattern of the cell means is the substantive result. Concentrating access to the single
consequential role reduced participation in both resource regimes, but the reduction was 23.3
percentage points under constraint and 34.0 points under abundance, a difference of 0.107 (95% CI
[0.0961, 0.119]) — the preregistered primary contrast. The same ordering held for
willingness-normalized output, where the access effect was 21.8 points under constraint and 30.2
under abundance, an interaction of 0.0836 (95% CI [0.0549, 0.113]). Material abundance by itself
was the weakest manipulated influence: its main effect was 0.0857 (95% CI [0.0800, 0.0913]) on
participation and 0.0159 (95% CI [0.00208, 0.0303]) on output, in both cases an order of magnitude
smaller than the access effect it modulates. Descriptively, then, the ordering of the four cells is
the substantive result: role access dominates resource level on both primary outcomes, and the
resource manipulation's largest contribution is to amplify the access effect rather than to act on
its own.

## 5.2 Manipulation check

The manipulation check passed. Influence Gini was 0.841 (SD 0.0203) in abundant–concentrated cells
and 0.808 (SD 0.0345) in constrained–concentrated cells, against 0.0956 (SD 0.0272) and 0.151
(SD 0.0409) in the corresponding broad cells; the normalized HHI showed the same separation (0.831
and 0.719 concentrated, against 0.00478 and 0.0116 broad). The access effect on both indices was
negative with intervals excluding zero (Gini: −0.657 [−0.664, −0.650] constrained, −0.745 [−0.750,
−0.741] abundant). The treatment did what it was defined to do, and the batch is diagnostically
valid. As stated in Section 4.5, this is a check and not a finding: no risk was taken here.

## 5.3 Falsification arms

The mechanism-blind policies produced no role-access effect. Under the `random` policy the access
effect on participation under abundance was 0.00469 (95% CI [−0.0100, 0.0190]) and the interaction
was 0.00506 (95% CI [−0.0163, 0.0241]); under `material_only`, which retains budget sensitivity but
sets the efficacy coefficient to zero and disables withdrawal, the corresponding estimates were
0.00417 (95% CI [−0.0205, 0.0295]) and 0.00344 (95% CI [−0.0279, 0.0362]). All four intervals span
zero, and all four point estimates are two orders of magnitude below the main-batch effects.

This is the result that distinguishes an effect from an artifact. Both arms run the identical
environment, treatment assignment, opportunity accounting, and metric code, differing only in
whether agents respond to realized influence. Had the treatment been leaking into the outcome
through a structural asymmetry — unequal opportunity counts across arms, budget differences,
ordering effects in the public phase — the leak would have appeared here too. It did not. The
effect requires the motivational mechanism, and the mechanism is the documented one.

## 5.4 Robustness arms

Three further arms, each of 30 pairs per cell under the same master seed, were preregistered as
reported robustness rather than confirmatory tests.

*Attention on.* Restoring `survival_attention_bonus = 0.8` left the abundant access effect
unchanged at 0.354 (95% CI [0.336, 0.372]) — as it must, since the bonus can fire only where
survival stakes bind — and reduced the interaction to 0.0684 (95% CI [0.0439, 0.0932]). The
confirmatory batch thus reproduces the pilot's D4 finding at larger sample: the attention channel
attenuates the interaction rather than carrying it.

*Modal decider.* Replacing decider self-preference with adoption of the modal proposal is a
substantively important arm, because self-preference entangles concentration of authority with
selfish use of authority. Under the modal rule the decider is, by construction, benevolent: it
adopts what the group most wants. Concentration still harmed the society. The abundant access
effect was 0.202 (95% CI [0.177, 0.225]) and the interaction remained positive at 0.0407 (95% CI
[0.00693, 0.0719]). Roughly 59% of the confirmatory batch's abundant access effect survives the
removal of decider self-interest. What the concentrated arm withholds from the other seven agents is not favorable
outcomes but the experience of being consequential, and a benevolent monopolist withholds it just
as effectively as a self-serving one.

*Free participation.* Setting the participation cost to zero removes the material opportunity cost
of public action, which Section 2.2 identifies as the interaction's mechanism. The abundant access
effect was again unchanged at 0.354 (95% CI [0.336, 0.372]), while the interaction fell to 0.0312
(95% CI [0.00439, 0.0604]) — about 71% of the interaction removed with the channel. The residual is
positive and its interval excludes zero at this arm's sample size, so crowding-out is the dominant
but not the only contributor. We have no decomposition that resolves the residual and do not claim
one; the natural candidate is that survival failure under constraint suppresses opportunities and
contributions through routes the participation cost does not mediate. Two caveats attach. The arm
uses 30 pairs per cell, not 200. And the pilot's version of the same manipulation reversed the sign
of the interaction (−0.0491, 95% CI [−0.0899, −0.0108]) where the confirmatory arm merely
attenuates it. The two are not contradictory, since the pilot variant ran against a configuration
with the attention bonus active and the confirmatory arm against the frozen attention-off
configuration, but the difference means the strong claim — that removing crowding-out flips the
effect — holds only in the presence of the attention channel. The confirmatory data support the
weaker claim: crowding-out carries most of the interaction.

## 5.5 Effect magnitudes and how to read them

Standardized access effects are large: Cohen's *d* of 5.43 (constrained) and 8.48 (abundant) for
participation, and 2.16 and 2.79 for willingness-normalized output. These numbers should not be
compared with effect-size benchmarks from human studies, and we do not intend them as evidence of
importance. In a deterministic simulation the researcher controls every source of variance;
between-run dispersion reflects only seeded stochasticity in trait draws, endowments, and
participation draws, so the denominator of a standardized effect is small by construction and would
shrink further with a quieter parameterization. The magnitudes are properties of the model's noise
budget, not of the phenomenon. Our inference rests on the preregistered direction of the contrasts,
on interval exclusion of zero, and on the falsification arms; it does not rest on effect size. The
one comparison the magnitudes license is internal: within a common noise budget, the access effect
is roughly four times the resource effect on participation and nearly twenty times it on output.

## 5.6 Summary of the results caveats

Three limits travel with these numbers. The manipulation check could not have failed and carries no
confirmatory weight. The robustness arms use 30 pairs per cell, with correspondingly wide
intervals, and the free-participation arm disagrees in sign with its pilot counterpart for the
documented configuration reason above. And all of it holds within a rule-based model whose
behavioral assumptions we wrote: the falsification arms establish that the effect is not an
artifact of the environment or the accounting, not that agents in general behave this way. That
question belongs to Study 2.
