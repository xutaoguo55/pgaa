"""Target-coverage checks for candidate external PGAA validation datasets."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_CANDIDATE_AUDIT_COLUMNS = {
    "target_gene",
    "unit_id",
    "validation_priority",
    "candidate_dataset_id",
    "same_context_class",
}


def _matches_target(obs_name: object, target_gene: str) -> bool:
    parts = str(obs_name).split("_")
    return target_gene in parts


def _control_counts(obs: pd.DataFrame) -> tuple[int, int]:
    obs_names = pd.Index(obs.index.astype(str))
    n_non_targeting = int(obs_names.str.contains("non-targeting", case=False, regex=False).sum())
    n_core_control = 0
    if "core_control" in obs.columns:
        n_core_control = int(obs["core_control"].fillna(False).astype(bool).sum())
    return n_non_targeting, n_core_control


def _matrix_level(source_file_name: str) -> str:
    lower = source_file_name.lower()
    if "bulk" in lower:
        return "pseudobulk_h5ad"
    if "singlecell" in lower or "single_cell" in lower:
        return "single_cell_h5ad"
    return "h5ad_unknown_level"


def build_external_target_coverage(
    candidate_audit: pd.DataFrame,
    obs: pd.DataFrame,
    candidate_dataset_id: str,
    source_file_name: str,
    source_url: str,
) -> pd.DataFrame:
    """Build per-target coverage evidence from external h5ad observation metadata."""
    missing = sorted(REQUIRED_CANDIDATE_AUDIT_COLUMNS - set(candidate_audit.columns))
    if missing:
        raise ValueError(f"candidate audit table is missing columns: {missing}")

    subset = candidate_audit[candidate_audit["candidate_dataset_id"] == candidate_dataset_id].copy()
    if subset.empty:
        raise ValueError(f"candidate audit has no rows for dataset: {candidate_dataset_id}")

    n_non_targeting, n_core_control = _control_counts(obs)
    control_status = (
        "verified_controls_present"
        if n_non_targeting > 0 or n_core_control > 0
        else "control_metadata_not_found"
    )
    rows: list[dict[str, object]] = []
    matrix_level = _matrix_level(source_file_name)
    for _, row in subset.drop_duplicates(["target_gene", "unit_id"]).iterrows():
        target = str(row["target_gene"])
        matches = [name for name in obs.index.astype(str) if _matches_target(name, target)]
        coverage_status = "verified_present" if matches else "not_found_in_obs_metadata"
        if coverage_status == "verified_present" and control_status == "verified_controls_present":
            if matrix_level == "single_cell_h5ad":
                import_status = "ready_for_external_singlecell_import"
                next_action = (
                    "Import the single-cell h5ad matrix and rerun PGAA/comparator claim-state gates; "
                    "do not cite as replication until external claim state is recomputed."
                )
            elif matrix_level == "pseudobulk_h5ad":
                import_status = "target_verified_pseudobulk_singlecell_required"
                next_action = (
                    "Use this pseudobulk h5ad as target-coverage proof, then import the matching "
                    "single-cell h5ad before PGAA distributional rerun; label any pseudobulk-only "
                    "analysis separately."
                )
            else:
                import_status = "target_verified_matrix_level_unclear"
                next_action = (
                    "Resolve whether the h5ad is single-cell or pseudobulk before PGAA/comparator rerun."
                )
            claim_use = "target_coverage_verified_not_replication"
        elif coverage_status == "verified_present":
            import_status = "target_present_controls_unresolved"
            claim_use = "target_coverage_partial_not_replication"
            next_action = "Resolve matched-control metadata before PGAA/comparator rerun."
        else:
            import_status = "not_import_ready_for_this_target"
            claim_use = "not_usable_for_target_replication"
            next_action = "Use another external source or verify a different file with target metadata."
        rows.append(
            {
                "target_gene": target,
                "unit_id": row["unit_id"],
                "validation_priority": row["validation_priority"],
                "candidate_dataset_id": candidate_dataset_id,
                "source_file_name": source_file_name,
                "source_url": source_url,
                "matrix_level": matrix_level,
                "n_obs_rows": len(obs),
                "n_matching_obs_rows": len(matches),
                "matching_obs_rows": ";".join(matches[:20]) if matches else "",
                "target_coverage_status": coverage_status,
                "n_non_targeting_control_rows": n_non_targeting,
                "n_core_control_rows": n_core_control,
                "matched_control_status": control_status,
                "external_import_status": import_status,
                "claim_use": claim_use,
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows).sort_values(["validation_priority", "target_gene"]).reset_index(
        drop=True
    )


def summarize_external_target_coverage(coverage: pd.DataFrame) -> pd.DataFrame:
    """Summarize per-target coverage evidence."""
    required = {
        "target_coverage_status",
        "matched_control_status",
        "external_import_status",
        "claim_use",
    }
    missing = sorted(required - set(coverage.columns))
    if missing:
        raise ValueError(f"coverage table is missing columns: {missing}")
    return (
        coverage.groupby(
            [
                "target_coverage_status",
                "matched_control_status",
                "external_import_status",
                "claim_use",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_targets")
        .sort_values(
            ["target_coverage_status", "matched_control_status", "external_import_status"]
        )
        .reset_index(drop=True)
    )


def render_external_target_coverage_report(
    coverage: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a claim-safe target-coverage report."""
    lines = [
        "# PGAA External Target-Coverage Audit",
        "",
        "This report verifies target coverage and control metadata in a candidate external h5ad file. It is not replication evidence: replication requires importing the matrix, rerunning PGAA and comparator gates, and obtaining a matching external claim state.",
        "",
        "## Summary",
        "",
        "| Target coverage | Control metadata | Import status | Allowed use | Targets |",
        "|---|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['target_coverage_status']} | {row['matched_control_status']} | "
            f"{row['external_import_status']} | {row['claim_use']} | {row['n_targets']} |"
        )
    lines.extend(
        [
            "",
            "## Target-Level Evidence",
            "",
            "| Target | Candidate dataset | Source file | Matching obs rows | Controls | Import status |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    for _, row in coverage.iterrows():
        controls = int(row["n_non_targeting_control_rows"]) + int(row["n_core_control_rows"])
        lines.append(
            f"| {row['target_gene']} | {row['candidate_dataset_id']} | "
            f"{Path(str(row['source_file_name'])).name} | {row['n_matching_obs_rows']} | "
            f"{controls} | {row['external_import_status']} |"
        )
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            "Use the verified h5ad metadata as target-coverage evidence. For a PGAA distributional replication, import the matching single-cell matrix and rerun the PGAA/comparator claim-state gates. The manuscript claim ceiling should remain unchanged until the external PGAA/comparator rerun produces audited claim-state rows.",
        ]
    )
    return "\n".join(lines) + "\n"
