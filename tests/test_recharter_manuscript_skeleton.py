import pandas as pd
import pytest

from pgaa.core.recharter_manuscript_skeleton import (
    build_and_render_recharter_manuscript_skeleton,
    build_recharter_story_payload,
)


def _route_scores() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "route_id": "failure_preserving_benchmark_engine",
                "route_name": "Failure-preserving perturbation benchmark engine",
                "central_object": "Benchmark failure mode and calibration object",
                "current_support": "source-driven Figure 1 and claim-bounded text",
                "next_decisive_action": "expand manuscript skeleton",
                "recommended_now": True,
            },
            {
                "route_id": "event_peptide_immune_compiler",
                "route_name": "Event-peptide immune evidence compiler",
                "central_object": "Event-peptide-HLA immune-evidence unit",
                "current_support": "blocked",
                "next_decisive_action": "add real event source",
                "recommended_now": False,
            },
        ]
    )


def _matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "benchmark_id": "main_figure_render",
                "endpoint": "source_driven_recharter_figure",
                "pass_condition": "figure rendered",
                "current_status": "complete",
                "blocking_file": "figures_png/figure1.png",
                "next_action": "draft text",
            },
            {
                "benchmark_id": "event_peptide_compiler",
                "endpoint": "auditable_event_peptide_hla_units",
                "pass_condition": "real rows",
                "current_status": "in_progress",
                "blocking_file": "evidence/event_sequence_contexts.tsv",
                "next_action": "add real source",
            },
        ]
    )


def _figure_sources() -> pd.DataFrame:
    rows = []
    base = {
        "source_kind": "",
        "context": "",
        "stability_class": "",
        "cross_dataset_status": "",
        "y_value": 0,
    }
    rows.append({**base, "panel_id": "A_claim_state_distribution", "state": "comparative_support", "y_value": 2})
    rows.append({**base, "panel_id": "A_claim_state_distribution", "state": "failure_or_guardrail", "y_value": 3})
    rows.append({**base, "panel_id": "B_responder_state_units", "state": "supported_responder_state", "context": "A"})
    rows.append({**base, "panel_id": "B_responder_state_units", "state": "provisional_responder_state", "context": "B"})
    rows.append(
        {
            **base,
            "panel_id": "C_unit_stability",
            "state": "supported_responder_state",
            "context": "A",
            "stability_class": "leave_one_method_stable",
            "cross_dataset_status": "no_cross_dataset_same_context",
        }
    )
    rows.append(
        {
            **base,
            "panel_id": "C_unit_stability",
            "state": "provisional_responder_state",
            "context": "B",
            "stability_class": "method_sensitive",
            "cross_dataset_status": "no_cross_dataset_same_context",
        }
    )
    return pd.DataFrame(rows)


def _readiness() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "check_id": "real_event_contexts",
                "status": "missing",
                "artifact": "evidence/event_sequence_contexts.tsv",
                "detail": "artifact is missing",
            },
            {
                "check_id": "real_candidate_peptides",
                "status": "missing",
                "artifact": "evidence/candidate_event_peptides.tsv",
                "detail": "artifact is missing",
            },
        ]
    )


def _novelty_upgrades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "upgrade_id": "P01.01",
                "pillar_id": "P01",
                "pillar_name": "Claim-state compiler",
                "upgrade_point": "Define PGAA as an evidence-to-claim compiler.",
                "elevation_type": "from score output to evidence-to-claim translation",
                "manuscript_role": "central framing",
                "evidence_gate": "result_claim_states plus manuscript audit",
                "current_status": "partially_implemented_in_current_recharter",
                "next_action": "Promote claim-state compiler language.",
                "claim_boundary": "claim language must be compiled from evidence rows",
                "priority_tier": "tier1_core_thesis",
            },
            {
                "upgrade_id": "P12.01",
                "pillar_id": "P12",
                "pillar_name": "Epistemic inflation control",
                "upgrade_point": "Frame the problem as evidentiary inflation.",
                "elevation_type": "from better analysis to control of evidentiary inflation",
                "manuscript_role": "highest-level thesis",
                "evidence_gate": "all claim artifacts",
                "current_status": "ready_for_manuscript_reframing",
                "next_action": "Rewrite high-level thesis.",
                "claim_boundary": "controlled interpretation only",
                "priority_tier": "tier1_core_thesis",
            },
        ]
    )


def test_recharter_story_payload_extracts_recommended_route_and_blockers():
    payload = build_recharter_story_payload(
        _route_scores(), _matrix(), _figure_sources(), _readiness()
    )

    assert payload["recommended_route"] == "failure_preserving_benchmark_engine"
    assert payload["n_benchmark_rows"] == 2
    assert payload["n_no_same_context_replication"] == 2
    assert len(payload["missing_readiness_artifacts"]) == 2


def test_recharter_story_payload_accepts_novelty_upgrade_map():
    payload = build_recharter_story_payload(
        _route_scores(), _matrix(), _figure_sources(), _readiness(), _novelty_upgrades()
    )

    assert payload["n_novelty_upgrades"] == 2
    assert payload["novelty_counts"]["tier1_core_thesis"] == 2
    assert len(payload["tier1_novelty_pillars"]) == 2


def test_recharter_manuscript_skeleton_is_claim_bounded():
    text = build_and_render_recharter_manuscript_skeleton(
        _route_scores(), _matrix(), _figure_sources(), _readiness()
    )

    assert "PGAA Recharter Manuscript Skeleton" in text
    assert "Prohibited claim" in text
    assert "Do not claim event-peptide presentation" in text
    assert "Missing Readiness Artifacts" in text


def test_recharter_manuscript_skeleton_includes_novelty_upgrade_spine():
    text = build_and_render_recharter_manuscript_skeleton(
        _route_scores(), _matrix(), _figure_sources(), _readiness(), _novelty_upgrades()
    )

    assert "Novelty Upgrade Spine" in text
    assert "claim-state compiler" in text
    assert "controlling evidentiary inflation" in text
    assert "evidence/novelty_upgrade_map.tsv" in text


def test_recharter_manuscript_skeleton_requires_schema():
    with pytest.raises(ValueError, match="route scores is missing columns"):
        build_recharter_story_payload(
            pd.DataFrame({"x": [1]}), _matrix(), _figure_sources(), _readiness()
        )
