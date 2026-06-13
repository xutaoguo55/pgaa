#!/usr/bin/env python3
"""Create a Communications Medicine entry schematic for PGAA."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path("figures_png/figure_cm_entry.png")


def box(ax, xy, wh, title, body, fc, ec="#263238"):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.025,rounding_size=0.035",
        facecolor=fc,
        edgecolor=ec,
        linewidth=2.0,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center",
            fontsize=14, weight="bold", color="#1d2730")
    ax.text(x + w / 2, y + h * 0.36, body, ha="center", va="center",
            fontsize=10.5, color="#263238", linespacing=1.2)


def arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=22,
            linewidth=2.2,
            color="#3b4a54",
        )
    )


def main():
    fig, ax = plt.subplots(figsize=(12, 5.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.94,
        "PGAA for clinically interpretable single-cell perturbation mapping",
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        color="#16212a",
    )
    ax.text(
        0.5,
        0.885,
        "Distribution-aware ranking of heterogeneous disease-relevant transcriptional responses",
        ha="center",
        va="center",
        fontsize=12,
        color="#4a5963",
    )

    box(
        ax,
        (0.04, 0.47),
        (0.22, 0.27),
        "Clinical problem",
        "patient-derived scRNA-seq\nor disease model\nperturbation screens",
        "#e8f1fb",
    )
    box(
        ax,
        (0.39, 0.62),
        (0.22, 0.20),
        "S1 Wasserstein",
        "full expression-distribution\nlocation, spread, and shape shifts",
        "#e7f5ec",
    )
    box(
        ax,
        (0.39, 0.35),
        (0.22, 0.20),
        "S2 persistence",
        "responder-associated\nhistogram-shape changes",
        "#f7eaf1",
    )
    box(
        ax,
        (0.73, 0.47),
        (0.22, 0.27),
        "Translational output",
        "calibrated gene rankings\nmarker-program recovery\nfollow-up hypotheses",
        "#f2f2f2",
    )

    arrow(ax, (0.27, 0.60), (0.38, 0.72))
    arrow(ax, (0.27, 0.60), (0.38, 0.45))
    arrow(ax, (0.62, 0.72), (0.72, 0.61))
    arrow(ax, (0.62, 0.45), (0.72, 0.58))

    ax.text(
        0.5,
        0.22,
        "Calibration layer: within-cluster permutation, Storey pi0-hat diagnostics, pilot sensitivity sweeps",
        ha="center",
        va="center",
        fontsize=11.5,
        color="#263238",
        bbox=dict(boxstyle="round,pad=0.45", fc="#fff8e1", ec="#d6a900", lw=1.5),
    )
    ax.text(
        0.5,
        0.11,
        "Intended use: translational hypothesis prioritization, not bedside diagnosis or direct treatment recommendation",
        ha="center",
        va="center",
        fontsize=10.5,
        color="#59656f",
    )

    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
