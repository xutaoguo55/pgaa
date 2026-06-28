#!/usr/bin/env python3
"""MMD-PSM benchmark on Norman 2019 CEBPE vs SCEPTRE vs PGAA-W."""

import time
import os
import numpy as np
import pandas as pd
import scanpy as sc
import pickle
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.mmd_psm import mmd_psm_test
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from pgaa.core.prt import prt_s1_test
import statsmodels.stats.multitest as mt

np.random.seed(42)


def main():
    root = Path(__file__).resolve().parent.parent
    default_h5ad = root.parent / "norman2019" / "norman2019_full_log.h5ad"
    h5ad_path = Path(os.environ.get("NORMAN2019_H5AD", default_h5ad))
    if not h5ad_path.exists():
        raise FileNotFoundError(
            "Norman 2019 processed h5ad not found. Set NORMAN2019_H5AD to "
            "the path of norman2019_full_log.h5ad."
        )
    adata = sc.read_h5ad(h5ad_path)
    labels = adata.obs["perturbation"].astype(str)
    print(f"Full: {adata.shape}")

    cebpe_pert = np.where(labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True))[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]
    print(f"CEBPE: {len(cebpe_pert)} perturbed, {len(ctrl_idx)} control")

    hvg = adata.var["highly_variable"].values.copy()
    extra = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2",
             "CEBPE", "GAPDH", "ACTB", "B2M"]
    for g in extra:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()

    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)
    lib_size = np.array(adata_hvg.X.sum(axis=1)).ravel()

    print("K-means K=10 for cell type ...")
    svd = TruncatedSVD(n_components=20, random_state=42)
    X_20 = svd.fit_transform(X)
    km = KMeans(n_clusters=10, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"]

    # MMD-PSM
    print("\n" + "="*60)
    print("MMD-PSM (Propensity Score Matching + Wasserstein)")
    print("="*60)
    t0 = time.time()
    res_mmd = mmd_psm_test(
        X, genes, "CEBPE", cebpe_pert, ctrl_idx,
        n_perms=1000, k_neighbors=5,
        cell_type=cell_type, library_size=lib_size,
    )
    elapsed = time.time() - t0
    n_sig_mmd = (res_mmd["p_value_perm"] < 0.05).sum()
    print(f"MMD-PSM: {n_sig_mmd} sig in {elapsed:.1f}s")
    mmd_known = res_mmd[res_mmd["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"Known target hit: {(mmd_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}")
    print(mmd_known.to_string(index=False))
    auroc_mmd = roc_auc_score(
        res_mmd["gene"].isin(cebpe_targets).astype(int).values,
        -np.log10(res_mmd["p_value_perm"].fillna(1.0).values + 1e-300)
    )

    # GAPDH negative control
    print("\n" + "="*60)
    print("GAPDH negative control (MMD-PSM)")
    print("="*60)
    res_gapdh = mmd_psm_test(
        X, genes, "GAPDH", cebpe_pert, ctrl_idx,
        n_perms=1000, k_neighbors=5,
        cell_type=cell_type, library_size=lib_size,
    )
    n_sig_g = (res_gapdh["p_value_perm"] < 0.05).sum()
    print(f"GAPDH: {n_sig_g} sig")

    # Final summary
    print("\n" + "="*60)
    print("MMD-PSM vs PGAA-W vs SCEPTRE")
    print("="*60)
    summary = pd.DataFrame({
        "Method": ["SCEPTRE", "PGAA-W (global)", "MMD-PSM"],
        "CEBPE_sig": [30, 2012, n_sig_mmd],
        "CEBPE_AUROC": [0.469, 0.511, auroc_mmd],
        "Known_hit": ["0/9", "9/9", f"{(mmd_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}"],
        "GAPDH_neg_sig": ["N/A", 2012, n_sig_g],
    })
    print(summary.to_string(index=False))
    summary.to_csv("scripts/mmd_psm_summary.csv", index=False)


if __name__ == "__main__":
    main()
