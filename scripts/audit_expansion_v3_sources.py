#!/usr/bin/env python3
"""Audit v3 H5AD structure and metadata without computing expression outcomes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/expansion_v3_source_manifest.tsv"
SPLIT_TOKENS = ("batch", "replicate", "donor", "sample", "library", "plate", "experiment", "time")
PERTURB_TOKENS = ("perturb", "target", "guide", "gene", "drug", "dose", "cytokine", "condition", "tf")
CONTROL_TOKENS = ("control", "ctrl", "ntc", "non-target", "nontarget", "vehicle", "dmso", "mock", "unperturbed")


def _matrix_block(source: object, n_obs: int, n_vars: int) -> np.ndarray:
    block = source[: min(n_obs, 16), : min(n_vars, 64)]
    if sparse.issparse(block):
        block = block.toarray()
    return np.asarray(block)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument(
        "--source-audit",
        type=Path,
        default=ROOT / "evidence/expansion_v3_source_audit.tsv",
    )
    parser.add_argument(
        "--field-inventory",
        type=Path,
        default=ROOT / "evidence/expansion_v3_obs_field_inventory.tsv",
    )
    args = parser.parse_args(argv)
    manifest = pd.read_csv(args.manifest, sep="\t").sort_values("priority")
    dataset_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    for _, source_row in manifest.iterrows():
        path = Path(str(source_row["resolved_source_path"]))
        base = {
            "priority": int(source_row["priority"]),
            "candidate_id": source_row["candidate_id"],
            "source_path": str(path),
        }
        if source_row["status"] not in {"verified_existing", "downloaded_and_verified"} or not path.is_file():
            dataset_rows.append({**base, "read_status": "missing_or_unverified"})
            continue
        try:
            adata = ad.read_h5ad(path, backed="r")
        except Exception as exc:
            dataset_rows.append({**base, "read_status": "read_error", "detail": f"{type(exc).__name__}: {exc}"})
            continue
        try:
            for column in adata.obs.columns:
                values = adata.obs[column]
                examples = sorted(values.dropna().astype(str).unique())[:16]
                lower = str(column).lower()
                field_rows.append(
                    {
                        **base,
                        "field": column,
                        "dtype": str(values.dtype),
                        "n_unique": int(values.nunique(dropna=True)),
                        "n_missing": int(values.isna().sum()),
                        "split_name_candidate": any(token in lower for token in SPLIT_TOKENS),
                        "perturbation_name_candidate": any(token in lower for token in PERTURB_TOKENS),
                        "control_value_detected": any(
                            token in value.lower() for value in examples for token in CONTROL_TOKENS
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
                    **base,
                    "read_status": "readable_backed",
                    "n_cells": adata.n_obs,
                    "n_features": adata.n_vars,
                    "obs_columns": json.dumps(list(map(str, adata.obs.columns))),
                    "var_columns": json.dumps(list(map(str, adata.var.columns))),
                    "layers": json.dumps(list(map(str, adata.layers.keys()))),
                    "matrix_source_audited": matrix_source,
                    "sample_min": float(finite.min()) if finite.size else np.nan,
                    "sample_max": float(finite.max()) if finite.size else np.nan,
                    "sample_integer_fraction": float(np.isclose(finite, np.rint(finite)).mean()) if finite.size else np.nan,
                }
            )
        finally:
            adata.file.close()
    pd.DataFrame(dataset_rows).to_csv(args.source_audit, sep="\t", index=False)
    pd.DataFrame(field_rows).to_csv(args.field_inventory, sep="\t", index=False)
    readable = sum(row["read_status"] == "readable_backed" for row in dataset_rows)
    print(f"V3 SOURCE AUDIT: {readable}/{len(dataset_rows)} readable")
    return int(readable != len(dataset_rows))


if __name__ == "__main__":
    raise SystemExit(main())
