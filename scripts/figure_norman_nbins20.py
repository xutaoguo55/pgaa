#!/usr/bin/env python3
"""
Figure 2: Norman 2019 CEBPE with n_bins=20.

Key result: ELANE rank 1452 (PGAA-W) to 57 (PGAA-H), upper-tail ratio = 1.32.

3 panels:
  (A) PGAA-H ranking plot: -log10(p) vs PGAA-H value, annotated top hits
  (B) ELANE rank comparison: SCEPTRE (1761) vs PGAA-W (1452) vs PGAA-H (57)
  (C) Summary table with calibration metrics
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300})

# Load n_bins=20 PGAA-H results
s2 = pd.read_csv("scripts/norman2019_prt_s2_nbins20.csv")
s1_full = pd.read_csv("scripts/norman2019_prt_s1_full.csv")

cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                 "PRTN3", "DEFA1", "RNASE2"]
is_known = s2["gene"].isin(cebpe_targets).values

# Metrics from the n_bins=20 run
s2_elane_rank = 57
s2_elane_p = 0.04
s2_nsig = 66
s2_pi0 = 1.32

# PGAA-W metrics from the current full rerun.
s1_p = s1_full["p_value_perm"].fillna(1.0).astype(float)
s1_ranks = s1_p.rank(method="min", ascending=True).astype(int)
s1_elane_idx = s1_full.index[s1_full["gene"] == "ELANE"][0]
s1_elane_rank = int(s1_ranks.loc[s1_elane_idx])
s1_elane_p = float(s1_p.loc[s1_elane_idx])
s1_auroc = roc_auc_score(
    s1_full["gene"].isin(cebpe_targets).values,
    -np.log10(s1_p.values + 1e-300),
)
s1_nsig = int((s1_p < 0.05).sum())

# SCEPTRE metrics
sceptre_elane_rank = 1761
sceptre_elane_p = 0.92
sceptre_auroc = 0.469

# AUROC for PGAA-H n_bins=20
s2_auroc = roc_auc_score(
    is_known, -np.log10(s2["p_value_perm"].fillna(1.0).values + 1e-300)
)

# ── Figure ──
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A: PGAA-H ranking plot
ax = axes[0]
ax.scatter(s2.loc[~is_known, "S2"],
           -np.log10(s2.loc[~is_known, "p_value_perm"].fillna(1.0) + 1e-300),
           s=6, color='gray', alpha=0.3, label='Other genes')
ax.scatter(s2.loc[is_known, "S2"],
           -np.log10(s2.loc[is_known, "p_value_perm"].fillna(1.0) + 1e-300),
           s=80, color='#E91E63', edgecolor='black', linewidth=0.5,
           label=f'Known targets (n={sum(is_known)})', zorder=5)
for _, row in s2[is_known].iterrows():
    ax.annotate(row["gene"],
                (row["S2"], -np.log10(row["p_value_perm"] + 1e-300)),
                fontsize=9, ha='left', va='bottom',
                xytext=(3, 3), textcoords='offset points', fontweight='bold')
ax.axhline(-np.log10(0.05), color='red', linestyle='--', linewidth=1, alpha=0.5,
           label='p=0.05')
ax.set_xlabel("PGAA-H histogram-shape diagnostic")
ax.set_ylabel("-log₁₀(p)")
ax.set_title("(A) PGAA-H on Norman 2019 CEBPE (n_bins=20)")
ax.legend(frameon=False, fontsize=8, loc='lower right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel B: ELANE rank comparison (bar chart)
ax = axes[1]
methods = ['SCEPTRE', 'PGAA-W\nWasserstein', 'PGAA-H\nhistogram-shape']
ranks = [sceptre_elane_rank, s1_elane_rank, 57]
p_vals = [sceptre_elane_p, s1_elane_p, s2_elane_p]
colors = ['#9E9E9E', '#FF9800', '#2196F3']
bars = ax.bar(methods, ranks, color=colors, edgecolor='black', linewidth=0.5)
for i, (r, p) in enumerate(zip(ranks, p_vals)):
    ax.text(i, r + 40, f'rank {r}\np={p:.2f}', ha='center', fontsize=10,
            fontweight='bold')
ax.axhline(2012, color='black', linestyle=':', linewidth=1, alpha=0.5,
           label=f'n_genes = 2012')
ax.set_ylabel("ELANE rank (lower = better)")
ax.set_title("(B) ELANE rank improvement")
ax.set_ylim(0, 2100)
ax.legend(frameon=False, fontsize=8, loc='upper right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
# Improvement label above the PGAA-H bar
improvement = int(s1_elane_rank / 57)
ax.text(2, 57 - 80, f'{improvement}× better', ha='center', fontsize=11,
        color='#1565C0', fontweight='bold')

# Panel C: Summary table
ax = axes[2]
ax.axis('off')
table_data = [
    ['Method', 'ELANE rank', 'ELANE p', 'n_sig', 'Calibration'],
    ['SCEPTRE', f'{sceptre_elane_rank}', f'{sceptre_elane_p:.2f}',
     '30', f'AUROC={sceptre_auroc:.2f}'],
    ['PGAA-W', f'{s1_elane_rank}', f'{s1_elane_p:.2f}',
     f'{s1_nsig}', f'AUROC={s1_auroc:.2f}'],
    ['PGAA-H (n_bins=20)', f'57', f'{s2_elane_p:.2f}',
     f'{s2_nsig}', f'R_lambda={s2_pi0:.2f}'],
]
table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                 colWidths=[0.35, 0.18, 0.18, 0.12, 0.18])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)
# Color header
for j in range(5):
    table[0, j].set_facecolor('#455A64')
    table[0, j].set_text_props(color='white', fontweight='bold')
# Highlight PGAA-H row
for j in range(5):
    table[3, j].set_facecolor('#C8E6C9')
ax.set_title("(C) Method comparison on ELANE", pad=20)

plt.tight_layout()
out = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
       "scripts/figure_norman_nbins20.tif")
plt.savefig(out, format='tiff', dpi=300, bbox_inches='tight')
print(f"Saved: {out}")
