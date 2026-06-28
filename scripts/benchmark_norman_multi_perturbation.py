#!/usr/bin/env python3
"""Norman 2019 multi-perturbation ranking benchmark.

This script evaluates PGAA-W Wasserstein ranking against standard
mean/location tests and a distribution-aware KS baseline across several
single-gene CRISPRa perturbations from Norman 2019.

The evaluation uses curated target-program panels, not a genome-wide DEG
gold standard from the original paper. Positive genes are forced into the
ranking universe in addition to HVGs so that AUROC/AUPRC calculations do not
silently drop the genes being evaluated.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.stats import ks_2samp, mannwhitneyu, ttest_ind
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pgaa.core.prt import wasserstein_1d


TARGET_PANELS = {
    "KLF1": [
        "HBB",
        "HBA1",
        "HBA2",
        "AHSP",
        "ALAS2",
        "GYPA",
        "GYPB",
        "HEMGN",
        "TFR2",
        "SLC25A37",
        "FECH",
        "HMBS",
        "UROS",
        "BLVRB",
        "TFRC",
        "SLC25A39",
    ],
    "CEBPE": ["ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3", "DEFA1", "RNASE2"],
    "CEBPA": ["CEBPB", "CSF3R", "GFI1", "GFI1B", "GATA1", "GATA2", "SPI1", "MPO", "ELANE"],
}


def default_h5ad() -> Path:
    root = Path(__file__).resolve().parent.parent
    return root.parent / "norman2019" / "norman2019_full_log.h5ad"


def single_perturbation_mask(labels: pd.Series, target: str) -> np.ndarray:
    pattern = re.compile(rf"^(?:{re.escape(target)}_NegCtrl\d+|NegCtrl\d+_{re.escape(target)})__")
    return labels.map(lambda value: bool(pattern.search(value))).to_numpy()


def control_mask(labels: pd.Series) -> np.ndarray:
    return labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True).to_numpy()


def dense_matrix(x):
    if sparse.issparse(x):
        return x.toarray()
    return np.asarray(x)


def select_gene_indices(adata, target: str, panel: list[str], n_hvg: int) -> tuple[list[int], list[str]]:
    var = adata.var.copy()
    if "highly_variable" in var.columns and var["highly_variable"].astype(bool).sum() > 0:
        hvg_names = var.index[var["highly_variable"].astype(bool)].tolist()[:n_hvg]
    else:
        # Fallback for h5ad files without an HVG mask.
        hvg_names = var.index.tolist()[:n_hvg]
    forced = [target] + list(panel)
    keep_names = []
    seen = set()
    for gene in hvg_names + forced:
        if gene in adata.var_names and gene not in seen:
            keep_names.append(gene)
            seen.add(gene)
    indices = [int(adata.var_names.get_loc(gene)) for gene in keep_names]
    return indices, keep_names


def residualize_expression(X: np.ndarray, random_state: int, n_clusters: int) -> tuple[np.ndarray, np.ndarray]:
    n_cells = X.shape[0]
    n_components = max(2, min(20, X.shape[1] - 1, n_cells - 1))
    if n_components < 2:
        cell_type = np.zeros(n_cells, dtype=int)
    else:
        svd = TruncatedSVD(n_components=n_components, random_state=random_state)
        emb = svd.fit_transform(X)
        k = max(2, min(n_clusters, n_cells // 25))
        cell_type = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(emb)

    parts = [np.ones(n_cells)]
    levels = np.unique(cell_type)
    if len(levels) > 1:
        dummies = np.zeros((n_cells, len(levels) - 1), dtype=float)
        for j, level in enumerate(levels[1:]):
            dummies[:, j] = cell_type == level
        parts.append(dummies)
    lib_size = X.sum(axis=1).astype(float)
    lib_z = (lib_size - lib_size.mean()) / (lib_size.std() + 1e-9)
    parts.append(lib_z[:, None])
    design = np.column_stack(parts)
    beta = np.linalg.pinv(design.T @ design) @ (design.T @ X)
    return X - design @ beta, cell_type


def score_target(
    adata,
    labels: pd.Series,
    target: str,
    panel: list[str],
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rng = np.random.default_rng(args.random_state)
    pert_idx = np.where(single_perturbation_mask(labels, target))[0]
    ctrl_all = np.where(control_mask(labels))[0]
    if len(pert_idx) < args.min_cells:
        raise ValueError(f"{target}: only {len(pert_idx)} perturbed cells")
    n_ctrl = min(len(ctrl_all), len(pert_idx) * args.control_ratio, args.max_controls)
    ctrl_idx = rng.choice(ctrl_all, size=n_ctrl, replace=False)
    rows = np.concatenate([pert_idx, ctrl_idx])
    treatment = np.r_[np.ones(len(pert_idx), dtype=bool), np.zeros(len(ctrl_idx), dtype=bool)]

    gene_indices, genes = select_gene_indices(adata, target, panel, args.n_hvg)
    X = dense_matrix(adata[rows, gene_indices].X).astype(np.float64, copy=False)
    Y, cell_type = residualize_expression(X, args.random_state, args.n_clusters)

    target_pos = genes.index(target) if target in genes else None
    ranked = [i for i, gene in enumerate(genes) if gene != target]
    ranked_genes = [genes[i] for i in ranked]
    Y_ranked = Y[:, ranked]
    pert = treatment
    ctrl = ~treatment

    s1 = np.array([wasserstein_1d(Y_ranked[pert, j], Y_ranked[ctrl, j]) for j in range(Y_ranked.shape[1])])
    t_res = ttest_ind(Y_ranked[pert], Y_ranked[ctrl], axis=0, equal_var=False, nan_policy="omit")
    t_score = np.abs(np.nan_to_num(t_res.statistic, nan=0.0))

    ks_stat = np.zeros(Y_ranked.shape[1], dtype=float)
    ks_p = np.ones(Y_ranked.shape[1], dtype=float)
    wilcoxon_score = np.zeros(Y_ranked.shape[1], dtype=float)
    wilcoxon_p = np.ones(Y_ranked.shape[1], dtype=float)
    for j in range(Y_ranked.shape[1]):
        x = Y_ranked[pert, j]
        y = Y_ranked[ctrl, j]
        ks = ks_2samp(x, y, alternative="two-sided", mode="asymp")
        ks_stat[j] = float(ks.statistic)
        ks_p[j] = float(ks.pvalue)
        try:
            mw = mannwhitneyu(x, y, alternative="two-sided", method="asymptotic")
            wilcoxon_p[j] = float(mw.pvalue)
            wilcoxon_score[j] = -np.log10(max(float(mw.pvalue), 1e-300))
        except ValueError:
            wilcoxon_p[j] = 1.0
            wilcoxon_score[j] = 0.0

    positive_genes = set(panel) - {target}
    is_positive = np.array([gene in positive_genes for gene in ranked_genes], dtype=bool)
    gene_scores = pd.DataFrame(
        {
            "target": target,
            "gene": ranked_genes,
            "is_positive": is_positive,
            "s1_wasserstein": s1,
            "ks_statistic": ks_stat,
            "ks_p_value": ks_p,
            "t_abs_statistic": t_score,
            "wilcoxon_neglog10_p": wilcoxon_score,
            "wilcoxon_p_value": wilcoxon_p,
        }
    )

    method_scores = {
        "PGAA_S1_Wasserstein": s1,
        "KS_statistic": ks_stat,
        "Welch_t_abs": t_score,
        "Wilcoxon_neglog10_p": wilcoxon_score,
    }
    summary_rows = []
    n_pos = int(is_positive.sum())
    for method, scores in method_scores.items():
        if n_pos == 0 or n_pos == len(is_positive):
            auroc = np.nan
            auprc = np.nan
        else:
            auroc = roc_auc_score(is_positive.astype(int), scores)
            auprc = average_precision_score(is_positive.astype(int), scores)
        order = np.argsort(-scores)
        top50_hits = int(is_positive[order[:50]].sum())
        top100_hits = int(is_positive[order[:100]].sum())
        summary_rows.append(
            {
                "target": target,
                "method": method,
                "n_perturbed_cells": len(pert_idx),
                "n_control_cells": len(ctrl_idx),
                "n_ranked_genes": len(ranked_genes),
                "n_positive_genes": n_pos,
                "random_auprc_baseline": n_pos / len(ranked_genes),
                "auroc": auroc,
                "auprc": auprc,
                "top50_positive_hits": top50_hits,
                "top100_positive_hits": top100_hits,
            }
        )

    panel_audit = pd.DataFrame(
        {
            "target": target,
            "panel_gene": panel,
            "present_in_h5ad": [gene in adata.var_names for gene in panel],
            "in_ranking_universe": [gene in ranked_genes for gene in panel],
            "hvg_flag": [
                bool(adata.var.loc[gene, "highly_variable"]) if gene in adata.var_names and "highly_variable" in adata.var.columns else False
                for gene in panel
            ],
        }
    )
    metadata = {
        "target_gene_position": target_pos,
        "n_clusters_observed": int(len(np.unique(cell_type))),
    }
    return pd.DataFrame(summary_rows), gene_scores, panel_audit, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=os.environ.get("NORMAN2019_H5AD", str(default_h5ad())))
    parser.add_argument("--targets", nargs="+", default=["KLF1", "CEBPE", "CEBPA"])
    parser.add_argument("--n-hvg", type=int, default=2000)
    parser.add_argument("--control-ratio", type=int, default=3)
    parser.add_argument("--max-controls", type=int, default=5000)
    parser.add_argument("--min-cells", type=int, default=100)
    parser.add_argument("--n-clusters", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--out-prefix", default="scripts/norman_multi_perturbation")
    args = parser.parse_args()

    data = Path(args.data)
    if not data.exists():
        raise FileNotFoundError(
            "Norman 2019 h5ad not found. Provide --data or set NORMAN2019_H5AD."
        )
    print(f"Loading {data}")
    adata = sc.read_h5ad(data)
    labels = adata.obs["perturbation"].astype(str)
    print(f"Loaded Norman 2019: {adata.n_obs} cells x {adata.n_vars} genes")

    summaries = []
    all_scores = []
    audits = []
    metadata_rows = []
    for target in args.targets:
        if target not in TARGET_PANELS:
            raise ValueError(f"No curated panel configured for target {target}")
        print(f"\n=== {target} ===")
        t0 = time.time()
        summary, scores, audit, metadata = score_target(adata, labels, target, TARGET_PANELS[target], args)
        elapsed = time.time() - t0
        print(summary.to_string(index=False))
        print(f"Elapsed: {elapsed:.1f}s")
        summaries.append(summary)
        all_scores.append(scores)
        audits.append(audit)
        metadata_rows.append({"target": target, "elapsed_seconds": elapsed, **metadata})

    prefix = Path(args.out_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    summary_df = pd.concat(summaries, ignore_index=True)
    score_df = pd.concat(all_scores, ignore_index=True)
    audit_df = pd.concat(audits, ignore_index=True)
    metadata_df = pd.DataFrame(metadata_rows)

    summary_path = prefix.with_name(prefix.name + "_summary.csv")
    score_path = prefix.with_name(prefix.name + "_gene_scores.csv")
    audit_path = prefix.with_name(prefix.name + "_panel_audit.csv")
    metadata_path = prefix.with_name(prefix.name + "_metadata.csv")
    summary_df.to_csv(summary_path, index=False)
    score_df.to_csv(score_path, index=False)
    audit_df.to_csv(audit_path, index=False)
    metadata_df.to_csv(metadata_path, index=False)

    print("\nWrote:")
    for path in [summary_path, score_path, audit_path, metadata_path]:
        print(f"  {path}")


if __name__ == "__main__":
    main()
