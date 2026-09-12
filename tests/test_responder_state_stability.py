import pandas as pd
import pytest

from pgaa.core.responder_state_stability import (
    build_leave_one_method_stability,
    render_responder_state_stability_report,
    summarize_responder_state_stability,
)
from pgaa.core.responder_state_units import build_responder_state_units


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
                "claim_id": "adamson::A::PGAA-H",
                "panel_key": "decision_benchmark",
                "evidence_type": "adamson_decision_benchmark",
                "context": "A",
                "method": "PGAA-H histogram-shape",
                "metric": "auroc_auprc",
                "metric_value": 0.77,
                "secondary_metric_value": 0.018,
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
                "claim_id": "norman::B::KS",
                "panel_key": "decision_benchmark",
                "evidence_type": "norman_decision_benchmark",
                "context": "B",
                "method": "KS_statistic",
                "metric": "auroc_auprc_top100_hits",
                "metric_value": 0.50,
                "secondary_metric_value": 0.005,
                "result_claim_state": "failure_or_guardrail",
                "severity": "high",
                "manuscript_allowed_claim": "failure",
                "technical_interpretation": "failed",
                "source_table": "norman.csv",
            },
        ]
    )


def test_leave_one_method_stability_flags_preserved_and_changed_states():
    panel = _panel_source_frame()
    units = build_responder_state_units(panel)
    detail = build_leave_one_method_stability(panel, units)
    summary = summarize_responder_state_stability(detail, units).set_index("unit_id")

    adamson = summary.loc["adamson_decision_benchmark::A"]
    assert adamson["stability_class"] == "leave_one_method_stable"
    assert adamson["n_state_changed"] == 0

    norman = summary.loc["norman_decision_benchmark::B"]
    assert norman["stability_class"] == "method_sensitive"
    assert norman["n_state_changed"] == 1

    pgaa_omission = detail[
        (detail["unit_id"] == "norman_decision_benchmark::B")
        & (detail["omitted_method"] == "PGAA_S1_Wasserstein")
    ].iloc[0]
    assert pgaa_omission["state_preserved"] is False or not pgaa_omission["state_preserved"]


def test_responder_state_stability_report():
    panel = _panel_source_frame()
    units = build_responder_state_units(panel)
    detail = build_leave_one_method_stability(panel, units)
    summary = summarize_responder_state_stability(detail, units)
    report = render_responder_state_stability_report(summary, detail)

    assert "PGAA Responder-State Stability Report" in report
    assert "leave_one_method_stable" in report
    assert summary["n_leave_one_checks"].sum() == len(detail)


def test_responder_state_stability_requires_schema():
    with pytest.raises(ValueError, match="responder-state table is missing columns"):
        build_leave_one_method_stability(_panel_source_frame(), pd.DataFrame({"unit_id": ["x"]}))
