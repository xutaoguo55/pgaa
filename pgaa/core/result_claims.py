"""Compile failure-mode audit rows into manuscript-facing claim states."""
from __future__ import annotations

import pandas as pd


CLAIM_STATE_BY_ACTION = {
    "allow_comparative_ranking_claim": (
        "comparative_support",
        "May support a bounded comparative ranking claim for this endpoint.",
        "decision_benchmark",
    ),
    "allow_descriptive_claim_only": (
        "descriptive_only",
        "Report descriptively; do not use as a strong superiority claim.",
        "decision_benchmark",
    ),
    "report_as_failure_or_comparator_limit": (
        "failure_or_guardrail",
        "Report as weak evidence, a comparator limit, or a failure mode.",
        "decision_benchmark",
    ),
    "interpretation_ready": (
        "calibration_support",
        "Calibration supports cautious interpretation of this statistic.",
        "calibration_guardrail",
    ),
    "use_with_diagnostic": (
        "calibration_support",
        "Use only with the calibration diagnostic shown.",
        "calibration_guardrail",
    ),
    "prefer_s1": (
        "restricted_use",
        "Prefer PGAA-W unless PGAA-H has independent support.",
        "calibration_guardrail",
    ),
    "s1_only": (
        "failure_or_guardrail",
        "Do not use PGAA-H for primary positive claims in this context.",
        "calibration_guardrail",
    ),
    "s2_caution_only": (
        "restricted_use",
        "PGAA-H can support ranking anecdotes only, not broad discovery claims.",
        "calibration_guardrail",
    ),
    "eligible_default_with_controls": (
        "calibration_support",
        "Parameter setting is eligible only with control diagnostics shown.",
        "parameter_guardrail",
    ),
    "reject_for_primary_analysis": (
        "failure_or_guardrail",
        "Reject this setting for primary analysis.",
        "parameter_guardrail",
    ),
    "do_not_tune_on_positive_case": (
        "failure_or_guardrail",
        "Use only as a parameter-sensitivity failure demonstration.",
        "parameter_guardrail",
    ),
    "require_control_sweep": (
        "restricted_use",
        "Requires additional control sweeps before manuscript claims.",
        "parameter_guardrail",
    ),
    "allow_pseudo_guarded_stability_claim": (
        "comparative_support",
        "May support a bounded response-stability claim after the pseudo-perturbation gate.",
        "response_specificity_guardrail",
    ),
    "diagnostic_specificity_only": (
        "restricted_use",
        "Report specificity diagnostically because absolute ranking stability is too low.",
        "response_specificity_guardrail",
    ),
    "reject_response_specific_superiority": (
        "failure_or_guardrail",
        "Do not claim response-specific superiority because pseudo-perturbation stability explains the result.",
        "response_specificity_guardrail",
    ),
}


def _claim_mapping(action: object) -> tuple[str, str, str]:
    return CLAIM_STATE_BY_ACTION.get(
        str(action),
        (
            "manual_review_required",
            "Manual review required before manuscript use.",
            "manual_review",
        ),
    )


def build_result_claim_table(audit: pd.DataFrame) -> pd.DataFrame:
    """Derive manuscript-facing claim states from a failure-mode audit."""
    required = {
        "audit_id",
        "evidence_type",
        "context",
        "recommended_action",
        "failure_state",
        "severity",
        "allowed_interpretation",
        "source_table",
    }
    missing = sorted(required - set(audit.columns))
    if missing:
        raise ValueError(f"failure audit is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in audit.iterrows():
        result_claim_state, allowed_claim, figure_panel = _claim_mapping(row["recommended_action"])
        rows.append(
            {
                "claim_id": row["audit_id"],
                "figure_panel": figure_panel,
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "method": row["method"] if "method" in audit.columns and pd.notna(row.get("method")) else "",
                "metric": row["metric"] if "metric" in audit.columns else "",
                "metric_value": row["metric_value"] if "metric_value" in audit.columns else "",
                "secondary_metric_value": (
                    row["secondary_metric_value"]
                    if "secondary_metric_value" in audit.columns and pd.notna(row.get("secondary_metric_value"))
                    else ""
                ),
                "result_claim_state": result_claim_state,
                "internal_failure_state": row["failure_state"],
                "severity": row["severity"],
                "recommended_action": row["recommended_action"],
                "manuscript_allowed_claim": allowed_claim,
                "technical_interpretation": row["allowed_interpretation"],
                "source_table": row["source_table"],
            }
        )
    return pd.DataFrame(rows)


def build_response_specificity_claim_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Compile pseudo-guarded response stability into manuscript-facing claim states."""
    required = {
        "method",
        "median_observed_top_k_overlap_fraction",
        "median_pseudo_top_k_overlap_fraction",
        "median_specificity_margin",
        "holm_adjusted_p",
    }
    missing = sorted(required - set(summary.columns))
    if missing:
        raise ValueError(f"response specificity summary is missing columns: {missing}")
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        method = str(row["method"])
        observed = float(row["median_observed_top_k_overlap_fraction"])
        pseudo = float(row["median_pseudo_top_k_overlap_fraction"])
        margin = float(row["median_specificity_margin"])
        adjusted_p = float(row["holm_adjusted_p"])
        if adjusted_p > 0.05 or margin <= 0:
            action = "reject_response_specific_superiority"
            failure_state = "stability_not_response_specific"
            severity = "high"
            interpretation = (
                "Observed cross-batch stability is not distinguishable from matched "
                "control-versus-control stability."
            )
        elif observed < 0.20:
            action = "diagnostic_specificity_only"
            failure_state = "specificity_detected_but_absolute_stability_low"
            severity = "moderate"
            interpretation = (
                "The specificity margin is positive, but absolute top-k replication is too "
                "low for a primary stability claim."
            )
        else:
            action = "allow_pseudo_guarded_stability_claim"
            failure_state = "pseudo_guarded_stability_support"
            severity = "low"
            interpretation = (
                "Observed top-k replication exceeds matched pseudo-perturbation stability "
                "with multiplicity control."
            )
        claim_state, allowed_claim, figure_panel = _claim_mapping(action)
        rows.append(
            {
                "claim_id": f"response_specificity::{method}",
                "figure_panel": figure_panel,
                "evidence_type": "heldout_batch_response_specificity",
                "context": "Replogle_K562_essential_16_target_panel",
                "method": method,
                "metric": "median_observed_top100_overlap",
                "metric_value": observed,
                "secondary_metric_value": margin,
                "result_claim_state": claim_state,
                "internal_failure_state": failure_state,
                "severity": severity,
                "recommended_action": action,
                "manuscript_allowed_claim": allowed_claim,
                "technical_interpretation": interpretation,
                "source_table": "evidence/replogle_essential_response_specificity_summary.tsv",
                "pseudo_overlap": pseudo,
                "holm_adjusted_p": adjusted_p,
            }
        )
    return pd.DataFrame(rows)


def build_stability_specificity_dual_gate(
    replication_summary: pd.DataFrame,
    specificity_summary: pd.DataFrame,
    *,
    minimum_stable_overlap: float = 0.20,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Classify methods by absolute replication and pseudo-guarded specificity.

    The two gates answer different questions: whether a ranking replicates at a
    usable absolute level, and whether that replication exceeds matched
    control-versus-control structure. Passing only one gate is not sufficient
    for a primary response-stability claim.
    """
    replication_required = {"method", "median_top_k_overlap_fraction"}
    specificity_required = {
        "method",
        "median_observed_top_k_overlap_fraction",
        "median_pseudo_top_k_overlap_fraction",
        "median_specificity_margin",
        "holm_adjusted_p",
    }
    missing_replication = sorted(replication_required - set(replication_summary.columns))
    missing_specificity = sorted(specificity_required - set(specificity_summary.columns))
    if missing_replication:
        raise ValueError(f"response replication summary is missing columns: {missing_replication}")
    if missing_specificity:
        raise ValueError(f"response specificity summary is missing columns: {missing_specificity}")
    if not 0 < minimum_stable_overlap <= 1:
        raise ValueError("minimum_stable_overlap must be in (0, 1]")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")

    merged = replication_summary[list(replication_required)].merge(
        specificity_summary[list(specificity_required)],
        on="method",
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    if not merged["_merge"].eq("both").all():
        unmatched = merged.loc[~merged["_merge"].eq("both"), ["method", "_merge"]]
        raise ValueError(f"dual-gate method mismatch: {unmatched.to_dict('records')}")

    rows: list[dict[str, object]] = []
    for _, row in merged.drop(columns="_merge").iterrows():
        replication_overlap = float(row["median_top_k_overlap_fraction"])
        observed_overlap = float(row["median_observed_top_k_overlap_fraction"])
        pseudo_overlap = float(row["median_pseudo_top_k_overlap_fraction"])
        margin = float(row["median_specificity_margin"])
        adjusted_p = float(row["holm_adjusted_p"])
        stability_pass = replication_overlap >= minimum_stable_overlap
        specificity_pass = margin > 0 and adjusted_p <= alpha

        if stability_pass and specificity_pass:
            dual_gate_state = "stable_and_specific"
            result_claim_state = "comparative_support"
            allowed_claim = "Bounded response-stability claim allowed within this benchmark."
        elif stability_pass:
            dual_gate_state = "stable_but_not_specific"
            result_claim_state = "failure_or_guardrail"
            allowed_claim = "Report reproducibility only; reject response-specific superiority."
        elif specificity_pass:
            dual_gate_state = "specific_but_not_stable"
            result_claim_state = "restricted_use"
            allowed_claim = "Report as a specificity diagnostic, not a usable stable ranking."
        else:
            dual_gate_state = "neither_stable_nor_specific"
            result_claim_state = "failure_or_guardrail"
            allowed_claim = "Do not use for response-stability claims."

        rows.append(
            {
                "method": row["method"],
                "replication_overlap": replication_overlap,
                "observed_overlap": observed_overlap,
                "pseudo_overlap": pseudo_overlap,
                "specificity_margin": margin,
                "holm_adjusted_p": adjusted_p,
                "minimum_stable_overlap": minimum_stable_overlap,
                "specificity_alpha": alpha,
                "stability_gate_pass": stability_pass,
                "specificity_gate_pass": specificity_pass,
                "dual_gate_state": dual_gate_state,
                "result_claim_state": result_claim_state,
                "manuscript_allowed_claim": allowed_claim,
            }
        )
    return pd.DataFrame(rows).sort_values("method").reset_index(drop=True)


def render_stability_specificity_dual_gate_report(gate: pd.DataFrame) -> str:
    """Render the two-gate decision object as a manuscript-facing report."""
    required = {
        "method",
        "observed_overlap",
        "pseudo_overlap",
        "specificity_margin",
        "holm_adjusted_p",
        "stability_gate_pass",
        "specificity_gate_pass",
        "dual_gate_state",
        "manuscript_allowed_claim",
    }
    missing = sorted(required - set(gate.columns))
    if missing:
        raise ValueError(f"dual-gate table is missing columns: {missing}")
    lines = [
        "# Response Stability-Specificity Dual Gate",
        "",
        "A ranking must pass both an absolute held-out replication gate and a matched "
        "pseudo-perturbation specificity gate before it can support a bounded response-stability claim.",
        "",
        "| Method | Observed overlap | Pseudo overlap | Margin | Holm p | Stability | Specificity | State |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in gate.iterrows():
        lines.append(
            f"| {row['method']} | {row['observed_overlap']:.3f} | {row['pseudo_overlap']:.3f} | "
            f"{row['specificity_margin']:.3f} | {row['holm_adjusted_p']:.4g} | "
            f"{'pass' if row['stability_gate_pass'] else 'fail'} | "
            f"{'pass' if row['specificity_gate_pass'] else 'fail'} | {row['dual_gate_state']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for _, row in gate.iterrows():
        lines.append(f"- `{row['method']}`: {row['manuscript_allowed_claim']}")
    lines.extend(
        [
            "",
            "The 0.20 stability threshold is a post-result decision floor fixed in this compiler, "
            "not a preregistered threshold or a universal biological constant. The specificity gate "
            "requires a positive median margin and Holm-adjusted p <= 0.05. Conclusions near either "
            "boundary require threshold sensitivity analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_result_claims(claims: pd.DataFrame) -> pd.DataFrame:
    """Summarize manuscript-facing claim states for figure captions and QC."""
    required = {"figure_panel", "result_claim_state"}
    missing = sorted(required - set(claims.columns))
    if missing:
        raise ValueError(f"claim table is missing columns: {missing}")
    return (
        claims.groupby(["figure_panel", "result_claim_state"], dropna=False)
        .size()
        .reset_index(name="n_rows")
        .sort_values(["figure_panel", "result_claim_state"])
    )


def render_result_claim_report(claims: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render the manuscript-facing claim-state report."""
    lines = [
        "# PGAA Result-Claim State Report",
        "",
        f"Claim rows: {len(claims)}",
        "",
        "## Claim-State Summary",
        "",
        "| Figure panel | Result claim state | Rows |",
        "|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['figure_panel']} | {row['result_claim_state']} | {row['n_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "`comparative_support` rows can support bounded benchmark statements. "
            "`descriptive_only` rows can be reported but should not carry superiority language. "
            "`failure_or_guardrail` and `restricted_use` rows are part of the method object: "
            "they define when PGAA outputs should be limited, rejected, or shown as failure modes.",
            "",
        ]
    )
    return "\n".join(lines)
