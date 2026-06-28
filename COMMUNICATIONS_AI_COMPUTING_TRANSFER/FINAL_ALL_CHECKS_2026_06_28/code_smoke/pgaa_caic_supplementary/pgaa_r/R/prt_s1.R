# PGAA-W / legacy S1: 1D Wasserstein distance
# ---------------------------
# For each gene g:
#   PGAA-W_g = W(F(Y_g | D=1), F(Y_g | D=0))
#        = integral |F1(t) - F0(t)| dt
#   Approx via quantile average on q = 0.01 .. 0.99

#' 1D Wasserstein distance via quantile average
#'
#' @param x numeric vector (perturbed group)
#' @param y numeric vector (control group)
#' @param n_quantiles number of quantile points
#' @return scalar Wasserstein distance
#' @export
#'
#' @examples
#' x <- rnorm(100, mean = 0.5)
#' y <- rnorm(100, mean = 0)
#' wasserstein_1d(x, y)
wasserstein_1d <- function(x, y, n_quantiles = 99) {
  if (any(is.na(x)) || any(is.na(y))) stop("Input contains NA values")
  if (any(is.infinite(x)) || any(is.infinite(y))) stop("Input contains Inf values")
  if (length(x) == 0 || length(y) == 0) stop("Input arrays must not be empty")
  q <- seq(0.01, 0.99, length.out = n_quantiles)
  x_q <- stats::quantile(x, q, names = FALSE)
  y_q <- stats::quantile(y, q, names = FALSE)
  mean(abs(x_q - y_q))
}

#' PGAA-W / legacy PRT-S1: Wasserstein ranking statistic
#'
#' Full PGAA-W ranking workflow with covariate residualization, within-cluster
#' permutation, and Storey upper-tail calibration.
#'
#' @param X numeric matrix (N cells x G genes), log-normalized
#' @param genes character vector of gene names
#' @param target character, name of the perturbed gene
#' @param perturbed_idx integer vector, indices of perturbed cells
#' @param control_idx integer vector, indices of control cells
#' @param n_perms number of permutations (default 2000)
#' @param cell_type integer vector of cluster labels (optional)
#' @param library_size numeric vector of library sizes (optional)
#' @param seed random seed
#' @return data.frame with columns: gene, W_observed, p_value_perm
#' @export
prt_s1_test <- function(X, genes, target,
                         perturbed_idx, control_idx,
                         n_perms = 2000,
                         cell_type = NULL,
                         library_size = NULL,
                         seed = 42) {
  test_idx <- c(perturbed_idx, control_idx)
  X_sub <- X[test_idx, , drop = FALSE]
  N_sub <- length(test_idx)

  tidx <- match(target, genes)
  if (is.na(tidx)) stop("target gene not found in genes vector")
  other_idx <- setdiff(seq_len(ncol(X_sub)), tidx)
  other_genes <- genes[other_idx]

  # Residualize
  ct_sub <- if (!is.null(cell_type)) cell_type[test_idx] else NULL
  lib_sub <- if (!is.null(library_size)) library_size[test_idx] else NULL
  Y_sub <- residualize(X_sub, ct_sub, lib_sub)
  Y <- Y_sub[, other_idx, drop = FALSE]

  n_pert <- length(perturbed_idx)
  D <- c(rep(TRUE, n_pert), rep(FALSE, N_sub - n_pert))

  # Run permutation null (seed set inside perm_null_s1 for reproducibility)
  result <- perm_null_s1(Y, D, cell_type = ct_sub,
                          n_perms = n_perms, seed = seed)

  data.frame(
    gene = other_genes,
    W_observed = result$obs_stat,
    p_value_perm = result$p_values,
    stringsAsFactors = FALSE
  )
}
