"""Extract PGAA CLI inputs from an external single-cell h5ad contract."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import hashlib

import numpy as np
import pandas as pd


REQUIRED_CONTRACT_COLUMNS = {
    "candidate_dataset_id",
    "target_gene",
    "singlecell_h5ad",
    "contract_status",
    "expression_csv",
    "metadata_csv",
}

CONTROL_TOKENS = ("non-targeting", "non_targeting", "control", "core_control")


def _read_h5ad(path: Path):
    try:
        import scanpy as sc  # type: ignore

        return sc.read_h5ad(path, backed="r")
    except ImportError:
        import anndata as ad  # type: ignore

        return ad.read_h5ad(path, backed="r")


def _label_columns(obs: pd.DataFrame, preferred: str | None = None) -> list[str]:
    if preferred:
        if preferred not in obs.columns:
            raise ValueError(f"preferred label column is absent from h5ad obs: {preferred}")
        return [preferred]
    columns = ["obs_names"]
    for column in obs.columns:
        series = obs[column]
        if pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            columns.append(str(column))
        elif pd.api.types.is_bool_dtype(series):
            columns.append(str(column))
    return columns


def _iter_values(obs: pd.DataFrame, columns: Iterable[str]) -> Iterable[tuple[str, pd.Series]]:
    for column in columns:
        if column == "obs_names":
            yield column, pd.Series(obs.index.astype(str), index=obs.index)
        elif column in obs.columns:
            yield column, obs[column].astype(str)


def _contains_any(obs: pd.DataFrame, columns: Iterable[str], tokens: Iterable[str]) -> pd.Series:
    mask = pd.Series(False, index=obs.index)
    for token in tokens:
        token_lower = str(token).lower()
        for _, values in _iter_values(obs, columns):
            mask = mask | values.str.lower().str.contains(token_lower, regex=False, na=False)
    return mask


def _matches_any_exact(
    obs: pd.DataFrame, columns: Iterable[str], tokens: Iterable[str]
) -> pd.Series:
    normalized = {str(token).lower() for token in tokens}
    mask = pd.Series(False, index=obs.index)
    for _, values in _iter_values(obs, columns):
        mask = mask | values.str.lower().isin(normalized)
    return mask


def _deterministic_subsample_mask(
    mask: np.ndarray, obs_names: pd.Index, maximum: int | None, seed: str
) -> np.ndarray:
    if maximum is None or int(mask.sum()) <= maximum:
        return mask
    if maximum < 1:
        raise ValueError("max_control_cells must be positive when provided")
    indices = np.flatnonzero(mask)
    ordered = sorted(
        indices,
        key=lambda idx: hashlib.sha256(
            f"{seed}\0{obs_names[idx]}".encode("utf-8", errors="replace")
        ).hexdigest(),
    )
    selected = np.zeros(len(mask), dtype=bool)
    selected[ordered[:maximum]] = True
    return selected


def _feature_names(adata) -> pd.Index:
    """Return PGAA-facing feature names, preferring gene symbols when available."""
    var_names = pd.Index(adata.var_names.astype(str))
    if "gene_name" not in adata.var.columns:
        return var_names

    symbols = pd.Index(adata.var["gene_name"].astype(str))
    valid = (symbols != "") & (symbols.str.lower() != "nan")
    duplicate_symbols = symbols.isin(symbols[valid][symbols[valid].duplicated(keep=False)])
    names = []
    for var_name, symbol, is_valid, is_duplicate in zip(
        var_names, symbols, valid, duplicate_symbols
    ):
        if not is_valid:
            names.append(str(var_name))
        elif is_duplicate:
            names.append(f"{symbol}|{var_name}")
        else:
            names.append(str(symbol))
    return pd.Index(names)


def _matrix_to_dense_frame(adata, row_mask: np.ndarray, feature_names: pd.Index) -> pd.DataFrame:
    matrix = adata.X[row_mask, :]
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()
    matrix = np.asarray(matrix)
    obs_names = adata.obs_names[row_mask].astype(str)
    return pd.DataFrame(matrix, index=obs_names, columns=feature_names)


def _existing_input_files_are_usable(
    expression_csv: Path,
    metadata_csv: Path,
    group_column: str,
    expected_sampling_signature: str | None = None,
) -> bool:
    if not expression_csv.is_file() or not metadata_csv.is_file():
        return False
    if expression_csv.stat().st_size == 0 or metadata_csv.stat().st_size == 0:
        return False
    try:
        expression_columns = pd.read_csv(expression_csv, nrows=0).columns
        metadata_columns = pd.read_csv(metadata_csv, nrows=0).columns
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return False
    if not (len(expression_columns) > 1 and {"cell_id", group_column}.issubset(metadata_columns)):
        return False
    if expected_sampling_signature is not None:
        if "extraction_sampling_signature" not in metadata_columns:
            return False
        signatures = pd.read_csv(
            metadata_csv, usecols=["extraction_sampling_signature"]
        )["extraction_sampling_signature"].astype(str)
        if signatures.empty or not signatures.eq(expected_sampling_signature).all():
            return False
    return True


def _existing_input_counts(
    expression_csv: Path,
    metadata_csv: Path,
    group_column: str,
    perturbed_value: str,
    control_value: str,
) -> tuple[int, int, int]:
    expression_columns = pd.read_csv(expression_csv, nrows=0).columns
    groups = pd.read_csv(metadata_csv, usecols=[group_column])[group_column].astype(str)
    return (
        int((groups == perturbed_value).sum()),
        int((groups == control_value).sum()),
        max(0, len(expression_columns) - 1),
    )


def extract_external_pgaa_inputs(
    contract: pd.DataFrame,
    label_column: str | None = None,
    group_column: str = "group",
    perturbed_value: str = "perturbed",
    control_value: str = "control",
    write_files: bool = True,
    max_control_cells: int | None = None,
    control_sampling_seed: str = "pgaa-control-v1",
    exact_label_matching: bool = False,
    metadata_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Extract expression/metadata CSVs required by the PGAA CLI.

    The function returns one audit row per target and writes files only for rows
    whose contract is ready and whose target/control metadata are sufficient.
    """
    missing = sorted(REQUIRED_CONTRACT_COLUMNS - set(contract.columns))
    if missing:
        raise ValueError(f"contract table is missing columns: {missing}")
    rows: list[dict[str, object]] = []
    passthrough_columns = sorted(set(metadata_columns or []))
    signature_parts = [
        f"sha256:{control_sampling_seed}",
        f"max={max_control_cells}",
        f"exact={exact_label_matching}",
    ]
    if passthrough_columns:
        signature_parts.append(f"metadata={','.join(passthrough_columns)}")
    sampling_signature = (
        ":".join(signature_parts)
        if max_control_cells is not None or exact_label_matching or passthrough_columns
        else None
    )

    ready_contract = contract[contract["contract_status"] == "ready_for_pgaa_input_extraction"]
    if ready_contract.empty:
        for _, row in contract.iterrows():
            rows.append(
                {
                    "candidate_dataset_id": row["candidate_dataset_id"],
                    "target_gene": row["target_gene"],
                    "singlecell_h5ad": row["singlecell_h5ad"],
                    "contract_status": row["contract_status"],
                    "extraction_status": "blocked_by_contract_status",
                    "n_perturbed_cells": 0,
                    "n_control_cells": 0,
                    "n_genes": 0,
                    "expression_csv": row["expression_csv"],
                    "metadata_csv": row["metadata_csv"],
                    "label_columns_used": "",
                    "claim_use": "input_extraction_not_replication",
                    "next_action": "Resolve the external claim-state contract before extracting PGAA inputs.",
                }
            )
        return pd.DataFrame(rows)

    h5ad_paths = sorted(ready_contract["singlecell_h5ad"].astype(str).unique())
    if len(h5ad_paths) != 1:
        raise ValueError(f"expected one h5ad path in ready contract, found: {h5ad_paths}")
    h5ad_path = Path(h5ad_paths[0])
    if not h5ad_path.exists():
        for _, row in contract.iterrows():
            rows.append(
                {
                    "candidate_dataset_id": row["candidate_dataset_id"],
                    "target_gene": row["target_gene"],
                    "singlecell_h5ad": row["singlecell_h5ad"],
                    "contract_status": row["contract_status"],
                    "extraction_status": "blocked_missing_h5ad",
                    "n_perturbed_cells": 0,
                    "n_control_cells": 0,
                    "n_genes": 0,
                    "expression_csv": row["expression_csv"],
                    "metadata_csv": row["metadata_csv"],
                    "label_columns_used": "",
                    "claim_use": "input_extraction_not_replication",
                    "next_action": "Place the matching single-cell h5ad at the contract path.",
                }
            )
        return pd.DataFrame(rows)

    if all(
        _existing_input_files_are_usable(
            Path(str(row["expression_csv"])),
            Path(str(row["metadata_csv"])),
            group_column,
            sampling_signature,
        )
        for _, row in ready_contract.iterrows()
    ):
        for _, row in contract.iterrows():
            expression_csv = Path(str(row["expression_csv"]))
            metadata_csv = Path(str(row["metadata_csv"]))
            if row["contract_status"] == "ready_for_pgaa_input_extraction":
                n_target, n_control, n_genes = _existing_input_counts(
                    expression_csv,
                    metadata_csv,
                    group_column,
                    perturbed_value,
                    control_value,
                )
                status = "extracted_pgaa_cli_inputs"
                next_action = "Run or audit the PGAA command in the external claim-state contract."
            else:
                n_target = n_control = n_genes = 0
                status = "blocked_by_contract_status"
                next_action = "Resolve the external claim-state contract before extracting PGAA inputs."
            rows.append(
                {
                    "candidate_dataset_id": row["candidate_dataset_id"],
                    "target_gene": row["target_gene"],
                    "singlecell_h5ad": row["singlecell_h5ad"],
                    "contract_status": row["contract_status"],
                    "extraction_status": status,
                    "n_perturbed_cells": n_target,
                    "n_control_cells": n_control,
                    "n_genes": n_genes,
                    "expression_csv": str(expression_csv),
                    "metadata_csv": str(metadata_csv),
                    "label_columns_used": "restored_from_existing_inputs",
                    "claim_use": "input_extraction_not_replication",
                    "next_action": next_action,
                }
            )
        return pd.DataFrame(rows)

    adata = _read_h5ad(h5ad_path)
    try:
        obs = adata.obs.copy()
        missing_metadata_columns = sorted(set(passthrough_columns) - set(obs.columns))
        if missing_metadata_columns:
            raise ValueError(
                "requested metadata columns are absent from h5ad obs: "
                f"{missing_metadata_columns}"
            )
        columns = _label_columns(obs, label_column)
        matcher = _matches_any_exact if exact_label_matching else _contains_any
        available_control_mask = matcher(obs, columns, CONTROL_TOKENS).to_numpy(dtype=bool)
        n_control_available = int(available_control_mask.sum())
        control_mask = _deterministic_subsample_mask(
            available_control_mask,
            adata.obs_names,
            max_control_cells,
            control_sampling_seed,
        )
        feature_names = _feature_names(adata)
        var_names = set(feature_names.astype(str))

        for _, row in contract.iterrows():
            target = str(row["target_gene"])
            expression_csv = Path(str(row["expression_csv"]))
            metadata_csv = Path(str(row["metadata_csv"]))

            if row["contract_status"] != "ready_for_pgaa_input_extraction":
                rows.append(
                    {
                        "candidate_dataset_id": row["candidate_dataset_id"],
                        "target_gene": target,
                        "singlecell_h5ad": row["singlecell_h5ad"],
                        "contract_status": row["contract_status"],
                        "extraction_status": "blocked_by_contract_status",
                        "n_perturbed_cells": 0,
                        "n_control_cells": 0,
                        "n_genes": int(adata.n_vars),
                        "expression_csv": str(expression_csv),
                        "metadata_csv": str(metadata_csv),
                        "label_columns_used": ";".join(columns),
                        "claim_use": "input_extraction_not_replication",
                        "next_action": "Resolve the external claim-state contract before extracting PGAA inputs.",
                    }
                )
                continue

            target_mask = matcher(obs, columns, [target]).to_numpy(dtype=bool)
            n_target = int(target_mask.sum())
            n_control = int(control_mask.sum())
            if target not in var_names:
                status = "blocked_target_gene_missing_from_expression"
                next_action = "Resolve gene identifiers before running PGAA CLI for this target."
            elif n_target == 0:
                status = "blocked_no_target_cells"
                next_action = "Resolve perturbation labels for this target before PGAA input extraction."
            elif n_control == 0:
                status = "blocked_no_control_cells"
                next_action = "Resolve control-cell labels before PGAA input extraction."
            elif _existing_input_files_are_usable(
                expression_csv, metadata_csv, group_column, sampling_signature
            ):
                status = "extracted_pgaa_cli_inputs"
                next_action = "Run or audit the PGAA command in the external claim-state contract."
            else:
                selected = target_mask | control_mask
                expr = _matrix_to_dense_frame(adata, selected, feature_names)
                selected_obs = obs.loc[selected].copy()
                selected_target = target_mask[selected]
                metadata = pd.DataFrame(
                    {
                        "cell_id": expr.index.astype(str),
                        group_column: np.where(selected_target, perturbed_value, control_value),
                        "source_obs_name": expr.index.astype(str),
                        "extraction_sampling_signature": sampling_signature or "legacy_all_controls",
                    }
                )
                for column in columns:
                    if column != "obs_names" and column in selected_obs.columns:
                        metadata[f"source_{column}"] = selected_obs[column].astype(str).to_numpy()
                for column in passthrough_columns:
                    metadata[f"source_{column}"] = selected_obs[column].astype(str).to_numpy()
                if write_files:
                    expression_csv.parent.mkdir(parents=True, exist_ok=True)
                    expr.to_csv(expression_csv)
                    metadata_csv.parent.mkdir(parents=True, exist_ok=True)
                    metadata.to_csv(metadata_csv, index=False)
                status = "extracted_pgaa_cli_inputs"
                next_action = "Run the PGAA command in the external claim-state contract."

            rows.append(
                {
                    "candidate_dataset_id": row["candidate_dataset_id"],
                    "target_gene": target,
                    "singlecell_h5ad": row["singlecell_h5ad"],
                    "contract_status": row["contract_status"],
                    "extraction_status": status,
                    "n_perturbed_cells": n_target,
                    "n_control_cells": n_control,
                    "n_control_cells_available": n_control_available,
                    "n_genes": int(adata.n_vars),
                    "expression_csv": str(expression_csv),
                    "metadata_csv": str(metadata_csv),
                    "label_columns_used": ";".join(columns),
                    "control_sampling": (
                        sampling_signature
                        if max_control_cells is not None
                        else "all_controls"
                    ),
                    "claim_use": "input_extraction_not_replication",
                    "next_action": next_action,
                }
            )
    finally:
        close = getattr(getattr(adata, "file", None), "close", None)
        if callable(close):
            close()
    return pd.DataFrame(rows)


def summarize_external_pgaa_input_extraction(extraction: pd.DataFrame) -> pd.DataFrame:
    """Summarize PGAA input extraction status."""
    required = {"contract_status", "extraction_status", "claim_use"}
    missing = sorted(required - set(extraction.columns))
    if missing:
        raise ValueError(f"extraction table is missing columns: {missing}")
    return (
        extraction.groupby(["contract_status", "extraction_status", "claim_use"], dropna=False)
        .size()
        .reset_index(name="n_targets")
        .sort_values(["contract_status", "extraction_status"])
        .reset_index(drop=True)
    )


def render_external_pgaa_input_extraction_report(
    extraction: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a claim-safe PGAA input extraction report."""
    lines = [
        "# PGAA External Input Extraction Gate",
        "",
        "This report tracks extraction of PGAA CLI inputs from an external single-cell h5ad. It is not replication evidence; replication requires running PGAA/comparator commands and compiling external claim-state evidence.",
        "",
        "## Summary",
        "",
        "| Contract status | Extraction status | Allowed use | Targets |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['contract_status']} | {row['extraction_status']} | "
            f"{row['claim_use']} | {row['n_targets']} |"
        )
    lines.extend(
        [
            "",
            "## Target Inputs",
            "",
            "| Target | Extraction status | Perturbed cells | Control cells | Genes | Expression CSV | Metadata CSV |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for _, row in extraction.iterrows():
        lines.append(
            f"| {row['target_gene']} | {row['extraction_status']} | "
            f"{row['n_perturbed_cells']} | {row['n_control_cells']} | {row['n_genes']} | "
            f"{row['expression_csv']} | {row['metadata_csv']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Extracted CSV files are inputs only. They should not be cited as external validation until the PGAA/comparator commands complete and the external claim-state table is audited.",
        ]
    )
    return "\n".join(lines) + "\n"
