#!/usr/bin/env python3
"""Render Bioinformatics-first method figures from claim-state evidence."""
from pathlib import Path

import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures_png"
EVIDENCE_DIR = ROOT / "evidence"


def render_claim_promotion_figure() -> None:
    summary = pd.read_csv(EVIDENCE_DIR / "claim_promotion_benchmark_summary.tsv", sep="\t")
    summary = summary[summary["scope"] == "all_scenarios"].copy()
    method_labels = {
        "claim_state_compiler": "Compiler",
        "state_blind_frozen_baseline": "Frozen\nreporting",
        "decision_only_baseline": "Decision\nonly",
        "external_only_baseline": "External\nonly",
    }
    summary["label"] = summary["method"].map(method_labels)
    summary = summary.set_index("method").loc[list(method_labels)].reset_index()

    metrics = [
        ("false_promotion_rate", "False promotion"),
        ("under_promotion_rate", "Under-promotion"),
        ("exact_permission_rate", "Exact permission"),
        ("replication_false_positive_rate", "Replication FP"),
    ]
    colors = ["#B2182B", "#EF8A62", "#2166AC", "#762A83"]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x_positions = range(len(summary))
    width = 0.18
    for offset, (column, label) in enumerate(metrics):
        values = summary[column].astype(float) * 100.0
        positions = [x + (offset - 1.5) * width for x in x_positions]
        ax.bar(positions, values, width=width, label=label, color=colors[offset])

    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(summary["label"])
    ax.set_ylabel("Scenario rate (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Claim-promotion stress test across 960 finite-state scenarios")
    ax.legend(frameon=False, ncol=2, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.7)
    fig.tight_layout()
    save_figure(fig, FIG_DIR / "figure2_claim_promotion_benchmark.png", dpi=300)
    save_figure(fig, FIG_DIR / "figure2_claim_promotion_benchmark.pdf")
    plt.close(fig)


def render_reproducibility_figure() -> None:
    claims = pd.read_csv(EVIDENCE_DIR / "result_claim_states.tsv", sep="\t")
    claim_counts = claims["result_claim_state"].value_counts().sort_values(ascending=True)

    manifest = pd.read_csv(ROOT / "DATASET_MANIFEST.tsv", sep="\t")
    status_col = "reproduction_status" if "reproduction_status" in manifest.columns else None
    if status_col is None:
        status_col = "status" if "status" in manifest.columns else None
    if status_col is not None:
        status_counts = manifest[status_col].fillna("unspecified").value_counts().sort_values(ascending=True)
    else:
        status_counts = pd.Series({"manifested sources": len(manifest)})

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.0), gridspec_kw={"width_ratios": [1.25, 1.0]})

    axes[0].barh(claim_counts.index, claim_counts.values, color="#4D9221")
    axes[0].set_title("Compiled claim states")
    axes[0].set_xlabel("Rows")
    axes[0].spines[["top", "right"]].set_visible(False)
    axes[0].grid(axis="x", color="#dddddd", linewidth=0.8, alpha=0.7)

    axes[1].barh(status_counts.index, status_counts.values, color="#4393C3")
    axes[1].set_title("Dataset/source audit states")
    axes[1].set_xlabel("Rows")
    axes[1].spines[["top", "right"]].set_visible(False)
    axes[1].grid(axis="x", color="#dddddd", linewidth=0.8, alpha=0.7)

    fig.suptitle("Reproducibility and source-data contract", y=1.02)
    fig.tight_layout()
    save_figure(fig, FIG_DIR / "figure5_reproducibility_source_audit.png", dpi=300, bbox_inches="tight")
    save_figure(fig, FIG_DIR / "figure5_reproducibility_source_audit.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    render_claim_promotion_figure()
    render_reproducibility_figure()
    print("Rendered Bioinformatics method figures.")


if __name__ == "__main__":
    main()
