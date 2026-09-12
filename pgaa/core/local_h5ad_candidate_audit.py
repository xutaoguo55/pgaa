"""Read-only identity and target-coverage audit for local external h5ad candidates."""
from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd


CONTROL_TOKENS = ("ctrl", "control", "non-target", "nontarget", "ntc", "safe")
PERTURBATION_COLUMNS = ("gene", "perturbation", "gene_A", "gene_B", "target_gene")


def _hash_strings(values: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(str(value).encode("utf-8", errors="replace"))
        digest.update(b"\0")
    return digest.hexdigest()


def _sample_matrix_hash(adata: ad.AnnData) -> str:
    row_starts = sorted({0, max(0, adata.n_obs // 2 - 4), max(0, adata.n_obs - 8)})
    col_starts = sorted({0, max(0, adata.n_vars // 2 - 32), max(0, adata.n_vars - 64)})
    digest = hashlib.sha256()
    for row_start in row_starts:
        for col_start in col_starts:
            block = np.asarray(
                adata.X[
                    row_start : min(row_start + 8, adata.n_obs),
                    col_start : min(col_start + 64, adata.n_vars),
                ]
            )
            digest.update(str(block.dtype).encode())
            digest.update(str(block.shape).encode())
            digest.update(block.tobytes())
    return digest.hexdigest()


def _logical_fingerprint(adata: ad.AnnData) -> tuple[str, str, str, str]:
    obs_hash = _hash_strings(adata.obs_names)
    var_hash = _hash_strings(adata.var_names)
    metadata_digest = hashlib.sha256()
    for column in PERTURBATION_COLUMNS:
        if column not in adata.obs:
            continue
        metadata_digest.update(column.encode())
        metadata_digest.update(b"\0")
        for value in adata.obs[column]:
            metadata_digest.update(str(value).encode("utf-8", errors="replace"))
            metadata_digest.update(b"\0")
    metadata_hash = metadata_digest.hexdigest()
    matrix_hash = _sample_matrix_hash(adata)
    return obs_hash, var_hash, metadata_hash, matrix_hash


def audit_local_h5ad_candidates(
    candidates: list[tuple[str, Path]], target_genes: set[str]
) -> pd.DataFrame:
    """Audit candidates in backed mode without modifying source files."""
    rows: list[dict[str, object]] = []
    for candidate_id, path in candidates:
        path = Path(path)
        if not path.exists():
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "source_path": str(path),
                    "read_status": "missing",
                    "candidate_role": "unavailable",
                }
            )
            continue
        try:
            adata = ad.read_h5ad(path, backed="r")
            available_columns = [c for c in PERTURBATION_COLUMNS if c in adata.obs]
            labels: set[str] = set()
            for column in available_columns:
                labels.update(adata.obs[column].astype(str).unique())
            target_hits = sorted(target_genes & labels)
            controls = sorted(
                label for label in labels if any(token in label.lower() for token in CONTROL_TOKENS)
            )
            obs_hash, var_hash, metadata_hash, matrix_hash = _logical_fingerprint(adata)
            role = (
                "same_target_replication_candidate"
                if target_hits and controls
                else "cross_target_generality_candidate"
                if controls
                else "insufficient_control_metadata"
            )
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "source_path": str(path),
                    "read_status": "readable_backed",
                    "file_size_bytes": path.stat().st_size,
                    "n_cells": adata.n_obs,
                    "n_features": adata.n_vars,
                    "perturbation_columns": ";".join(available_columns),
                    "n_unique_perturbation_labels": len(labels),
                    "target_hits": ";".join(target_hits),
                    "n_target_hits": len(target_hits),
                    "control_labels_present": bool(controls),
                    "control_label_examples": ";".join(controls[:10]),
                    "obs_names_sha256": obs_hash,
                    "var_names_sha256": var_hash,
                    "perturbation_metadata_sha256": metadata_hash,
                    "sample_matrix_sha256": matrix_hash,
                    "candidate_role": role,
                }
            )
            adata.file.close()
        except Exception as exc:
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "source_path": str(path),
                    "read_status": f"error:{type(exc).__name__}",
                    "candidate_role": "unreadable",
                }
            )
    result = pd.DataFrame(rows)
    fingerprint_columns = [
        "n_cells",
        "n_features",
        "obs_names_sha256",
        "var_names_sha256",
        "perturbation_metadata_sha256",
        "sample_matrix_sha256",
    ]
    readable = result["read_status"] == "readable_backed"
    result["logical_duplicate_group"] = ""
    if readable.any():
        keys = result.loc[readable, fingerprint_columns].astype(str).agg("|".join, axis=1)
        group_ids = {key: f"logical_group_{i + 1:02d}" for i, key in enumerate(sorted(keys.unique()))}
        result.loc[readable, "logical_duplicate_group"] = keys.map(group_ids)
        counts = result.loc[readable, "logical_duplicate_group"].value_counts()
        result["independence_status"] = result["logical_duplicate_group"].map(
            lambda group: (
                "duplicate_representation_not_independent"
                if group and counts.get(group, 0) > 1
                else "distinct_logical_matrix"
            )
        )
    else:
        result["independence_status"] = "not_assessable"
    result["replication_claim_eligible"] = (
        (result["read_status"] == "readable_backed")
        & (result["candidate_role"] == "same_target_replication_candidate")
        & (result["independence_status"] == "distinct_logical_matrix")
    )
    return result


def render_local_h5ad_candidate_report(audit: pd.DataFrame, targets: set[str]) -> str:
    """Render the local candidate identity and claim-eligibility report."""
    readable = audit[audit["read_status"] == "readable_backed"]
    eligible = audit[audit["replication_claim_eligible"].astype(bool)]
    duplicate_groups = readable.groupby("logical_duplicate_group").size()
    n_duplicate_groups = int((duplicate_groups > 1).sum())
    lines = [
        "# Local External h5ad Candidate Audit",
        "",
        "This audit is read-only. No source file was copied, modified, or deleted.",
        "",
        f"Priority targets: {', '.join(sorted(targets))}.",
        "",
        f"Readable candidates: {len(readable)}/{len(audit)}. Logical duplicate groups: {n_duplicate_groups}. Replication-eligible distinct matrices: {len(eligible)}.",
        "",
        "| Candidate | Shape | Target hits | Controls | Logical group | Independence | Allowed role |",
        "|---|---:|---|---|---|---|---|",
    ]
    for _, row in audit.iterrows():
        shape = f"{int(row['n_cells'])} x {int(row['n_features'])}" if row["read_status"] == "readable_backed" else "NA"
        lines.append(
            f"| `{row['candidate_id']}` | {shape} | {row.get('target_hits', '') or 'none'} | "
            f"{row.get('control_labels_present', False)} | `{row.get('logical_duplicate_group', '')}` | "
            f"`{row.get('independence_status', 'not_assessable')}` | `{row['candidate_role']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Different file sizes do not establish dataset independence. Files with matching cell identities, feature identities, perturbation metadata, and sampled matrix values are treated as duplicate representations. A distinct matrix without priority-target overlap may support future cross-target generality analysis, but it cannot be counted as same-target replication for the current responder states.",
            "",
        ]
    )
    return "\n".join(lines)
