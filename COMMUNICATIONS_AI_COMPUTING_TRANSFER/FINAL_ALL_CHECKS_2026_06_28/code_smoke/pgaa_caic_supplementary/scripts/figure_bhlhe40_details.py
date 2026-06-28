#!/usr/bin/env python3
"""Build Supplementary Figure 5: Adamson BHLHE40 perturbation details."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "figure_source_data" / "adamson_gene_level_scores.csv"
DISTRIBUTIONS = ROOT / "figure_source_data" / "adamson_bhlhe40_distribution.csv"
OUTPUTS = [
    ROOT / "figures_png" / "figure_s2_bhlhe40.png",
    ROOT / "COMMUNICATIONS_AI_COMPUTING_TRANSFER" / "figures_png" / "figure_s2_bhlhe40.png",
]


def main() -> None:
    scores = pd.read_csv(SCORES)
    scores = scores[scores["perturbation"] == "BHLHE40_pDS258"].copy()
    distributions = pd.read_csv(DISTRIBUTIONS)
    marker_genes = list(distributions["gene"].drop_duplicates())

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.dpi": 300,
        }
    )

    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(10.8, 5.1),
        gridspec_kw={"width_ratios": [1.0, 1.22], "wspace": 0.34},
    )

    # Panel a: gene-level score map.
    ax_a.scatter(
        scores["W_observed"],
        scores["S2"],
        s=10,
        color="#CFCFCF",
        alpha=0.62,
        linewidth=0,
        zorder=1,
    )
    markers = scores[scores["gene"].isin(marker_genes)].copy()
    ax_a.scatter(
        markers["W_observed"],
        markers["S2"],
        s=62,
        color="#CC79A7",
        edgecolor="black",
        linewidth=0.6,
        zorder=3,
    )

    label_offsets = {
        "HSPA5": (0.006, 0.006),
        "XBP1": (-0.016, 0.006),
        "DDIT3": (0.006, 0.002),
        "DNAJC3": (0.006, -0.006),
        "PPP1R15A": (0.006, -0.011),
        "TRIB3": (0.006, 0.006),
        "ATF4": (0.006, -0.002),
        "DNAJB9": (0.006, -0.010),
    }
    for _, row in markers.iterrows():
        dx, dy = label_offsets.get(row["gene"], (0.006, 0.004))
        ax_a.text(
            row["W_observed"] + dx,
            row["S2"] + dy,
            row["gene"],
            fontsize=8.5,
            fontstyle="italic",
            ha="left" if dx >= 0 else "right",
            va="center",
            zorder=4,
        )

    ax_a.set_title("a  BHLHE40 gene-level score map", loc="left", fontweight="bold", pad=8)
    ax_a.set_xlabel("Wasserstein statistic S1")
    ax_a.set_ylabel("Persistence statistic S2")
    ax_a.grid(alpha=0.24, linewidth=0.8)
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.set_xlim(-0.01, max(0.68, scores["W_observed"].max() * 1.05))
    ax_a.set_ylim(-0.02, max(0.49, scores["S2"].max() * 1.08))
    ax_a.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#CC79A7",
                markeredgecolor="black",
                markersize=8,
                label="UPR marker genes",
            )
        ],
        frameon=False,
        loc="upper right",
    )

    # Panel b: distributions summarized as paired boxplots.
    values = []
    positions = []
    colors = []
    tick_positions = []
    for idx, gene in enumerate(["HSPA5", "XBP1", "DDIT3", "DNAJC3", "PPP1R15A", "TRIB3"]):
        base = idx * 2.4
        tick_positions.append(base + 0.35)
        for offset, group, color in [
            (0.0, "control", "#D9D9D9"),
            (0.7, "BHLHE40_perturbed", "#66C2A5"),
        ]:
            vals = distributions[
                (distributions["gene"] == gene) & (distributions["group"] == group)
            ]["expression"].to_numpy()
            values.append(vals)
            positions.append(base + offset)
            colors.append(color)

    bp = ax_b.boxplot(
        values,
        positions=positions,
        widths=0.58,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.1},
        whiskerprops={"color": "#666666", "linewidth": 0.8},
        capprops={"color": "#666666", "linewidth": 0.8},
        boxprops={"edgecolor": "#666666", "linewidth": 0.8},
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    ax_b.set_title(
        "b  BHLHE40 perturbation: available UPR marker distributions",
        loc="left",
        fontweight="bold",
        pad=8,
    )
    ax_b.set_ylabel("log(CPM+1) expression")
    ax_b.set_xticks(tick_positions)
    ax_b.set_xticklabels(["HSPA5", "XBP1", "DDIT3", "DNAJC3", "PPP1R15A", "TRIB3"], rotation=30, ha="right")
    ax_b.grid(axis="y", alpha=0.24, linewidth=0.8)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)
    ax_b.legend(
        handles=[
            Line2D([0], [0], marker="s", color="none", markerfacecolor="#D9D9D9", markeredgecolor="#666666", markersize=8, label="Control"),
            Line2D([0], [0], marker="s", color="none", markerfacecolor="#66C2A5", markeredgecolor="#666666", markersize=8, label="BHLHE40 perturbed"),
        ],
        frameon=False,
        loc="upper right",
    )

    fig.tight_layout()
    for out in OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
