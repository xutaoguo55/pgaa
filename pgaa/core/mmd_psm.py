"""
MMD-PSM: Propensity Score Matching + Wasserstein distance for exploratory Perturb-seq ranking.

Scope
-----
Exploratory combination of three classical ideas:

1. Propensity Score Matching (Rosenbaum & Rubin 1983, Biometrika)
   - Originally from observational treatment-effect studies
   - Stratify or match on the conditional probability of treatment
   - Adjusts for measured covariates in the matching model; unmeasured
     confounding can remain

2. MMD / Wasserstein (Gretton et al. 2012; Ramdas et al. 2017)
   - Originally from two-sample testing
   - W_1 distance is sensitive to O(alpha^2) effects (quadratic)

3. Perturb-seq (Norman 2019, Replogle 2022)
   - Each cell has a "treatment dose" (UMI_count)
   - Cells in different states have different response propensities

MMD-PSM exploratory workflow:
  1. Estimate propensity score: P(D=1 | Z) using logistic regression
     on cell type + library size + PCA
  2. For each perturbed cell, find K nearest control cells in
     propensity score space
  3. Compute Wasserstein distance only within matched pairs
  4. Permutation: shuffle matched pair labels

This module is not a primary manuscript contribution and should be treated as
an exploratory ranking workflow rather than as a primary inferential method.

Mathematical formulation
-------------------------
For each gene g:
  W_g = mean_{i in treated} W_1(Y_g[i], Y_g[matched_KNN(i)])
  Null: shuffle matched pair labels within each pair

Interpretation
--------------
The matched-score permutation is a heuristic calibration step for measured
covariates. It does not remove unmeasured confounding and is not used for
formal claims in the manuscript.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


def estimate_propensity(
    X: np.ndarray,
    D: np.ndarray,
    cell_type: Optional[np.ndarray] = None,
    library_size: Optional[np.ndarray] = None,
    n_pcs: int = 5,
    random_state: int = 42,
) -> np.ndarray:
    """
    Estimate P(D=1 | covariates) using logistic regression.

    Returns propensity scores in [0, 1] for each cell.
    """
    n = len(D)
    features = []

    if cell_type is not None:
        ct = pd.Categorical(cell_type)
        ct_dummies = pd.get_dummies(ct, drop_first=True, dtype=float).values
        features.append(ct_dummies)

    if library_size is not None:
        lib_z = (library_size - library_size.mean()) / (library_size.std() + 1e-9)
        features.append(lib_z[:, None])

    # Add first n_pcs as continuous confounders
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=n_pcs, random_state=random_state)
    X_pcs = svd.fit_transform(X)
    features.append(X_pcs)

    Z = np.column_stack(features)

    # Logistic regression for propensity (LR adds intercept automatically)
    lr = LogisticRegression(max_iter=1000, random_state=random_state)
    lr.fit(Z, D.astype(int))
    return lr.predict_proba(Z)[:, 1]


def mmd_psm_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_perms: int = 1000,
    k_neighbors: int = 5,
    cell_type: Optional[np.ndarray] = None,
    library_size: Optional[np.ndarray] = None,
    random_state: int = 42,
    n_jobs: int = 1,
) -> pd.DataFrame:
    """
    MMD-PSM exploratory ranking workflow for all genes.

    Parameters
    ----------
    X : (N, G) log-normalized expression
    genes : list of str
    target : str - the perturbed gene
    perturbed_idx, control_idx : cell indices
    n_perms : int
    k_neighbors : int - K for KNN matching
    """
    rng = np.random.default_rng(random_state)

    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)
    tidx = genes.index(target)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]

    # Estimate propensity
    ct_sub = cell_type[test_idx] if cell_type is not None else None
    lib_sub = library_size[test_idx] if library_size is not None else None
    D = np.zeros(N_sub, dtype=bool)
    D[:len(perturbed_idx)] = True

    propensity = estimate_propensity(X_sub, D, ct_sub, lib_sub, n_pcs=5,
                                    random_state=random_state)
    # Match each treated cell to K nearest controls in propensity space
    treated_pos = np.where(D)[0]
    control_pos = np.where(~D)[0]

    # For each treated cell, find K nearest control cells
    knn = NearestNeighbors(n_neighbors=k_neighbors, n_jobs=n_jobs)
    knn.fit(propensity[control_pos].reshape(-1, 1))
    distances, indices = knn.kneighbors(propensity[treated_pos].reshape(-1, 1))
    # matched_pairs[i, j] = index in control_pos of j-th neighbor of treated_pos[i]
    matched_pairs = control_pos[indices]  # (n_treated, K)

    # Compute observed Wasserstein: for each gene, mean Wasserstein
    # between treated cell and its K matched controls
    Y = X_sub[:, other_idx]
    Y_centered = Y - Y.mean(axis=0, keepdims=True)

    # Vectorized 1D Wasserstein between each treated cell and its K matched
    # controls. For a singleton treated sample, W_1({x}, {y_1, ..., y_K}) is
    # mean_k |x - y_k|; averaging over treated cells gives one score per gene.
    obs_w = np.abs(
        Y_centered[treated_pos, None, :] - Y_centered[matched_pairs, :]
    ).mean(axis=(0, 1))

    # Permutation null: shuffle matched pair assignments
    print(f"MMD-PSM: {n_perms} permutations ...")
    import time
    t0 = time.time()
    null_w = np.zeros((n_perms, len(other_idx)))
    for b in range(n_perms):
        if b % 100 == 0 and b > 0:
            print(f"  perm {b}/{n_perms}, {time.time()-t0:.1f}s")
        # For each treated cell, draw K random control cells (matched by propensity, not random)
        # To break the treatment-matches-control assignment, we shuffle the treated indicator
        # within the propensity score space
        D_perm = rng.permutation(D)
        treated_perm = np.where(D_perm)[0]
        # For each perm-treated cell, find K nearest controls in propensity space
        knn_perm = NearestNeighbors(n_neighbors=k_neighbors)
        knn_perm.fit(propensity[~D_perm].reshape(-1, 1))
        _, idx_perm = knn_perm.kneighbors(propensity[treated_perm].reshape(-1, 1))
        # matched pairs for permuted treatment
        ctrl_pos_perm = np.where(~D_perm)[0]
        matched_perm = ctrl_pos_perm[idx_perm]

        null_w[b] = np.abs(
            Y_centered[treated_perm, None, :] - Y_centered[matched_perm, :]
        ).mean(axis=(0, 1))

    # Two-sided p-value (treating abs difference)
    p_perm = (null_w >= obs_w[None, :]).sum(axis=0) + 1
    p_perm = p_perm / (n_perms + 1)

    return pd.DataFrame({
        "gene": other_genes,
        "W_observed": obs_w,
        "W_null_mean": null_w.mean(axis=0),
        "W_null_std": null_w.std(axis=0),
        "z_score": (obs_w - null_w.mean(axis=0)) / (null_w.std(axis=0) + 1e-15),
        "p_value_perm": p_perm,
    }).sort_values("p_value_perm")
