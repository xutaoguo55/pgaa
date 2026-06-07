# pgaa (R package)

R implementation of PGAA: Perturbation-response Generalized Association Analysis
for single-cell perturbation screens.

## Installation

```r
# From local directory
install.packages("pgaa_r", repos = NULL, type = "source")

# From GitHub (after pushing)
# remotes::install_github("username/pgaa_r")
```

## Quick start

```r
library(pgaa)

# Load a Perturb-seq dataset (log-normalized expression matrix X)
# X: N cells x G genes
# pert_idx: indices of perturbed cells
# ctrl_idx: indices of control cells
# genes: character vector of gene names

# S1 (Wasserstein)
res_s1 <- prt_s1_test(X, genes, target = "MYC",
                       perturbed_idx = pert_idx,
                       control_idx = ctrl_idx,
                       n_perms = 2000)

# S2 (Persistent Homology)
res_s2 <- prt_s2_test(X, genes, target = "MYC",
                       perturbed_idx = pert_idx,
                       control_idx = ctrl_idx,
                       n_perms = 500, n_bins = 20)

# Calibration diagnostics
pi0_s1 <- pi0_storey(res_s1$p_value_perm)
pi0_s2 <- pi0_storey(res_s2$p_value_perm)

# Combined test
p_combined <- combined_z_test(res_s1$p_value_perm, res_s2$p_value_perm)
```

## Main functions

| Function | Description |
|---|---|
| `prt_s1_test()` | S₁ Wasserstein distance test |
| `prt_s2_test()` | S₂ persistent homology test |
| `prt_s3_test()` | S₃ conditional MI test (exploratory) |
| `prt_s4_test()` | S₄ Fisher NB test (exploratory) |
| `wasserstein_1d()` | 1D Wasserstein distance (low-level) |
| `compute_persistence_1d()` | 1D persistence diagram from histogram (low-level) |
| `persistence_landscape_distance()` | L2 distance between top-N persistence values |
| `residualize()` | Covariate residualization |
| `pi0_storey()` | Storey π̂₀ estimator |
| `perm_null_s1()` | Permutation null for S₁ |
| `perm_null_s2()` | Permutation null for S₂ |
| `combined_z_test()` | Combined z statistic from multiple p-value vectors |

## Differences from Python pgaa

The R and Python implementations produce statistically equivalent
results (within Monte Carlo noise for permutation tests). Key differences:
- R uses `graphics::hist()` instead of `numpy.histogram()` for S₂
- Default `n_bins = 20` in both packages
- Default `n_perms = 2000` (S₁), `500` (S₂) in both
- `MASS::ginv()` for pseudoinverse in residualization (Python uses `np.linalg.pinv`)

## Citation

If you use pgaa in your research, please cite:
[Paper reference to be added upon publication]
