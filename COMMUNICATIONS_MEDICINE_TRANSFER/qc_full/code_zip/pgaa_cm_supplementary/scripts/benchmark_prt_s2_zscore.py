#!/usr/bin/env python3
"""
PRT-S₂ RANK-BASED / Z-SCORE CALIBRATION on Norman 2019.

Idea: replace absolute S₂ value test with per-gene z-score:
    z_g = (S₂_obs[g] - mean(null_S₂[g,:])) / std(null_S₂[g,:])
    p_g = 2 * (1 - Φ(|z_g|))

This is what S₁ does (z_score in pgaa/core/prt.py:154-160). Should fix
the over-sensitivity of S₂ (1075/2012 sig) by penalizing genes whose
null distribution is wide.

If this works, we expect:
  - n_sig drops from 1075 to ~50-200 (reasonable FDR)
  - ELANE remains significant
  - AUROC improves (or at least ELANE rank improves)
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt_s2 import compute_persistence_1d, persistence_landscape_distance
from pgaa.core.prt import prt_s1_test
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import norm

np.random.seed(42)


def residualize(X, cell_type, library_size):
    N = X.shape[0]
    parts = [np.ones(N)]
    if cell_type is not None:
        ct = pd.Categorical(cell_type)
        parts.append(pd.get_dummies(ct, drop_first=True, dtype=float).values)
    if library_size is not None:
        lib = library_size.astype(np.float64)
        lib_z = (lib - lib.mean()) / (lib.std() + 1e-9)
        parts.append(lib_z[:, None])
    Z = np.column_stack(parts)
    return X - Z @ np.linalg.pinv(Z.T @ Z) @ (Z.T @ X)


def s2_test_fast(Y_on, Y_off, n_bins=50):
    g_min = min(Y_on.min(), Y_off.min())
    g_max = max(Y_on.max(), Y_off.max())
    bins = np.linspace(g_min, g_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    n_genes = Y_on.shape[1]
    s2 = np.zeros(n_genes)
    for g in range(n_genes):
        h_on, _ = np.histogram(Y_on[:, g], bins=bins, density=True)
        h_off, _ = np.histogram(Y_off[:, g], bins=bins, density=True)
        pd_on = compute_persistence_1d(h_on, bin_centers)
        pd_off = compute_persistence_1d(h_off, bin_centers)
        s2[g] = persistence_landscape_distance(pd_on, pd_off, n_top=3)
    return s2


def main():
    adata = sc.read_h5ad(
        "/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad"
    )
    labels = adata.obs["perturbation"].astype(str)
    cebpe_pert = np.where(
        labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True)
    )[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]

    hvg = adata.var["highly_variable"].values.copy() \
        if "highly_variable" in adata.var.columns \
        else np.ones(adata.n_vars, dtype=bool)
    extra = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
             "DEFA1", "RNASE2", "CEBPE", "GAPDH", "ACTB", "B2M"]
    for g in extra:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()
    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)
    lib_size = np.array(adata_hvg.X.sum(axis=1)).ravel()
    svd = TruncatedSVD(n_components=10, random_state=42)
    X_20 = svd.fit_transform(X)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)

    test_idx = np.concatenate([cebpe_pert, ctrl_idx])
    N_sub = len(test_idx)
    tidx = genes.index("CEBPE")
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]
    n_pert = len(cebpe_pert)

    Y_sub = residualize(X[test_idx], cell_type[test_idx], lib_size[test_idx])
    Y = Y_sub[:, other_idx]
    D_obs = np.zeros(N_sub, dtype=bool)
    D_obs[:n_pert] = True
    ct_sub = cell_type[test_idx].astype(int)
    unique_ct = np.unique(ct_sub)

    # Observed
    Y_on = Y[D_obs]
    Y_off = Y[~D_obs]
    s2_obs = s2_test_fast(Y_on, Y_off, n_bins=50)

    # Within-cluster perm
    n_perms = 500
    null_stats = np.zeros((n_perms, len(other_genes)))
    D_int = D_obs.astype(int)
    rng = np.random.default_rng(42)
    t0 = time.time()
    for b in range(n_perms):
        if b % 100 == 0:
            print(f"  perm {b}/{n_perms}, {int(time.time()-t0)}s", flush=True)
        D_perm = D_int.copy()
        for u in unique_ct:
            mask = ct_sub == u
            if mask.sum() < 2:
                continue
            D_perm[mask] = rng.permutation(D_int[mask])
        D_perm = D_perm.astype(bool)
        null_stats[b] = s2_test_fast(Y[D_perm], Y[~D_perm], n_bins=50)
    print(f"  perm done in {time.time()-t0:.1f}s", flush=True)

    # --- Three calibration modes ---
    # Mode 1: per-gene permutation p (current)
    p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)

    # Mode 2: per-gene z-score
    null_mean = null_stats.mean(axis=0)
    null_std = null_stats.std(axis=0)
    z_gene = (s2_obs - null_mean) / (null_std + 1e-15)
    p_zscore = 2 * (1 - norm.cdf(np.abs(z_gene)))

    # Mode 3: pooled rank (rank of S₂_obs within null distribution pooled
    # across all genes)
    null_pooled = null_stats.flatten()
    # For each gene, rank of obs vs null pool
    p_pooled = np.zeros(len(other_genes))
    for g in range(len(other_genes)):
        # rank = (number of null values >= obs) / total null
        p_pooled[g] = (null_pooled >= s2_obs[g]).sum() / len(null_pooled)

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]
    is_known = np.array([g in cebpe_targets for g in other_genes])

    print("\n=== Mode comparison ===")
    print(f"{'Mode':<35} {'ELANE p':>10} {'n_sig':>8} {'AUROC':>8} {'ELANE rank':>12}")
    for name, p in [("1. per-gene perm p", p_perm),
                    ("2. per-gene z-score", p_zscore),
                    ("3. pooled rank", p_pooled)]:
        n_sig = int((p < 0.05).sum())
        elane_p = float(p[other_genes.index("ELANE")])
        elane_rank = (np.argsort(p) == other_genes.index("ELANE")).sum() + 1 \
            if "ELANE" in other_genes else None
        # Compute rank
        order = np.argsort(p)
        elane_rank = int(np.where(order == other_genes.index("ELANE"))[0][0]) + 1
        auroc = roc_auc_score(is_known, -np.log10(p + 1e-300))
        print(f"{name:<35} {elane_p:>10.4f} {n_sig:>8} {auroc:>8.3f} {elane_rank:>12}")

    # Save all three modes
    res = pd.DataFrame({
        "gene": other_genes,
        "S2_obs": s2_obs,
        "null_mean": null_mean,
        "null_std": null_std,
        "z_score": z_gene,
        "p_perm": p_perm,
        "p_zscore": p_zscore,
        "p_pooled": p_pooled,
    })
    res.to_csv("scripts/norman2019_prt_s2_3modes.csv", index=False)
    print(f"\nSaved: scripts/norman2019_prt_s2_3modes.csv")

    # Final recommendation
    print("\n=== Known targets at p<0.05 by mode ===")
    for name, col in [("1. perm", "p_perm"),
                      ("2. zscore", "p_zscore"),
                      ("3. pooled", "p_pooled")]:
        hits = res[res["gene"].isin(cebpe_targets) & (res[col] < 0.05)]["gene"].tolist()
        print(f"  {name}: {len(hits)}/9  ({', '.join(hits)})")


if __name__ == "__main__":
    main()
