#!/usr/bin/env python3
"""
4-METHOD HEAD-TO-HEAD ON FULL DATA (no subsampling).

Datasets:
  - CLL 36k
  - Sepsis 64k
  - RA 10k
  - PBMC 25k
  - IBD 11k

Methods: t-test, S₁ (Wasserstein), S₂ (TDA), S₃ (Conditional MI)
"""
import sys, time, numpy as np, pandas as pd, scanpy as sc
from scipy.io import mmread; from scipy import sparse
from pathlib import Path
sys.path.insert(0, '/Users/guoxutao/.openclaw/workspace/PGAA_method_paper')
from pgaa.core.prt_s3 import s3_test
from pgaa.core.prt import wasserstein_1d
from pgaa.core.prt_s2 import s2_test
from sklearn.cluster import KMeans; from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import ttest_ind
np.random.seed(42)

BCR = ["CD79A","CD79B","MS4A1","CD19","CD22","BLNK","BTK","LYN","SYK","BANK1","CD24","PLCG2","PIK3CD"]


def load_cll_full():
    counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
    genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
    barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
    meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
    sc.pp.filter_cells(adata, min_counts=500); sc.pp.filter_genes(adata, min_cells=50)
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
    adata = adata[adata.obs.pct_counts_mt < 20].copy()
    adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
    sc.pp.normalize_total(adata, target_sum=1e4); sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
    return adata


def load_h5ad(path, n_top_genes=2000, subsample=None):
    adata = sc.read_h5ad(path)
    if subsample and adata.n_obs > subsample:
        sc.pp.subsample(adata, n_obs=subsample, random_state=42)
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=10)
    sc.pp.normalize_total(adata, target_sum=1e4); sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, subset=False)
    return adata


def run_one(adata, target, name, hvg_only=True, immune_set="BCR"):
    """
    Run all 4 methods on a single (adata, target) pair using FULL data.
    Returns dict with results.
    """
    print(f"\n{'='*60}")
    print(f"[{name}] {target}: {adata.n_obs} cells × {adata.n_vars} genes")
    print(f"{'='*60}")

    if hvg_only:
        adata = adata[:, adata.var["highly_variable"].values].copy()
        print(f"  HVG subset: {adata.shape}")

    if target not in adata.var_names:
        print(f"  SKIP: {target} not in data")
        return None

    X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
    gl = list(adata.var_names)
    lib = np.array(adata.X.sum(axis=1)).ravel()
    svd = TruncatedSVD(n_components=10, random_state=42)
    ct = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(svd.fit_transform(X))

    immune_genes = {
        "BCR": ["CD79A","CD79B","MS4A1","CD19","CD22","BLNK","BTK","LYN","SYK","BANK1","CD24","PLCG2","PIK3CD"],
        "TCR": ["CD3D","CD3E","CD3G","CD247","TRAC","TRBC1","TRBC2","LCK","ZAP70"],
        "Mye": ["CD14","CD68","FCGR3A","CSF1R","ITGAM","LYZ","MPO","ELANE"],
    }
    target_imm = [g for g in immune_genes.get(immune_set, immune_genes["BCR"]) if g in gl]

    tidx = gl.index(target); v = X[:, tidx]
    # Quartile split
    hi = v >= np.percentile(v, 75); lo = v <= np.percentile(v, 25)
    if hi.sum() < 50 or lo.sum() < 50:
        print(f"  SKIP: too few hi/lo cells")
        return None
    hi_idx = np.where(hi)[0]; lo_idx = np.where(lo)[0]

    res = {"name": name, "target": target, "n": adata.n_obs}

    # t-test
    t0 = time.time()
    ts = np.array([abs(ttest_ind(X[hi,g], X[lo,g])[0]) if g!=tidx else 0 for g in range(adata.n_vars)])
    ts = np.nan_to_num(ts)
    res["t"] = pd.DataFrame({"gene":gl,"score":ts}).sort_values("score",ascending=False)
    res["t_time"] = time.time()-t0
    res["t_imm"] = len([g for g in target_imm if g in res["t"].head(100)["gene"].tolist()])

    # S₁
    t0 = time.time()
    ws = np.array([wasserstein_1d(X[hi,g], X[lo,g]) if g!=tidx else 0 for g in range(adata.n_vars)])
    res["s1"] = pd.DataFrame({"gene":gl,"score":ws}).sort_values("score",ascending=False)
    res["s1_time"] = time.time()-t0
    res["s1_imm"] = len([g for g in target_imm if g in res["s1"].head(100)["gene"].tolist()])

    # S₂
    t0 = time.time()
    res["s2"] = s2_test(X, gl, target, hi_idx, lo_idx, cell_type=ct, library_size=lib)
    res["s2_time"] = time.time()-t0
    res["s2_imm"] = len([g for g in target_imm if g in res["s2"].head(100)["gene"].tolist()])

    # S₃ fast (n_partners=30, n_perm=10 for speed on full data)
    t0 = time.time()
    res["s3"] = s3_test(X, gl, target, hi_idx, lo_idx, n_partners=30, k=4, n_perm=10)
    res["s3_time"] = time.time()-t0
    res["s3_imm"] = len([g for g in target_imm if g in res["s3"].head(100)["gene"].tolist()])
    res["s3_sig"] = int(res["s3"]["significant"].sum())

    # AUROC
    y_true = np.array([g in target_imm for g in gl])
    res["t_auc"] = roc_auc_score(y_true, ts) if y_true.sum() > 0 else np.nan
    res["s1_auc"] = roc_auc_score(y_true, ws) if y_true.sum() > 0 else np.nan
    res["s2_auc"] = roc_auc_score(y_true, res["s2"]["S2"].values) if y_true.sum() > 0 else np.nan
    res["s3_auc"] = roc_auc_score(y_true, res["s3"]["S3"].values) if y_true.sum() > 0 else np.nan

    print(f"  t-test:  BCR={res['t_imm']}/{len(target_imm)}  AUROC={res['t_auc']:.3f}  t={res['t_time']:.0f}s")
    print(f"  S₁:      BCR={res['s1_imm']}/{len(target_imm)}  AUROC={res['s1_auc']:.3f}  t={res['s1_time']:.0f}s")
    print(f"  S₂:      BCR={res['s2_imm']}/{len(target_imm)}  AUROC={res['s2_auc']:.3f}  t={res['s2_time']:.0f}s")
    print(f"  S₃:      BCR={res['s3_imm']}/{len(target_imm)}  AUROC={res['s3_auc']:.3f}  t={res['s3_time']:.0f}s  sig={res['s3_sig']}")
    print(f"  S₃ Top 5: {res['s3'].head(5)['gene'].tolist()}")

    return res


# ── 1. CLL FULL (36k) ─────────────────────────────────────────
cll = load_cll_full()
res_cll_tcl1a = run_one(cll, "TCL1A", "CLL 36k", immune_set="BCR")
res_cll_lyn = run_one(cll, "LYN", "CLL 36k", immune_set="BCR")
res_cll_cd79a = run_one(cll, "CD79A", "CLL 36k", immune_set="BCR")

# Save CLL results
if res_cll_tcl1a is not None:
    for k in ["t", "s1", "s2", "s3"]:
        if k in res_cll_tcl1a:
            res_cll_tcl1a[k].to_csv(f"scripts/final_TCL1A_{k}.csv", index=False)
