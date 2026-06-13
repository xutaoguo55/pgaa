#!/usr/bin/env python3
"""Build the main Adamson 2016 UPR CRISPRi benchmark figure."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figure_source_data" / "fig6_adamson_results.csv"
OUT = ROOT / "figures_png" / "figure_adamson_benchmark.png"


def main() -> None:
    df = pd.read_csv(SRC)
    targets = [x.split("_")[0] for x in df["target"]]
    methods = [
        ("S1 Wasserstein", "auroc_s1", "auprc_s1", "#2F6DB3"),
        ("S2 persistence", "auroc_s2", "auprc_s2", "#2F9E44"),
        ("Wilcoxon", "auroc_wilcox", "auprc_wilcox", "#8C8C8C"),
        ("t-test", "auroc_ttest", "auprc_ttest", "#B0B0B0"),
        ("MAST", "auroc_mast", "auprc_mast", "#D0D0D0"),
    ]

    plt.rcParams.update({
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300,
    })

    fig = plt.figure(figsize=(10.6, 9.0), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.9, 1.2])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # Panel A: design summary
    ax_a.axis("off")
    ax_a.set_title("(A) Benchmark design", loc="left", fontweight="bold")
    design_lines = [
        "Adamson 2016 UPR CRISPRi (GSE90546)",
        "5,680 QC-passed K562 cells",
        "5 pre-specified UPR perturbations",
        "468-686 perturbed cells per sgRNA",
        "1,759 non-targeting controls",
        "13 UPR positives in the 2,000-HVG universe",
    ]
    ax_a.text(
        0.02, 0.87, "\n".join(design_lines),
        va="top", ha="left", linespacing=1.45,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#F3F6FA", "edgecolor": "#B8C2CC"},
    )

    # Panel B: mean AUROC with per-perturbation dots.
    ax_b.set_title("(B) Mean AUROC", loc="left", fontweight="bold")
    x = np.arange(len(methods))
    auroc_means = [df[col].mean() for _, col, _, _ in methods]
    auroc_sds = [df[col].std(ddof=1) for _, col, _, _ in methods]
    colors = [m[3] for m in methods]
    bars = ax_b.bar(x, auroc_means, yerr=auroc_sds, capsize=4, color=colors, edgecolor="black", linewidth=0.6)
    for i, (_, col, _, _) in enumerate(methods):
        jitter = np.linspace(-0.08, 0.08, len(df))
        ax_b.scatter(np.full(len(df), i) + jitter, df[col], s=22, color="white", edgecolor="black", linewidth=0.5, zorder=3)
    for bar, val in zip(bars, auroc_means):
        ax_b.text(bar.get_x() + bar.get_width() / 2, val + 0.03, f"{val:.3f}", ha="center", va="bottom", fontsize=9)
    ax_b.axhline(0.5, color="#B22222", linestyle="--", linewidth=1)
    ax_b.text(len(methods) - 0.55, 0.515, "random", color="#B22222", ha="right", va="bottom", fontsize=9)
    ax_b.set_ylim(0.25, 0.9)
    ax_b.set_ylabel("AUROC")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(["S1 W1", "S2 PH", "Wilcoxon", "t-test", "MAST"])
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)

    # Panel C: AUPRC against random baseline.
    ax_c.set_title("(C) AUPRC vs random baseline", loc="left", fontweight="bold")
    auprc_labels = ["S1 W1", "S2 PH", "Random"]
    auprc_vals = [df["auprc_s1"].mean(), df["auprc_s2"].mean(), 13 / 2000]
    auprc_colors = ["#2F6DB3", "#2F9E44", "#D9D9D9"]
    bars = ax_c.bar(np.arange(3), auprc_vals, color=auprc_colors, edgecolor="black", linewidth=0.6)
    for bar, val in zip(bars, auprc_vals):
        ax_c.text(bar.get_x() + bar.get_width() / 2, val + 0.0015, f"{val:.4f}", ha="center", va="bottom", fontsize=10)
    ax_c.text(0, auprc_vals[0] + 0.0047, "2.9x random", ha="center", fontsize=9)
    ax_c.text(1, auprc_vals[1] + 0.0047, "3.9x random", ha="center", fontsize=9)
    ax_c.set_ylim(0, 0.036)
    ax_c.set_ylabel("AUPRC")
    ax_c.set_xticks(np.arange(3))
    ax_c.set_xticklabels(auprc_labels)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)

    # Panel D: per-perturbation AUROC heatmap.
    ax_d.set_title("(D) Per-perturbation AUROC", loc="left", fontweight="bold")
    heat_cols = [m[1] for m in methods]
    heat = df[heat_cols].to_numpy().T
    im = ax_d.imshow(heat, aspect="auto", cmap="YlGnBu", vmin=0.35, vmax=0.85)
    ax_d.set_xticks(np.arange(len(targets)))
    ax_d.set_xticklabels(targets, rotation=35, ha="right")
    ax_d.set_yticks(np.arange(len(methods)))
    ax_d.set_yticklabels([m[0] for m in methods])
    cbar = fig.colorbar(im, ax=ax_d, fraction=0.046, pad=0.02)
    cbar.set_label("AUROC")
    ax_d.text(
        0.99,
        -0.30,
        "Exact values in Supplementary Table S5",
        transform=ax_d.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        color="#333333",
    )

    fig.suptitle("Adamson 2016 UPR CRISPRi benchmark", fontsize=15, fontweight="bold")
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
