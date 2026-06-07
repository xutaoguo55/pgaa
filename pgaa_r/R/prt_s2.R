# S2: 1D Persistent Homology
# ---------------------------
# For each gene g:
#   1. Compute histogram of Y_g | D=1 and Y_g | D=0
#   2. Find peaks and saddles (1D persistence / Elder Rule)
#   3. S2_g = L2 distance between top-3 persistence pairs

#' Compute 1D persistence diagram from histogram
#'
#' Returns sorted persistence pairs (birth, death, persistence) for each peak.
#' Uses the Elder Rule: death is the max of left/right saddles.
#'
#' @param hist numeric vector of histogram counts
#' @param bins numeric vector of bin centers
#' @return matrix with columns birth, death, persistence; sorted by persistence desc
#' @export
compute_persistence_1d <- function(hist, bins) {
  n <- length(hist)
  if (n < 3) return(matrix(0, nrow = 1, ncol = 3))

  # Find local maxima
  peaks <- which(hist[2:(n-1)] > hist[1:(n-2)] & hist[2:(n-1)] > hist[3:n]) + 1
  peak_vals <- hist[peaks]

  if (length(peaks) == 0) return(matrix(0, nrow = 1, ncol = 3))

  # For each peak, find saddle
  result <- matrix(0, nrow = length(peaks), ncol = 3)
  for (i in seq_along(peaks)) {
    p_idx <- peaks[i]
    birth <- hist[p_idx]

    # Left saddle
    left_saddle <- birth
    for (j in p_idx:1) {
      if (hist[j] > birth) break
      if (hist[j] < left_saddle) left_saddle <- hist[j]
    }

    # Right saddle
    right_saddle <- birth
    for (j in p_idx:n) {
      if (hist[j] > birth) break
      if (hist[j] < right_saddle) right_saddle <- hist[j]
    }

    death <- max(left_saddle, right_saddle)
    persistence <- max(0, birth - death)
    result[i, ] <- c(birth, death, persistence)
  }

  if (nrow(result) == 0) return(matrix(0, nrow = 1, ncol = 3))

  # Sort by persistence descending
  result <- result[order(-result[, 3]), , drop = FALSE]
  result
}

#' L2 distance between top-N persistence values
#'
#' @param pd1 persistence diagram matrix (n x 3)
#' @param pd2 persistence diagram matrix (m x 3)
#' @param n_top number of top persistence values to use (default 3)
#' @return scalar L2 distance
#' @export
persistence_landscape_distance <- function(pd1, pd2, n_top = 3) {
  get_top <- function(pd, k) {
    if (nrow(pd) >= k) {
      pd[1:k, 3]
    } else {
      c(pd[, 3], rep(0, k - nrow(pd)))
    }
  }
  p1 <- get_top(pd1, n_top)
  p2 <- get_top(pd2, n_top)
  sqrt(mean((p1 - p2)^2))
}

#' PRT-S2: Persistent homology perturbation test
#'
#' Full S2 test with covariate residualization, within-cluster
#' permutation, and Storey pi0 calibration.
#'
#' @param X numeric matrix (N cells x G genes), log-normalized
#' @param genes character vector of gene names
#' @param target character, name of the perturbed gene
#' @param perturbed_idx integer vector, indices of perturbed cells
#' @param control_idx integer vector, indices of control cells
#' @param n_perms number of permutations (default 500)
#' @param n_bins number of histogram bins (default 20)
#' @param cell_type integer vector of cluster labels (optional)
#' @param library_size numeric vector of library sizes (optional)
#' @param seed random seed
#' @return data.frame with columns: gene, S2, p_value_perm
#' @export
prt_s2_test <- function(X, genes, target,
                         perturbed_idx, control_idx,
                         n_perms = 500,
                         n_bins = 20,
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

  result <- perm_null_s2(Y, D, cell_type = ct_sub,
                          n_perms = n_perms, n_bins = n_bins,
                          seed = seed)

  data.frame(
    gene = other_genes,
    S2 = result$obs_stat,
    p_value_perm = result$p_values,
    stringsAsFactors = FALSE
  )
}
