# GSE75602 T790M Evolution-Trajectory Audit

Verdict: `EVOLUTION_STAGE_MODULATES_EGFR_DIRECTION_NO_FIXED_T790M_EFFECT`

## Vehicle-State EGFR Trajectory

| Stage | T790M state | Mean CPM | Replicates |
|---|---|---:|---:|
| parental | negative_or_not_selected | 606.270 | 2 |
| gefitinib_tolerant | negative_or_not_selected | 1266.830 | 2 |
| wz4002_tolerant | negative_or_not_selected | 1370.940 | 2 |
| early_t790m_gr2 | positive | 1203.585 | 2 |
| late_t790m_gr3 | positive | 887.810 | 2 |

## Locked Contrasts

| Contrast | Fold change | Exact directional p | Direction robust |
|---|---:|---:|---|
| parental_to_early_t790m | 1.985 | 0.167 | True |
| parental_to_late_t790m | 1.464 | 0.167 | True |
| tolerant_to_late_t790m | 0.701 | 0.167 | True |
| early_to_late_t790m | 0.738 | 0.167 | True |

## Interpretation

Both early pre-existing-path GR2 and late drug-tolerant-path GR3 are T790M-positive and have higher EGFR CPM than parental PC9. However, late GR3 is lower than the gefitinib-tolerant precursor state and lower than early GR2. The observed EGFR direction therefore depends on the comparison state and evolutionary path rather than behaving as a fixed T790M effect.

Each state has only two RNA-seq replicates. The smallest attainable one-sided exact permutation p value is 1/6 (0.167), so these contrasts are descriptive even when every cross-replicate pair has the same direction.

This trajectory can explain why clone-level systems show different magnitudes, but it does not rescue the discordance with the GSE112274 same-cell result. The cross-system T790M-expression claim remains failed or unresolved.
