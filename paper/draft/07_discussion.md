# 7. General discussion

## 7.1 Abundance as unmasking

The headline result is an interaction, and the interpretation we defend for it is narrow. Material
abundance did not harm these societies directly: its main effect on participation was positive and
small (0.0857, 95% CI [0.0800, 0.0913]) and on willingness-normalized output smaller still (0.0159,
95% CI [0.00208, 0.0303]). What abundance changed was how much the distribution of role access
mattered. Under constraint an agent's engagement had somewhere else to go — a survival cost to
meet, a budget to protect, a participation fee competing with both — and whether its public action
could ever bind was one consideration among several. Under abundance nothing competed, and that
question was the only thing standing between an agent and public life. The access effect grew
accordingly, by 10.7 percentage points on participation and 8.4 on output, and removing the
participation cost eliminated about 71% of the interaction, locating the mechanism in the
opportunity-cost channel rather than in any motivational response to scarcity as such.

This is a different claim from "abundance is bad for societies." In this model abundance is inert on
its own: a revealing condition rather than a causal agent. The corollary is that a society can look
healthy under material pressure for reasons that have nothing to do with the quality of its
institutions, and can appear to deteriorate when the pressure lifts without any institutional
change having occurred. Calhoun's proposed remedy was to increase the supply of roles
(Calhoun, 1973 [VERIFY]); our design
speaks to a version of that remedy — widening access to a fixed role — but not to its more
ambitious form. Whether raising $K_s$ itself produces the same relief is the experiment we have not
run.

## 7.2 Structure, not selfishness

The modal-decider arm is the result we find hardest to argue away and would most like to see
replicated. When the concentrated decider was made benevolent by construction — adopting the
proposal the group most preferred rather than its own — the abundant access effect remained 0.202
(95% CI [0.177, 0.225]), around 59% of the effect under a self-interested decider, and the
interaction remained positive. The harm does not require the powerful agent to misuse its power; it
is enough that the other seven never occupy the position from which action becomes consequential.
In the vocabulary of exit and voice (Hirschman, 1970 [VERIFY]), a benevolent monopolist can deliver
excellent outcomes while supplying no voice at all, and the withdrawal response here tracks the
absence of voice rather than the quality of outcomes. This is also the sense in which the result is
positional (Hirsch, 1976 [VERIFY]): what concentration withholds is a share of consequence, and
output cannot be substituted for it.

## 7.3 Implications for multi-agent AI systems

Read as engineering, the result cautions against a popular scaling instinct. When a collective of
agents underperforms, the available levers are usually material — more agents, larger context, more
compute, longer horizons — while the governance structure, typically one planner with authority
over a population of executors, is held fixed because it is the cheap part of the design. Our
experiment is the controlled version of doing exactly that, and in it the material lever is the
weak one: its main effect is an order of magnitude below the access effect, and its principal
consequence is to enlarge the cost of the fixed governance structure. Adding compute did not fix
coordination in these societies; it made the coordination structure the only thing that mattered.

The corresponding design principle is that access to consequential positions should be a
first-class, measured property of an agent collective rather than an implementation detail.
Rotation was the cheapest instrument we tested and the most effective, and it requires remarkably
little: the same number of decision seats, the same decision mechanism, the same total authority,
distributed differently over time. Realized influence concentration — which agent's outputs
actually changed environment state, as opposed to which held a title — is computable in any
orchestrated system from logs it already keeps, and it is the quantity our design shows to be
consequential. We offer these as hypotheses worth testing in deployed systems rather than as
validated guidance; a model this small licenses a direction of investigation, not a specification.

## 7.4 Implications for social theory

For social theory the contribution is a minimal, fully inspectable instance of a positional
mechanism. Theories of positional goods hold that some valued things are scarce by their relational
structure rather than by any limit on production (Hirsch, 1976 [VERIFY]), and cumulative-advantage
accounts describe how occupancy of consequential positions concentrates (Merton, 1968 [VERIFY]);
both are ordinarily entangled, in observational settings, with crowding, physiological stress, and
material deprivation. The present design removes those specific confounds by construction: the
substrate has no bodies, no space, no population growth, and — in the abundant arm — nothing
material in short supply, yet concentrating access to a single consequential role still depressed
participation and collective output, and did so more where provisioning was unlimited. The
separation of $K_m$ from $K_s$ is thereby more than notational: within this model the two
capacities have distinguishable behavioral consequences, and only one of them was ever raised in
the abundant arm. What the result licenses is not a claim about natural societies but a clean
demonstration that a purely positional scarcity suffices to generate the withdrawal pattern in at
least one minimal system.

## 7.5 Limitations

Society size is fixed at eight, so no demographic channel exists and the program's proposed
signature involving population growth cannot be addressed here; the study speaks to participation
and, through its secondary diversity measures, to behavioral variety. Inference is at run level
over 800 runs, so the small society is a controlled constant rather than a small sample, but
nothing establishes that the effects hold at other sizes, and $\rho_s$ is fixed at eight throughout.

The behavioral mechanisms are authored. Falsification arms establish that the effect is not an
artifact of the environment, the treatment accounting, or the metrics, since agents without the
efficacy response show role-access effects of 0.00469 and 0.00417 with intervals spanning zero.
They do not establish that agents in general possess anything like an efficacy response, and no
internal control can supply that. Study 2 is the appropriate test and its results are pending.

Only one institutional form was studied: a single binding decision role, held permanently or in
rotation. Majority voting changes the aggregation mechanism rather than the distribution of access
and was excluded rather than pooled with rotation. Role count was held at one, so the manipulation
is role *access*, and we make no claim about varying the number of consequential positions. Decider
self-preference was the frozen rule; the modal-decider arm shows the effect survives its removal,
but both rules are stylized.

The mechanism decomposition is partial. Removing the participation cost removed about 71% of the
interaction but left a positive residual whose source we have not identified, and the same
manipulation in the pilot — against a configuration with the attention channel active — reversed
the interaction's sign rather than attenuating it. Crowding-out is the dominant channel under the
frozen configuration; it is not the only one.

Effect magnitudes are properties of a deterministic simulation's noise budget and are not
comparable to human-study benchmarks (Section 5.5). The robustness arms use 30 pairs per cell.
Calibration constants are chosen rather than fitted; sweeps preserve the interaction's sign, but
its magnitude varies by more than an order of magnitude across the swept range.

Finally, the scope guards. Nothing here is a claim about human societies; the artificial society is
not a model of any human population, and we assert no human analogue for the treatments. Nothing
here is a claim about consciousness, suffering, or experience: "withdrawal," "efficacy," and
"participation" name state variables and observable actions in a simulation and are used in that
sense throughout. And we decline the program's inherited vocabulary of societal failure. What we
observed is a reduction in participation and in willingness-normalized contribution under
concentrated role access, amplified under abundance; that description is complete, and no
preregistered threshold licenses a stronger one.

## 7.6 Future work

Three extensions follow directly. The first is the role-count sweep this design deliberately did
not perform: holding resources and population fixed while varying the number of simultaneous
consequential roles over $R/N \in \{1/8, 2/8, 4/8\}$, which manipulates $K_s$ itself and tests
whether $\rho_s$ behaves as a congestion ratio. The second is a status-competition channel, in
which recognition rather than decision authority is the scarce positional good, testing whether the
effect requires consequence for the environment or only consequence for standing. The third is
Study 2's completion, followed by the program's replication-and-governance study, in which
population size varies and the demographic channel excluded here becomes the object of study.
