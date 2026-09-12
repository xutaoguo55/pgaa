#!/usr/bin/env python3
"""Render the cross-platform stability-specificity gate plane."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--states",
        type=Path,
        default=ROOT / "evidence/cross_platform_dual_gate_states.tsv",
    )
    parser.add_argument(
        "--png-out",
        type=Path,
        default=ROOT / "figures_png/cross_platform_dual_gate.png",
    )
    parser.add_argument(
        "--pdf-out",
        type=Path,
        default=ROOT / "figures_png/cross_platform_dual_gate.pdf",
    )
    args = parser.parse_args()

    states = pd.read_csv(args.states, sep="\t")
    dataset_labels = {
        "replogle2022_k562_crispri": "Replogle CRISPRi",
        "norman2019_k562_crispra": "Norman CRISPRa",
        "datlinger2017_jurkat_crispr": "Datlinger CRISPR",
        "sciplex3_a549_drug": "SciPlex3 drug",
        "nadig2024_hepg2_crispri": "Nadig HepG2 CRISPRi",
    }
    method_labels = {
        "pgaa_w": "PGAA-W",
        "pgaa_h": "PGAA-H",
        "absolute_mean_shift": "Mean shift",
        "welch_abs_t": "Welch |t|",
    }
    colors = {
        "replogle2022_k562_crispri": "#0072B2",
        "norman2019_k562_crispra": "#009E73",
        "datlinger2017_jurkat_crispr": "#CC79A7",
        "sciplex3_a549_drug": "#D55E00",
        "nadig2024_hepg2_crispri": "#7A5AA6",
    }
    markers = {
        "pgaa_w": "o",
        "pgaa_h": "s",
        "absolute_mean_shift": "^",
        "welch_abs_t": "D",
    }

    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    ax.axhline(0.20, color="#444444", linestyle="--", linewidth=1)
    ax.axvline(0.0, color="#999999", linestyle=":", linewidth=0.9)
    for row in states.itertuples():
        ax.scatter(
            row.median_specificity_margin,
            row.median_observed_overlap,
            s=74,
            facecolor=colors[row.dataset_id] if row.specificity_gate_pass else "white",
            marker=markers[row.method],
            edgecolor=colors[row.dataset_id],
            linewidth=1.8,
            zorder=3,
        )
    dataset_handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=7,
                   markerfacecolor=color, markeredgecolor="white", label=dataset_labels[key])
        for key, color in colors.items()
    ]
    method_handles = [
        plt.Line2D([0], [0], marker=marker, linestyle="", markersize=7,
                   markerfacecolor="#666666", markeredgecolor="white", label=method_labels[key])
        for key, marker in markers.items()
    ]
    first = ax.legend(handles=dataset_handles, title="Dataset / platform", loc="upper right", frameon=False)
    ax.add_artist(first)
    second = ax.legend(handles=method_handles, title="Method", loc="center right", frameon=False)
    ax.add_artist(second)
    specificity_handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=7,
                   markerfacecolor="#666666", markeredgecolor="#666666", label="Specificity pass"),
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=7,
                   markerfacecolor="white", markeredgecolor="#666666", label="Specificity fail"),
    ]
    ax.legend(handles=specificity_handles, title="Point fill", loc="lower right", frameon=False)
    ax.set_xlabel("Median specificity margin (observed minus pseudo overlap)")
    ax.set_ylabel("Median discovery-validation top-100 overlap")
    ax.set_title("Stability and specificity separate across perturbation platforms")
    ax.set_xlim(min(-0.02, states["median_specificity_margin"].min() - 0.02), 0.31)
    ax.set_ylim(0, 0.88)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D8D8D8", linewidth=0.6, alpha=0.7)
    fig.tight_layout()
    for path in (args.png_out, args.pdf_out):
        path.parent.mkdir(parents=True, exist_ok=True)
        save_figure(fig, path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {args.png_out} and {args.pdf_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
