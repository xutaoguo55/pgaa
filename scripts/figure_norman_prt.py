#!/usr/bin/env python3
"""Figure: PRT variants on Norman 2019 CEBPE → ELANE.

3-panel figure showing:
  (A) Volcano-style: -log10(p) vs S₂ value, top hits annotated
  (B) ELANE rank comparison: S₁ vs S₂ vs Combined z
  (C) Method summary: AUROC + ELANE p + n_sig
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300,
                      'font.family': 'sans-serif'})

# Load calibrated S₂ results
res_s2 = pd.read_csv("scripts/norman2019_prt_s2_calibrated.csv")
# Load S₁ results from prt_s1_summary context (regenerate if needed)
from pgaa.core.prt import prt_s1_test
import scanpy as sc
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score

np.random.seed(42)
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

print("Running S₁ (Wasserstein) ...", flush=True)
res_s1 = prt_s1_test(X, genes, "CEBPE", cebpe_pert, ctrl_idx, n_perms=2000,
                     cell_type=cell_type, library_size=lib_size)
print("Done.", flush=True)

cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                 "PRTN3", "DEFA1", "RNASE2"]

# ── Figure: 3 panels ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

# Panel A: Volcano (-log10 p vs S₂ value)
ax = axes[0]
is_known = res_s2["gene"].isin(cebpe_targets).values
ax.scatter(res_s2.loc[~is_known, "S2"],
           -np.log10(res_s2.loc[~is_known, "p_value_perm"].fillna(1.0) + 1e-300),
           s=6, color='gray', alpha=0.4, label='Other genes')
ax.scatter(res_s2.loc[is_known, "S2"],
           -np.log10(res_s2.loc[is_known, "p_value_perm"].fillna(1.0) + 1e-300),
           s=60, color='#E91E63', edgecolor='black', linewidth=0.5,
           label='Known targets (n=9)', zorder=5)
for _, row in res_s2[is_known].iterrows():
    ax.annotate(row["gene"], (row["S2"], -np.log10(row["p_value_perm"] + 1e-300)),
                fontsize=8, ha='left', va='bottom',
                xytext=(3, 3), textcoords='offset points')
ax.axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=1, alpha=0.5)
ax.set_xlabel("S₂ (persistence landscape distance)")
ax.set_ylabel("-log₁₀(p)")
ax.set_title("(A) S₂ on Norman 2019 CEBPE")
ax.legend(frameon=False, fontsize=8, loc='lower right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel B: ELANE rank comparison (bar chart)
ax = axes[1]
methods = ['S₁\nWasserstein', 'S₂\nTDA', 'Combined\nz=(z₁+z₂)/√2']
ranks = []
s1_rank = (res_s1.sort_values("p_value_perm")["gene"]
           .tolist().index("ELANE") + 1) if "ELANE" in res_s1["gene"].values else 0
s2_rank = (res_s2["gene"].tolist().index("ELANE") + 1) if "ELANE" in res_s2["gene"].values else 0
from scipy.stats import norm
s1 = res_s1.set_index("gene")["p_value_perm"].fillna(1.0)
s2 = res_s2.set_index("gene")["p_value_perm"].fillna(1.0)
common = s1.index.intersection(s2.index)
z1 = norm.ppf(1 - s1.loc[common].values)
z2 = norm.ppf(1 - s2.loc[common].values)
p_comb = 1 - norm.cdf((z1 + z2) / np.sqrt(2))
comb_rank = (pd.Series(p_comb, index=common).sort_values()
             .index.tolist().index("ELANE") + 1) if "ELANE" in common else 0
ranks = [s1_rank, s2_rank, comb_rank]
colors = ['#FF9800', '#2196F3', '#4CAF50']
bars = ax.bar(methods, ranks, color=colors, edgecolor='black', linewidth=0.5)
for i, (r, c) in enumerate(zip(ranks, colors)):
    ax.text(i, r + 30, f'#{r}', ha='center', fontsize=10, fontweight='bold')
ax.axhline(2000, color='red', linestyle='--', linewidth=1, alpha=0.5,
           label='n_genes=2012')
ax.set_ylabel("ELANE rank (lower = better)")
ax.set_title("(B) ELANE rank by method")
ax.set_ylim(0, 2200)
ax.legend(frameon=False, fontsize=8, loc='upper right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel C: Summary table
ax = axes[2]
ax.axis('off')
auroc_s1 = roc_auc_score(
    res_s1["gene"].isin(cebpe_targets).astype(int).values,
    -np.log10(res_s1["p_value_perm"].fillna(1.0).values + 1e-300))
auroc_s2 = roc_auc_score(
    res_s2["gene"].isin(cebpe_targets).astype(int).values,
    -np.log10(res_s2["p_value_perm"].fillna(1.0).values + 1e-300))
is_known_c = np.array([g in cebpe_targets for g in common])
auroc_comb = roc_auc_score(is_known_c, -np.log10(p_comb + 1e-300))

table_data = [
    ['S₁ Wasserstein', f'{s1_rank}', f'{res_s1[res_s1["gene"]=="ELANE"]["p_value_perm"].iloc[0]:.3f}',
     f'{auroc_s1:.3f}', f'{(res_s1["p_value_perm"]<0.05).sum()}'],
    ['S₂ TDA (cal.)', f'{s2_rank}', f'{res_s2[res_s2["gene"]=="ELANE"]["p_value_perm"].iloc[0]:.3f}',
     f'{auroc_s2:.3f}', f'{(res_s2["p_value_perm"]<0.05).sum()}'],
    ['Combined z', f'{comb_rank}', f'{p_comb[common=="ELANE"][0]:.3f}',
     f'{auroc_comb:.3f}', f'{(p_comb<0.05).sum()}'],
]
table = ax.table(cellText=table_data,
                 colLabels=['Method', 'ELANE\nrank', 'ELANE p', 'AUROC', 'n_sig\np<0.05'],
                 loc='center', cellLoc='center',
                 colWidths=[0.28, 0.18, 0.18, 0.18, 0.18])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)
for i in range(1, 4):
    table[i, 0].set_facecolor(['#FFE0B2', '#BBDEFB', '#C8E6C9'][i-1])
ax.set_title("(C) Summary: Norman 2019 CEBPE", pad=20)

plt.tight_layout()
out_path = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
            "scripts/figure_norman_prt.tif")
plt.savefig(out_path, format='tiff', dpi=300, bbox_inches='tight')
print(f"Figure saved: {out_path}")
