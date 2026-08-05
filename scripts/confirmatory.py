"""Confirmatory batch per docs/PREREGISTRATION.md.

Runs the frozen 200-pairs/cell batch (master seed 314159265), the five
robustness/falsification arms, applies the preregistered decision rules, and
writes docs/CONFIRMATORY_REPORT.md plus data/confirmatory_run_summary.csv.
Everything is regenerable from recorded seeds; do not edit the frozen config.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from universe25.analysis import bootstrap_contrasts, full_report
from universe25.config import BatchConfig, load_batch_config, with_policy
from universe25.figures import make_all_figures
from universe25.runner import run_batch
from universe25.validate import validate_summary

BOOT_SEED = 1
N_BOOT = 2000
ROBUSTNESS_PAIRS = 30


def robustness_arms(frozen: BatchConfig) -> dict[str, BatchConfig]:
    run = frozen.run
    arms = {
        "attention_on": replace(run, behavior=replace(run.behavior, survival_attention_bonus=0.8)),
        "modal_decider": replace(run, decider_rule="modal"),
        "free_participation": replace(run, economy=replace(run.economy, participation_cost=0.0)),
        "policy_random": with_policy(run, "random"),
        "policy_material_only": with_policy(run, "material_only"),
    }
    return {
        name: BatchConfig(
            master_seed=frozen.master_seed, n_pairs=ROBUSTNESS_PAIRS, run=cfg,
            output_dir=f"outputs/confirmatory_{name}",
        )
        for name, cfg in arms.items()
    }


def verdict(row: pd.Series, predicted_positive: bool) -> str:
    lo, hi = row["ci_lo"], row["ci_hi"]
    if lo > 0:
        return "SUPPORTED" if predicted_positive else "REVERSED"
    if hi < 0:
        return "REVERSED" if predicted_positive else "SUPPORTED"
    return "INCONCLUSIVE"


def main() -> None:
    frozen = load_batch_config(ROOT / "configs" / "confirmatory.toml")
    git_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()

    print("Confirmatory batch (frozen):", flush=True)
    summary = run_batch(frozen)
    failures = validate_summary(summary)
    print(f"  {len(summary)} runs; validation: {failures if failures else 'PASS'}", flush=True)

    report = full_report(summary, n_boot=N_BOOT, seed=BOOT_SEED)
    contrasts = report["contrasts"]

    verdict_rows = []
    for outcome in ("participation_rate", "output_norm"):
        oc = contrasts[contrasts["outcome"] == outcome].set_index("contrast")
        verdict_rows.append({
            "hypothesis": f"H4 interaction ({outcome})",
            "estimate": oc.loc["interaction", "estimate"],
            "ci_lo": oc.loc["interaction", "ci_lo"],
            "ci_hi": oc.loc["interaction", "ci_hi"],
            "verdict": verdict(oc.loc["interaction"], predicted_positive=True),
        })
        for level in ("constrained", "abundant"):
            key = f"access_effect_{level}"
            label = "H1" if outcome == "participation_rate" else "H2"
            verdict_rows.append({
                "hypothesis": f"{label} access effect, {level} ({outcome})",
                "estimate": oc.loc[key, "estimate"],
                "ci_lo": oc.loc[key, "ci_lo"],
                "ci_hi": oc.loc[key, "ci_hi"],
                "verdict": verdict(oc.loc[key], predicted_positive=True),
            })
    verdicts = pd.DataFrame(verdict_rows)

    manip = contrasts[
        (contrasts["outcome"].isin(("influence_gini", "influence_nhhi")))
        & (contrasts["contrast"].str.startswith("access_effect"))
    ]
    manip_pass = bool((manip["ci_hi"] < 0).all())

    print("Robustness arms:", flush=True)
    arm_rows = []
    for name, batch in robustness_arms(frozen).items():
        arm_summary = run_batch(batch)
        t = bootstrap_contrasts(arm_summary, "participation_rate", n_boot=1000, seed=BOOT_SEED)
        t = t[t["contrast"].isin(["access_effect_abundant", "interaction"])]
        arm_rows.append(t.assign(arm=name))
        print(f"  {name}: {len(arm_summary)} runs", flush=True)
    arms_table = pd.concat(arm_rows, ignore_index=True)

    falsification = arms_table[
        arms_table["arm"].isin(["policy_random", "policy_material_only"])
        & (arms_table["contrast"] == "access_effect_abundant")
    ]
    falsification_pass = bool((falsification["estimate"].abs() < 0.03).all())

    events = pd.read_parquet(ROOT / "outputs" / "confirmatory" / "events.parquet")
    make_all_figures(summary, events, ROOT / "outputs" / "confirmatory" / "figures")

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    summary.to_csv(data_dir / "confirmatory_run_summary.csv", index=False)

    lines = [
        "# Confirmatory Report — Study 1 ABM batch",
        "",
        f"Executed per docs/PREREGISTRATION.md at freeze commit `{git_hash}`.",
        f"Master seed 314159265; {frozen.n_pairs} pairs/cell; validation: "
        f"{'PASS' if not failures else failures}.",
        "",
        "## Preregistered verdicts",
        "",
        verdicts.to_markdown(index=False),
        "",
        f"**Manipulation check:** {'PASS' if manip_pass else 'FAIL'} "
        "(influence concentration higher in concentrated cells; access effect on both "
        "concentration indices negative with CI excluding zero).",
        "",
        f"**Falsification arms:** {'PASS' if falsification_pass else 'FAIL'} "
        "(mechanism-blind policies show |access effect| < 0.03 on participation).",
        "",
        "## Cell means",
        "",
        report["cell_means"].to_markdown(index=False),
        "",
        "## All preregistered contrasts",
        "",
        contrasts.to_markdown(index=False),
        "",
        "## Standardized effects",
        "",
        report["standardized"].to_markdown(index=False),
        "",
        "## Robustness and falsification arms (participation_rate)",
        "",
        arms_table.to_markdown(index=False),
        "",
        "## Reproduction",
        "",
        "```bash",
        "uv run python scripts/confirmatory.py",
        "```",
        "Run-level data: `data/confirmatory_run_summary.csv`. Event logs regenerate",
        "deterministically from the recorded seeds in `configs/confirmatory.toml`.",
    ]
    (ROOT / "docs" / "CONFIRMATORY_REPORT.md").write_text("\n".join(lines))
    print("\nReport -> docs/CONFIRMATORY_REPORT.md", flush=True)


if __name__ == "__main__":
    main()
