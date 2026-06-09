"""Unit tests for DML/GCM engine."""

import numpy as np
import pandas as pd
import pytest

from pgaa.core.dml_engine import DMLEngine
from pgaa.core.null_calibrator import NullCalibrator


class TestDMLEngine:
    def test_linear_data_recovery(self):
        """On linear data with linear Stage 1, alpha should recover true theta."""
        rng = np.random.default_rng(42)
        n = 2000
        K = 3
        G = 20

        Z = rng.normal(size=(n, K))
        beta_D = np.array([0.5, -0.3, 0.2])
        theta_true = 0.35

        # Generate G genes, where gene 0 is D and gene 1 is Y
        expr = np.zeros((G, n))
        for g in range(G):
            beta_g = rng.normal(size=K)
            expr[g, :] = Z @ beta_g + rng.normal(size=n) * 0.5

        # Override gene 0 as D and gene 1 as Y with true causal link
        expr[0, :] = Z @ beta_D + rng.normal(size=n) * 0.3
        expr[1, :] = theta_true * expr[0, :] + Z @ rng.normal(size=K) + rng.normal(size=n) * 0.3

        engine = DMLEngine(
            n_confounders=K,
            use_linear_stage1=True,
            random_state=42,
        )
        engine.fit_confounders(expr, genes=[f"g{i}" for i in range(G)])
        res = engine.estimate_target("g0")

        row_g1 = res[res["gene"] == "g1"].iloc[0]
        assert abs(row_g1["alpha"] - theta_true) < 0.05
        assert row_g1["ci_lower"] <= theta_true <= row_g1["ci_upper"]

    def test_null_calibration(self):
        """Under H0, p-values should be uniform and Type I error ~ 0.05."""
        rng = np.random.default_rng(42)
        n = 500
        K = 3
        G = 100

        Z = rng.normal(size=(n, K))
        expr = np.zeros((G, n))
        for g in range(G):
            beta = rng.normal(size=K)
            expr[g, :] = Z @ beta + rng.normal(size=n) * 0.5

        engine = DMLEngine(
            n_confounders=K,
            use_linear_stage1=True,
            random_state=42,
        )
        engine.fit_confounders(expr)
        res = engine.estimate_target(0)

        cal = NullCalibrator.calibration_test(res["p_value"].values, alpha=0.05)
        assert cal["empirical_type_i"] < 0.10
        assert cal["ks_pvalue"] > 0.01

    def test_power_increases_with_alpha(self):
        """Larger true effects should have smaller p-values."""
        rng = np.random.default_rng(42)
        n = 1000
        K = 3
        G = 20
        thetas = [0.0, 0.1, 0.2, 0.4]

        pvals = []
        for theta in thetas:
            Z = rng.normal(size=(n, K))
            expr = np.zeros((G, n))
            for g in range(G):
                beta = rng.normal(size=K)
                expr[g, :] = Z @ beta + rng.normal(size=n) * 0.5
            expr[0, :] = Z @ rng.normal(size=K) + rng.normal(size=n)
            expr[1, :] = theta * expr[0, :] + Z @ rng.normal(size=K) + rng.normal(size=n)

            engine = DMLEngine(n_confounders=K, use_linear_stage1=True, random_state=42)
            engine.fit_confounders(expr)
            res = engine.estimate_target(0)
            pvals.append(res.iloc[0]["p_value"])

        for i in range(len(pvals) - 1):
            assert pvals[i] >= pvals[i + 1] or pvals[i + 1] < 0.2

    def test_batch_vs_explicit_formula(self):
        """Vectorized alpha should match explicit OLS formula for each gene."""
        rng = np.random.default_rng(42)
        n = 300
        K = 2
        G = 20

        Z = rng.normal(size=(n, K))
        expr = np.zeros((G, n))
        for g in range(G):
            expr[g, :] = Z @ rng.normal(size=K) + rng.normal(size=n)

        engine = DMLEngine(n_confounders=K, use_linear_stage1=True, random_state=42)
        engine.fit_confounders(expr)
        batch_res = engine.estimate_target(0)

        # Explicit OLS for first other gene
        tidx = 0
        oidx = 1
        D = engine.residuals[tidx, :]
        Y = engine.residuals[oidx, :]
        D_c = D - np.mean(D)
        Y_c = Y - np.mean(Y)
        alpha_explicit = np.sum(D_c * Y_c) / np.sum(D_c ** 2)

        row = batch_res[batch_res["gene"] == engine.genes[oidx]].iloc[0]
        assert abs(row["alpha"] - alpha_explicit) < 1e-10


class TestNullCalibrator:
    def test_uniform_pvalues_pass(self):
        rng = np.random.default_rng(42)
        pvals = rng.random(500)
        cal = NullCalibrator.calibration_test(pvals)
        assert cal["ks_pvalue"] > 0.05
        assert abs(cal["empirical_type_i"] - 0.05) < 0.03

    def test_power_analysis_monotonic(self):
        p1 = NullCalibrator.power_analysis(200, 0.3)
        p2 = NullCalibrator.power_analysis(1000, 0.3)
        assert p2["power"] > p1["power"]
