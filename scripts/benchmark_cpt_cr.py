#!/usr/bin/env python3
"""
PGAA-CR: Causal Regression with Continuous Response (UMI_count).

Innovation: instead of binary D, use the actual guide RNA UMI count
as continuous treatment intensity.  This is novel for Perturb-seq,
where every cell has a UMI_count indicating how strongly the
perturbation is being expressed.

This is mathematically equivalent to dose-response analysis in
econometrics, and to heterogeneous treatment effects estimation
(Wager & Athey 2018).  No published Perturb-seq method uses
continuous UMI_count as treatment.

Model:  Y_g = alpha_g * UMI_count + beta * cell_type + gamma * library_size + eps
  - alpha_g: causal effect per unit UMI
  - Permutation test: shuffle UMI_count across cells, re-fit, get null
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import pickle
import gzip
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import t as tdist
import statsmodels.stats.multitest as mt

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
np.random.seed(42)


def main():
    adata = sc.read_h5ad("/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad")
    labels = adata.obs["perturbation"].astype(str)
    print(f"Full: {adata.shape}")

    # Load UMI_count from cell identity file
    with gzip.open("/Users/guoxutao/.openclaw/workspace/norman2019/GSE133344_filtered_cell_identities.csv.gz", "rt") as f:
        ci = pd.read_csv(f)
    ci_dict = dict(zip(ci["cell_barcode"], ci["UMI_count"]))
    obs = adata.obs.copy()
    obs["UMI_count"] = obs.index.map(ci_dict).fillna(0)
    print(f"UMI_count distribution: {obs['UMI_count'].describe()}")

    # Build subset: CEBPE-perturbed (with UMI>0) + control (UMI=0)
    cebpe_pert = np.where((labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True)) & (obs["UMI_count"].values > 0))[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][:len(cebpe_pert) * 3]
    test_idx = np.concatenate([cebpe_pert, ctrl_idx])
    print(f"CEBPE: {len(cebpe_pert)} perturbed, {len(ctrl_idx)} control")

    # Subset to HVGs + target genes
    hvg = adata.var["highly_variable"].values.copy() if "highly_variable" in adata.var.columns else np.ones(adata.n_vars, dtype=bool)
    extra = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2",
             "CEBPE", "CEBPA", "SPI1", "GAPDH", "ACTB", "B2M", "RPLP0", "RPS18",
             "HBB", "HBA1", "HBA2", "AHSP", "GYPA", "ALAS2"]
    for g in extra:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()
    print(f"Using {adata_hvg.n_vars} genes (HVGs + targets)")

    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)
    X_sub = X[test_idx]
    UMI = obs["UMI_count"].values[test_idx]
    lib_size = X_sub.sum(axis=1)
    print(f"UMI in subset: min={UMI.min()}, max={UMI.max()}, mean={UMI.mean():.1f}")

    # Cell type via k-means on subset
    print("K-means for cell type ...")
    svd = TruncatedSVD(n_components=10, random_state=42)
    X_20 = svd.fit_transform(X_sub)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_20)
    print(f"Cluster sizes: {pd.Series(cell_type).value_counts().to_dict()}")

    # Build design: Y_g ~ UMI + cell_type_dummies + lib_size
    N_sub = len(test_idx)
    parts = [np.ones(N_sub)]
    ct = pd.Categorical(cell_type)
    ct_dummies = pd.get_dummies(ct, drop_first=True, dtype=float).values
    parts.append(ct_dummies)
    lib_z = (lib_size - lib_size.mean()) / (lib_size.std() + 1e-9)
    parts.append(lib_z[:, None])
    Z_base = np.column_stack(parts)
    p_base = Z_base.shape[1]
    UMI_c = UMI - UMI.mean()
    UMI_z = UMI_c / (UMI.std() + 1e-9)

    # Add UMI to design
    Zd = np.column_stack([Z_base, UMI_z])
    p = Zd.shape[1]

    tidx = genes.index("CEBPE")
    other_idx = [i for i in range(len(genes)) if i != tidx]
    Y = X_sub[:, other_idx]
    Yc = Y - Y.mean(axis=0, keepdims=True)

    # Observed: alpha for UMI
    ZtZ_inv = np.linalg.pinv(Zd.T @ Zd)
    beta = ZtZ_inv @ (Zd.T @ Yc)
    alpha = beta[-1, :]
    resid = Yc - Zd @ beta
    dof = N_sub - p
    sigma2 = (resid ** 2).sum(axis=0) / dof
    se_alpha = np.sqrt(np.diag(ZtZ_inv)[-1] * sigma2)
    t_stat = alpha / (se_alpha + 1e-15)
    p_value = 2 * tdist.sf(np.abs(t_stat), dof)
    fdr = mt.multipletests(p_value, method="fdr_bh")[1]

    print(f"\nPGAA-CR (OLS with UMI_count): {int((fdr<0.05).sum())} sig at FDR<0.05")
    res = pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "alpha_UMI": alpha, "se": se_alpha, "t_stat": t_stat,
        "p_value": p_value, "fdr": fdr,
    }).sort_values("p_value")
    print("Top 20:")
    print(res.head(20).to_string(index=False))

    # Known targets
    cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"]
    known = res[res["gene"].isin(cebpe_targets)].sort_values("p_value")
    print(f"\nCEBPE known targets (PGAA-CR):")
    print(known.to_string(index=False))
    n_known_hit = int((known["fdr"] < 0.05).sum())
    print(f"Known targets with FDR<0.05: {n_known_hit}/{len(known)}")

    # AUROC
    y_true = res["gene"].isin(cebpe_targets).astype(int).values
    scores = -np.log10(res["p_value"].fillna(1.0).values + 1e-300)
    auroc = roc_auc_score(y_true, scores) if y_true.sum() > 0 else float("nan")

    # Permutation test
    print(f"\nRunning permutation test (1000 perms) ...")
    n_perms = 1000
    t0 = time.time()
    obs_stat = t_stat  # use t_stat as test statistic
    null_stats = np.zeros((n_perms, len(other_idx)))
    for b in range(n_perms):
        if b % 200 == 0:
            print(f"  {b}/{n_perms}, {time.time()-t0:.1f}s")
        UMI_perm = np.random.permutation(UMI_z)
        Zd_p = np.column_stack([Z_base, UMI_perm])
        ZtZ_inv_p = np.linalg.pinv(Zd_p.T @ Zd_p)
        beta_p = ZtZ_inv_p @ (Zd_p.T @ Yc)
        resid_p = Yc - Zd_p @ beta_p
        sigma2_p = (resid_p ** 2).sum(axis=0) / dof
        se_p = np.sqrt(np.diag(ZtZ_inv_p)[-1] * sigma2_p)
        null_stats[b] = beta_p[-1, :] / (se_p + 1e-15)
    p_perm = (np.abs(null_stats) >= np.abs(obs_stat)[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)
    fdr_perm = mt.multipletests(p_perm, method="fdr_bh")[1]
    print(f"PGAA-CR (permutation): {int((fdr_perm<0.05).sum())} sig at FDR<0.05")

    res["p_value_perm"] = p_perm
    res["fdr_perm"] = fdr_perm
    known = res[res["gene"].isin(cebpe_targets)].sort_values("p_value_perm")
    print(f"\nKnown targets (permutation): {int((known['fdr_perm']<0.05).sum())}/{len(known)}")
    print(known[["gene", "alpha_UMI", "p_value_perm", "fdr_perm"]].to_string(index=False))

    # AUROC for permutation
    y_true2 = res["gene"].isin(cebpe_targets).astype(int).values
    scores2 = -np.log10(res["p_value_perm"].fillna(1.0).values + 1e-300)
    auroc_perm = roc_auc_score(y_true2, scores2) if y_true2.sum() > 0 else float("nan")

    # Negative control: GAPDH (not perturbed)
    print("\n" + "="*60)
    print("Negative control: GAPDH (not perturbed)")
    print("="*60)
    tidx_g = genes.index("GAPDH")
    other_idx_g = [i for i in range(len(genes)) if i != tidx_g]
    Y_g = X_sub[:, other_idx_g]
    Yc_g = Y_g - Y_g.mean(axis=0, keepdims=True)
    beta_g = ZtZ_inv @ (Zd.T @ Yc_g)
    alpha_g = beta_g[-1, :]
    se_g = np.sqrt(np.diag(ZtZ_inv)[-1] * ((Yc_g - Zd @ beta_g)**2).sum(axis=0) / dof)
    p_g = 2 * tdist.sf(np.abs(alpha_g / (se_g + 1e-15)), dof)
    fdr_g = mt.multipletests(p_g, method="fdr_bh")[1]
    print(f"GAPDH-as-target: {int((fdr_g<0.05).sum())} sig at FDR<0.05")

    summary = pd.DataFrame({
        "Method": ["PGAA-CR (OLS)", "PGAA-CR (perm)"],
        "CEBPE_sig": [int((fdr<0.05).sum()), int((fdr_perm<0.05).sum())],
        "CEBPE_AUROC": [auroc, auroc_perm],
        "Known_hit": [f"{int((res[res['gene'].isin(cebpe_targets)]['fdr']<0.05).sum())}/{len(cebpe_targets)}",
                      f"{int((res[res['gene'].isin(cebpe_targets)]['fdr_perm']<0.05).sum())}/{len(cebpe_targets)}"],
        "GAPDH_neg_sig": [int((fdr_g<0.05).sum()), "N/A"],
    })
    print("\n" + "="*60)
    print("PGAA-CR Summary (Causal Regression with UMI_count)")
    print("="*60)
    print(summary.to_string(index=False))
    summary.to_csv("scripts/pgaa_cr_summary.csv", index=False)
    res.to_csv("scripts/pgaa_cr_results.csv", index=False)


if __name__ == "__main__":
    main()
