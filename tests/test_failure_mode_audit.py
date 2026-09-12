import pandas as pd

from pgaa.core.failure_mode_audit import (
    build_adamson_decision_audit,
    build_calibration_failure_audit,
    build_failure_mode_audit,
    build_norman_decision_audit,
    build_sensitivity_failure_audit,
    render_failure_mode_report,
    summarize_failure_mode_audit,
)


def test_calibration_audit_maps_verdicts_to_actions():
    calibration = pd.DataFrame(
        [
            {
                "Perturbation": "KLF1",
                "n_sig (p<0.05)": 54,
                "Storey π̂₀": 1.148,
                "Calibration verdict": "well-calibrated",
                "Recommended use": "S2 + S1",
            },
            {
                "Perturbation": "BAK1",
                "n_sig (p<0.05)": 1789,
                "Storey π̂₀": 0.104,
                "Calibration verdict": "catastrophically over-sensitive",
                "Recommended use": "S1 only",
            },
        ]
    )

    audit = build_calibration_failure_audit(calibration).set_index("context")

    assert audit.loc["KLF1", "recommended_action"] == "interpretation_ready"
    assert audit.loc["KLF1", "severity"] == "low"
    assert audit.loc["BAK1", "recommended_action"] == "s1_only"
    assert audit.loc["BAK1", "severity"] == "critical"


def test_sensitivity_audit_flags_rank_collapse_and_over_sensitivity():
    sensitivity = pd.DataFrame(
        [
            {"n_bins": 20, "elane_rank": 32, "n_sig": 66, "pi0": 1.321, "known_hits": "1/9"},
            {"n_bins": 30, "elane_rank": 1807, "n_sig": 387, "pi0": 0.407, "known_hits": "0/9"},
            {"n_bins": 50, "elane_rank": 489, "n_sig": 1063, "pi0": 0.246, "known_hits": "3/9"},
        ]
    )

    audit = build_sensitivity_failure_audit(sensitivity).set_index("context")

    assert audit.loc["n_bins=20", "failure_state"] == "calibrated_parameter_region"
    assert audit.loc["n_bins=30", "failure_state"] == "parameter_over_sensitivity"
    assert audit.loc["n_bins=50", "failure_state"] == "severe_parameter_over_sensitivity"


def test_failure_mode_summary_and_report():
    calibration = pd.DataFrame(
        [
            {
                "Perturbation": "KLF1",
                "n_sig (p<0.05)": 54,
                "Storey π̂₀": 1.148,
                "Calibration verdict": "well-calibrated",
                "Recommended use": "S2 + S1",
            }
        ]
    )
    sensitivity = pd.DataFrame(
        [{"n_bins": 20, "elane_rank": 32, "n_sig": 66, "pi0": 1.321, "known_hits": "1/9"}]
    )

    audit = build_failure_mode_audit(calibration, sensitivity)
    summary = summarize_failure_mode_audit(audit)
    report = render_failure_mode_report(audit, summary)

    assert len(audit) == 2
    assert summary["n_rows"].sum() == 2
    assert "Failure-Mode Audit" in report


def test_norman_decision_audit_assigns_claim_states():
    norman = pd.DataFrame(
        [
            {
                "target": "supported",
                "method": "PGAA_S1_Wasserstein",
                "random_auprc_baseline": 0.01,
                "auroc": 0.75,
                "auprc": 0.03,
                "top50_positive_hits": 1,
                "top100_positive_hits": 2,
            },
            {
                "target": "weak",
                "method": "Comparator",
                "random_auprc_baseline": 0.01,
                "auroc": 0.49,
                "auprc": 0.005,
                "top50_positive_hits": 0,
                "top100_positive_hits": 0,
            },
        ]
    )

    audit = build_norman_decision_audit(norman).set_index("context")

    assert audit.loc["supported", "failure_state"] == "decision_supported"
    assert audit.loc["supported", "recommended_action"] == "allow_comparative_ranking_claim"
    assert audit.loc["weak", "failure_state"] == "negative_or_failure_evidence"


def test_adamson_decision_audit_pivots_method_columns():
    adamson = pd.DataFrame(
        [
            {
                "target": "BHLHE40",
                "auroc_s1": 0.788,
                "auprc_s1": 0.0178,
                "auroc_s2": 0.833,
                "auprc_s2": 0.0594,
                "auroc_wilcox": 0.466,
                "auprc_wilcox": 0.0065,
                "auroc_ttest": 0.475,
                "auprc_ttest": 0.0066,
                "auroc_mast": 0.365,
                "auprc_mast": 0.0013,
            }
        ]
    )

    audit = build_adamson_decision_audit(adamson)
    indexed = audit.set_index("method")

    assert len(audit) == 5
    assert indexed.loc["PGAA-H histogram-shape", "failure_state"] == "decision_supported"
    assert indexed.loc["MAST", "failure_state"] == "negative_or_failure_evidence"
