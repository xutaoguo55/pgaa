# PGAA Failure-Mode Audit

Audited rows: 49
High-risk or critical rows: 25

## Severity Summary

| Evidence type | Severity | Recommended action | Rows |
|---|---|---|---:|
| adamson_decision_benchmark | high | report_as_failure_or_comparator_limit | 13 |
| adamson_decision_benchmark | low | allow_comparative_ranking_claim | 9 |
| adamson_decision_benchmark | moderate | allow_descriptive_claim_only | 3 |
| norman_decision_benchmark | high | report_as_failure_or_comparator_limit | 4 |
| norman_decision_benchmark | moderate | allow_descriptive_claim_only | 8 |
| s2_calibration | critical | s1_only | 1 |
| s2_calibration | high | s1_only | 1 |
| s2_calibration | low | interpretation_ready | 1 |
| s2_calibration | low | use_with_diagnostic | 1 |
| s2_calibration | moderate | prefer_s1 | 1 |
| s2_calibration | very_high | s2_caution_only | 1 |
| s2_parameter_sensitivity | high | reject_for_primary_analysis | 1 |
| s2_parameter_sensitivity | low | eligible_default_with_controls | 1 |
| s2_parameter_sensitivity | very_high | do_not_tune_on_positive_case | 4 |

## Interpretation

The failure-preserving route is currently better supported than the event-peptide route because it uses existing PGAA benchmark artifacts and converts failures into explicit interpretation states. This does not make PGAA a top-journal paper by itself, but it creates a stronger method object than a score-only ranking tool.

High-risk rows must be shown, not hidden. They define where PGAA-H should be restricted, where PGAA-W is preferred, and where parameter choices are not acceptable for primary claims.

Decision-benchmark rows extend the same principle to method-comparison tables: each row receives a claim state before it can be used in manuscript language.
