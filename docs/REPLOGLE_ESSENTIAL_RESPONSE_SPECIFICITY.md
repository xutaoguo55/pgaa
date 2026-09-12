# Matched Control Specificity Stress Test

This post-result sensitivity analysis tests whether cross-batch ranking stability exceeds a control-vs-control pseudo-perturbation background. Within each batch half and repeat, the observed comparison and pseudo comparison use equal group sizes and share the same matched-control group.

| Method | Complete targets | Observed overlap | Pseudo overlap | Specificity margin | Positive targets | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| `pgaa_w` | 16 | 0.820 | 0.810 | 0.015 | 9 | 0.1399 |
| `pgaa_h` | 16 | 0.030 | 0.015 | 0.015 | 11 | 0.009317 |
| `absolute_mean_shift` | 16 | 0.675 | 0.575 | 0.080 | 10 | 0.01848 |
| `welch_abs_t` | 16 | 0.070 | 0.010 | 0.065 | 14 | 0.001957 |

## Interpretation Boundary

A positive margin supports response-specific stability beyond gene-wise variability and abundance that can make null rankings reproducible. This diagnostic was specified after inspecting the primary split result, uses one experiment, and is sensitivity evidence rather than independent confirmation.
