test_that("wasserstein_1d works for simple cases", {
  # Same distribution -> W close to 0
  set.seed(42)
  x <- rnorm(1000, mean = 2)
  y <- rnorm(1000, mean = 2)
  w <- wasserstein_1d(x, y)
  expect_lt(w, 0.2)  # should be very small

  # Shifted mean -> W > 0
  y2 <- rnorm(1000, mean = 3)
  w2 <- wasserstein_1d(x, y2)
  expect_gt(w2, 0.5)
})

test_that("prt_s1_test returns correct structure", {
  set.seed(42)
  # Simulate simple data
  X <- matrix(rnorm(2000 * 50), nrow = 2000, ncol = 50)
  colnames(X) <- paste0("gene_", 1:50)
  genes <- colnames(X)
  pert_idx <- 1:500
  ctrl_idx <- 501:1500

  # Add a small effect to gene_2
  X[1:500, 2] <- X[1:500, 2] + 1.0

  # Quick test with few perms
  result <- prt_s1_test(X, genes, target = "gene_1",
                         perturbed_idx = pert_idx,
                         control_idx = ctrl_idx,
                         n_perms = 100, seed = 42)
  expect_s3_class(result, "data.frame")
  expect_equal(ncol(result), 3)
  expect_true("gene" %in% names(result))
  expect_true("W_observed" %in% names(result))
  expect_true("p_value_perm" %in% names(result))

  # gene_2 should rank high (we added effect)
  expect_true(result$p_value_perm[result$gene == "gene_2"] < 0.2)
})
