# 3. Related work

## 3.1 Minimal artificial societies

The design belongs to a tradition in which deliberately impoverished agent models are used to show
that a macro-level pattern requires far less machinery than intuition suggests. Schelling's
(1971 [VERIFY]) segregation model demonstrated that strong aggregate sorting follows from mild
individual preferences, without prejudice of the strength the outcome appears to imply. Epstein and
Axtell's (1996 [VERIFY]) Sugarscape showed how wealth distributions, migration, and trade emerge
from local rules over a resource landscape, and established the genre's characteristic claim form:
generative sufficiency, in which a mechanism is shown to be able to produce the pattern rather than
shown to be the pattern's cause in any particular empirical case. Axelrod's (1997 [VERIFY]) work on
the dissemination of culture and on tournament studies of cooperation extended the same logic to
convention and strategy. Our model is squarely in this lineage in its ambition — eight agents, five
traits, one decision seat — and departs from it in two respects: the mechanism carriers are exposed
as configuration parameters that can be switched off, and the analysis was preregistered before the
confirmatory batch existed.

In each of these three foundational models, the scarce quantity agents contend over is material or
spatial — sugar and terrain in Sugarscape, desirable neighborhoods in Schelling's model, payoff in
Axelrod's tournaments. Our design inverts that emphasis: in the abundant arm agents compete for
nothing material at all, and the only scarce thing in the environment is the seat from which a
decision binds.

## 3.2 Collective action, commons, and governance

The theoretical vocabulary for why collectively beneficial action fails to occur comes from Olson's
(1965 [VERIFY]) analysis of the logic of collective action, in which individually rational agents
under-supply a public good whose benefits they cannot be excluded from, and from Ostrom's
(1990 [VERIFY]) demonstration that real commons are frequently governed successfully through
institutional arrangements that formal models had declared impossible. Ostrom's design principles
are explicitly institutional, and several of them — collective-choice arrangements in which those
affected participate in modifying the rules, and nested or rotating authority — concern precisely
the distribution of access to consequential positions rather than the size of the resource.

That institutional dimension has largely not carried over into work on artificial agent
collectives, which has adopted the resource-depletion framing instead. GovSim (Piatti et al.,
2024 [VERIFY]) places language-model agents in shared-resource scenarios and reports that most
model populations fail to sustain the commons, with survival depending on the capacity to
deliberate about the resource: the dependent variable is the stock, and the independent variables
are model, prompt, and communication affordances. Our experiment is deliberately orthogonal. In the
abundant arm there is no stock to deplete, and the manipulated institutional variable is who may
bind the group.

## 3.3 Language-model agent societies

Persistent language-model agent populations have become a research object in their own right. Park
et al. (2023 [VERIFY]) showed that generative agents with memory, reflection, and planning produce
recognizable social behavior over extended interaction, and established the architectural pattern —
environment state owned by code, agents observing a restricted view — that Study 2 follows. Ashery,
Aiello, and Baronchelli (2025 [VERIFY]) showed that populations of language-model agents playing
naming games converge on shared conventions and develop collective biases absent in individual
agents, evidence that population-level structure in such systems is not simply the aggregate of
individual model tendencies. Neither line of work manipulates the distribution of consequential
authority or separates material from institutional constraint. The construct-validity question our
Study 2 asks is well posed only because this literature has established that such populations
exhibit stable, measurable, population-level behavior at all.

## 3.4 Calhoun as inspiration, not as evidence

Calhoun's rodent enclosures (1962 [VERIFY]; 1973 [VERIFY]) supply this paper's motivating anomaly
and nothing more. The interpretive claims attached to that work — the "behavioral sink," the
inference from crowded pens to human urban life — have been contested on grounds of confounding,
external validity, and the looseness of the analogy to human institutions. We take no position on
those disputes because our argument does not require one: we do not infer from mice to artificial
agents, and we do not treat the rodent results as evidence about our system. What we take from
Calhoun is a question his enclosure poses sharply and his critics do not dissolve, namely what
constrains a society whose material provisioning is unlimited. The contribution stands or falls on
the formal separation of $K_m$ and $K_s$ and on the factorial evidence below. For the same reason
we avoid the program's inherited vocabulary of societal failure when describing our own data; the
observed pattern is a reduction in participation and in willingness-normalized output under
concentrated role access, and that is what we call it.

## 3.5 Methodological standards for simulation

Two standards shape the reporting. The ODD protocol and its updates (Grimm et al., 2020 [VERIFY])
set the expectation that an agent-based model be described in sufficient detail — entities, state
variables, process overview and scheduling, design concepts, initialization, input, submodels — for
an independent group to reimplement it; Section 4 and the repository's specification document are
organized to meet it. Preregistration norms (Nosek et al., 2018 [VERIFY]) address a problem that
simulation research shares in aggravated form, since a simulationist can re-run an experiment under
new parameters at negligible cost and choose among the results. Our response is to freeze
parameters, sample size, seeds, outcomes, exclusion rules, and decision rules in a committed
document, to fix a master seed disjoint from the pilot's, and to commit in advance to publishing
null and contrary results without reframing. Applying these norms to a rule-based model raises a
question they were not designed to answer — what it means to preregister a hypothesis about code
one has written oneself — which Section 4.4 takes up directly.
