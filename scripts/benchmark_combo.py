#!/usr/bin/env python3
"""
Benchmark combinatorial perturbation prediction.

Uses simulate_perturbseq data (multiple single-gene perturbations)
to evaluate ComboPredictor.  True combination effects are assumed
to be additive: theta_AB = theta_A + theta_B.
"""

import time
import numpy as np
import pandas as pd
from scipy import stats
import scanpy as sc

from pgaa.tools.scanpy_api import virtual_ko
from pgaa.core.combo_predictor import ComboPredictor
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from simulate_perturbseq import simulate_perturbseq

np.random.seed(42)


def preprocess(adata):
    sc.pp.filter_cells(adata, min_counts=100)
    sc.pp.filter_genes(adata, min_cells=5)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    return adata


def run():
    print("Simulating multi-target Perturb-seq ...")
    adata = simulate_perturbseq(
        n_cells=1000,
        n_genes=300,
        n_confounders=5,
        n_targets=6,
        n_downstream_per_target=15,
        theta_mean=0.30,
        theta_std=0.10,
        seed=42,
    )
    adata = preprocess(adata)
    gt = adata.uns["ground_truth"]
    targets = gt["target"].unique().tolist()

    # Single-gene estimates
    results_map = {}
    for target in targets:
        print(f"  Estimating {target} ...")
        t0 = time.time()
        res = virtual_ko(
            adata, target,
            use_permutation=False,
            use_linear_stage1=True,
            n_confounders=5,
            n_top_genes=adata.n_vars,
            random_state=42,
        )
        print(f"    done in {time.time()-t0:.2f}s")
        results_map[target] = res

    cp = ComboPredictor(results_map)

    # Evaluate all pairwise combinations
    from sklearn.metrics import roc_auc_score, average_precision_score

    records = []
    for i, a in enumerate(targets):
        for b in targets[i+1:]:
            pred = cp.predict_additive(a, b)
            # Ground truth: union of downstreams from A and B
            gt_a = gt[gt["target"] == a][["downstream", "theta"]].rename(
                columns={"theta": "theta_a"}
            )
            gt_b = gt[gt["target"] == b][["downstream", "theta"]].rename(
                columns={"theta": "theta_b"}
            )
            gt_ab = gt_a.merge(gt_b, on="downstream", how="outer").fillna(0.0)
            gt_ab["theta_ab"] = gt_ab["theta_a"] + gt_ab["theta_b"]
            gt_ab["is_true"] = gt_ab["theta_ab"].abs() > 0.01

            merged = pred.merge(gt_ab, left_on="gene", right_on="downstream", how="left")
            merged["is_true"] = merged["is_true"].fillna(False)

            y_true = merged["is_true"].astype(int).values
            scores = np.abs(merged["alpha_pred"].fillna(0.0).values)

            auroc = roc_auc_score(y_true, scores)
            auprc = average_precision_score(y_true, scores)

            # Rank correlation of predicted vs true absolute effect
            mask = merged["is_true"] | True  # all genes
            spearman = stats.spearmanr(
                merged.loc[mask, "alpha_pred"].abs(),
                merged.loc[mask, "theta_ab"].abs(),
            )[0]

            records.append({
                "pair": f"{a}+{b}",
                "auroc": auroc,
                "auprc": auprc,
                "spearman": spearman,
            })

    summary = pd.DataFrame(records)
    print("\n=== Combo Prediction Summary ===")
    print(summary)
    print("\nMean AUROC:", summary["auroc"].mean())
    print("Mean AUPRC:", summary["auprc"].mean())
    print("Mean Spearman:", summary["spearman"].mean())
    summary.to_csv("scripts/combo_prediction.csv", index=False)
    print("Saved scripts/combo_prediction.csv")
    return summary


if __name__ == "__main__":
    run()
