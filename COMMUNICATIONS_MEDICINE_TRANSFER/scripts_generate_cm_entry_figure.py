#!/usr/bin/env python3
"""Create a Communications Medicine entry schematic for PGAA."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path("figures_png/figure_cm_entry.png")


def box(ax, xy, wh, title, body, fc, ec="#263238", title_size=10.5, body_size=8.2):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        facecolor=fc,
        edgecolor=ec,
        linewidth=1.5,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h * 0.72,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        weight="bold",
        color="#17212b",
    )
    ax.text(
        x + w / 2,
        y + h * 0.38,
        body,
        ha="center",
        va="center",
        fontsize=body_size,
        color="#263238",
        linespacing=1.18,
    )


def arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.8,
            color="#3b4a54",
        )
    )


def main():
    fig, ax = plt.subplots(figsize=(13.2, 5.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.96,
        "PGAA prioritizes heterogeneous disease-relevant single-cell responses",
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        color="#16212a",
    )
    ax.text(
        0.5,
        0.91,
        "Intended use: transparent translational hypothesis prioritization, not clinical diagnosis or treatment recommendation",
        ha="center",
        va="center",
        fontsize=10.8,
        color="#4a5963",
    )

    box(
        ax,
        (0.03, 0.55),
        (0.18, 0.25),
        "(A) Clinical problem",
        "patient-derived disease tissue\ncontains mixed responder and\nnon-responder cell states",
        "#e8f1fb",
    )
    box(
        ax,
        (0.25, 0.55),
        (0.18, 0.25),
        "(B) Standard limitation",
        "mean-focused tests can\nunder-rank subset-confined\ntranscriptional responses",
        "#fff2df",
    )
    box(
        ax,
        (0.47, 0.55),
        (0.22, 0.25),
        "(C) PGAA solution",
        "S1 Wasserstein: distribution shift\nS2 persistence: responder shape\ncalibration: permutation + pi0-hat",
        "#e9f6ed",
    )
    box(
        ax,
        (0.73, 0.55),
        (0.23, 0.25),
        "(D) Translational output",
        "ranked disease-relevant programs\nfor patient-derived models,\norganoids, or perturbation screens",
        "#f1edf7",
    )

    arrow(ax, (0.215, 0.675), (0.245, 0.675))
    arrow(ax, (0.435, 0.675), (0.465, 0.675))
    arrow(ax, (0.695, 0.675), (0.725, 0.675))

    box(
        ax,
        (0.05, 0.17),
        (0.27, 0.22),
        "(E) Disease-state anchoring",
        "CLL, sepsis, RA, IBD, PBMC\nknown-marker recovery\nobservational, not causal",
        "#f7fbff",
        title_size=10.2,
        body_size=8.0,
    )
    box(
        ax,
        (0.365, 0.17),
        (0.27, 0.22),
        "(F) Perturb-seq benchmarks",
        "Adamson UPR CRISPRi: S1 AUROC 0.786\nNorman CEBPE CRISPRa: S2 ranks ELANE\nranking evidence, not FDR discovery",
        "#f7fff8",
        title_size=10.2,
        body_size=8.0,
    )
    box(
        ax,
        (0.68, 0.17),
        (0.27, 0.22),
        "(G) Guardrails",
        "negative controls, n_bins sweep,\npi0-hat diagnostics, and\nsource-code reproducibility",
        "#fffdf2",
        title_size=10.2,
        body_size=8.0,
    )

    ax.text(
        0.5,
        0.07,
        "PGAA is a prioritization layer for heterogeneous responses that require downstream experimental or clinical validation.",
        ha="center",
        va="center",
        fontsize=10.8,
        color="#33434c",
        bbox=dict(boxstyle="round,pad=0.35", fc="#ffffff", ec="#b8c2cc", lw=1.0),
    )

    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
