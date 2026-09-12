import pandas as pd
import pytest

from pgaa.core.main_figure_sources import (
    build_main_figure_sources,
    render_main_figure_source_report,
    summarize_main_figure_sources,
)


def _claim_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "figure_id": "Figure 1",
                "panel_key": "decision_benchmark",
                "result_claim_state": "comparative_support",
                "severity": "low",
                "n_rows": 2,
            },
            {
                "figure_id": "Figure 2",
                "panel_key": "calibration_guardrail",
                "result_claim_state": "failure_or_guardrail",
                "severity": "critical",
                "n_rows": 1,
            },
        ]
    )


def _units() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::A",
                "evidence_type": "adamson",
                "context": "A",
                "decision_state": "supported_responder_state",
                "primary_method": "PGAA-W",
                "primary_metric": "auroc_auprc",
                "primary_metric_value": 0.8,
                "primary_secondary_metric_value": 0.02,
                "n_methods": 3,
                "n_pgaa_methods": 2,
                "n_comparative_support": 2,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 1,
                "allowed_manuscript_use": "bounded",
            }
        ]
    )


def _stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::A",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 3,
                "n_state_preserved": 3,
                "n_state_changed": 0,
                "n_pgaa_omission_changed": 0,
            }
        ]
    )


def _integrated_stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::A",
                "integrated_stability_class": "leave_one_method_stable_external_concordant",
                "integrated_cross_dataset_status": "external_same_context_concordant",
                "claim_ceiling": "bounded_computational_same_context_replication_allowed",
            }
        ]
    )


def test_main_figure_sources_compile_three_panel_inputs():
    figure_sources = build_main_figure_sources(_claim_summary(), _units(), _stability())

    assert set(figure_sources["panel_id"]) == {
        "A_claim_state_distribution",
        "B_responder_state_units",
        "C_unit_stability",
    }
    assert len(figure_sources) == 4
    unit_row = figure_sources[figure_sources["panel_id"] == "B_responder_state_units"].iloc[0]
    assert unit_row["state"] == "supported_responder_state"
    assert unit_row["stability_class"] == "leave_one_method_stable"


def test_main_figure_sources_use_integrated_external_status_when_available():
    figure_sources = build_main_figure_sources(
        _claim_summary(), _units(), _stability(), _integrated_stability()
    )
    stability_row = figure_sources[
        figure_sources["panel_id"] == "C_unit_stability"
    ].iloc[0]
    report = render_main_figure_source_report(
        figure_sources, summarize_main_figure_sources(figure_sources)
    )

    assert stability_row["stability_class"] == "leave_one_method_stable_external_concordant"
    assert stability_row["cross_dataset_status"] == "external_same_context_concordant"
    assert "bounded_computational_same_context_replication_allowed" in stability_row[
        "allowed_manuscript_use"
    ]
    assert "external_same_context_concordant" in report


def test_main_figure_summary_and_report():
    figure_sources = build_main_figure_sources(_claim_summary(), _units(), _stability())
    summary = summarize_main_figure_sources(figure_sources)
    report = render_main_figure_source_report(figure_sources, summary)

    assert summary["n_rows"].sum() == len(figure_sources)
    assert "PGAA Main-Figure Source Report" in report
    assert "Same-context cross-dataset replication is absent" in report


def test_main_figure_sources_require_schema():
    with pytest.raises(ValueError, match="claim summary is missing columns"):
        build_main_figure_sources(pd.DataFrame({"x": [1]}), _units(), _stability())
