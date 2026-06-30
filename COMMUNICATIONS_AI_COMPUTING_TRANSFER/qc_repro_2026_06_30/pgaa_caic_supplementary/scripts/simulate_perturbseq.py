#!/usr/bin/env python3
"""
High-fidelity Perturb-seq simulator with known causal ground truth.

Generates scRNA-seq count data with:
  - latent confounders (cell state)
  - negative-binomial expression
  - dropout (zero-inflation)
  - library size variation
  - causal perturbation effects with known target -> downstream edges
"""

import numpy as np
import pandas as pd
from scipy import sparse
import scanpy as sc


def simulate_perturbseq(
    n_cells: int = 2000,
    n_genes: int = 500,
    n_confounders: int = 5,
    n_targets: int = 10,
    n_downstream_per_target: int = 20,
    theta_mean: float = 0.30,
    theta_std: float = 0.10,
    dropout_rate: float = 0.10,
    overdispersion: float = 2.0,
    fraction_perturbed: float = 0.5,
    seed: int = 42,
):
    """
    Simulate Perturb-seq-like data.

    Parameters
    ----------
    n_cells, n_genes
        Dataset size.
    n_confounders
        Number of latent cell-state factors.
    n_targets
        Number of genes that will be artificially perturbed.
    n_downstream_per_target
        Number of true downstream genes per target.
    theta_mean, theta_std
        Gaussian prior on true causal coefficients (log-scale fold-change).
    dropout_rate
        Global dropout probability scale.
    overdispersion
        NB dispersion parameter (alpha). Larger = less overdispersed.
    fraction_perturbed
        Fraction of cells receiving perturbation.
    seed
        Random seed.

    Returns
    -------
    adata : AnnData
        .X = raw counts (int sparse matrix)
        .obs['perturbation'] = target gene name or 'control'
        .var_names = gene names
        .uns['ground_truth'] = DataFrame columns [target, downstream, theta]
    """
    rng = np.random.default_rng(seed)

    # Confounders
    Z = rng.normal(size=(n_cells, n_confounders))  # N x K

    # Baseline gene parameters
    beta = rng.normal(size=(n_confounders, n_genes), scale=0.5)  # K x G
    intercept = rng.lognormal(mean=1.5, sigma=1.0, size=n_genes)  # G

    # Mean log-expression
    mu_log = Z @ beta + intercept  # N x G
    mu_log = np.clip(mu_log, -2, 8)
    mu = np.exp(mu_log)

    # Library size variation
    lib_size = rng.lognormal(mean=0, sigma=0.3, size=n_cells)[:, None]  # N x 1
    mu = mu * lib_size

    # Negative-binomial counts
    # parameterisation: n = 1/alpha, p = n/(n+mu)
    alpha = 1.0 / overdispersion
    n_nb = 1.0 / alpha
    p_nb = n_nb / (n_nb + mu)
    counts = rng.negative_binomial(n_nb, p_nb)  # N x G

    # Dropout (zero-inflation) – higher dropout for lowly-expressed genes
    dropout_prob = dropout_rate * np.exp(-mu_log)
    dropout_prob = np.clip(dropout_prob, 0, 0.8)
    mask = rng.random(counts.shape) < dropout_prob
    counts[mask] = 0

    # Gene and cell names
    gene_names = [f"gene_{i:04d}" for i in range(n_genes)]
    cell_names = [f"cell_{i:04d}" for i in range(n_cells)]

    # Choose targets and downstream genes
    target_idx = rng.choice(n_genes, size=n_targets, replace=False)
    downstream_map = {}
    gt_rows = []
    for tidx in target_idx:
        available = [i for i in range(n_genes) if i != tidx]
        didx = rng.choice(available, size=n_downstream_per_target, replace=False)
        thetas = rng.normal(loc=theta_mean, scale=theta_std, size=n_downstream_per_target)
        # half negative
        flip = rng.random(n_downstream_per_target) < 0.3
        thetas[flip] = -thetas[flip]
        downstream_map[tidx] = (didx, thetas)
        for d, th in zip(didx, thetas):
            gt_rows.append({
                "target": gene_names[tidx],
                "downstream": gene_names[d],
                "theta": float(th),
            })
    gt_df = pd.DataFrame(gt_rows)

    # Assign perturbation labels
    n_pert = int(n_cells * fraction_perturbed)
    pert_cells = rng.choice(n_cells, size=n_pert, replace=False)
    pert_labels = np.full(n_cells, "control", dtype=object)
    # round-robin assign targets to perturbed cells
    for i, cidx in enumerate(pert_cells):
        tidx = target_idx[i % n_targets]
        pert_labels[cidx] = gene_names[tidx]
        # Apply perturbation
        # KO: set target gene to near-zero counts
        counts[cidx, tidx] = rng.poisson(0.5)
        # Downstream effect (multiplicative on mean)
        didx_list, thetas = downstream_map[tidx]
        for d, th in zip(didx_list, thetas):
            # fold-change in log-space
            fc = np.exp(th)
            new_mu = counts[cidx, d] * fc
            counts[cidx, d] = rng.poisson(np.clip(new_mu, 0, 500))

    adata = sc.AnnData(
        X=sparse.csr_matrix(counts, dtype=np.int32),
        obs=pd.DataFrame({"perturbation": pert_labels}, index=cell_names),
        var=pd.DataFrame(index=gene_names),
    )
    adata.uns["ground_truth"] = gt_df
    return adata


if __name__ == "__main__":
    ad = simulate_perturbseq(
        n_cells=1000,
        n_genes=200,
        n_confounders=5,
        n_targets=5,
        n_downstream_per_target=10,
        seed=42,
    )
    print(ad)
    print(ad.obs["perturbation"].value_counts())
    print("Ground-truth edges:", len(ad.uns["ground_truth"]))
