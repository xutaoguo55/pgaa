"""
PRT-S₄: exploratory Fisher-information-inspired perturbation score

Scope
-----
Treat each gene's expression as a 1-parameter exponential family:
  P(Y_g | θ) = exp(θ_g * T(Y_g) - ψ(θ_g))

where T(Y) = Y (natural sufficient statistic for normal).

The Fisher information metric:
  g(θ) = Var_θ[T(Y)]

Under perturbation D, the "natural parameter" θ changes:
  θ_on = E[Y | D=1]   (MLE under H1)
  θ_off = E[Y | D=0]  (MLE under H0)

The Fisher-Rao geodesic distance between P_on and P_off:
  S4_g = |θ_on - θ_off| * sqrt(g(θ_eff))

where θ_eff = (θ_on + θ_off)/2 (midpoint).

For Normal(μ, σ²), this simplifies to:
  S4_g = |μ_on - μ_off| / σ_pooled

which is the standard t-test statistic scaled by 1/sqrt(N).
HOWEVER, for NB(μ, φ) (Negative Binomial, used in scRNA-seq),
  θ = log(μ / (μ + φ⁻¹))  (natural parameter for NB canonical form)
  g(θ) = ... (more complex but has closed form)

This module is exploratory and is not a primary benchmarked contribution in
the manuscript. It should be described as a count-model-inspired score, not
as a validated detector.
"""

import numpy as np
import pandas as pd
from scipy.special import digamma, polygamma


def negbinom_mle_mu_phi(x: np.ndarray, eps: float = 1e-3) -> tuple:
    """
    Method-of-moments estimate of NB parameters (mu, phi).
    phi = 1/alpha (dispersion parameter).
    """
    mu = np.mean(x)
    var = np.var(x, ddof=1)
    phi = 1.0 / max((var - mu) / (mu * mu + eps), 0.05)
    return mu, phi


def negbinom_fisher(mu: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """
    Fisher information for NB mean parameter μ (NB-2 parameterization).
    g(μ) = φ * μ² / (1 + φ * μ)

    Returns per-gene Fisher info.
    """
    return phi * mu * mu / (1.0 + phi * mu + 1e-12)


def s4_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
) -> pd.DataFrame:
    """
    PRT-S₄ Fisher-information-inspired exploratory score.

    For each gene g:
      Estimate NB(mu_on, phi_on) and NB(mu_off, phi_off) from
      perturbed and control cells.
      Compute Fisher metric: g = φ * μ² / (1 + φμ)
      S4_g = |μ_on - μ_off| * sqrt(g(mu_eff, phi_eff))
    """
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)

    tidx = genes.index(target)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]

    n_pert = len(perturbed_idx)
    D = np.zeros(N_sub, dtype=bool)
    D[:n_pert] = True

    Y_on = X_sub[D]
    Y_off = X_sub[~D]

    mu_on = Y_on.mean(axis=0)
    var_on = Y_on.var(axis=0, ddof=1)
    phi_on = 1.0 / np.maximum((var_on - mu_on) / (mu_on * mu_on + 1e-3), 0.01)

    mu_off = Y_off.mean(axis=0)
    var_off = Y_off.var(axis=0, ddof=1)
    phi_off = 1.0 / np.maximum((var_off - mu_off) / (mu_off * mu_off + 1e-3), 0.01)

    # Pooled
    mu_pool = (mu_on * n_pert + mu_off * (N_sub - n_pert)) / N_sub
    phi_pool = (phi_on * n_pert + phi_off * (N_sub - n_pert)) / N_sub

    # Fisher info at pooled estimate
    g_pool = phi_pool * mu_pool * mu_pool / (1.0 + phi_pool * mu_pool + 1e-12)

    # S4: absolute mean difference weighted by Fisher curvature
    delta = np.abs(mu_on - mu_off)
    s4_values = delta[other_idx] * np.sqrt(g_pool[other_idx] + 1e-12)

    res = pd.DataFrame({
        "gene": other_genes,
        "S4": s4_values,
        "delta_mu": delta[other_idx],
        "g_fisher": g_pool[other_idx],
        "phi_on": phi_on[other_idx],
        "phi_off": phi_off[other_idx],
    }).sort_values("S4", ascending=False)

    return res
