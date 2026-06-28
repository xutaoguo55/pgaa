#!/usr/bin/env python3
"""
Perturb-seq benchmark: PGAA vs baselines on simulated ground-truth data.

Metrics
-------
- AUROC / AUPRC (edge recovery)
- Type I error rate (FPR at FDR<0.05 among negatives)
- Calibration (KS test vs Uniform)
- Power vs effect size
- Runtime
"""

import time
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import scanpy as sc

from pgaa.tools.scanpy_api import virtual_ko

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from simulate_perturbseq import simulate_perturbseq

np.random.seed(42)


def preprocess(adata):
    """Standard scanpy QC + normalization."""
    sc.pp.filter_cells(adata, min_counts=100)
    sc.pp.filter_genes(adata, min_cells=5)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
    return adata


def evaluate_method(pred_df, gt_df, target=None, gene_col="gene", p_col="p_value",
                     alpha_col="alpha", fdr_col="significant"):
    """
    Compute AUROC, AUPRC, Type-I error, calibration.
    pred_df must contain columns: gene, p_value, alpha, significant
    gt_df must contain: target, downstream, theta
    """
    # Merge ground truth (target-specific evaluation)
    merged = pred_df.merge(
        gt_df.rename(columns={"downstream": gene_col, "theta": "true_theta"}),
        on=gene_col,
        how="left",
    )
    merged["is_true"] = merged["true_theta"].notna()
    if target is not None:
        merged = merged[merged[gene_col] != target].copy()

    y_true = merged["is_true"].astype(int).values
    # P-value ranking (lower = more significant)
    pvals = merged[p_col].fillna(1.0).values
    scores = -np.log10(pvals + 1e-300)

    # AUROC / AUPRC
    from sklearn.metrics import roc_auc_score, average_precision_score
    auroc = roc_auc_score(y_true, scores)
    auprc = average_precision_score(y_true, scores)

    # Type I error (false positives among true negatives)
    neg_mask = ~merged["is_true"]
    if fdr_col in merged.columns:
        fp_rate = merged.loc[neg_mask, fdr_col].mean()
    else:
        fp_rate = (merged.loc[neg_mask, p_col] < 0.05).mean()

    # Calibration (KS test on negatives)
    cal = stats.kstest(pvals[neg_mask], "uniform", args=(0, 1))

    # Power by effect size bin
    pos = merged[merged["is_true"]].copy()
    pos["abs_theta"] = pos["true_theta"].abs()
    pos["theta_bin"] = pd.cut(pos["abs_theta"], bins=[0, 0.15, 0.25, 0.5, 1.5])
    power_by_bin = pos.groupby("theta_bin", observed=False).apply(
        lambda df: (df[fdr_col].mean() if fdr_col in df.columns else (df[p_col] < 0.05).mean()),
        include_groups=False,
    )

    return {
        "auroc": auroc,
        "auprc": auprc,
        "type_i": fp_rate,
        "ks_stat": cal.statistic,
        "ks_pvalue": cal.pvalue,
        "power_by_bin": power_by_bin,
    }


def baseline_spearman(adata, target):
    """Naive Spearman correlation on log1p data."""
    from scipy.stats import spearmanr
    X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
    tidx = list(adata.var_names).index(target)
    D = X[:, tidx]
    pvals = []
    rhos = []
    for g in range(adata.n_vars):
        if g == tidx:
            pvals.append(1.0)
            rhos.append(0.0)
            continue
        r, p = spearmanr(D, X[:, g])
        rhos.append(r)
        pvals.append(p)
    df = pd.DataFrame({
        "gene": adata.var_names,
        "rho": rhos,
        "p_value": pvals,
    })
    # simple BH
    from pgaa.core.multiple_testing import apply_fdr
    df = apply_fdr(df, p_col="p_value", method="bh")
    return df


def baseline_partial_pearson(adata, target, n_confounders=5):
    """Pearson partial correlation after PCA residualization."""
    X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
    X_c = X - X.mean(axis=0)
    U, s, Vt = np.linalg.svd(X_c, full_matrices=False)
    K = min(n_confounders, X.shape[1], X.shape[0])
    Z = U[:, :K] * s[:K]
    tidx = list(adata.var_names).index(target)

    pvals = []
    betas = []
    for g in range(adata.n_vars):
        if g == tidx:
            pvals.append(1.0)
            betas.append(0.0)
            continue
        Y = X[:, g]
        D = X[:, tidx]
        Zd = np.column_stack([np.ones(len(Z)), Z])
        # residualize Y and D w.r.t Z
        beta_y = np.linalg.pinv(Zd.T @ Zd) @ (Zd.T @ Y)
        beta_d = np.linalg.pinv(Zd.T @ Zd) @ (Zd.T @ D)
        res_y = Y - Zd @ beta_y
        res_d = D - Zd @ beta_d
        # Pearson on residuals
        r = np.corrcoef(res_y, res_d)[0, 1]
        # t-statistic
        n = len(Y)
        t = r * np.sqrt((n - 2) / (1 - r ** 2 + 1e-15))
        p = 2 * stats.t.sf(np.abs(t), n - 2)
        pvals.append(p)
        betas.append(r)

    df = pd.DataFrame({
        "gene": adata.var_names,
        "alpha": betas,
        "p_value": pvals,
    })
    from pgaa.core.multiple_testing import apply_fdr
    df = apply_fdr(df, p_col="p_value", method="bh")
    return df


def run_benchmark(
    n_cells=1000,
    n_genes=300,
    n_confounders=5,
    n_targets=5,
    n_downstream=15,
    theta_mean=0.30,
    theta_std=0.10,
    seed=42,
):
    print(f"Simulating Perturb-seq: {n_cells} cells x {n_genes} genes ...")
    adata = simulate_perturbseq(
        n_cells=n_cells,
        n_genes=n_genes,
        n_confounders=n_confounders,
        n_targets=n_targets,
        n_downstream_per_target=n_downstream,
        theta_mean=theta_mean,
        theta_std=theta_std,
        seed=seed,
    )
    adata = preprocess(adata)
    gt = adata.uns["ground_truth"]
    target_genes = gt["target"].unique().tolist()

    records = []
    for target in target_genes:
        print(f"  Target: {target}")
        gt_sub = gt[gt["target"] == target]

        # PGAA (linear stage1, fast)
        t0 = time.time()
        res_pgaa = virtual_ko(
            adata, target,
            use_permutation=False,
            use_linear_stage1=True,
            n_confounders=n_confounders,
            n_top_genes=adata.n_vars,
            random_state=42,
        )
        t_pgaa = time.time() - t0
        ev = evaluate_method(res_pgaa, gt_sub, target=target)
        records.append({"method": "PGAA_linear", "target": target, **ev, "time": t_pgaa})

        # Baseline: Spearman
        t0 = time.time()
        res_spear = baseline_spearman(adata, target)
        t_spear = time.time() - t0
        ev = evaluate_method(res_spear, gt_sub, target=target, p_col="p_value", alpha_col="rho")
        records.append({"method": "Spearman", "target": target, **ev, "time": t_spear})

        # Baseline: partial Pearson
        t0 = time.time()
        res_pear = baseline_partial_pearson(adata, target, n_confounders=n_confounders)
        t_pear = time.time() - t0
        ev = evaluate_method(res_pear, gt_sub, target=target, p_col="p_value", alpha_col="alpha")
        records.append({"method": "Partial_Pearson", "target": target, **ev, "time": t_pear})

    summary = pd.DataFrame(records)
    # power_by_bin is a Series; drop for clean print
    summary_clean = summary.drop(columns=["power_by_bin"], errors="ignore")
    print("\n=== Summary ===")
    print(summary_clean.groupby("method").mean(numeric_only=True))
    return summary


if __name__ == "__main__":
    res = run_benchmark(
        n_cells=800,
        n_genes=300,
        n_confounders=5,
        n_targets=5,
        n_downstream=15,
        theta_mean=0.30,
        theta_std=0.10,
        seed=42,
    )
    res.to_csv("scripts/benchmark_results.csv", index=False)
    print("\nSaved scripts/benchmark_results.csv")
