#!/usr/bin/env python3
"""Figure: S₁ vs S₂ vs Combined z power across perturbation types."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
                      'legend.fontsize': 9, 'figure.dpi': 300})

df = pd.read_csv("scripts/simulation_powers.csv")
thetas = sorted(df["theta"].unique())
types = ["A", "B", "C"]
type_names = {"A": "Mean shift", "B": "Bimodality shift", "C": "Both"}

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)

for ax, ptype in zip(axes, types):
    sub = df[df["type"] == ptype]
    s1_mean = [sub[sub["theta"] == t]["TPR_S1"].mean() for t in thetas]
    s2_mean = [sub[sub["theta"] == t]["TPR_S2"].mean() for t in thetas]
    cb_mean = [sub[sub["theta"] == t]["TPR_comb"].mean() for t in thetas]
    s1_se = [sub[sub["theta"] == t]["TPR_S1"].std() / np.sqrt(3) for t in thetas]
    s2_se = [sub[sub["theta"] == t]["TPR_S2"].std() / np.sqrt(3) for t in thetas]
    cb_se = [sub[sub["theta"] == t]["TPR_comb"].std() / np.sqrt(3) for t in thetas]

    ax.errorbar(thetas, s1_mean, yerr=s1_se, marker='o', color='#FF9800',
                linewidth=2, capsize=3, label='S₁ (Wasserstein)')
    ax.errorbar(thetas, s2_mean, yerr=s2_se, marker='s', color='#2196F3',
                linewidth=2, capsize=3, label='S₂ (TDA)')
    ax.errorbar(thetas, cb_mean, yerr=cb_se, marker='^', color='#4CAF50',
                linewidth=2, capsize=3, label='S₁+S₂ mean z')
    ax.set_xlabel("Effect size θ (log-FC)")
    ax.set_title(f"({['A','B','C'].index(ptype)+1}) {ptype}: {type_names[ptype]}")
    ax.set_ylim(-0.05, 1.1)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.3)
    if ax is axes[0]:
        ax.set_ylabel("TPR @ FPR=0.05")
        ax.legend(frameon=False, fontsize=8, loc='lower right')

plt.tight_layout()
out = ("/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/"
       "scripts/figure_simulation_powers.tif")
plt.savefig(out, format='tiff', dpi=300, bbox_inches='tight')
print(f"Saved: {out}")

# Final takeaway
print("\n=== Honest takeaway ===")
print("S₁ dominates across all perturbation types in this simulation.")
print("S₂ alone is weak (TPR < 0.4 even at θ=1.0).")
print("Combined z is intermediate — never best, never worst.")
print()
print("The 'S₂ advantage' seen in Norman 2019 CEBPE happens only when S₁")
print("is completely blind (p=0.84, 0/9 hits) — i.e., when the perturbation")
print("truly leaves no mean shift. In that pathological case, S₂ is the")
print("only viable method. The Combined z helps in mid-range cases where")
print("S₁ is partially informative.")
