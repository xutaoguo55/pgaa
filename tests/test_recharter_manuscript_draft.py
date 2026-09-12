import pandas as pd
import pytest

from pgaa.core.recharter_manuscript_draft import (
    build_and_render_recharter_manuscript_draft,
    build_recharter_manuscript_payload,
)


def _route_scores() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "route_id": "failure_preserving_benchmark_engine",
                "route_name": "Failure-preserving perturbation benchmark engine",
                "central_object": "Benchmark failure mode and calibration object",
                "current_support": "claim-bounded draft",
                "next_decisive_action": "expand manuscript",
                "recommended_now": True,
            }
        ]
    )


def _matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "benchmark_id": "draft",
                "endpoint": "claim_bounded_manuscript",
                "pass_condition": "draft generated",
                "current_status": "complete",
                "blocking_file": "docs/RECHARTER_MANUSCRIPT_DRAFT.md",
                "next_action": "revise",
            }
        ]
    )


def _figure_sources() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "panel_id": "A_claim_state_distribution",
                "state": "comparative_support",
                "stability_class": "",
                "cross_dataset_status": "",
                "y_value": 2,
            },
            {
                "panel_id": "A_claim_state_distribution",
                "state": "failure_or_guardrail",
                "stability_class": "",
                "cross_dataset_status": "",
                "y_value": 1,
            },
            {
                "panel_id": "B_responder_state_units",
                "state": "supported_responder_state",
                "stability_class": "",
                "cross_dataset_status": "",
                "y_value": 0.8,
            },
            {
                "panel_id": "C_unit_stability",
                "state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "y_value": 5,
            },
        ]
    )


def _readiness() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "check_id": "real_event_contexts",
                "status": "missing",
                "artifact": "evidence/event_sequence_contexts.tsv",
                "detail": "artifact is missing",
            }
        ]
    )


def _claim_states() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "result_claim_state": "comparative_support",
                "figure_panel": "decision_benchmark",
                "evidence_type": "adamson_decision_benchmark",
                "context": "A",
                "method": "PGAA-W",
                "metric": "auroc_auprc",
                "metric_value": 0.8,
                "manuscript_allowed_claim": "May support bounded interpretation.",
            },
            {
                "result_claim_state": "failure_or_guardrail",
                "figure_panel": "calibration_guardrail",
                "evidence_type": "s2_calibration",
                "context": "B",
                "method": "",
                "metric": "pi0",
                "metric_value": 0.2,
                "manuscript_allowed_claim": "Do not use for primary claims.",
            },
        ]
    )


def _units() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "context": "A",
                "decision_state": "supported_responder_state",
                "primary_method": "PGAA-W",
                "primary_metric": "auroc_auprc",
                "primary_metric_value": 0.8,
                "n_methods": 5,
                "n_comparative_support": 1,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 4,
            },
            {
                "context": "B",
                "decision_state": "provisional_responder_state",
                "primary_method": "PGAA-W",
                "primary_metric": "auroc_auprc",
                "primary_metric_value": 0.6,
                "n_methods": 4,
                "n_comparative_support": 0,
                "n_descriptive_only": 1,
                "n_failure_or_guardrail": 3,
            },
        ]
    )


def _stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "context": "A",
                "baseline_decision_state": "supported_responder_state",
                "n_leave_one_checks": 5,
                "n_state_preserved": 5,
                "n_state_changed": 0,
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
            },
            {
                "context": "B",
                "baseline_decision_state": "provisional_responder_state",
                "n_leave_one_checks": 4,
                "n_state_preserved": 3,
                "n_state_changed": 1,
                "stability_class": "method_sensitive",
                "cross_dataset_status": "no_cross_dataset_same_context",
            },
        ]
    )


def _external_stability_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "integrated_stability_class": "leave_one_method_stable_external_concordant",
                "integrated_cross_dataset_status": "external_same_context_concordant",
                "claim_ceiling": "bounded_computational_same_context_replication_allowed",
                "n_units": 1,
            },
            {
                "integrated_stability_class": "method_sensitive_external_blocked",
                "integrated_cross_dataset_status": "external_same_context_blocked",
                "claim_ceiling": "internal_only_no_external_replication_claim",
                "n_units": 1,
            },
        ]
    )


def test_recharter_manuscript_payload_summarizes_claim_bounded_inputs():
    payload = build_recharter_manuscript_payload(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
    )

    assert payload["n_claim_rows"] == 2
    assert payload["n_supported_units"] == 1
    assert payload["n_sensitive_units"] == 1
    assert payload["max_primary_metric"] == pytest.approx(0.8)


def test_recharter_manuscript_payload_summarizes_external_stability_layer():
    payload = build_recharter_manuscript_payload(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        _external_stability_summary(),
    )

    assert payload["n_external_concordant_units"] == 1
    assert payload["n_external_blocked_units"] == 1


def test_recharter_manuscript_draft_contains_required_boundaries():
    text = build_and_render_recharter_manuscript_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
    )

    assert "PGAA Recharter Manuscript Draft" in text
    assert "Forbidden Phrases For This Draft" in text
    assert "validated antigen" in text
    assert "Claim boundary" in text
    assert "no_cross_dataset_same_context" in text


def test_recharter_manuscript_draft_contains_external_claim_boundary_when_available():
    text = build_and_render_recharter_manuscript_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        _external_stability_summary(),
    )

    assert "external same-context evidence supports only bounded computational replication" in text
    assert "external_same_context_concordant" in text


def test_recharter_manuscript_draft_requires_claim_schema():
    with pytest.raises(ValueError, match="claim states is missing columns"):
        build_recharter_manuscript_payload(
            _route_scores(),
            _matrix(),
            _figure_sources(),
            _readiness(),
            pd.DataFrame({"x": [1]}),
            _units(),
            _stability(),
        )
