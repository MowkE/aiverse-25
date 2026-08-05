# Draft status (ARS Phase 4)

Drafted against `paper/OUTLINE.md` (approved) and `paper/CONFIG.md`. All result numbers trace to
`docs/CONFIRMATORY_REPORT.md` or `outputs/pilot/PILOT_REPORT.md`. Citations are restricted to the
outline's verification ledger and every in-text citation carries `[VERIFY]`. No reference list yet
(pending `/ars-citation-check`). No figures generated.

## Word counts vs budget

| File | Section | Budget | Actual | Δ | Δ% |
|---|---|---:|---:|---:|---:|
| 01_introduction.md | 1. Introduction | 1,100 | 1,068 | −32 | −2.9% |
| 02_theory.md | 2. Carrying capacity → opportunity structure | 1,400 | 1,371 | −29 | −2.1% |
| 03_related_work.md | 3. Related work | 900 | 956 | +56 | +6.2% |
| 04_study1_methods.md | 4. Study 1 methods | 2,600 | 2,712 | +112 | +4.3% |
| 05_study1_results.md | 5. Study 1 results | 1,300 | 1,368 | +68 | +5.2% |
| 06_study2_placeholder.md | 6. Study 2 (placeholder) | 1,200 | 1,276 | +76 | +6.3% |
| 07_discussion.md | 7. General discussion | 1,300 | 1,409 | +109 | +8.4% |
| 08_reproducibility.md | 8. Reproducibility statement | 250 | 269 | +19 | +7.6% |
| 09_ethics_note.md | 9. Ethical interpretation note | 150 | 170 | +20 | +13.3% |
| **Total** | | **10,200** | **10,599** | **+399** | **+3.9%** |

Counts are `wc -w` on the Markdown source, so they include table rows (Tables 1 and 2), display
equations, the Section 6 status blockquote, and file paths — roughly 250 words of display material
that would not count as manuscript prose. Prose total is therefore ≈10,350.

**Budget reconciliation note.** OUTLINE.md states a total target of ~9,500 words, but its
per-section budgets sum to 10,200; CONFIG.md specifies 9,000–10,000 excluding references and
appendices. The draft was written to the per-section budgets. Bringing the manuscript inside the
CONFIG band requires a further ~400-word trim, most easily taken from §3.1 (Sugarscape/Schelling
detail), §4.2 (round-phase enumeration, which duplicates SPEC §5), and §7.3 (design implications).

## Coverage checks

- Section 06 contains no invented Study 2 results; six results slots are marked
  `[PENDING: Study 2 results]` and the section opens with an explicit status blockquote.
- "Collapse" appears zero times across all nine files (verified by grep).
- No claims about consciousness, suffering, or human societies; the three occurrences of those
  terms are explicit disclaimers (§6.1, §7.5, §9).
- All 14 ledger works are cited with `[VERIFY]`; no citation outside the ledger appears.
- Five blueprint counter-arguments are addressed in place: (1) "you programmed the result" → §4.4
  and §5.3; (2) "effect sizes are absurd" → §5.5; (3) "Calhoun doesn't generalize" → §3.4;
  (4) "rotation is turnover, not role scarcity" → §2.1, §4.1, §7.5; (5) "8 agents is tiny" → §4.1,
  §7.5.
- D4/D12 pilot reversal reported as a pilot-driven model revision in §4.6, referenced forward from
  §2.2 and back from §5.4.
- Figures referenced but not generated: Figure 1 (model schematic, placeholder, §4.2), Figure 2
  (`outputs/confirmatory/figures/cell_means.png`, §5.1), Figure 3
  (`outputs/confirmatory/figures/participation_timeseries.png`, §5.1).

## Not yet written

Title page, abstract, keywords, reference list, appendices, ODD-format model description appendix,
AI-usage disclosure (`/ars-disclosure`), and Figure 1 itself.
