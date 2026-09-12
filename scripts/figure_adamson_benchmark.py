#!/usr/bin/env python3
"""Build the main Adamson 2016 UPR CRISPRi benchmark figure.

The AUROC bars in panels b-d are computed on the raw per-gene statistic. That
quantity tracks gene expression (rho = 0.91) and an expression-only ranking
scores higher than the Wasserstein statistic, so panel e carries the
expression-matched null, the calibrated statistic and the expression-stratified
stratified values that the AUROC claim has to be read against. Sources:
scripts/adamson_expression_confound.csv and scripts/adamson_calibrated_auroc.csv.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figure_source_data" / "fig6_adamson_results.csv"
CONFOUND = ROOT / "scripts" / "adamson_expression_confound.csv"
CALIBRATED = ROOT / "scripts" / "adamson_calibrated_auroc.csv"
OUT = ROOT / "figures_png" / "figure_adamson_benchmark.png"
CM_OUT = ROOT / "COMMUNICATIONS_MEDICINE_TRANSFER" / "figures_png" / "figure_adamson_benchmark.png"
CAIC_OUT = ROOT / "COMMUNICATIONS_AI_COMPUTING_TRANSFER" / "figures_png" / "figure_adamson_benchmark.png"


def add_box(ax, xy, width, height, text, facecolor="#F3F6FA"):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.02",
        linewidth=0.8,
        edgecolor="#9AA9B8",
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=9.5,
        linespacing=1.25,
    )


def main() -> None:
    df = pd.read_csv(SRC)
    confound = pd.read_csv(CONFOUND)
    calibrated = pd.read_csv(CALIBRATED)
    targets = [x.split("_")[0] for x in df["target"]]
    methods = [
        ("PGAA-W Wasserstein", "auroc_s1", "auprc_s1", "#2F6DB3"),
        ("PGAA-H histogram-shape", "auroc_s2", "auprc_s2", "#2F9E44"),
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

    fig = plt.figure(figsize=(14.4, 9.0), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[0.9, 1.2])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, :2])
    ax_e = fig.add_subplot(gs[1, 2])

    # Panel A: design summary as a compact workflow schematic.
    ax_a.axis("off")
    ax_a.set_xlim(0, 1)
    ax_a.set_ylim(0, 1)
    ax_a.set_title("a  Benchmark design", loc="left", fontweight="bold")
    add_box(ax_a, (0.05, 0.70), 0.88, 0.18, "Adamson 2016 UPR CRISPRi\nGSE90546", "#EEF4FB")
    add_box(ax_a, (0.05, 0.45), 0.39, 0.16, "QC-passed K562 cells\nn=5,680", "#F7F9FB")
    add_box(ax_a, (0.54, 0.45), 0.39, 0.16, "Non-targeting controls\nn=1,759", "#F7F9FB")
    add_box(ax_a, (0.05, 0.19), 0.39, 0.16, "5 pre-specified\nUPR perturbations", "#F7F9FB")
    add_box(ax_a, (0.54, 0.19), 0.39, 0.16, "2,000 HVGs\n13 UPR positives", "#F7F9FB")
    arrow_kw = {"arrowstyle": "->", "lw": 1.0, "color": "#5C6770", "shrinkA": 4, "shrinkB": 4}
    ax_a.annotate("", xy=(0.245, 0.61), xytext=(0.49, 0.70), arrowprops=arrow_kw)
    ax_a.annotate("", xy=(0.735, 0.61), xytext=(0.49, 0.70), arrowprops=arrow_kw)
    ax_a.annotate("", xy=(0.245, 0.35), xytext=(0.245, 0.45), arrowprops=arrow_kw)
    ax_a.annotate("", xy=(0.735, 0.35), xytext=(0.735, 0.45), arrowprops=arrow_kw)
    ax_a.text(0.49, 0.08, "Rank genes by each method, then score recovery of curated UPR positives",
              ha="center", va="center", fontsize=9, color="#333333")

    # Panel B: mean AUROC with per-perturbation dots.
    ax_b.set_title("b  Mean AUROC", loc="left", fontweight="bold")
    x = np.arange(len(methods))
    auroc_means = [df[col].mean() for _, col, _, _ in methods]
    auroc_sds = [df[col].std(ddof=1) for _, col, _, _ in methods]
    colors = [m[3] for m in methods]
    bars = ax_b.bar(x, auroc_means, yerr=auroc_sds, capsize=4, color=colors, edgecolor="black", linewidth=0.6)
    for i, (_, col, _, _) in enumerate(methods):
        jitter = np.linspace(-0.08, 0.08, len(df))
        ax_b.scatter(np.full(len(df), i) + jitter, df[col], s=22, color="white", edgecolor="black", linewidth=0.5, zorder=3)
    for bar, val in zip(bars, auroc_means):
        # Above the bar where the reference lines are clear of it, inside the
        # bar for the two tall ones.
        if val > 0.7:
            ax_b.text(bar.get_x() + bar.get_width() / 2, val - 0.035, f"{val:.3f}",
                      ha="center", va="top", fontsize=9, color="white", fontweight="bold")
        else:
            ax_b.text(bar.get_x() + bar.get_width() / 2, val + 0.015, f"{val:.3f}",
                      ha="center", va="bottom", fontsize=9, color="#222222")
    # The two controls panel e is built from, drawn on the same scale: the UPR
    # markers are a high-expression gene set, so a ranking that never sees the
    # perturbation already reaches these values.
    expr_only = float(confound["auroc_expression_only"].mean())
    matched = float(confound["matched_null_mean"].mean())
    line_expr = ax_b.axhline(expr_only, color="#7030A0", linestyle=":", linewidth=1.4)
    line_matched = ax_b.axhline(matched, color="#C55A11", linestyle="-.", linewidth=1.4)
    line_random = ax_b.axhline(0.5, color="#B22222", linestyle="--", linewidth=1)
    ax_b.legend(
        [line_random, line_expr, line_matched],
        ["random", f"expression only ({expr_only:.3f})",
         f"expression-matched null ({matched:.3f})"],
        loc="upper left", frameon=True, framealpha=0.92, edgecolor="#CCCCCC",
        fontsize=8.5, handlelength=1.8, borderpad=0.5,
    )
    ax_b.set_ylim(0.25, 0.98)
    ax_b.set_ylabel("AUROC (raw)")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(["PGAA-W", "PGAA-H", "Wilcoxon", "t-test", "MAST"], fontsize=9.5)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)

    # Panel C: AUPRC against random baseline.
    ax_c.set_title("c  AUPRC vs random baseline", loc="left", fontweight="bold")
    auprc_labels = ["PGAA-W W1", "PGAA-H shape", "Random"]
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
    ax_d.set_title("d  Per-perturbation AUROC, raw statistic (expression-confounded)",
                   loc="left", fontweight="bold")
    heat_cols = [m[1] for m in methods]
    heat = df[heat_cols].to_numpy().T
    im = ax_d.imshow(heat, aspect="auto", cmap="YlGnBu", vmin=0.35, vmax=0.85)
    ax_d.set_xticks(np.arange(len(targets)))
    ax_d.set_xticklabels(targets, rotation=35, ha="right")
    ax_d.set_yticks(np.arange(len(methods)))
    ax_d.set_yticklabels([m[0] for m in methods])
    cbar = fig.colorbar(im, ax=ax_d, fraction=0.046, pad=0.02)
    cbar.set_label("AUROC (raw)")

    # Panel E: what is left once expression is removed from the comparison.
    ax_e.set_title("e  AUROC after removing expression", loc="left", fontweight="bold")
    controls = [
        ("PGAA-W\ncalibrated $z$", calibrated["auroc_calibrated_z"].values, "#2F6DB3"),
        ("PGAA-W\nstratified", confound["auroc_stratified"].values, "#5B9BD5"),
        ("PGAA-H\nstratified", confound["auroc_s2_stratified"].values, "#2F9E44"),
    ]
    for i, (label, values, color) in enumerate(controls):
        ax_e.bar(i, values.mean(), color=color, edgecolor="black", linewidth=0.6, width=0.62)
        ax_e.scatter(np.full(len(values), i) + np.linspace(-0.13, 0.13, len(values)),
                     values, s=22, color="white", edgecolor="black", linewidth=0.5, zorder=3)
        ax_e.text(i, values.mean() + 0.022, f"{values.mean():.3f}",
                  ha="center", va="bottom", fontsize=9)
    ax_e.axhline(0.5, color="#B22222", linestyle="--", linewidth=1)
    ax_e.text(0.5, 0.507, "random", color="#B22222", ha="center", va="bottom", fontsize=8.5)
    bhlhe40 = float(confound.loc[confound["perturbation"].str.startswith("BHLHE40"),
                                 "auroc_s2_stratified"].iloc[0])
    ax_e.annotate(f"BHLHE40, {bhlhe40:.3f}", xy=(2, bhlhe40), xytext=(1.35, 0.70),
                  fontsize=8.5, color="#1B5E20",
                  arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "#1B5E20"})
    ax_e.set_ylim(0.3, 0.78)
    ax_e.set_ylabel("AUROC (expression removed)")
    ax_e.set_xticks(np.arange(len(controls)))
    ax_e.set_xticklabels([label for label, _, _ in controls], fontsize=9)
    ax_e.spines["top"].set_visible(False)
    ax_e.spines["right"].set_visible(False)

    fig.suptitle("Adamson 2016 UPR CRISPRi benchmark", fontsize=15, fontweight="bold")
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    fig.savefig(CM_OUT, dpi=300, bbox_inches="tight")
    fig.savefig(CAIC_OUT, dpi=300, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
