#!/usr/bin/env python3
"""
PRT-S₂ benchmark: 1D persistent homology (TDA) on Norman 2019.

Optimized: residualize once, then permute only D.
Compares against PRT-S₁ on CEBPE → ELANE.
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
    """Compute S₂ for all genes given pre-split matrices. Vectorized."""
    g_min = min(Y_on.min(), Y_off.min())
    g_max = max(Y_on.max(), Y_off.max())
    bins = np.linspace(g_min, g_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    n_genes = Y_on.shape[1]
    s2 = np.zeros(n_genes)
    n_peaks_on = np.zeros(n_genes, dtype=int)
    n_peaks_off = np.zeros(n_genes, dtype=int)
    for g in range(n_genes):
        h_on, _ = np.histogram(Y_on[:, g], bins=bins, density=True)
        h_off, _ = np.histogram(Y_off[:, g], bins=bins, density=True)
        pd_on = compute_persistence_1d(h_on, bin_centers)
        pd_off = compute_persistence_1d(h_off, bin_centers)
        s2[g] = persistence_landscape_distance(pd_on, pd_off, n_top=3)
        n_peaks_on[g] = len(pd_on) if pd_on.shape[0] > 1 or (pd_on.shape[0] == 1 and pd_on[0, 2] > 0) else 0
        n_peaks_off[g] = len(pd_off) if pd_off.shape[0] > 1 or (pd_off.shape[0] == 1 and pd_off[0, 2] > 0) else 0
    return s2, n_peaks_on, n_peaks_off


def main():
    adata = sc.read_h5ad(
        "/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad"
    )
    labels = adata.obs["perturbation"].astype(str)
    print(f"Full: {adata.shape}", flush=True)

    cebpe_pert = np.where(
        labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True)
    )[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]
    print(f"CEBPE: {len(cebpe_pert)} perturbed, {len(ctrl_idx)} control", flush=True)

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

    print("K-means ...", flush=True)
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

    # PRE-RESIDUALIZE ONCE
    print("Residualizing once ...", flush=True)
    t0 = time.time()
    Y_sub = residualize(X[test_idx], cell_type[test_idx], lib_size[test_idx])
    Y = Y_sub[:, other_idx]
    print(f"  done in {time.time()-t0:.1f}s, Y shape {Y.shape}", flush=True)

    D_obs = np.zeros(N_sub, dtype=bool)
    D_obs[:n_pert] = True
    Y_on = Y[D_obs]
    Y_off = Y[~D_obs]

    # Observed S₂
    print("Observed S₂ ...", flush=True)
    t0 = time.time()
    s2_obs, np_on, np_off = s2_test_fast(Y_on, Y_off, n_bins=50)
    print(f"  done in {time.time()-t0:.1f}s", flush=True)

    # Permutation null
    n_perms = 500
    print(f"Permutation null ({n_perms} perms) ...", flush=True)
    t0 = time.time()
    null_stats = np.zeros((n_perms, len(other_genes)))
    for b in range(n_perms):
        if b % 50 == 0:
            print(f"  perm {b}/{n_perms}, {int(time.time()-t0)}s", flush=True)
        D_perm = np.random.permutation(D_obs)
        Y_on_p = Y[D_perm]
        Y_off_p = Y[~D_perm]
        s2_p, _, _ = s2_test_fast(Y_on_p, Y_off_p, n_bins=50)
        null_stats[b] = s2_p
    elapsed_perm = time.time() - t0
    print(f"  total perm time: {elapsed_perm:.1f}s", flush=True)

    p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    res_s2 = pd.DataFrame({
        "gene": other_genes,
        "S2": s2_obs,
        "p_value_perm": p_perm,
        "n_peaks_on": np_on,
        "n_peaks_off": np_off,
    })
    res_s2 = res_s2.sort_values("S2", ascending=False)

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]
    elane_row = res_s2[res_s2["gene"] == "ELANE"]
    elane_rank = (res_s2["gene"].tolist().index("ELANE") + 1) \
        if "ELANE" in res_s2["gene"].values else None
    elane_p = float(elane_row["p_value_perm"].iloc[0]) if len(elane_row) else None
    n_sig_s2 = int((p_perm < 0.05).sum())
    s2_known = res_s2[res_s2["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"\nPRT-S₂: {n_sig_s2} sig, ELANE rank {elane_rank}, p={elane_p}", flush=True)
    print(s2_known.to_string(index=False))

    auroc_s2 = roc_auc_score(
        res_s2["gene"].isin(cebpe_targets).astype(int).values,
        -np.log10(res_s2["p_value_perm"].fillna(1.0).values + 1e-300)
    )

    # PRT-S₁ for comparison
    print("\nPRT-S₁ (Wasserstein) ...", flush=True)
    t0 = time.time()
    res_s1 = prt_s1_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                         cell_type=cell_type, library_size=lib_size)
    elapsed_s1 = time.time() - t0
    elane_rank_s1 = (res_s1.sort_values("p_value_perm")["gene"]
                     .tolist().index("ELANE") + 1) if "ELANE" in res_s1["gene"].values else None
    elane_p_s1 = float(res_s1[res_s1["gene"] == "ELANE"]["p_value_perm"].iloc[0])
    auroc_s1 = roc_auc_score(
        res_s1["gene"].isin(cebpe_targets).astype(int).values,
        -np.log10(res_s1["p_value_perm"].fillna(1.0).values + 1e-300)
    )
    print(f"PRT-S₁: {elapsed_s1:.1f}s, ELANE rank {elane_rank_s1}, p={elane_p_s1}, AUROC={auroc_s2:.3f} (s2)", flush=True)
    print(f"        AUROC_s1={auroc_s1:.3f}", flush=True)

    # Combined z
    print("\nCombined z = (z_S1 + z_S2) / sqrt(2) ...", flush=True)
    s1 = res_s1.set_index("gene")["p_value_perm"].fillna(1.0)
    s2 = res_s2.set_index("gene")["p_value_perm"].fillna(1.0)
    common = s1.index.intersection(s2.index)
    z1 = norm.ppf(1 - s1.loc[common].values)
    z2 = norm.ppf(1 - s2.loc[common].values)
    z_comb = (z1 + z2) / np.sqrt(2)
    p_comb = 1 - norm.cdf(z_comb)
    elane_rank_comb = (pd.Series(p_comb, index=common).sort_values()
                       .index.tolist().index("ELANE") + 1) if "ELANE" in common else None
    elane_p_comb = float(pd.Series(p_comb, index=common).loc["ELANE"]) if "ELANE" in common else None
    is_known = np.array([g in cebpe_targets for g in common])
    auroc_comb = roc_auc_score(is_known, -np.log10(p_comb + 1e-300))
    print(f"Combined: ELANE rank {elane_rank_comb}, p={elane_p_comb}, AUROC={auroc_comb:.3f}", flush=True)

    # Summary
    summary = pd.DataFrame({
        "Method": ["PRT-S₁ (Wasserstein)", "PRT-S₂ (TDA)", "Combined z"],
        "Time_s": [round(elapsed_s1, 1), round(elapsed_perm, 1), 0.0],
        "ELANE_rank": [elane_rank_s1, elane_rank, elane_rank_comb],
        "ELANE_p": [elane_p_s1, elane_p, elane_p_comb],
        "AUROC_known_targets": [round(auroc_s1, 4), round(auroc_s2, 4), round(auroc_comb, 4)],
        "n_sig_0.05": [(res_s1["p_value_perm"] < 0.05).sum(), n_sig_s2, int((p_comb < 0.05).sum())],
    })
    print("\n" + "=" * 60)
    print("Summary: Norman 2019 CEBPE")
    print("=" * 60)
    print(summary.to_string(index=False))
    summary.to_csv("scripts/prt_s2_summary.csv", index=False)
    res_s2.to_csv("scripts/norman2019_prt_s2_full.csv", index=False)
    print("\nSaved: scripts/prt_s2_summary.csv, scripts/norman2019_prt_s2_full.csv", flush=True)


if __name__ == "__main__":
    main()
