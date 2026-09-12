import pandas as pd
import pytest

from pgaa.core.claim_state_formalization import (
    audit_claim_state_invariants,
    build_claim_state_space,
    build_claim_transition_rules,
    build_formal_decision_objects,
    compile_unit_claim_ceiling,
    render_claim_state_formalization_report,
)
from pgaa.core.result_claims import CLAIM_STATE_BY_ACTION


def _claims() -> pd.DataFrame:
    rows = [
        ("a1", "set_a", "A", "PGAA-W", "allow_comparative_ranking_claim"),
        ("a2", "set_a", "A", "Comparator", "report_as_failure_or_comparator_limit"),
        ("b1", "set_b", "B", "PGAA-H", "allow_descriptive_claim_only"),
    ]
    compiled = []
    for claim_id, evidence_type, context, method, action in rows:
        state, allowed, _panel = CLAIM_STATE_BY_ACTION[action]
        compiled.append(
            {
                "claim_id": claim_id,
                "evidence_type": evidence_type,
                "context": context,
                "method": method,
                "recommended_action": action,
                "result_claim_state": state,
                "manuscript_allowed_claim": allowed,
            }
        )
    return pd.DataFrame(compiled)


def _units() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "set_a::A",
                "evidence_type": "set_a",
                "context": "A",
                "decision_state": "supported_responder_state",
                "n_comparative_support": 1,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 1,
            },
            {
                "unit_id": "set_b::B",
                "evidence_type": "set_b",
                "context": "B",
                "decision_state": "provisional_responder_state",
                "n_comparative_support": 0,
                "n_descriptive_only": 1,
                "n_failure_or_guardrail": 0,
            },
        ]
    )


def _stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "set_a::A",
                "baseline_decision_state": "supported_responder_state",
                "n_leave_one_checks": 2,
                "n_state_preserved": 2,
                "n_state_changed": 0,
                "n_pgaa_omission_changed": 0,
                "stability_class": "leave_one_method_stable",
            },
            {
                "unit_id": "set_b::B",
                "baseline_decision_state": "provisional_responder_state",
                "n_leave_one_checks": 1,
                "n_state_preserved": 0,
                "n_state_changed": 1,
                "n_pgaa_omission_changed": 0,
                "stability_class": "method_sensitive",
            },
        ]
    )


def _integrated() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "set_a::A",
                "baseline_decision_state": "supported_responder_state",
                "internal_stability_class": "leave_one_method_stable",
                "integrated_cross_dataset_status": "external_same_context_concordant",
                "claim_ceiling": "bounded_computational_same_context_replication_allowed",
            },
            {
                "unit_id": "set_b::B",
                "baseline_decision_state": "provisional_responder_state",
                "internal_stability_class": "method_sensitive",
                "integrated_cross_dataset_status": "external_same_context_blocked",
                "claim_ceiling": "internal_only_no_external_replication_claim",
            },
        ]
    )


def test_compile_unit_claim_ceiling_requires_all_replication_preconditions():
    allowed = compile_unit_claim_ceiling(
        "supported_responder_state",
        "leave_one_method_stable",
        "external_same_context_concordant",
    )
    blocked = compile_unit_claim_ceiling(
        "supported_responder_state",
        "leave_one_method_stable",
        "external_same_context_blocked",
    )
    unstable = compile_unit_claim_ceiling(
        "supported_responder_state",
        "method_sensitive",
        "external_same_context_concordant",
    )

    assert allowed["permission_rank"] == 3
    assert allowed["compiled_claim_ceiling"] == "bounded_computational_same_context_replication"
    assert blocked["permission_rank"] == 2
    assert unstable["permission_rank"] == 2
    assert not allowed["wet_lab_claim_allowed"]


def test_formalization_audits_current_contract_and_renders_report():
    state_space = build_claim_state_space()
    transitions = build_claim_transition_rules()
    objects = build_formal_decision_objects(_units(), _stability(), _integrated())
    audit = audit_claim_state_invariants(
        _claims(), _units(), _stability(), _integrated(), objects
    )
    report = render_claim_state_formalization_report(
        state_space, transitions, objects, audit
    )

    assert len(audit) == 12
    assert set(audit["status"]) == {"pass"}
    assert objects.loc[objects["unit_id"] == "set_a::A", "permission_rank"].item() == 3
    assert "computational replication permission is emitted if and only if" in report
    assert "Permission rank 4" in report


def test_invariant_audit_detects_illegal_external_promotion():
    integrated = _integrated()
    integrated.loc[
        integrated["unit_id"] == "set_b::B", "integrated_cross_dataset_status"
    ] = "external_same_context_concordant"
    integrated.loc[integrated["unit_id"] == "set_b::B", "claim_ceiling"] = (
        "bounded_computational_same_context_replication_allowed"
    )
    objects = build_formal_decision_objects(_units(), _stability(), integrated)
    audit = audit_claim_state_invariants(
        _claims(), _units(), _stability(), integrated, objects
    )

    assert audit.set_index("invariant_id").loc["I09", "status"] == "fail"
    assert "set_b::B" in audit.set_index("invariant_id").loc["I09", "violation_ids"]


def test_formalization_requires_unit_schema():
    with pytest.raises(ValueError, match="responder-state units is missing columns"):
        build_formal_decision_objects(pd.DataFrame({"unit_id": ["x"]}), _stability(), _integrated())
