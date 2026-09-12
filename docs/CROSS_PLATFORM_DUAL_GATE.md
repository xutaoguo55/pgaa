# Cross-platform Stability-Specificity Dual Gate

The same count-ranked unit selection, equal-group sampling, top-100 ranking, five-repeat pseudo-perturbation design, and multiplicity correction were applied without dataset-specific result tuning.

## Platform Gate States

| Dataset | Split | Method | Units | Observed | Pseudo | Margin | Holm p | State |
|---|---|---|---:|---:|---:|---:|---:|---|
| datlinger2017_jurkat_crispr | experimental_replicate_holdout_3_vs_3 | `absolute_mean_shift` | 16 | 0.065 | 0.060 | 0.010 | 0.2798 | neither_stable_nor_specific |
| datlinger2017_jurkat_crispr | experimental_replicate_holdout_3_vs_3 | `pgaa_h` | 16 | 0.020 | 0.020 | 0.000 | 0.2798 | neither_stable_nor_specific |
| datlinger2017_jurkat_crispr | experimental_replicate_holdout_3_vs_3 | `pgaa_w` | 16 | 0.075 | 0.070 | 0.005 | 0.2798 | neither_stable_nor_specific |
| datlinger2017_jurkat_crispr | experimental_replicate_holdout_3_vs_3 | `welch_abs_t` | 16 | 0.020 | 0.020 | 0.000 | 0.2798 | neither_stable_nor_specific |
| nadig2024_hepg2_crispri | experimental_batch_holdout_28_vs_28 | `absolute_mean_shift` | 16 | 0.245 | 0.050 | 0.180 | 0.001957 | stable_and_specific |
| nadig2024_hepg2_crispri | experimental_batch_holdout_28_vs_28 | `pgaa_h` | 16 | 0.040 | 0.030 | 0.000 | 0.7021 | neither_stable_nor_specific |
| nadig2024_hepg2_crispri | experimental_batch_holdout_28_vs_28 | `pgaa_w` | 16 | 0.265 | 0.080 | 0.160 | 0.001957 | stable_and_specific |
| nadig2024_hepg2_crispri | experimental_batch_holdout_28_vs_28 | `welch_abs_t` | 16 | 0.120 | 0.020 | 0.095 | 0.001957 | specific_but_not_stable |
| norman2019_k562_crispra | technical_batch_holdout_4_vs_4 | `absolute_mean_shift` | 16 | 0.300 | 0.045 | 0.270 | 0.00098 | stable_and_specific |
| norman2019_k562_crispra | technical_batch_holdout_4_vs_4 | `pgaa_h` | 16 | 0.050 | 0.045 | 0.000 | 0.3275 | neither_stable_nor_specific |
| norman2019_k562_crispra | technical_batch_holdout_4_vs_4 | `pgaa_w` | 16 | 0.330 | 0.060 | 0.275 | 0.0001831 | stable_and_specific |
| norman2019_k562_crispra | technical_batch_holdout_4_vs_4 | `welch_abs_t` | 16 | 0.225 | 0.020 | 0.210 | 0.00098 | stable_and_specific |
| replogle2022_k562_crispri | technical_batch_holdout_24_vs_24 | `absolute_mean_shift` | 16 | 0.675 | 0.575 | 0.080 | 0.01848 | stable_and_specific |
| replogle2022_k562_crispri | technical_batch_holdout_24_vs_24 | `pgaa_h` | 16 | 0.030 | 0.015 | 0.015 | 0.009317 | specific_but_not_stable |
| replogle2022_k562_crispri | technical_batch_holdout_24_vs_24 | `pgaa_w` | 16 | 0.820 | 0.810 | 0.015 | 0.1399 | stable_but_not_specific |
| replogle2022_k562_crispri | technical_batch_holdout_24_vs_24 | `welch_abs_t` | 16 | 0.070 | 0.010 | 0.065 | 0.001957 | specific_but_not_stable |
| sciplex3_a549_drug | biological_replicate_holdout_1_vs_1 | `absolute_mean_shift` | 16 | 0.235 | 0.230 | 0.005 | 0.6894 | stable_but_not_specific |
| sciplex3_a549_drug | biological_replicate_holdout_1_vs_1 | `pgaa_h` | 16 | 0.230 | 0.225 | -0.010 | 1 | stable_but_not_specific |
| sciplex3_a549_drug | biological_replicate_holdout_1_vs_1 | `pgaa_w` | 16 | 0.280 | 0.265 | 0.000 | 1 | stable_but_not_specific |
| sciplex3_a549_drug | biological_replicate_holdout_1_vs_1 | `welch_abs_t` | 16 | 0.080 | 0.085 | 0.000 | 1 | neither_stable_nor_specific |

## Cross-platform Recurrence

| Method | Platforms | Stability pass | Specificity pass | Both | Stable only | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `absolute_mean_shift` | 5 | 4 | 3 | 3 | 1 | no_recurrent_decoupling_demonstrated |
| `pgaa_h` | 5 | 1 | 1 | 0 | 1 | no_recurrent_decoupling_demonstrated |
| `pgaa_w` | 5 | 4 | 2 | 2 | 2 | recurrent_stability_specificity_decoupling |
| `welch_abs_t` | 5 | 1 | 3 | 1 | 0 | no_recurrent_decoupling_demonstrated |

## Claim Boundary

Recurrence on multiple independent platforms supports a cross-platform empirical regularity, not a universal theorem. The 0.20 stability floor remains a post-result decision threshold, and results close to either gate require sensitivity analysis. Platform split strength is retained because biological-replicate or batch holdout is stronger than an arbitrary cell split.

Source hashes and USB paths: `evidence/cross_platform_source_manifest.tsv`.

Newly selected perturbation units: 64; the locked Replogle reference contributes 16 additional units.
