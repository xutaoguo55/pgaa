#!/usr/bin/env python3
"""
S₂ STRICT negative control: use KLF1 perturbation as "fake target".

Hypothesis: if S₂ is detecting cell-type composition differences
(rather than perturbation-specific downstream effects), then running
S₂ with KLF1 as the "target" should give similar top hits to running
with CEBPE — because the same set of perturbed cells is being compared
to the same control cells.

If S₂ is truly perturbation-specific, ELANE/AZU1/MPO (CEBPE targets)
should DROP in KLF1 ranking (they're neutrophil granule proteins,
not KLF1 targets).
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


def run_s2_for_target(adata, target_gene, n_perms=200, seed=42):
    """Run S₂ with a given target gene's perturbed cells."""
    labels = adata.obs["perturbation"].astype(str)
    pert = np.where(
        labels.str.contains(rf"^{target_gene}_NegCtrl\d+__", regex=True)
    )[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl = np.where(ctrl_mask)[0][:len(pert) * 3]
    if len(pert) < 30:
        return None

    hvg = adata.var["highly_variable"].values.copy()
    for g in ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
              "DEFA1", "RNASE2", "CEBPE", "GAPDH", "ACTB", "B2M",
              target_gene]:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    X = adata[:, hvg].X.toarray() if hasattr(adata[:, hvg].X, "toarray") else adata[:, hvg].X
    genes = list(adata[:, hvg].var_names)
    lib_size = np.array(adata[:, hvg].X.sum(axis=1)).ravel()
    svd = TruncatedSVD(n_components=10, random_state=42)
    X_20 = svd.fit_transform(X)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)

    test_idx = np.concatenate([pert, ctrl])
    tidx = genes.index(target_gene)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]
    Y_sub = residualize(X[test_idx], cell_type[test_idx], lib_size[test_idx])
    Y = Y_sub[:, other_idx]
    D_obs = np.zeros(len(test_idx), dtype=bool)
    D_obs[:len(pert)] = True
    ct_sub = cell_type[test_idx].astype(int)
    unique_ct = np.unique(ct_sub)

    Y_on = Y[D_obs]; Y_off = Y[~D_obs]
    s2_obs = s2_test_fast(Y_on, Y_off, n_bins=50)

    null_stats = np.zeros((n_perms, len(other_genes)))
    D_int = D_obs.astype(int)
    rng = np.random.default_rng(seed)
    t0 = time.time()
    for b in range(n_perms):
        D_perm = D_int.copy()
        for u in unique_ct:
            mask = ct_sub == u
            if mask.sum() >= 2:
                D_perm[mask] = rng.permutation(D_int[mask])
        D_perm = D_perm.astype(bool)
        null_stats[b] = s2_test_fast(Y[D_perm], Y[~D_perm], n_bins=50)
        if b % 50 == 0:
            print(f"  perm {b}/{n_perms}, {int(time.time()-t0)}s", flush=True)

    p_perm = (null_stats >= s2_obs[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    res = pd.DataFrame({
        "gene": other_genes, "S2": s2_obs, "p_value_perm": p_perm,
    })
    return res, len(pert)


def main():
    adata = sc.read_h5ad(
        "/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad"
    )

    targets = ["CEBPE", "KLF1", "SLC4A1", "BAK1", "DUSP9", "CBL"]
    results = {}
    for t in targets:
        print(f"\n=== Running S₂ for {t} (200 perms) ===", flush=True)
        r = run_s2_for_target(adata, t, n_perms=200)
        if r is None:
            print(f"  Skipping {t} (too few cells)")
            continue
        res, n_pert = r
        results[t] = res
        n_sig = int((res["p_value_perm"] < 0.05).sum())
        pi0 = max(1, (res["p_value_perm"] > 0.5).sum()) / (0.5 * len(res))
        print(f"  {t}: n_pert={n_pert}, n_sig={n_sig}, π̂₀={pi0:.3f}", flush=True)

    # Compare known CEBPE targets across targets
    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                     "PRTN3", "DEFA1", "RNASE2"]
    print("\n=== CEBPE target genes: rank & p across all 'targets' ===")
    print(f"{'gene':<10}", end="")
    for t in targets:
        if t in results:
            print(f" {t+' p':>10}", end="")
    print()
    for g in cebpe_targets:
        print(f"{g:<10}", end="")
        for t in targets:
            if t in results and g in results[t]["gene"].values:
                p = float(results[t].set_index("gene").loc[g, "p_value_perm"])
                print(f" {p:>10.4f}", end="")
            else:
                print(f" {'N/A':>10}", end="")
        print()

    # Save
    pd.concat([df.assign(target=t) for t, df in results.items()]).to_csv(
        "scripts/s2_multitarget_neg_ctrl.csv", index=False
    )
    print(f"\nSaved: scripts/s2_multitarget_neg_ctrl.csv")

    # Key test: are CEBPE targets also "significant" for non-CEBPE perturbations?
    print("\n=== KEY DIAGNOSTIC ===")
    print("If CEBPE targets are 'sig' for KLF1/SLC4A1 too, S₂ is non-specific.")
    for g in cebpe_targets:
        sig_for = []
        for t in targets:
            if t in results and g in results[t]["gene"].values:
                p = float(results[t].set_index("gene").loc[g, "p_value_perm"])
                if p < 0.05:
                    sig_for.append(f"{t}(p={p:.3f})")
        print(f"  {g}: {', '.join(sig_for) if sig_for else 'no sig'}")


if __name__ == "__main__":
    main()
