"""Exploratory simple-baseline audit for the locked generality panel."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _rank(score: pd.Series, target: str) -> tuple[int, float]:
    ordered = score.sort_values(ascending=False, kind="mergesort")
    rank = int(np.flatnonzero(ordered.index.astype(str) == target)[0]) + 1
    return rank, rank / len(ordered)


def compile_generality_baselines(
    contract: pd.DataFrame, pgaa_results: pd.DataFrame
) -> pd.DataFrame:
    """Compare PGAA target ranks with mean-shift and Welch-statistic ranks."""
    required = {"target_gene", "expression_csv", "metadata_csv"}
    missing = sorted(required - set(contract.columns))
    if missing:
        raise ValueError(f"Contract is missing columns: {', '.join(missing)}")
    pgaa = pgaa_results.set_index("target_gene")
    rows: list[dict[str, object]] = []
    for _, row in contract.iterrows():
        target = str(row["target_gene"])
        expression = pd.read_csv(Path(str(row["expression_csv"])), index_col=0)
        metadata = pd.read_csv(Path(str(row["metadata_csv"]))).set_index("cell_id")
        metadata = metadata.loc[expression.index.astype(str)]
        target_x = expression.loc[metadata["group"].astype(str) == "perturbed"]
        control_x = expression.loc[metadata["group"].astype(str) == "control"]
        mean_shift = (target_x.mean(axis=0) - control_x.mean(axis=0)).abs()
        variance = target_x.var(axis=0, ddof=1) / len(target_x) + control_x.var(axis=0, ddof=1) / len(control_x)
        welch = (target_x.mean(axis=0) - control_x.mean(axis=0)).abs() / np.sqrt(variance.replace(0, np.nan))
        welch = welch.fillna(0.0)
        mean_rank, mean_pct = _rank(mean_shift, target)
        welch_rank, welch_pct = _rank(welch, target)
        current = pgaa.loc[target]
        rows.append(
            {
                "target_gene": target,
                "pgaa_w_rank": int(current["pgaa_w_rank"]),
                "pgaa_w_percentile": float(current["pgaa_w_percentile"]),
                "pgaa_h_rank": int(current["pgaa_h_rank"]),
                "pgaa_h_percentile": float(current["pgaa_h_percentile"]),
                "absolute_mean_shift_rank": mean_rank,
                "absolute_mean_shift_percentile": mean_pct,
                "welch_abs_t_rank": welch_rank,
                "welch_abs_t_percentile": welch_pct,
                "mean_shift_top10pct": mean_pct <= 0.10,
                "welch_top10pct": welch_pct <= 0.10,
                "pgaa_w_beats_both_baselines": float(current["pgaa_w_percentile"]) < min(mean_pct, welch_pct),
                "pgaa_h_beats_both_baselines": float(current["pgaa_h_percentile"]) < min(mean_pct, welch_pct),
                "analysis_role": "post_pilot_exploratory_baseline_audit",
            }
        )
    return pd.DataFrame(rows)


def summarize_generality_baselines(comparison: pd.DataFrame) -> pd.DataFrame:
    metrics = {
        "pgaa_w_top10pct": comparison["pgaa_w_percentile"] <= 0.10,
        "pgaa_h_top10pct": comparison["pgaa_h_percentile"] <= 0.10,
        "absolute_mean_shift_top10pct": comparison["mean_shift_top10pct"],
        "welch_abs_t_top10pct": comparison["welch_top10pct"],
        "pgaa_w_beats_both_baselines": comparison["pgaa_w_beats_both_baselines"],
        "pgaa_h_beats_both_baselines": comparison["pgaa_h_beats_both_baselines"],
    }
    return pd.DataFrame(
        [
            {
                "metric": name,
                "n_targets": int(mask.sum()),
                "n_locked_targets": len(comparison),
                "fraction": float(mask.mean()),
            }
            for name, mask in metrics.items()
        ]
    )


def render_generality_baseline_report(
    comparison: pd.DataFrame, summary: pd.DataFrame
) -> str:
    lines = [
        "# Replogle Essential Generality Baseline Audit",
        "",
        "This is a post-pilot exploratory comparator audit. Absolute mean shift and absolute Welch t-statistic were added after the locked panel run to test whether direct target recovery alone distinguishes PGAA from conventional summaries; they are not preregistered primary endpoints.",
        "",
        "| Metric | Targets / locked | Fraction |",
        "|---|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['metric']}` | {int(row['n_targets'])}/{int(row['n_locked_targets'])} | {float(row['fraction']):.1%} |"
        )
    lines.extend(
        [
            "",
            "| Target | W pct | H pct | Mean-shift pct | Welch pct | W beats both | H beats both |",
            "|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for _, row in comparison.iterrows():
        lines.append(
            f"| `{row['target_gene']}` | {row['pgaa_w_percentile']:.3f} | {row['pgaa_h_percentile']:.3f} | "
            f"{row['absolute_mean_shift_percentile']:.3f} | {row['welch_abs_t_percentile']:.3f} | "
            f"{bool(row['pgaa_w_beats_both_baselines'])} | {bool(row['pgaa_h_beats_both_baselines'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "A high target-recovery rate shared by simple baselines demonstrates assay signal, not PGAA superiority. Method-specific value requires better ranks, complementary recovery, calibration, or claim-control behavior beyond these baselines. This audit uses one experiment and cannot establish independent biological replication.",
            "",
        ]
    )
    return "\n".join(lines)
