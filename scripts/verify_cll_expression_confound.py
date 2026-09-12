#!/usr/bin/env python3
"""Test whether the CLL BCR AUROC of 0.958 is a gene-expression effect.

The manuscript (MANUSCRIPT.md:125) reports that on CLL the Wasserstein statistic
recovers a 13-gene BCR marker set with AUROC 0.958, five of those markers being
in the 2,000-HVG universe (CD79A, CD79B, MS4A1, CD24, BANK1). scripts/
verify_adamson_expression_confound.py showed that the same statistic's only
"beats the baselines" number on Adamson 2016 is an expression-scale effect, so
that claim needs the same control.

Unlike the other four observational datasets, the CLL input is on this machine
(cll_counts.mtx, 36601 genes x 36568 cells), so the check runs end to end: the
20k HVG matrix is rebuilt through the published code path
(scripts/cll20k_4method.py, same seeds), which also re-derives the published
AUROC from the raw deposit rather than trusting the bundled per-gene scores.

The confound signature to look for is the Adamson one: the statistic correlating
with gene expression, and a ranking built from expression alone -- which knows
nothing about TCL1A -- matching or beating the observed AUROC.

Exit status is 0 if the BCR AUROC beats an expression-matched null, 1 if it does
not (i.e. the claim is confounded), 2 if the published pipeline cannot be
reproduced.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from pgaa.core.prt import wasserstein_1d  # noqa: E402

# The CLL counts live outside the repository; point at them with PGAA_RAW_DATA.
RAW = Path(os.environ.get("PGAA_RAW_DATA", REPO.parent))
COUNTS = RAW / "cll_counts.mtx"
GENES = RAW / "cll_genes.txt"
BARCODES = RAW / "cll_barcodes.txt"
META = RAW / "cll_meta.csv"

SCORES = "scripts/cll20k_tcl1a_s1.csv"
QUOTED = {"auroc": 0.958, "n_markers": 5, "top100": 4}
BCR = ["CD79A", "CD79B", "MS4A1", "CD19", "CD22", "BLNK", "BTK", "LYN",
       "SYK", "BANK1", "CD24", "PLCG2", "PIK3CD"]

MATCH_WINDOW = 0.15      # log10 units, as in the Adamson and Norman matches
MATCH_PERCENTILE = 0.01  # tighter alternative match, in expression-percentile units
N_NULL = 2000
SEED = 42
N_HVG = 2000
N_CELLS = 20000
CHUNK = 10_000_000


def read_counts() -> sparse.csr_matrix:
    """Stream the mtx into cells x genes CSR without a dense transpose copy."""
    rows, cols, vals = [], [], []
    with open(COUNTS) as handle:
        header = None
        while header is None:
            line = handle.readline()
            if not line.startswith("%"):
                header = line
        n_genes, n_cells = (int(x) for x in header.split()[:2])
        reader = pd.read_csv(handle, sep=r"\s+", header=None, names=["i", "j", "v"],
                             dtype={"i": np.int32, "j": np.int32, "v": np.float64},
                             chunksize=CHUNK)
        for chunk in reader:
            rows.append(chunk["j"].to_numpy() - 1)
            cols.append(chunk["i"].to_numpy() - 1)
            vals.append(chunk["v"].to_numpy())
    matrix = sparse.csr_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
        shape=(n_cells, n_genes))
    print(f"matrix: {n_cells} cells x {n_genes} genes, {matrix.nnz:,} entries", flush=True)
    return matrix


def build_hvg_matrix() -> sc.AnnData:
    """The published CLL 20k HVG matrix, by the published code path."""
    counts = read_counts()
    genes = pd.read_csv(GENES, header=None)[0].values
    barcodes = pd.read_csv(BARCODES, header=None)[0].values
    meta = pd.read_csv(META, index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=50)
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None,
                               log1p=False, inplace=True)
    adata = adata[adata.obs.pct_counts_mt < 20].copy()
    adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
    sc.pp.subsample(adata, n_obs=N_CELLS, random_state=SEED)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=N_HVG, subset=False)
    adata = adata[:, adata.var["highly_variable"].values].copy()
    print(f"HVG matrix: {adata}", flush=True)
    return adata


def wasserstein_scores(adata: sc.AnnData) -> tuple[pd.Series, int, int]:
    """Recompute S1 from the rebuilt matrix, by the published contrast.

    scripts/cll20k_4method.py bins cells on endogenous TCL1A into a top and a
    bottom quartile and runs ``wasserstein_1d`` on each gene. Reproducing that
    here is what makes the "the published AUROC is reproducible" claim a
    statement about the raw deposit rather than about the bundled artifact.
    """
    dense = adata.X.toarray() if hasattr(adata.X, "toarray") else np.asarray(adata.X)
    genes = list(adata.var_names)
    target = genes.index("TCL1A")
    value = dense[:, target]
    hi = np.where(value >= np.percentile(value, 75))[0]
    lo = np.where(value <= np.percentile(value, 25))[0]
    scores = np.array([wasserstein_1d(dense[hi, g], dense[lo, g]) if g != target else 0.0
                       for g in range(adata.n_vars)])
    return pd.Series(scores, index=genes), len(hi), len(lo)


def expression_only_auroc(frame: pd.DataFrame, is_marker: np.ndarray) -> float:
    return roc_auc_score(is_marker, frame["mean"].values)


def stratified_auroc(frame: pd.DataFrame, is_marker: np.ndarray,
                     n_strata: int = 10) -> float:
    """AUROC of the score ranked only against genes of its own expression decile."""
    stratum = pd.qcut(frame["mean"].rank(method="first"), n_strata, labels=False)
    adjusted = np.zeros(len(frame))
    for value in range(n_strata):
        mask = (stratum == value).values
        adjusted[mask] = frame.loc[mask, "score"].rank(ascending=True, pct=True).values
    return roc_auc_score(is_marker, adjusted)


def matching_pools(frame: pd.DataFrame, markers: list[str], is_marker: np.ndarray,
                   mode: str) -> tuple[list[np.ndarray], list[tuple[str, int, float]]]:
    """Pool of expression-matched candidate genes for each marker.

    ``log10`` matches on the mean within a log10 window, as the Adamson and
    Norman controls do. ``percentile`` matches on the expression percentile
    instead, which matters here: the log10 window is symmetric in log space, so
    at the extreme top of the distribution the pool becomes one-sided and a drawn
    gene sits systematically below the marker it matches. Matching on percentile
    removes that asymmetry and makes the null conservative. The second return
    value reports, per marker, where the marker sits inside its own log10 pool
    (0.5 is centred; near 1.0 means the pool is all below it).
    """
    block = np.flatnonzero(is_marker)
    index = frame["gene"].values
    if mode == "percentile":
        axis, tolerance = frame["mean"].rank(pct=True).values, MATCH_PERCENTILE
    else:
        axis, tolerance = np.log10(frame["mean"].values + 1e-6), MATCH_WINDOW
    pools, balance = [], []
    for gene in markers:
        target = float(axis[index == gene][0])
        mask = np.abs(axis - target) < tolerance
        balance.append((gene, int(mask.sum()), float((axis[mask] < target).mean())))
        pools.append(np.setdiff1d(np.flatnonzero(mask), block))
    return pools, balance


def matched_null_auroc(frame: pd.DataFrame, pools: list[np.ndarray],
                       rng: np.random.Generator, n_null: int) -> np.ndarray:
    """AUROC of random marker sets drawn from the expression-matched pools."""
    scores = frame["score"].values
    out = np.empty(n_null)
    for rep in range(n_null):
        label = np.zeros(len(frame), dtype=bool)
        label[[rng.choice(pool) if pool.size else rng.integers(len(frame)) for pool in pools]] = True
        out[rep] = roc_auc_score(label, scores)
    return out


def enrichment_in_top100(frame: pd.DataFrame, pools: list[np.ndarray], is_marker: np.ndarray,
                         rng: np.random.Generator, n_null: int,
                         top: int = 100) -> tuple[int, np.ndarray]:
    """Markers in the top ``top`` by score, against expression-matched gene sets.

    The manuscript's primary CLL claim is enrichment of the marker set in the top
    100, so the same control has to be run on that count and not only on the AUROC.
    """
    ranks = frame["score"].rank(ascending=False, method="min").values
    observed = int((ranks[is_marker] <= top).sum())
    null = np.empty(n_null, dtype=int)
    for rep in range(n_null):
        drawn = [rng.choice(pool) if pool.size else rng.integers(len(frame)) for pool in pools]
        null[rep] = int((ranks[np.array(drawn)] <= top).sum())
    return observed, null


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="scripts/cll_expression_confound.csv")
    parser.add_argument("--expression-cache", default="scripts/cll_expression_summary.csv")
    parser.add_argument("--n-null", type=int, default=N_NULL)
    parser.add_argument("--no-recompute", dest="recompute", action="store_false",
                        help="trust the bundled per-gene artifact instead of recomputing "
                             "the statistic from the raw deposit")
    args = parser.parse_args()
    n_null = args.n_null

    cache = Path(args.expression_cache)
    adata = None
    if args.recompute or not cache.exists():
        adata = build_hvg_matrix()
    if cache.exists():
        expression = pd.read_csv(cache)[["gene", "mean", "detection_rate"]]
        print(f"using cached expression summary {cache} ({len(expression)} genes)")
    else:
        # Sparse column means keep the 20k x 2k matrix out of dense memory.
        mean = np.asarray(adata.X.mean(axis=0)).ravel()
        detected = np.asarray((adata.X > 0).mean(axis=0)).ravel()
        expression = pd.DataFrame({"gene": list(adata.var_names), "mean": mean,
                                   "detection_rate": detected, "n_cells": N_CELLS})
        expression.to_csv(cache, index=False)
        print(f"wrote {cache}")

    scores = pd.read_csv(SCORES)
    frame = scores.merge(expression, on="gene", how="inner").reset_index(drop=True)
    print(f"\n{len(scores)} genes in the artifact, {len(frame)} with expression")

    # The published AUROC is only reproduced if the statistic itself is recomputed
    # from the deposit; scoring the bundled artifact again would only restate it.
    recompute = {}
    if adata is not None:
        recomputed, n_hi, n_lo = wasserstein_scores(adata)
        check = (scores.set_index("gene")["score"].rename("artifact")
                 .to_frame().join(recomputed.rename("recomputed"), how="inner"))
        delta = (check["artifact"] - check["recomputed"]).abs()
        in_bcr = pd.Index(check.index).isin(BCR)
        recompute = {
            "recomputed_max_abs_diff": round(float(delta.max()), 6),
            "recomputed_spearman_vs_artifact": round(
                float(spearmanr(check["artifact"], check["recomputed"]).statistic), 6),
            "auroc_artifact": round(float(roc_auc_score(
                in_bcr, check["artifact"].to_numpy())), 4),
            "auroc_recomputed": round(float(roc_auc_score(
                in_bcr, check["recomputed"].to_numpy())), 4),
        }
        print(f"\nrecomputed S1 from the rebuilt matrix (TCL1A hi n={n_hi}, lo n={n_lo}, "
              f"{len(check)} shared genes)")
        for key, value in recompute.items():
            print(f"  {key:34s} {value}")
        frame["score"] = frame["gene"].map(recomputed).values
        if frame["score"].isna().any():
            print("recomputed scores do not cover the artifact's genes", file=sys.stderr)
            return 2

    markers = [g for g in BCR if (frame["gene"] == g).any()]
    is_marker = frame["gene"].isin(markers).values
    ranks = frame["score"].rank(ascending=False, method="min")
    for gene in markers:
        row = frame.index[frame["gene"] == gene][0]
        print(f"  {gene:7s} rank {int(ranks[row]):5d}   score {frame['score'].iloc[row]:.4f}   "
              f"mean expression {frame['mean'].iloc[row]:.3f} "
              f"(percentile {100 * (frame['mean'] < frame['mean'].iloc[row]).mean():.1f})")

    auroc = roc_auc_score(is_marker, frame["score"].values)
    auroc_expr = expression_only_auroc(frame, is_marker)
    rho = spearmanr(frame["score"], frame["mean"]).statistic
    strata = stratified_auroc(frame, is_marker)
    top100 = int(ranks[is_marker].le(100).sum())
    print(f"\nmarkers in universe: {len(markers)} of {len(BCR)}; in top 100: {top100}")
    print(f"AUROC (raw Wasserstein)          {auroc:.4f}")
    print(f"AUROC (expression only)          {auroc_expr:.4f}")
    print(f"AUROC (expression-stratified)    {strata:.4f}")
    print(f"rho(score, expression)           {rho:+.3f}")

    rng = np.random.default_rng(SEED)
    pools, balance = matching_pools(frame, markers, is_marker, "log10")
    null = matched_null_auroc(frame, pools, rng, n_null)
    p_matched = max(float((null >= auroc).mean()), 1.0 / n_null)
    print(f"expression-matched null (log10)  {null.mean():.4f} "
          f"(sd {null.std():.4f}, {n_null} draws)  p = {p_matched:.4f}")
    print("  pool balance (marker's percentile inside its own matching pool; "
          "0.5 = centred, ->1.0 = pool drawn from below):")
    for gene, size, position in balance:
        print(f"    {gene:7s} pool n={size:4d}  marker at {position:.3f}")

    # The percentile mode matches on rank, so its pool is symmetric by construction
    # and its balance diagnostic carries no information; only the log10 one is read.
    pct_pools, _ = matching_pools(frame, markers, is_marker, "percentile")
    null_pct = matched_null_auroc(frame, pct_pools, rng, n_null)
    p_pct = max(float((null_pct >= auroc).mean()), 1.0 / n_null)
    print(f"expression-matched null (pctile)  {null_pct.mean():.4f} "
          f"(sd {null_pct.std():.4f}, {n_null} draws)  p = {p_pct:.4f}"
          f"   [pool n={[int(p.size) for p in pct_pools]}]")

    # Calibration of the stratification itself: if expression-only scores the same
    # after stratification, the diagnostic has not removed the expression effect
    # and its value must not be read as evidence of a surviving signal.
    expr_strata = stratified_auroc(frame.assign(score=frame["mean"]), is_marker)
    print(f"expression-only, expression-stratified {expr_strata:.4f} "
          f"(same number for a pure expression ranking)")

    observed_top, null_top = enrichment_in_top100(frame, pools, is_marker, rng, n_null)
    p_top = max(float((null_top >= observed_top).mean()), 1.0 / n_null)
    print(f"top-100 enrichment               {observed_top}/{len(markers)} observed, "
          f"expression-matched null {null_top.mean():.2f} (sd {null_top.std():.2f})  "
          f"p = {p_top:.4f}")

    # If a pure location-shift statistic reaches the same AUROC, the Wasserstein
    # number is carrying expression, not distributional information.
    print()
    for name, path, column in (("t-test", "scripts/cll20k_tcl1a_t.csv", "score"),
                               ("S2 persistence", "scripts/cll20k_tcl1a_s2.csv", "S2"),
                               ("S3", "scripts/cll20k_tcl1a_s3.csv", "S3")):
        other = Path(path)
        if not other.exists():
            continue
        table = pd.read_csv(other)
        if column not in table.columns:
            continue
        merged = table.merge(expression, on="gene", how="inner")
        if len(merged) < len(table) // 2:
            continue
        label = merged["gene"].isin(markers).values
        rank = merged[column].rank(ascending=False, method="min")
        print(f"{name:15s} AUROC {roc_auc_score(label, merged[column]):.4f} | "
              f"rho(score, expression) {spearmanr(merged[column], merged['mean']).statistic:+.3f} | "
              f"markers in top 100 {int(rank[label].le(100).sum())}")

    print(f"\nquoted in MANUSCRIPT.md:125 -> AUROC {QUOTED['auroc']}, "
          f"{QUOTED['n_markers']} markers in universe, {QUOTED['top100']} in top 100")

    out = pd.DataFrame([{
        "n_markers": len(markers), "top100": top100,
        "auroc_raw": round(auroc, 4), "auroc_expression_only": round(auroc_expr, 4),
        "auroc_expression_stratified": round(strata, 4),
        "spearman_rho_score_expression": round(float(rho), 4),
        "matched_null_mean_auroc": round(float(null.mean()), 4),
        "matched_null_sd": round(float(null.std()), 4),
        "auroc_expression_only_stratified": round(float(expr_strata), 4),
        "matched_null_percentile_mean_auroc": round(float(null_pct.mean()), 4),
        "matched_null_percentile_sd": round(float(null_pct.std()), 4),
        "p_matched_percentile": round(p_pct, 4),
        "top100_observed": observed_top,
        "top100_matched_null_mean": round(float(null_top.mean()), 2),
        "p_top100": round(p_top, 4),
        "p_matched": round(p_matched, 4), "n_null": n_null,
        **recompute,
        "markers": ";".join(markers)}])
    out.to_csv(args.out, index=False)
    print(f"\nwrote {args.out}")

    # The verdict rests on the conservative (percentile-matched) null, and is only
    # meaningful if the statistic was recomputed rather than re-read from the artifact.
    conservative = max(p_matched, p_pct)
    if pct_balance and max(b[2] for b in balance) > 0.75:
        print("\nwarning: at least one log10 matching pool is one-sided "
              "(marker sits above 75% of its pool), so the log10 null is the weaker one")
    if adata is None:
        print("\nnote: --no-recompute, so this scores the bundled artifact rather than "
              "the raw deposit")
    if conservative < 0.05:
        print(f"\nthe BCR AUROC of {auroc:.3f} exceeds both expression-matched nulls "
              f"({null.mean():.3f} log10 / {null_pct.mean():.3f} percentile): marker "
              f"recovery is not an expression-range effect.")
        return 0
    print(f"\nthe BCR AUROC of {auroc:.3f} is not distinguishable from the "
          f"expression-matched null ({null.mean():.3f} log10 / {null_pct.mean():.3f} "
          f"percentile, p = {p_matched:.4f} / {p_pct:.4f}): the marker recovery in this "
          f"dataset is an expression-range effect.", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
