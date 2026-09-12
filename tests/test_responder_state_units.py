import pandas as pd
import pytest

from pgaa.core.responder_state_units import (
    build_responder_state_units,
    render_responder_state_report,
    summarize_responder_state_units,
)


def _panel_source_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "claim_id": "adamson::A::PGAA-W",
                "panel_key": "decision_benchmark",
                "evidence_type": "adamson_decision_benchmark",
                "context": "A",
                "method": "PGAA-W Wasserstein",
                "metric": "auroc_auprc",
                "metric_value": 0.80,
                "secondary_metric_value": 0.02,
                "result_claim_state": "comparative_support",
                "severity": "low",
                "manuscript_allowed_claim": "bounded positive",
                "technical_interpretation": "supported",
                "source_table": "adamson.csv",
            },
            {
                "claim_id": "adamson::A::MAST",
                "panel_key": "decision_benchmark",
                "evidence_type": "adamson_decision_benchmark",
                "context": "A",
                "method": "MAST",
                "metric": "auroc_auprc",
                "metric_value": 0.40,
                "secondary_metric_value": 0.001,
                "result_claim_state": "failure_or_guardrail",
                "severity": "high",
                "manuscript_allowed_claim": "failure",
                "technical_interpretation": "failed",
                "source_table": "adamson.csv",
            },
            {
                "claim_id": "norman::B::PGAA-W",
                "panel_key": "decision_benchmark",
                "evidence_type": "norman_decision_benchmark",
                "context": "B",
                "method": "PGAA_S1_Wasserstein",
                "metric": "auroc_auprc_top100_hits",
                "metric_value": 0.64,
                "secondary_metric_value": 0.01,
                "result_claim_state": "descriptive_only",
                "severity": "moderate",
                "manuscript_allowed_claim": "descriptive",
                "technical_interpretation": "limited",
                "source_table": "norman.csv",
            },
            {
                "claim_id": "calibration::BAK1",
                "panel_key": "calibration_guardrail",
                "evidence_type": "s2_calibration",
                "context": "BAK1",
                "method": "",
                "metric": "pi0",
                "metric_value": 0.10,
                "secondary_metric_value": "",
                "result_claim_state": "failure_or_guardrail",
                "severity": "critical",
                "manuscript_allowed_claim": "reject",
                "technical_interpretation": "over-sensitive",
                "source_table": "calibration.csv",
            },
        ]
    )


def test_responder_state_units_aggregate_contexts_and_preserve_failures():
    units = build_responder_state_units(_panel_source_frame()).set_index("unit_id")

    supported = units.loc["adamson_decision_benchmark::A"]
    assert supported["decision_state"] == "supported_responder_state"
    assert supported["primary_method"] == "PGAA-W Wasserstein"
    assert supported["n_methods"] == 2
    assert supported["n_failure_or_guardrail"] == 1
    assert "MAST" in supported["failure_or_guardrail_methods"]

    provisional = units.loc["norman_decision_benchmark::B"]
    assert provisional["decision_state"] == "provisional_responder_state"
    assert provisional["n_descriptive_only"] == 1


def test_responder_state_summary_and_report():
    units = build_responder_state_units(_panel_source_frame())
    summary = summarize_responder_state_units(units)
    report = render_responder_state_report(units, summary)

    assert summary["n_units"].sum() == len(units)
    assert "PGAA Responder-State Decision Unit Report" in report
    assert "supported_responder_state" in report


def test_responder_state_units_require_panel_schema():
    with pytest.raises(ValueError, match="panel source table is missing columns"):
        build_responder_state_units(pd.DataFrame({"claim_id": ["x"]}))
