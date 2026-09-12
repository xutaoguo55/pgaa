import pandas as pd
import pytest

from pgaa.core.result_claims import (
    build_response_specificity_claim_table,
    build_result_claim_table,
    build_stability_specificity_dual_gate,
    render_result_claim_report,
    render_stability_specificity_dual_gate_report,
    summarize_result_claims,
)


def _audit_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "audit_id": "norman_decision_benchmark:PGAA:KLF1",
                "evidence_type": "norman_decision_benchmark",
                "context": "KLF1",
                "method": "PGAA-W",
                "metric": "auprc",
                "metric_value": 0.04,
                "secondary_metric_value": 0.72,
                "recommended_action": "allow_comparative_ranking_claim",
                "failure_state": "decision_supported",
                "severity": "low",
                "allowed_interpretation": "bounded comparative claim allowed",
                "source_table": "scripts/norman_multi_perturbation_summary.csv",
            },
            {
                "audit_id": "norman_decision_benchmark:PGAA:CEBPE",
                "evidence_type": "norman_decision_benchmark",
                "context": "CEBPE",
                "method": "PGAA-W",
                "metric": "auprc",
                "metric_value": 0.01,
                "secondary_metric_value": 0.50,
                "recommended_action": "allow_descriptive_claim_only",
                "failure_state": "limited_or_descriptive",
                "severity": "moderate",
                "allowed_interpretation": "descriptive only",
                "source_table": "scripts/norman_multi_perturbation_summary.csv",
            },
            {
                "audit_id": "s2_calibration:BAK1",
                "evidence_type": "s2_calibration",
                "context": "BAK1",
                "method": "PGAA-H",
                "metric": "pi0",
                "metric_value": 0.10,
                "secondary_metric_value": 1789,
                "recommended_action": "s1_only",
                "failure_state": "catastrophic_over_sensitivity",
                "severity": "critical",
                "allowed_interpretation": "PGAA-H rejected for primary claims",
                "source_table": "scripts/table2_s2_calibration.csv",
            },
            {
                "audit_id": "manual:test",
                "evidence_type": "manual",
                "context": "unknown",
                "method": "Comparator",
                "metric": "score",
                "metric_value": 1.0,
                "secondary_metric_value": "",
                "recommended_action": "unmapped_action",
                "failure_state": "unknown",
                "severity": "manual",
                "allowed_interpretation": "manual review",
                "source_table": "manual.tsv",
            },
        ]
    )


def test_result_claim_table_maps_actions_to_manuscript_states():
    claims = build_result_claim_table(_audit_frame()).set_index("claim_id")

    supported = claims.loc["norman_decision_benchmark:PGAA:KLF1"]
    assert supported["result_claim_state"] == "comparative_support"
    assert supported["figure_panel"] == "decision_benchmark"
    assert "bounded comparative" in supported["manuscript_allowed_claim"]

    descriptive = claims.loc["norman_decision_benchmark:PGAA:CEBPE"]
    assert descriptive["result_claim_state"] == "descriptive_only"

    rejected = claims.loc["s2_calibration:BAK1"]
    assert rejected["result_claim_state"] == "failure_or_guardrail"
    assert rejected["figure_panel"] == "calibration_guardrail"

    manual = claims.loc["manual:test"]
    assert manual["result_claim_state"] == "manual_review_required"
    assert manual["figure_panel"] == "manual_review"


def test_result_claim_summary_and_report_are_manuscript_facing():
    claims = build_result_claim_table(_audit_frame())
    summary = summarize_result_claims(claims)
    report = render_result_claim_report(claims, summary)

    assert summary["n_rows"].sum() == len(claims)
    assert "PGAA Result-Claim State Report" in report
    assert "comparative_support" in report
    assert "failure_or_guardrail" in report


def test_result_claim_table_requires_failure_audit_schema():
    with pytest.raises(ValueError, match="failure audit is missing columns"):
        build_result_claim_table(pd.DataFrame({"audit_id": ["x"]}))


def test_response_specificity_gate_downgrades_stable_null_and_low_overlap():
    summary = pd.DataFrame(
        [
            {
                "method": "pgaa_w",
                "median_observed_top_k_overlap_fraction": 0.82,
                "median_pseudo_top_k_overlap_fraction": 0.81,
                "median_specificity_margin": 0.015,
                "holm_adjusted_p": 0.14,
            },
            {
                "method": "pgaa_h",
                "median_observed_top_k_overlap_fraction": 0.03,
                "median_pseudo_top_k_overlap_fraction": 0.015,
                "median_specificity_margin": 0.015,
                "holm_adjusted_p": 0.009,
            },
            {
                "method": "absolute_mean_shift",
                "median_observed_top_k_overlap_fraction": 0.675,
                "median_pseudo_top_k_overlap_fraction": 0.575,
                "median_specificity_margin": 0.08,
                "holm_adjusted_p": 0.018,
            },
        ]
    )

    claims = build_response_specificity_claim_table(summary).set_index("method")

    assert claims.loc["pgaa_w", "result_claim_state"] == "failure_or_guardrail"
    assert claims.loc["pgaa_h", "result_claim_state"] == "restricted_use"
    assert claims.loc["absolute_mean_shift", "result_claim_state"] == "comparative_support"
    assert claims["figure_panel"].eq("response_specificity_guardrail").all()


def test_stability_specificity_dual_gate_covers_all_four_states():
    replication = pd.DataFrame(
        {
            "method": ["both", "stable_only", "specific_only", "neither"],
            "median_top_k_overlap_fraction": [0.7, 0.8, 0.1, 0.05],
        }
    )
    specificity = pd.DataFrame(
        {
            "method": ["both", "stable_only", "specific_only", "neither"],
            "median_observed_top_k_overlap_fraction": [0.7, 0.8, 0.1, 0.05],
            "median_pseudo_top_k_overlap_fraction": [0.3, 0.79, 0.01, 0.04],
            "median_specificity_margin": [0.4, 0.01, 0.09, 0.01],
            "holm_adjusted_p": [0.01, 0.20, 0.01, 0.20],
        }
    )

    gate = build_stability_specificity_dual_gate(replication, specificity).set_index("method")

    assert gate.loc["both", "dual_gate_state"] == "stable_and_specific"
    assert gate.loc["stable_only", "dual_gate_state"] == "stable_but_not_specific"
    assert gate.loc["specific_only", "dual_gate_state"] == "specific_but_not_stable"
    assert gate.loc["neither", "dual_gate_state"] == "neither_stable_nor_specific"
    assert gate.loc["both", "result_claim_state"] == "comparative_support"
    assert gate.loc["stable_only", "result_claim_state"] == "failure_or_guardrail"
    assert "Response Stability-Specificity Dual Gate" in render_stability_specificity_dual_gate_report(
        gate.reset_index()
    )


def test_stability_specificity_dual_gate_rejects_method_mismatch():
    replication = pd.DataFrame(
        {"method": ["a"], "median_top_k_overlap_fraction": [0.5]}
    )
    specificity = pd.DataFrame(
        {
            "method": ["b"],
            "median_observed_top_k_overlap_fraction": [0.5],
            "median_pseudo_top_k_overlap_fraction": [0.2],
            "median_specificity_margin": [0.3],
            "holm_adjusted_p": [0.01],
        }
    )

    with pytest.raises(ValueError, match="dual-gate method mismatch"):
        build_stability_specificity_dual_gate(replication, specificity)


def test_stability_gate_uses_locked_replication_summary():
    replication = pd.DataFrame(
        {"method": ["m"], "median_top_k_overlap_fraction": [0.25]}
    )
    specificity = pd.DataFrame(
        {
            "method": ["m"],
            "median_observed_top_k_overlap_fraction": [0.15],
            "median_pseudo_top_k_overlap_fraction": [0.01],
            "median_specificity_margin": [0.14],
            "holm_adjusted_p": [0.01],
        }
    )

    gate = build_stability_specificity_dual_gate(replication, specificity).iloc[0]

    assert bool(gate["stability_gate_pass"])
    assert gate["dual_gate_state"] == "stable_and_specific"
