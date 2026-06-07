#!/usr/bin/env python3
"""
Combine S₁ + S₂ via multiple methods on Norman 2019 CEBPE.

Methods tested:
  (a) mean z = (z_S1 + z_S2) / sqrt(2)
  (b) max z  = max(z_S1, z_S2)
  (c) Fisher:  chi2 with 2k df
  (d) Bonferroni-min: 2 * min(p)
  (e) harmonic mean p (Wilson-Hilferty approx)
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import compute_persistence_1d, persistence_landscape_distance
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import norm, chi2

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
    cebpe_pert = np.where(labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True))[0]
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

    # S₁ (re-run for consistency, save to file)
    print("Running S₁ (Wasserstein) ...", flush=True)
    t0 = time.time()
    res_s1 = prt_s1_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                         cell_type=cell_type, library_size=lib_size)
    print(f"  done in {time.time()-t0:.1f}s", flush=True)
    res_s1 = res_s1.set_index("gene").loc[other_genes].reset_index()
    res_s1.to_csv("scripts/norman2019_prt_s1_full.csv", index=False)

    # S₂ (load 3modes if exists, else re-run)
    s2_path = "scripts/norman2019_prt_s2_3modes.csv"
    if Path(s2_path).exists():
        res_s2 = pd.read_csv(s2_path).set_index("gene").loc[other_genes].reset_index()
        print(f"S₂ loaded from {s2_path}", flush=True)
    else:
        # Run S₂ again
        Y_sub = residualize(X[test_idx], cell_type[test_idx], lib_size[test_idx])
        Y = Y_sub[:, other_idx]
        D_obs = np.zeros(N_sub, dtype=bool)
        D_obs[:n_pert] = True
        ct_sub = cell_type[test_idx].astype(int)
        unique_ct = np.unique(ct_sub)
        Y_on = Y[D_obs]; Y_off = Y[~D_obs]
        s2_obs = s2_test_fast(Y_on, Y_off, n_bins=50)
        n_perms = 500
        null_stats = np.zeros((n_perms, len(other_genes)))
        D_int = D_obs.astype(int)
        rng = np.random.default_rng(42)
        t0 = time.time()
        for b in range(n_perms):
            D_perm = D_int.copy()
            for u in unique_ct:
                mask = ct_sub == u
                if mask.sum() >= 2:
                    D_perm[mask] = rng.permutation(D_int[mask])
            D_perm = D_perm.astype(bool)
            null_stats[b] = s2_test_fast(Y[D_perm], Y[~D_perm], n_bins=50)
            if b % 100 == 0:
                print(f"  perm {b}/{n_perms}, {int(time.time()-t0)}s", flush=True)
        p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
        p_perm = p_perm / (n_perms + 1)
        null_mean = null_stats.mean(axis=0)
        null_std = null_stats.std(axis=0)
        z_gene = (s2_obs - null_mean) / (null_std + 1e-15)
        p_zscore = 2 * (1 - norm.cdf(np.abs(z_gene)))
        res_s2 = pd.DataFrame({
            "gene": other_genes, "S2_obs": s2_obs,
            "p_perm": p_perm, "z_score": z_gene, "p_zscore": p_zscore,
        })

    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]
    is_known = np.array([g in cebpe_targets for g in other_genes])

    # Combination methods
    p1 = res_s1["p_value_perm"].fillna(1.0).values
    p2 = res_s2["p_perm"].fillna(1.0).values
    z1 = norm.ppf(1 - p1)
    z2 = norm.ppf(1 - p2)

    # (a) mean z
    p_mean = 1 - norm.cdf((z1 + z2) / np.sqrt(2))
    # (b) max z
    p_max = 1 - norm.cdf(np.maximum(z1, z2))
    # (c) Fisher
    p_fisher = 1 - chi2.cdf(-2 * (np.log(p1 + 1e-300) + np.log(p2 + 1e-300)), df=4)
    # (d) Bonferroni-min
    p_bonf = 2 * np.minimum(p1, p2)
    p_bonf = np.minimum(p_bonf, 1.0)
    # (e) harmonic mean p (HMP approximation, Wilson 2019)
    n_harm = 2
    p_hmp = (np.sum(np.column_stack([1.0 / np.maximum(p1, 1e-10),
                                     1.0 / np.maximum(p2, 1e-10)]), axis=1) / n_harm) ** (-1.0 / n_harm)
    p_hmp = np.minimum(p_hmp, 1.0)

    methods = {
        "S₁ alone": p1,
        "S₂ alone": p2,
        "(a) mean z": p_mean,
        "(b) max z": p_max,
        "(c) Fisher": p_fisher,
        "(d) Bonferroni-min": p_bonf,
        "(e) harmonic mean p": p_hmp,
    }

    print("\n=== Method comparison: Norman 2019 CEBPE ===")
    print(f"{'Method':<25} {'ELANE p':>10} {'n_sig':>8} {'AUROC':>8} {'ELANE rank':>12} {'Known hits':>14}")
    rows = []
    for name, p in methods.items():
        n_sig = int((p < 0.05).sum())
        elane_p = float(p[other_genes.index("ELANE")])
        order = np.argsort(p)
        elane_rank = int(np.where(order == other_genes.index("ELANE"))[0][0]) + 1
        auroc = roc_auc_score(is_known, -np.log10(p + 1e-300))
        hits = sum(1 for g in cebpe_targets if p[other_genes.index(g)] < 0.05)
        print(f"{name:<25} {elane_p:>10.4f} {n_sig:>8} {auroc:>8.3f} {elane_rank:>12} {hits:>13}/9")
        rows.append({"method": name, "elane_p": elane_p, "n_sig": n_sig,
                     "auroc": auroc, "elane_rank": elane_rank, "known_hits": hits})
    df = pd.DataFrame(rows)
    df.to_csv("scripts/combination_methods.csv", index=False)
    print(f"\nSaved: scripts/combination_methods.csv")

    # Save per-gene detail
    detail = pd.DataFrame({
        "gene": other_genes,
        "is_known": is_known,
        "p_S1": p1, "p_S2": p2,
        "p_mean": p_mean, "p_max": p_max,
        "p_fisher": p_fisher, "p_bonf": p_bonf, "p_hmp": p_hmp,
    })
    detail.to_csv("scripts/combination_per_gene.csv", index=False)
    print(f"Saved: scripts/combination_per_gene.csv")


if __name__ == "__main__":
    main()
