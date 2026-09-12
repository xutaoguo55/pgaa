#!/usr/bin/env python3
"""Test whether the Adamson 2016 mean AUROC of 0.786 is explained by gene expression.

MANUSCRIPT.md:180 reports that the Wasserstein test reached a mean AUROC of 0.786
across five UPR perturbations, beating Wilcoxon (0.529), t-test (0.523) and MAST
(0.406). That AUROC asks how well the per-gene statistic separates the thirteen
high-confidence UPR genes from the rest of the 2,000-HVG universe. The UPR genes
are ER chaperones and stress-response factors, which are abundantly expressed, and
a per-gene distributional statistic grows with the number of counts behind each
distribution. So the comparison needs a control: does a ranking that uses gene
expression *alone*, with no perturbation information, reach the same AUROC?

This script supplies that control. It takes mean expression and detection rate per
gene from the deposit's own 10X matrix (downloaded once, cached), joins them to the
bundled per-gene score artifact, and reports:

  1. Spearman rho between the per-gene statistic and expression,
  2. the AUROC of an expression-only ranking against the same UPR gold standard,
  3. an expression-matched null: random gene sets drawn to match the UPR genes'
     expression level, which is the null the published AUROC should be read against,
  4. the AUROC restricted to the top-500 expressed genes, where expression is
     roughly homogeneous,
  5. the expression-stratified AUROC: computed within expression deciles and
     weighted by positives, which removes the between-stratum contrast entirely.

The script exits non-zero if the confound does NOT reproduce, so that a change in
the underlying data or the statistic surfaces as a failure rather than as silence.
"""
from __future__ import annotations

import argparse
import gzip
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

GEO_SAMPLE = "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2406nnn/GSM2406675/suppl"
REMOTE = ("GSM2406675_10X001_genes.tsv.gz",
          "GSM2406675_10X001_barcodes.tsv.gz",
          "GSM2406675_10X001_matrix.mtx.txt.gz")

SCORES = "figure_source_data/adamson_gene_level_scores.csv"
UPR_GENES = {
    "IRE1 branch": ["ERN1", "XBP1", "HSPA5", "DNAJB9", "DNAJC3", "SEC61A1"],
    "PERK branch": ["EIF2AK3", "ATF4", "DDIT3", "PPP1R15A", "TRIB3", "CHAC1"],
    "ATF6 branch": ["ATF6", "MBTPS1", "MBTPS2", "CALR", "PDIA4", "HYOU1"],
    "ERAD": ["EDEM1", "SYVN1", "SEL1L", "HERPUD1", "DERL1"],
    "Chaperones": ["HSPA5", "HSP90B1", "CALR", "PDIA3", "PDIA6", "ERP29"],
}
ALL_UPR = set(sum(UPR_GENES.values(), []))

# MANUSCRIPT.md:180 -- the published values this script is auditing.
PUBLISHED = {"SPI1_pDS255": 0.806, "ZNF326_pDS262": 0.767, "BHLHE40_pDS258": 0.788,
             "CREB1_pDS269": 0.772, "DDIT3_pDS263": 0.799}
PUBLISHED_MEAN = 0.786

MATCH_WINDOW = 0.15      # log10 units, i.e. about 1.4x in expression
N_NULL = 2000
SEED = 42


def fetch(name: str, cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / name
    if dest.exists() and dest.stat().st_size:
        return dest
    print(f"downloading {name}")
    with urllib.request.urlopen(f"{GEO_SAMPLE}/{name}", timeout=300) as response:
        dest.write_bytes(response.read())
    return dest


def expression_summary(cache: Path) -> pd.DataFrame:
    """Per-gene mean expression and detection rate from the deposit's 10X matrix."""
    genes = fetch(REMOTE[0], cache)
    barcodes = fetch(REMOTE[1], cache)
    matrix = fetch(REMOTE[2], cache)

    symbols = [line.rstrip("\n").split("\t")[1] for line in gzip.open(genes, "rt")]
    n_cells = sum(1 for _ in gzip.open(barcodes, "rt"))

    total = np.zeros(len(symbols))
    detected = np.zeros(len(symbols), dtype=np.int64)
    seen_header = False
    with gzip.open(matrix, "rt") as handle:
        for line in handle:
            if line[0] == "%":
                continue
            if not seen_header:
                seen_header = True
                continue
            row, _col, value = line.split()
            index = int(row) - 1
            total[index] += float(value)
            detected[index] += 1

    frame = pd.DataFrame({"gene": symbols, "total": total, "detected": detected})
    frame["mean"] = frame["total"] / n_cells
    frame["detection_rate"] = frame["detected"] / n_cells
    return frame.drop_duplicates("gene")


def matched_null(frame: pd.DataFrame, k: int, rng: np.random.Generator) -> np.ndarray:
    """AUROCs of random k-gene sets drawn to match the positives' expression level."""
    log_e = np.log10(frame["mean"].values + 1e-6)
    target = np.sort(log_e[frame["gene"].isin(ALL_UPR).values])[::-1][:k]
    scores = frame["W_observed"].values
    n = len(scores)
    out = np.empty(N_NULL)
    for rep in range(N_NULL):
        chosen: list[int] = []
        for level in target:
            pool = np.where(np.abs(log_e - level) < MATCH_WINDOW)[0]
            pool = pool[~np.isin(pool, chosen)]
            if pool.size == 0:
                pool = np.setdiff1d(np.arange(n), chosen)
            chosen.append(int(rng.choice(pool)))
        mask = np.zeros(n, dtype=bool)
        mask[chosen] = True
        out[rep] = roc_auc_score(mask, scores)
    return out


def stratified_auroc(frame: pd.DataFrame, column: str, n_strata: int = 10) -> tuple[float, int]:
    """AUROC computed within expression deciles and weighted by positives.

    Removes the between-stratum contrast, so a value near 0.5 means the ranking
    carried no signal beyond the gene's expression level.
    """
    frame = frame.copy()
    frame["stratum"] = pd.qcut(frame["mean"].rank(method="first"), n_strata, labels=False)
    weighted = 0.0
    total = 0
    for _, group in frame.groupby("stratum"):
        labels = group["gene"].isin(ALL_UPR).values
        if labels.sum() in (0, len(labels)):
            continue
        weighted += roc_auc_score(labels, group[column].values) * labels.sum()
        total += int(labels.sum())
    return (weighted / total if total else float("nan")), total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "pgaa" / "adamson_matrix"))
    parser.add_argument("--out", default="scripts/adamson_expression_confound.csv")
    args = parser.parse_args()

    try:
        expression = expression_summary(Path(args.cache_dir))
    except OSError as exc:
        print(f"cannot reach GEO: {exc}", file=sys.stderr)
        return 2

    scores = pd.read_csv(SCORES)
    rng = np.random.default_rng(SEED)
    rows = []

    print(f"\n{'perturbation':16s} {'AUROC':>7s} {'published':>9s} "
          f"{'rho(expr)':>10s} {'AUROC(expr)':>12s} {'matched null':>16s} {'p':>7s} "
          f"{'strat(W)':>9s} {'strat(S2)':>10s}")
    print("-" * 108)
    for perturbation, group in scores.groupby("perturbation", sort=False):
        group = group.drop_duplicates("gene").merge(expression, on="gene", how="inner")
        is_upr = group["gene"].isin(ALL_UPR).values
        k = int(is_upr.sum())
        auroc = roc_auc_score(is_upr, group["W_observed"].values)
        rho = spearmanr(group["W_observed"], group["mean"]).statistic
        auroc_expr = roc_auc_score(is_upr, group["mean"].values)
        null = matched_null(group, k, rng)
        p_value = max(float((null >= auroc).mean()), 1.0 / N_NULL)
        stratum_w, _ = stratified_auroc(group, "W_observed")
        stratum_s2, _ = stratified_auroc(group, "S2")
        rows.append({"perturbation": perturbation, "n_positive": k,
                     "auroc": round(auroc, 4), "published_auroc": PUBLISHED.get(perturbation),
                     "spearman_rho_expression": round(rho, 3),
                     "auroc_expression_only": round(auroc_expr, 4),
                     "matched_null_mean": round(float(null.mean()), 4),
                     "matched_null_sd": round(float(null.std()), 4),
                     "p_matched": round(p_value, 4),
                     "auroc_stratified": round(stratum_w, 4),
                     "auroc_s2": round(float(roc_auc_score(is_upr, group["S2"].values)), 4),
                     "auroc_s2_stratified": round(stratum_s2, 4)})
        print(f"{perturbation:16s} {auroc:7.4f} {PUBLISHED.get(perturbation, float('nan')):9.3f} "
              f"{rho:10.3f} {auroc_expr:12.4f} "
              f"{null.mean():8.3f}+-{null.std():.3f} {p_value:7.4f} "
              f"{stratum_w:9.4f} {stratum_s2:10.4f}")

    df = pd.DataFrame(rows)
    mean_auroc = float(df["auroc"].mean())
    print("-" * 108)
    print(f"mean AUROC over perturbations: {mean_auroc:.4f} (published {PUBLISHED_MEAN})")
    print(f"mean rho(statistic, expression): {df['spearman_rho_expression'].mean():.3f}")
    print(f"mean AUROC of an expression-only ranking: {df['auroc_expression_only'].mean():.4f}")
    print(f"mean expression-matched null: {df['matched_null_mean'].mean():.4f}")
    print(f"mean stratified AUROC, Wasserstein: {df['auroc_stratified'].mean():.4f}")
    print(f"mean stratified AUROC, S2: {df['auroc_s2_stratified'].mean():.4f}")

    # Restricted to the top-500 expressed genes, where expression is homogeneous.
    top = scores.drop_duplicates(["gene", "perturbation"]).merge(expression, on="gene", how="inner")
    cutoff = top["mean"].quantile(1 - 500 / top["gene"].nunique())
    restricted = []
    for perturbation, group in top[top["mean"] >= cutoff].groupby("perturbation", sort=False):
        if group["gene"].isin(ALL_UPR).sum() < 3:
            continue
        restricted.append({"perturbation": perturbation,
                           "auroc_top500": round(roc_auc_score(group["gene"].isin(ALL_UPR),
                                                               group["W_observed"]), 4)})
    restricted_df = pd.DataFrame(restricted)
    print(f"\nAUROC restricted to the top-500 expressed genes:")
    print(restricted_df.to_string(index=False))

    df = df.merge(restricted_df, on="perturbation", how="left")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nwrote {out}")

    mean_rho = float(df["spearman_rho_expression"].mean())
    mean_expr_auroc = float(df["auroc_expression_only"].mean())
    mean_restricted = float(df["auroc_top500"].mean())
    failures = []
    if mean_rho < 0.7:
        failures.append(f"statistic no longer tracks expression (mean rho {mean_rho:.3f})")
    if mean_expr_auroc < mean_auroc - 0.05:
        failures.append("expression-only ranking no longer matches the Wasserstein AUROC")
    if mean_restricted > 0.6:
        failures.append(f"signal survives expression restriction (mean AUROC {mean_restricted:.3f})")
    if failures:
        print("\nthe published AUROC is NOT explained by expression:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("\nreproduced: the published AUROC is explained by gene expression level.")
    print(f"  rho(statistic, expression) = {mean_rho:.3f}")
    print(f"  expression-only AUROC {mean_expr_auroc:.4f} vs Wasserstein {mean_auroc:.4f}")
    print(f"  AUROC within the top-500 expressed genes = {mean_restricted:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
