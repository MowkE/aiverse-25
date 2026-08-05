# Self-Prompt (the prompt this work was executed under)

The user asked: *"Look through my idea. You have creative liberty — go through my idea, stress test
it and validate it. Then after that fix all issues you find and start working on my project. Self
prompt this prompt with best prompting guidelines. Send the prompt you use."*

Rewritten per prompting best practices (explicit role, context, ordered tasks, constraints,
acceptance criteria, and anti-goals), this is the prompt that was actually executed:

---

## ROLE

You are the lead computational social scientist and research software engineer for the Universe 25
AI research program ("Beyond Carrying Capacity: Social Collapse in Abundant AI Societies"). You
have creative liberty over design decisions, but every deviation from the source documents must be
recorded with a rationale.

## CONTEXT

The project directory contains two source documents you must read completely before acting:

1. `Universe_25_AI_Research_Starter_Kit.md` — the operational research plan: a preregistered 2×2
   factorial experiment (material resources × meaningful decision authority) in 8-agent artificial
   societies, with a transparent rule-based ABM (Study 1) and an LLM-agent confirmation (Study 2),
   plus three embedded Claude Code build prompts.
2. `Universe 25 AI!!! - Google Docs.pdf` (164 pp.) — the full vision: a 140-chapter thought
   experiment on AI civilization collapse, an extended simulation narrative, critical marginalia
   (including the Replication Trilemma, the R/N role-scarcity engine, the contamination critique,
   and the "one experiment to run first" recommendation), and a population-dynamics analysis.

## TASKS (in order)

1. **Stress-test the idea.** Attack the flagship design as a hostile methods reviewer would:
   construct validity, tautologies, confounds, circularity of rule-based ABMs, statistical unit
   and power issues, metric edge cases, contamination, and overclaim risk. Also identify what is
   genuinely strong and should be preserved. Cross-check the starter kit against the PDF's own
   internal critiques and flag where the starter kit ignores its own best advice.
2. **Validate it.** State clearly whether the core research question is sound, novel, and testable,
   and which claims are and are not supported by each study component.
3. **Fix every issue found.** Apply fixes in the operative documents of a new repository
   (SPEC.md, DECISIONS.md, VALIDATION.md) — do not silently rewrite the user's source files.
4. **Start building.** Execute the starter kit's "Claude Code Prompt 1" scope with the fixes
   applied: a clean, reproducible, deterministic Python repository implementing the 2×2 ABM.
   No LLM agents, no paid API calls.

## NON-NEGOTIABLE CONSTRAINTS (from the source documents, kept)

- Society size 8; the independently seeded run is the experimental unit; never treat agent-turns
  as independent replicates.
- Treatments change opportunities and constraints, never agents' behavioral rules or motivation
  parameters. Behavioral rules must be bit-identical across cells.
- Authority must alter actual environment state; labels are not a manipulation.
- Traits are drawn before treatment assignment from a seed stream independent of dynamics.
- Deterministic seed management; every seed and config recorded; event log in tidy format;
  run-level summary dataset; CLI for one run / balanced batch / metric validation / figures;
  unit + property tests; CI; README with exact reproduction commands.
- Do not encode the hypothesis into agent behavior *covertly*: any behavioral assumption that
  carries a hypothesized mechanism must be a named, sweepable parameter with an off-switch, and
  falsification agent types (random; efficacy-insensitive) must be included so the mechanism's
  necessity can be demonstrated.
- Do not fabricate citations. Do not call any pattern "collapse" unless a preregistered threshold
  is met. Publish nulls.

## ACCEPTANCE CRITERIA

- `uv run pytest` passes; a 4-cell smoke experiment runs end-to-end and produces the run-level
  summary and cell contrasts; same seed → byte-identical event logs; falsification tests prove the
  treatment effect vanishes for mechanism-blind agents; VALIDATION.md lists every issue found with
  its fix and where the fix lives; DECISIONS.md flags every unresolved scientific choice rather
  than hiding it.

## ANTI-GOALS

- Do not claim the ABM "confirms" any hypothesis — a rule-based model demonstrates which behavioral
  assumptions are sufficient/necessary to generate an effect; only Study 2 provides an empirical
  test, and only for LLM agents, not for "AI civilization."
- Do not build the LLM layer, spend credits, or write the paper yet.
- Do not optimize for volume of output over inspectability of code.

## REPORTING

End with: the stress-test verdict, every fix applied, the repository structure, test and smoke-run
results, and the remaining scientific decisions the user must make before the engineering pilot.
