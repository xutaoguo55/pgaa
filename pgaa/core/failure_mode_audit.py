"""Failure-preserving audit tables for PGAA benchmark interpretation."""
from __future__ import annotations

import pandas as pd


CALIBRATION_ACTIONS = {
    "well-calibrated": ("interpretation_ready", "low", "S2 can be interpreted with S1."),
    "acceptable": ("use_with_diagnostic", "low", "S2 can be used with calibration reporting."),
    "mild over-sensitive": ("prefer_s1", "moderate", "Prefer S1 unless S2 has strong external support."),
    "over-sensitive": ("s1_only", "high", "Do not use S2 for positive claims."),
    "severely over-sensitive": ("s2_caution_only", "very_high", "S2 supports ranking anecdotes only."),
    "catastrophically over-sensitive": ("s1_only", "critical", "Treat S2 positives as calibration failure."),
}


def _calibration_action(verdict: object) -> tuple[str, str, str]:
    normalized = str(verdict).strip().lower()
    return CALIBRATION_ACTIONS.get(
        normalized,
        ("manual_review", "unknown", f"Unmapped calibration verdict: {verdict}"),
    )


def build_calibration_failure_audit(calibration: pd.DataFrame) -> pd.DataFrame:
    """Convert the S2 calibration table into failure-preserving audit rows."""
    required = ["Perturbation", "n_sig (p<0.05)", "Storey π̂₀", "Calibration verdict", "Recommended use"]
    missing = [column for column in required if column not in calibration.columns]
    if missing:
        raise ValueError(f"calibration table is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in calibration.iterrows():
        action, severity, allowed_interpretation = _calibration_action(row["Calibration verdict"])
        rows.append(
            {
                "audit_id": f"s2_calibration::{row['Perturbation']}",
                "evidence_type": "s2_calibration",
                "context": row["Perturbation"],
                "metric": "Storey_pi0",
                "metric_value": float(row["Storey π̂₀"]),
                "n_flagged": int(row["n_sig (p<0.05)"]),
                "failure_state": str(row["Calibration verdict"]),
                "severity": severity,
                "recommended_action": action,
                "allowed_interpretation": allowed_interpretation,
                "source_table": "scripts/table2_s2_calibration.csv",
            }
        )
    return pd.DataFrame(rows)


def _sensitivity_state(pi0: float, n_sig: int, elane_rank: int) -> tuple[str, str, str, str]:
    if pi0 < 0.3:
        state = "severe_parameter_over_sensitivity"
        severity = "very_high"
        action = "do_not_tune_on_positive_case"
        interpretation = "Bin setting creates too many nominal positives; use only as failure demonstration."
    elif pi0 < 0.5:
        state = "parameter_over_sensitivity"
        severity = "high"
        action = "reject_for_primary_analysis"
        interpretation = "S2 is too sensitive at this bin setting for primary claims."
    elif elane_rank > 1000:
        state = "rank_collapse"
        severity = "high"
        action = "reject_for_primary_analysis"
        interpretation = "Known target rank collapses under this parameter setting."
    elif pi0 >= 0.8 and n_sig < 200:
        state = "calibrated_parameter_region"
        severity = "low"
        action = "eligible_default_with_controls"
        interpretation = "Parameter setting is compatible with cautious ranking use."
    else:
        state = "manual_review"
        severity = "moderate"
        action = "require_control_sweep"
        interpretation = "Parameter setting requires additional negative-control checks."
    return state, severity, action, interpretation


def build_sensitivity_failure_audit(sensitivity: pd.DataFrame) -> pd.DataFrame:
    """Convert S2 bin sensitivity into failure-preserving audit rows."""
    required = ["n_bins", "elane_rank", "n_sig", "pi0", "known_hits"]
    missing = [column for column in required if column not in sensitivity.columns]
    if missing:
        raise ValueError(f"sensitivity table is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in sensitivity.iterrows():
        state, severity, action, interpretation = _sensitivity_state(
            float(row["pi0"]),
            int(row["n_sig"]),
            int(row["elane_rank"]),
        )
        rows.append(
            {
                "audit_id": f"s2_nbins::{int(row['n_bins'])}",
                "evidence_type": "s2_parameter_sensitivity",
                "context": f"n_bins={int(row['n_bins'])}",
                "metric": "pi0_and_elane_rank",
                "metric_value": float(row["pi0"]),
                "n_flagged": int(row["n_sig"]),
                "failure_state": state,
                "severity": severity,
                "recommended_action": action,
                "allowed_interpretation": interpretation,
                "source_table": "scripts/sensitivity_s2_bins.csv",
            }
        )
    return pd.DataFrame(rows)


def _claim_state_from_metrics(
    auroc: float,
    auprc: float,
    baseline_auprc: float | None = None,
    top_hits: int | None = None,
) -> tuple[str, str, str, str]:
    if auroc >= 0.70 and (baseline_auprc is None or auprc >= 2 * baseline_auprc):
        if top_hits is None or top_hits > 0:
            return (
                "decision_supported",
                "low",
                "allow_comparative_ranking_claim",
                "Benchmark row supports a comparative ranking claim with explicit endpoint limits.",
            )
    if auroc >= 0.60 or (baseline_auprc is not None and auprc > baseline_auprc):
        return (
            "limited_or_descriptive",
            "moderate",
            "allow_descriptive_claim_only",
            "Benchmark row is useful descriptively but should not carry a strong superiority claim.",
        )
    return (
        "negative_or_failure_evidence",
        "high",
        "report_as_failure_or_comparator_limit",
        "Benchmark row should be reported as weak, negative, or comparator-limited evidence.",
    )


def build_norman_decision_audit(norman: pd.DataFrame) -> pd.DataFrame:
    """Convert Norman multi-perturbation method rows into claim-state audit rows."""
    required = [
        "target",
        "method",
        "random_auprc_baseline",
        "auroc",
        "auprc",
        "top50_positive_hits",
        "top100_positive_hits",
    ]
    missing = [column for column in required if column not in norman.columns]
    if missing:
        raise ValueError(f"Norman summary table is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in norman.iterrows():
        top_hits = int(row["top100_positive_hits"])
        state, severity, action, interpretation = _claim_state_from_metrics(
            float(row["auroc"]),
            float(row["auprc"]),
            float(row["random_auprc_baseline"]),
            top_hits,
        )
        method = str(row["method"])
        rows.append(
            {
                "audit_id": f"norman_decision::{row['target']}::{method}",
                "evidence_type": "norman_decision_benchmark",
                "context": row["target"],
                "method": method,
                "metric": "auroc_auprc_top100_hits",
                "metric_value": float(row["auroc"]),
                "secondary_metric_value": float(row["auprc"]),
                "n_flagged": top_hits,
                "failure_state": state,
                "severity": severity,
                "recommended_action": action,
                "allowed_interpretation": interpretation,
                "source_table": "scripts/norman_multi_perturbation_summary.csv",
            }
        )
    return pd.DataFrame(rows)


def build_adamson_decision_audit(adamson_full: pd.DataFrame) -> pd.DataFrame:
    """Convert Adamson perturbation rows into method-specific claim-state audit rows."""
    method_columns = {
        "PGAA-W Wasserstein": ("auroc_s1", "auprc_s1"),
        "PGAA-H histogram-shape": ("auroc_s2", "auprc_s2"),
        "Wilcoxon rank-sum": ("auroc_wilcox", "auprc_wilcox"),
        "t-test": ("auroc_ttest", "auprc_ttest"),
        "MAST": ("auroc_mast", "auprc_mast"),
    }
    required = ["target", *[column for pair in method_columns.values() for column in pair]]
    missing = [column for column in required if column not in adamson_full.columns]
    if missing:
        raise ValueError(f"Adamson full-results table is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in adamson_full.iterrows():
        for method, (auroc_col, auprc_col) in method_columns.items():
            state, severity, action, interpretation = _claim_state_from_metrics(
                float(row[auroc_col]),
                float(row[auprc_col]),
                None,
                None,
            )
            rows.append(
                {
                    "audit_id": f"adamson_decision::{row['target']}::{method}",
                    "evidence_type": "adamson_decision_benchmark",
                    "context": row["target"],
                    "method": method,
                    "metric": "auroc_auprc",
                    "metric_value": float(row[auroc_col]),
                    "secondary_metric_value": float(row[auprc_col]),
                    "n_flagged": 0,
                    "failure_state": state,
                    "severity": severity,
                    "recommended_action": action,
                    "allowed_interpretation": interpretation,
                    "source_table": "scripts/adamson2016_full_results.csv",
                }
            )
    return pd.DataFrame(rows)


def build_failure_mode_audit(
    calibration: pd.DataFrame,
    sensitivity: pd.DataFrame,
    norman: pd.DataFrame | None = None,
    adamson_full: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build a combined failure-mode audit from existing benchmark tables."""
    tables = [
        build_calibration_failure_audit(calibration),
        build_sensitivity_failure_audit(sensitivity),
    ]
    if norman is not None:
        tables.append(build_norman_decision_audit(norman))
    if adamson_full is not None:
        tables.append(build_adamson_decision_audit(adamson_full))
    return pd.concat(tables, ignore_index=True)


def summarize_failure_mode_audit(audit: pd.DataFrame) -> pd.DataFrame:
    """Summarize failure-mode severity counts."""
    required = {"evidence_type", "severity", "recommended_action"}
    missing = sorted(required - set(audit.columns))
    if missing:
        raise ValueError(f"audit table is missing columns: {missing}")
    return (
        audit.groupby(["evidence_type", "severity", "recommended_action"], dropna=False)
        .size()
        .reset_index(name="n_rows")
        .sort_values(["evidence_type", "severity", "recommended_action"])
    )


def render_failure_mode_report(audit: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render the failure-preserving benchmark report."""
    high_risk = audit[audit["severity"].isin(["high", "very_high", "critical"])]
    lines = [
        "# PGAA Failure-Mode Audit",
        "",
        f"Audited rows: {len(audit)}",
        f"High-risk or critical rows: {len(high_risk)}",
        "",
        "## Severity Summary",
        "",
        "| Evidence type | Severity | Recommended action | Rows |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['evidence_type']} | {row['severity']} | "
            f"{row['recommended_action']} | {row['n_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The failure-preserving route is currently better supported than the event-peptide "
            "route because it uses existing PGAA benchmark artifacts and converts failures "
            "into explicit interpretation states. This does not make PGAA a top-journal "
            "paper by itself, but it creates a stronger method object than a score-only "
            "ranking tool.",
            "",
        "High-risk rows must be shown, not hidden. They define where PGAA-H should be "
        "restricted, where PGAA-W is preferred, and where parameter choices are not "
        "acceptable for primary claims.",
            "",
            "Decision-benchmark rows extend the same principle to method-comparison tables: "
            "each row receives a claim state before it can be used in manuscript language.",
            "",
        ]
    )
    return "\n".join(lines)
