# 2. From material carrying capacity to social opportunity structure

## 2.1 Two capacities

The standard formalism for a population under a material constraint is logistic growth,

$$\frac{dN}{dt} = rN\left(1 - \frac{N}{K_m}\right),$$

in which $K_m$ is the material carrying capacity: the population the environment can feed, house,
and power. The behavior of this system under abundance is unambiguous. As $K_m \to \infty$ the
braking term vanishes and $dN/dt \to rN$; the constraint simply lifts. Artificial agent populations
are the closest thing we have to a substrate in which that limit is approachable, because the
material requirements of an additional agent are a marginal cost in compute and storage rather than
a share of a fixed physical stock.

A society, however, is not only a stock of consumable resources. It is also a structure of
positions through which action becomes consequential — who proposes, who decides, whose decision
binds others. Following the program's formal seed, we define a second quantity, the **social
opportunity capacity** $K_s$: the number and diversity of consequential roles the society makes
available per unit time. A minimal congestion measure is the ratio

$$\rho_s = \frac{N}{K_s},$$

the number of agents per consequential role. The two capacities are logically independent. A
society can raise $K_m$ arbitrarily — provisioning every agent with more than it can spend — while
leaving $K_s$ untouched, because roles are defined by the institution rather than by the resource
base. This is precisely the configuration that Universe 25 approximated and that scaled multi-agent
architectures approximate by default: $K_m$ elastic, $K_s$ fixed at one.

Two constructs must be kept apart within $K_s$ itself. Role **count** is the number of
consequential positions available per round, and lowering it raises $\rho_s$ directly. Role
**access** is the distribution of occupancy of a fixed number of positions across agents over time.
The present experiment manipulates access, not count: exactly one binding decision role exists per
round in both arms, so $\rho_s = 8$ throughout, and the treatment varies whether that seat is
permanently occupied by one agent or rotates round-robin through all eight. This is a narrower
manipulation than a role-count sweep, and naming it correctly matters. A design that varied
rotation while calling it "role scarcity" would invite the objection that it manipulates turnover
rather than scarcity. We therefore reserve the term role access for what we manipulate, treat a
role-count sweep over $R/N \in \{1/8, 2/8, 4/8\}$ as the declared follow-up experiment, and make no
claim in this paper about the effect of the number of roles.

## 2.2 Why abundance should amplify rather than buffer

The intuition that abundance protects a society rests on a substitution assumption: with more
resources, agents can afford to do more of everything, including participate. The competing
intuition, which we formalize here, is that material scarcity does not merely suppress
participation but also *supplies* it with an alternative. Under scarcity, an agent's time and
budget are absorbed by survival activity that is unambiguously consequential for that agent: it
determines whether the agent can act at all in the next round. Public participation carries a
material opportunity cost, and its returns are uncertain and shared. Role structure, in this
regime, is only one of several things competing for an agent's engagement, and it is therefore
partially masked.

Remove the material constraint and the masking goes with it. Nothing now competes with public
life, and the question of whether an agent's public action can ever become consequential is left
standing alone. Where access to the consequential role is concentrated, most agents discover that
their proposals never bind, their efficacy erodes, and there is no survival task to absorb the
activity that public life is no longer returning. Abundance, on this account, does not cause the
dysfunction; it *unmasks* role scarcity by removing the competing demand that had been obscuring
it. The prediction is an interaction rather than a main effect: the damage from concentrated access
is larger under abundance than under constraint.

In a rule-based model this argument must be carried by something concrete, and we require that the
carrier be a named parameter rather than an implicit property of the behavioral equations. Two
implementations are available. The first is **material crowding-out**: public participation costs a
fixed amount from the agent's balance, which under scarcity competes directly with the survival
cost and under abundance is trivially affordable. The second is a **psychological survival-attention
bonus**: a positive term in the participation logit when survival stakes bind, representing
heightened engagement under pressure. Both are consistent with the verbal theory. They are not
consistent with each other in behavior: the calibration pilot showed that the attention bonus works
*against* the predicted interaction, because it asymmetrically rescues engaged agents in the
constrained cells and widens the constrained access effect, while material crowding-out produces
the interaction robustly. The pilot therefore forced a revision of the model's mechanism before the
preregistration was written. Section 4.6 reports that revision and its numbers in full; here we note
only that the theory as frozen is an opportunity-cost theory, not an attention theory, and that the
attention parameter was set to zero and retained solely as a robustness knob.

## 2.3 Anchors in social theory

The claim that a growing material base does not dissolve social scarcity is not new. Hirsch's
(1976 [VERIFY]) analysis of positional goods identifies a class of goods whose value depends on
relative standing, so that general economic growth cannot make everyone better supplied with them:
one cannot expand the supply of "being the one who decides" by expanding output. Merton's
(1968 [VERIFY]) account of cumulative advantage describes the complementary dynamic on the supply
side, in which recognition accrues to those who already hold it, so that access to consequential
positions concentrates further absent an institutional counterweight. Our concentrated arm is an
extreme, institutionally imposed version of that end state, and our broad arm is the minimal
counterweight: rotation.

For the response to role exclusion we draw on Hirschman's (1970 [VERIFY]) exit-and-voice framework.
An agent whose voice is structurally unable to bind has, in a society it cannot leave, only
degraded forms of exit: reduced participation, then withdrawal from public activity. Our model
implements exactly this ordering. Agents whose actions do not become consequential experience an
erosion of an internal efficacy state; low efficacy lowers the probability of public participation;
sustained low efficacy triggers a withdrawal state that further suppresses both participation and
contribution and from which agents recover if efficacy returns. We describe these as behavioral
states throughout, and make no claim that they correspond to experience of any kind.

## 2.4 Hypotheses as frozen

The following hypothesis structure is reproduced from the preregistration and was fixed before the
confirmatory batch was run. The estimator in every case is a difference in cell means over runs,
with 95% percentile bootstrap confidence intervals resampling runs within cells (B = 2,000, seeded);
decisions are two-sided, with an interval excluding zero as the decision rule.

**H4 (preregistered primary; interaction).** The role-access effect on each primary outcome is
larger under abundance than under constraint:
$\mathrm{DiD} = (\text{broad} - \text{concentrated} \mid \text{abundant}) - (\text{broad} -
\text{concentrated} \mid \text{constrained}) > 0$. The hypothesis is supported if the interval
excludes zero from above, theory-revising if it excludes zero from below, and inconclusive
otherwise. All three outcomes were committed to publication in advance.

**H1 and H2 (co-primary main effects).** Within each resource level, broad access yields a higher
participation rate (H1) and higher willingness-normalized output (H2) than concentrated access.

**Manipulation check.** Concentrated cells must show higher realized influence concentration than
broad cells on both indices. This was formerly stated as a hypothesis (H3) and was reclassified,
because a treatment that assigns decision authority to one agent cannot fail to concentrate
realized influence; testing it as a hypothesis would report a prediction that could not have been
falsified. It is retained as a diagnostic: a batch that fails it is invalid rather than
disconfirming.

**Exploratory mechanism decomposition.** The relative contribution of the crowding-out channel is
examined by re-running the design with the participation cost set to zero, and the dependence of
the effect on the efficacy response is examined through the mechanism-blind falsification policies.
Neither is a confirmatory test; both were specified in advance as reported robustness arms.
