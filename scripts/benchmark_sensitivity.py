#!/usr/bin/env python3
"""
Sensitivity analysis: benchmark across simulation parameters.

Varied parameters:
  - n_cells
  - true effect size (theta_mean)
  - n_confounders
"""

import time
import itertools
import numpy as np
import pandas as pd
import scanpy as sc

from pgaa.tools.scanpy_api import virtual_ko
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from simulate_perturbseq import simulate_perturbseq
from benchmark_perturbseq import preprocess, evaluate_method, baseline_spearman, baseline_partial_pearson

np.random.seed(42)


def run_sensitivity(
    n_cells_list=(400, 800, 1600),
    theta_mean_list=(0.15, 0.30, 0.50),
    n_confounders_list=(3, 5, 10),
    n_genes=300,
    n_targets=4,
    n_downstream=12,
    seed=42,
):
    rows = []
    configs = list(itertools.product(n_cells_list, theta_mean_list, n_confounders_list))
    total = len(configs)
    for idx, (n_cells, theta_mean, n_confounders) in enumerate(configs, 1):
        print(f"\n[{idx}/{total}] n_cells={n_cells}, theta={theta_mean}, K={n_confounders}")
        adata = simulate_perturbseq(
            n_cells=n_cells,
            n_genes=n_genes,
            n_confounders=n_confounders,
            n_targets=n_targets,
            n_downstream_per_target=n_downstream,
            theta_mean=theta_mean,
            theta_std=0.10,
            seed=seed + idx,
        )
        adata = preprocess(adata)
        gt = adata.uns["ground_truth"]
        targets = gt["target"].unique().tolist()

        for target in targets:
            gt_sub = gt[gt["target"] == target]

            # PGAA
            t0 = time.time()
            res = virtual_ko(
                adata, target,
                use_permutation=False,
                use_linear_stage1=True,
                n_confounders=n_confounders,
                n_top_genes=adata.n_vars,
                random_state=42,
            )
            t = time.time() - t0
            ev = evaluate_method(res, gt_sub, target=target)
            rows.append({
                "method": "PGAA_linear",
                "n_cells": n_cells,
                "theta_mean": theta_mean,
                "n_confounders": n_confounders,
                "target": target,
                "auroc": ev["auroc"],
                "auprc": ev["auprc"],
                "type_i": ev["type_i"],
                "ks_stat": ev["ks_stat"],
                "time": t,
            })

            # Partial Pearson
            t0 = time.time()
            res = baseline_partial_pearson(adata, target, n_confounders=n_confounders)
            t = time.time() - t0
            ev = evaluate_method(res, gt_sub, target=target, p_col="p_value", alpha_col="alpha")
            rows.append({
                "method": "Partial_Pearson",
                "n_cells": n_cells,
                "theta_mean": theta_mean,
                "n_confounders": n_confounders,
                "target": target,
                "auroc": ev["auroc"],
                "auprc": ev["auprc"],
                "type_i": ev["type_i"],
                "ks_stat": ev["ks_stat"],
                "time": t,
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = run_sensitivity()
    df.to_csv("scripts/sensitivity_results.csv", index=False)
    print("\n=== Sensitivity Summary ===")
    print(df.groupby(["method", "n_cells", "theta_mean", "n_confounders"]).mean(numeric_only=True))
    print("\nSaved scripts/sensitivity_results.csv")
