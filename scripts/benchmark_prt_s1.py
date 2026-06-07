#!/usr/bin/env python3
"""
PRT-S1 benchmark: 1D Wasserstein distance on real Perturb-seq.

Tests SCEPTRE, SCEPTRE+UMI, and PRT-S1 on Norman 2019 CEBPE.
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import pickle
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt import prt_s1_test
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import t as tdist
import statsmodels.stats.multitest as mt

np.random.seed(42)


def sceptre_test(X, genes, target, perturbed_idx, control_idx, n_perms=2000,
                 cell_type=None, library_size=None):
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)
    parts = [np.ones(N_sub)]
    if cell_type is not None:
        ct = pd.Categorical(cell_type[test_idx])
        ct_dummies = pd.get_dummies(ct, drop_first=True, dtype=float).values
        parts.append(ct_dummies)
    if library_size is not None:
        lib = library_size[test_idx].astype(np.float64)
        lib_z = (lib - lib.mean()) / (lib.std() + 1e-9)
        parts.append(lib_z[:, None])
    Z_base = np.column_stack(parts)
    tidx = genes.index(target)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    Y = X_sub[:, other_idx]
    ZtZ_inv = np.linalg.pinv(Z_base.T @ Z_base)
    Y_resid = Y - Z_base @ (ZtZ_inv @ (Z_base.T @ Y))
    Y_std = (Y_resid - Y_resid.mean(axis=0, keepdims=True)) / (Y_resid.std(axis=0, keepdims=True) + 1e-9)
    D = np.zeros(N_sub)
    D[:len(perturbed_idx)] = 1.0
    rank_D = np.argsort(np.argsort(D))
    rank_D_c = rank_D - rank_D.mean()
    obs_stat = (Y_std.T @ rank_D_c) / (np.sum(rank_D_c ** 2) + 1e-15)
    print(f"  SCEPTRE: {n_perms} perms ...")
    t0 = time.time()
    null_stats = np.zeros((n_perms, len(other_idx)))
    for b in range(n_perms):
        D_perm = np.random.permutation(D)
        rank_D_p = np.argsort(np.argsort(D_perm))
        rank_D_p_c = rank_D_p - rank_D_p.mean()
        null_stats[b] = (Y_std.T @ rank_D_p_c) / (np.sum(rank_D_p_c ** 2) + 1e-15)
    p_perm = (np.abs(null_stats) >= np.abs(obs_stat)[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    return pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "p_value_perm": p_perm,
    })


def main():
    adata = sc.read_h5ad("/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad")
    labels = adata.obs["perturbation"].astype(str)
    print(f"Full: {adata.shape}")

    cebpe_pert = np.where(labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True))[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]
    print(f"CEBPE: {len(cebpe_pert)} perturbed, {len(ctrl_idx)} control")

    # Subset to HVGs + target genes
    hvg = adata.var["highly_variable"].values.copy() if "highly_variable" in adata.var.columns else np.ones(adata.n_vars, dtype=bool)
    extra = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2",
             "CEBPE", "GAPDH", "ACTB", "B2M"]
    for g in extra:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()

    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)
    lib_size = np.array(adata_hvg.X.sum(axis=1)).ravel()

    # K-means for cell type
    print("K-means for cell type ...")
    svd = TruncatedSVD(n_components=10, random_state=42)
    X_20 = svd.fit_transform(X)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)
    print(f"Cluster sizes: {pd.Series(cell_type).value_counts().to_dict()}")

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"]

    # SCEPTRE
    print("\n" + "="*60)
    print("SCEPTRE (baseline)")
    print("="*60)
    res_sceptre = sceptre_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                                cell_type=cell_type, library_size=lib_size)
    n_sig_s = (res_sceptre["p_value_perm"] < 0.05).sum()
    sceptre_known = res_sceptre[res_sceptre["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"SCEPTRE: {n_sig_s} sig, known target hit: {(sceptre_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}")
    auroc_s = roc_auc_score(
        res_sceptre["gene"].isin(cebpe_targets).astype(int).values,
        -np.log10(res_sceptre["p_value_perm"].fillna(1.0).values + 1e-300)
    )

    # PRT-S1
    print("\n" + "="*60)
    print("PRT-S1 (Wasserstein distance)")
    print("="*60)
    t0 = time.time()
    res_s1 = prt_s1_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                         cell_type=cell_type, library_size=lib_size)
    elapsed = time.time() - t0
    n_sig_s1 = (res_s1["p_value_perm"] < 0.05).sum()
    s1_known = res_s1[res_s1["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"PRT-S1: {n_sig_s1} sig in {elapsed:.1f}s")
    print(f"Known targets: {(s1_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}")
    print(s1_known.to_string(index=False))
    auroc_s1 = roc_auc_score(
        res_s1["gene"].isin(cebpe_targets).astype(int).values,
        -np.log10(res_s1["p_value_perm"].fillna(1.0).values + 1e-300)
    )

    # GAPDH negative control
    print("\n" + "="*60)
    print("GAPDH negative control")
    print("="*60)
    res_gapdh = prt_s1_test(X, genes, "GAPDH", cebpe_pert, ctrl_idx, n_perms=2000,
                            cell_type=cell_type, library_size=lib_size)
    n_sig_g = (res_gapdh["p_value_perm"] < 0.05).sum()
    print(f"PRT-S1 GAPDH: {n_sig_g} sig")

    # Final summary
    print("\n" + "="*60)
    print("PRT-S1 vs SCEPTRE on Norman 2019 CEBPE")
    print("="*60)
    summary = pd.DataFrame({
        "Method": ["SCEPTRE", "PRT-S1"],
        "CEBPE_sig": [n_sig_s, n_sig_s1],
        "CEBPE_AUROC": [auroc_s, auroc_s1],
        "Known_hit": [f"{(sceptre_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}",
                      f"{(s1_known['p_value_perm']<0.05).sum()}/{len(cebpe_targets)}"],
        "GAPDH_neg_sig": ["N/A", n_sig_g],
    })
    print(summary.to_string(index=False))
    summary.to_csv("scripts/prt_s1_summary.csv", index=False)


if __name__ == "__main__":
    main()
