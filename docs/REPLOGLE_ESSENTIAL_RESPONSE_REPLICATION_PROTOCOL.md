# Replogle Essential Held-out-batch Response Replication Protocol

## Locked question

Do PGAA-W or PGAA-H produce non-target response-gene rankings that are more reproducible across held-out experimental batches than absolute mean shift or absolute Welch t-statistic?

## Design fixed before outcome inspection

- Dataset: the same Replogle K562 essential Perturb-seq experiment used by the 16-target locked generality panel.
- Targets: all 16 selected targets; computational failures remain in the denominator.
- Batch universe: source batches `1` through `48`.
- Split: SHA256 ordering with seed `pgaa-response-replication-v1`, first 24 batches as discovery and remaining 24 as validation.
- Discovery batches: `3, 4, 9, 13, 14, 15, 16, 17, 19, 20, 25, 26, 27, 28, 30, 33, 34, 35, 38, 41, 42, 44, 46, 47`.
- Validation batches: `1, 2, 5, 6, 7, 8, 10, 11, 12, 18, 21, 22, 23, 24, 29, 31, 32, 36, 37, 39, 40, 43, 45, 48`.
- Eligibility: at least 10 perturbed and 10 fixed-subsample control cells in each split.
- Gene universe: all measured genes except the directly perturbed target gene.
- Methods: PGAA-W, PGAA-H with 20 bins, absolute mean shift, and absolute Welch t-statistic.
- Primary ranking set: top 100 non-target genes in each split.
- Primary endpoint: discovery-validation top-100 overlap fraction.
- Supporting endpoints: Jaccard index, hypergeometric overlap enrichment, all-gene Spearman correlation, and median validation percentile of discovery top-100 genes.
- Multiplicity: Benjamini-Hochberg correction over 16 target-level overlap tests within each method.
- Incremental-value tests: four one-sided paired Wilcoxon tests comparing PGAA-W and PGAA-H with each simple baseline, followed by Holm correction.

## Claim boundary

This is a within-experiment, cross-batch stability test. It is not an independent dataset replication, does not supply biological ground truth for response genes, and cannot establish causal or therapeutic validity. A PGAA win would support incremental ranking stability only. A tie or loss is evidence against method-specific stability advantage in this experiment.

The hypergeometric calculation is a common random-set reference, not a fully calibrated gene-level null: correlated expression violates its independence idealization. The overlap fraction and paired target-level comparisons therefore remain the main evidence.
