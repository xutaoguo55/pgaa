#!/usr/bin/env python3
"""A/B/C Full Plan: Test PRT-S₃ on Norman 2019 CEBPE.

If S₃ works (CEBPE known targets hit + GAPDH neg passes):
  → write S₃ method section
If S₃ fails → try S₂ (TDA) → S₄ (info geometry) → S₅ (RG)
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import pickle
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt_s3 import s3_test
from sklearn.metrics import roc_auc_score
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
import statsmodels.stats.multitest as mt

np.random.seed(42)


def main():
    # ─── load data ──────────────────────────────────────────
    adata = sc.read_h5ad(
        "/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad"
    )
    labels = adata.obs["perturbation"].astype(str)

    cebpe_pert = np.where(
        labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True)
    )[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][: len(cebpe_pert) * 3]
    print(f"CEBPE: {len(cebpe_pert)} perturbed, {len(ctrl_idx)} control")

    # Subset to manageable gene set
    hvg = (
        adata.var["highly_variable"].values.copy()
        if "highly_variable" in adata.var.columns
        else np.ones(adata.n_vars, dtype=bool)
    )
    extra = [
        "ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
        "DEFA1", "RNASE2", "CEBPE", "GAPDH", "ACTB", "B2M", "CEBPA", "SPI1",
    ]
    for g in extra:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()

    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)

    cebpe_targets = [
        "ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
        "DEFA1", "RNASE2",
    ]

    # ─── S₃ on CEBPE ────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PRT-S₃ on CEBPE")
    print("=" * 60)
    t0 = time.time()
    res_s3 = s3_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx,
                     partner_genes=genes[:200])  # top 200 as partners
    elapsed = time.time() - t0
    n_sig_s3 = res_s3["significant"].sum()
    print(f"S₃: {n_sig_s3} sig at FDR<0.05 in {elapsed:.0f}s")
    print("Top 10:")
    print(res_s3.head(10).to_string(index=False))

    s3_known = res_s3[res_s3["gene"].isin(cebpe_targets)].sort_values("S3", ascending=False)
    print(f"\nKnown target S₃ values:")
    print(s3_known.to_string(index=False))
    n_hit = (s3_known["significant"].sum())

    # AUROC
    y_true = res_s3["gene"].isin(cebpe_targets).astype(int).values
    if y_true.sum() > 0:
        auroc = roc_auc_score(y_true, res_s3["S3"].values)
    else:
        auroc = float("nan")
    print(f"AUROC: {auroc:.3f}")

    # ─── S₃ on GAPDH (negative control) ─────────────────────
    print("\n" + "=" * 60)
    print("GAPDH negative control (S₃)")
    print("=" * 60)
    res_gapdh = s3_test(X, genes, "GAPDH", cebpe_pert, ctrl_idx,
                        partner_genes=genes[:200])
    n_sig_g = res_gapdh["significant"].sum()
    print(f"GAPDH: {n_sig_g} sig at FDR<0.05")

    # ─── quick summary table ─────────────────────────────────
    print("\n" + "=" * 60)
    print("PRT-S₃ vs SCEPTRE vs PRT-S₁ (global)")
    print("=" * 60)
    summary = pd.DataFrame({
        "Method":              ["SCEPTRE", "PRT-S₁ (global)", "MMD-PSM", "PRT-S₃"],
        "CEBPE_sig":           [30, 2012, 0, n_sig_s3],
        "AUROC":               [0.47, 0.51, 0.55, auroc],
        "Known_target_hit":    [
            "0/9", "9/9", "0/9",
            f"{n_hit}/{len(cebpe_targets)}"],
        "GAPDH_negative_sig":  ["N/A", 2012, 0, n_sig_g],
    })
    print(summary.to_string(index=False))
    summary.to_csv("scripts/prt_s3_summary.csv", index=False)


if __name__ == "__main__":
    main()
