"""Plan safe import of external single-cell matrices for PGAA reruns."""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


REQUIRED_COVERAGE_COLUMNS = {
    "target_gene",
    "candidate_dataset_id",
    "target_coverage_status",
    "matched_control_status",
    "external_import_status",
}

REQUIRED_FILE_COLUMNS = {
    "candidate_dataset_id",
    "file_role",
    "file_name",
    "download_url",
    "size_bytes",
    "matrix_level",
    "preferred_for_pgaa",
}


def _bool_text(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _download_status(
    size_bytes: int,
    available_bytes: int,
    safety_multiplier: float,
    matrix_level: str,
    preferred: bool,
) -> tuple[str, str]:
    required_bytes = int(size_bytes * safety_multiplier)
    if matrix_level != "single_cell_h5ad":
        return (
            "not_singlecell_matrix",
            "Do not use this file as the primary PGAA distributional replication matrix.",
        )
    if not preferred:
        return (
            "secondary_singlecell_option",
            "Keep as an alternate only; prioritize the preferred raw single-cell matrix.",
        )
    if available_bytes >= required_bytes:
        return (
            "download_allowed_with_scratch_margin",
            "Download to scratch outside the repository, verify the h5ad opens, then run the external PGAA gate.",
        )
    if available_bytes >= size_bytes:
        return (
            "download_not_recommended_margin_too_low",
            "Nominal free space exceeds file size but lacks safety margin; use external storage or cloud scratch.",
        )
    return (
        "download_blocked_insufficient_space",
        "Free space is below the single-cell file size; use external storage or cloud scratch.",
    )


def build_external_singlecell_import_plan(
    coverage: pd.DataFrame,
    file_manifest: pd.DataFrame,
    scratch_dir: str | Path,
    safety_multiplier: float = 1.25,
) -> pd.DataFrame:
    """Build an import plan for external single-cell files."""
    missing_coverage = sorted(REQUIRED_COVERAGE_COLUMNS - set(coverage.columns))
    if missing_coverage:
        raise ValueError(f"coverage table is missing columns: {missing_coverage}")
    missing_files = sorted(REQUIRED_FILE_COLUMNS - set(file_manifest.columns))
    if missing_files:
        raise ValueError(f"file manifest is missing columns: {missing_files}")

    if safety_multiplier < 1:
        raise ValueError("safety_multiplier must be >= 1")

    scratch_path = Path(scratch_dir)
    usage = shutil.disk_usage(scratch_path if scratch_path.exists() else scratch_path.parent)
    available_bytes = int(usage.free)

    coverage_ok = coverage[
        (coverage["target_coverage_status"] == "verified_present")
        & (coverage["matched_control_status"] == "verified_controls_present")
    ]
    target_count_by_dataset = (
        coverage_ok.groupby("candidate_dataset_id", dropna=False)["target_gene"]
        .nunique()
        .to_dict()
    )
    rows: list[dict[str, object]] = []
    for _, file_row in file_manifest.iterrows():
        dataset_id = str(file_row["candidate_dataset_id"])
        size_bytes = int(file_row["size_bytes"])
        matrix_level = str(file_row["matrix_level"])
        preferred = _bool_text(file_row["preferred_for_pgaa"])
        status, next_action = _download_status(
            size_bytes, available_bytes, safety_multiplier, matrix_level, preferred
        )
        rows.append(
            {
                "candidate_dataset_id": dataset_id,
                "file_role": file_row["file_role"],
                "file_name": file_row["file_name"],
                "download_url": file_row["download_url"],
                "matrix_level": matrix_level,
                "preferred_for_pgaa": preferred,
                "size_bytes": size_bytes,
                "size_gib": round(size_bytes / (1024**3), 2),
                "scratch_dir": str(scratch_path),
                "available_bytes": available_bytes,
                "available_gib": round(available_bytes / (1024**3), 2),
                "safety_multiplier": safety_multiplier,
                "required_bytes_with_margin": int(size_bytes * safety_multiplier),
                "required_gib_with_margin": round(size_bytes * safety_multiplier / (1024**3), 2),
                "n_verified_priority_targets": int(target_count_by_dataset.get(dataset_id, 0)),
                "target_control_gate": (
                    "passed"
                    if int(target_count_by_dataset.get(dataset_id, 0)) > 0
                    else "not_passed"
                ),
                "singlecell_import_status": status,
                "claim_use": "import_planning_not_replication",
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["candidate_dataset_id", "preferred_for_pgaa", "file_role"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def summarize_external_singlecell_import_plan(plan: pd.DataFrame) -> pd.DataFrame:
    """Summarize the single-cell import plan."""
    required = {
        "target_control_gate",
        "singlecell_import_status",
        "claim_use",
        "preferred_for_pgaa",
    }
    missing = sorted(required - set(plan.columns))
    if missing:
        raise ValueError(f"import plan is missing columns: {missing}")
    return (
        plan.groupby(
            [
                "target_control_gate",
                "singlecell_import_status",
                "claim_use",
                "preferred_for_pgaa",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_files")
        .sort_values(["target_control_gate", "preferred_for_pgaa", "singlecell_import_status"])
        .reset_index(drop=True)
    )


def render_external_singlecell_import_plan_report(
    plan: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a conservative import-planning report."""
    lines = [
        "# PGAA External Single-Cell Import Plan",
        "",
        "This report plans import of external single-cell matrices after target/control metadata has been verified. It is not replication evidence; replication requires a completed import and a rerun of PGAA/comparator claim-state gates.",
        "",
        "## Summary",
        "",
        "| Target/control gate | Import status | Preferred | Allowed use | Files |",
        "|---|---|---:|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['target_control_gate']} | {row['singlecell_import_status']} | "
            f"{row['preferred_for_pgaa']} | {row['claim_use']} | {row['n_files']} |"
        )
    lines.extend(
        [
            "",
            "## File-Level Plan",
            "",
            "| File | Role | Size GiB | Available GiB | Required GiB | Status | Next action |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for _, row in plan.iterrows():
        lines.append(
            f"| {row['file_name']} | {row['file_role']} | {row['size_gib']} | "
            f"{row['available_gib']} | {row['required_gib_with_margin']} | "
            f"{row['singlecell_import_status']} | {row['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Do not download large h5ad files into the repository. If current scratch space lacks margin, use external storage or cloud scratch, then run the external PGAA/comparator gate from the downloaded single-cell h5ad.",
        ]
    )
    return "\n".join(lines) + "\n"
