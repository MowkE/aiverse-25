# 8. Reproducibility statement

Every number, table, and figure in Section 5 regenerates from the repository with one command,
`uv run python scripts/confirmatory.py`, executed against the frozen configuration file
`configs/confirmatory.toml`. That file was committed unchanged at the preregistration freeze commit
`36d5ac6` (full hash `36d5ac6724d524905d0aa356952286ec3e129b8e`), which the confirmatory report
records, and it carries the master seed 314159265, the 200-pairs-per-cell sample size, and every
economic and behavioral parameter used in the confirmatory batch.

The simulation is deterministic. All randomness derives from `numpy` `SeedSequence` streams spawned
from the master seed and the pair index, with separate streams for traits, structure, and dynamics,
so that identical seeds reproduce byte-identical event logs — a property asserted by the test suite
rather than assumed. Seed-paired cells share their trait and structure streams by construction. No
run in the batch was excluded, and no alternative master seed was executed.

Released artifacts comprise the run-level summary (`data/confirmatory_run_summary.csv`, 800 rows),
the tidy per-round event logs, the pilot batch with all sweep variants and power curves, the
robustness and falsification arms, the figures reproduced here (`outputs/confirmatory/figures/`),
the frozen configuration files, the preregistration, the specification, the decision log, and the
validation report. Event logs regenerate deterministically from the recorded seeds, so the archive
is verifiable rather than merely deposited.

The Study 2 layer is included in the same repository with its mock provider, contract tests,
contamination tests, cache-and-resume tests, and cost estimator; no billable call has been made and
the mock smoke run is reproducible offline. Continuous integration runs linting, type checking, and
the full test suite, including the falsification and invariant tests on which the paper's causal
interpretation depends.
