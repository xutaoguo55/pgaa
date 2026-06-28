"""Null distribution calibration and diagnostic utilities."""

import numpy as np
from scipy import stats


class NullCalibrator:
    """
    Calibrate Type I error control and compare analytical vs permutation p-values.
    """

    @staticmethod
    def calibration_test(p_values: np.ndarray, alpha: float = 0.05) -> dict:
        """
        Test whether p-values are Uniform(0,1) under H0.

        Returns KS statistic, p-value, and empirical Type I error rate.
        """
        pvals = np.asarray(p_values)
        pvals = pvals[np.isfinite(pvals)]

        # Kolmogorov-Smirnov vs Uniform(0,1)
        ks_stat, ks_p = stats.kstest(pvals, "uniform", args=(0, 1))

        # Empirical Type I error
        empirical_fpr = np.mean(pvals <= alpha)

        # QQ data
        theoretical = np.linspace(0, 1, len(pvals) + 2)[1:-1]
        observed = np.sort(pvals)

        return {
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_p),
            "empirical_type_i": float(empirical_fpr),
            "expected_type_i": alpha,
            "qq_theoretical": theoretical,
            "qq_observed": observed,
        }

    @staticmethod
    def compare_analytical_vs_permutation(
        p_analytical: np.ndarray,
        p_permutation: np.ndarray,
    ) -> dict:
        """
        Compare analytical (GCM) p-values with permutation p-values.
        """
        mask = np.isfinite(p_analytical) & np.isfinite(p_permutation)
        pa = p_analytical[mask]
        pp = p_permutation[mask]

        # Correlation on -log10 scale
        lpa = -np.log10(pa + 1e-300)
        lpp = -np.log10(pp + 1e-300)
        corr = np.corrcoef(lpa, lpp)[0, 1] if len(pa) > 2 else np.nan

        # Calibration slope
        slope = np.sum(pa * pp) / np.sum(pa ** 2) if np.sum(pa ** 2) > 0 else np.nan

        return {
            "n": int(np.sum(mask)),
            "log10_correlation": float(corr),
            "calibration_slope": float(slope),
            "mean_abs_diff": float(np.mean(np.abs(pa - pp))),
        }

    @staticmethod
    def power_analysis(
        n_cells: int,
        alpha_effect: float,
        sigma_eta: float = 0.28,
        sigma_nu: float = 1.0,
        alpha_level: float = 0.05,
    ) -> dict:
        """
        Analytical power approximation for detecting an alpha association score.

        Uses asymptotic normal approximation:
        power = 1 - Phi(z_{alpha/2} - sqrt(N) * alpha * sigma_eta / sigma_nu)
        """
        z = stats.norm.ppf(1 - alpha_level / 2)
        ncp = np.sqrt(n_cells) * alpha_effect * sigma_eta / sigma_nu
        power = 1 - stats.norm.cdf(z - ncp)
        return {
            "n_cells": n_cells,
            "alpha_effect": alpha_effect,
            "non_centrality": float(ncp),
            "power": float(power),
        }
