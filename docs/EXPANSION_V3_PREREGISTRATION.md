# PGAA Expansion v3: prospective context-moderated validation

## Frozen question

Can platform context known before expression-outcome scoring predict whether PGAA-W falls into the stable-and-specific, stable-but-not-specific, specific-but-not-stable, or neither state on a new perturbation platform?

## Prospective cohort

The test cohort is the first ten eligible studies in `evidence/expansion_v3_candidate_queue.tsv`, traversed in priority order. Each included platform must come from a different source study and laboratory group and represent a distinct cell-context class. All studies whose expression outcomes were scored in expansion v1 or v2 are excluded. Metadata or QC failures remain visible and cause advancement to the next frozen candidate; unfavorable expression outcomes never cause replacement.

Raw H5AD files remain on `/Volumes/MOVESPEED`. Metadata inspection may establish eligibility and compute design features, but v3 expression values cannot be used to change context annotations, the model, or the queue.

## Primary endpoint

The primary event is **PGAA-W stable and specific**. The primary summary is its count and fraction among ten prospective platforms with an exact Clopper-Pearson 95% interval. Cross-context recurrence requires at least 4/10 events spanning at least three perturbation-mechanism classes and four cell-context classes; leave-one-platform robustness requires at least three events after every deletion.

## Context model

The model predicts stability and specificity as separate biological/statistical axes, using two class-balanced L2-logistic regressions. Their probabilities are combined by a fixed product rule into four state probabilities. Six pre-outcome features are allowed: perturbation modality, primary/in-vivo status, species, split-independence tier, log2 recorded split count, and usable group-size fraction. Definitions are fixed in `evidence/context_moderator_dictionary.tsv`.

All preprocessing is fit within each training fold. The v2 development estimate uses leave-one-platform-out predictions. The primary metric is the mean of the two axis-level Brier scores, compared with a training-fold Laplace-smoothed prevalence predictor. Model confirmation requires all three conditions: lower Brier score than the comparator, exact state accuracy at least 0.60, and one-sided paired exact Wilcoxon P < 0.05.

## Temporal lock

After ten platforms pass metadata eligibility, their context table is passed to `scripts/freeze_expansion_v3_predictions.py`. This creates a prediction table and SHA-256 digest. v3 expression scoring is permitted only after those artifacts exist. The script refuses to create or replace predictions if a v3 outcome-state table already exists.

The machine-readable protocol and queue are independently hashed. `scripts/validate_expansion_v3_protocol.py` checks the endpoint, feature order, cohort independence, and all three digests.
