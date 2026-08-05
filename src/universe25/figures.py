"""Publication figures for batch outputs.

Encoding rules (dataviz method): color follows the entity — role access owns
the hue (broad = blue #2a78d6, concentrated = orange #eb6834, a CVD-validated
pair); the resource factor is carried by position (bar groups) or line style
(solid/dashed), never by extra hues. One axis per plot; recessive grid; direct
labels over legends where space allows.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analysis import MANIPULATION_CHECKS, PRIMARY_OUTCOMES, bootstrap_contrasts
from .config import ACCESS_LEVELS, RESOURCE_LEVELS

ACCESS_COLOR = {"broad": "#2a78d6", "concentrated": "#eb6834"}
RESOURCE_STYLE = {"constrained": "--", "abundant": "-"}
TEXT = "#3a3a37"
GRID = "#e4e4e0"

OUTCOME_LABELS = {
    "participation_rate": "Public participation rate",
    "output_norm": "Collective output (willingness-normalized)",
    "influence_gini": "Influence concentration (Gini)",
    "influence_nhhi": "Influence concentration (norm. HHI)",
}


def _style_axis(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _bootstrap_ci_of_mean(vals: np.ndarray, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = np.array([
        vals[rng.integers(0, vals.size, vals.size)].mean() for _ in range(n_boot)
    ])
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def cell_means_figure(summary: pd.DataFrame, out_path: Path) -> None:
    outcomes = list(PRIMARY_OUTCOMES) + ["influence_gini"]
    fig, axes = plt.subplots(1, len(outcomes), figsize=(4.0 * len(outcomes), 3.4))
    x = np.arange(len(RESOURCE_LEVELS))
    width = 0.36
    for ax, outcome in zip(axes, outcomes):
        for k, access in enumerate(ACCESS_LEVELS):
            means, los, his = [], [], []
            for r in RESOURCE_LEVELS:
                vals = summary.loc[
                    (summary["resources"] == r) & (summary["access"] == access), outcome
                ].to_numpy(dtype=float)
                means.append(vals.mean())
                lo, hi = _bootstrap_ci_of_mean(vals)
                los.append(means[-1] - lo)
                his.append(hi - means[-1])
            pos = x + (k - 0.5) * (width + 0.04)
            ax.bar(
                pos, means, width, color=ACCESS_COLOR[access], zorder=3,
                label=f"{access} access",
            )
            ax.errorbar(
                pos, means, yerr=[los, his], fmt="none", ecolor=TEXT,
                elinewidth=1.0, capsize=3, zorder=4,
            )
        ax.set_xticks(x, [r.capitalize() for r in RESOURCE_LEVELS])
        ax.set_title(OUTCOME_LABELS.get(outcome, outcome), fontsize=10, color=TEXT)
        _style_axis(ax)
    axes[0].legend(frameon=False, fontsize=9, labelcolor=TEXT)
    fig.suptitle(
        "Cell means with 95% bootstrap CIs (run-level; runs are the unit)",
        fontsize=11, color=TEXT,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def participation_timeseries_figure(events: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    active = events[events["active"]]
    series = (
        active.groupby(["resources", "access", "round"])["participated"].mean().reset_index()
    )
    for r in RESOURCE_LEVELS:
        for a in ACCESS_LEVELS:
            s = series[(series["resources"] == r) & (series["access"] == a)]
            ax.plot(
                s["round"], s["participated"], RESOURCE_STYLE[r],
                color=ACCESS_COLOR[a], linewidth=2.0, zorder=3,
            )
            ax.annotate(
                f"{a[:4]}/{r[:4]}", xy=(s["round"].iloc[-1], s["participated"].iloc[-1]),
                xytext=(4, 0), textcoords="offset points",
                fontsize=8, color=ACCESS_COLOR[a], va="center",
            )
    if events["in_shock"].any():
        sr = events.loc[events["in_shock"], "round"]
        ax.axvspan(sr.min() - 0.5, sr.max() + 0.5, color=GRID, alpha=0.5, zorder=1)
    ax.set_xlabel("Round", color=TEXT, fontsize=10)
    ax.set_ylabel("Participation rate (active agents)", color=TEXT, fontsize=10)
    ax.set_title(
        "Participation by round, mean over runs (solid = abundant, dashed = constrained; shaded = shock)",
        fontsize=10, color=TEXT,
    )
    _style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def contrast_figure(summary: pd.DataFrame, out_path: Path, seed: int = 0) -> None:
    outcomes = list(PRIMARY_OUTCOMES) + list(MANIPULATION_CHECKS)
    tables = [bootstrap_contrasts(summary, o, seed=seed) for o in outcomes]
    df = pd.concat(tables, ignore_index=True)
    df = df[df["contrast"].isin(["access_effect_constrained", "access_effect_abundant", "interaction"])]
    fig, ax = plt.subplots(figsize=(7.5, 0.55 * len(df) + 1.5))
    ypos = np.arange(len(df))[::-1]
    colors = [
        ACCESS_COLOR["broad"] if "abundant" in c else
        (ACCESS_COLOR["concentrated"] if "constrained" in c else TEXT)
        for c in df["contrast"]
    ]
    ax.hlines(ypos, df["ci_lo"], df["ci_hi"], color=colors, linewidth=2.0, zorder=3)
    ax.plot(df["estimate"], ypos, "o", color=TEXT, markersize=5, zorder=4)
    ax.axvline(0, color=GRID, linewidth=1.2, zorder=1)
    ax.set_yticks(ypos, [f"{o}\n{c}" for o, c in zip(df["outcome"], df["contrast"])], fontsize=8)
    ax.set_xlabel("Effect estimate (95% bootstrap CI, clustered by run)", color=TEXT, fontsize=9)
    ax.set_title("Treatment contrasts — interaction is the preregistered primary", fontsize=10, color=TEXT)
    _style_axis(ax)
    ax.yaxis.grid(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def make_all_figures(summary: pd.DataFrame, events: pd.DataFrame, out_dir: str | Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [
        out / "cell_means.png",
        out / "participation_timeseries.png",
        out / "contrasts.png",
    ]
    cell_means_figure(summary, paths[0])
    participation_timeseries_figure(events, paths[1])
    contrast_figure(summary, paths[2])
    return paths
