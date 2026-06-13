# S3: Conditional Mutual Information (exploratory)
# -----------------------------------------------
# Tests whether perturbation changes gene-gene dependency structure.
# Implemented as a stub: full k-NN entropy estimation via FNN package
# would be required for production use.

#' PRT-S3: Conditional mutual information test (exploratory stub)
#'
#' @param X numeric matrix (N cells x G genes)
#' @param genes character vector of gene names
#' @param target character, perturbed gene
#' @param perturbed_idx integer vector
#' @param control_idx integer vector
#' @param n_partners number of neighbour genes for MI estimation
#' @param seed random seed
#' @return data.frame with columns gene and S3
#' @export
prt_s3_test <- function(X, genes, target,
                         perturbed_idx, control_idx,
                         n_partners = 15,
                         seed = 42) {
  set.seed(seed)
  test_idx <- c(perturbed_idx, control_idx)
  X_sub <- X[test_idx, , drop = FALSE]
  N_sub <- length(test_idx)

  tidx <- match(target, genes)
  if (is.na(tidx)) stop("target gene not found in genes vector")
  other_idx <- setdiff(seq_len(ncol(X_sub)), tidx)
  other_genes <- genes[other_idx]

  n_pert <- length(perturbed_idx)
  D <- c(rep(TRUE, n_pert), rep(FALSE, N_sub - n_pert))

  Y <- X_sub[, other_idx, drop = FALSE]

  # For each gene, compute empirical MI change
  # (simplified: covariance-based approximation)
  s3_values <- vapply(seq_along(other_idx), function(g) {
    y <- Y[, g]
    # Find k nearest neighbours in expression space for brevity
    # This is a placeholder; real implementation uses FNN::knn
    cors <- stats::cor(y, Y)
    partners <- order(-abs(cors))[2:min(n_partners + 1, ncol(Y))]

    mi_on <- abs(mean(stats::cor(Y[D, g], Y[D, partners])))
    mi_off <- abs(mean(stats::cor(Y[!D, g], Y[!D, partners])))
    max(0, mi_on - mi_off)
  }, numeric(1))

  data.frame(
    gene = other_genes,
    S3 = s3_values,
    stringsAsFactors = FALSE
  )
}

#' PRT-S4: Fisher NB test (exploratory stub)
#'
#' @param X numeric matrix (N cells x G genes)
#' @param genes character vector of gene names
#' @param target character, perturbed gene
#' @param perturbed_idx integer vector
#' @param control_idx integer vector
#' @param seed random seed
#' @return data.frame with columns gene and S4
#' @export
prt_s4_test <- function(X, genes, target,
                         perturbed_idx, control_idx,
                         seed = 42) {
  set.seed(seed)
  test_idx <- c(perturbed_idx, control_idx)
  X_sub <- X[test_idx, , drop = FALSE]
  N_sub <- length(test_idx)

  tidx <- match(target, genes)
  if (is.na(tidx)) stop("target gene not found in genes vector")
  other_idx <- setdiff(seq_len(ncol(X_sub)), tidx)
  other_genes <- genes[other_idx]

  n_pert <- length(perturbed_idx)
  D <- c(rep(TRUE, n_pert), rep(FALSE, N_sub - n_pert))

  Y <- X_sub[, other_idx, drop = FALSE]

  s4_values <- vapply(seq_along(other_idx), function(g) {
    y <- Y[, g]
    # Fisher information approximation: variance ratio
    var_on <- stats::var(y[D])
    var_off <- stats::var(y[!D])
    mean_on <- mean(y[D])
    mean_off <- mean(y[!D])

    # Combine mean and variance effects
    abs(mean_on - mean_off) * (1 + var_on / (var_off + 1e-9))
  }, numeric(1))

  data.frame(
    gene = other_genes,
    S4 = s4_values,
    stringsAsFactors = FALSE
  )
}
