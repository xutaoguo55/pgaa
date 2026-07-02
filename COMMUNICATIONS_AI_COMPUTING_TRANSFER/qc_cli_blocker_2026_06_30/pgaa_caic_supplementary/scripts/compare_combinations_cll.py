#!/usr/bin/env python3
"""
S₁ + S₂ + S₃ combination on CLL 20k TCL1A.

Pre-computed scores available in cll20k_tcl1a_s{1,2,3}.csv.
Convert raw scores to ranks, then test:
  (a) mean z
  (b) max z
  (c) Fisher
  (d) Bonferroni-min
  (e) harmonic mean p
  (f) mean z of S1+S2 (paper-recommended)
  (g) mean z of S1+S2+S3
  (h) S1 alone (baseline)

Validate: BCR markers (CD79A, CD79B, BANK1, LYN, BLNK, SYK, BTK, PLCG2,
PIK3CD, MS4A1, CD19, CD22, CD24) should rank high.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm, chi2
from sklearn.metrics import roc_auc_score

np.random.seed(42)

BCR = ['CD79A', 'CD79B', 'BANK1', 'LYN', 'BLNK', 'SYK', 'BTK',
       'PLCG2', 'PIK3CD', 'MS4A1', 'CD19', 'CD22', 'CD24']
TCR = ['CD3D', 'CD3E', 'CD3G', 'CD4', 'CD8A', 'CD8B', 'TRAC',
       'TRBC1', 'TRBC2', 'TRBV7-2', 'TRBV7-6', 'TRBV20-1',
       'TRAV12-1', 'TRAV12-2', 'TRAV38-1']
KNOWN_IMMUNE = BCR + TCR


def rank_normalize(scores):
    """Convert scores to z-scores via rank-based inverse normal."""
    if not isinstance(scores, pd.Series):
        scores = pd.Series(scores)
    ranks = scores.rank(method='average')
    p = (ranks - 0.5) / len(ranks)
    z = norm.ppf(p)
    return pd.Series(np.asarray(z), index=scores.index)


def main():
    s1 = pd.read_csv("scripts/cll20k_tcl1a_s1.csv").set_index("gene")
    s2 = pd.read_csv("scripts/cll20k_tcl1a_s2.csv").set_index("gene")
    s3 = pd.read_csv("scripts/cll20k_tcl1a_s3.csv").set_index("gene")
    t = pd.read_csv("scripts/cll20k_tcl1a_t.csv").set_index("gene")

    common = s1.index.intersection(s2.index).intersection(s3.index).intersection(t.index)
    print(f"Common genes: {len(common)}")

    # All methods as ranks → z-scores (higher z = more significant)
    z_s1 = rank_normalize(s1.loc[common, "score"]).values
    z_s2 = rank_normalize(s2.loc[common, "S2"]).values
    z_s3 = rank_normalize(s3.loc[common, "S3"]).values
    z_t = rank_normalize(t.loc[common, "score"]).values

    # Convert z to one-sided p (high z = high expression shift)
    p_s1 = 1 - norm.cdf(z_s1)
    p_s2 = 1 - norm.cdf(z_s2)
    p_s3 = 1 - norm.cdf(z_s3)
    p_t = 1 - norm.cdf(z_t)

    is_bcr = np.array([g in BCR for g in common])
    is_tcr = np.array([g in TCR for g in common])
    is_known = np.array([g in KNOWN_IMMUNE for g in common])

    methods = {
        "S₁ (Wasserstein)": (p_s1, z_s1),
        "S₂ (TDA)": (p_s2, z_s2),
        "S₃ (cond MI)": (p_s3, z_s3),
        "t-test": (p_t, z_t),
        "S₁+S₂ mean z": (
            1 - norm.cdf((z_s1 + z_s2) / np.sqrt(2)),
            None,
        ),
        "S₁+S₂+S₃ mean z": (
            1 - norm.cdf((z_s1 + z_s2 + z_s3) / np.sqrt(3)),
            None,
        ),
        "S₁+S₂ max z": (
            1 - norm.cdf(np.maximum(z_s1, z_s2)),
            None,
        ),
        "S₁+S₂ Fisher": (
            1 - chi2.cdf(
                -2 * (np.log(np.maximum(p_s1, 1e-300)) +
                      np.log(np.maximum(p_s2, 1e-300))),
                df=4
            ),
            None,
        ),
        "S₁+S₂ Bonf-min": (
            np.minimum(2 * np.minimum(p_s1, p_s2), 1.0),
            None,
        ),
    }

    print("\n=== CLL 20k TCL1A — method comparison (rank-based z) ===")
    print(f"{'Method':<25} {'CD79A':>8} {'CD79B':>8} {'CD24':>8} "
          f"{'MS4A1':>8} {'TRBV7-6':>10} {'n_sig':>8} {'BCR≤100':>10} {'TCR≤100':>10}")
    rows = []
    for name, (p, z) in methods.items():
        p_series = pd.Series(p, index=common)
        n_sig = int((p < 0.05).sum())
        # Ranks
        order = np.argsort(p)
        ranks = pd.Series(order, index=common)
        bcr_in_top100 = sum(1 for g in BCR if g in common and ranks.loc[g] < 100)
        tcr_in_top100 = sum(1 for g in TCR if g in common and ranks.loc[g] < 100)
        cd79a = int(ranks.loc["CD79A"]) + 1 if "CD79A" in common else None
        cd79b = int(ranks.loc["CD79B"]) + 1 if "CD79B" in common else None
        cd24 = int(ranks.loc["CD24"]) + 1 if "CD24" in common else None
        ms4a1 = int(ranks.loc["MS4A1"]) + 1 if "MS4A1" in common else None
        trbv76 = int(ranks.loc["TRBV7-6"]) + 1 if "TRBV7-6" in common else None
        print(f"{name:<25} {cd79a:>8} {cd79b:>8} {cd24:>8} {ms4a1:>8} "
              f"{trbv76:>10} {n_sig:>8} {bcr_in_top100:>10} {tcr_in_top100:>10}")
        rows.append({
            "method": name, "n_sig": n_sig,
            "BCR_in_top100": bcr_in_top100, "TCR_in_top100": tcr_in_top100,
            "CD79A_rank": cd79a, "CD79B_rank": cd79b, "CD24_rank": cd24,
            "MS4A1_rank": ms4a1, "TRBV7-6_rank": trbv76,
        })
    df = pd.DataFrame(rows)
    df.to_csv("scripts/cll_combination_methods.csv", index=False)
    print(f"\nSaved: scripts/cll_combination_methods.csv")

    # Also: BCR hit rate (rank ≤ 200)
    print("\n=== BCR markers rank ≤ 200 (real AUROC-like metric) ===")
    for name, (p, z) in methods.items():
        p_series = pd.Series(p, index=common).sort_values()
        hits = sum(1 for g in BCR if g in common and p_series.index.get_loc(g) < 200)
        print(f"  {name:<25}: {hits}/13 BCR in top 200")

    # Top 30 by best combined method
    p_best = 1 - norm.cdf((z_s1 + z_s2) / np.sqrt(2))
    p_best_series = pd.Series(p_best, index=common).sort_values()
    print("\n=== Top 30 by S₁+S₂ mean z ===")
    for i, g in enumerate(p_best_series.head(30).index):
        flag = ""
        if g in BCR: flag = "[BCR]"
        elif g in TCR: flag = "[TCR]"
        print(f"  {i+1:>3}. {g:<20} {flag}")


if __name__ == "__main__":
    main()
