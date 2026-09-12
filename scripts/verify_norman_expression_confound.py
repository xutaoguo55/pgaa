#!/usr/bin/env python3
"""Test whether the Norman 2019 CEBPE ELANE ranking is explained by gene expression.

scripts/verify_adamson_expression_confound.py showed that the Adamson benchmark's
mean AUROC of 0.786 -- the manuscript's only "beats the baselines" number -- is a
gene-expression effect: the raw Wasserstein statistic tracks expression at
rho = 0.91 and collapses to chance once each gene is standardised against its own
permutation null (scripts/rerun_adamson_calibrated_auroc.py).

The remaining positive score-utility claim in the manuscript is the Norman 2019
CEBPE result: the persistence statistic ranks ELANE at position 57 (MANUSCRIPT.md
:137), against 1761 for SCEPTRE and 1452 for the Wasserstein statistic. That claim
deserves the same control, so this script runs the Adamson test on it.

Per-gene expression comes from the deposit's own filtered matrix (GSE133344),
streamed rather than stored: 362M entries is about 1.1 GB compressed and the
matrix is ordered by cell, so a partial read would not be a clean gene subset.
Only the per-gene totals and detection counts are kept.

Two statistics are audited side by side, because the manuscript's rank is on the
second one:

  * ``S2``           the raw persistence statistic stored in the artifact,
  * ``p_value_perm`` the same statistic against its own permutation null.

The test is whether ELANE's rank survives matching on expression. If random genes
of ELANE's expression level reach the same rank as often as not, the rank is a
statement about expression range rather than about the CEBPE perturbation.
"""
from __future__ import annotations

import argparse
import gzip
import io
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

GEO_BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl"
GENES_FILE = "GSE133344_filtered_genes.tsv.gz"
BARCODES_FILE = "GSE133344_filtered_barcodes.tsv.gz"
MATRIX_FILE = "GSE133344_filtered_matrix.mtx.gz"

SCORES = "scripts/norman2019_prt_s2_nbins20.csv"
CEBPE_TARGETS = ["ELANE", "AZU1", "MPO", "LYZ", "CTSG", "GFI1", "PRTN3", "DEFA1", "RNASE2"]
# MANUSCRIPT.md:137 -- the values this script is auditing.
QUOTED = {"ELANE_rank": 57, "Wasserstein_ELANE_rank": 1452, "S2_AUROC": 0.476}

MATCH_WINDOW = 0.15      # log10 units, as in the Adamson expression match
MATCH_PERCENTILE = 0.01  # tighter alternative match, in expression-percentile units
N_NULL = 2000
SEED = 42
CHUNK = 20_000_000


def fetch(name: str, cache: Path) -> Path:
    """Download a small side file into ``cache``, resumable and atomic."""
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / name
    if dest.exists() and dest.stat().st_size:
        return dest
    part = dest.with_name(dest.name + ".part")
    url = f"{GEO_BASE}/{name}"
    print(f"downloading {name}", flush=True)
    while True:
        have = part.stat().st_size if part.exists() else 0
        request = urllib.request.Request(url)
        if have:
            request.add_header("Range", f"bytes={have}-")
        with urllib.request.urlopen(request, timeout=600) as response:
            length = int(response.headers.get("Content-Length") or 0)
            if response.status == 206:
                total = have + length
            else:
                have, total = 0, length
            with open(part, "ab" if have else "wb") as handle:
                while True:
                    block = response.read(1 << 22)
                    if not block:
                        break
                    handle.write(block)
        if part.stat().st_size >= total:
            break
        print(f"  interrupted at {part.stat().st_size:,}/{total:,}, resuming", flush=True)
    os.replace(part, dest)
    return dest


def expression_summary(cache: Path, max_cells: int | None = None) -> tuple[pd.DataFrame, dict]:
    """Per-gene total counts and detection counts, streamed from the deposit.

    The matrix is stored by cell (column), so stopping at ``max_cells`` gives the
    same cell subset for every gene, and the connection is closed there -- the
    remaining ~60% of a 1.1 GB download is never fetched. The diagnostics check
    that prefix for representativeness by comparing per-cell library size in its
    first and last deciles: if the deposit's cell ordering carried a batch effect
    the two would diverge, and the expression estimates would be biased.
    """
    genes_path = fetch(GENES_FILE, cache)
    symbols = [line.rstrip("\n").split("\t")[1] for line in gzip.open(genes_path, "rt")]

    url = f"{GEO_BASE}/{MATRIX_FILE}"
    response = urllib.request.urlopen(url, timeout=600)
    handle = gzip.GzipFile(fileobj=response)
    header = None
    while header is None:
        line = handle.readline()
        if not line.startswith(b"%"):
            header = line.decode()
    n_rows, n_cols, n_entries = (int(x) for x in header.split()[:3])
    print(f"matrix: {n_rows} genes x {n_cols} cells, {n_entries} entries", flush=True)
    limit = min(max_cells or n_cols, n_cols)

    total = np.zeros(n_rows)
    detected = np.zeros(n_rows, dtype=np.int64)
    per_cell = np.zeros(limit + 1)
    done, read_cells = 0, 0
    reader = pd.read_csv(io.TextIOWrapper(handle, encoding="utf-8"), sep=r"\s+",
                         header=None, names=["i", "j", "v"],
                         dtype={0: np.int32, 1: np.int32, 2: np.float32},
                         chunksize=CHUNK)
    for chunk in reader:
        read_cells = max(read_cells, int(chunk["j"].max()))
        chunk = chunk[chunk["j"] <= limit]
        if len(chunk):
            rows = chunk["i"].to_numpy() - 1
            total += np.bincount(rows, weights=chunk["v"].to_numpy(), minlength=n_rows)
            detected += np.bincount(rows, minlength=n_rows)
            per_cell += np.bincount(chunk["j"].to_numpy(),
                                    weights=chunk["v"].to_numpy(), minlength=limit + 1)
        done += len(chunk)
        print(f"  {done:,} entries over {read_cells:,} cells", flush=True)
        if read_cells > limit:
            break
    reader.close()
    response.close()

    frame = pd.DataFrame({"gene": symbols, "total": total, "detected": detected})
    frame["mean"] = frame["total"] / limit
    frame["detection_rate"] = frame["detected"] / limit
    libraries = per_cell[1:limit + 1]
    decile = max(1, limit // 10)
    diagnostics = {"cells_used": limit, "cells_in_deposit": n_cols,
                   "first_decile_mean_library": float(libraries[:decile].mean()),
                   "last_decile_mean_library": float(libraries[-decile:].mean())}
    return frame.drop_duplicates("gene"), diagnostics


def rank_of(frame: pd.DataFrame, gene: str, column: str, ascending: bool) -> float:
    ranks = frame[column].rank(ascending=ascending, method="first")
    return float(ranks[frame["gene"] == gene].iloc[0])


def matching_pool(frame: pd.DataFrame, gene: str, mode: str) -> tuple[np.ndarray, float]:
    """Pool of expression-matched genes, and where ``gene`` sits inside it.

    ``log10`` uses a window on the log10 mean, as the Adamson control does;
    ``percentile`` matches on the expression percentile instead. The distinction
    matters when the gene sits at the very top of the expression distribution,
    where a log10 window becomes one-sided and matched genes are drawn from
    below the gene they match. The second value is the gene's own percentile
    inside the pool (0.5 = centred, near 1.0 = the pool is all below it).
    """
    is_gene = (frame["gene"] == gene).values
    if mode == "percentile":
        axis, tolerance = frame["mean"].rank(pct=True).values, MATCH_PERCENTILE
    else:
        axis, tolerance = np.log10(frame["mean"].values + 1e-6), MATCH_WINDOW
    target = float(axis[is_gene][0])
    mask = np.abs(axis - target) < tolerance
    position = float((axis[mask] < target).mean())
    pool = np.flatnonzero(mask)
    pool = pool[pool != int(np.flatnonzero(is_gene)[0])]
    return (pool if pool.size else np.arange(len(frame))), position


def matched_null(frame: pd.DataFrame, gene: str, column: str, ascending: bool,
                 rng: np.random.Generator, mode: str = "log10") -> np.ndarray:
    """Ranks of random genes drawn to match ``gene``'s expression level."""
    pool, _ = matching_pool(frame, gene, mode)
    ranks = frame[column].rank(ascending=ascending, method="first").values
    return ranks[rng.choice(pool, size=N_NULL)]


def stratified_rank(frame: pd.DataFrame, gene: str, column: str, ascending: bool,
                    n_strata: int = 10) -> tuple[float, int]:
    """Percentile of ``gene``'s rank within its own expression decile."""
    frame = frame.copy()
    frame["stratum"] = pd.qcut(frame["mean"].rank(method="first"), n_strata, labels=False)
    stratum = int(frame.loc[frame["gene"] == gene, "stratum"].iloc[0])
    group = frame[frame["stratum"] == stratum].reset_index(drop=True)
    ranks = group[column].rank(ascending=ascending, method="first")
    value = float(ranks[group["gene"] == gene].iloc[0])
    return value / len(group), len(group)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "pgaa" / "norman_matrix"))
    parser.add_argument("--out", default="scripts/norman_expression_confound.csv")
    parser.add_argument("--expression-cache", default="scripts/norman_expression_summary.csv",
                        help="per-gene expression summary; written on first success so the "
                             "1.1 GB matrix is fetched only once")
    parser.add_argument("--max-cells", type=int, default=45000,
                        help="stop after this many cells (the deposit is ordered by cell, "
                             "so this is a prefix subset); 0 means read all 111,668")
    args = parser.parse_args()

    cache_path = Path(args.expression_cache)
    if cache_path.exists():
        expression = pd.read_csv(cache_path)
        diagnostics = {"cells_used": int(expression["n_cells"].iloc[0]),
                       "cells_in_deposit": 111668,
                       "first_decile_mean_library": float(expression["first_decile_library"].iloc[0]),
                       "last_decile_mean_library": float(expression["last_decile_library"].iloc[0])}
        expression = expression[["gene", "total", "detected", "mean", "detection_rate"]]
        print(f"using cached expression summary {cache_path} "
              f"({len(expression)} genes, {diagnostics['cells_used']:,} cells)")
    else:
        try:
            expression, diagnostics = expression_summary(Path(args.cache_dir),
                                                         args.max_cells or None)
        except OSError as exc:
            print(f"cannot reach GEO: {exc}", file=sys.stderr)
            return 2
        cached = expression.copy()
        cached["n_cells"] = diagnostics["cells_used"]
        cached["first_decile_library"] = diagnostics["first_decile_mean_library"]
        cached["last_decile_library"] = diagnostics["last_decile_mean_library"]
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cached.to_csv(cache_path, index=False)
        print(f"wrote {cache_path}")
    print(f"\ncells used: {diagnostics['cells_used']:,} of {diagnostics['cells_in_deposit']:,}")
    ratio = (diagnostics["last_decile_mean_library"]
             / diagnostics["first_decile_mean_library"])
    print(f"per-cell library size, first decile {diagnostics['first_decile_mean_library']:.0f} "
          f"vs last decile {diagnostics['last_decile_mean_library']:.0f} (ratio {ratio:.3f})")
    if not 0.8 < ratio < 1.25:
        print("the cell prefix is not representative of the deposit's library sizes",
              file=sys.stderr)
        return 1

    scores = pd.read_csv(SCORES)
    frame = scores.merge(expression, on="gene", how="inner")
    print(f"\n{scores['gene'].nunique()} genes in the artifact, {len(frame)} with expression")

    is_target = frame["gene"].isin(CEBPE_TARGETS).values
    rng = np.random.default_rng(SEED)
    rows = []
    for column, ascending, label in (("S2", False, "raw S2"),
                                     ("p_value_perm", True, "permutation p")):
        auroc = roc_auc_score(is_target, frame[column].values if not ascending
                              else -frame[column].values)
        auroc_expr = roc_auc_score(is_target,
                                   frame["mean"].values if not ascending else -frame["mean"].values)
        rho = spearmanr(frame[column], frame["mean"]).statistic
        for gene in ("ELANE", "PRTN3"):
            rank = rank_of(frame, gene, column, ascending)
            null = matched_null(frame, gene, column, ascending, rng, "log10")
            p_matched = max(float((null <= rank).mean()), 1.0 / N_NULL)
            null_pct = matched_null(frame, gene, column, ascending, rng, "percentile")
            p_pct = max(float((null_pct <= rank).mean()), 1.0 / N_NULL)
            pool, position = matching_pool(frame, gene, "log10")
            pct_pool, _ = matching_pool(frame, gene, "percentile")
            frac, n_stratum = stratified_rank(frame, gene, column, ascending)
            rows.append({"basis": label, "gene": gene, "rank": int(rank),
                         "expression_matched_null_mean_rank": round(float(null.mean()), 1),
                         "p_matched": round(p_matched, 4),
                         "matched_null_percentile_mean_rank": round(float(null_pct.mean()), 1),
                         "p_matched_percentile": round(p_pct, 4),
                         "log10_pool_n": int(pool.size), "pctile_pool_n": int(pct_pool.size),
                         "marker_percentile_in_log10_pool": round(position, 3),
                         "expression_decile_percentile": round(frac, 3),
                         "n_in_decile": n_stratum})
            print(f"{label:16s} {gene:7s} rank {int(rank):5d} | matched null mean rank "
                  f"{null.mean():7.1f} (p {p_matched:.4f}) | pctile-matched "
                  f"{null_pct.mean():7.1f} (p {p_pct:.4f}) | "
                  f"within decile {frac:.3f} (n={n_stratum}) | pool n={pool.size}, "
                  f"gene at {position:.2f} of its pool")
        print(f"{label:16s} AUROC vs 9 CEBPE targets: {auroc:.4f} | "
              f"expression-only AUROC: {auroc_expr:.4f} | rho(stat, expression): {rho:+.3f}")

    df = pd.DataFrame(rows)
    summary = {f"auroc_{label}": roc_auc_score(is_target, frame[col].values)
               for col, ascending, label in (("S2", False, "S2"),
                                             ("p_value_perm", True, "p"))}
    for col, ascending, label in (("S2", False, "S2"), ("p_value_perm", True, "p")):
        summary[f"expression_only_auroc_{label}"] = roc_auc_score(
            is_target, frame["mean"].values if not ascending else -frame["mean"].values)
        summary[f"spearman_rho_{label}"] = float(spearmanr(frame[col], frame["mean"]).statistic)
        summary[f"ELANE_rank_{label}"] = rank_of(frame, "ELANE", col, ascending)

    out = Path(args.out)
    df.to_csv(out, index=False)
    print(f"\nwrote {out}")
    print("\n" + "=" * 72)
    for key, value in summary.items():
        print(f"{key:32s} {value:.4f}" if isinstance(value, float) else f"{key:32s} {value}")
    print("=" * 72)
    print(f"quoted in MANUSCRIPT.md:137 -> ELANE rank {QUOTED['ELANE_rank']} "
          f"(p basis), S2 AUROC {QUOTED['S2_AUROC']}")

    # ELANE's quoted rank is on the permutation-p basis; that is the number the
    # expression-matched null has to be read against. The conservative verdict is
    # the worse of the two matching modes: a one-sided pool (the gene sitting at
    # the very top of the expression distribution, so its log10 window reaches
    # only downward) can make the log10 null look easy to beat, and the percentile
    # match does not have that failure mode.
    elane_p = df[(df["gene"] == "ELANE") & (df["basis"] == "permutation p")].iloc[0]
    p_log10, p_pct = float(elane_p["p_matched"]), float(elane_p["p_matched_percentile"])
    conservative = max(p_log10, p_pct)
    print(f"\nELANE rank {int(elane_p['rank'])}: log10-matched null mean rank "
          f"{elane_p['expression_matched_null_mean_rank']} (p = {p_log10}), "
          f"percentile-matched {elane_p['matched_null_percentile_mean_rank']} "
          f"(p = {p_pct}); conservative p = {conservative}")
    if conservative < 0.05:
        print("ELANE ranks better than genes of its own expression level under both "
              "matching modes: the CEBPE persistence signal is not an expression-range "
              "effect.")
        return 0
    print("ELANE's rank is not distinguishable from that of genes at the same "
          "expression level under at least one matching mode.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
