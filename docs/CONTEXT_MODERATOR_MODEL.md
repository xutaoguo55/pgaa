# Context moderator model

## Model role

This model converts the cross-platform dual-gate analysis from a recurrence count into a prospective prediction problem. It is deliberately limited to context and design information available before expression outcomes are calculated. The v2 fit is a development analysis; the frozen v3 cohort is the confirmatory test.

## v2 leave-one-platform-out result

The initial six-feature model did **not** validate internally. Its mean two-axis Brier score was 0.355, versus 0.269 for the prevalence comparator. Exact four-state accuracy was 0.10, and the paired one-sided Wilcoxon P value was 0.976. Stability ROC AUC was 0.292; specificity ROC AUC was 0.000. The frozen confirmation rule therefore failed.

This negative result is retained as an estimand boundary: broad study-design labels alone do not currently explain which platform reaches both gates. The v3 test remains useful because predictions are now locked prospectively, but the current model must be described as an unvalidated contextual hypothesis rather than a validated platform-selection tool.

## Outputs

- `evidence/context_moderator_v2_training_table.tsv`: joined outcomes and pre-outcome covariates.
- `evidence/context_moderator_v2_lopo_predictions.tsv`: one strictly held-out prediction per platform.
- `evidence/context_moderator_v2_metrics.tsv`: primary and axis-level performance.
- `evidence/context_moderator_v2_coefficients.tsv`: standardized full-fit coefficients.
- `evidence/context_moderator_model_frozen.json`: portable inference parameters and input hashes.
- `evidence/context_moderator_model_frozen.sha256`: immutable model digest.

No v2 platform is presented as external validation, and no coefficient is interpreted causally.
