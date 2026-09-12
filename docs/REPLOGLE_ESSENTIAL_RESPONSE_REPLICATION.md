# Replogle Essential Held-out-batch Response Replication

This locked benchmark asks whether non-target response-gene rankings replicate across a deterministic discovery/validation split of experimental batches. The directly perturbed gene is excluded. It measures within-experiment reproducibility, not independent biological replication or biological correctness.

## Method Summary

| Method | Complete / locked | Median top-k overlap | Median Jaccard | Median Spearman | FDR-significant targets |
|---|---:|---:|---:|---:|---:|
| `pgaa_w` | 16/16 | 0.820 | 0.695 | 0.657 | 16 |
| `pgaa_h` | 16/16 | 0.030 | 0.015 | 0.287 | 4 |
| `absolute_mean_shift` | 16/16 | 0.725 | 0.569 | 0.359 | 16 |
| `welch_abs_t` | 16/16 | 0.115 | 0.061 | 0.066 | 13 |

## Predeclared Paired Comparisons

| PGAA method | Baseline | Paired targets | Median difference | One-sided Wilcoxon p | Holm p |
|---|---|---:|---:|---:|---:|
| `pgaa_w` | `absolute_mean_shift` | 16 | 0.085 | 1.526e-05 | 6.104e-05 |
| `pgaa_w` | `welch_abs_t` | 16 | 0.660 | 1.526e-05 | 6.104e-05 |
| `pgaa_h` | `absolute_mean_shift` | 16 | -0.700 | 1 | 1 |
| `pgaa_h` | `welch_abs_t` | 16 | -0.095 | 0.9995 | 1 |

## Failure Accounting

0 of 16 locked targets failed at least one method. Failures remain in the locked denominator.

## Interpretation Boundary

Greater held-out overlap would support incremental ranking stability, but would not establish that the recovered genes are true biological effectors. A tie or loss against simple summaries is evidence against a PGAA-specific stability advantage in this experiment.
