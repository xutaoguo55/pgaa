#!/usr/bin/env python3
"""Generate a Norman 2019 CEBPE figure for the CAIC main text."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CAIC_ROOT = Path(__file__).resolve().parent
ROOT = CAIC_ROOT.parent
OUT = CAIC_ROOT / "figures_png" / "figure_norman_main_caic.png"


def main() -> None:
    s2 = pd.read_csv(ROOT / "scripts" / "norman2019_prt_s2_nbins20.csv")
    s1 = pd.read_csv(ROOT / "scripts" / "norman2019_prt_s1_full.csv")
    # Source-data columns retain legacy S1/S2 names for compatibility; the
    # manuscript labels them PGAA-W and PGAA-H.
    s2_score_col = "S2"

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"]
    is_known = s2["gene"].isin(cebpe_targets)
    p_s2 = s2["p_value_perm"].fillna(1.0).astype(float)
    y_s2 = -np.log10(p_s2 + 1e-300)

    p_s1 = s1["p_value_perm"].fillna(1.0).astype(float)
    s1_rank = int(p_s1.rank(method="min").loc[s1.index[s1["gene"] == "ELANE"][0]])
    s1_p = float(p_s1.loc[s1.index[s1["gene"] == "ELANE"][0]])

    # Read ELANE S2 rank/p from source-data CSV to keep figure reproducible
    cebpe_csv = ROOT / "figure_source_data" / "cebpe_target_ranks.csv"
    cebpe_df = pd.read_csv(cebpe_csv)
    elane_row = cebpe_df[cebpe_df["target"] == "ELANE"].iloc[0]
    s2_rank = int(elane_row["s2_rank"])
    s2_p = float(elane_row["s2_p"])
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8,
        "figure.dpi": 600,
    })

    fig, axes = plt.subplots(
        1, 2, figsize=(10.8, 4.4),
        gridspec_kw={"width_ratios": [1.25, 1.0]},
        constrained_layout=True,
    )

    ax = axes[0]
    ax.scatter(s2.loc[~is_known, s2_score_col], y_s2[~is_known], s=7, color="#9E9E9E", alpha=0.35, linewidth=0)
    ax.scatter(
        s2.loc[is_known, s2_score_col], y_s2[is_known],
        s=42, color="#D81B60", edgecolor="black", linewidth=0.4, zorder=3,
        label="CEBPE targets",
    )
    for gene in ["ELANE", "PRTN3"]:
        row = s2[s2["gene"] == gene].iloc[0]
        ax.annotate(
            gene,
            (row[s2_score_col], -np.log10(float(row["p_value_perm"]) + 1e-300)),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )
    ax.axhline(-np.log10(0.05), color="#B22222", linestyle="--", linewidth=0.9)
    ax.text(0.995, 0.86, "p=0.05", transform=ax.transAxes, ha="right", va="top", color="#B22222", fontsize=8.5)
    ax.set_xlabel("PGAA-H histogram-shape diagnostic")
    ax.set_ylabel("-log10(permutation p)")
    ax.set_title("a  PGAA-H histogram-shape ranking in CEBPE CRISPRa", loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax = axes[1]
    methods = ["SCEPTRE", "PGAA-W\nWasserstein", "PGAA-H\nhistogram-shape"]
    ranks = [1761, s1_rank, s2_rank]
    pvals = [0.92, s1_p, s2_p]
    colors = ["#9E9E9E", "#F39C12", "#2F6DB3"]
    bars = ax.bar(np.arange(3), ranks, color=colors, edgecolor="black", linewidth=0.6)
    ax.set_ylim(0, 2050)
    ax.set_ylabel("ELANE rank (lower is better)")
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(methods)
    ax.axhline(2012, color="#333333", linestyle=":", linewidth=0.8)
    ax.text(2.55, 1990, "2,012 genes", ha="right", va="top", fontsize=8.5)
    for bar, rank, pval in zip(bars, ranks, pvals):
        y = min(rank + 65, 1880)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            f"rank {rank}\np={pval:.2f}",
            ha="center",
            va="bottom",
            fontsize=8.7,
            fontweight="bold",
        )
    ax.set_title("b  ELANE rank comparison", loc="left", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(OUT, dpi=600, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
