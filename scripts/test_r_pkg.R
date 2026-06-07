#!/usr/bin/env Rscript
# Comprehensive test of PGAA R package

# Source all R files
r_dir <- "/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/pgaa_r/R"
for (f in list.files(r_dir, full.names = TRUE)) source(f)

# Track failures
errors <- character(0)
check <- function(cond, msg) {
  if (!isTRUE(cond)) {
    cat(sprintf("❌ %s\n", msg))
    errors <<- c(errors, msg)
  } else {
    cat(sprintf("✅ %s\n", msg))
  }
}

set.seed(42)

# T1: wasserstein_1d basic
x <- rnorm(500, 0, 1); y <- rnorm(500, 0.8, 1)
w <- wasserstein_1d(x, y)
check(w > 0.5, sprintf("T1 W>0.5: got %.4f", w))

# T2: same distribution
x2 <- rnorm(1000, 2, 0.5); y2 <- rnorm(1000, 2, 0.5)
w2 <- wasserstein_1d(x2, y2)
check(w2 < 0.2, sprintf("T2 W<0.2: got %.4f", w2))

# T3: shifted
y3 <- rnorm(1000, 4, 0.5)
w3 <- wasserstein_1d(x2, y3)
check(w3 > 1.5, sprintf("T3 W>1.5: got %.4f", w3))

# T4: persistence single peak
h <- c(0.1, 0.5, 1.0, 0.5, 0.1)
pd <- compute_persistence_1d(h, 1:5)
check(nrow(pd) == 1, sprintf("T4 1 peak: got %d peaks", nrow(pd)))

# T5: flat histogram
h_flat <- rep(1, 10)
pd_flat <- compute_persistence_1d(h_flat, 1:10)
check(pd_flat[1, 3] == 0, sprintf("T5 flat pers=0: got %.4f", pd_flat[1, 3]))

# T6: bimodal
h2 <- c(0.1, 0.8, 0.3, 0.8, 0.1)
pd1 <- compute_persistence_1d(h, 1:5)
pd2 <- compute_persistence_1d(h2, 1:5)
d <- persistence_landscape_distance(pd1, pd2)
check(d > 0.2, sprintf("T6 bimodality dist>0.2: got %.4f", d))

# T7: pi0_storey
p_uniform <- runif(200)
check(pi0_storey(p_uniform) > 0.9,
      sprintf("T7 pi0 uniform ~1: got %.3f", pi0_storey(p_uniform)))

p_mixed <- c(runif(180), runif(20, 0, 0.005))
check(pi0_storey(p_mixed) < 1.0,
      sprintf("T8 pi0 mixed <1: got %.3f", pi0_storey(p_mixed)))

# T8: combined_z_test
p1 <- runif(100); p2 <- runif(100)
p_comb <- combined_z_test(p1, p2)
check(abs(mean(p_comb) - 0.5) < 0.1,
      sprintf("T9 combined z mean~0.5: got %.4f", mean(p_comb)))

# T9: prt_s1_test full pipeline
X <- matrix(rnorm(500 * 20), 500, 20)
colnames(X) <- paste0("gene_", sprintf("%04d", 1:20))
genes <- colnames(X)
X[1:100, 3] <- X[1:100, 3] + 2.0
ct <- kmeans(X, centers = 3, nstart = 10)$cluster

res_s1 <- prt_s1_test(X, genes, "gene_0001",
                       perturbed_idx = 1:100,
                       control_idx = 101:400,
                       n_perms = 100, cell_type = ct,
                       library_size = rep(10000, 500), seed = 42)
check(nrow(res_s1) == 19,
      sprintf("T10 prt_s1_test 19 genes: got %d", nrow(res_s1)))
p_g3 <- res_s1$p_value_perm[res_s1$gene == "gene_0003"]
check(p_g3 < 0.2,
      sprintf("T11 gene_0003 sig: p=%.4f", p_g3))

# T10: prt_s2_test full pipeline
X_bimod <- matrix(rnorm(300 * 15), 300, 15)
colnames(X_bimod) <- paste0("gene_", sprintf("%04d", 1:15))
genes15 <- colnames(X_bimod)
X_bimod[1:40, 4] <- X_bimod[1:40, 4] + 2.5
X_bimod[41:70, 4] <- X_bimod[41:70, 4] - 2.5

res_s2 <- prt_s2_test(X_bimod, genes15, "gene_0001",
                       perturbed_idx = 1:70,
                       control_idx = 71:250,
                       n_perms = 100, n_bins = 20, seed = 42)
check(nrow(res_s2) == 14,
      sprintf("T12 prt_s2_test 14 genes: got %d", nrow(res_s2)))
s2_g4 <- res_s2$S2[res_s2$gene == "gene_0004"]
check(s2_g4 > 0, sprintf("T13 gene_0004 S2>0: got %.4f", s2_g4))

# T11: reproducibility
set.seed(123)
r1 <- prt_s1_test(X, genes, "gene_0001", 1:100, 101:400,
                   n_perms = 50, seed = 42)
set.seed(123)
r2 <- prt_s1_test(X, genes, "gene_0001", 1:100, 101:400,
                   n_perms = 50, seed = 42)
check(all(r1$p_value_perm == r2$p_value_perm),
      "T14 S1 reproducibility: p_values match")

# T12: S1+S2 combined pipeline
p_s1 <- res_s1$p_value_perm
p_s2 <- rnorm(length(p_s1)) * 0.5 + 0.5  # mock S2
p_s2 <- pmax(pmin(p_s2, 1), 1e-5)
p_comb12 <- combined_z_test(p_s1, p_s2)
check(length(p_comb12) == length(p_s1),
      sprintf("T15 combined z length: %d", length(p_comb12)))

# T13: residualize
Xtest <- matrix(rnorm(200 * 10), 200, 10)
ct_test <- sample(1:3, 200, replace = TRUE)
lib_test <- rlnorm(200, mean = 9)
Xres <- residualize(Xtest, cell_type = ct_test, library_size = lib_test)
check(nrow(Xres) == 200 && ncol(Xres) == 10,
      sprintf("T16 residualize dims: %dx%d", nrow(Xres), ncol(Xres)))

# T14: prt_s3_test, prt_s4_test stubs
res_s3 <- prt_s3_test(X, genes, "gene_0001", 1:100, 101:400)
check(nrow(res_s3) == 19, sprintf("T17 S3 stub: %d genes", nrow(res_s3)))

res_s4 <- prt_s4_test(X, genes, "gene_0001", 1:100, 101:400)
check(nrow(res_s4) == 19, sprintf("T18 S4 stub: %d genes", nrow(res_s4)))

# ── Summary ──
cat(sprintf("\n%s\n", paste(rep("=", 50), collapse="")))
if (length(errors) == 0) {
  cat("✅ All 18 R tests PASSED\n")
} else {
  cat(sprintf("❌ %d tests FAILED:\n", length(errors)))
  for (e in errors) cat(sprintf("  %s\n", e))
}
cat(sprintf("%s\n", paste(rep("=", 50), collapse="")))
quit(status = if (length(errors) == 0) 0 else 1)
