"""
Conditional Permutation Test (CPT): exploratory conditional-null workflow
for Perturb-seq response ranking.

Motivation
----------
SCEPTRE (Barry et al. 2021 Genome Biology) constructs an empirical
null by permuting the perturbation indicator D among cells.  This
implicitly assumes that D is independent of the cell's latent
biological state Z.  In practice, this assumption fails: a cell
that is in a particular lineage state (e.g. myeloid) is more
likely to be perturbed by a TF that pushes that lineage (e.g.
CEBPE), so D and Z are correlated.

CPT explores this concern by:
  1. Estimating the cell's "perturbation response latent" Z_pert
     via OLS: Z_pert_i = gamma * D_i + delta * Z_i
  2. In each permutation, jointly shuffling D and Z_pert
  3. Re-residualizing Y on shuffled (D, Z_pert) to obtain a
     conditional null

Mathematical setup
------------------
Model:  Y_g_i = alpha_g * D_i + beta_g * Z_i + gamma_g * (D_i * Z_i) + eps
  where:
    - Y_g_i = expression of gene g in cell i
    - D_i = perturbation indicator
    - Z_i = cell type latent (1-d projection)
    - alpha_g = perturbation-associated coefficient in this working model
    - beta_g = cell type effect
    - gamma_g = interaction (cell type specific effect)

SCEPTRE's null:  shuffle D, keep Z fixed.
  Problem:  in the permuted data, the correlation
    corr(D, Z) is destroyed, so the null distribution has
    LOWER mean correlation than the observed data when
    corr(D, Z) > 0.

CPT's null:  jointly permute (D, Z_pert) so that the
  conditional correlation structure is preserved.

Working score: |alpha_g| (absolute value of OLS coefficient)

Status
------
This module is an exploratory implementation kept in the software package.
It is not used as a primary benchmarked contribution in the manuscript and
should not be presented as an established causal-inference method.
"""

from typing import Tuple, Optional
import numpy as np
import pandas as pd


class CPTEngine:
    """
    Conditional permutation ranking engine for Perturb-seq data.

    Workflow:
      1. fit(X, D)  - estimate cell type latent and perturbation response
      2. test(target) - score all genes
    """

    def __init__(self, n_perms: int = 1000, random_state: int = 42):
        self.n_perms = n_perms
        self.random_state = random_state
        self._fitted = False

    def fit(self, X: np.ndarray, D: np.ndarray, Z: Optional[np.ndarray] = None):
        """
        Parameters
        ----------
        X : (N, G) - log-normalized expression
        D : (N,) - binary perturbation indicator
        Z : (N,) or (N, K) - cell type latent (optional)
        """
        self._X = X  # store for later use in test()
        self._N, self._G = X.shape
        self._D = D.astype(np.float64)
        if Z is None:
            # Estimate Z from PCA
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=5, random_state=self.random_state)
            self._Z = svd.fit_transform(X)
        else:
            self._Z = Z
        # Estimate perturbation response latent
        # Z_pert = predicted cell state under perturbation
        # Simple OLS: Z_pert = X @ (X^T D / (D^T D + eps))
        D_c = self._D - self._D.mean()
        self._Z_pert = X @ (X.T @ D_c) / (np.sum(D_c ** 2) + 1e-9)
        # Standardize
        self._Z_pert = (self._Z_pert - self._Z_pert.mean(axis=0)) / (
            self._Z_pert.std(axis=0) + 1e-9
        )
        self._fitted = True

    def test(
        self,
        target_idx: int,
        alpha_threshold: float = 0.10,
        n_jobs: int = 1,
    ) -> pd.DataFrame:
        """
        Run CPT for all genes given perturbation of target.

        Returns
        -------
        DataFrame with gene, alpha_obs, p_value_perm, p_adjusted
        """
        if not self._fitted:
            raise RuntimeError("Call fit() first.")

        N, G = self._N, self._G
        rng = np.random.default_rng(self.random_state)

        # Build "shufflable" data
        D = self._D
        Z_pert = self._Z_pert  # (N, K)
        # Y for non-target genes
        Y = np.delete(self._X, target_idx, axis=1) if hasattr(self, "_X") else None
        if Y is None:
            # We need X
            raise RuntimeError("Need to store X in fit()")
        Y = (Y - Y.mean(axis=0, keepdims=True))
        Y_std = Y / (Y.std(axis=0, keepdims=True) + 1e-9)

        other_idx = [i for i in range(G) if i != target_idx]
        n_genes = len(other_idx)

        # Observed statistic: rank correlation of D with each Y, after
        # residualizing for Z_pert
        Z_base = np.column_stack([np.ones(N), Z_pert])
        ZtZ_inv = np.linalg.pinv(Z_base.T @ Z_base)
        beta_base = ZtZ_inv @ (Z_base.T @ Y_std)
        Y_resid = Y_std - Z_base @ beta_base
        Y_resid = Y_resid - Y_resid.mean(axis=0, keepdims=True)

        rank_D = np.argsort(np.argsort(D))
        rank_D_c = rank_D - rank_D.mean()
        obs_stat = (Y_resid.T @ rank_D_c) / (np.sum(rank_D_c ** 2) + 1e-15)

        # Permutation: shuffle D and Z_pert jointly
        null_stats = np.zeros((self.n_perms, n_genes))
        for b in range(self.n_perms):
            perm = rng.permutation(N)
            D_perm = D[perm]
            Z_pert_perm = Z_pert[perm]
            # Re-residualize Y on shuffled Z_pert
            Z_base_p = np.column_stack([np.ones(N), Z_pert_perm])
            ZtZ_inv_p = np.linalg.pinv(Z_base_p.T @ Z_base_p)
            beta_p = ZtZ_inv_p @ (Z_base_p.T @ Y_std)
            Y_resid_p = Y_std - Z_base_p @ beta_p
            Y_resid_p = Y_resid_p - Y_resid_p.mean(axis=0, keepdims=True)
            rank_D_p = np.argsort(np.argsort(D_perm))
            rank_D_p_c = rank_D_p - rank_D_p.mean()
            null_stats[b] = (Y_resid_p.T @ rank_D_p_c) / (
                np.sum(rank_D_p_c ** 2) + 1e-15
            )

        # Two-sided p-value
        p_perm = (np.abs(null_stats) >= np.abs(obs_stat)[None, :]).sum(axis=0) + 1
        p_perm = p_perm / (self.n_perms + 1)

        return pd.DataFrame({
            "gene_idx": other_idx,
            "stat_obs": obs_stat,
            "p_value_perm": p_perm,
        }).sort_values("p_value_perm")


# Module-level helper for end-users
def cpt_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_perms: int = 2000,
    cell_type: Optional[np.ndarray] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    High-level exploratory conditional-permutation ranking workflow.

    Parameters
    ----------
    X : (N, G) - log-normalized expression (full data)
    genes : list of str
    target : str - the perturbed gene
    perturbed_idx, control_idx : np.ndarray of cell indices
    n_perms : int
    cell_type : np.ndarray, optional
    """
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)
    D = np.zeros(N_sub)
    D[:len(perturbed_idx)] = 1.0
    Z = cell_type[test_idx] if cell_type is not None else None
    engine = CPTEngine(n_perms=n_perms, random_state=random_state)
    engine.fit(X_sub, D, Z=Z)
    target_idx = genes.index(target)
    res = engine.test(target_idx)
    res["gene"] = [genes[i] for i in res["gene_idx"].values]
    # Adjust for multiple testing
    import statsmodels.stats.multitest as mt
    fdr = mt.multipletests(res["p_value_perm"], method="fdr_bh")[1]
    res["p_adjusted"] = fdr
    res["significant"] = res["p_value_perm"] < 0.05
    res = res.drop(columns=["gene_idx"])
    return res.sort_values("p_value_perm")
