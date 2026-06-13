#!/usr/bin/env python3
"""
Figure: S₂ calibration varies wildly across perturbation types.

This is the HONEST contribution: TDA on Perturb-seq data can be
over-sensitive. We quantify this with 6 different perturbations and
show that the same S₂ implementation gives π̂₀ from 0.10 to 1.15
depending on the perturbation.

Panel:
  (A) n_sig vs π̂₀ for 6 perturbations (with KLF1 as ideal)
  (B) CEBPE target gene p-values across 6 perturbations (showing
      that ELANE/LYZ/MPO are 'sig' in multiple non-CEBPE perturbations)
  (C) Top 30 S₂ hits colored by perturbation overlap
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300})

# Hand-curated data from the 6-target run
results = {
    "KLF1":    {"n_sig": 54,   "pi0": 1.148, "n_pert": 1197, "type": "clean unimodal"},
    "CBL":     {"n_sig": 173,  "pi0": 0.715, "n_pert": 663,  "type": "clean"},
    "SLC4A1":  {"n_sig": 222,  "pi0": 0.665, "n_pert": 1000, "type": "mild bimodal"},
    "DUSP9":   {"n_sig": 460,  "pi0": 0.679, "n_pert": 731,  "type": "mixed"},
    "CEBPE":   {"n_sig": 1063, "pi0": 0.246, "n_pert": 566,  "type": "CRISPRa bimodal"},
    "BAK1":    {"n_sig": 1789, "pi0": 0.104, "n_pert": 687,  "type": "severe bimodal"},
}
df = pd.DataFrame(results).T
df.index.name = "target"
df = df.reset_index()
df = df.sort_values("n_sig")

cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                 "PRTN3", "DEFA1", "RNASE2"]
# From the multi-target log
p_table = {
    "ELANE":  {"CEBPE": 0.005, "KLF1": 0.697, "SLC4A1": 0.159, "BAK1": 0.005, "DUSP9": 0.901, "CBL": 0.577},
    "LYZ":    {"CEBPE": 0.005, "KLF1": 0.851, "SLC4A1": 0.005, "BAK1": 0.005, "DUSP9": 0.050, "CBL": 0.244},
    "MPO":    {"CEBPE": 0.005, "KLF1": 0.488, "SLC4A1": 0.672, "BAK1": 0.005, "DUSP9": 0.428, "CBL": 0.239},
    "AZU1":   {"CEBPE": 0.060, "KLF1": 0.741, "SLC4A1": 0.562, "BAK1": 0.005, "DUSP9": 0.289, "CBL": 0.249},
    "GFI1":   {"CEBPE": 0.886, "KLF1": 0.716, "SLC4A1": 0.423, "BAK1": 0.005, "DUSP9": 0.632, "CBL": 0.309},
    "CTSG":   {"CEBPE": 0.070, "KLF1": 0.373, "SLC4A1": 0.259, "BAK1": 0.119, "DUSP9": 0.229, "CBL": 0.463},
    "PRTN3":  {"CEBPE": 0.622, "KLF1": 0.612, "SLC4A1": 0.766, "BAK1": 0.254, "DUSP9": 0.323, "CBL": 0.731},
    "DEFA1":  {"CEBPE": 0.517, "KLF1": 0.224, "SLC4A1": 0.413, "BAK1": 0.532, "DUSP9": 0.448, "CBL": 0.184},
    "RNASE2": {"CEBPE": 0.189, "KLF1": 0.090, "SLC4A1": 0.259, "BAK1": 0.005, "DUSP9": 0.269, "CBL": 0.065},
}

# ── Figure: 3 panels ──────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel A: n_sig vs π̂₀ scatter
ax = axes[0]
colors = ['#4CAF50' if t['pi0'] >= 0.9 else ('#FFC107' if t['pi0'] >= 0.5 else '#F44336')
          for _, t in df.iterrows()]
sizes = [t['n_pert'] / 4 for _, t in df.iterrows()]
ax.scatter(df["n_sig"], df["pi0"], s=sizes, c=colors, edgecolor='black', linewidth=1, alpha=0.8)
for _, t in df.iterrows():
    ax.annotate(t["target"], (t["n_sig"], t["pi0"]),
                fontsize=10, fontweight='bold', ha='center', va='center')
ax.axhline(1.0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Ideal π̂₀=1')
ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='Acceptable π̂₀=0.5')
ax.set_xlabel("# sig (p<0.05)")
ax.set_ylabel("π̂₀ (Storey)")
ax.set_title("(A) S₂ calibration across 6 perturbations")
ax.set_xscale('log')
ax.set_ylim(-0.1, 1.4)
ax.legend(frameon=False, fontsize=8, loc='lower right')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# Add color legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#4CAF50', label='Well-calibrated (π̂₀≥0.9)'),
    Patch(facecolor='#FFC107', label='Acceptable (0.5≤π̂₀<0.9)'),
    Patch(facecolor='#F44336', label='Over-sensitive (π̂₀<0.5)'),
]
ax.legend(handles=legend_elements, frameon=False, fontsize=8, loc='upper right')

# Panel B: heatmap of CEBPE target p-values across perturbations
ax = axes[1]
genes_order = cebpe_targets
targets_order = ["CEBPE", "KLF1", "SLC4A1", "DUSP9", "CBL", "BAK1"]
mat = np.zeros((len(genes_order), len(targets_order)))
for i, g in enumerate(genes_order):
    for j, t in enumerate(targets_order):
        mat[i, j] = p_table[g][t]
im = ax.imshow(mat, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=0.5)
ax.set_xticks(range(len(targets_order)))
ax.set_xticklabels(targets_order, rotation=30, ha='right', fontsize=9)
ax.set_yticks(range(len(genes_order)))
ax.set_yticklabels(genes_order, fontsize=9)
ax.set_title("(B) CEBPE 'target' genes: p across 6 perturbations", pad=10)
# Annotate sig ones
for i in range(len(genes_order)):
    for j in range(len(targets_order)):
        v = mat[i, j]
        mark = "*" if v < 0.05 else ""
        ax.text(j, i, f"{v:.2f}{mark}", ha='center', va='center',
                fontsize=7, color='black')
cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
cbar.set_label("p-value", fontsize=8)
# Mark CEBPE column without colliding with the panel title.
ax.axvline(0.5, color='red', linewidth=2, alpha=0.3)
ax.text(
    0.06, -0.28, "real target",
    transform=ax.transAxes,
    color='red',
    fontsize=8,
    ha='left',
    va='top',
    clip_on=False,
)

# Panel C: how many CEBPE 'target' genes are sig (p<0.05) in each perturbation
ax = axes[2]
n_sig_per_target = {t: sum(1 for g in cebpe_targets if p_table[g][t] < 0.05) for t in targets_order}
bars = ax.bar(range(len(targets_order)),
              [n_sig_per_target[t] for t in targets_order],
              color=['#F44336' if t == 'CEBPE' else '#2196F3' for t in targets_order],
              edgecolor='black', linewidth=0.5)
for i, (t, n) in enumerate(n_sig_per_target.items()):
    ax.text(i, n + 0.15, str(n), ha='center', fontsize=10, fontweight='bold')
ax.set_xticks(range(len(targets_order)))
ax.set_xticklabels(targets_order, rotation=30, ha='right', fontsize=9)
ax.set_ylabel("# CEBPE 'target' genes sig (p<0.05)")
ax.set_ylim(0, 9)
ax.axhline(9, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.set_title("(C) CEBPE target leakage across perturbations")
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.suptitle("S₂ calibration: perturbation-specific variability (Norman 2019)",
             fontsize=13, y=1.02)
plt.tight_layout()
out = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
       "scripts/figure_s2_calibration_multitarget.tif")
plt.savefig(out, format='tiff', dpi=300, bbox_inches='tight')
print(f"Saved: {out}")
print("\nThis figure replaces the broken 'S₂ succeeds' narrative.")
print("It documents S₂'s calibration problem as a contribution: users should")
print("always run multiple perturbation controls before trusting S₂ on new data.")
