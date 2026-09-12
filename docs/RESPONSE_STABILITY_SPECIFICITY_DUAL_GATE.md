# Response Stability-Specificity Dual Gate

A ranking must pass both an absolute held-out replication gate and a matched pseudo-perturbation specificity gate before it can support a bounded response-stability claim.

| Method | Observed overlap | Pseudo overlap | Margin | Holm p | Stability | Specificity | State |
|---|---:|---:|---:|---:|---|---|---|
| absolute_mean_shift | 0.675 | 0.575 | 0.080 | 0.01848 | pass | pass | stable_and_specific |
| pgaa_h | 0.030 | 0.015 | 0.015 | 0.009317 | fail | pass | specific_but_not_stable |
| pgaa_w | 0.820 | 0.810 | 0.015 | 0.1399 | pass | fail | stable_but_not_specific |
| welch_abs_t | 0.070 | 0.010 | 0.065 | 0.001957 | fail | pass | specific_but_not_stable |

## Claim Boundary

- `absolute_mean_shift`: Bounded response-stability claim allowed within this benchmark.
- `pgaa_h`: Report as a specificity diagnostic, not a usable stable ranking.
- `pgaa_w`: Report reproducibility only; reject response-specific superiority.
- `welch_abs_t`: Report as a specificity diagnostic, not a usable stable ranking.

The 0.20 stability threshold is a post-result decision floor fixed in this compiler, not a preregistered threshold or a universal biological constant. The specificity gate requires a positive median margin and Holm-adjusted p <= 0.05. Conclusions near either boundary require threshold sensitivity analysis.
