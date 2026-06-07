"""4-method head-to-head on CLL 20k (large sample per user rule)."""
import sys, time, numpy as np, pandas as pd, scanpy as sc
from scipy.io import mmread; from scipy import sparse
sys.path.insert(0, '/Users/guoxutao/.openclaw/workspace/PGAA_method_paper')
from pgaa.core.prt_s3 import s3_test
from pgaa.core.prt import wasserstein_1d
from pgaa.core.prt_s2 import s2_test
from sklearn.cluster import KMeans; from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import ttest_ind
np.random.seed(42)

print("Loading CLL 20k...")
counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes)); adata.obs_names = barcodes
sc.pp.filter_cells(adata, min_counts=500); sc.pp.filter_genes(adata, min_cells=50)
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
adata = adata[adata.obs.pct_counts_mt < 20].copy()
adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
sc.pp.subsample(adata, n_obs=20000, random_state=42)
sc.pp.normalize_total(adata, target_sum=1e4); sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
adata = adata[:, adata.var["highly_variable"].values].copy()
print(f"CLL 20k HVG: {adata}")

X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
gl = list(adata.var_names)
lib = np.array(adata.X.sum(axis=1)).ravel()
ct = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(
    TruncatedSVD(n_components=10, random_state=42).fit_transform(X))

BCR = ["CD79A","CD79B","MS4A1","CD19","CD22","BLNK","BTK","LYN","SYK","BANK1","CD24","PLCG2","PIK3CD"]
BCR_in_data = [g for g in BCR if g in gl]

target = "TCL1A"
tidx = gl.index(target); v = X[:, tidx]
hi = v >= np.percentile(v, 75); lo = v <= np.percentile(v, 25)
hi_idx = np.where(hi)[0]; lo_idx = np.where(lo)[0]
print(f"TCL1A: hi={len(hi_idx)}, lo={len(lo_idx)}")

print("="*60)
print("4-METHOD on CLL 20k — TCL1A target")
print("="*60)

# t-test
t0 = time.time()
ts = np.array([abs(ttest_ind(X[hi,g], X[lo,g])[0]) if g!=tidx else 0 for g in range(adata.n_vars)])
ts = np.nan_to_num(ts)
res_t = pd.DataFrame({"gene":gl,"score":ts}).sort_values("score",ascending=False)
bcr_t = len([g for g in BCR_in_data if g in res_t.head(100)["gene"].tolist()])
auc_t = roc_auc_score(np.array([g in BCR_in_data for g in gl]), ts)
print(f"t-test:    BCR={bcr_t}/13  AUROC={auc_t:.3f}  t={time.time()-t0:.0f}s")

# S1
t0 = time.time()
ws = np.array([wasserstein_1d(X[hi,g], X[lo,g]) if g!=tidx else 0 for g in range(adata.n_vars)])
res_w = pd.DataFrame({"gene":gl,"score":ws}).sort_values("score",ascending=False)
bcr_w = len([g for g in BCR_in_data if g in res_w.head(100)["gene"].tolist()])
auc_w = roc_auc_score(np.array([g in BCR_in_data for g in gl]), ws)
print(f"S1:        BCR={bcr_w}/13  AUROC={auc_w:.3f}  t={time.time()-t0:.0f}s")

# S2
t0 = time.time()
res_s2 = s2_test(X, gl, target, hi_idx, lo_idx, cell_type=ct, library_size=lib)
bcr_s2 = len([g for g in BCR_in_data if g in res_s2.head(100)["gene"].tolist()])
auc_s2 = roc_auc_score(np.array([g in BCR_in_data for g in res_s2["gene"]]), res_s2["S2"].values)
print(f"S2:        BCR={bcr_s2}/13  AUROC={auc_s2:.3f}  t={time.time()-t0:.0f}s")

# S3 fast (subsample 4000 cells, no permutation, ranking only)
print("\nRunning S3 (subsample 4000, no perm)...")
t0 = time.time()
res_s3 = s3_test(X, gl, target, hi_idx, lo_idx, n_partners=15, k=4, mi_subsample=4000)
elapsed = time.time()-t0
bcr_s3 = len([g for g in BCR_in_data if g in res_s3.head(100)["gene"].tolist()])
auc_s3 = roc_auc_score(np.array([g in BCR_in_data for g in res_s3["gene"]]), res_s3["S3"].values)
print(f"S3:        BCR={bcr_s3}/13  AUROC={auc_s3:.3f}  t={elapsed:.0f}s")
print(f"  Top 10 S3: {res_s3.head(10)['gene'].tolist()}")

print("\nBCR in top-100:")
for name, s in [("t-test", res_t), ("S1", res_w), ("S2", res_s2), ("S3", res_s3)]:
    bcr = [g for g in BCR_in_data if g in s.head(100)["gene"].tolist()]
    print(f"  {name:8s}: {bcr}")

res_t.to_csv("scripts/cll20k_tcl1a_t.csv", index=False)
res_w.to_csv("scripts/cll20k_tcl1a_s1.csv", index=False)
res_s2.to_csv("scripts/cll20k_tcl1a_s2.csv", index=False)
res_s3.to_csv("scripts/cll20k_tcl1a_s3.csv", index=False)
print("\n✓ Saved 4 methods on CLL 20k")
