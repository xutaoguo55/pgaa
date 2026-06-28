#!/usr/bin/env python3
"""
Sensitivity analysis: S₂ n_bins ∈ {20, 30, 50, 75, 100, 150} on Norman 2019 CEBPE.

For each setting, run full S₂ with 200 perms and report:
  - ELANE rank, ELANE p-value
  - n_sig (p<0.05)
  - Storey π̂₀
  - Top known-targets hit count

This is a robustness check for the persistence statistic.
"""
import time
import numpy as np
import pandas as pd
import scanpy as sc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt_s2 import compute_persistence_1d, persistence_landscape_distance
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

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


def s2_test_fast(Y_on, Y_off, n_bins):
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
    cebpe_pert = np.where(labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True))[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]

    hvg = adata.var["highly_variable"].values.copy()
    for g in ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
              "DEFA1", "RNASE2", "CEBPE", "GAPDH", "ACTB", "B2M"]:
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

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]

    n_perms = 200
    n_bins_list = [20, 30, 50, 75, 100, 150]
    rows = []
    for n_bins in n_bins_list:
        t0 = time.time()
        Y_on = Y[D_obs]; Y_off = Y[~D_obs]
        s2_obs = s2_test_fast(Y_on, Y_off, n_bins=n_bins)
        null_stats = np.zeros((n_perms, len(other_genes)))
        D_int = D_obs.astype(int)
        rng = np.random.default_rng(42)
        for b in range(n_perms):
            D_perm = D_int.copy()
            for u in unique_ct:
                mask = ct_sub == u
                if mask.sum() >= 2:
                    D_perm[mask] = rng.permutation(D_int[mask])
            D_perm = D_perm.astype(bool)
            null_stats[b] = s2_test_fast(Y[D_perm], Y[~D_perm], n_bins=n_bins)

        p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
        p_perm = p_perm / (n_perms + 1)
        elapsed = time.time() - t0

        # Metrics
        n_sig = int((p_perm < 0.05).sum())
        pi0 = max(1, (p_perm > 0.5).sum()) / (0.5 * len(p_perm))
        elane_rank = int(np.where(np.argsort(p_perm) == other_genes.index("ELANE"))[0][0]) + 1
        elane_p = float(p_perm[other_genes.index("ELANE")])
        hits = sum(1 for g in cebpe_targets if p_perm[other_genes.index(g)] < 0.05)

        rows.append({
            "n_bins": n_bins, "elane_rank": elane_rank, "elane_p": elane_p,
            "n_sig": n_sig, "pi0": round(pi0, 3), "known_hits": f"{hits}/9",
            "time_s": round(elapsed, 1),
        })
        print(f"n_bins={n_bins:>4}: ELANE rank {elane_rank:>4} p={elane_p:.4f} "
              f"n_sig={n_sig:>4} π̂₀={pi0:.3f} hits={hits}/9 ({int(elapsed)}s)",
              flush=True)

    df = pd.DataFrame(rows)
    df.to_csv("scripts/sensitivity_s2_bins.csv", index=False)
    print(f"\nSaved: scripts/sensitivity_s2_bins.csv")

    # Verdict
    elane_ranks = df["elane_rank"].values
    if elane_ranks.std() < 50:
        print(f"\n✅ S₂ ELANE rank stable across n_bins ∈ {n_bins_list}: "
              f"{elane_ranks.min()}–{elane_ranks.max()} (range {elane_ranks.max()-elane_ranks.min()})")
    else:
        print(f"\n⚠️ S₂ ELANE rank varies widely: "
              f"{elane_ranks.min()}–{elane_ranks.max()} (range {elane_ranks.max()-elane_ranks.min()})")
        print("   Default n_bins=50 is a good compromise.")


if __name__ == "__main__":
    main()
