#!/usr/bin/env python3
"""
DML/GCM Engine Validation Script

Validates three core claims for Nature Methods submission:
1. Under H0, analytical p-values are calibrated (Uniform, Type I = 0.05)
2. Under nonlinear confounding, ML-based Stage 1 maintains calibration
   while linear Stage 1 inflates Type I error
3. Analytical p-values correlate strongly with permutation p-values
   but are ~1000x faster
"""

import time
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

from pgaa.core.dml_engine import DMLEngine
from pgaa.core.null_calibrator import NullCalibrator

np.random.seed(42)


def simulate_data(n, G, K, theta=0.0, nonlinear_confounding=False):
    """Simulate scRNA-like expression with known causal structure."""
    rng = np.random.default_rng(42)
    Z = rng.normal(size=(n, K))

    expr = np.zeros((G, n))
    for g in range(G):
        beta = rng.normal(size=K)
        if nonlinear_confounding and g % 3 == 0:
            # Nonlinear confounding: quadratic in first PC
            expr[g, :] = (Z @ beta) ** 2 + rng.normal(size=n) * 0.5
        else:
            expr[g, :] = Z @ beta + rng.normal(size=n) * 0.5

    # Gene 0 = D (target), Gene 1 = Y (primary response)
    expr[0, :] = Z @ rng.normal(size=K) + rng.normal(size=n)
    expr[1, :] = theta * expr[0, :] + Z @ rng.normal(size=K) + rng.normal(size=n)
    return expr


def benchmark_null_calibration():
    print("=" * 60)
    print("Benchmark 1: Null Calibration (H0: theta=0)")
    print("=" * 60)

    n, G, K = 500, 100, 3
    expr = simulate_data(n, G, K, theta=0.0)

    results = {}
    for stage1, label in [(True, "Linear_Stage1"), (False, "ML_Stage1")]:
        engine = DMLEngine(
            n_confounders=K,
            use_linear_stage1=stage1,
            ml_method="rf",
            random_state=42,
        )
        engine.fit_confounders(expr)
        res = engine.estimate_target(0)

        cal = NullCalibrator.calibration_test(res["p_value"].values, alpha=0.05)
        results[label] = cal
        print(f"\n{label}:")
        print(f"  Empirical Type I error: {cal['empirical_type_i']:.4f} (expected 0.05)")
        print(f"  KS vs Uniform: D={cal['ks_statistic']:.4f}, p={cal['ks_pvalue']:.3f}")
        print(f"  Significant genes (FDR<0.05): {res['significant'].sum()}")

    return results


def benchmark_nonlinear_confounding():
    print("\n" + "=" * 60)
    print("Benchmark 2: Nonlinear Confounding Robustness")
    print("=" * 60)

    n, G, K = 500, 100, 3
    expr = simulate_data(n, G, K, theta=0.0, nonlinear_confounding=True)

    for stage1, label in [(True, "Linear_Stage1"), (False, "ML_Stage1")]:
        engine = DMLEngine(
            n_confounders=K,
            use_linear_stage1=stage1,
            ml_method="rf",
            random_state=42,
        )
        engine.fit_confounders(expr)
        res = engine.estimate_target(0)

        cal = NullCalibrator.calibration_test(res["p_value"].values, alpha=0.05)
        print(f"\n{label} (nonlinear confounding):")
        print(f"  Empirical Type I error: {cal['empirical_type_i']:.4f}")
        print(f"  KS vs Uniform: D={cal['ks_statistic']:.4f}, p={cal['ks_pvalue']:.3f}")
        print(f"  Significant genes: {res['significant'].sum()}")


def benchmark_analytical_vs_permutation():
    print("\n" + "=" * 60)
    print("Benchmark 3: Analytical vs Permutation Speed & Accuracy")
    print("=" * 60)

    n, G, K = 300, 100, 3
    expr = simulate_data(n, G, K, theta=0.2)

    engine = DMLEngine(
        n_confounders=K,
        use_linear_stage1=True,
        random_state=42,
    )
    engine.fit_confounders(expr)

    # Analytical
    t0 = time.time()
    res_ana = engine.estimate_target(0)
    t_ana = time.time() - t0

    # Permutation (5000)
    t0 = time.time()
    res_perm = engine.permutation_test(0, n_perms=5000, n_jobs=1)
    t_perm = time.time() - t0

    # Merge and compare
    merged = res_ana.merge(res_perm[["gene", "p_value_perm"]], on="gene")
    mask = merged["p_value"] > 0
    corr = np.corrcoef(
        -np.log10(merged.loc[mask, "p_value"] + 1e-300),
        -np.log10(merged.loc[mask, "p_value_perm"] + 1e-300),
    )[0, 1]

    print(f"\nAnalytical p-values: {t_ana:.3f} sec")
    print(f"Permutation (5000):  {t_perm:.3f} sec")
    print(f"Speedup: {t_perm / t_ana:.0f}x")
    print(f"Correlation (-log10 p): {corr:.3f}")


def plot_qq(results_dict, output_path="scripts/qq_plot.png"):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, (label, cal) in zip(axes, results_dict.items()):
        ax.scatter(cal["qq_theoretical"], cal["qq_observed"], s=5, alpha=0.5)
        ax.plot([0, 1], [0, 1], "r--", lw=1)
        ax.set_xlabel("Theoretical Quantile")
        ax.set_ylabel("Observed Quantile")
        ax.set_title(f"{label}\nType I = {cal['empirical_type_i']:.3f}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"\nQQ plot saved: {output_path}")


if __name__ == "__main__":
    null_results = benchmark_null_calibration()
    benchmark_nonlinear_confounding()
    benchmark_analytical_vs_permutation()
    plot_qq(null_results)
    print("\nValidation complete.")
