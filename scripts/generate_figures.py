#!/usr/bin/env python3
"""D: Generate publication-quality figures for PRT paper."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 600,
                      'font.family': 'sans-serif'})

# ── Figure 1: Multi-dataset POS vs NEG immune hits ─────────
datasets = ['CLL\nB cell', 'Sepsis\nPBMC', 'RA\nPBMC',
            'PBMC\n3k', 'IBD\ngut']
# CLL: verified from cll20k_tcl1a_s1.csv (4 BCR, 1 HK = 4.0x)
# Others: from original pre-computed S1 analysis (to be re-verified)
pos_means = [4.0, 5.1, 6.9, 4.0, 2.9]
neg_means = [1.0, 2.4, 2.8, 1.4, 0.0]
ratios = [4.0, 2.1, 2.5, 2.9, 5.8]
cells = ['36k', '20k', '10k', '2.7k', '10k']

ROOT = Path("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper")
CM_FIG_DIR = ROOT / "COMMUNICATIONS_MEDICINE_TRANSFER" / "figures_png"
CAIC_FIG_DIR = ROOT / "COMMUNICATIONS_AI_COMPUTING_TRANSFER" / "figures_png"

fig, axes = plt.subplots(
    1, 3, figsize=(13.8, 4.4),
    gridspec_kw={"wspace": 0.42},
)

# Panel A: Bar plot POS vs NEG
ax = axes[0]
x = np.arange(len(datasets))
w = 0.35
bars1 = ax.bar(x - w/2, pos_means, w, label='Known markers (POS)',
               color='#2196F3', edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + w/2, neg_means, w, label='Housekeeping (NEG)',
               color='#FF9800', edgecolor='black', linewidth=0.5)
ax.set_ylabel('Known pathway markers\nin top-100 W₁ ranking')
ax.set_xticks(x)
ax.set_xticklabels(datasets, fontsize=8)
ax.legend(frameon=False, fontsize=8)
ax.set_title('a  Marker recovery across datasets', fontsize=11, loc='left', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel B: POS/NEG ratio
ax = axes[1]
colors = ['#4CAF50' if r >= 2.0 else '#FFC107' for r in ratios]
bars = ax.bar(x, ratios, color=colors, edgecolor='black', linewidth=0.5)
ax.axhline(2.0, color='red', linestyle='--', linewidth=1, label='2× threshold')
ax.axhline(1.0, color='gray', linestyle=':', linewidth=1, label='Random (1×)')
ax.set_ylabel('POS / NEG ratio')
ax.set_xticks(x)
ax.set_xticklabels(datasets, fontsize=8)
ax.legend(frameon=False, fontsize=8)
ax.set_title('b  Enrichment ratio', fontsize=11, loc='left', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel C: Method comparison (verified by cll20k_4method.py 2026-06-28)
ax = axes[2]
methods = ['Wasserstein', 't-test', 'PGAA-H', 'S3 (MI)']
pos_bcr = [4.0, 4.0, 0.0, 2.0]
neg_bcr = [1.0, 1.0, 1.0, 1.0]
aurocs = [0.958, 0.966, 0.460, 0.694]
x2 = np.arange(len(methods))
w2 = 0.3
ax2 = ax.twinx()
bars_a = ax.bar(x2 - w2/2, [p/n for p,n in zip(pos_bcr, neg_bcr)],
                w2, label='POS/NEG ratio', color='#2196F3', edgecolor='black', linewidth=0.5)
bars_b = ax2.bar(x2 + w2/2, aurocs, w2, label='AUROC', color='#9C27B0',
                  edgecolor='black', linewidth=0.5, alpha=0.7)
ax.set_ylabel('Ratio')
ax2.set_ylabel('AUROC')
ax.set_xticks(x2); ax.set_xticklabels(methods, fontsize=7)
ax.set_title('c  CLL marker-recovery comparison', fontsize=11, loc='left', fontweight='bold')
ax.set_ylim(0, 7.1)
ax2.set_ylim(0, 1.05)
ax2.spines["right"].set_position(("axes", 1.08))
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(
    lines1 + lines2,
    labels1 + labels2,
    frameon=False,
    fontsize=7,
    loc='upper center',
    bbox_to_anchor=(0.5, 0.98),
    ncol=2,
    borderaxespad=0.2,
)
ax.spines['top'].set_visible(False)

plt.subplots_adjust(left=0.06, right=0.94, bottom=0.20, top=0.88, wspace=0.48)
plt.savefig(ROOT / 'scripts' / 'figure_multidataset.tif',
            format='tiff', dpi=600, bbox_inches='tight')
plt.savefig(ROOT / 'figures_png' / 'figure_1.png',
            format='png', dpi=600, bbox_inches='tight')
plt.savefig(CM_FIG_DIR / 'figure_1.png',
            format='png', dpi=600, bbox_inches='tight')
plt.savefig(CAIC_FIG_DIR / 'figure_1.png',
            format='png', dpi=600, bbox_inches='tight')
print("Figure 1 saved: figure_multidataset.tif")

# ── Figure 2: Sample size stability (CD24 ranking) ────────
sample_sizes = [2000, 5000, 10000, 20000, 36568]
cd24_ranks = {
    'TCL1A': [55, 55, 65, 69, None],
    'LYN':   [62, 62, 60, 61, None],
    'CD79A': [41, 41, 46, 50, None],
}
# Approximation from earlier runs
cd24_pos = [55, 60, 65, 69, 62.5]  # average POS rank
cd24_neg = [387, 387, 269, 214, 150]  # GAPDH rank across N

fig, ax = plt.subplots(1, 1, figsize=(6, 4))
ax.semilogy(sample_sizes[:4], cd24_pos[:4], 'o-', color='#2196F3', linewidth=2,
            markersize=8, label='CD24 rank (TCL1A POS)')
ax.semilogy(sample_sizes[:4], cd24_neg[:4], 's-', color='#FF9800', linewidth=2,
            markersize=8, label='CD24 rank (GAPDH NEG)')
ax.fill_between(sample_sizes[:4], [40]*4, [80]*4, alpha=0.1, color='#2196F3')
ax.fill_between(sample_sizes[:4], [100]*4, [500]*4, alpha=0.1, color='#FF9800')
ax.set_xlabel('Number of cells'); ax.set_ylabel('CD24 rank (log scale)')
ax.legend(frameon=False); ax.set_title('d  Sample size stability', loc='left', fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.set_xlim(1000, 40000)

plt.tight_layout()
plt.savefig('/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/scripts/figure_stability.tif',
            format='tiff', dpi=300, bbox_inches='tight')
print("Figure 2 saved: figure_stability.tif")

print("\n✅ All figures generated.")
