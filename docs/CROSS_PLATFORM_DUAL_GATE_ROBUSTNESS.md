# Cross-platform Dual-gate Robustness Audit

Leave-one-platform-out analysis re-applies the locked recurrence rule after removing each dataset. Exact binomial intervals describe the sampled platforms; they are not population estimates under guaranteed exchangeability.

## Leave-one-platform-out

| Method | Omitted dataset | Remaining | Stable only | Recurrence survives |
|---|---|---:|---:|---|
| `absolute_mean_shift` | datlinger2017_jurkat_crispr | 4 | 1 | false |
| `absolute_mean_shift` | nadig2024_hepg2_crispri | 4 | 1 | false |
| `absolute_mean_shift` | norman2019_k562_crispra | 4 | 1 | false |
| `absolute_mean_shift` | replogle2022_k562_crispri | 4 | 1 | false |
| `absolute_mean_shift` | sciplex3_a549_drug | 4 | 0 | false |
| `pgaa_h` | datlinger2017_jurkat_crispr | 4 | 1 | false |
| `pgaa_h` | nadig2024_hepg2_crispri | 4 | 1 | false |
| `pgaa_h` | norman2019_k562_crispra | 4 | 1 | false |
| `pgaa_h` | replogle2022_k562_crispri | 4 | 1 | false |
| `pgaa_h` | sciplex3_a549_drug | 4 | 0 | false |
| `pgaa_w` | datlinger2017_jurkat_crispr | 4 | 2 | true |
| `pgaa_w` | nadig2024_hepg2_crispri | 4 | 2 | true |
| `pgaa_w` | norman2019_k562_crispra | 4 | 2 | true |
| `pgaa_w` | replogle2022_k562_crispri | 4 | 1 | false |
| `pgaa_w` | sciplex3_a549_drug | 4 | 1 | false |
| `welch_abs_t` | datlinger2017_jurkat_crispr | 4 | 0 | false |
| `welch_abs_t` | nadig2024_hepg2_crispri | 4 | 0 | false |
| `welch_abs_t` | norman2019_k562_crispra | 4 | 0 | false |
| `welch_abs_t` | replogle2022_k562_crispri | 4 | 0 | false |
| `welch_abs_t` | sciplex3_a549_drug | 4 | 0 | false |

## Platform-state uncertainty

| Method | Event | Count | Proportion | Exact 95% CI |
|---|---|---:|---:|---:|
| `absolute_mean_shift` | specificity_pass | 3/5 | 0.600 | [0.147, 0.947] |
| `absolute_mean_shift` | stability_pass | 4/5 | 0.800 | [0.284, 0.995] |
| `absolute_mean_shift` | stable_but_not_specific | 1/5 | 0.200 | [0.005, 0.716] |
| `pgaa_h` | specificity_pass | 1/5 | 0.200 | [0.005, 0.716] |
| `pgaa_h` | stability_pass | 1/5 | 0.200 | [0.005, 0.716] |
| `pgaa_h` | stable_but_not_specific | 1/5 | 0.200 | [0.005, 0.716] |
| `pgaa_w` | specificity_pass | 2/5 | 0.400 | [0.053, 0.853] |
| `pgaa_w` | stability_pass | 4/5 | 0.800 | [0.284, 0.995] |
| `pgaa_w` | stable_but_not_specific | 2/5 | 0.400 | [0.053, 0.853] |
| `welch_abs_t` | specificity_pass | 3/5 | 0.600 | [0.147, 0.947] |
| `welch_abs_t` | stability_pass | 1/5 | 0.200 | [0.005, 0.716] |
| `welch_abs_t` | stable_but_not_specific | 0/5 | 0.000 | [0.000, 0.522] |

## Interpretation

A nominal recurrence that fails after deletion of a contributing platform is classified as platform-sensitive evidence. It remains a replicated observation, but does not warrant a platform-robust or universal claim.
