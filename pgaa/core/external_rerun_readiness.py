"""Preflight gate for external single-cell PGAA reruns."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


REQUIRED_IMPORT_PLAN_COLUMNS = {
    "candidate_dataset_id",
    "file_name",
    "matrix_level",
    "preferred_for_pgaa",
    "singlecell_import_status",
    "target_control_gate",
}

REQUIRED_COVERAGE_COLUMNS = {
    "target_gene",
    "candidate_dataset_id",
    "validation_priority",
    "target_coverage_status",
    "matched_control_status",
}

CONTROL_TOKENS = ("non-targeting", "non_targeting", "control", "core_control")


def _bool_text(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _priority_bucket(value: object) -> str:
    text = str(value).strip().lower().replace(" ", "_")
    if text.startswith("tier1"):
        return "tier1"
    if text.startswith("tier2"):
        return "tier2"
    if text.startswith("tier3"):
        return "tier3"
    return text


def _matrix_level_from_name(path: str | Path) -> str:
    name = Path(path).name.lower()
    if "bulk" in name or "pseudobulk" in name:
        return "pseudobulk_or_bulk_h5ad"
    if "singlecell" in name or "single_cell" in name:
        return "single_cell_h5ad"
    return "h5ad_unknown_level"


def _read_h5ad_backed(path: Path):
    try:
        import scanpy as sc  # type: ignore

        return sc.read_h5ad(path, backed="r")
    except ImportError:
        import anndata as ad  # type: ignore

        return ad.read_h5ad(path, backed="r")


def _candidate_label_columns(obs: pd.DataFrame) -> list[str]:
    columns: list[str] = ["obs_names"]
    for column in obs.columns:
        series = obs[column]
        if pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            columns.append(str(column))
        elif pd.api.types.is_bool_dtype(series):
            columns.append(str(column))
    return columns


def _iter_label_values(obs: pd.DataFrame, columns: Iterable[str]) -> Iterable[tuple[str, pd.Series]]:
    for column in columns:
        if column == "obs_names":
            yield column, pd.Series(obs.index.astype(str), index=obs.index)
        elif column in obs.columns:
            yield column, obs[column].astype(str)


def _count_token_matches(obs: pd.DataFrame, columns: Iterable[str], token: str) -> tuple[int, str]:
    token_lower = token.lower()
    matched_any = pd.Series(False, index=obs.index)
    matched_columns: list[str] = []
    for column, values in _iter_label_values(obs, columns):
        matches = values.str.lower().str.contains(token_lower, regex=False, na=False)
        if bool(matches.any()):
            matched_columns.append(column)
            matched_any = matched_any | matches
    return int(matched_any.sum()), ";".join(matched_columns)


def _count_controls(obs: pd.DataFrame, columns: Iterable[str]) -> tuple[int, str]:
    matched_any = pd.Series(False, index=obs.index)
    matched_columns: list[str] = []
    for token in CONTROL_TOKENS:
        token_lower = token.lower()
        for column, values in _iter_label_values(obs, columns):
            matches = values.str.lower().str.contains(token_lower, regex=False, na=False)
            if bool(matches.any()):
                matched_columns.append(f"{column}:{token}")
                matched_any = matched_any | matches
    return int(matched_any.sum()), ";".join(dict.fromkeys(matched_columns))


def _priority_targets(coverage: pd.DataFrame) -> pd.DataFrame:
    passed = coverage[
        (coverage["target_coverage_status"] == "verified_present")
        & (coverage["matched_control_status"] == "verified_controls_present")
    ].copy()
    priority_order = {"tier1": 0, "tier2": 1, "tier3": 2}
    passed["_priority_bucket"] = passed["validation_priority"].map(_priority_bucket)
    passed["_priority_order"] = passed["_priority_bucket"].map(priority_order).fillna(9)
    return (
        passed.sort_values(["_priority_order", "target_gene"])
        .drop_duplicates(["candidate_dataset_id", "target_gene"])
        .drop(columns=["_priority_bucket", "_priority_order"])
    )


def build_external_rerun_readiness(
    import_plan: pd.DataFrame,
    coverage: pd.DataFrame,
    singlecell_h5ad: str | Path,
    candidate_dataset_id: str = "replogle_2022_k562_gwps",
    require_tier1_only: bool = True,
) -> pd.DataFrame:
    """Build an external rerun preflight table.

    The output is a readiness gate, not replication evidence. It only says whether a
    local external single-cell h5ad is present and has enough metadata to support a
    downstream PGAA/comparator rerun.
    """
    missing_plan = sorted(REQUIRED_IMPORT_PLAN_COLUMNS - set(import_plan.columns))
    if missing_plan:
        raise ValueError(f"import plan is missing columns: {missing_plan}")
    missing_coverage = sorted(REQUIRED_COVERAGE_COLUMNS - set(coverage.columns))
    if missing_coverage:
        raise ValueError(f"coverage table is missing columns: {missing_coverage}")

    dataset_plan = import_plan[import_plan["candidate_dataset_id"] == candidate_dataset_id].copy()
    if dataset_plan.empty:
        raise ValueError(f"import plan has no rows for dataset: {candidate_dataset_id}")
    dataset_coverage = coverage[coverage["candidate_dataset_id"] == candidate_dataset_id].copy()
    if dataset_coverage.empty:
        raise ValueError(f"coverage table has no rows for dataset: {candidate_dataset_id}")

    targets = _priority_targets(dataset_coverage)
    if require_tier1_only:
        tier1 = targets[targets["validation_priority"].map(_priority_bucket) == "tier1"]
        if not tier1.empty:
            targets = tier1
    target_genes = sorted(targets["target_gene"].astype(str).unique())
    path = Path(singlecell_h5ad)

    preferred = dataset_plan[dataset_plan["preferred_for_pgaa"].map(_bool_text)]
    preferred_status = (
        ";".join(sorted(preferred["singlecell_import_status"].astype(str).unique()))
        if not preferred.empty
        else ""
    )
    target_control_gate = (
        "passed"
        if not targets.empty
        and (targets["target_coverage_status"] == "verified_present").all()
        and (targets["matched_control_status"] == "verified_controls_present").all()
        else "not_passed"
    )

    base: dict[str, object] = {
        "candidate_dataset_id": candidate_dataset_id,
        "singlecell_h5ad": str(path),
        "singlecell_file_exists": path.exists(),
        "preferred_import_status": preferred_status,
        "target_control_gate": target_control_gate,
        "required_target_scope": "tier1" if require_tier1_only else "all_verified_priority_targets",
        "required_targets": ";".join(target_genes),
        "n_required_targets": len(target_genes),
        "claim_use": "rerun_readiness_not_replication",
    }

    if not path.exists():
        return pd.DataFrame(
            [
                {
                    **base,
                    "h5ad_read_status": "missing",
                    "matrix_level": _matrix_level_from_name(path),
                    "n_obs": 0,
                    "n_vars": 0,
                    "label_columns_checked": "",
                    "targets_found": "",
                    "targets_missing": ";".join(target_genes),
                    "n_targets_found": 0,
                    "n_control_rows": 0,
                    "control_columns": "",
                    "singlecell_gate_status": "blocked_waiting_for_singlecell_h5ad",
                    "next_action": (
                        "Acquire external storage or cloud scratch, download the matching single-cell "
                        "h5ad, then rerun this preflight gate before PGAA/comparator claim-state rerun."
                    ),
                }
            ]
        )

    try:
        adata = _read_h5ad_backed(path)
    except Exception as exc:  # pragma: no cover - exercised by real corrupt files, not fixtures.
        return pd.DataFrame(
            [
                {
                    **base,
                    "h5ad_read_status": f"read_error:{type(exc).__name__}",
                    "matrix_level": _matrix_level_from_name(path),
                    "n_obs": 0,
                    "n_vars": 0,
                    "label_columns_checked": "",
                    "targets_found": "",
                    "targets_missing": ";".join(target_genes),
                    "n_targets_found": 0,
                    "n_control_rows": 0,
                    "control_columns": "",
                    "singlecell_gate_status": "singlecell_file_unreadable",
                    "next_action": "Resolve h5ad readability before PGAA/comparator external rerun.",
                }
            ]
        )

    try:
        obs = adata.obs.copy()
        n_obs = int(adata.n_obs)
        n_vars = int(adata.n_vars)
    finally:
        close = getattr(getattr(adata, "file", None), "close", None)
        if callable(close):
            close()

    inferred_matrix_level = _matrix_level_from_name(path)
    label_columns = _candidate_label_columns(obs)
    target_counts: dict[str, int] = {}
    target_columns: dict[str, str] = {}
    for target in target_genes:
        count, columns = _count_token_matches(obs, label_columns, target)
        target_counts[target] = count
        target_columns[target] = columns
    found_targets = sorted([target for target, count in target_counts.items() if count > 0])
    missing_targets = sorted([target for target, count in target_counts.items() if count == 0])
    n_controls, control_columns = _count_controls(obs, label_columns)

    if inferred_matrix_level != "single_cell_h5ad":
        status = "not_singlecell_matrix"
        next_action = "Use the matching single-cell h5ad, not a bulk or pseudobulk matrix."
    elif target_control_gate != "passed":
        status = "target_control_prerequisite_not_passed"
        next_action = "Resolve upstream target/control coverage before external PGAA rerun."
    elif missing_targets:
        status = "target_missing_in_singlecell_metadata"
        next_action = "Resolve single-cell perturbation-label metadata or choose a file containing all required targets."
    elif n_controls == 0:
        status = "control_missing_in_singlecell_metadata"
        next_action = "Resolve matched-control metadata before PGAA/comparator external rerun."
    else:
        status = "ready_for_external_claim_state_rerun"
        next_action = (
            "Run PGAA/comparator external claim-state and stability workflows from this h5ad; "
            "only then consider a replication claim."
        )

    return pd.DataFrame(
        [
            {
                **base,
                "h5ad_read_status": "readable",
                "matrix_level": inferred_matrix_level,
                "n_obs": n_obs,
                "n_vars": n_vars,
                "label_columns_checked": ";".join(label_columns),
                "targets_found": ";".join(found_targets),
                "targets_missing": ";".join(missing_targets),
                "n_targets_found": len(found_targets),
                "target_match_counts": ";".join(
                    f"{target}:{target_counts[target]}" for target in target_genes
                ),
                "target_match_columns": ";".join(
                    f"{target}:{target_columns[target]}" for target in target_genes
                ),
                "n_control_rows": n_controls,
                "control_columns": control_columns,
                "singlecell_gate_status": status,
                "next_action": next_action,
            }
        ]
    )


def summarize_external_rerun_readiness(readiness: pd.DataFrame) -> pd.DataFrame:
    """Summarize external rerun readiness statuses."""
    required = {"singlecell_gate_status", "claim_use", "target_control_gate"}
    missing = sorted(required - set(readiness.columns))
    if missing:
        raise ValueError(f"readiness table is missing columns: {missing}")
    return (
        readiness.groupby(
            ["singlecell_gate_status", "claim_use", "target_control_gate"], dropna=False
        )
        .size()
        .reset_index(name="n_rows")
        .sort_values(["singlecell_gate_status", "claim_use"])
        .reset_index(drop=True)
    )


def render_external_rerun_readiness_report(
    readiness: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a claim-safe external rerun readiness report."""
    row = readiness.iloc[0]
    lines = [
        "# PGAA External Rerun Readiness Gate",
        "",
        "This report is a preflight gate for an external single-cell PGAA/comparator rerun. It is not replication evidence; replication requires a completed PGAA/comparator rerun and an audited external claim-state table.",
        "",
        "## Summary",
        "",
        "| Gate status | Target/control gate | Allowed use | Rows |",
        "|---|---|---|---:|",
    ]
    for _, summary_row in summary.iterrows():
        lines.append(
            f"| {summary_row['singlecell_gate_status']} | {summary_row['target_control_gate']} | "
            f"{summary_row['claim_use']} | {summary_row['n_rows']} |"
        )
    lines.extend(
        [
            "",
            "## File Check",
            "",
            "| Dataset | h5ad | Exists | Read status | Matrix level | n_obs | n_vars |",
            "|---|---|---:|---|---|---:|---:|",
            f"| {row['candidate_dataset_id']} | {Path(str(row['singlecell_h5ad'])).name} | "
            f"{row['singlecell_file_exists']} | {row['h5ad_read_status']} | "
            f"{row['matrix_level']} | {row['n_obs']} | {row['n_vars']} |",
            "",
            "## Metadata Check",
            "",
            "| Required targets | Found targets | Missing targets | Control rows | Label columns checked |",
            "|---|---|---|---:|---|",
            f"| {row['required_targets']} | {row['targets_found']} | {row['targets_missing']} | "
            f"{row['n_control_rows']} | {row['label_columns_checked']} |",
            "",
            "## Next Action",
            "",
            str(row["next_action"]),
            "",
            "The manuscript claim ceiling must remain unchanged until this gate reaches `ready_for_external_claim_state_rerun` and the downstream PGAA/comparator rerun produces external claim-state evidence.",
        ]
    )
    return "\n".join(lines) + "\n"
