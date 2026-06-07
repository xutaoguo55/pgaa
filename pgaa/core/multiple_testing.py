"""Multiple testing correction utilities."""

import numpy as np
import pandas as pd
from scipy import interpolate, stats


def apply_fdr(
    df: pd.DataFrame,
    p_col: str = "p_value",
    method: str = "bh",
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Apply FDR correction to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
    p_col : str
        Column containing raw p-values.
    method : str
        'bh' (Benjamini-Hochberg) or 'by' (Benjamini-Yekutieli).
    alpha : float
        FDR threshold.

    Returns
    -------
    pd.DataFrame with added columns 'p_adjusted' and 'significant'.
    """
    pvals = df[p_col].values.copy()
    pvals[np.isnan(pvals)] = 1.0

    m = len(pvals)
    if m == 0:
        df["p_adjusted"] = np.nan
        df["significant"] = False
        return df

    if method == "bh":
        # Benjamini-Hochberg
        order = np.argsort(pvals)
        p_sorted = pvals[order]
        ranks = np.arange(1, m + 1)
        thresholds = ranks / m * alpha
        # step-up
        below = p_sorted <= thresholds
        if np.any(below):
            max_rank = np.max(ranks[below])
            adj = np.minimum.accumulate(p_sorted[::-1])[::-1]
            adj = np.minimum(adj * m / ranks, 1.0)
        else:
            max_rank = 0
            adj = np.minimum(p_sorted * m / ranks, 1.0)

        p_adj = np.empty(m)
        p_adj[order] = adj
        sig = np.zeros(m, dtype=bool)
        if max_rank > 0:
            sig[order[:max_rank]] = True

    elif method == "by":
        # Benjamini-Yekutieli (valid under arbitrary dependence)
        cm = np.sum(1.0 / np.arange(1, m + 1))
        order = np.argsort(pvals)
        p_sorted = pvals[order]
        ranks = np.arange(1, m + 1)
        adj = np.minimum.accumulate(p_sorted[::-1] * cm * m / ranks[::-1])[::-1]
        adj = np.minimum(adj, 1.0)
        p_adj = np.empty(m)
        p_adj[order] = adj
        sig = p_adj <= alpha

    else:
        raise ValueError(f"Unknown method: {method}")

    df = df.copy()
    df["p_adjusted"] = p_adj
    df["significant"] = sig
    return df


def apply_storey_qvalue(
    pvals: np.ndarray,
    lambda_val: float = 0.5,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Storey's q-value procedure (adaptive FDR).

    Parameters
    ----------
    pvals : np.ndarray
        Raw p-values.
    lambda_val : float
        Tuning parameter for pi0 estimation.
    alpha : float
        FDR threshold.

    Returns
    -------
    pd.DataFrame with columns p_value, q_value, significant.
    """
    pvals = np.asarray(pvals)
    m = len(pvals)
    pvals_clean = np.where(np.isnan(pvals), 1.0, pvals)

    # Estimate pi0
    pi0 = min((np.sum(pvals_clean > lambda_val) / m) / (1 - lambda_val), 1.0)

    order = np.argsort(pvals_clean)
    p_sorted = pvals_clean[order]
    ranks = np.arange(1, m + 1)

    # q-value
    qvals_sorted = np.minimum.accumulate(
        (pi0 * m * p_sorted / ranks)[::-1]
    )[::-1]
    qvals_sorted = np.minimum(qvals_sorted, 1.0)

    qvals = np.empty(m)
    qvals[order] = qvals_sorted

    return pd.DataFrame({
        "p_value": pvals,
        "q_value": qvals,
        "significant": qvals <= alpha,
    })
