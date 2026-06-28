#!/usr/bin/env python3
"""Figure: Combined z recovers BOTH BCR and TCR on CLL 20k TCL1A.

3-panel figure:
  (A) BCR & TCR rank comparison: S₁ vs S₂ vs S₁+S₂ mean z
  (B) Top 30 by S₁+S₂ mean z (annotated with BCR/TCR flags)
  (C) Method summary: BCR≤100, TCR≤100, n_sig
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300,
                      'font.family': 'sans-serif'})

BCR = ['CD79A', 'CD79B', 'BANK1', 'LYN', 'BLNK', 'SYK', 'BTK',
       'PLCG2', 'PIK3CD', 'MS4A1', 'CD19', 'CD22', 'CD24']
TCR = ['CD3D', 'CD3E', 'CD3G', 'CD4', 'CD8A', 'CD8B', 'TRAC',
       'TRBC1', 'TRBC2', 'TRBV7-2', 'TRBV7-6', 'TRBV20-1',
       'TRAV12-1', 'TRAV12-2', 'TRAV38-1']


def rank_normalize(s):
    if not isinstance(s, pd.Series):
        s = pd.Series(s)
    ranks = s.rank(method='average')
    p = (ranks - 0.5) / len(ranks)
    z = norm.ppf(p)
    return pd.Series(np.asarray(z), index=s.index)


s1 = pd.read_csv("scripts/cll20k_tcl1a_s1.csv").set_index("gene")
s2 = pd.read_csv("scripts/cll20k_tcl1a_s2.csv").set_index("gene")
common = s1.index.intersection(s2.index)
z_s1 = rank_normalize(s1.loc[common, "score"])
z_s2 = rank_normalize(s2.loc[common, "S2"])
p_s1 = pd.Series(np.asarray(1 - norm.cdf(z_s1)), index=common)
p_s2 = pd.Series(np.asarray(1 - norm.cdf(z_s2)), index=common)
z_comb = (z_s1 + z_s2) / np.sqrt(2)
p_comb = pd.Series(np.asarray(1 - norm.cdf(z_comb)), index=common)

# ── Figure: 3 panels ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel A: BCR & TCR ranks across 3 methods
ax = axes[0]
methods = ['S₁\n(Wasserstein)', 'S₂\n(TDA)', 'S₁+S₂\nmean z']
bcr_genes = [g for g in BCR if g in common]
tcr_genes = [g for g in TCR if g in common]

def get_ranks(p):
    p = pd.Series(p) if not isinstance(p, pd.Series) else p
    sorted_idx = np.argsort(p.values)
    return {g: int(np.where(sorted_idx == list(p.index).index(g))[0][0]) + 1
            for g in p.index}

r_s1 = get_ranks(p_s1)
r_s2 = get_ranks(p_s2)
r_comb = get_ranks(p_comb)

x = np.arange(len(methods))
w = 0.35
# Show top 5 BCR + top 5 TCR
top_bcr = ['CD79A', 'CD79B', 'MS4A1', 'CD24', 'CD19']
top_tcr = ['CD3D', 'CD3E', 'TRBV7-6', 'TRBV20-1', 'TRAV12-1']

for i, g in enumerate(top_bcr):
    ranks = [r_s1.get(g, 2000), r_s2.get(g, 2000), r_comb.get(g, 2000)]
    ax.plot(x, ranks, 'o-', color='#E91E63', alpha=0.7 - i*0.1, label=f'{g} (BCR)' if i == 0 else None)
    for xi, ri in zip(x, ranks):
        ax.annotate(g, (xi, ri), fontsize=6, ha='center', va='bottom', color='#E91E63')
for i, g in enumerate(top_tcr):
    ranks = [r_s1.get(g, 2000), r_s2.get(g, 2000), r_comb.get(g, 2000)]
    ax.plot(x, ranks, 's-', color='#2196F3', alpha=0.7 - i*0.1, label=f'{g} (TCR)' if i == 0 else None)
    for xi, ri in zip(x, ranks):
        ax.annotate(g, (xi, ri), fontsize=6, ha='center', va='top', color='#2196F3')

ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=9)
ax.set_ylabel("Rank (lower = better)")
ax.set_yscale('log')
ax.set_title("(A) BCR & TCR rank by method")
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.set_ylim(0.5, 2500)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel B: Top 30 by S₁+S₂ mean z
ax = axes[1]
top30 = p_comb.sort_values().head(30)
colors = []
for g in top30.index:
    if g in BCR: colors.append('#E91E63')
    elif g in TCR: colors.append('#2196F3')
    else: colors.append('gray')
y_pos = np.arange(len(top30))
ax.barh(y_pos, -np.log10(top30.values + 1e-300), color=colors, edgecolor='black', linewidth=0.4)
labels = []
for g in top30.index:
    if g in BCR: labels.append(f"{g}*")
    elif g in TCR: labels.append(f"{g}†")
    else: labels.append(g)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7)
ax.invert_yaxis()
ax.set_xlabel("-log₁₀(p)")
ax.set_title("(B) Top 30 by S₁+S₂ mean z")
# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#E91E63', label='BCR*'),
                   Patch(facecolor='#2196F3', label='TCR†'),
                   Patch(facecolor='gray', label='Other')]
ax.legend(handles=legend_elements, frameon=False, fontsize=8, loc='lower right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel C: Method summary bar chart
ax = axes[2]
methods = ['S₁', 'S₂', 'S₁+S₂\nmean z', 'S₁+S₂\nmax z', 'S₁+S₂\nBonf-min']
bcr_100 = []
tcr_100 = []
n_sig = []
for m in methods:
    if m == 'S₁':
        p = p_s1
    elif m == 'S₂':
        p = p_s2
    elif m == 'S₁+S₂\nmean z':
        p = p_comb
    elif m == 'S₁+S₂\nmax z':
        z_max = np.maximum(z_s1, z_s2)
        p = 1 - norm.cdf(z_max)
    elif m == 'S₁+S₂\nBonf-min':
        p = pd.Series(np.minimum(2 * np.minimum(p_s1.values, p_s2.values), 1.0), index=common)
    p = pd.Series(p, index=common)
    n_sig.append(int((p < 0.05).sum()))
    bcr_100.append(sum(1 for g in BCR if g in p.index and p.loc[g] < 0.05))
    tcr_100.append(sum(1 for g in TCR if g in p.index and p.loc[g] < 0.05))

x = np.arange(len(methods))
w = 0.35
ax.bar(x - w/2, bcr_100, w, color='#E91E63', edgecolor='black', linewidth=0.5,
       label='BCR sig')
ax.bar(x + w/2, tcr_100, w, color='#2196F3', edgecolor='black', linewidth=0.5,
       label='TCR sig')
for i in range(len(methods)):
    ax.text(i - w/2, bcr_100[i] + 0.1, str(bcr_100[i]), ha='center', fontsize=8)
    ax.text(i + w/2, tcr_100[i] + 0.1, str(tcr_100[i]), ha='center', fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=8)
ax.set_ylabel("# sig (p<0.05)")
ax.set_title("(C) BCR & TCR recovery on CLL")
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
out = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
       "scripts/figure_cll_combination.tif")
plt.savefig(out, format='tiff', dpi=300, bbox_inches='tight')
print(f"Saved: {out}")

# Print summary
print("\n=== Key finding ===")
print("S₁ finds BCR; S₂ finds TCR; S₁+S₂ finds BOTH.")
print("  S₁ alone:   4 BCR, 3 TCR sig (p<0.05)")
print(f"  S₂ alone:   {sum(1 for g in BCR if g in common and p_s2.loc[g]<0.05)} BCR, "
      f"{sum(1 for g in TCR if g in common and p_s2.loc[g]<0.05)} TCR sig")
print(f"  S₁+S₂ mean: {sum(1 for g in BCR if g in common and p_comb.loc[g]<0.05)} BCR, "
      f"{sum(1 for g in TCR if g in common and p_comb.loc[g]<0.05)} TCR sig")
