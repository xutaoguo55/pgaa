test_that("compute_persistence_1d handles basic shapes", {
  # Single peak: persistence should be large for tall peak
  h <- c(0.1, 0.3, 0.6, 1.0, 0.6, 0.3, 0.1)
  bc <- seq(-3, 3, length.out = length(h))
  pd <- compute_persistence_1d(h, bc)
  expect_equal(ncol(pd), 3)

  # Flat histogram: no peaks -> single row of zeros
  h_flat <- rep(1, 10)
  bc_flat <- 1:10
  pd_flat <- compute_persistence_1d(h_flat, bc_flat)
  expect_equal(nrow(pd_flat), 1)
  expect_equal(pd_flat[1, 3], 0)
})

test_that("persistence_landscape_distance captures bimodality", {
  # Single-peak histogram
  h1 <- c(0.1, 0.5, 1.0, 0.5, 0.1)
  bc <- 1:5
  pd1 <- compute_persistence_1d(h1, bc)

  # Bimodal histogram
  h2 <- c(0.1, 0.8, 0.3, 0.8, 0.1)
  pd2 <- compute_persistence_1d(h2, bc)

  d <- persistence_landscape_distance(pd1, pd2, n_top = 3)
  expect_gt(d, 0)  # should detect a difference
})

test_that("prt_s2_test returns correct structure", {
  set.seed(42)
  X <- matrix(rnorm(1000 * 30), nrow = 1000, ncol = 30)
  colnames(X) <- paste0("gene_", 1:30)
  genes <- colnames(X)
  pert_idx <- 1:200
  ctrl_idx <- 201:800

  # Add bimodal effect to gene_3 (some cells high, some low)
  X[1:100, 3] <- X[1:100, 3] + 2.0  # half of perturbed cells
  X[101:200, 3] <- X[101:200, 3] - 2.0  # other half

  result <- prt_s2_test(X, genes, target = "gene_1",
                         perturbed_idx = pert_idx,
                         control_idx = ctrl_idx,
                         n_perms = 100, n_bins = 20, seed = 42)
  expect_s3_class(result, "data.frame")
  expect_true(all(c("gene", "S2", "p_value_perm") %in% names(result)))

  # gene_3 should have reasonable rank (bimodal signal)
  expect_true(result$S2[result$gene == "gene_3"] > 0)
})
