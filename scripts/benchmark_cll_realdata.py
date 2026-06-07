#!/usr/bin/env python3
"""
PGAA validation with Pearson residual variance stabilization.

This is a more robust path than scVI. We:
  1. Compute Pearson residuals from raw counts (Anscombe-like)
  2. Run linear PCA on Pearson residuals
  3. Cross-fit OLS residualization
  4. GCM test

Pearson residuals are designed to remove mean-variance dependence, which
should reduce expression-magnitude-driven false positives (ribosome hits).
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.io import mmread

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.dml_engine import DMLEngine

np.random.seed(42)

HK_GENES = [
    "ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
    "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1",
]

BCR_MARKERS = ["CD79A", "CD79B", "BANK1", "LYN", "BLNK", "SYK", "BTK",
               "PLCG2", "PIK3CD", "MS4A1", "CD19", "CD22"]


def load_cll():
    print("Loading CLL data ...")
    counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
    genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
    barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
    meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
    print(f"Loaded: {adata.n_obs} cells × {adata.n_vars} genes")
    return adata


def preprocess_pearson(adata, n_cells_max=5000):
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=50)
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
    adata = adata[adata.obs.pct_counts_mt < 20].copy()
    adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
    if adata.n_obs > n_cells_max:
        sc.pp.subsample(adata, n_obs=n_cells_max, random_state=42)

    # Convert to dense (Pearson residual needs cell sums)
    adata.layers["counts"] = adata.X.copy()

    # Standard size factor normalization first
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=5000, subset=False)

    # Compute Pearson residuals on raw counts (not log-transformed)
    from scipy.stats import nbinom, nbinom as nb
    X = adata.layers["counts"]
    if sparse.issparse(X):
        X = X.toarray()
    X = X.astype(np.float64)
    n_cells = X.shape[0]
    cell_sums = X.sum(axis=1)
    cell_sums = np.maximum(cell_sums, 1e-3)
    # Gene-wise mean and overdispersion via method-of-moments
    gene_means = X.mean(axis=0)
    gene_vars = X.var(axis=0)
    overdisp = np.maximum((gene_vars - gene_means) / (gene_means ** 2 + 1e-9), 0.01)

    # Pearson residuals per cell, per gene:
    # r_g = (X_g - mu_g) / sqrt(mu_g + phi_g * mu_g^2)
    mu = gene_means[None, :]
    phi = overdisp[None, :]
    size_factor = cell_sums / cell_sums.mean()
    mu_cell = size_factor[:, None] * mu
    var_cell = mu_cell + phi * mu_cell ** 2
    pearson = (X - mu_cell) / np.sqrt(var_cell + 1e-9)

    # Clip extreme values and replace .X
    pearson = np.clip(pearson, -np.sqrt(n_cells), np.sqrt(n_cells))
    adata.X = sparse.csr_matrix(pearson.astype(np.float32))

    print(f"After QC + Pearson residual: {adata.n_obs} cells × {adata.n_vars} genes")
    return adata


def run_target(adata, target, label, hk_genes=None):
    print(f"\n{'='*60}")
    print(f"Target: {target} ({label})")
    print(f"{'='*60}")
    if target not in adata.var_names:
        print(f"WARNING: {target} not found.")
        return None, 0

    adata_hvg = adata[:, adata.var["highly_variable"]].copy()

    t0 = time.time()
    expr = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    expr = np.asarray(expr, dtype=np.float64).T
    genes = list(adata_hvg.var_names)

    engine = DMLEngine(
        n_confounders=10,
        use_linear_stage1=True,
        random_state=42,
    )
    tidx = genes.index(target)
    engine.fit_confounders(expr, genes=genes, exclude_idx=tidx)
    res = engine.estimate_target(target, hk_genes=hk_genes)
    elapsed = time.time() - t0

    n_sig = int(res["significant"].sum())
    print(f"Runtime: {elapsed:.1f}s")
    print(f"Significant (FDR<0.05): {n_sig}")
    if n_sig > 0:
        print("Top 10:")
        print(res[res["significant"]].head(10)[["gene", "alpha", "p_value", "p_adjusted", "tier"]].to_string(index=False))

    hits = res[res["significant"]].head(200)["gene"].tolist()
    bcr = [g for g in hits if g in BCR_MARKERS]
    ribo = [g for g in hits if g.startswith("RPS") or g.startswith("RPL")]
    print(f"  BCR (positive control) in top-200: {len(bcr)} ({bcr})")
    print(f"  Ribo (negative control) in top-200: {len(ribo)}")
    return res, elapsed


if __name__ == "__main__":
    adata = load_cll()
    adata = preprocess_pearson(adata)

    results = []
    for target, label in [("TCL1A", "positive"), ("ACTB", "negative")]:
        res, t = run_target(adata, target, label, hk_genes=HK_GENES)
        if res is not None:
            hits = res[res["significant"]].head(200)["gene"].tolist()
            bcr = [g for g in hits if g in BCR_MARKERS]
            ribo = [g for g in hits if g.startswith("RPS") or g.startswith("RPL")]
            results.append({
                "target": target, "label": label, "sig": int(res["significant"].sum()),
                "time": t, "bcr": len(bcr), "ribo": len(ribo),
            })

    print("\n" + "="*60)
    print("Summary (Pearson residual + Linear PCA)")
    print("="*60)
    summary = pd.DataFrame(results)
    print(summary.to_string(index=False))
    summary.to_csv("scripts/benchmark_cll_pearson.csv", index=False)
