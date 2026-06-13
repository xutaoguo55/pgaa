"""
PRT-S₂: 1D Persistent Homology for Perturbation Detection

Mathematical foundation
-----------------------
For a 1D function f(x) (estimated via histogram/KDE), the persistence
diagram PD(f) = {(b_i, d_i)} where:
  - b_i = birth level (peak maximum)
  - d_i = death level (saddle connecting two peaks)
  - persistence = b_i - d_i

For two samples X~P and Y~Q, we compute:
  PD_X = persistence_diagram(histogram(X))
  PD_Y = persistence_diagram(histogram(Y))
  S₂ = bottleneck_distance(PD_X, PD_Y)  (or L2 landscape distance)

Computational shortcut for 1D
-----------------------------
In 1D, the persistence diagram can be computed by:
  1. Computing the level-set tree of the histogram
  2. Each local maximum corresponds to a connected component
  3. The "death" of a component occurs when its basin merges with
     a higher component

For a discrete histogram h[0..n-1], the persistence pairs are:
  For each local maximum at index i with height h[i]:
    Find the lowest saddle to its left (local min between i and next higher peak)
    Find the lowest saddle to its right
    death = max(left_saddle, right_saddle)
    persistence = h[i] - death

This is equivalent to the Elder Rule in persistent homology.

Innovation for Perturb-seq
---------------------------
S₂ measures changes in the TOPOLOGY of gene expression distributions
under perturbation:
  - If a gene switches from unimodal to bimodal → S₂ increases
  - This captures "bimodality shifts" (e.g. ON/OFF states) that
    mean-based tests (t-test, W1) miss

Reference
---------
  - Edelsbrunner & Harer (2010) Computational Topology
  - Bubenik (2015) Statistical Topological Data Analysis using
    Persistence Landscapes
"""

import numpy as np
import pandas as pd


def compute_persistence_1d(hist: np.ndarray, bins: np.ndarray) -> np.ndarray:
    """
    Compute 1D persistence diagram from histogram.

    Parameters
    ----------
    hist : histogram counts (length n)
    bins : bin centers (length n)

    Returns
    -------
    persistence : array of (birth, death, persistence) for each peak
        sorted by persistence descending
    """
    n = len(hist)
    # Find local maxima (peaks)
    peaks = []
    for i in range(1, n - 1):
        if hist[i] > hist[i - 1] and hist[i] > hist[i + 1]:
            peaks.append(i)

    if len(peaks) == 0:
        return np.zeros((1, 3))

    # For each peak, find the saddle to left and right
    result = []
    for p_idx in peaks:
        # Left saddle: lowest point between this peak and previous peak
        left_saddle = hist[p_idx]
        for j in range(p_idx - 1, -1, -1):
            if hist[j] > hist[p_idx]:
                break
            if hist[j] < left_saddle:
                left_saddle = hist[j]

        # Right saddle
        right_saddle = hist[p_idx]
        for j in range(p_idx + 1, n):
            if hist[j] > hist[p_idx]:
                break
            if hist[j] < right_saddle:
                right_saddle = hist[j]

        death = max(left_saddle, right_saddle)
        birth = hist[p_idx]
        persistence = max(0.0, birth - death)
        result.append([birth, death, persistence])

    if not result:
        return np.zeros((1, 3))
    result = np.array(result)
    # Sort by persistence descending
    result = result[np.argsort(-result[:, 2])]
    return result


def persistence_landscape_distance(
    pd1: np.ndarray, pd2: np.ndarray, n_top: int = 3
) -> float:
    """
    L2 distance between top-n persistence values.

    If two diagrams have different numbers of peaks, pad with zeros.
    """
    # Take top n persistence values
    p1 = pd1[:n_top, 2] if len(pd1) >= n_top else np.pad(
        pd1[:, 2], (0, n_top - len(pd1)), 'constant'
    )
    p2 = pd2[:n_top, 2] if len(pd2) >= n_top else np.pad(
        pd2[:, 2], (0, n_top - len(pd2)), 'constant'
    )
    return float(np.sqrt(np.mean((p1 - p2) ** 2)))


def s2_test(
    X: np.ndarray,
    genes: list,
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_bins: int = 100,
    cell_type: np.ndarray = None,
    library_size: np.ndarray = None,
) -> pd.DataFrame:
    """
    PRT-S₂: Persistence homology test.

    For each gene g:
      1. Compute histogram of Y_g | D=1 and Y_g | D=0
      2. Compute persistence diagrams
      3. S₂_g = landscape distance between diagrams
    """
    test_idx = np.concatenate([perturbed_idx, control_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)

    if n_bins < 2:
        raise ValueError(f"n_bins must be >= 2, got {n_bins}")
    if len(perturbed_idx) == 0:
        raise ValueError("perturbed_idx is empty — need at least one perturbed cell")
    if len(control_idx) == 0:
        raise ValueError("control_idx is empty — need at least one control cell")

    genes = list(genes)  # ensure list for .index()
    tidx = genes.index(target)
    other_idx = [i for i in range(len(genes)) if i != tidx]
    other_genes = [genes[i] for i in other_idx]

    n_pert = len(perturbed_idx)
    D = np.zeros(N_sub, dtype=bool)
    D[:n_pert] = True

    # Optional confounder residualization (same as S₁)
    if cell_type is not None or library_size is not None:
        parts = [np.ones(N_sub)]
        if cell_type is not None:
            ct = pd.Categorical(cell_type[test_idx])
            ct_dummies = pd.get_dummies(ct, drop_first=True, dtype=float).values
            parts.append(ct_dummies)
        if library_size is not None:
            lib = library_size[test_idx].astype(np.float64)
            lib_z = (lib - lib.mean()) / (lib.std() + 1e-9)
            parts.append(lib_z[:, None])
        Z = np.column_stack(parts)
        Y_sub = X_sub - Z @ np.linalg.pinv(Z.T @ Z) @ (Z.T @ X_sub)
    else:
        Y_sub = X_sub

    Y = Y_sub[:, other_idx]
    Y_on = Y[D]
    Y_off = Y[~D]

    # Global bin edges (shared across genes)
    global_min = Y_sub.min()
    global_max = Y_sub.max()
    bins = np.linspace(global_min, global_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    s2_values = np.zeros(len(other_idx))
    import time
    t0 = time.time()
    for g in range(len(other_idx)):
        if g % 200 == 0 and g > 0:
            elapsed = time.time() - t0
            eta = elapsed / g * (len(other_idx) - g)
            print(f"  S₂: {g}/{len(other_idx)}, {int(elapsed)}s, ~{int(eta)}s left")

        h_on, _ = np.histogram(Y_on[:, g], bins=bins, density=True)
        h_off, _ = np.histogram(Y_off[:, g], bins=bins, density=True)

        pd_on = compute_persistence_1d(h_on, bin_centers)
        pd_off = compute_persistence_1d(h_off, bin_centers)

        s2_values[g] = persistence_landscape_distance(pd_on, pd_off)

    # Compute n_peaks_on efficiently (one pass)
    n_peaks_on = np.array([
        len(compute_persistence_1d(
            np.histogram(Y_on[:, g], bins=bins, density=True)[0], bin_centers
        )) for g in range(len(other_idx))
    ])
    res = pd.DataFrame({
        "gene": other_genes,
        "S2": s2_values,
        "n_peaks_on": n_peaks_on,
    }).sort_values("S2", ascending=False)

    return res
