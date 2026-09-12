#!/usr/bin/env python3
"""Render the ATM/HDAC branch-vulnerability map."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure
import pandas as pd


COLORS = {
    "ATM": "#0072B2",
    "HDAC": "#D55E00",
    "missing": "#D9D9D9",
}


def render_map(candidate_map: pd.DataFrame, png_out: Path, pdf_out: Path | None) -> None:
    required = {
        "target_class",
        "lead_drug",
        "gse193258_spearman_rho",
        "gse193258_exact_p",
        "gse335846_dynamic_rho",
        "evidence_state",
    }
    missing = required.difference(candidate_map.columns)
    if missing:
        raise ValueError(f"candidate map missing columns: {sorted(missing)}")

    candidate_map = candidate_map.sort_values("target_class").reset_index(drop=True)
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.8, 3.4),
        gridspec_kw={"width_ratios": [1.0, 1.15], "wspace": 0.35},
    )
    ax = axes[0]
    x_positions = range(len(candidate_map))
    colors = [COLORS.get(target, "#666666") for target in candidate_map["target_class"]]
    ax.bar(
        x_positions,
        candidate_map["gse193258_spearman_rho"],
        color=colors,
        edgecolor="#222222",
        linewidth=0.7,
    )
    for idx, row in candidate_map.iterrows():
        ax.text(
            idx,
            float(row["gse193258_spearman_rho"]) + 0.04,
            f"p={float(row['gse193258_exact_p']):.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_title("A. Branch-linked drug response", loc="left", fontweight="bold", fontsize=10)
    ax.set_xticks(
        list(x_positions),
        [f"{row.target_class}\n{row.lead_drug}" for row in candidate_map.itertuples()],
    )
    ax.set_ylabel("GSE193258 Spearman rho", fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax = axes[1]
    evidence_layers = [
        ("GSE193258", "gse193258_spearman_rho"),
        ("GSE335846", "gse335846_dynamic_rho"),
        ("prospective", "prospective"),
    ]
    y_positions = range(len(candidate_map))
    for layer_idx, (label, column) in enumerate(evidence_layers):
        values = []
        for _, row in candidate_map.iterrows():
            if column == "prospective":
                values.append(0.5)
            else:
                value = row[column]
                values.append(0.0 if pd.isna(value) else float(value))
        ax.scatter(
            [layer_idx] * len(values),
            list(y_positions),
            s=[260 if value >= 0.95 else 140 if value > 0 else 90 for value in values],
            c=[
                COLORS.get(row.target_class, "#666666") if value > 0 else COLORS["missing"]
                for value, row in zip(values, candidate_map.itertuples())
            ],
            edgecolor="#222222",
            linewidth=0.7,
        )
    ax.set_title("B. Evidence layers", loc="left", fontweight="bold", fontsize=10)
    ax.set_xticks(range(len(evidence_layers)), [label for label, _ in evidence_layers])
    ax.set_yticks(
        list(y_positions),
        [row.target_class for row in candidate_map.itertuples()],
    )
    ax.set_xlim(-0.5, len(evidence_layers) - 0.5)
    ax.set_ylim(-0.6, len(candidate_map) - 0.4)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Evidence layer", fontsize=9)
    fig.suptitle(
        "ATM leads the dynamic branch-vulnerability map; HDAC remains secondary",
        fontsize=10,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.62,
        0.86,
        "Circle size tracks association strength; gray marks missing dynamic support.",
        fontsize=7.5,
        color="#444444",
        ha="center",
    )
    fig.subplots_adjust(top=0.78, bottom=0.2, left=0.08, right=0.98)
    png_out.parent.mkdir(parents=True, exist_ok=True)
    save_figure(fig, png_out, dpi=300, bbox_inches="tight")
    if pdf_out:
        pdf_out.parent.mkdir(parents=True, exist_ok=True)
        save_figure(fig, pdf_out, bbox_inches="tight")
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render ATM/HDAC branch map.")
    parser.add_argument(
        "--candidate-map",
        type=Path,
        default=Path("evidence/atm_hdac_branch_vulnerability_map.tsv"),
    )
    parser.add_argument(
        "--png-out",
        type=Path,
        default=Path("figures_png/atm_hdac_branch_vulnerability_map.png"),
    )
    parser.add_argument(
        "--pdf-out",
        type=Path,
        default=Path("figures_png/atm_hdac_branch_vulnerability_map.pdf"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    render_map(pd.read_csv(args.candidate_map, sep="\t"), args.png_out, args.pdf_out)
    print(f"Wrote {args.png_out}")
    if args.pdf_out:
        print(f"Wrote {args.pdf_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
