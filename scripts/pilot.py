"""Engineering pilot: main batch + mechanism controls + robustness sweeps.

Executes the pilot plan agreed in DECISIONS D1/D4/D5/D7/D12:
  - main:                 default model, 30 pairs (120 runs)
  - d4_attention_off:     survival_attention_bonus = 0 (H4 mechanism control)
  - d12_free_participation: participation_cost = 0 (removes affordability censoring)
  - d5_modal_decider:     benevolent decider (modal proposal instead of self)
  - one-at-a-time sweeps of the D1/D7 calibration knobs

Writes outputs/pilot/<variant>/ plus outputs/pilot/PILOT_REPORT.md and the
power analysis. Pilot results inform calibration and power only — they
confirm nothing (SPEC section 2).
"""

from __future__ import annotations

import sys
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from universe25.analysis import bootstrap_contrasts, contrasts_point, full_report
from universe25.config import BatchConfig, RunConfig
from universe25.figures import make_all_figures
from universe25.power import power_report
from universe25.runner import run_batch

MASTER_SEED = 20260805
BASE = RunConfig()
OUT = Path("outputs/pilot")


def beh(**kw) -> RunConfig:
    return replace(BASE, behavior=replace(BASE.behavior, **kw))


def eco(**kw) -> RunConfig:
    return replace(BASE, economy=replace(BASE.economy, **kw))


NAMED_VARIANTS: dict[str, tuple[RunConfig, int]] = {
    "main": (BASE, 30),
    "d4_attention_off": (beh(survival_attention_bonus=0.0), 15),
    "d12_free_participation": (eco(participation_cost=0.0), 15),
    "d5_modal_decider": (replace(BASE, decider_rule="modal"), 15),
}

SWEEPS: dict[str, tuple[RunConfig, int]] = {
    f"sweep_{field}_{value}": (beh(**{field: value}), 10)
    for field, values in {
        "lambda_up": (0.25, 0.75),
        "lambda_down": (0.04, 0.16),
        "efficacy_sensitivity": (1.5, 3.5),
        "withdrawn_penalty": (-1.5, -3.5),
        "withdraw_patience": (2, 5),
        "survival_attention_bonus": (0.4, 1.2),
    }.items()
    for value in values
}


def run_variant(name: str, cfg: RunConfig, n_pairs: int) -> pd.DataFrame:
    batch = BatchConfig(master_seed=MASTER_SEED, n_pairs=n_pairs, run=cfg,
                        output_dir=str(OUT / name))
    t0 = time.time()
    summary = run_batch(batch)
    print(f"  {name}: {len(summary)} runs in {time.time() - t0:.1f}s", flush=True)
    return summary


def contrast_rows(name: str, summary: pd.DataFrame) -> list[dict]:
    rows = []
    for outcome in ("participation_rate", "output_norm"):
        c = contrasts_point(summary, outcome)
        rows.append({"variant": name, "outcome": outcome, **c})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    summaries: dict[str, pd.DataFrame] = {}

    print("Named variants:")
    for name, (cfg, n_pairs) in NAMED_VARIANTS.items():
        summaries[name] = run_variant(name, cfg, n_pairs)
        all_rows += contrast_rows(name, summaries[name])

    print("Calibration sweeps:")
    for name, (cfg, n_pairs) in SWEEPS.items():
        summary = run_variant(name, cfg, n_pairs)
        all_rows += contrast_rows(name, summary)

    contrasts = pd.DataFrame(all_rows)
    contrasts.to_csv(OUT / "variant_contrasts.csv", index=False)

    ci_tables = []
    for name in NAMED_VARIANTS:
        for outcome in ("participation_rate", "output_norm"):
            t = bootstrap_contrasts(summaries[name], outcome, n_boot=1000, seed=1)
            ci_tables.append(t.assign(variant=name))
    cis = pd.concat(ci_tables, ignore_index=True)
    cis.to_csv(OUT / "named_variant_cis.csv", index=False)

    power = power_report(summaries["main"], n_sims=1000)
    power.to_csv(OUT / "power_curve.csv", index=False)

    events = pd.read_parquet(OUT / "main" / "events.parquet")
    make_all_figures(summaries["main"], events, OUT / "figures")

    report = full_report(summaries["main"], n_boot=2000, seed=1)
    write_report(contrasts, cis, power, report)
    print(f"\nPilot complete -> {OUT / 'PILOT_REPORT.md'}")


def write_report(contrasts, cis, power, report) -> None:
    lines = [
        "# Pilot Report",
        "",
        "Engineering pilot only: informs calibration, mechanism decomposition, and power.",
        "Nothing here is confirmatory (SPEC section 2). Main batch: 30 pairs/cell (120 runs).",
        "",
        "## Main-batch cell means",
        "",
        report["cell_means"].to_markdown(index=False),
        "",
        "## Main-batch contrasts (95% bootstrap CIs, clustered by run)",
        "",
        report["contrasts"].to_markdown(index=False),
        "",
        "## Standardized effects (Cohen's d, access effect)",
        "",
        report["standardized"].to_markdown(index=False),
        "",
        "## Named variants (mechanism decomposition)",
        "",
        cis[cis["contrast"] == "interaction"].to_markdown(index=False),
        "",
        "## All variant point contrasts",
        "",
        contrasts.to_markdown(index=False),
        "",
        "## Power curve (from main-batch moments)",
        "",
        power.to_markdown(index=False),
    ]
    (OUT / "PILOT_REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
