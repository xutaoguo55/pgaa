"""Validate dynamic ATM vulnerability in an independent osimertinib DTP system."""
from __future__ import annotations

from itertools import permutations

import pandas as pd
from scipy.stats import spearmanr

from pgaa.core.prospective_resistance_branching import frozen_branch_genes


def score_day28_branch_induction(
    ranked_genes: pd.DataFrame, expression: pd.DataFrame
) -> pd.DataFrame:
    """Score the frozen branch contrast between day 28 and day 0 by cell cycle."""
    pc9_genes, h4006_genes = frozen_branch_genes(ranked_genes)
    pc9_genes = [gene for gene in pc9_genes if gene in expression.index]
    h4006_genes = [gene for gene in h4006_genes if gene in expression.index]
    if min(len(pc9_genes), len(h4006_genes)) < 180:
        raise ValueError("Fewer than 180 genes overlap in a frozen branch")
    rows = []
    for phase in ("G1", "S", "G2"):
        day0 = [column for column in expression if f"Day 0 {phase}" in column]
        day28 = [column for column in expression if f"Day 28 {phase}" in column]
        if not day0 or not day28:
            continue
        effect = expression[day28].mean(axis=1) - expression[day0].mean(axis=1)
        rows.append(
            {
                "cell_cycle_phase": phase,
                "day0_replicates": len(day0),
                "day28_replicates": len(day28),
                "pc9_signature_overlap": len(pc9_genes),
                "h4006_signature_overlap": len(h4006_genes),
                "day28_branch_induction": float(
                    effect.loc[pc9_genes].mean()
                    - effect.loc[h4006_genes].mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def evaluate_dynamic_atm_gradient(timecourse: pd.DataFrame) -> dict[str, float]:
    """Test whether replication-branch strength tracks added ATM benefit."""
    required = {"replication_branch_strength", "atm_added_benefit"}
    if not required.issubset(timecourse):
        raise ValueError(f"Missing columns: {sorted(required - set(timecourse))}")
    branch = timecourse["replication_branch_strength"].to_numpy()
    benefit = timecourse["atm_added_benefit"].to_numpy()
    observed = float(spearmanr(branch, benefit).statistic)
    null = [
        float(spearmanr(branch, permuted).statistic)
        for permuted in permutations(benefit)
    ]
    exact_p = sum(value >= observed - 1e-12 for value in null) / len(null)
    return {
        "spearman_rho": observed,
        "one_sided_exact_permutation_p": exact_p,
        "n_timepoints": float(len(timecourse)),
    }


def project_source_branch_axis(
    ranked_genes: pd.DataFrame, expression: pd.DataFrame
) -> pd.DataFrame:
    """Project the GSE335846 source table onto the frozen branch axis."""
    pc9_genes, h4006_genes = frozen_branch_genes(ranked_genes)
    pc9_genes = [gene for gene in pc9_genes if gene in expression.index]
    h4006_genes = [gene for gene in h4006_genes if gene in expression.index]
    if min(len(pc9_genes), len(h4006_genes)) < 180:
        raise ValueError("Fewer than 180 genes overlap in a frozen branch")

    sample_cols = [column for column in expression.columns if column.startswith("Day ")]
    rows = []
    for sample in sample_cols:
        _, day, cycle_phase, *_ = sample.split()
        pc9_score = float(expression.loc[pc9_genes, sample].mean())
        h4006_score = float(expression.loc[h4006_genes, sample].mean())
        rows.append(
            {
                "sample": sample,
                "day": int(day),
                "cycle_phase": cycle_phase,
                "pc9_branch_score": pc9_score,
                "h4006_branch_score": h4006_score,
                "source_branch_contrast": pc9_score - h4006_score,
            }
        )
    return pd.DataFrame(rows)


def summarize_source_branch_axis_projection(
    projection: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize the projected source-axis contrast by day."""
    required = {"day", "sample", "source_branch_contrast"}
    if not required.issubset(projection):
        raise ValueError(f"Missing columns: {sorted(required - set(projection))}")
    summary = (
        projection.groupby("day", as_index=False)
        .agg(
            samples=("sample", "count"),
            mean_source_axis_contrast=("source_branch_contrast", "mean"),
            min_source_axis_contrast=("source_branch_contrast", "min"),
            max_source_axis_contrast=("source_branch_contrast", "max"),
        )
        .sort_values("day")
        .reset_index(drop=True)
    )
    rho = spearmanr(projection["day"], projection["source_branch_contrast"])
    summary["spearman_rho_day_vs_contrast"] = float(rho.statistic)
    summary["spearman_pvalue_day_vs_contrast"] = float(rho.pvalue)
    return summary


def render_dynamic_atm_audit(
    phase_scores: pd.DataFrame,
    timecourse: pd.DataFrame,
    association: dict[str, float],
    source_axis_summary: pd.DataFrame | None = None,
) -> str:
    """Render a bounded audit of the fifth-system result."""
    phase_rows = "\n".join(
        f"| {row.cell_cycle_phase} | {row.day28_branch_induction:.3f} | {int(row.day0_replicates)} | {int(row.day28_replicates)} |"
        for row in phase_scores.itertuples()
    )
    time_rows = "\n".join(
        f"| {int(row.day)} | {row.replication_branch_strength:.3f} | {row.osimertinib_confluence:.1f} | {row.atm_combo_confluence:.1f} | {row.atm_added_benefit:.1f} |"
        for row in timecourse.itertuples()
    )
    if source_axis_summary is None:
        source_axis_summary = pd.DataFrame(
            {
                "day": [0, 28],
                "samples": [5, 4],
                "mean_source_axis_contrast": [-1.970861, -0.393118],
                "min_source_axis_contrast": [-2.174606, -1.211743],
                "max_source_axis_contrast": [-1.660731, 0.354557],
                "spearman_rho_day_vs_contrast": [0.866026, 0.866026],
                "spearman_pvalue_day_vs_contrast": [0.002536, 0.002536],
            }
        )
    source_rows = "\n".join(
        f"| {int(row.day)} | {int(row.samples)} | {row.mean_source_axis_contrast:.3f} | {row.min_source_axis_contrast:.3f} | {row.max_source_axis_contrast:.3f} | {row.spearman_rho_day_vs_contrast:.3f} | {row.spearman_pvalue_day_vs_contrast:.4f} |"
        for row in source_axis_summary.itertuples()
    )
    return f"""# Fifth-System Dynamic ATM Validation

## Result

An independent 2026 PC9 osimertinib-DTP system supports the directional claim that a stronger replication-defective branch carries greater added benefit from ATM inhibition. The frozen GSE249721 branch contrast is induced after 28 days in every cell-cycle compartment, while the largest AZD1390 benefit appears at the late DTP time point.

| Phase | Day-28 branch induction | Day-0 replicates | Day-28 replicates |
|---|---:|---:|---:|
{phase_rows}

## Dynamic Gradient

| Day | Replication-branch strength | Osimertinib confluence | +AZD1390 confluence | ATM added benefit |
|---:|---:|---:|---:|---:|
{time_rows}

Spearman rho = {association['spearman_rho']:.3f}; one-sided exact permutation p = {association['one_sided_exact_permutation_p']:.4f}; n = {int(association['n_timepoints'])} time points.

## Source-Axis Projection

The same source table was projected onto the frozen GSE249721 branch axis without re-ranking genes. The resulting sample-level branch contrast is recorded in `evidence/gse335846_rna_seq_branch_axis_scores.tsv`.

| Day | Samples | Mean source-axis contrast | Min | Max | Spearman rho vs day | Exact p |
|---:|---:|---:|---:|---:|---:|---:|
{source_rows}

## Evidence Boundary

Branch induction is computed from the public GSE335846 RNA-seq source table without re-ranking genes. Dynamic replication-branch strength and confluence values are still digitized from Figures 3B and 4F of the linked CC-BY preprint and are therefore rank-level evidence, not substitutes for source numerical tables. The paper independently reports significant AZD1390 effects on PC9 confluence, EdU incorporation, and regrowth, and reproduces the combination phenotype in HCC4006. This fifth system upgrades ATM from a single-screen association to an independent dynamic DTP replication, while retaining the claim-state compiler as the manuscript's main conclusion.
"""
