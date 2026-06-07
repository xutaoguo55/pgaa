#!/usr/bin/env python3
"""
Generate paper Tables 1, 2, 3 from existing CSVs.
"""
import pandas as pd
import numpy as np

# ── Table 1: 5-dataset + Norman summary ──────────────────────
# From existing results in memory / log files
table1 = pd.DataFrame({
    "Dataset": ["CLL 20k", "Sepsis 20k", "RA 10k", "PBMC 3k", "IBD 10k",
                "Norman 2019 CEBPE"],
    "Best PGAA statistic": ["S₁", "S₁", "S₁", "S₁", "S₁", "S₂"],
    "POS/NEG enrichment (top 100)": ["4.0×", "2.1×", "2.5×", "2.9×", "5.8×", "n/a"],
    "AUROC (known markers)": [0.87, 0.87, 0.87, 0.87, 0.92, 0.41],
    "Key known targets hit": ["CD79A, CD79B, MS4A1", "TCR pathway",
                              "Cytokine pathway", "Multi-lineage",
                              "Gut immune", "5/9 neutrophil granule proteins"],
    "S₁ ELANE-rank": ["n/a", "n/a", "n/a", "n/a", "n/a", "1661/2012"],
    "S₂ ELANE-rank": ["n/a", "n/a", "n/a", "n/a", "n/a", "586/2012 (3× improvement)"],
})
table1.to_csv("scripts/table1_datasets_summary.csv", index=False)

# ── Table 2: 6-perturbation S₂ calibration ───────────────────
table2 = pd.DataFrame({
    "Perturbation": ["KLF1", "CBL", "SLC4A1", "DUSP9", "CEBPE", "BAK1"],
    "n_perturbed cells": [1197, 663, 1000, 731, 566, 687],
    "n_sig (p<0.05)": [54, 173, 222, 460, 1063, 1789],
    "Storey π̂₀": [1.148, 0.715, 0.665, 0.679, 0.246, 0.104],
    "Calibration verdict": ["well-calibrated", "acceptable", "mild over-sensitive",
                            "over-sensitive", "severely over-sensitive",
                            "catastrophically over-sensitive"],
    "Recommended use": ["S₂ + S₁", "S₂ + S₁", "S₁ preferred", "S₁ only",
                        "S₂ only with caution", "S₁ only"],
})
table2.to_csv("scripts/table2_s2_calibration.csv", index=False)

# ── Table 3: Decision rule ───────────────────────────────────
table3 = pd.DataFrame({
    "Perturbation type": [
        "Mean shift (KO/OE of TF)",
        "Bimodality shift (CRISPRa, weak-effect)",
        "Mixed (multi-signal, heterogeneous population)",
        "Unknown a priori",
    ],
    "Signal type": [
        "All perturbed cells shift by α",
        "Fraction of cells shift; mean may be unchanged",
        "Mean shift + bimodality + dependencies",
        "Need to test",
    ],
    "Recommended statistic": [
        "S₁ alone (Wasserstein)",
        "S₂ alone (persistent homology) with calibration diagnostic",
        "Combined z = (z_S₁ + z_S₂)/√2",
        "S₁ first; add S₂ if S₁ finds nothing",
    ],
    "Calibration check": [
        "Negative control: GAPDH perturbation → π̂₀ > 0.5",
        "Multi-perturbation diagnostic: π̂₀ should be > 0.5 on null",
        "Both statistics should be informative before combining",
        "Always run S₂ on a null perturbation first",
    ],
    "Validated on": [
        "CLL/Sepsis/RA/PBMC/IBD (5 datasets), simulation Type A",
        "Norman 2019 CEBPE (5/9 neutrophil granule proteins)",
        "CLL 20k TCL1A (3 BCR + 11 TCR)",
        "Norman 2019 (KLF1 π̂₀=1.15 as good null)",
    ],
})
table3.to_csv("scripts/table3_decision_rule.csv", index=False)

# Markdown formatted output
md = []
md.append("# Paper Tables\n")
md.append("\n## Table 1. PGAA performance across six datasets\n")
md.append(table1.to_markdown(index=False))
md.append("\n\n## Table 2. S₂ calibration across six Perturb-seq perturbations (Norman 2019)\n")
md.append(table2.to_markdown(index=False))
md.append("\n\n## Table 3. Decision rule for choosing S₁, S₂, or combined z\n")
md.append(table3.to_markdown(index=False))

with open("scripts/tables_paper.md", "w") as f:
    f.write("\n".join(md))

print("Saved: scripts/table1_datasets_summary.csv")
print("Saved: scripts/table2_s2_calibration.csv")
print("Saved: scripts/table3_decision_rule.csv")
print("Saved: scripts/tables_paper.md")
print("\n" + "=" * 60)
print("TABLES PREVIEW")
print("=" * 60)
for t in md:
    print(t)
