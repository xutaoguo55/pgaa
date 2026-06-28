#!/usr/bin/env python3
"""Validate the realdata Y~D+covariates approach on CLL."""

import time
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.io import mmread

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.tools.realdata import virtual_oe_reald

np.random.seed(42)

HK_GENES = ["ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
            "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]
BCR_MARKERS = ["CD79A", "CD79B", "BANK1", "LYN", "BLNK", "SYK", "BTK",
               "PLCG2", "PIK3CD", "MS4A1", "CD19", "CD22"]


def load_cll(n_cells_max=5000):
    counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
    genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
    barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
    meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
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
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
    return adata


def evaluate(res, adata, target, label):
    n_sig = int(res["significant"].sum())
    top200 = res.head(200)["gene"].tolist()
    bcr = [g for g in top200 if g in BCR_MARKERS]
    ribo = [g for g in top200 if g.startswith("RPS") or g.startswith("RPL")]
    hk_top200 = [g for g in top200 if g in HK_GENES]
    print(f"\n{target} ({label}): sig={n_sig}, BCR={len(bcr)} ({bcr[:3]}), Ribo={len(ribo)}, HK-in-top200={len(hk_top200)}")
    if n_sig > 0:
        print("Top 5:", res.head(5)[["gene", "alpha", "p_value", "p_adjusted"]].to_string(index=False))
    return n_sig, len(bcr), len(ribo)


if __name__ == "__main__":
    rows = []
    # Use real validation: TCL1A positive, GAPDH true-negative
    # ACTB/B2M in CLL have real biology (cytoskeleton / MHC-I), not ideal negatives
    for n_cells in [5000, 10000, 20000, 36568]:
        print(f"\n{'#'*60}\n# n_cells = {n_cells}\n{'#'*60}")
        adata = load_cll(n_cells_max=n_cells)
        print(f"Using {adata.n_obs} cells, {adata.var['highly_variable'].sum()} HVGs")
        for target, label in [("TCL1A", "POS"), ("GAPDH", "NEG")]:
            t0 = time.time()
            res = virtual_oe_reald(
                adata, target,
                hk_genes=HK_GENES,
                n_pcs=10,
                random_state=42,
            )
            elapsed = time.time() - t0
            n_sig, n_bcr, n_ribo = evaluate(res, adata, target, label)
            rows.append({"n_cells": n_cells, "target": target, "label": label,
                         "sig": n_sig, "bcr": n_bcr, "ribo": n_ribo, "time": elapsed})

    df = pd.DataFrame(rows)
    print("\n" + "="*60)
    print("Final Summary (TCL1A POS vs GAPDH NEG)")
    print("="*60)
    print(df.to_string(index=False))
    df.to_csv("scripts/benchmark_reald.csv", index=False)
