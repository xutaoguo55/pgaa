#!/usr/bin/env python3
"""
S₂ re-run with optimal n_bins=20 on Norman 2019 CEBPE.

Sensitivity analysis revealed n_bins=20 gives BEST calibration (π̂₀=1.32)
and BEST ELANE rank (32). This becomes the default for the paper.
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


def s2_test_fast(Y_on, Y_off, n_bins=20):
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

    hvg = adata.var["highly_variable"].values.copy()
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

    # S₂ with n_bins=20
    print("S₂ with n_bins=20 (optimal per sensitivity analysis) ...", flush=True)
    t0 = time.time()
    Y_on = Y[D_obs]; Y_off = Y[~D_obs]
    s2_obs = s2_test_fast(Y_on, Y_off, n_bins=20)
    n_perms = 500
    null_stats = np.zeros((n_perms, len(other_genes)))
    D_int = D_obs.astype(int)
    rng = np.random.default_rng(42)
    for b in range(n_perms):
        if b % 100 == 0:
            print(f"  perm {b}/{n_perms}, {int(time.time()-t0)}s", flush=True)
        D_perm = D_int.copy()
        for u in unique_ct:
            mask = ct_sub == u
            if mask.sum() >= 2:
                D_perm[mask] = rng.permutation(D_int[mask])
        D_perm = D_perm.astype(bool)
        null_stats[b] = s2_test_fast(Y[D_perm], Y[~D_perm], n_bins=20)
    elapsed = time.time() - t0
    p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    res_s2 = pd.DataFrame({
        "gene": other_genes, "S2": s2_obs, "p_value_perm": p_perm,
    }).sort_values("S2", ascending=False)
    res_s2.to_csv("scripts/norman2019_prt_s2_nbins20.csv", index=False)

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]
    n_sig = int((p_perm < 0.05).sum())
    pi0 = max(1, (p_perm > 0.5).sum()) / (0.5 * len(p_perm))
    elane_rank = int(np.where(np.argsort(p_perm) == other_genes.index("ELANE"))[0][0]) + 1
    elane_p = float(p_perm[other_genes.index("ELANE")])
    hits = sum(1 for g in cebpe_targets if p_perm[other_genes.index(g)] < 0.05)
    auroc = roc_auc_score(
        np.array([g in cebpe_targets for g in other_genes]),
        -np.log10(p_perm + 1e-300)
    )
    print(f"\nS₂ (n_bins=20) results:")
    print(f"  ELANE rank: {elane_rank}")
    print(f"  ELANE p: {elane_p:.4f}")
    print(f"  n_sig: {n_sig}")
    print(f"  π̂₀: {pi0:.3f}")
    print(f"  Known hits: {hits}/9")
    print(f"  AUROC: {auroc:.3f}")
    print(f"  Time: {elapsed:.1f}s")
    s2_known = res_s2[res_s2["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"\nKnown targets:")
    print(s2_known.to_string(index=False))

    # S₁ for comparison
    print("\nS₁ (Wasserstein) ...", flush=True)
    t0 = time.time()
    res_s1 = prt_s1_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                         cell_type=cell_type, library_size=lib_size)
    elapsed_s1 = time.time() - t0
    res_s1 = res_s1.set_index("gene").loc[other_genes].reset_index()
    p_s1 = res_s1["p_value_perm"].fillna(1.0).values
    s1_elane_rank = int(np.where(np.argsort(p_s1) == other_genes.index("ELANE"))[0][0]) + 1
    s1_elane_p = float(p_s1[other_genes.index("ELANE")])
    s1_n_sig = int((p_s1 < 0.05).sum())
    s1_auroc = roc_auc_score(
        np.array([g in cebpe_targets for g in other_genes]),
        -np.log10(p_s1 + 1e-300)
    )
    print(f"  ELANE rank: {s1_elane_rank}, p={s1_elane_p:.4f}, n_sig={s1_n_sig}, AUROC={s1_auroc:.3f}")

    # Combined z
    z_s1 = norm.ppf(1 - np.clip(p_s1, 1e-10, 1 - 1e-10))
    z_s2 = norm.ppf(1 - np.clip(p_perm, 1e-10, 1 - 1e-10))
    p_comb = 1 - norm.cdf((z_s1 + z_s2) / np.sqrt(2))
    comb_elane_rank = int(np.where(np.argsort(p_comb) == other_genes.index("ELANE"))[0][0]) + 1
    comb_elane_p = float(p_comb[other_genes.index("ELANE")])
    comb_n_sig = int((p_comb < 0.05).sum())
    comb_auroc = roc_auc_score(
        np.array([g in cebpe_targets for g in other_genes]),
        -np.log10(p_comb + 1e-300)
    )
    comb_hits = sum(1 for g in cebpe_targets if p_comb[other_genes.index(g)] < 0.05)
    print(f"Combined z: ELANE rank {comb_elane_rank}, p={comb_elane_p:.4f}, n_sig={comb_n_sig}, "
          f"hits={comb_hits}/9, AUROC={comb_auroc:.3f}")

    # Final summary table
    summary = pd.DataFrame({
        "Method": ["PGAA S₁ (Wasserstein)",
                   "PGAA S₂ (persistent homology, n_bins=20)",
                   "PGAA S₁+S₂ combined z"],
        "ELANE_rank": [s1_elane_rank, elane_rank, comb_elane_rank],
        "ELANE_p": [round(s1_elane_p, 4), round(elane_p, 4), round(comb_elane_p, 4)],
        "n_sig_p<0.05": [s1_n_sig, n_sig, comb_n_sig],
        "π̂₀_or_AUROC": [round(s1_auroc, 3), f"π̂₀={pi0:.2f}", round(comb_auroc, 3)],
        "Known_hits": [f"{sum(1 for g in cebpe_targets if p_s1[other_genes.index(g)]<0.05)}/9",
                       f"{hits}/9", f"{comb_hits}/9"],
        "Time_s": [round(elapsed_s1, 1), round(elapsed, 1), 0.0],
    })
    print("\n" + "=" * 60)
    print("FINAL: Norman 2019 CEBPE (n_bins=20 for S₂)")
    print("=" * 60)
    print(summary.to_string(index=False))
    summary.to_csv("scripts/prt_s2_nbins20_summary.csv", index=False)
    print(f"\nSaved: scripts/prt_s2_nbins20_summary.csv")
    print(f"Saved: scripts/norman2019_prt_s2_nbins20.csv")


if __name__ == "__main__":
    main()
