# Paper Outline + Evidence Map (ARS Phase 2) and Argument Blueprint (Phase 3)

Structure pattern: **Theory-driven two-study empirical simulation paper** (Introduction → Theory →
Study 1 → Study 2 → General Discussion), the standard shape for JASSS/computational social science.
Total target: ~9,500 words.

---

## Central thesis (one sentence)

Material abundance does not protect artificial societies from dysfunction; it removes the survival
activity that masks role scarcity, so concentrating access to consequential roles depresses
participation and collective output *more* under abundance — Calhoun's Universe 25 result
reproduced in a substrate with no bodies, no space, and no biology.

---

## Section outline with word counts and evidence map

### 1. Introduction (~1,100 words)
- Hook: Calhoun's Universe 25 — the colony died at 2,200 in a pen built for 3,840; space and food
  were never binding, roles were. [E1]
- The AI translation: multi-agent AI systems are heading toward persistent agent populations where
  compute is abundant but consequential positions are structurally scarce. [E2]
- Gap: multi-agent AI research studies cooperation under *resource* scarcity (e.g., commons
  dilemmas); the role-scarcity channel is untested and conflated with material scarcity.
- Contribution list: (i) a formal separation of material carrying capacity from social opportunity
  structure; (ii) a preregistered 2×2 factorial ABM with falsification controls; (iii) the
  abundance-amplification result; (iv) open, deterministic, one-command-reproducible pipeline.
- Evidence: [E1] Calhoun 1962, 1973 (verify); [E2] Park et al. 2023 generative agents; Piatti et
  al. 2024 GovSim (verify); repo docs/VALIDATION.md for the design rationale.

### 2. From material carrying capacity to social opportunity structure (~1,400 words)
- Logistic growth and K_m; abundance as K_m → ∞ (starter kit §2 formal seed).
- Social opportunity capacity K_s and the role-congestion ratio ρ_s = N/K_s; role *access* vs role
  *count* (docs/SPEC.md §4, VALIDATION C4).
- The crowding-out mechanism: participation in public life carries material opportunity cost under
  scarcity; abundance removes the competition, leaving role structure as the binding constraint —
  "abundance unmasks role scarcity" (docs/DECISIONS.md D4, pilot-revised).
- Positional goods and status scarcity as the human-social-science anchor. [E3: Hirsch 1976; Merton
  1968 Matthew effect — verify]
- Exit/voice framing for withdrawal. [E4: Hirschman 1970 — verify]
- Hypotheses: H1 participation, H2 output (co-primary main effects), H4 interaction (preregistered
  primary), manipulation check (formerly H3), exploratory mechanism decomposition (formerly H5) —
  exactly as frozen in docs/PREREGISTRATION.md §6.

### 3. Related work (~900 words)
- Classic artificial societies: Sugarscape, Schelling, Axelrod. [Epstein & Axtell 1996; Schelling
  1971; Axelrod 1997 — verify]
- Commons governance and collective action: Ostrom 1990; Olson 1965 (verify) → GovSim shows LLM
  populations often fail commons problems [Piatti et al. 2024 — verify].
- LLM-agent societies: generative agents, emergent conventions/collective bias. [Park et al. 2023;
  Ashery, Aiello & Baronchelli 2025 Science Advances — verify]
- Behavioral-sink literature and its critiques — position Calhoun as inspiration, not evidence
  (docs/SPEC.md §10 scope guards; starter-kit validity threats).
- Simulation methodology standards: ODD protocol, preregistration. [Grimm et al. 2020; Nosek et
  al. 2018 — verify]

### 4. Study 1: A transparent agent-based model (~2,600 words)
- 4.1 Design: 2×2 factorial, run as unit, seed-paired cells with common random numbers
  (SPEC §1, §4). Table 1: treatment matrix.
- 4.2 Environment and round structure: endowment/survival → public phase → binding decision →
  contribution → feedback; authority alters environment state (multiplier), not labels (SPEC §5).
- 4.3 Agents: heterogeneous traits drawn pre-treatment; efficacy dynamics; withdrawal;
  treatment-blind behavioral code (SPEC §3, §5; agents.py).
- 4.4 Epistemic scope — the honest ABM framing: mechanism mapping (sufficiency + necessity via
  falsification agents), not hypothesis confirmation (SPEC §2; VALIDATION C2). This subsection is
  a methodological contribution in itself.
- 4.5 Outcomes and metrics: participation rate; willingness-normalized output (the affordability
  confound fix, VALIDATION C3); influence Gini/nHHI as manipulation check (VALIDATION C1).
- 4.6 Calibration pilot and mechanism decomposition: the D4 reversal story — the psychological
  attention bonus fought the interaction; crowding-out carried it (PILOT_REPORT.md; DECISIONS D4,
  D12). Report as a worked example of pilot-driven model revision.
- 4.7 Preregistration and frozen confirmatory protocol: 200 pairs/cell, master seed disjoint from
  pilot, no exclusions, decision rules (PREREGISTRATION.md; freeze commit hash).
- Figures: Fig 1 model schematic (to make); Fig 2 cell means (outputs/confirmatory/figures);
  Fig 3 participation time-series.

### 5. Study 1 results (~1,300 words)
- Preregistered verdicts table (CONFIRMATORY_REPORT.md): all supported.
  - H4 participation interaction +0.107 [0.096, 0.119]; output +0.084 [0.055, 0.113].
  - Access effects: participation +23.3 pts constrained / +34.0 abundant; output +21.8 / +30.2.
  - Manipulation check PASS (Gini ~0.82 vs ~0.12); falsification arms PASS (|effect| < 0.005,
    CIs spanning zero).
- Robustness: attention-on, modal (benevolent) decider — concentration harms even when used
  benevolently (+20 pts effect); free-participation decomposition — crowding-out carries ~70% of
  the interaction, residual from survival-driven inactivity; calibration sweeps all preserve sign.
- Cohen's d 2.2–8.5 with the explicit caveat: deterministic-simulation effect sizes are not
  comparable to human-study benchmarks.

### 6. Study 2: LLM-agent confirmation (~1,200 words — placeholder until results land)
- Purpose: construct validity — do directional effects appear in agents whose behavior we did not
  author? Claims scoped to LLM-agent societies (SPEC §2).
- Architecture: code owns state; structured action schemas; per-run memory; cache/resume;
  contamination controls (banned-terms tests; agents never see condition names or hypotheses) —
  from docs/LLM_DESIGN.md / LLM_EXPERIMENT.md (in progress).
- Preregistration to mirror Study 1: frozen prompts/templates, power analysis from LLM pilot,
  budget disclosure.
- Results: PENDING — outline reserves: cell means table, sign comparison with Study 1, invalid-
  output and failure rates reported as results, framing-sensitivity check.

### 7. General discussion (~1,300 words)
- The abundance-amplification finding and its interpretation: abundance as unmasking, not as
  direct harm; connection back to Calhoun's remedy (role creation) and its limits.
- Benevolent-dictator result: structure, not selfishness, drives the harm.
- Implications for multi-agent AI system design: rotation/broad access as a design principle for
  agent collectives; why adding compute doesn't fix governance.
- Implications for social theory: a minimal, fully-inspectable existence proof that role-access
  concentration alone generates withdrawal dynamics.
- Limitations: N=8 fixed (no demographic channel — the full collapse signature N↑,H↓,P↓ is out of
  scope); rule-based mechanisms are authored (mitigated but not removed by falsification controls);
  one institution form (single decider); LLM results pending; no claims about consciousness,
  suffering, or human societies; the word "collapse" deliberately unused (SPEC §10).
- Future work: role-count sweep (R/N, the marginalia's "one experiment"); status-competition
  channel (v0.2); replication/population papers per the program roadmap.

### 8. Reproducibility statement (~250 words)
- Deterministic seeds, frozen configs, one-command regeneration; repo + data availability;
  freeze commit hash 36d5ac6; CI.

### 9. Ethical interpretation note (~150 words)
- Behavioral language only; symmetric uncertainty stance on agent moral status (per vision doc's
  own §135 critique).

---

## Argument blueprint (Phase 3)

**Chain 1 (main):** C: Role-access concentration causes participation/output decline independent
of material scarcity → E: H1/H2 effects in both resource conditions with CIs excluding zero →
R: treatments alter environment only; behavioral code identical across cells; falsification agents
show no effect, so the effect requires the motivational mechanism, not leakage.

**Chain 2 (headline):** C: Abundance amplifies the damage → E: preregistered H4 interaction
+0.107/+0.084, CIs exclude zero, frozen before data → R: decomposition shows the crowding-out
channel (participation cost binding under scarcity) carries the interaction; removing it flips the
sign, establishing mechanism, not just pattern.

**Chain 3 (methodological):** C: Rule-based ABMs can be used honestly for causal-mechanism claims
→ E: the C1–C4 repairs (manipulation check reclassification, willingness normalization, named
mechanism parameters, falsification controls) → R: each repair closes a specific circularity a
reviewer would raise; the pilot's D4 reversal demonstrates the controls have teeth.

**Counter-arguments and rebuttals:**
1. "You programmed the result." → Rebuttal: mechanism-mapping framing (SPEC §2); necessity shown
   via mechanism-blind agents; sufficiency claims are conditional and explicit; Study 2 tests
   agents we did not author.
2. "Effect sizes are absurd." → Rebuttal: acknowledged as deterministic-simulation artifacts;
   inference rests on preregistered direction + CI discipline, not magnitude benchmarks.
3. "Calhoun's work doesn't generalize / is itself contested." → Rebuttal: Calhoun is inspiration
   and framing only; no claim of cross-species inference; the contribution stands on its own
   formal separation of K_m and K_s.
4. "Rotation vs fixed decider is turnover, not role scarcity." → Rebuttal: named precisely as role
   *access* (C4); role-count sweep declared as follow-up, not smuggled in.
5. "8 agents is tiny." → Rebuttal: run-level inference over 800 runs; society size is a controlled
   constant, not a sample; scaling is future work.

**Logical flow:** Calhoun anomaly → formal K_m/K_s separation → hypotheses → transparent ABM with
honesty machinery → confirmatory results → mechanism decomposition → LLM construct-validity test →
design implications for AI collectives.

---

## Citation verification ledger

All external works cited above (Calhoun 1962, 1973; Hirsch 1976; Merton 1968; Hirschman 1970;
Epstein & Axtell 1996; Schelling 1971; Axelrod 1997; Ostrom 1990; Olson 1965; Park et al. 2023;
Piatti et al. 2024; Ashery et al. 2025; Grimm et al. 2020; Nosek et al. 2018) are cited from
memory and MUST pass /ars-citation-check with DOI verification before any draft is finalized.
None may appear in a draft without verification. No other citations may be added without entering
this ledger.
