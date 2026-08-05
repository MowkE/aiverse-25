# 1. Introduction

John B. Calhoun's final rodent enclosure, which he called Universe 25, was built to house 3,840
mice and provisioned so that food, water, and nesting material were never exhausted. The
population peaked at roughly 2,200 animals, well short of the physical capacity of the pen, and
then declined until the colony died out (Calhoun, 1973 [VERIFY]). Whatever ended that society, it
was not material carrying capacity. Calhoun's own interpretation pointed instead at the social
structure of the enclosure: as the population grew, the positions through which an animal could
act consequentially — territory, mate, rank, care of young — were already occupied, and successive
cohorts matured into a world that had run out of things for them to do (Calhoun, 1962 [VERIFY];
Calhoun, 1973 [VERIFY]). The enclosure had two capacities, and only one of them was ever raised.

The distinction matters for artificial societies for an unusual reason: they are the first
populations for which the two capacities can be pulled apart by construction. Multi-agent AI
systems are moving toward persistent populations of agents that hold state, accumulate memory, and
interact over long horizons (Park et al., 2023 [VERIFY]). In such systems the material substrate —
compute, storage, context, tokens — is elastic and can be scaled at low marginal cost, while the
positions that make an agent's action consequential are structurally scarce and usually scarce by
design. A typical architecture has one planner and many executors, one orchestrator and many
tools, one arbiter of the merge and many contributors. Adding agents does not add decision seats.
If role scarcity has behavioral consequences that are separable from material scarcity, then
scaling an agent collective by adding compute could increase dysfunction rather than relieve it,
and would do so precisely in the regime where engineers expect abundance to help.

That channel is, at present, untested. Research on collective failure in multi-agent systems is
framed overwhelmingly around resource scarcity: commons dilemmas, harvesting games, and
sustainability thresholds, where the binding constraint is a depletable stock and the failure mode
is over-extraction (Piatti et al., 2024 [VERIFY]). The literature on emergent conventions and
collective bias in language-model populations studies how norms form, not how access to
consequential positions is distributed (Ashery, Aiello, & Baronchelli, 2025 [VERIFY]). In
naturally occurring settings, and in most simulations of them, material scarcity and role scarcity
covary: societies short of resources are usually also short of positions, so the two constructs are
routinely conflated and the counterfactual of interest — abundance with concentrated access — is
rarely observed. An artificial society can construct that cell directly.

We do so here. We separate material carrying capacity, K_m, from a social opportunity capacity,
K_s, defined over consequential roles, and we manipulate the two independently in a balanced 2 × 2
factorial experiment on eight-agent artificial societies. The first factor, `resources`, contrasts
a constrained regime in which a stochastic endowment must cover a binding survival cost with an
abundant regime in which the endowment never binds. The second factor, `role_access`, contrasts a
concentrated regime in which one agent holds the binding decision role for all forty rounds with a
broad regime in which the same single role rotates round-robin across all eight agents. Per-round
role scarcity is therefore identical in both arms — one decision seat among eight agents — and what
varies is the concentration of access to that seat over time. The independently seeded run is the
experimental unit; 200 seed-paired runs per cell yield 800 runs. Hypotheses, outcomes, sample size,
seed policy, and decision rules were frozen in a preregistration committed before the confirmatory
batch was executed, with the interaction, not the main effect, as the preregistered primary test.

All six preregistered contrasts were supported. Broad access raised the participation rate by 23.3
percentage points under constraint (95% CI [0.224, 0.241]) and by 34.0 points under abundance
(95% CI [0.332, 0.348]), and raised willingness-normalized output by 21.8 points (95% CI [0.199,
0.238]) and 30.2 points (95% CI [0.281, 0.324]) respectively. The preregistered interaction was
positive for both primary outcomes: 0.107 (95% CI [0.0961, 0.119]) for participation and 0.0836
(95% CI [0.0549, 0.113]) for output. Concentrating access to a single consequential role depressed
participation and collective output in both resource regimes, and it did so *more* where material
resources were abundant. Mechanism-blind control agents, whose policies contain no efficacy
response, showed no such pattern: their role-access effects on participation were 0.00469 (95% CI
[−0.0100, 0.0190]) and 0.00417 (95% CI [−0.0205, 0.0295]), with intervals spanning zero.

We are deliberate about what this establishes. Study 1 is a transparent rule-based model, and a
rule-based model cannot confirm a hypothesis whose mechanism its own code contains. We therefore
frame Study 1 as mechanism mapping rather than hypothesis confirmation: it establishes that a small
set of documented behavioral assumptions is *sufficient* to generate the pattern under parameters
frozen before the confirmatory data existed, that the pattern is *absent* for agents stripped of
those assumptions, and that the magnitude and variance of the effects support a power analysis for
a second study whose agents we do not author. Study 2, a language-model-agent replication of the
identical treatment logic, supplies the construct-validity test; its infrastructure is built and
contamination-tested, and its results are pending.

The paper makes four contributions. First, it gives an explicit formal separation of material
carrying capacity from social opportunity structure, together with a construct-valid
operationalization of the second as role *access* rather than role count. Second, it demonstrates
an honesty apparatus for rule-based simulation — manipulation checks reclassified out of the
hypothesis set, a willingness-normalized outcome that survives the resource manipulation,
mechanism-carrying parameters exposed as named configuration fields with off-switches, and
falsification agents whose null result is enforced by tests — and shows that this apparatus has
teeth by reporting a pilot result that overturned our initial mechanism choice. Third, it reports
the abundance-amplification result itself, with the mechanism decomposition that identifies which
channel carries it. Fourth, it releases a deterministic, one-command-reproducible pipeline in which
every figure, table, and interval regenerates from recorded seeds.

Section 2 develops the theory and states the hypotheses as frozen. Section 3 situates the design in
the artificial-societies, collective-action, and language-model-agent literatures. Section 4
specifies the model, the epistemic scope of a rule-based study, the calibration pilot, and the
preregistration. Section 5 reports Study 1. Section 6 specifies Study 2 and marks its results as
pending. Section 7 discusses implications and limits.
