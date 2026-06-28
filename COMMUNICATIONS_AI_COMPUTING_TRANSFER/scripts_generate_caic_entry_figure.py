#!/usr/bin/env python3
"""Generate Figure 1 for the CAIC manuscript."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parent
SOURCE_PNG = ROOT / "figures_source" / "Figure_1_PGAA_framework_final.png"
SOURCE_TIFF = ROOT / "figures_source" / "Figure_1_PGAA_framework_final.tiff"
OUT = ROOT / "figures_png" / "figure_caic_entry.png"


def rounded_box(ax, xy, width, height, text, fc="#FFFFFF", ec="#C6CDD4", lw=1.4, fs=10.5):
    box = FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.025,rounding_size=0.025",
        linewidth=lw, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text,
            ha="center", va="center", fontsize=fs, fontweight="bold",
            linespacing=1.15)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops={"arrowstyle": "-|>", "lw": 1.6, "color": "#222222", "mutation_scale": 14},
    )


def normal_curve(x, mu, sd):
    return np.exp(-0.5 * ((x - mu) / sd) ** 2)


def panel_a(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.015, 0.94, "A", fontsize=21, fontweight="bold", va="top")
    ax.text(0.075, 0.93, "Response regimes", fontsize=18, fontweight="bold", va="top")

    # Left regime: uniform shift.
    x = np.linspace(0.08, 0.43, 220)
    y0 = normal_curve(x, 0.22, 0.045)
    y1 = normal_curve(x, 0.31, 0.045)
    y0 = 0.20 + 0.20 * y0 / y0.max()
    y1 = 0.20 + 0.20 * y1 / y1.max()
    ax.plot(x, y0, color="#777777", lw=2)
    ax.plot(x, y1, color="#2459A6", lw=2)
    ax.fill_between(x, 0.20, y0, color="#777777", alpha=0.12)
    ax.fill_between(x, 0.20, y1, color="#2459A6", alpha=0.12)
    arrow(ax, 0.08, 0.20, 0.43, 0.20)
    arrow(ax, 0.08, 0.20, 0.08, 0.47)
    ax.text(0.25, 0.53, "Uniform shift", color="#2459A6", fontsize=16, fontweight="bold", ha="center")
    ax.text(0.25, 0.08, "Mean-based tests usually work", color="#2459A6", fontsize=13, fontweight="bold", ha="center")
    ax.text(0.15, 0.42, "Control", color="#777777", fontsize=11)
    ax.text(0.32, 0.42, "Perturbed", color="#2459A6", fontsize=11)
    ax.text(0.04, 0.32, "Density", rotation=90, fontsize=11, va="center")
    ax.text(0.25, 0.12, "Expression", fontsize=11, ha="center")

    # Right regime: responder subset / shape change.
    x = np.linspace(0.58, 0.93, 260)
    ctrl = normal_curve(x, 0.70, 0.045)
    resp = 0.80 * normal_curve(x, 0.72, 0.045) + 0.45 * normal_curve(x, 0.83, 0.030)
    ctrl = 0.20 + 0.20 * ctrl / ctrl.max()
    resp = 0.20 + 0.22 * resp / resp.max()
    ax.plot(x, ctrl, color="#777777", lw=2)
    ax.plot(x, resp, color="#D95F02", lw=2)
    ax.fill_between(x, 0.20, resp, color="#D95F02", alpha=0.14)
    arrow(ax, 0.58, 0.20, 0.93, 0.20)
    arrow(ax, 0.58, 0.20, 0.58, 0.47)
    ax.text(0.755, 0.53, "Responder-associated shape change", color="#D95F02",
            fontsize=15, fontweight="bold", ha="center")
    ax.text(0.755, 0.08, "Average shift can be weak", color="#D95F02", fontsize=13, fontweight="bold", ha="center")
    ax.text(0.64, 0.42, "Control", color="#777777", fontsize=11)
    ax.text(0.81, 0.42, "Perturbed", color="#D95F02", fontsize=11)
    ax.text(0.54, 0.32, "Density", rotation=90, fontsize=11, va="center")
    ax.text(0.755, 0.12, "Expression", fontsize=11, ha="center")


def panel_b(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.015, 0.94, "B", fontsize=21, fontweight="bold", va="top")
    ax.text(0.075, 0.91, "Distribution-aware PGAA workflow", fontsize=18, fontweight="bold", va="top")

    rounded_box(ax, (0.04, 0.30), 0.16, 0.43, "Single-cell\nperturbation\ndata", fs=10.2)
    rounded_box(ax, (0.24, 0.30), 0.17, 0.43, "Residualization\n\ncell-state and\nlibrary-size effects", fs=10.2)
    rounded_box(ax, (0.45, 0.30), 0.27, 0.43, "", ec="#91A9C8", fs=11.5)
    rounded_box(ax, (0.75, 0.30), 0.14, 0.43, "Permutation\ncalibration\n\nupper-tail\ndiagnostic", ec="#2E7D45", fs=10.0)
    rounded_box(ax, (0.91, 0.30), 0.075, 0.43, "Ranked\ngenes\n\n1\n2\n3\n...", fs=9.6)

    arrow(ax, 0.205, 0.515, 0.235, 0.515)
    arrow(ax, 0.415, 0.515, 0.445, 0.515)
    arrow(ax, 0.72, 0.515, 0.745, 0.515)
    arrow(ax, 0.89, 0.515, 0.905, 0.515)

    ax.text(0.585, 0.665, "PGAA statistics", color="#111111", fontsize=12.5,
            fontweight="bold", ha="center")
    ax.text(0.485, 0.580, "PGAA-W", color="#2459A6", fontsize=13.0, fontweight="bold", ha="left")
    ax.text(0.485, 0.515, "Wasserstein distribution shift", color="#222222", fontsize=9.0, ha="left", va="top")
    ax.text(0.485, 0.405, "PGAA-H", color="#D95F02", fontsize=13.0, fontweight="bold", ha="left")
    ax.text(0.485, 0.340, "histogram-shape diagnostic", color="#222222", fontsize=9.0, ha="left", va="top")

    # Small icons inside the boxes.
    for i in range(5):
        for j in range(4):
            c = "#AFC1D9" if (i + j) % 3 == 0 else "#F7F7F7"
            ax.add_patch(Rectangle((0.096 + 0.012 * i, 0.405 + 0.020 * j), 0.010, 0.016,
                                   facecolor=c, edgecolor="#999999", linewidth=0.3))
    xx = np.linspace(0.64, 0.70, 50)
    ax.plot(xx, 0.55 + 0.035 * normal_curve(xx, 0.675, 0.025), color="#2459A6", lw=2)
    bins = np.linspace(0.64, 0.70, 9)
    heights = [0.01, 0.02, 0.04, 0.025, 0.01, 0.018, 0.045, 0.03]
    ax.bar(bins[:-1], heights, width=0.006, bottom=0.345, color="#D95F02", alpha=0.75)
    ax.plot([0.79, 0.82, 0.865], [0.385, 0.475, 0.385], color="#2E7D45", lw=2)


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 600})
    fig = plt.figure(figsize=(12.2, 6.0), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])
    panel_a(fig.add_subplot(gs[0, 0]))
    panel_b(fig.add_subplot(gs[1, 0]))

    for path in [SOURCE_PNG, OUT]:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=600, bbox_inches="tight")
    fig.savefig(SOURCE_TIFF, dpi=600, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
