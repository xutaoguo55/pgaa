#!/usr/bin/env python3
"""
CPT (Conditional Permutation Test) benchmark on real Perturb-seq data.

Compares:
  1. SCEPTRE (standard permutation)
  2. CPT (novel: jointly shuffle D and Z_pert)

Tests:
  - CEBPE (positive): expected to find ELANE, CTSG, LYZ, MPO
  - GAPDH (negative): expected to find < 5 sig
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import pickle
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import t as tdist
import statsmodels.stats.multitest as mt

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.cpt import cpt_test

np.random.seed(42)


def sceptre_simple(
    X, genes, target, perturbed_idx, control_idx, n_perms=2000,
    cell_type=None, library_size=None,
):
    """Standard SCEPTRE-style permutation (shuffle D only)."""
    N_total, G = X.shape
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
    other_idx = [i for i in range(G) if i != tidx]
    Y = X_sub[:, other_idx]
    ZtZ_inv = np.linalg.pinv(Z_base.T @ Z_base)
    Y_resid = Y - Z_base @ (ZtZ_inv @ (Z_base.T @ Y))
    Y_std = (Y_resid - Y_resid.mean(axis=0, keepdims=True)) / (Y_resid.std(axis=0, keepdims=True) + 1e-9)

    D = np.zeros(N_sub)
    D[:len(perturbed_idx)] = 1.0
    rank_D = np.argsort(np.argsort(D))
    rank_D_c = rank_D - rank_D.mean()
    obs_stat = (Y_std.T @ rank_D_c) / (np.sum(rank_D_c ** 2) + 1e-15)

    print(f"  SCEPTRE: {n_perms} permutations ...")
    t0 = time.time()
    null_stats = np.zeros((n_perms, len(other_idx)))
    for b in range(n_perms):
        if b % 500 == 0:
            print(f"    {b}/{n_perms}, {time.time()-t0:.1f}s")
        D_perm = np.random.permutation(D)
        rank_D_p = np.argsort(np.argsort(D_perm))
        rank_D_p_c = rank_D_p - rank_D_p.mean()
        null_stats[b] = (Y_std.T @ rank_D_p_c) / (np.sum(rank_D_p_c ** 2) + 1e-15)
    p_perm = (np.abs(null_stats) >= np.abs(obs_stat)[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    return pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "stat_obs": obs_stat,
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

    # Subset to HVGs + targets + known target genes
    hvg = adata.var["highly_variable"].values.copy() if "highly_variable" in adata.var.columns else np.ones(adata.n_vars, dtype=bool)
    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2",
                     "CEBPE", "CEBPA", "CEBPB", "SPI1", "TFRC", "HBB", "HBA1", "HBA2", "AHSP",
                     "GAPDH", "ACTB", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
                     "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]
    for g in cebpe_targets:
        if g in adata.var_names:
            idx = list(adata.var_names).index(g)
            hvg[idx] = True
    adata_hvg = adata[:, hvg].copy()
    print(f"Using {adata_hvg.n_vars} genes (HVGs + targets)")

    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)
    lib_size = np.array(adata_hvg.X.sum(axis=1)).ravel()

    # K-means cell type
    print("K-means for cell type ...")
    svd = TruncatedSVD(n_components=20, random_state=42)
    X_20 = svd.fit_transform(X)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)
    print(f"Cluster sizes: {pd.Series(cell_type).value_counts().to_dict()}")

    # Run SCEPTRE
    print("\n" + "="*60)
    print("SCEPTRE (standard permutation) on CEBPE")
    print("="*60)
    res_sceptre = sceptre_simple(
        X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
        cell_type=cell_type, library_size=lib_size,
    )
    n_sig_sceptre = (res_sceptre["p_value_perm"] < 0.05).sum()
    print(f"SCEPTRE: {n_sig_sceptre} sig at p<0.05")
    print("Top 10:")
    print(res_sceptre.head(10).to_string(index=False))

    # Run CPT
    print("\n" + "="*60)
    print("CPT (novel: joint shuffle D + Z_pert) on CEBPE")
    print("="*60)
    t0 = time.time()
    res_cpt = cpt_test(
        X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
        cell_type=cell_type, random_state=42,
    )
    elapsed = time.time() - t0
    n_sig_cpt = (res_cpt["p_value_perm"] < 0.05).sum()
    print(f"CPT: {n_sig_cpt} sig at p<0.05, in {elapsed:.1f}s")
    print("Top 10:")
    print(res_cpt.head(10).to_string(index=False))

    # CEBPE known targets
    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"]
    sceptre_known = res_sceptre[res_sceptre["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    cpt_known = res_cpt[res_cpt["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print("\nCEBPE known targets (SCEPTRE):")
    print(sceptre_known.to_string(index=False))
    print("\nCEBPE known targets (CPT):")
    print(cpt_known.to_string(index=False))

    # AUROC
    def auroc(res, known):
        y_true = res["gene"].isin(known).astype(int).values
        scores = -np.log10(res["p_value_perm"].fillna(1.0).values + 1e-300)
        return roc_auc_score(y_true, scores) if y_true.sum() > 0 else float("nan")

    auroc_sceptre = auroc(res_sceptre, cebpe_targets)
    auroc_cpt = auroc(res_cpt, cebpe_targets)
    print(f"\nAUROC: SCEPTRE={auroc_sceptre:.3f}, CPT={auroc_cpt:.3f}")

    # Negative control: GAPDH
    print("\n" + "="*60)
    print("Negative control: GAPDH (not perturbed)")
    print("="*60)
    res_gapdh_sceptre = sceptre_simple(
        X, genes, "GAPDH", cebpe_pert, ctrl_idx, n_perms=2000,
        cell_type=cell_type, library_size=lib_size,
    )
    res_gapdh_cpt = cpt_test(
        X, genes, "GAPDH", cebpe_pert, ctrl_idx, n_perms=2000,
        cell_type=cell_type, random_state=42,
    )
    n_sig_g_s = (res_gapdh_sceptre["p_value_perm"] < 0.05).sum()
    n_sig_g_c = (res_gapdh_cpt["p_value_perm"] < 0.05).sum()
    print(f"GAPDH SCEPTRE: {n_sig_g_s} sig, CPT: {n_sig_g_c} sig")

    # Final summary
    print("\n" + "="*60)
    print("FINAL: SCEPTRE vs CPT on real Perturb-seq")
    print("="*60)
    summary = pd.DataFrame({
        "Method": ["SCEPTRE (std perm)", "CPT (novel)"],
        "CEBPE_sig": [n_sig_sceptre, n_sig_cpt],
        "CEBPE_AUROC": [auroc_sceptre, auroc_cpt],
        "CEBPE_known_hit": [
            f"{int((sceptre_known['p_value_perm']<0.05).sum())}/{len(sceptre_known)}",
            f"{int((cpt_known['p_value_perm']<0.05).sum())}/{len(cpt_known)}",
        ],
        "GAPDH_neg_sig": [n_sig_g_s, n_sig_g_c],
    })
    print(summary.to_string(index=False))
    summary.to_csv("scripts/cpt_vs_sceptre.csv", index=False)


if __name__ == "__main__":
    main()
