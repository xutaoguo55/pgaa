"""Candidate public-dataset triage for external PGAA validation."""
from __future__ import annotations

import pandas as pd


REQUIRED_OPPORTUNITY_COLUMNS = {
    "unit_id",
    "target_gene",
    "evidence_type",
    "validation_priority",
    "preferred_external_modality",
}

REQUIRED_CANDIDATE_COLUMNS = {
    "candidate_dataset_id",
    "source_name",
    "accession_or_url",
    "cell_context",
    "perturbation_modality",
    "candidate_scope",
    "data_access_status",
    "target_coverage_status",
    "raw_single_cell_status",
    "source_note",
}


def _same_context_class(row: pd.Series) -> str:
    cell = str(row["cell_context"]).lower()
    modality = str(row["perturbation_modality"]).lower()
    scope = str(row["candidate_scope"]).lower()
    target_status = str(row["target_coverage_status"]).lower()
    raw_status = str(row["raw_single_cell_status"]).lower()

    if "processed_signature" in scope or raw_status in {"not_raw_single_cell", "summary_only"}:
        return "processed_signature_or_index_only"
    if "k562" in cell and "crispri" in modality and "genome" in scope:
        if target_status == "verified_present":
            return "same_context_candidate_target_verified"
        return "same_context_candidate_metadata_required"
    if "k562" in cell and "crispri" in modality:
        return "near_context_limited_panel"
    if "k562" in cell:
        return "near_cell_context_wrong_or_unclear_modality"
    return "not_same_context"


def _rerun_feasibility(row: pd.Series, same_context_class: str) -> str:
    access = str(row["data_access_status"]).lower()
    raw = str(row["raw_single_cell_status"]).lower()
    if same_context_class == "processed_signature_or_index_only":
        return "not_pgaa_rerunnable"
    if "download" in access and raw in {"raw_or_processed_single_cell_available", "h5ad_or_matrix_available"}:
        if same_context_class.endswith("metadata_required"):
            return "rerun_feasible_after_target_metadata_check"
        if same_context_class.endswith("target_verified"):
            return "rerun_feasible_after_import"
        return "rerun_feasible_but_context_mismatch_risk"
    if "metadata" in access or "check" in access:
        return "metadata_access_check_required"
    return "not_yet_rerunnable"


def _claim_use(same_context_class: str, feasibility: str) -> str:
    if same_context_class == "same_context_candidate_target_verified" and feasibility.startswith(
        "rerun_feasible"
    ):
        return "candidate_for_external_rerun_not_yet_replication"
    if same_context_class == "same_context_candidate_metadata_required":
        return "candidate_for_metadata_verification_not_replication"
    if same_context_class == "processed_signature_or_index_only":
        return "source_discovery_only_not_replication"
    return "background_candidate_only_not_replication"


def _required_next_check(row: pd.Series, same_context_class: str, feasibility: str) -> str:
    if same_context_class == "same_context_candidate_metadata_required":
        return "download or inspect perturbation metadata; confirm each Tier 1 target and matched controls"
    if same_context_class == "same_context_candidate_target_verified":
        return "import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates"
    if feasibility == "not_pgaa_rerunnable":
        return "use only as a pointer to primary data; do not use processed signatures as PGAA replication evidence"
    return "verify target coverage, control metadata, and single-cell matrix accessibility before use"


def audit_external_dataset_candidates(
    opportunities: pd.DataFrame, candidates: pd.DataFrame
) -> pd.DataFrame:
    """Cross candidate public datasets with priority external-validation units."""
    missing_opportunities = sorted(REQUIRED_OPPORTUNITY_COLUMNS - set(opportunities.columns))
    if missing_opportunities:
        raise ValueError(f"opportunity table is missing columns: {missing_opportunities}")
    missing_candidates = sorted(REQUIRED_CANDIDATE_COLUMNS - set(candidates.columns))
    if missing_candidates:
        raise ValueError(f"candidate manifest is missing columns: {missing_candidates}")

    priority = opportunities[
        opportunities["validation_priority"].isin(
            ["tier1_replication_candidate", "tier2_dependency_stress_test"]
        )
    ].copy()
    rows: list[dict[str, object]] = []
    for _, unit in priority.iterrows():
        for _, candidate in candidates.iterrows():
            same_context = _same_context_class(candidate)
            feasibility = _rerun_feasibility(candidate, same_context)
            rows.append(
                {
                    "target_gene": unit["target_gene"],
                    "unit_id": unit["unit_id"],
                    "validation_priority": unit["validation_priority"],
                    "candidate_dataset_id": candidate["candidate_dataset_id"],
                    "source_name": candidate["source_name"],
                    "accession_or_url": candidate["accession_or_url"],
                    "cell_context": candidate["cell_context"],
                    "perturbation_modality": candidate["perturbation_modality"],
                    "candidate_scope": candidate["candidate_scope"],
                    "target_coverage_status": candidate["target_coverage_status"],
                    "data_access_status": candidate["data_access_status"],
                    "same_context_class": same_context,
                    "pgaa_rerun_feasibility": feasibility,
                    "claim_use": _claim_use(same_context, feasibility),
                    "required_next_check": _required_next_check(
                        candidate, same_context, feasibility
                    ),
                    "source_note": candidate["source_note"],
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["validation_priority", "target_gene", "same_context_class", "candidate_dataset_id"]
    ).reset_index(drop=True)


def summarize_external_dataset_candidates(audit: pd.DataFrame) -> pd.DataFrame:
    """Summarize candidate public datasets by claim-safe use class."""
    required = {"same_context_class", "pgaa_rerun_feasibility", "claim_use"}
    missing = sorted(required - set(audit.columns))
    if missing:
        raise ValueError(f"candidate audit table is missing columns: {missing}")
    return (
        audit.groupby(["same_context_class", "pgaa_rerun_feasibility", "claim_use"], dropna=False)
        .size()
        .reset_index(name="n_target_candidate_pairs")
        .sort_values(["same_context_class", "pgaa_rerun_feasibility", "claim_use"])
        .reset_index(drop=True)
    )


def render_external_dataset_candidate_report(
    audit: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a conservative report for public external-dataset candidates."""
    targets = sorted(audit["target_gene"].astype(str).unique())
    candidates = sorted(audit["candidate_dataset_id"].astype(str).unique())
    metadata_required = audit[
        audit["same_context_class"] == "same_context_candidate_metadata_required"
    ]
    target_verified = audit[
        audit["same_context_class"] == "same_context_candidate_target_verified"
    ]
    lines = [
        "# PGAA External Dataset Candidate Audit",
        "",
        "This is candidate-data triage, not replication evidence. No row in this report should be cited as external validation until target coverage, controls, and rerunnable single-cell matrices are verified and the PGAA/comparator gates are rerun.",
        "",
        f"Priority targets screened: {len(targets)} ({', '.join(targets)})",
        f"Candidate public sources screened: {len(candidates)}",
        "",
        "## Claim-Safe Summary",
        "",
        "| Same-context class | PGAA rerun feasibility | Allowed use | Target-candidate pairs |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['same_context_class']} | {row['pgaa_rerun_feasibility']} | "
            f"{row['claim_use']} | {row['n_target_candidate_pairs']} |"
        )
    lines.extend(
        [
            "",
            "## Highest-Priority Metadata Checks",
            "",
            "| Target | Candidate source | Candidate class | Required next check |",
            "|---|---|---|---|",
        ]
    )
    if metadata_required.empty:
        lines.append("| none | none | none | none |")
    else:
        for _, row in metadata_required.iterrows():
            lines.append(
                f"| {row['target_gene']} | {row['source_name']} | {row['same_context_class']} | "
                f"{row['required_next_check']} |"
            )
    lines.extend(
        [
            "",
            "## Target-Verified Import Candidates",
            "",
            "| Target | Candidate source | Candidate class | Required next check |",
            "|---|---|---|---|",
        ]
    )
    if target_verified.empty:
        lines.append("| none | none | none | none |")
    else:
        for _, row in target_verified.iterrows():
            lines.append(
                f"| {row['target_gene']} | {row['source_name']} | {row['same_context_class']} | "
                f"{row['required_next_check']} |"
            )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "The correct next action is metadata verification and import planning, not manuscript promotion. A candidate becomes replication evidence only after the target perturbation is present, matched controls are usable, the single-cell matrix can be rerun, and the external claim-state matches the internal unit under the predeclared gates.",
        ]
    )
    return "\n".join(lines) + "\n"
