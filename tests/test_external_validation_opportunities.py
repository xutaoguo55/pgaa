import pandas as pd
import pytest

from pgaa.core.external_validation_opportunities import (
    build_external_validation_opportunities,
    render_external_validation_report,
    summarize_external_validation_opportunities,
)


def _units() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::BHLHE40_pDS258",
                "evidence_type": "adamson_decision_benchmark",
                "context": "BHLHE40_pDS258",
                "decision_state": "supported_responder_state",
                "primary_method": "PGAA-H",
                "primary_metric": "auroc_auprc",
                "primary_metric_value": 0.83,
                "n_comparative_support": 2,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 3,
            },
            {
                "unit_id": "adamson::SPI1_pDS255",
                "evidence_type": "adamson_decision_benchmark",
                "context": "SPI1_pDS255",
                "decision_state": "supported_responder_state",
                "primary_method": "PGAA-W",
                "primary_metric": "auroc_auprc",
                "primary_metric_value": 0.81,
                "n_comparative_support": 1,
                "n_descriptive_only": 3,
                "n_failure_or_guardrail": 1,
            },
            {
                "unit_id": "norman::CEBPE",
                "evidence_type": "norman_decision_benchmark",
                "context": "CEBPE",
                "decision_state": "provisional_responder_state",
                "primary_method": "PGAA-W",
                "primary_metric": "auroc_auprc_top100_hits",
                "primary_metric_value": 0.64,
                "n_comparative_support": 0,
                "n_descriptive_only": 4,
                "n_failure_or_guardrail": 0,
            },
        ]
    )


def _stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::BHLHE40_pDS258",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 5,
                "n_state_preserved": 5,
                "n_state_changed": 0,
            },
            {
                "unit_id": "adamson::SPI1_pDS255",
                "stability_class": "pgaa_support_dependent",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 5,
                "n_state_preserved": 4,
                "n_state_changed": 1,
            },
            {
                "unit_id": "norman::CEBPE",
                "stability_class": "method_sensitive",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 4,
                "n_state_preserved": 3,
                "n_state_changed": 1,
            },
        ]
    )


def _manifest() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset_id": "adamson2016",
                "display_name": "Adamson 2016",
                "data_type": "Perturb-seq CRISPRi",
                "analysis_role": "BHLHE40 benchmark",
                "raw_data_status": "source-data",
                "limitations": "current internal benchmark",
            }
        ]
    )


def test_external_validation_opportunities_rank_units_by_replication_value():
    opportunities = build_external_validation_opportunities(_units(), _stability(), _manifest())

    priorities = dict(zip(opportunities["unit_id"], opportunities["validation_priority"]))
    assert priorities["adamson::BHLHE40_pDS258"] == "tier1_replication_candidate"
    assert priorities["adamson::SPI1_pDS255"] == "tier2_dependency_stress_test"
    assert priorities["norman::CEBPE"] == "tier3_provisional_state_test"
    assert opportunities.iloc[0]["unit_id"] == "adamson::BHLHE40_pDS258"


def test_external_validation_opportunities_summary_and_report():
    opportunities = build_external_validation_opportunities(_units(), _stability(), _manifest())
    summary = summarize_external_validation_opportunities(opportunities)
    report = render_external_validation_report(opportunities, summary)

    assert int(summary["n_units"].sum()) == 3
    assert "This audit is a worklist, not replication evidence" in report
    assert "BHLHE40" in report


def test_external_validation_opportunities_require_unit_schema():
    units = _units().drop(columns=["decision_state"])
    with pytest.raises(ValueError, match="responder-state table is missing columns"):
        build_external_validation_opportunities(units, _stability(), _manifest())
