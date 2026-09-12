"""
PRT: Perturbation Response Thermodynamics
S₁ statistic: 1D Wasserstein distance (a.k.a. Earth Mover's Distance)

For each gene g, compute:
  PGAA-W_g = W(F(Y_g | D=1), F(Y_g | D=0))
       = ∫ |F1^{-1}(q) - F0^{-1}(q)| dq

The statistic is evaluated by the same quantile approximation for observed
and permuted labels, so the permutation p-values compare like with like.

Reference:
  - Ramdas et al. 2017 "On Wasserstein Two-Sample Testing"
  - PGAA uses this quantile-grid summary as a perturbation-response
    ranking statistic, not as causal identification by itself.
"""

from typing import Tuple
import numpy as np
import pandas as pd


def wasserstein_1d(x: np.ndarray, y: np.ndarray) -> float:
    """
    1D Wasserstein distance between two samples (quantile-based).

    W_1 = ∫|F_x^{-1}(t) - F_y^{-1}(t)| dt
    Approximated via np.quantile at p = 0.01, 0.02, ..., 0.99.
    This avoids interpolation artifacts when sample sizes differ.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("Input contains NaN values")
    if np.any(np.isinf(x)) or np.any(np.isinf(y)):
        raise ValueError("Input contains Inf values")
    if len(x) == 0 or len(y) == 0:
        raise ValueError("Input arrays must not be empty")
    q = np.linspace(0.01, 0.99, 99)
    x_q = np.quantile(x, q)
    y_q = np.quantile(y, q)
    return float(np.mean(np.abs(x_q - y_q)))


def wasserstein_1d_by_column(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Column-wise version of ``wasserstein_1d`` using the same quantile grid."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("Input contains NaN values")
    if np.any(np.isinf(x)) or np.any(np.isinf(y)):
        raise ValueError("Input contains Inf values")
    if x.shape[0] == 0 or y.shape[0] == 0:
        raise ValueError("Input arrays must not be empty")
    q = np.linspace(0.01, 0.99, 99)
    x_q = np.quantile(x, q, axis=0)
    y_q = np.quantile(y, q, axis=0)
    return np.mean(np.abs(x_q - y_q), axis=0)


def prt_s1_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_perms: int = 2000,
    cell_type: np.ndarray = None,
    library_size: np.ndarray = None,
    random_state: int = 42,
    target_only_permutation_p: bool = False,
):
    """
    PRT S₁ ranking statistic for all genes given target perturbation.

    Parameters
    ----------
    X : (N, G) log-normalized expression
    genes : list of str
    target : str - perturbed gene
    perturbed_idx, control_idx : cell indices
    n_perms : int
    cell_type, library_size : optional covariates
    """
    if random_state < 0:
        raise ValueError(f"random_state must be non-negative, got {random_state}")
    if len(perturbed_idx) == 0:
        raise ValueError("perturbed_idx is empty")
    if len(control_idx) == 0:
        raise ValueError("control_idx is empty")
    if n_perms < 0:
        raise ValueError(f"n_perms must be non-negative, got {n_perms}")
    genes = list(genes)  # ensure list (not numpy array) for .index()
    if len(set(genes)) != len(genes):
        raise ValueError("Duplicate gene names in genes list")
    if X.shape[1] != len(genes):
        raise ValueError(f"X has {X.shape[1]} columns but genes has {len(genes)} entries")
    rng = np.random.default_rng(random_state)
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)
    if target not in genes:
        raise ValueError(f"Target gene '{target}' is not in genes list")
    tidx = genes.index(target)
    gene_idx = list(range(len(genes)))

    # Optional: residualize for cell type + library size
    if cell_type is not None or library_size is not None:
        parts = [np.ones(N_sub)]
        if cell_type is not None:
            ct = np.asarray(cell_type[test_idx])
            unique_ct_local = np.unique(ct)
            n_unique = len(unique_ct_local)
            ct_dummies = np.zeros((N_sub, n_unique))
            for k, u in enumerate(unique_ct_local):
                ct_dummies[ct == u, k] = 1.0
            if n_unique > 1:
                ct_dummies = ct_dummies[:, 1:]
            parts.append(ct_dummies)
        if library_size is not None:
            lib = library_size[test_idx].astype(np.float64)
            lib_z = (lib - lib.mean()) / (lib.std() + 1e-9)
            parts.append(lib_z[:, None])
        Z_base = np.column_stack(parts)
        ZtZ_inv = np.linalg.pinv(Z_base.T @ Z_base)
        Y_sub = X_sub - Z_base @ (ZtZ_inv @ (Z_base.T @ X_sub))
    else:
        Y_sub = X_sub

    Y_other = Y_sub[:, gene_idx]
    n_pert = len(perturbed_idx)
    n_ctrl = len(control_idx)
    D = np.zeros(N_sub, dtype=bool)
    D[:n_pert] = True

    # Observed: Wasserstein distance per gene
    obs_w = wasserstein_1d_by_column(Y_other[D], Y_other[~D])

    # Permutation null - vectorized: for each perm, compute Wasserstein for ALL genes
    # CONDITIONAL permutation: shuffle D WITHIN each cell type cluster
    # This removes cell type confounding while preserving D's within-cluster effect
    import time
    print(f"PGAA-W / legacy PRT-S1: {n_perms} permutations (within-cluster shuffle) ...")
    t0 = time.time()
    if target_only_permutation_p:
        null_w_target = np.zeros(n_perms)
    else:
        null_w = np.zeros((n_perms, len(gene_idx)))

    # If cell_type provided, do within-cluster shuffle; else global shuffle
    if cell_type is not None:
        ct_sub = cell_type[test_idx].astype(int)
        unique_ct = np.unique(ct_sub)
        # Build index: for each cell, where does it go in D?
        D_int = D.astype(int)
    else:
        ct_sub = None

    for b in range(n_perms):
        if b % 100 == 0 and b > 0:
            print(f"  perm {b}/{n_perms}, {time.time()-t0:.1f}s")
        if ct_sub is not None:
            # Within-cluster shuffle: keep cluster structure but randomize D
            D_perm = D_int.copy()
            for u in unique_ct:
                mask = ct_sub == u
                D_perm[mask] = rng.permutation(D_int[mask])
            D_perm = D_perm.astype(bool)
        else:
            D_perm = rng.permutation(D)
        if target_only_permutation_p:
            null_w_target[b] = wasserstein_1d(Y_sub[D_perm, tidx], Y_sub[~D_perm, tidx])
        else:
            Y_pert_perm = Y_other[D_perm]
            Y_ctrl_perm = Y_other[~D_perm]
            null_w[b] = wasserstein_1d_by_column(Y_pert_perm, Y_ctrl_perm)

    # Standardized Wasserstein: W_std = W * sqrt(min(n_pert, n_ctrl))
    scale = np.sqrt(min(n_pert, n_ctrl))
    obs_std = obs_w * scale

    if n_perms > 0:
        if target_only_permutation_p:
            p_perm = np.full(len(gene_idx), np.nan)
            null_mean = np.full(len(gene_idx), np.nan)
            null_sd = np.full(len(gene_idx), np.nan)
            z_score = np.full(len(gene_idx), np.nan)
            null_std_target = null_w_target * scale
            p_perm[tidx] = ((null_w_target >= obs_w[tidx]).sum() + 1) / (n_perms + 1)
            null_mean[tidx] = null_std_target.mean()
            null_sd[tidx] = null_std_target.std()
            z_score[tidx] = (obs_std[tidx] - null_mean[tidx]) / (null_sd[tidx] + 1e-15)
        else:
            p_perm = (null_w >= obs_w[None, :]).sum(axis=0) + 1
            p_perm = p_perm / (n_perms + 1)
            null_std = null_w * scale
            null_mean = null_std.mean(axis=0)
            null_sd = null_std.std(axis=0)
            z_score = (obs_std - null_mean) / (null_sd + 1e-15)
    else:
        p_perm = np.full(len(gene_idx), np.nan)
        null_mean = np.zeros(len(gene_idx))
        null_sd = np.ones(len(gene_idx))
        z_score = np.zeros(len(gene_idx))

    res = pd.DataFrame({
        "gene": genes,
        "W_observed": obs_w,
        "W_std_observed": obs_std,
        "W_null_mean": null_mean,
        "W_null_std": null_sd,
        "z_score": z_score,
        "p_value_perm": p_perm,
    })
    return res
