# Cross-platform Dual-gate Threshold Sensitivity

The stability floor was not preregistered. The full declared range below therefore shows whether the cross-platform interpretation depends on the nominal 0.20 choice. Specificity remains defined by a positive median margin and Holm-adjusted p <= 0.05.

| Method | Stability floor | Platforms | Both | Stable only | Specific only | Neither | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| `absolute_mean_shift` | 0.10 | 5 | 3 | 1 | 0 | 1 | no_recurrent_decoupling_demonstrated |
| `absolute_mean_shift` | 0.15 | 5 | 3 | 1 | 0 | 1 | no_recurrent_decoupling_demonstrated |
| `absolute_mean_shift` | 0.20 | 5 | 3 | 1 | 0 | 1 | no_recurrent_decoupling_demonstrated |
| `absolute_mean_shift` | 0.25 | 5 | 2 | 0 | 1 | 2 | no_recurrent_decoupling_demonstrated |
| `absolute_mean_shift` | 0.30 | 5 | 2 | 0 | 1 | 2 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 0.10 | 5 | 0 | 1 | 1 | 3 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 0.15 | 5 | 0 | 1 | 1 | 3 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 0.20 | 5 | 0 | 1 | 1 | 3 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 0.25 | 5 | 0 | 0 | 1 | 4 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 0.30 | 5 | 0 | 0 | 1 | 4 | no_recurrent_decoupling_demonstrated |
| `pgaa_w` | 0.10 | 5 | 2 | 2 | 0 | 1 | recurrent_stability_specificity_decoupling |
| `pgaa_w` | 0.15 | 5 | 2 | 2 | 0 | 1 | recurrent_stability_specificity_decoupling |
| `pgaa_w` | 0.20 | 5 | 2 | 2 | 0 | 1 | recurrent_stability_specificity_decoupling |
| `pgaa_w` | 0.25 | 5 | 2 | 2 | 0 | 1 | recurrent_stability_specificity_decoupling |
| `pgaa_w` | 0.30 | 5 | 1 | 1 | 1 | 2 | no_recurrent_decoupling_demonstrated |
| `welch_abs_t` | 0.10 | 5 | 2 | 0 | 1 | 2 | no_recurrent_decoupling_demonstrated |
| `welch_abs_t` | 0.15 | 5 | 1 | 0 | 2 | 2 | no_recurrent_decoupling_demonstrated |
| `welch_abs_t` | 0.20 | 5 | 1 | 0 | 2 | 2 | no_recurrent_decoupling_demonstrated |
| `welch_abs_t` | 0.25 | 5 | 0 | 0 | 3 | 2 | no_recurrent_decoupling_demonstrated |
| `welch_abs_t` | 0.30 | 5 | 0 | 0 | 3 | 2 | no_recurrent_decoupling_demonstrated |

## Robustness Readout

Methods retaining recurrent decoupling at every tested stability floor: none.

This analysis tests threshold dependence only. It does not make the sampled platforms representative of all perturbation technologies or biological systems.
