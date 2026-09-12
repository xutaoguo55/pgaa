#!/usr/bin/env python3
"""Render platform-level uncertainty and leave-one-out influence."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--uncertainty",
        type=Path,
        default=ROOT / "evidence/cross_platform_dual_gate_platform_uncertainty.tsv",
    )
    parser.add_argument(
        "--leave-one-out",
        type=Path,
        default=ROOT / "evidence/cross_platform_dual_gate_leave_one_out.tsv",
    )
    parser.add_argument(
        "--png-out",
        type=Path,
        default=ROOT / "figures_png/cross_platform_dual_gate_robustness.png",
    )
    parser.add_argument(
        "--pdf-out",
        type=Path,
        default=ROOT / "figures_png/cross_platform_dual_gate_robustness.pdf",
    )
    args = parser.parse_args()

    uncertainty = pd.read_csv(args.uncertainty, sep="\t")
    stable_only = uncertainty[
        uncertainty["platform_event"].eq("stable_but_not_specific")
    ].copy()
    order = ["pgaa_w", "pgaa_h", "absolute_mean_shift", "welch_abs_t"]
    labels = ["PGAA-W", "PGAA-H", "Mean shift", "Welch |t|"]
    stable_only["method"] = pd.Categorical(stable_only["method"], order, ordered=True)
    stable_only = stable_only.sort_values("method")

    loo = pd.read_csv(args.leave_one_out, sep="\t")
    loo = loo[loo["method"].eq("pgaa_w")].sort_values("omitted_dataset_id")
    short_names = {
        "replogle2022_k562_crispri": "Replogle",
        "norman2019_k562_crispra": "Norman",
        "datlinger2017_jurkat_crispr": "Datlinger",
        "sciplex3_a549_drug": "SciPlex3",
        "nadig2024_hepg2_crispri": "Nadig",
    }

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), gridspec_kw={"width_ratios": [1.05, 1]})
    y = np.arange(len(stable_only))
    estimate = stable_only["proportion"].to_numpy(float)
    low = stable_only["exact_ci_low"].to_numpy(float)
    high = stable_only["exact_ci_high"].to_numpy(float)
    axes[0].errorbar(
        estimate,
        y,
        xerr=np.vstack([estimate - low, high - estimate]),
        fmt="o",
        color="#0072B2",
        ecolor="#555555",
        capsize=3,
        markersize=6,
    )
    axes[0].set_yticks(y, labels)
    axes[0].set_xlim(-0.03, 1.03)
    axes[0].set_xlabel("Platform proportion (exact 95% CI)")
    axes[0].set_title("A  Stable but not specific")
    axes[0].grid(axis="x", color="#DDDDDD", linewidth=0.6)

    x = np.arange(len(loo))
    counts = loo["n_stable_but_not_specific"].to_numpy(int)
    colors = np.where(loo["recurrence_survives_omission"], "#009E73", "#D55E00")
    axes[1].bar(x, counts, color=colors, width=0.68)
    axes[1].axhline(2, color="#333333", linestyle="--", linewidth=1)
    axes[1].set_xticks(
        x,
        [short_names.get(value, value) for value in loo["omitted_dataset_id"]],
        rotation=30,
        ha="right",
    )
    axes[1].set_ylabel("Remaining PGAA-W stable-only platforms")
    axes[1].set_title("B  Leave one platform out")
    axes[1].set_ylim(0, max(3, counts.max() + 0.6))
    axes[1].grid(axis="y", color="#DDDDDD", linewidth=0.6)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    for path in (args.png_out, args.pdf_out):
        path.parent.mkdir(parents=True, exist_ok=True)
        save_figure(fig, path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {args.png_out} and {args.pdf_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
