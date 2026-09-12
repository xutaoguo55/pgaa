#!/usr/bin/env python3
"""Audit expansion-v2 H5AD metadata without computing method outcomes."""
from __future__ import annotations

import json
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "evidence/expansion_v2_candidate_queue.tsv"
QUEUE_AMENDMENTS = (ROOT / "evidence/expansion_v2_candidate_queue_amendment_02.tsv",)
USB_ROOT = Path("/Volumes/MOVESPEED/pgaa_cross_platform/v2")
SPLIT_TOKENS = ("batch", "replicate", "donor", "sample", "library", "plate", "experiment")
PERTURB_TOKENS = ("perturb", "target", "guide", "gene", "drug", "dose", "cytokine", "condition")
CONTROL_TOKENS = ("control", "ctrl", "ntc", "non-target", "nontarget", "vehicle", "dmso", "mock")


def _matrix_block(source: object, n_obs: int, n_vars: int) -> np.ndarray:
    block = source[: min(n_obs, 32), : min(n_vars, 128)]
    if sparse.issparse(block):
        block = block.toarray()
    return np.asarray(block)


def main() -> int:
    queue_parts = [pd.read_csv(QUEUE, sep="\t")]
    queue_parts.extend(
        pd.read_csv(path, sep="\t") for path in QUEUE_AMENDMENTS if path.is_file()
    )
    queue = pd.concat(queue_parts, ignore_index=True)
    queue = queue.sort_values("priority")
    dataset_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    for _, candidate in queue.iterrows():
        path = (
            USB_ROOT
            / "sources"
            / str(candidate["candidate_id"])
            / str(candidate["source_file"])
        )
        if not path.is_file():
            dataset_rows.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "source_path": str(path),
                    "read_status": "missing_or_unverified",
                }
            )
            continue
        adata = ad.read_h5ad(path, backed="r")
        try:
            for column in adata.obs.columns:
                values = adata.obs[column]
                examples = sorted(values.dropna().astype(str).unique())[:12]
                lower = column.lower()
                field_rows.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "field": column,
                        "dtype": str(values.dtype),
                        "n_unique": int(values.nunique(dropna=True)),
                        "n_missing": int(values.isna().sum()),
                        "split_name_candidate": any(token in lower for token in SPLIT_TOKENS),
                        "perturbation_name_candidate": any(
                            token in lower for token in PERTURB_TOKENS
                        ),
                        "control_value_detected": any(
                            token in value.lower()
                            for value in examples
                            for token in CONTROL_TOKENS
                        ),
                        "examples": json.dumps(examples, ensure_ascii=True),
                    }
                )
            source = adata.X
            matrix_source = "X"
            for preferred in ("counts", "raw", "logNor"):
                if preferred in adata.layers:
                    source = adata.layers[preferred]
                    matrix_source = f"layers/{preferred}"
                    break
            block = _matrix_block(source, adata.n_obs, adata.n_vars)
            finite = block[np.isfinite(block)]
            dataset_rows.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "source_path": str(path),
                    "read_status": "readable_backed",
                    "n_cells": adata.n_obs,
                    "n_features": adata.n_vars,
                    "obs_columns": json.dumps(list(map(str, adata.obs.columns))),
                    "var_columns": json.dumps(list(map(str, adata.var.columns))),
                    "layers": json.dumps(list(map(str, adata.layers.keys()))),
                    "matrix_source_audited": matrix_source,
                    "sample_min": float(finite.min()) if finite.size else np.nan,
                    "sample_max": float(finite.max()) if finite.size else np.nan,
                    "sample_integer_fraction": (
                        float(np.isclose(finite, np.rint(finite)).mean())
                        if finite.size
                        else np.nan
                    ),
                    "uns_keys": json.dumps(list(map(str, adata.uns.keys()))),
                }
            )
        finally:
            adata.file.close()
    pd.DataFrame(dataset_rows).to_csv(
        ROOT / "evidence/expansion_v2_source_audit.tsv", sep="\t", index=False
    )
    pd.DataFrame(field_rows).to_csv(
        ROOT / "evidence/expansion_v2_obs_field_inventory.tsv", sep="\t", index=False
    )
    print(f"Audited {len(dataset_rows)} frozen candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
