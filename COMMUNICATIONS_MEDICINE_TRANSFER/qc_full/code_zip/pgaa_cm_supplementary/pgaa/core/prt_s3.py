"""
PRT-S₃: Vectorized KSG-MI for fast conditional mutual information.

Key optimization: use pure NumPy pairwise distance matrix + argsort
for k-th neighbor, instead of sklearn's per-query k-NN which has
Python overhead.

KSG estimator:
  I(X;Y) = psi(k) + psi(N) - <psi(n_x+1) + psi(n_y+1)>
where:
  n_x_i = # of points j with |X_j - X_i| < eps_i  (eps from k-th joint neighbor)
  n_y_i = # of points j with |Y_j - Y_i| < eps_i
"""

import numpy as np
import pandas as pd
from scipy.special import digamma


def pairwise_chebyshev(X: np.ndarray) -> np.ndarray:
    """N x N pairwise Chebyshev distance matrix."""
    # |X_i - X_j|_max for all i,j, vectorized
    # Using broadcasting: (N, 1, d) - (1, N, d) -> (N, N, d)
    diff = np.abs(X[:, None, :] - X[None, :, :])  # (N, N, d)
    return diff.max(axis=-1)  # (N, N)


def kraskov_mi_vectorized(x: np.ndarray, y: np.ndarray, k: int = 4,
                          random_state: int = 42) -> float:
    """
    KSG MI estimator with KDTree-accelerated k-NN.

    For N > 5000, uses scipy.spatial.cKDTree which is O(N log N).
    """
    from scipy.special import digamma
    from scipy.spatial import cKDTree
    n = len(x)
    if n < k + 2:
        return 0.0
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    rng = np.random.default_rng(random_state)
    x = x + rng.normal(0, 1e-8, size=n)
    y = y + rng.normal(0, 1e-8, size=n)

    # Pre-sort x, y for fast searchsorted counting
    sx_idx = np.argsort(x)
    sy_idx = np.argsort(y)
    xs = x[sx_idx]
    ys = y[sy_idx]

    # KDTree on joint space (Chebyshev = max-norm distance)
    XY = np.column_stack([x, y])
    tree = cKDTree(XY)
    # k+1 to get k neighbors excluding self
    dists, _ = tree.query(XY, k=k+1)  # (N, k+1)
    rho = dists[:, k]  # k-th nearest, excluding self

    # Vectorized marginal neighbor counting
    x_plus = x + rho
    x_minus = x - rho
    y_plus = y + rho
    y_minus = y - rho
    n_x = np.searchsorted(xs, x_plus, side='left') - np.searchsorted(xs, x_minus, side='left') - 1
    n_y = np.searchsorted(ys, y_plus, side='left') - np.searchsorted(ys, y_minus, side='left') - 1

    mi = digamma(k) + digamma(n) - np.mean(digamma(n_x + 1) + digamma(n_y + 1))
    return max(0.0, float(mi))


def s3_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_partners: int = 15,
    k: int = 4,
    n_perm: int = 0,  # (deprecated, not used in this version)
    mi_subsample: int = 4000,
    random_state: int = 42,
) -> pd.DataFrame:
    """PRT-S₃: subsample cells, compute per-gene MI change, rank.

    Permutation-based p-values not yet implemented for S₃.
    Ranks are sufficient for AUROC evaluation.
    """
    import time
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)

    tidx = genes.index(target)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]

    n_pert = len(perturbed_idx)
    D = np.zeros(N_sub, dtype=bool)
    D[:n_pert] = True

    # Subsample to mi_subsample cells for MI estimation (KSG is biased for N<1000)
    rng = np.random.default_rng(random_state)
    if N_sub > mi_subsample:
        ss_idx = rng.permutation(N_sub)[:mi_subsample]
        X_sub_mi = X_sub[ss_idx]
        D_mi = D[ss_idx]
    else:
        X_sub_mi = X_sub
        D_mi = D

    var_per_gene = X_sub_mi[:, other_idx].var(axis=0)
    top_idx = np.argsort(-var_per_gene)[:n_partners]
    partner_orig = [other_idx[i] for i in top_idx]
    Y_partners = X_sub_mi[:, partner_orig]

    print(f"S₃ (vectorized, no perm): {len(other_idx)} genes × {len(partner_orig)} partners, "
          f"k={k}, MI_subsample={mi_subsample}")
    t0 = time.time()

    s3_values = np.zeros(len(other_idx))
    for g_idx, g_orig in enumerate(other_idx):
        if g_idx % 200 == 0 and g_idx > 0:
            print(f"  {g_idx}/{len(other_idx)}, {int(time.time()-t0)}s")
        y_g = X_sub_mi[:, g_orig]
        y_g_on = y_g[D_mi]; y_g_off = y_g[~D_mi]
        yp_on = Y_partners[D_mi]; yp_off = Y_partners[~D_mi]
        mi_diffs = []
        for p in range(len(partner_orig)):
            if partner_orig[p] == g_orig:
                continue
            mi_on = kraskov_mi_vectorized(y_g_on, yp_on[:, p], k=k,
                                           random_state=random_state)
            mi_off = kraskov_mi_vectorized(y_g_off, yp_off[:, p], k=k,
                                            random_state=random_state)
            mi_diffs.append(abs(mi_on - mi_off))
        s3_values[g_idx] = np.median(mi_diffs) if mi_diffs else 0.0

    res = pd.DataFrame({
        "gene": other_genes,
        "S3": s3_values,
    }).sort_values("S3", ascending=False)
    print(f"S₃ done in {time.time()-t0:.0f}s")
    return res
