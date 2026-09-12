#!/usr/bin/env python3
"""Uncertainty for the Norman 2019 CEBPE set-level AUROCs quoted in the manuscript.

MANUSCRIPT.md section 3.3 states that the nine-gene CEBPE AUROC falls below the
0.5 chance level for every method in Supplementary Table S4, and that only the
Wasserstein statistic's deficit is established. Nine positives among 2012 genes
is a small sample, so the point estimates alone do not settle that question.
This script attaches an interval to each AUROC, using the same permutation
p-value score as ``scripts/table_sceptre_vs_pgaa.py`` (score = -log10 p), so the
point estimates here reproduce that table exactly.

Bootstrap: genes are resampled with replacement (a whole-gene unit, since the
ranking is over genes); resamples without both classes are skipped. The seed is
fixed, so the interval is reproducible. The analytic Hanley-McNeil standard
error is reported alongside as a closed-form cross-check.

The sign test counts known targets ranked above the median gene; under the null
that count is Binomial(9, 0.5). It is reported because a rank-based statistic
makes no distributional assumption about the score.
"""
from __future__ import annotations

import argparse
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

CEBPE_TARGETS = ("ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1",
                 "PRTN3", "DEFA1", "RNASE2")

# scripts/table_sceptre_vs_pgaa.py:92-97, and the two sources it reads.
SOURCES = (
    ("PGAA-W Wasserstein", "scripts/norman2019_prt_s1_full.csv"),
    ("PGAA-H histogram-shape (n_bins=20)", "scripts/norman2019_prt_s2_nbins20.csv"),
)
# :79 -- SCEPTRE's per-gene output is not in this archive, so its AUROC is a
# table literal with no artifact behind it and gets no interval here.
SCEPTRE_AUROC = 0.469
# :106-107 -- the combined z is a function of the two files above.
COMBINED = "PGAA-W+PGAA-H combined z"

N_BOOT = 2000
SEED = 42


def score(p: np.ndarray) -> np.ndarray:
    return -np.log10(p + 1e-300)


def hanley_mcneil_se(auc: float, n_pos: int, n_neg: int) -> float:
    q1 = auc / (2 - auc)
    q2 = 2 * auc ** 2 / (1 + auc)
    return float(np.sqrt(
        (auc * (1 - auc) + (n_pos - 1) * (q1 - auc ** 2) + (n_neg - 1) * (q2 - auc ** 2))
        / (n_pos * n_neg)
    ))


def interval(is_known: np.ndarray, s: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    aucs = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(is_known), len(is_known))
        y = is_known[idx]
        if y.sum() in (0, len(y)):
            continue
        aucs.append(roc_auc_score(y, s[idx]))
    lo, hi = np.percentile(aucs, [2.5, 97.5])
    return float(lo), float(hi)


def sign_test(is_known: np.ndarray, s: np.ndarray) -> tuple[int, int, float]:
    """Known targets above the median score, and the two-sided binomial p."""
    median = np.median(s)
    above = int((s[is_known] > median).sum())
    n = int(is_known.sum())
    tail = sum(comb(n, k) for k in range(above, n + 1)) / 2 ** n
    return above, n, float(min(1.0, 2 * tail))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="scripts/norman_auroc_ci.csv")
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    rows = []

    s1 = pd.read_csv(SOURCES[0][1])
    s2 = pd.read_csv(SOURCES[1][1])
    p_s1 = s1["p_value_perm"].fillna(1.0).values
    p_s2 = s2["p_value_perm"].fillna(1.0).values

    from scipy.stats import norm
    common = [list(s1["gene"]).index(g) for g in s2["gene"]]
    z1 = norm.ppf(1 - np.clip(p_s1[common], 1e-10, 1 - 1e-10))
    z2 = norm.ppf(1 - np.clip(p_s2, 1e-10, 1 - 1e-10))
    p_comb = 1 - norm.cdf((z1 + z2) / np.sqrt(2))

    panels = [
        ("SCEPTRE", None, None),
        (SOURCES[0][0], s1["gene"].values, p_s1),
        (SOURCES[1][0], s2["gene"].values, p_s2),
        (COMBINED, s2["gene"].values, p_comb),
    ]

    for name, genes, p in panels:
        if genes is None:
            rows.append({"method": name, "auroc": SCEPTRE_AUROC, "ci_low": "", "ci_high": "",
                         "hm_ci_low": "", "hm_ci_high": "", "excludes_chance": "",
                         "n_pos": "", "above_median": "", "binomial_p": "",
                         "note": "per-gene SCEPTRE output not in this archive; no interval"})
            continue
        is_known = np.array([g in CEBPE_TARGETS for g in genes])
        s = score(np.asarray(p, dtype=float))
        auc = float(roc_auc_score(is_known, s))
        lo, hi = interval(is_known, s, rng)
        se = hanley_mcneil_se(auc, int(is_known.sum()), int((~is_known).sum()))
        above, n, p_binom = sign_test(is_known, s)
        rows.append({
            "method": name, "auroc": round(auc, 4),
            "ci_low": round(lo, 3), "ci_high": round(hi, 3),
            "hm_ci_low": round(auc - 1.96 * se, 3), "hm_ci_high": round(auc + 1.96 * se, 3),
            "excludes_chance": (lo > 0.5 or hi < 0.5),
            "n_pos": n, "above_median": above, "binomial_p": round(p_binom, 3),
            "note": "",
        })

    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {out}")
    print(f"\nbootstrap: {N_BOOT} gene resamples, seed {SEED}")

    failing = [r["method"] for r in rows if r["auroc"] and r["auroc"] > 0.5]
    if failing:
        print(f"note: these methods are not below chance: {', '.join(failing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
