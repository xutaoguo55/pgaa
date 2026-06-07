"""
Real-data specific path for PGAA.

Uses cell-level covariates (library size, gene count, %MT, PCs of HVGs)
instead of gene-level residualization.  This avoids absorbing target
gene expression into nuisance parameters and is robust to
gene-magnitude confounds.
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.stats import t as tdist, norm


def virtual_oe_reald(
    adata: sc.AnnData,
    target: str,
    hk_genes: Optional[List[str]] = None,
    n_pcs: int = 10,
    covariates: Optional[List[str]] = None,
    alpha_threshold: float = 0.1,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Regress Y_g ~ D + cell-covariates for each gene g != target.

    Parameters
    ----------
    adata : sc.AnnData
        Log-normalized expression matrix.
    target : str
        Target gene name.
    hk_genes : list of str
        Housekeeping genes for Storey pi0 calibration.
    n_pcs : int
        Number of HVG-based PCs to include as covariates.
    covariates : list of str
        Additional cell-level covariate column names from adata.obs.
    alpha_threshold : float
        Effect size threshold (in log-FC) for significance.
    random_state : int

    Returns
    -------
    pd.DataFrame with columns: gene, alpha, se, t_stat, p_value,
                                 p_adjusted, significant, tier.
    """
    if target not in adata.var_names:
        raise ValueError(f"Target {target} not in adata.var_names.")

    if covariates is None:
        covariates = ["total_counts", "n_genes_by_counts"]
    covariates = [c for c in covariates if c in adata.obs.columns]

    # Build Y (G x N)
    X = adata.X
    if sparse.issparse(X):
        X = X.toarray()
    Y = np.asarray(X, dtype=np.float64)  # cells x genes
    genes = list(adata.var_names)
    tidx = genes.index(target)
    D = Y[:, tidx]
    D_c = D - D.mean()

    # Cell-level covariates
    Z_parts = []
    for c in covariates:
        z = adata.obs[c].values.astype(np.float64)
        z = (z - z.mean()) / (z.std() + 1e-9)
        Z_parts.append(z)
    if "pct_counts_mt" in adata.obs.columns:
        z = adata.obs["pct_counts_mt"].values.astype(np.float64)
        z = (z - z.mean()) / (z.std() + 1e-9)
        Z_parts.append(z)
    if "highly_variable" in adata.var.columns:
        hvg_mask = adata.var["highly_variable"].values.copy()
        hvg_mask[tidx] = False
        Yh = Y[:, hvg_mask]
        scaler = lambda v: (v - v.mean(axis=0)) / (v.std(axis=0) + 1e-9)
        Yh_std = scaler(Yh)
        U, s, Vt = np.linalg.svd(Yh_std, full_matrices=False)
        K = min(n_pcs, Yh_std.shape[0], Yh_std.shape[1])
        PCs = U[:, :K] * s[:K]
        Z_parts.append(PCs)
    Z = np.column_stack(Z_parts) if Z_parts else np.empty((len(D), 0))
    Zd = np.column_stack([np.ones(len(D)), Z, D_c])
    N, p = Zd.shape

    # Center Y
    Yc = Y - Y.mean(axis=0, keepdims=True)
    other_idx = [i for i in range(Y.shape[1]) if i != tidx]
    Yc_other = Yc[:, other_idx]

    # Vectorized OLS: beta = (Z^T Z)^-1 Z^T Y
    ZtZ_inv = np.linalg.pinv(Zd.T @ Zd)
    beta = ZtZ_inv @ (Zd.T @ Yc_other)  # p x (G-1)
    alpha = beta[-1, :]
    resid = Yc_other - Zd @ beta
    dof = N - p
    sigma2 = (resid ** 2).sum(axis=0) / dof
    se_alpha = np.sqrt(np.diag(ZtZ_inv)[-1] * sigma2)
    t_stat = alpha / (se_alpha + 1e-15)
    p_value = 2 * tdist.sf(np.abs(t_stat), dof)

    res = pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "alpha": alpha,
        "se": se_alpha,
        "t_stat": t_stat,
        "p_value": p_value,
    })

    # ---- Storey-BH with HK pi0 ----
    if hk_genes:
        hk_mask = res["gene"].isin(hk_genes)
        if hk_mask.sum() >= 3:
            hk_p = res.loc[hk_mask, "p_value"].values
            pi0 = min(1.0, np.median(hk_p) * 2)
        else:
            pi0 = 1.0
    else:
        pi0 = 1.0

    m = len(res)
    res = res.sort_values("p_value").reset_index(drop=True)
    res["rank"] = np.arange(1, m + 1)
    res["p_adjusted"] = np.minimum.accumulate(
        (res["p_value"] * m * pi0 / res["rank"]).values[::-1]
    )[::-1]
    res["p_adjusted"] = res["p_adjusted"].clip(upper=1.0)
    res["significant"] = (res["p_adjusted"] < 0.05) & (np.abs(res["alpha"]) > alpha_threshold)

    # Tiers
    res["tier"] = "NS"
    a = np.abs(res["alpha"])
    res.loc[res["significant"] & (a > 0.20), "tier"] = "HIGH"
    res.loc[res["significant"] & (a > 0.15) & (a <= 0.20), "tier"] = "MEDIUM"
    res.loc[res["significant"] & (a > 0.10) & (a <= 0.15), "tier"] = "LOW"
    res = res.sort_values("p_value")
    return res
