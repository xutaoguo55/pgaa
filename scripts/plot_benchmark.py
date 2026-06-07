#!/usr/bin/env python3
"""Publication-quality benchmark figure."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "figure.dpi": 300,
})


def plot_benchmark_summary(csv_path="scripts/benchmark_results.csv",
                           out_path="scripts/benchmark_summary.tif"):
    df = pd.read_csv(csv_path)
    summary = df.groupby("method").mean(numeric_only=True).reset_index()

    methods = ["Spearman", "Partial_Pearson", "PGAA_linear"]
    colors = {"Spearman": "#E69F00",
              "Partial_Pearson": "#56B4E9",
              "PGAA_linear": "#009E73"}
    labels = {"Spearman": "Naïve Spearman",
              "Partial_Pearson": "Partial Pearson",
              "PGAA_linear": "PGAA (linear)"}

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))

    # Panel A: AUROC / AUPRC
    ax = axes[0]
    x = np.arange(len(methods))
    width = 0.35
    aurocs = [summary.loc[summary["method"] == m, "auroc"].values[0] for m in methods]
    auprcs = [summary.loc[summary["method"] == m, "auprc"].values[0] for m in methods]
    bars1 = ax.bar(x - width/2, aurocs, width, label="AUROC", color="#0072B2", edgecolor="black", linewidth=0.5)
    bars2 = ax.bar(x + width/2, auprcs, width, label="AUPRC", color="#D55E00", edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels([labels[m] for m in methods], rotation=15, ha="right")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False)
    ax.set_title("(A) Edge Recovery")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel B: Type I error
    ax = axes[1]
    type_i = [summary.loc[summary["method"] == m, "type_i"].values[0] for m in methods]
    bar_colors = [colors[m] for m in methods]
    bars = ax.bar(x, type_i, color=bar_colors, edgecolor="black", linewidth=0.5)
    ax.axhline(0.05, color="red", linestyle="--", linewidth=1, label="Nominal α=0.05")
    ax.set_ylabel("Empirical Type I error")
    ax.set_xticks(x)
    ax.set_xticklabels([labels[m] for m in methods], rotation=15, ha="right")
    ax.set_ylim(0, max(type_i) * 1.2)
    ax.legend(frameon=False)
    ax.set_title("(B) False Positive Control")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Panel C: Calibration (example from one target)
    ax = axes[2]
    for m in methods:
        sub = df[df["method"] == m]
        # Aggregate p-values from all targets: we don't have raw p-vals in CSV,
        # so use KS statistic as proxy (smaller = better calibration)
        ks_vals = sub["ks_stat"].values
        ax.scatter([labels[m]] * len(ks_vals), ks_vals, color=colors[m], s=60, zorder=3, edgecolor="black", linewidth=0.5)
    ax.axhline(0.05, color="red", linestyle="--", linewidth=1)
    ax.set_ylabel("KS statistic vs Uniform(0,1)")
    ax.set_xticklabels([labels[m] for m in methods], rotation=15, ha="right")
    ax.set_ylim(0, 0.5)
    ax.set_title("(C) P-value Calibration")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(out_path, format="tiff", dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    plot_benchmark_summary()
