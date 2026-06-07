# PGAA utilities: residualization, calibration, permutation helpers
# ----------------------------------------------------------------

#' Covariate residualization
#'
#' Regress out covariates Z from expression matrix X.
#'
#' @param X numeric matrix (N cells x G genes)
#' @param cell_type integer vector of length N (cluster labels)
#' @param library_size numeric vector of length N
#' @return numeric matrix of same dimensions as X, residuals after OLS
#' @export
residualize <- function(X, cell_type = NULL, library_size = NULL) {
  N <- nrow(X)
  parts <- list(rep(1, N))  # intercept

  if (!is.null(cell_type)) {
    ct <- factor(cell_type)
    dummies <- model.matrix(~ ct - 1)
    if (ncol(dummies) > 1) {
      parts[[length(parts) + 1]] <- dummies[, -1, drop = FALSE]
    }
  }

  if (!is.null(library_size)) {
    lib <- as.numeric(library_size)
    lib_z <- (lib - mean(lib)) / (stats::sd(lib) + 1e-9)
    parts[[length(parts) + 1]] <- as.matrix(lib_z)
  }

  Z <- do.call(cbind, parts)
  ZtZ_inv <- MASS::ginv(crossprod(Z))
  beta_hat <- ZtZ_inv %*% crossprod(Z, X)
  X - Z %*% beta_hat
}

#' Storey pi0 estimator
#'
#' Estimate the fraction of true null hypotheses from p-values.
#'
#' @param p numeric vector of p-values
#' @param lambda threshold for null tail (default 0.5)
#' @return scalar pi0 estimate, capped at 1.0
#' @export
pi0_storey <- function(p, lambda = 0.5) {
  pi0_hat <- sum(p > lambda) / (lambda * length(p))
  min(max(pi0_hat, 0), 1.0)
}

#' Permutation null for S1 (within-cluster shuffle)
#'
#' @param Y residualized expression matrix (N x G)
#' @param D logical vector of perturbation labels (TRUE = perturbed)
#' @param cell_type integer vector of cluster labels
#' @param n_perms number of permutations
#' @param seed random seed
#' @return list with p_values, null_stats, obs_stat
#' @export
perm_null_s1 <- function(Y, D, cell_type = NULL, n_perms = 2000, seed = 42) {
  set.seed(seed)
  N <- length(D)
  n_pert <- sum(D)
  obs <- vapply(seq_len(ncol(Y)), function(g) {
    wasserstein_1d(Y[D, g], Y[!D, g])
  }, numeric(1))

  null_stats <- matrix(0, nrow = n_perms, ncol = ncol(Y))
  D_int <- as.integer(D)
  unique_ct <- if (!is.null(cell_type)) unique(cell_type) else NULL

  for (b in seq_len(n_perms)) {
    D_perm <- D_int
    if (!is.null(unique_ct)) {
      for (u in unique_ct) {
        mask <- cell_type == u
        if (sum(mask) >= 2) {
          D_perm[mask] <- sample(D_int[mask])
        }
      }
    } else {
      D_perm <- sample(D_int)
    }
    Dp <- as.logical(D_perm)
    Y_on <- Y[Dp, , drop = FALSE]
    Y_off <- Y[!Dp, , drop = FALSE]

    for (g in seq_len(ncol(Y))) {
      null_stats[b, g] <- wasserstein_1d(
        Y_on[, g],
        Y_off[, g]
      )
    }
  }

  p_values <- vapply(seq_len(ncol(Y)), function(g) {
    (sum(null_stats[, g] >= obs[g]) + 1) / (n_perms + 1)
  }, numeric(1))
  list(p_values = p_values, obs_stat = obs, null_stats = null_stats, n_perms = n_perms)
}

#' Permutation null for S2 (within-cluster shuffle)
#'
#' @param Y residualized expression matrix (N x G)
#' @param D logical vector of perturbation labels
#' @param cell_type integer cluster labels
#' @param n_perms number of permutations
#' @param n_bins histogram bins for persistence
#' @param seed random seed
#' @return list with p_values, null_stats, obs_stat
#' @export
perm_null_s2 <- function(Y, D, cell_type = NULL, n_perms = 500,
                          n_bins = 20, seed = 42) {
  set.seed(seed)
  N <- length(D)
  n_pert <- sum(D)
  obs <- vapply(seq_len(ncol(Y)), function(g) {
    g_min <- min(min(Y[D, g]), min(Y[!D, g]))
    g_max <- max(max(Y[D, g]), max(Y[!D, g]))
    bins <- seq(g_min, g_max, length.out = n_bins + 1)
    bc <- (bins[-1] + bins[-(n_bins + 1)]) / 2
    h_on <- graphics::hist(Y[D, g], breaks = bins, plot = FALSE)$density
    h_off <- graphics::hist(Y[!D, g], breaks = bins, plot = FALSE)$density
    pd_on <- compute_persistence_1d(h_on, bc)
    pd_off <- compute_persistence_1d(h_off, bc)
    persistence_landscape_distance(pd_on, pd_off)
  }, numeric(1))

  null_stats <- matrix(0, nrow = n_perms, ncol = ncol(Y))
  D_int <- as.integer(D)
  unique_ct <- if (!is.null(cell_type)) unique(cell_type) else NULL

  for (b in seq_len(n_perms)) {
    D_perm <- D_int
    if (!is.null(unique_ct)) {
      for (u in unique_ct) {
        mask <- cell_type == u
        if (sum(mask) >= 2) {
          D_perm[mask] <- sample(D_int[mask])
        }
      }
    } else {
      D_perm <- sample(D_int)
    }
    Dp <- as.logical(D_perm)
    for (g in seq_len(ncol(Y))) {
      g_min <- min(min(Y[Dp, g]), min(Y[!Dp, g]))
      g_max <- max(max(Y[Dp, g]), max(Y[!Dp, g]))
      bins <- seq(g_min, g_max, length.out = n_bins + 1)
      bc <- (bins[-1] + bins[-(n_bins + 1)]) / 2
      h_on <- graphics::hist(Y[Dp, g], breaks = bins, plot = FALSE)$density
      h_off <- graphics::hist(Y[!Dp, g], breaks = bins, plot = FALSE)$density
      pd_on <- compute_persistence_1d(h_on, bc)
      pd_off <- compute_persistence_1d(h_off, bc)
      null_stats[b, g] <- persistence_landscape_distance(pd_on, pd_off)
    }
  }

  p_values <- vapply(seq_len(ncol(Y)), function(g) {
    (sum(null_stats[, g] >= obs[g]) + 1) / (n_perms + 1)
  }, numeric(1))
  list(p_values = p_values, obs_stat = obs, null_stats = null_stats, n_perms = n_perms)
}

#' Combined z-test from multiple p-value vectors
#'
#' @param ... named arguments, each a numeric vector of p-values
#' @return numeric vector of combined p-values
#' @export
combined_z_test <- function(...) {
  p_list <- list(...)
  k <- length(p_list)

  p_mat <- do.call(cbind, p_list)
  p_mat <- pmax(pmin(p_mat, 1 - 1e-10), 1e-10)
  z_mat <- stats::qnorm(1 - p_mat)
  z_comb <- rowSums(z_mat) / sqrt(k)

  stats::pnorm(z_comb, lower.tail = FALSE)
}
