#!/usr/bin/env python3
"""Diagnostic: understand why PGAA fails on real CLL data."""

import time
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.io import mmread
from scipy.stats import spearmanr, pearsonr, norm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

np.random.seed(42)

BCR_MARKERS = ["CD79A", "CD79B", "BANK1", "LYN", "BLNK", "SYK", "BTK", "PLCG2", "PIK3CD", "MS4A1", "CD19", "CD22"]


def load_cll():
    print("Loading CLL data ...")
    counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
    genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
    barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
    meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
    return adata


def preprocess(adata, n_cells_max=5000, n_top_genes=2000):
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=50)
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
    adata = adata[adata.obs.pct_counts_mt < 20].copy()
    adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
    if adata.n_obs > n_cells_max:
        sc.pp.subsample(adata, n_obs=n_cells_max, random_state=42)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, subset=False)
    return adata


def test1_variance_breakdown(adata):
    print("\n" + "="*60)
    print("Test 1: Target gene variance breakdown")
    print("="*60)
    for target in ["TCL1A", "ACTB", "GAPDH", "RPS18", "CD79A"]:
        if target not in adata.var_names:
            continue
        idx = list(adata.var_names).index(target)
        hvg_mask = adata.var["highly_variable"].values.copy()
        hvg_mask[idx] = False
        X_hvg = adata.X[:, hvg_mask]
        if sparse.issparse(X_hvg):
            X_hvg = X_hvg.toarray()
        X_hvg = np.asarray(X_hvg, dtype=np.float64)
        scaler = StandardScaler()
        X_std = scaler.fit_transform(X_hvg)
        K = min(50, X_std.shape[0], X_std.shape[1])
        U, s, Vt = np.linalg.svd(X_std, full_matrices=False)
        Z = U[:, :K] * s[:K]
        x = adata.X[:, idx]
        if sparse.issparse(x):
            x = x.toarray().ravel()
        x = np.asarray(x, dtype=np.float64)
        x_c = x - x.mean()
        for k_test in [5, 10, 20, 50]:
            Z_k = Z[:, :k_test]
            Zd = np.column_stack([np.ones(len(Z_k)), Z_k])
            beta = np.linalg.pinv(Zd.T @ Zd) @ (Zd.T @ x)
            x_pred = Zd @ beta
            ss_res = np.sum((x - x_pred) ** 2)
            ss_tot = np.sum(x_c ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            r2_corr = 1 - (1 - r2) * (len(x) - 1) / (len(x) - k_test - 1)
            print(f"  {target:6s}  K={k_test:2d}  R^2={r2:.3f}  R^2_adj={r2_corr:.3f}")


def test2_scenith_baseline(adata):
    print("\n" + "="*60)
    print("Test 2: SCENITH-style regression Y ~ D + cell covariates")
    print("="*60)
    hvg_mask = adata.var["highly_variable"].values
    Y = adata.X[:, hvg_mask]
    if sparse.issparse(Y):
        Y = Y.toarray()
    Y = np.asarray(Y, dtype=np.float64)
    Y = Y - Y.mean(axis=0, keepdims=True)
    genes_hvg = list(adata.var_names[hvg_mask])

    cov = adata.obs[["n_genes_by_counts", "total_counts", "pct_counts_mt"]].values
    cov = (cov - cov.mean(axis=0)) / (cov.std(axis=0) + 1e-9)
    scaler = StandardScaler()
    Y_std = scaler.fit_transform(Y)
    U, s, Vt = np.linalg.svd(Y_std, full_matrices=False)
    Z5 = U[:, :5] * s[:5]
    X_full = np.column_stack([cov, Z5])

    for target in ["TCL1A", "ACTB"]:
        if target not in adata.var_names:
            continue
        idx = list(adata.var_names).index(target)
        D = adata.X[:, idx]
        if sparse.issparse(D):
            D = D.toarray().ravel()
        D = np.asarray(D, dtype=np.float64)
        D_c = D - D.mean()
        Zd = np.column_stack([np.ones(len(D_c)), X_full, D_c])
        ZtZ_inv = np.linalg.pinv(Zd.T @ Zd)
        beta = ZtZ_inv @ (Zd.T @ Y)
        alpha = beta[-1, :]
        resid = Y - Zd @ beta
        sigma2 = (resid ** 2).sum(axis=0) / (len(D) - Zd.shape[1])
        se_alpha = np.sqrt(np.diag(ZtZ_inv)[-1] * sigma2)
        z = alpha / (se_alpha + 1e-15)
        p = 2 * (1 - norm.cdf(np.abs(z)))
        n_sig = ((p < 0.05) & (np.abs(alpha) > 0.1)).sum()
        order = np.argsort(p)
        top10_genes = [genes_hvg[i] for i in order[:10]]
        top200 = [genes_hvg[i] for i in order[:200]]
        bcr_hits = [g for g in top200 if g in BCR_MARKERS]
        ribo = [g for g in top200 if g.startswith("RPS") or g.startswith("RPL")]
        print(f"  {target:6s}  sig={n_sig:4d}  BCR={len(bcr_hits):2d}  Ribo={len(ribo):2d}  top10={top10_genes[:5]}")


if __name__ == "__main__":
    adata = load_cll()
    adata = preprocess(adata, n_cells_max=5000, n_top_genes=2000)
    print(f"Using {adata.n_obs} cells x {adata.n_vars} genes ({adata.var['highly_variable'].sum()} HVGs)")
    test1_variance_breakdown(adata)
    test2_scenith_baseline(adata)
