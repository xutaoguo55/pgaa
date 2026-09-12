"""External same-context validation opportunity audit for PGAA responder-state units."""
from __future__ import annotations

import pandas as pd


REQUIRED_UNIT_COLUMNS = {
    "unit_id",
    "evidence_type",
    "context",
    "decision_state",
    "primary_method",
    "primary_metric",
    "primary_metric_value",
    "n_comparative_support",
    "n_descriptive_only",
    "n_failure_or_guardrail",
}

REQUIRED_STABILITY_COLUMNS = {
    "unit_id",
    "stability_class",
    "cross_dataset_status",
    "n_leave_one_checks",
    "n_state_preserved",
    "n_state_changed",
}

REQUIRED_DATASET_COLUMNS = {
    "dataset_id",
    "display_name",
    "data_type",
    "analysis_role",
    "raw_data_status",
    "limitations",
}


def _target_gene(context: object) -> str:
    text = str(context)
    if "_pDS" in text:
        return text.split("_pDS", 1)[0]
    return text


def _preferred_external_modality(evidence_type: object) -> str:
    evidence = str(evidence_type)
    if evidence == "adamson_decision_benchmark":
        return "independent K562 CRISPRi or comparable UPR perturbation screen"
    if evidence == "norman_decision_benchmark":
        return "independent K562 CRISPRa or comparable transcription-factor perturbation screen"
    return "independent Perturb-seq screen with matched controls"


def _priority(row: pd.Series) -> tuple[str, int, str]:
    stable = str(row["stability_class"]) == "leave_one_method_stable"
    supported = str(row["decision_state"]) == "supported_responder_state"
    pgaa_dependent = str(row["stability_class"]) == "pgaa_support_dependent"
    provisional = str(row["decision_state"]) == "provisional_responder_state"
    if stable and supported:
        return (
            "tier1_replication_candidate",
            1,
            "Supported and leave-one-method stable; best immediate target for external same-context replication.",
        )
    if pgaa_dependent:
        return (
            "tier2_dependency_stress_test",
            2,
            "Supported in baseline but PGAA-dependent; external data should test whether the state survives outside the current benchmark.",
        )
    if provisional:
        return (
            "tier3_provisional_state_test",
            3,
            "Currently provisional and method-sensitive; external data would test whether the state can be promoted or should remain descriptive.",
        )
    return (
        "tier4_low_priority",
        4,
        "Lower-priority context until stronger internal support or clearer external target is available.",
    )


def _local_dataset_context(units: pd.DataFrame) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for _, row in units.iterrows():
        mapping.setdefault(str(row["context"]), set()).add(str(row["evidence_type"]))
    return mapping


def _local_same_context_status(row: pd.Series, context_to_evidence: dict[str, set[str]]) -> str:
    evidence_types = context_to_evidence.get(str(row["context"]), set())
    if len(evidence_types) > 1:
        return "local_same_context_multiple_sources"
    return "local_same_context_absent"


def _dataset_manifest_hint(dataset_manifest: pd.DataFrame, target_gene: str) -> str:
    searchable = (
        dataset_manifest["analysis_role"].astype(str)
        + " "
        + dataset_manifest["display_name"].astype(str)
        + " "
        + dataset_manifest["limitations"].astype(str)
    )
    hits = dataset_manifest[searchable.str.contains(target_gene, case=False, regex=False)]
    if hits.empty:
        return "no current DATASET_MANIFEST row names this target"
    return (
        "current package mentions target in "
        + "; ".join(hits["dataset_id"].astype(str).tolist())
        + "; this is not external same-context evidence"
    )


def build_external_validation_opportunities(
    units: pd.DataFrame,
    stability_summary: pd.DataFrame,
    dataset_manifest: pd.DataFrame,
) -> pd.DataFrame:
    """Build a per-unit worklist for external same-context validation."""
    missing_units = sorted(REQUIRED_UNIT_COLUMNS - set(units.columns))
    if missing_units:
        raise ValueError(f"responder-state table is missing columns: {missing_units}")
    missing_stability = sorted(REQUIRED_STABILITY_COLUMNS - set(stability_summary.columns))
    if missing_stability:
        raise ValueError(f"stability summary is missing columns: {missing_stability}")
    missing_manifest = sorted(REQUIRED_DATASET_COLUMNS - set(dataset_manifest.columns))
    if missing_manifest:
        raise ValueError(f"dataset manifest is missing columns: {missing_manifest}")

    merged = units.merge(
        stability_summary[
            [
                "unit_id",
                "stability_class",
                "cross_dataset_status",
                "n_leave_one_checks",
                "n_state_preserved",
                "n_state_changed",
            ]
        ],
        on="unit_id",
        how="left",
        validate="one_to_one",
    )
    context_to_evidence = _local_dataset_context(units)
    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        priority, priority_rank, rationale = _priority(row)
        target_gene = _target_gene(row["context"])
        local_status = _local_same_context_status(row, context_to_evidence)
        manifest_hint = _dataset_manifest_hint(dataset_manifest, target_gene)
        external_status = (
            "external_same_context_needed"
            if str(row["cross_dataset_status"]) == "no_cross_dataset_same_context"
            else "external_same_context_present_or_discordant"
        )
        rows.append(
            {
                "unit_id": row["unit_id"],
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "target_gene": target_gene,
                "decision_state": row["decision_state"],
                "stability_class": row["stability_class"],
                "cross_dataset_status": row["cross_dataset_status"],
                "local_same_context_status": local_status,
                "external_validation_status": external_status,
                "validation_priority": priority,
                "priority_rank": priority_rank,
                "preferred_external_modality": _preferred_external_modality(row["evidence_type"]),
                "required_external_inputs": (
                    "single-cell expression matrix; perturbation metadata; matched controls; "
                    "same target gene/context; enough cells for PGAA-W/PGAA-H and comparator rerun"
                ),
                "minimal_acceptance_rule": (
                    "Recompute claim-state and responder-state unit on the external dataset; "
                    "promote replication only if the external unit reaches the same decision state "
                    "without unsupported claim language."
                ),
                "current_manifest_hint": manifest_hint,
                "rationale": rationale,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["priority_rank", "evidence_type", "context"]
    ).reset_index(drop=True)


def summarize_external_validation_opportunities(opportunities: pd.DataFrame) -> pd.DataFrame:
    """Summarize external validation opportunities by priority and current status."""
    required = {
        "validation_priority",
        "external_validation_status",
        "local_same_context_status",
        "priority_rank",
    }
    missing = sorted(required - set(opportunities.columns))
    if missing:
        raise ValueError(f"opportunity table is missing columns: {missing}")
    summary = (
        opportunities.groupby(
            [
                "priority_rank",
                "validation_priority",
                "external_validation_status",
                "local_same_context_status",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_units")
        .sort_values(["priority_rank", "external_validation_status"])
    )
    return summary


def render_external_validation_report(
    opportunities: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a manuscript-facing external validation worklist report."""
    n_units = len(opportunities)
    n_needing_external = int(
        (opportunities["external_validation_status"] == "external_same_context_needed").sum()
    )
    tier1 = opportunities[opportunities["validation_priority"] == "tier1_replication_candidate"]
    lines = [
        "# PGAA External Same-Context Validation Opportunity Audit",
        "",
        f"Responder-state units audited: {n_units}",
        f"Units still needing external same-context evidence: {n_needing_external}",
        "",
        "## Priority Summary",
        "",
        "| Priority | External status | Local status | Units |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['validation_priority']} | {row['external_validation_status']} | "
            f"{row['local_same_context_status']} | {row['n_units']} |"
        )
    lines.extend(
        [
            "",
            "## Tier 1 External Replication Candidates",
            "",
            "| Unit | Target | Stability | Required external modality | Manifest hint |",
            "|---|---|---|---|---|",
        ]
    )
    if tier1.empty:
        lines.append("| none | none | none | none | none |")
    else:
        for _, row in tier1.iterrows():
            lines.append(
                f"| `{row['unit_id']}` | {row['target_gene']} | {row['stability_class']} | "
                f"{row['preferred_external_modality']} | {row['current_manifest_hint']} |"
            )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "This audit is a worklist, not replication evidence. A responder-state unit must "
            "remain `no_cross_dataset_same_context` until an external dataset with the same "
            "target/context is added and the claim-state compiler is rerun on that dataset.",
            "",
            "Top-journal priority should start with Tier 1 units because they are already "
            "supported and leave-one-method stable internally. Tier 2 and Tier 3 units are "
            "better used as stress tests or provisional-state adjudication.",
            "",
        ]
    )
    return "\n".join(lines)
