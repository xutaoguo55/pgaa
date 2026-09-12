"""Executable formalization and invariant audit for the PGAA claim-state compiler."""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from pgaa.core.result_claims import CLAIM_STATE_BY_ACTION


CLAIM_STATES = {
    "comparative_support",
    "descriptive_only",
    "restricted_use",
    "calibration_support",
    "failure_or_guardrail",
    "manual_review_required",
}

DECISION_STATES = {
    "supported_responder_state",
    "comparator_supported_state",
    "provisional_responder_state",
    "descriptive_comparator_state",
    "failed_or_limited_state",
    "manual_review_state",
}

STABILITY_STATES = {
    "leave_one_method_stable",
    "method_sensitive",
    "pgaa_support_dependent",
    "support_method_dependent",
}

EXTERNAL_STATES = {
    "no_cross_dataset_same_context",
    "external_same_context_concordant",
    "external_same_context_blocked",
    "external_same_context_discordant",
    "external_same_context_unresolved",
}

REQUIRED_CLAIM_COLUMNS = {
    "claim_id",
    "evidence_type",
    "context",
    "method",
    "recommended_action",
    "result_claim_state",
    "manuscript_allowed_claim",
}

REQUIRED_UNIT_COLUMNS = {
    "unit_id",
    "evidence_type",
    "context",
    "decision_state",
    "n_comparative_support",
    "n_descriptive_only",
    "n_failure_or_guardrail",
}

REQUIRED_STABILITY_COLUMNS = {
    "unit_id",
    "baseline_decision_state",
    "n_leave_one_checks",
    "n_state_preserved",
    "n_state_changed",
    "n_pgaa_omission_changed",
    "stability_class",
}

REQUIRED_INTEGRATED_COLUMNS = {
    "unit_id",
    "baseline_decision_state",
    "internal_stability_class",
    "integrated_cross_dataset_status",
    "claim_ceiling",
}


def _validate(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def build_claim_state_space() -> pd.DataFrame:
    """Return the finite state vocabulary and its maximum permitted interpretation."""
    rows = [
        ("row_claim", "failure_or_guardrail", "failure", 0, "failure_or_guardrail_only"),
        ("row_claim", "manual_review_required", "unresolved", 0, "manual_review_required"),
        ("row_claim", "restricted_use", "guardrail", 1, "restricted_or_diagnostic_use"),
        ("row_claim", "calibration_support", "guardrail", 1, "calibration_statement_only"),
        ("row_claim", "descriptive_only", "decision", 1, "descriptive_statement"),
        ("row_claim", "comparative_support", "decision", 2, "bounded_comparative_support"),
        ("decision", "failed_or_limited_state", "failure", 0, "no_positive_claim"),
        ("decision", "manual_review_state", "unresolved", 0, "manual_review_required"),
        ("decision", "descriptive_comparator_state", "decision", 1, "descriptive_statement"),
        ("decision", "provisional_responder_state", "decision", 1, "descriptive_statement"),
        ("decision", "comparator_supported_state", "decision", 2, "bounded_comparator_support"),
        ("decision", "supported_responder_state", "decision", 2, "bounded_comparative_support"),
        ("external", "external_same_context_blocked", "replication", 2, "internal_ceiling_only"),
        ("external", "external_same_context_unresolved", "replication", 2, "internal_ceiling_only"),
        ("external", "external_same_context_discordant", "replication", 2, "replication_claim_blocked"),
        ("external", "external_same_context_concordant", "replication", 3, "bounded_computational_same_context_replication"),
        ("validation", "direct_biological_validation", "wet_lab", 4, "outside_current_compiler"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "state_layer",
            "state",
            "state_family",
            "permission_rank",
            "maximum_allowed_interpretation",
        ],
    )


def build_claim_transition_rules() -> pd.DataFrame:
    """Return allowed and forbidden compiler transitions as an inspectable contract."""
    rows = [
        ("T01", "recommended_action", "mapped_action", "row_claim", "mapped_claim_state", True, "action is present in the declared mapping"),
        ("T02", "row_claim", "comparative_support", "decision", "supported_responder_state", True, "at least one PGAA comparative-support witness exists"),
        ("T03", "row_claim", "descriptive_only", "decision", "provisional_responder_state", True, "PGAA descriptive evidence exists and no comparative witness exists"),
        ("T04", "decision", "supported_responder_state", "stability", "leave_one_method_stable", True, "all leave-one-method perturbations preserve the decision state"),
        ("T05", "stability", "leave_one_method_stable", "external", "external_same_context_concordant", True, "the internal unit is supported and the aligned external claim state is concordant"),
        ("T06", "external", "external_same_context_concordant", "permission", "bounded_computational_same_context_replication", True, "supported and leave-one-method stable preconditions both hold"),
        ("T07", "external", "external_same_context_blocked", "permission", "bounded_computational_same_context_replication", False, "missing external evidence cannot increase permission"),
        ("T08", "external", "external_same_context_unresolved", "permission", "bounded_computational_same_context_replication", False, "unresolved evidence cannot increase permission"),
        ("T09", "external", "external_same_context_discordant", "permission", "bounded_computational_same_context_replication", False, "discordant evidence blocks replication language"),
        ("T10", "decision", "provisional_responder_state", "permission", "bounded_computational_same_context_replication", False, "descriptive internal evidence cannot be promoted by external status alone"),
        ("T11", "stability", "method_sensitive", "permission", "bounded_computational_same_context_replication", False, "an unstable decision cannot receive the replication ceiling"),
        ("T12", "permission", "bounded_computational_same_context_replication", "validation", "direct_biological_validation", False, "computational concordance is not wet-lab evidence"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "rule_id",
            "source_layer",
            "source_state",
            "target_layer",
            "target_state",
            "transition_allowed",
            "precondition_or_reason",
        ],
    )


def compile_unit_claim_ceiling(
    decision_state: str,
    stability_class: str,
    external_status: str,
) -> dict[str, object]:
    """Compile one decision unit to its maximum allowed interpretation."""
    internal_ceiling = {
        "supported_responder_state": "bounded_comparative_support",
        "comparator_supported_state": "bounded_comparator_support",
        "provisional_responder_state": "descriptive_statement",
        "descriptive_comparator_state": "descriptive_statement",
        "failed_or_limited_state": "no_positive_claim",
        "manual_review_state": "manual_review_required",
    }.get(decision_state, "manual_review_required")

    replication_allowed = (
        decision_state == "supported_responder_state"
        and stability_class == "leave_one_method_stable"
        and external_status == "external_same_context_concordant"
    )
    if replication_allowed:
        compiled_ceiling = "bounded_computational_same_context_replication"
        permission_rank = 3
        replication_gate = "allowed"
    else:
        compiled_ceiling = internal_ceiling
        permission_rank = {
            "no_positive_claim": 0,
            "manual_review_required": 0,
            "descriptive_statement": 1,
            "bounded_comparator_support": 2,
            "bounded_comparative_support": 2,
        }[internal_ceiling]
        if external_status == "external_same_context_discordant":
            replication_gate = "blocked_by_discordance"
        elif external_status == "external_same_context_unresolved":
            replication_gate = "blocked_by_unresolved_state"
        elif external_status in {
            "external_same_context_blocked",
            "no_cross_dataset_same_context",
        }:
            replication_gate = "blocked_by_missing_external_evidence"
        elif decision_state != "supported_responder_state":
            replication_gate = "blocked_by_internal_decision_state"
        else:
            replication_gate = "blocked_by_internal_instability"

    return {
        "internal_claim_ceiling": internal_ceiling,
        "compiled_claim_ceiling": compiled_ceiling,
        "permission_rank": permission_rank,
        "replication_gate": replication_gate,
        "wet_lab_claim_allowed": False,
    }


def build_formal_decision_objects(
    units: pd.DataFrame,
    stability: pd.DataFrame,
    integrated: pd.DataFrame,
) -> pd.DataFrame:
    """Compile current responder-state units into formal permission objects."""
    _validate(units, REQUIRED_UNIT_COLUMNS, "responder-state units")
    _validate(stability, REQUIRED_STABILITY_COLUMNS, "stability summary")
    _validate(integrated, REQUIRED_INTEGRATED_COLUMNS, "integrated stability")
    joined = units.merge(
        stability[
            [
                "unit_id",
                "stability_class",
                "n_leave_one_checks",
                "n_state_preserved",
                "n_state_changed",
                "n_pgaa_omission_changed",
            ]
        ],
        on="unit_id",
        how="left",
        validate="one_to_one",
    ).merge(
        integrated[
            [
                "unit_id",
                "integrated_cross_dataset_status",
                "claim_ceiling",
            ]
        ],
        on="unit_id",
        how="left",
        validate="one_to_one",
    )

    rows: list[dict[str, object]] = []
    for _, row in joined.iterrows():
        compiled = compile_unit_claim_ceiling(
            str(row["decision_state"]),
            str(row["stability_class"]),
            str(row["integrated_cross_dataset_status"]),
        )
        rows.append(
            {
                "unit_id": row["unit_id"],
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "decision_state": row["decision_state"],
                "n_comparative_support": row["n_comparative_support"],
                "n_descriptive_only": row["n_descriptive_only"],
                "n_failure_or_guardrail": row["n_failure_or_guardrail"],
                "stability_class": row["stability_class"],
                "n_leave_one_checks": row["n_leave_one_checks"],
                "n_state_preserved": row["n_state_preserved"],
                "n_state_changed": row["n_state_changed"],
                "n_pgaa_omission_changed": row["n_pgaa_omission_changed"],
                "external_state": row["integrated_cross_dataset_status"],
                **compiled,
                "source_external_claim_ceiling": row["claim_ceiling"],
            }
        )
    return pd.DataFrame(rows)


def _audit_row(
    invariant_id: str,
    description: str,
    checked_ids: Iterable[object],
    violation_ids: Iterable[object],
) -> dict[str, object]:
    checked = [str(value) for value in checked_ids]
    violations = [str(value) for value in violation_ids]
    return {
        "invariant_id": invariant_id,
        "description": description,
        "n_checked": len(checked),
        "n_violations": len(violations),
        "status": "pass" if not violations else "fail",
        "violation_ids": ";".join(violations),
    }


def audit_claim_state_invariants(
    claims: pd.DataFrame,
    units: pd.DataFrame,
    stability: pd.DataFrame,
    integrated: pd.DataFrame,
    formal_objects: pd.DataFrame,
) -> pd.DataFrame:
    """Audit compiler invariants against the current evidence artifacts."""
    _validate(claims, REQUIRED_CLAIM_COLUMNS, "claim states")
    _validate(units, REQUIRED_UNIT_COLUMNS, "responder-state units")
    _validate(stability, REQUIRED_STABILITY_COLUMNS, "stability summary")
    _validate(integrated, REQUIRED_INTEGRATED_COLUMNS, "integrated stability")
    rows: list[dict[str, object]] = []

    invalid_claims = claims[~claims["result_claim_state"].isin(CLAIM_STATES)]
    rows.append(_audit_row("I01", "Every claim row has a declared claim state.", claims["claim_id"], invalid_claims["claim_id"]))

    mapping_violations: list[str] = []
    for _, row in claims.iterrows():
        mapping = CLAIM_STATE_BY_ACTION.get(str(row["recommended_action"]))
        if mapping is None or str(row["result_claim_state"]) != mapping[0] or str(row["manuscript_allowed_claim"]) != mapping[1]:
            mapping_violations.append(str(row["claim_id"]))
    rows.append(_audit_row("I02", "Action-to-claim compilation is deterministic and mapping-faithful.", claims["claim_id"], mapping_violations))

    failure_rows = claims[claims["result_claim_state"] == "failure_or_guardrail"]
    failure_violations = failure_rows[
        failure_rows["manuscript_allowed_claim"].str.contains(
            r"May support a bounded|strong superiority|replication allowed", case=False, regex=True, na=False
        )
    ]
    rows.append(_audit_row("I03", "Failure rows cannot carry positive or replication permission.", failure_rows["claim_id"], failure_violations["claim_id"]))

    claim_groups = claims.groupby(["evidence_type", "context"], dropna=False)
    unit_violations: list[str] = []
    provisional_violations: list[str] = []
    aggregation_violations: list[str] = []
    for _, unit in units.iterrows():
        key = (unit["evidence_type"], unit["context"])
        group = claim_groups.get_group(key) if key in claim_groups.groups else claims.iloc[0:0]
        pgaa = group["method"].astype(str).str.contains("PGAA", case=False, na=False)
        if unit["decision_state"] == "supported_responder_state" and not (
            pgaa & (group["result_claim_state"] == "comparative_support")
        ).any():
            unit_violations.append(str(unit["unit_id"]))
        if unit["decision_state"] == "provisional_responder_state" and (
            int(unit["n_comparative_support"]) != 0
            or not (pgaa & (group["result_claim_state"] == "descriptive_only")).any()
        ):
            provisional_violations.append(str(unit["unit_id"]))
        expected_counts = (
            int((group["result_claim_state"] == "comparative_support").sum()),
            int((group["result_claim_state"] == "descriptive_only").sum()),
            int((group["result_claim_state"] == "failure_or_guardrail").sum()),
        )
        observed_counts = (
            int(unit["n_comparative_support"]),
            int(unit["n_descriptive_only"]),
            int(unit["n_failure_or_guardrail"]),
        )
        if expected_counts != observed_counts:
            aggregation_violations.append(str(unit["unit_id"]))
    rows.append(_audit_row("I04", "Supported units require a PGAA comparative-support witness.", units["unit_id"], unit_violations))
    rows.append(_audit_row("I05", "Provisional units require PGAA descriptive evidence and no comparative witness.", units["unit_id"], provisional_violations))
    rows.append(_audit_row("I06", "Responder aggregation preserves row-level support, descriptive, and failure counts.", units["unit_id"], aggregation_violations))

    stable = stability[stability["stability_class"] == "leave_one_method_stable"]
    stable_bad = stable[
        (stable["n_state_changed"] != 0)
        | (stable["n_state_preserved"] != stable["n_leave_one_checks"])
    ]
    rows.append(_audit_row("I07", "Stable units preserve state under every leave-one-method perturbation.", stable["unit_id"], stable_bad["unit_id"]))

    dependent = stability[stability["stability_class"] == "pgaa_support_dependent"]
    dependent_bad = dependent[
        (dependent["n_state_changed"] < 1) | (dependent["n_pgaa_omission_changed"] < 1)
    ]
    rows.append(_audit_row("I08", "PGAA-dependent units contain an observed PGAA-omission state change.", dependent["unit_id"], dependent_bad["unit_id"]))

    concordant = integrated[
        integrated["integrated_cross_dataset_status"] == "external_same_context_concordant"
    ]
    concordant_bad = concordant[
        (concordant["baseline_decision_state"] != "supported_responder_state")
        | (concordant["internal_stability_class"] != "leave_one_method_stable")
    ]
    rows.append(_audit_row("I09", "External concordance requires a supported and internally stable unit.", concordant["unit_id"], concordant_bad["unit_id"]))

    expected_source_ceiling = {
        "external_same_context_concordant": "bounded_computational_same_context_replication_allowed",
        "external_same_context_blocked": "internal_only_no_external_replication_claim",
        "external_same_context_discordant": "replication_claim_blocked_by_external_discordance",
        "external_same_context_unresolved": "replication_claim_blocked_by_unresolved_external_state",
    }
    external_bad = integrated[
        integrated.apply(
            lambda row: expected_source_ceiling.get(str(row["integrated_cross_dataset_status"]))
            != str(row["claim_ceiling"]),
            axis=1,
        )
    ]
    rows.append(_audit_row("I10", "Typed external states map to their declared replication ceilings.", integrated["unit_id"], external_bad["unit_id"]))

    formal_bad = formal_objects[
        (formal_objects["permission_rank"] > 3)
        | formal_objects["wet_lab_claim_allowed"].astype(bool)
    ]
    rows.append(_audit_row("I11", "The computational compiler cannot emit biological-validation permission.", formal_objects["unit_id"], formal_bad["unit_id"]))

    counterfactuals = [
        ("blocked", "supported_responder_state", "leave_one_method_stable", "external_same_context_blocked"),
        ("unresolved", "supported_responder_state", "leave_one_method_stable", "external_same_context_unresolved"),
        ("discordant", "supported_responder_state", "leave_one_method_stable", "external_same_context_discordant"),
        ("provisional", "provisional_responder_state", "leave_one_method_stable", "external_same_context_concordant"),
        ("unstable", "supported_responder_state", "method_sensitive", "external_same_context_concordant"),
    ]
    counterfactual_bad = [
        case_id
        for case_id, decision, stable_state, external in counterfactuals
        if compile_unit_claim_ceiling(decision, stable_state, external)["permission_rank"] >= 3
    ]
    rows.append(_audit_row("I12", "Blocked, unresolved, discordant, provisional, or unstable counterfactuals cannot gain replication permission.", [row[0] for row in counterfactuals], counterfactual_bad))
    return pd.DataFrame(rows)


def render_claim_state_formalization_report(
    state_space: pd.DataFrame,
    transitions: pd.DataFrame,
    formal_objects: pd.DataFrame,
    invariant_audit: pd.DataFrame,
) -> str:
    """Render the executable compiler specification and current audit result."""
    verdict = "PASS" if (invariant_audit["status"] == "pass").all() else "FAIL"
    lines = [
        "# PGAA Claim-State Compiler Formalization",
        "",
        f"Invariant verdict: `{verdict}` ({int((invariant_audit['status'] == 'pass').sum())}/{len(invariant_audit)} passed).",
        "",
        "## Formal Object",
        "",
        "The compiler is a finite permission system over four linked layers: row-level claim state, context-level responder decision, leave-one-method stability, and typed external evidence. Its output is not a truth label. It is the maximum interpretation licensed by the currently compiled evidence.",
        "",
        "For a unit u, let D(u) be its responder decision, S(u) its omission stability, and X(u) its external state. The computational replication permission is emitted if and only if D(u) is supported, S(u) is leave-one-method stable, and X(u) is external same-context concordant. Every other combination retains or lowers the internal claim ceiling. No state emitted by this compiler licenses biological validation.",
        "",
        "## State Space",
        "",
        "| Layer | State | Family | Permission rank | Maximum interpretation |",
        "|---|---|---|---:|---|",
    ]
    for _, row in state_space.iterrows():
        lines.append(f"| {row['state_layer']} | `{row['state']}` | {row['state_family']} | {row['permission_rank']} | `{row['maximum_allowed_interpretation']}` |")
    lines.extend(["", "## Transition Contract", "", "| Rule | Source | Target | Allowed | Condition or reason |", "|---|---|---|---|---|"])
    for _, row in transitions.iterrows():
        lines.append(f"| {row['rule_id']} | `{row['source_layer']}:{row['source_state']}` | `{row['target_layer']}:{row['target_state']}` | {str(bool(row['transition_allowed'])).lower()} | {row['precondition_or_reason']} |")
    lines.extend(["", "## Current Decision Objects", "", "| Unit | Decision | Stability | External state | Compiled ceiling | Rank |", "|---|---|---|---|---|---:|"])
    for _, row in formal_objects.iterrows():
        lines.append(f"| {row['unit_id']} | `{row['decision_state']}` | `{row['stability_class']}` | `{row['external_state']}` | `{row['compiled_claim_ceiling']}` | {row['permission_rank']} |")
    lines.extend(["", "## Invariant Audit", "", "| Invariant | Status | Checked | Violations | Definition |", "|---|---|---:|---:|---|"])
    for _, row in invariant_audit.iterrows():
        lines.append(f"| {row['invariant_id']} | {row['status']} | {row['n_checked']} | {row['n_violations']} | {row['description']} |")
    lines.extend([
        "",
        "## Falsifiability",
        "",
        "The method fails its formal contract if any source action compiles nondeterministically, a supported unit lacks a PGAA comparative witness, aggregation drops failure rows, a stable label hides an omission-induced state change, or a non-concordant or unstable unit receives computational replication permission. These failures are emitted as audit rows rather than being repaired in manuscript prose.",
        "",
        "## Claim Boundary",
        "",
        "Permission rank 3 is bounded computational same-context replication. Permission rank 4 is direct biological validation and lies outside the current compiler. The present evidence therefore cannot establish immune presentation, synthetic-peptide validation, or T-cell function.",
        "",
    ])
    return "\n".join(lines)
