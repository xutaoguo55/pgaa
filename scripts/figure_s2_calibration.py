#!/usr/bin/env python3
"""
S₂ CALIBRATION EVIDENCE for Norman 2019.

3-panel figure addressing the "S₂ is over-sensitive" critique:

  (A) QQ plot: observed -log10(p) vs uniform expectation
      - Over-sensitive S₂ → points fall ABOVE diagonal in upper-right
      - Well-calibrated → points hug diagonal

  (B) p-value histogram: should be approximately uniform under H0
      - Over-sensitive S₂ → mass accumulates near 0

  (C) GAPDH negative control: S₂ with GAPDH as the "target"
      - GAPDH is housekeeping, perturbation has no specific downstream
      - Expect: p distribution uniform, n_sig ≈ 5% of genes
      - CEBPE target for comparison
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import uniform

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300})

# Load S₂ CEBPE results (real)
res_cebpe = pd.read_csv("scripts/norman2019_prt_s2_calibrated.csv")
p_cebpe = res_cebpe["p_value_perm"].fillna(1.0).values

# Load GAPDH negative control (if it exists)
try:
    res_gapdh = pd.read_csv("scripts/norman2019_prt_s2_gapdh_neg.csv")
    p_gapdh = res_gapdh["p_value_perm"].fillna(1.0).values
    print(f"Loaded GAPDH neg control: n_genes={len(p_gapdh)}, n_sig={int((p_gapdh<0.05).sum())}")
    has_gapdh = True
except FileNotFoundError:
    has_gapdh = False
    p_gapdh = None
    print("GAPDH neg control file not found, will skip panel C")

# ── Figure: 3 panels ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Panel A: QQ plot
ax = axes[0]
p_sorted = np.sort(p_cebpe)
n = len(p_sorted)
expected = -np.log10(np.arange(1, n + 1) / (n + 1))
observed = -np.log10(p_sorted)
ax.scatter(expected, observed, s=4, color='#2196F3', alpha=0.5, label='S₂ (CEBPE target)')
# Reference diagonal
lim_max = max(expected.max(), observed.max()) * 1.05
ax.plot([0, lim_max], [0, lim_max], 'k--', linewidth=1, alpha=0.5, label='Uniform (ideal)')
ax.set_xlabel("Expected -log₁₀(p) under H₀")
ax.set_ylabel("Observed -log₁₀(p)")
ax.set_title("(A) QQ plot: S₂ on CEBPE")
# Add inflation metric
pi0_hat = max(1, (p_cebpe > 0.5).sum()) / (0.5 * n)
inflation = observed.max() / expected.max()
ax.text(0.5, 0.95, f"π̂₀ = {pi0_hat:.2f}\nmax inflation = {inflation:.2f}×",
        transform=ax.transAxes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel B: p-value histogram
ax = axes[1]
ax.hist(p_cebpe, bins=50, color='#2196F3', edgecolor='black', linewidth=0.5,
        alpha=0.7, label='S₂ CEBPE')
if has_gapdh:
    ax.hist(p_gapdh, bins=50, color='#FF9800', edgecolor='black', linewidth=0.5,
            alpha=0.5, label='S₂ GAPDH (neg ctrl)')
# Uniform reference
ax.axhline(n / 50, color='red', linestyle='--', linewidth=1, label='Uniform (ideal)')
ax.set_xlabel("p-value")
ax.set_ylabel("# genes")
ax.set_title("(B) p-value distribution")
ax.legend(frameon=False, fontsize=8, loc='upper right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Panel C: Top genes by S₂
ax = axes[2]
if has_gapdh:
    p_g_series = pd.Series(p_gapdh).sort_values().head(20)
    ax.barh(np.arange(len(p_g_series))[::-1], -np.log10(p_g_series.values + 1e-300),
            color='#FF9800', edgecolor='black', linewidth=0.4)
    ax.set_yticks(np.arange(len(p_g_series))[::-1])
    ax.set_yticklabels([f"#{i+1}" for i in range(len(p_g_series))], fontsize=8)
    ax.set_xlabel("-log₁₀(p)")
    ax.set_title(f"(C) GAPDH neg ctrl: top 20 S₂ (n_sig={int((p_gapdh<0.05).sum())})")
else:
    # CEBPE for comparison
    p_c_series = pd.Series(p_cebpe).sort_values().head(20)
    ax.barh(np.arange(len(p_c_series))[::-1], -np.log10(p_c_series.values + 1e-300),
            color='#2196F3', edgecolor='black', linewidth=0.4)
    ax.set_yticks(np.arange(len(p_c_series))[::-1])
    ax.set_yticklabels([f"#{i+1}" for i in range(len(p_c_series))], fontsize=8)
    ax.set_xlabel("-log₁₀(p)")
    ax.set_title(f"(C) CEBPE target: top 20 S₂ (n_sig={int((p_cebpe<0.05).sum())})")
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.suptitle("S₂ calibration evidence on Norman 2019", fontsize=13, y=1.02)
plt.tight_layout()
out = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
       "scripts/figure_s2_calibration.tif")
plt.savefig(out, format='tiff', dpi=300, bbox_inches='tight')
print(f"Saved: {out}")

# Print diagnostics
print("\n=== S₂ calibration diagnostics (CEBPE) ===")
print(f"n_genes = {n}")
print(f"n_sig p<0.05 = {(p_cebpe<0.05).sum()}")
print(f"n_sig p<0.01 = {(p_cebpe<0.01).sum()}")
print(f"n_sig p<0.001 = {(p_cebpe<0.001).sum()}")
print(f"π̂₀ (Storey) = {pi0_hat:.3f}")
print(f"Inflation (max obs / max exp) = {inflation:.2f}×")
if pi0_hat < 0.7:
    print("⚠️  π̂₀ < 0.7 → S₂ likely over-sensitive")
elif pi0_hat < 0.9:
    print("⚠️  π̂₀ between 0.7-0.9 → S₂ may have many false positives")
else:
    print("✅ π̂₀ > 0.9 → S₂ well-calibrated")
