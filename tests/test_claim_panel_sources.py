import pandas as pd
import pytest

from pgaa.core.claim_panel_sources import (
    build_claim_panel_sources,
    render_claim_panel_report,
    summarize_claim_panels,
)


def _claim_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "claim_id": "decision:1",
                "figure_panel": "decision_benchmark",
                "evidence_type": "norman_decision_benchmark",
                "context": "KLF1",
                "method": "PGAA-W",
                "metric": "auprc",
                "metric_value": 0.04,
                "secondary_metric_value": 0.72,
                "result_claim_state": "comparative_support",
                "severity": "low",
                "manuscript_allowed_claim": "bounded claim",
                "technical_interpretation": "supported",
                "source_table": "norman.csv",
            },
            {
                "claim_id": "calibration:1",
                "figure_panel": "calibration_guardrail",
                "evidence_type": "s2_calibration",
                "context": "BAK1",
                "method": "PGAA-H",
                "metric": "pi0",
                "metric_value": 0.10,
                "secondary_metric_value": 1789,
                "result_claim_state": "failure_or_guardrail",
                "severity": "critical",
                "manuscript_allowed_claim": "reject",
                "technical_interpretation": "over-sensitive",
                "source_table": "calibration.csv",
            },
        ]
    )


def test_claim_panel_sources_assign_figure_metadata_and_ordering():
    panel_sources = build_claim_panel_sources(_claim_frame()).set_index("claim_id")

    assert panel_sources.loc["decision:1", "figure_id"] == "Figure 1"
    assert panel_sources.loc["decision:1", "panel_title"] == "Benchmark decision states"
    assert panel_sources.loc["decision:1", "claim_state_order"] == 1
    assert panel_sources.loc["calibration:1", "figure_id"] == "Figure 2"
    assert panel_sources.loc["calibration:1", "severity_order"] == 5


def test_claim_panel_summary_and_report():
    panel_sources = build_claim_panel_sources(_claim_frame())
    summary = summarize_claim_panels(panel_sources)
    report = render_claim_panel_report(panel_sources, summary)

    assert summary["n_rows"].sum() == 2
    assert "PGAA Claim-Panel Source Report" in report
    assert "comparative_support" in report


def test_claim_panel_sources_require_claim_schema():
    with pytest.raises(ValueError, match="claim table is missing columns"):
        build_claim_panel_sources(pd.DataFrame({"claim_id": ["x"]}))
