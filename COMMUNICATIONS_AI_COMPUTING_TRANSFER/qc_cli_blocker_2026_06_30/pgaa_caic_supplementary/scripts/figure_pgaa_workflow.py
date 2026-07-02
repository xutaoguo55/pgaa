#!/usr/bin/env python3
"""Create a clean PGAA workflow schematic without using deprecated assets."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures_png" / "figure_pgaa_workflow.png"


def box(ax, xy, w, h, title, body, face, edge="#2f3a45"):
    rect = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.3,
        facecolor=face,
        edgecolor=edge,
    )
    ax.add_patch(rect)
    x, y = xy
    ax.text(x + w / 2, y + h - 0.065, title, ha="center", va="top",
            fontsize=8.8, fontweight="bold", color="#1c252e")
    ax.text(x + w / 2, y + h / 2 - 0.05, body, ha="center", va="center",
            fontsize=7.4, color="#26323d", linespacing=1.22)


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.35,
        color="#4a5561",
        shrinkA=4,
        shrinkB=4,
    ))


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.linewidth": 0,
        "savefig.dpi": 350,
    })

    fig, ax = plt.subplots(figsize=(9.2, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    colors = {
        "input": "#e8f1fb",
        "prep": "#f3f0e7",
        "s1": "#e9f6ef",
        "s2": "#f7edf2",
        "cal": "#eef0f8",
        "out": "#f4f5f6",
    }

    box(ax, (0.035, 0.34), 0.13, 0.32, "Input",
        "Perturb-seq matrix\nperturbation labels\ncontrol cells", colors["input"])
    box(ax, (0.205, 0.34), 0.15, 0.32, "Preprocessing",
        "QC, log-CPM\n2,000 HVGs\nfixed target inclusion", colors["prep"])
    box(ax, (0.395, 0.57), 0.15, 0.30, "PGAA-W Wasserstein",
        "99-quantile distance\nlocation, spread,\nshape shifts", colors["s1"])
    box(ax, (0.395, 0.13), 0.15, 0.30, "PGAA-H histogram-shape",
        "histogram peaks\ntop-3 prominence\nresponder pattern", colors["s2"])
    box(ax, (0.59, 0.34), 0.16, 0.32, "Calibration",
        "within-cluster\npermutation\nupper-tail diagnostic", colors["cal"])
    box(ax, (0.79, 0.34), 0.17, 0.32, "Outputs",
        "gene ranking\np-values when valid\nAUROC/AUPRC\nruntime diagnostics", colors["out"])

    arrow(ax, (0.165, 0.50), (0.205, 0.50))
    arrow(ax, (0.355, 0.56), (0.395, 0.70))
    arrow(ax, (0.355, 0.44), (0.395, 0.28))
    arrow(ax, (0.545, 0.70), (0.59, 0.55))
    arrow(ax, (0.545, 0.28), (0.59, 0.45))
    arrow(ax, (0.75, 0.50), (0.79, 0.50))

    ax.text(0.035, 0.91, "PGAA distribution-aware Perturb-seq ranking workflow",
            fontsize=12, fontweight="bold", ha="left", color="#15212c")
    ax.text(0.035, 0.085,
            "PGAA-H p-values from 500 permutations are used as ranking evidence unless permutation depth supports genome-wide error control.",
            fontsize=7.7, ha="left", color="#4a5561")

    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.05)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
