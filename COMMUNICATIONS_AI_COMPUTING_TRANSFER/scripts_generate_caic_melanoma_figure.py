#!/usr/bin/env python3
"""Generate the CAIC melanoma treatment-response validation figure."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "figures_source" / "gse120575"
OUT = ROOT / "figures_png" / "figure_melanoma_treatment_response.png"


def first_row(name: str) -> pd.Series:
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path).iloc[0]


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    baseline = first_row("gse120575_baseline_summary.csv")
    all_cells = first_row("gse120575_all_cells_summary.csv")
    ranks = pd.read_csv(SRC / "gse120575_response_marker_ranks.csv")
    baseline_ranks = ranks[ranks["analysis"] == "Baseline"].copy()

    blue = "#0072B2"
    orange = "#D55E00"
    gray = "#8A8A8A"
    light = "#E8ECEF"
    dark = "#222222"

    fig = plt.figure(figsize=(7.4, 5.4), dpi=300)
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.05, 1.35],
        height_ratios=[1.0, 1.18],
        wspace=0.42,
        hspace=0.55,
    )

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # Panel A: cohort and validation design.
    ax_a.axis("off")
    ax_a.text(-0.11, 1.10, "A", transform=ax_a.transAxes, fontsize=11, fontweight="bold", va="top")
    ax_a.text(0.08, 0.96, "Melanoma checkpoint-immunotherapy", fontweight="bold", fontsize=7.9)
    ax_a.text(
        0.08,
        0.71,
        "GSE120575 immune single cells\nResponder vs non-responder\nanti-PD1 / anti-CTLA4 / combination",
        fontsize=7.2,
        linespacing=1.35,
    )
    labels = ["Baseline\ncells", "Baseline\npatients", "All\ncells", "All\npatients"]
    values = [
        int(baseline["n_cells"]),
        int(baseline["n_patients"]),
        int(all_cells["n_cells"]),
        int(all_cells["n_patients"]),
    ]
    x0 = [0.16, 0.38, 0.64, 0.86]
    for x, label, val in zip(x0, labels, values):
        circle = plt.Circle((x, 0.37), 0.085, transform=ax_a.transAxes, color=light, ec="#B8C2CC", lw=1)
        ax_a.add_patch(circle)
        ax_a.text(x, 0.39, f"{val:,}", transform=ax_a.transAxes, ha="center", va="center", fontweight="bold", fontsize=8)
        ax_a.text(x, 0.20, label, transform=ax_a.transAxes, ha="center", va="center", fontsize=7)
    ax_a.annotate(
        "",
        xy=(0.78, 0.56),
        xytext=(0.22, 0.56),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", lw=1.4, color=dark),
    )
    ax_a.text(0.5, 0.60, "PGAA-W response-marker ranking", transform=ax_a.transAxes, ha="center", fontsize=7)

    # Panel B: AUROC and AUPRC benchmark against simple baselines.
    ax_b.text(-0.14, 1.11, "B", transform=ax_b.transAxes, fontsize=11, fontweight="bold", va="top")
    methods = ["PGAA-W\nWasserstein", "Abs. mean\ndifference", "Abs.\nt-statistic"]
    auroc = [baseline["s1_wasserstein_auroc"], baseline["abs_mean_diff_auroc"], baseline["t_abs_auroc"]]
    auprc = [baseline["s1_wasserstein_auprc"], baseline["abs_mean_diff_auprc"], baseline["t_abs_auprc"]]
    x = np.arange(len(methods))
    w = 0.34
    ax_b.bar(x - w / 2, auroc, width=w, color=blue, label="AUROC")
    ax_b.bar(x + w / 2, auprc, width=w, color=orange, label="AUPRC")
    ax_b.axhline(float(baseline["random_auprc_baseline"]), color=gray, lw=1, ls="--", label="random AUPRC")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(methods)
    ax_b.set_ylim(0, 1.04)
    ax_b.set_ylabel("Marker recovery")
    ax_b.set_title("Baseline response-marker recovery")
    ax_b.legend(frameon=False, loc="upper right", ncol=1, handlelength=1.8)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)

    # Panel C: enrichment in top ranked genes.
    ax_c.text(-0.21, 1.14, "C", transform=ax_c.transAxes, fontsize=11, fontweight="bold", va="top")
    cuts = [50, 100, 250, 500]
    base_enrich = [baseline[f"s1_wasserstein_top{k}_enrichment"] for k in cuts]
    all_enrich = [all_cells[f"s1_wasserstein_top{k}_enrichment"] for k in cuts]
    x = np.arange(len(cuts))
    ax_c.bar(x - 0.17, base_enrich, width=0.34, color=orange, label="Baseline")
    ax_c.bar(x + 0.17, all_enrich, width=0.34, color=blue, label="All cells")
    ax_c.axhline(1, color=gray, lw=1, ls="--")
    ax_c.set_xticks(x)
    ax_c.set_xticklabels([f"Top {k}" for k in cuts])
    ax_c.set_ylabel("Observed / random")
    ax_c.set_title("Response-state marker enrichment", fontsize=8.4, pad=9)
    ax_c.set_ylim(0, max(base_enrich) * 1.18)
    ax_c.legend(frameon=False)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)

    # Panel D: selected marker ranks.
    ax_d.text(-0.13, 1.11, "D", transform=ax_d.transAxes, fontsize=11, fontweight="bold", va="top")
    genes = ["NKG7", "PRF1", "GZMB", "CCL4", "CCR7", "HAVCR2", "SELL", "WARS", "CXCL13", "PDCD1", "TCF7", "ENTPD1"]
    plot_df = baseline_ranks[baseline_ranks["gene"].isin(genes)].copy()
    plot_df["gene"] = pd.Categorical(plot_df["gene"], categories=genes[::-1], ordered=True)
    plot_df = plot_df.sort_values("gene")
    y = np.arange(plot_df.shape[0])
    colors = [orange if row["signed_mean_diff"] > 0 else blue for _, row in plot_df.iterrows()]
    ax_d.scatter(plot_df["rank_s1_wasserstein"], y, c=colors, s=35, edgecolors="white", linewidths=0.5)
    ax_d.set_xscale("log")
    ax_d.set_yticks(y)
    ax_d.set_yticklabels(plot_df["gene"])
    ax_d.set_xlabel("PGAA-W rank among 20,741 tested genes")
    ax_d.set_title("Predeclared melanoma response-state markers")
    ax_d.grid(axis="x", color="#DDDDDD", lw=0.6)
    ax_d.spines["top"].set_visible(False)
    ax_d.spines["right"].set_visible(False)

    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.08)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
