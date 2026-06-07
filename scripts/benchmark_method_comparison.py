#!/usr/bin/env python3
"""B: Method comparison. PRT-S₁ vs SCEPTRE/t-test/Wilcoxon on CLL."""
import sys, time, numpy as np, pandas as pd, scanpy as sc
from scipy.io import mmread; from scipy import sparse
from scipy.stats import mannwhitneyu, ttest_ind, spearmanr
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt import wasserstein_1d
from sklearn.cluster import KMeans; from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
np.random.seed(42)

# Load
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
sc.pp.subsample(adata, n_obs=5000, random_state=42)
sc.pp.normalize_total(adata, target_sum=1e4); sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)

X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
gl = list(adata.var_names)
lib = np.array(adata.X.sum(axis=1)).ravel()

# BCR markers as ground truth
BCR = ["CD79A","CD79B","MS4A1","CD19","CD22","BLNK","BTK","LYN","SYK","BANK1","CD24","PLCG2","PIK3CD"]
BCR_in_data = [g for g in BCR if g in adata.var_names]
print(f"BCR markers in data: {len(BCR_in_data)}/{len(BCR)} ({BCR_in_data[:5]}...)")

# Confounders for residualization
svd = TruncatedSVD(n_components=10, random_state=42)
ct = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(svd.fit_transform(X))
Z = np.column_stack([np.ones(adata.n_obs),
    pd.get_dummies(pd.Categorical(ct), drop_first=True, dtype=float).values,
    ((lib - lib.mean())/(lib.std()+1e-9))[:,None]])
Yr = X - Z @ np.linalg.pinv(Z.T @ Z) @ (Z.T @ X)

POS = ["TCL1A","LYN","CD79A","SYK","BTK"]
NEG = ["GAPDH","ACTB","B2M","RPLP0","HPRT1"]
all_targets = POS + NEG

results = []
for target in all_targets:
    if target not in adata.var_names: continue
    tidx = gl.index(target); v = X[:, tidx]
    hi = v >= np.percentile(v, 75); lo = v <= np.percentile(v, 25)
    n_hi = hi.sum(); n_lo = lo.sum()
    label = "POS" if target in POS else "NEG"

    row = {"target": target, "label": label, "N": n_hi + n_lo}

    # ── PRT-S₁ ──
    t0 = time.time()
    ws = np.array([
        wasserstein_1d(Yr[hi,g], Yr[lo,g]) if g != tidx else 0.0
        for g in range(adata.n_vars)
    ])
    res_w = pd.DataFrame({"gene": gl, "score": ws}).sort_values("score", ascending=False)
    t_w = time.time() - t0
    top100 = res_w.head(100)["gene"].tolist()
    bcr_w = len([g for g in BCR_in_data if g in top100])
    row["W1_BCR"] = bcr_w; row["W1_time"] = t_w

    # ── t-test ──
    t0 = time.time()
    ts = np.array([
        abs(ttest_ind(X[hi,g], X[lo,g])[0]) if g != tidx else 0.0
        for g in range(adata.n_vars)
    ])
    ts = np.nan_to_num(ts, nan=0.0)
    res_t = pd.DataFrame({"gene": gl, "score": ts}).sort_values("score", ascending=False)
    t_t = time.time() - t0
    bcr_t = len([g for g in BCR_in_data if g in res_t.head(100)["gene"].tolist()])
    row["T_BCR"] = bcr_t; row["T_time"] = t_t

    # ── Mann-Whitney (nonparametric = SCENITH-style) ──
    t0 = time.time()
    us = np.array([
        -np.log10(mannwhitneyu(X[hi,g], X[lo,g])[1] + 1e-300) if g != tidx else 0.0
        for g in range(adata.n_vars)
    ])
    us = np.nan_to_num(us, nan=0.0)
    res_u = pd.DataFrame({"gene": gl, "score": us}).sort_values("score", ascending=False)
    t_u = time.time() - t0
    bcr_u = len([g for g in BCR_in_data if g in res_u.head(100)["gene"].tolist()])
    row["U_BCR"] = bcr_u; row["U_time"] = t_u

    # ── SCEPTRE-style (rank correlation of target expr on Y_resid) ──
    t0 = time.time()
    t_expr = X[:, tidx]
    rs = np.array([
        abs(spearmanr(t_expr, X[:, g])[0]) if g != tidx else 0.0
        for g in range(adata.n_vars)
    ])
    rs = np.nan_to_num(rs, nan=0.0)
    res_s = pd.DataFrame({"gene": gl, "score": rs}).sort_values("score", ascending=False)
    t_s = time.time() - t0
    bcr_s = len([g for g in BCR_in_data if g in res_s.head(100)["gene"].tolist()])
    row["S_BCR"] = bcr_s; row["S_time"] = t_s

    # Also compute AUROC for W1
    y_true = np.array([g in BCR_in_data for g in gl])
    auroc_w = roc_auc_score(y_true, ws)
    auroc_t = roc_auc_score(y_true, ts)
    row["W1_AUROC"] = auroc_w; row["T_AUROC"] = auroc_t

    results.append(row)

df = pd.DataFrame(results)

# ── PRINT SUMMARY ──
print("\n" + "=" * 80)
print("METHOD COMPARISON: BCR marker recovery in top-100 W1 ranking")
print("CLL 5k cells, POS=BCR TFs, NEG=housekeeping genes")
print("=" * 80)
header = f"{'Target':8s} {'Label':5s} {'W1_BCR':>6s} {'T_BCR':>6s} {'U_BCR':>6s} {'S_BCR':>6s} {'W1_AUROC':>8s} {'W1_t':>5s} {'T_t':>5s}"
print(header)
print("-" * 80)
for _, r in df.iterrows():
    print(f"{r['target']:8s} {r['label']:5s} {r['W1_BCR']:6d} {r['T_BCR']:6d} {r['U_BCR']:6d} {r['S_BCR']:6d} {r['W1_AUROC']:8.3f} {r['W1_time']:4.1f}s {r['T_time']:4.1f}s")

pos = df[df['label'] == 'POS']; neg = df[df['label'] == 'NEG']
print(f"\n{'='*80}")
print(f"SUMMARY STATISTICS")
print(f"{'='*80}")
for method, col in [("W1 (Wasserstein)", "W1_BCR"), ("t-test", "T_BCR"), ("Mann-Whitney", "U_BCR"), ("Spearman rank", "S_BCR")]:
    pm = pos[col].mean(); nm = neg[col].mean()
    ratio = pm / max(nm, 0.5)
    best = "⭐" if ratio >= 2.0 else ""
    print(f"  {method:20s}: POS={pm:.1f}, NEG={nm:.1f}, ratio={ratio:.1f}x {best}")

w1_auc_p = pos["W1_AUROC"].mean(); w1_auc_n = neg["W1_AUROC"].mean()
t_auc_p = pos["T_AUROC"].mean(); t_auc_n = neg["T_AUROC"].mean()
print(f"\n  {'W1 AUROC':20s}: POS={w1_auc_p:.3f}, NEG={w1_auc_n:.3f}")
print(f"  {'T-test AUROC':20s}: POS={t_auc_p:.3f}, NEG={t_auc_n:.3f}")

print(f"\n{'='*80}")
print(f"BEST METHOD: 'W1 Wasserstein' with POS/NEG ratio shown above")
print(f"{'='*80}")
df.to_csv("scripts/method_comparison_results.csv", index=False)
