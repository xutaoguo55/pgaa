"""Integrate external claim states into responder-state stability classes."""
from __future__ import annotations

import pandas as pd


REQUIRED_INTERNAL_STABILITY_COLUMNS = {
    "unit_id",
    "evidence_type",
    "context",
    "baseline_decision_state",
    "stability_class",
    "cross_dataset_status",
    "n_leave_one_checks",
    "n_state_preserved",
    "n_state_changed",
}

REQUIRED_EXTERNAL_COLUMNS = {
    "target_gene",
    "internal_unit_id",
    "external_claim_state",
    "concordance_state",
    "claim_use",
}


def integrate_external_responder_state_stability(
    internal_stability: pd.DataFrame,
    external_claim_states: pd.DataFrame,
) -> pd.DataFrame:
    """Add external same-context claim-state status to internal stability rows."""
    missing_internal = sorted(REQUIRED_INTERNAL_STABILITY_COLUMNS - set(internal_stability.columns))
    if missing_internal:
        raise ValueError(f"internal stability table is missing columns: {missing_internal}")
    missing_external = sorted(REQUIRED_EXTERNAL_COLUMNS - set(external_claim_states.columns))
    if missing_external:
        raise ValueError(f"external claim-state table is missing columns: {missing_external}")

    external_index = external_claim_states.set_index("internal_unit_id", drop=False)
    rows: list[dict[str, object]] = []
    for _, row in internal_stability.iterrows():
        unit_id = str(row["unit_id"])
        if unit_id in external_index.index:
            ext = external_index.loc[unit_id]
            if isinstance(ext, pd.DataFrame):
                ext = ext.iloc[0]
            external_target = str(ext["target_gene"])
            external_claim_state = str(ext["external_claim_state"])
            external_concordance_state = str(ext["concordance_state"])
            external_claim_use = str(ext["claim_use"])
        else:
            external_target = ""
            external_claim_state = "missing_external_claim_state"
            external_concordance_state = "not_assessable"
            external_claim_use = "no_external_claim_state_available"

        concordance_preconditions_met = (
            str(row["baseline_decision_state"]) == "supported_responder_state"
            and str(row["stability_class"]) == "leave_one_method_stable"
        )
        if (
            external_concordance_state == "external_concordant_with_internal_supported_unit"
            and concordance_preconditions_met
        ):
            integrated_cross_dataset_status = "external_same_context_concordant"
            integrated_stability_class = f"{row['stability_class']}_external_concordant"
            claim_ceiling = "bounded_computational_same_context_replication_allowed"
            next_action = "Route any manuscript replication language through the bounded external claim-state row."
        elif external_concordance_state == "external_concordant_with_internal_supported_unit":
            integrated_cross_dataset_status = "external_same_context_unresolved"
            integrated_stability_class = f"{row['stability_class']}_external_unresolved"
            claim_ceiling = "replication_claim_blocked_by_unresolved_external_state"
            next_action = (
                "Resolve the unsupported or internally unstable decision state before "
                "using external concordance as replication evidence."
            )
        elif external_concordance_state == "external_discordant_with_internal_supported_unit":
            integrated_cross_dataset_status = "external_same_context_discordant"
            integrated_stability_class = f"{row['stability_class']}_external_discordant"
            claim_ceiling = "replication_claim_blocked_by_external_discordance"
            next_action = "Treat this as a failure-preserving benchmark row and investigate context or method differences."
        elif external_concordance_state in {
            "external_unresolved_for_internal_supported_unit",
            "external_support_without_internal_supported_unit",
        }:
            integrated_cross_dataset_status = "external_same_context_unresolved"
            integrated_stability_class = f"{row['stability_class']}_external_unresolved"
            claim_ceiling = "replication_claim_blocked_by_unresolved_external_state"
            next_action = "Resolve external PGAA output ranking and internal-unit alignment before replication language."
        elif external_claim_state in {
            "blocked_by_external_execution_status",
            "blocked_missing_internal_unit",
            "external_claim_state_unresolved",
            "missing_external_claim_state",
        }:
            integrated_cross_dataset_status = "external_same_context_blocked"
            integrated_stability_class = f"{row['stability_class']}_external_blocked"
            claim_ceiling = "internal_only_no_external_replication_claim"
            next_action = "Complete external PGAA execution and claim-state compilation before updating replication claims."
        else:
            integrated_cross_dataset_status = str(row["cross_dataset_status"])
            integrated_stability_class = str(row["stability_class"])
            claim_ceiling = "internal_only_no_external_replication_claim"
            next_action = "Manually review external claim-state category before manuscript use."

        rows.append(
            {
                "unit_id": unit_id,
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "baseline_decision_state": row["baseline_decision_state"],
                "internal_stability_class": row["stability_class"],
                "internal_cross_dataset_status": row["cross_dataset_status"],
                "external_target_gene": external_target,
                "external_claim_state": external_claim_state,
                "external_concordance_state": external_concordance_state,
                "external_claim_use": external_claim_use,
                "integrated_stability_class": integrated_stability_class,
                "integrated_cross_dataset_status": integrated_cross_dataset_status,
                "claim_ceiling": claim_ceiling,
                "n_leave_one_checks": int(row["n_leave_one_checks"]),
                "n_state_preserved": int(row["n_state_preserved"]),
                "n_state_changed": int(row["n_state_changed"]),
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows)


def summarize_external_responder_state_stability(integrated: pd.DataFrame) -> pd.DataFrame:
    """Summarize integrated internal/external stability status."""
    required = {
        "integrated_stability_class",
        "integrated_cross_dataset_status",
        "claim_ceiling",
    }
    missing = sorted(required - set(integrated.columns))
    if missing:
        raise ValueError(f"integrated stability table is missing columns: {missing}")
    return (
        integrated.groupby(
            ["integrated_stability_class", "integrated_cross_dataset_status", "claim_ceiling"],
            dropna=False,
        )
        .size()
        .reset_index(name="n_units")
        .sort_values(["integrated_cross_dataset_status", "integrated_stability_class"])
        .reset_index(drop=True)
    )


def render_external_responder_state_stability_report(
    integrated: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a conservative external responder-state stability report."""
    lines = [
        "# PGAA External Responder-State Stability Integration Report",
        "",
        "This report integrates external claim-state rows with internal responder-state stability. It can upgrade a unit only to bounded computational same-context replication; it cannot support immune presentation, synthetic-peptide validation, or T-cell function.",
        "",
        "## Summary",
        "",
        "| Integrated stability class | Cross-dataset status | Claim ceiling | Units |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['integrated_stability_class']} | "
            f"{row['integrated_cross_dataset_status']} | {row['claim_ceiling']} | "
            f"{row['n_units']} |"
        )

    lines.extend(
        [
            "",
            "## Integrated Units",
            "",
            "| Unit | External target | External claim state | Concordance | Integrated status | Claim ceiling |",
            "|---|---|---|---|---|---|",
        ]
    )
    for _, row in integrated.iterrows():
        lines.append(
            f"| {row['unit_id']} | {row['external_target_gene']} | "
            f"{row['external_claim_state']} | {row['external_concordance_state']} | "
            f"{row['integrated_cross_dataset_status']} | {row['claim_ceiling']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Rows with `external_same_context_blocked` or `external_same_context_unresolved` remain internal-only. Rows with `external_same_context_concordant` still support only computational replication language and must not be described as wet-lab or immune validation.",
        ]
    )
    return "\n".join(lines) + "\n"
