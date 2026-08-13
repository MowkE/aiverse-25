# Request for methodological criticism — role scarcity vs. resource scarcity in artificial societies

Samahith Thellakal · samahith@gmail.com · August 2026
*Asking for 15–20 minutes of criticism (conversation or written), not validation. The attached
one-page graphic summarizes results; a full reproducible repository is available.*

## The question

Calhoun's Universe 25 removed material scarcity from a mouse colony and the colony still
collapsed — the binding constraint appeared to be meaningful social positions, not resources.
AI-agent populations make this separable for the first time: compute is effectively abundant
while consequential roles remain structurally scarce. **Does scarcity of role access cause
dysfunction in artificial societies independently of material scarcity — and does abundance
amplify it?**

## What has been done

**Study 1 (complete).** A preregistered 2×2 factorial in transparent rule-based artificial
societies (8 agents, 40 rounds): material resources (constrained/abundant) × role access
(one fixed decision-holder vs. rotating). The run is the experimental unit; 200 seed-paired
runs per cell (800 total), frozen before execution (hypotheses, decision rules, seeds, no
exclusions; freeze and results are separate git commits). Design features I most want
challenged:

- *Mechanism-mapping framing.* Because hand-coded agents can only "confirm" what their rules
  imply, Study 1 claims only (a) sufficiency — the documented mechanism generates the pattern —
  and (b) necessity — the effect vanishes for mechanism-blind agent policies (`random`,
  `material-only`), enforced as failing tests, plus (c) variance estimates for power analysis.
- *Results.* All preregistered contrasts landed: role-access effect on participation +23 pts
  (constrained) / +34 pts (abundant); preregistered primary interaction +0.107 [0.096, 0.119]
  (participation) and +0.084 [0.055, 0.113] (output); manipulation check and falsification
  arms passed. A benevolent-decider robustness arm still shows ~−20 pts — structure, not
  leader selfishness. Mechanism decomposition attributes ~71% of the interaction to material
  crowding-out (participation costs bind under scarcity; abundance removes the competition —
  "abundance unmasks role scarcity").

**Study 2 (infrastructure complete, unexecuted).** An LLM-agent replication: same factorial,
agents are language models given structured action schemas, per-run memory, and no knowledge of
condition names or hypotheses (contamination-tested). A zero-cost engineering shakedown with
real model agents (four societies — four experimental units, explicitly non-evidential) surfaced
a real design problem: LLM agents respond to the material manipulation far more strongly than
rule agents, putting abundant cells at ~0.99 participation — a ceiling that would mask the
primary contrast. A blinded calibration protocol with a pre-committed parameter-selection rule
is written but unexecuted.

## The seven questions I need criticized

1. Is the ABM appropriately framed as mechanism mapping, or is the sufficiency/necessity
   structure still too close to assuming the conclusion?
2. Do the falsification controls (mechanism-blind agent policies that must show null effects)
   provide meaningful evidential leverage, or are they theater?
3. Should Study 2 confirm the same factorial effect, or test a narrower mechanism claim
   (e.g., only the interaction, or only the access effect under abundance)?
4. Is participation-cost calibration scientifically defensible, given the pre-committed
   selection rule (target 50–80% baseline participation, chosen blind to access effects)?
   Where is the line between calibration and manufacturing an effect?
5. Should calibration be performed separately per model, and does per-model calibration
   compromise cross-model comparison?
6. Confirmatory evidence via a wrapped CLI (small but unauditable ~500-token residual context,
   no sampling control) vs. direct API calls (fully controlled, costs money): is the former
   ever acceptable for preregistered runs?
7. What would make this publishable at JASSS or a comparable computational social science
   venue — and what would make you desk-reject it?

## What I am not asking

Not for endorsement, co-authorship, or data collection — strictly for the places where this
design would not survive review. The harshest version of that is the most useful.

*Materials: preregistration, frozen confirmatory report, decision log (16 entries recording
every deviation), full draft manuscript, and a deterministic one-command reproduction pipeline.*
