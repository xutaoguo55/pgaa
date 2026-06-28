# Remaining Limitations to Acknowledge Before Submission

Date: 2026-06-27

1. Adamson 2016 remains a proof-of-principle benchmark, not a broad validation set. The positive set has only 13 positives among 2,000 HVGs, so AUPRC must be interpreted relative to the 0.0065 random baseline.

2. The Norman 2019 CEBPE result is a narrow S2 ranking example. ELANE ranking improves under S2, but full CEBPE target-program recovery is weak.

3. S2 is sensitive to histogram binning and sample size. It should remain a secondary responder-state diagnostic, not a genome-wide discovery statistic.

4. The 500-permutation S2 analyses cannot support strong genome-wide FDR-controlled inference. They should be described as ranking evidence unless deeper permutation depth is run.

5. The combined z-score is exploratory only because S1 and S2 are not independent.

6. Full residualization sensitivity across k-means k = 3, 5, 10 and no-residualization has not been fully completed in this package. The manuscript should not imply this robustness check is complete.

7. MMD-PSM was added as a distribution-aware comparator from processed source data. The full 1000-permutation rerun completed and remained negative for curated CEBPE targets (AUROC 0.499; 0/9 nominal target hits), so it should be framed as a comparator that did not rescue full target-program recovery.

8. The Norman multi-perturbation extension uses curated KLF1/CEBPE/CEBPA target-program panels and forced panel-gene inclusion because the processed HVG mask excludes the panel positives. It strengthens the S1 comparison against KS/Welch/Wilcoxon, but it is still not a genome-wide original-study DEG benchmark.

9. Observational disease-related datasets are marker-recovery stress checks only. They do not support causal perturbation effects, clinical biomarker discovery, or treatment-response claims.

10. Full raw GEO-to-final-figure reproduction is partial. Some figures rely on curated source-data CSVs rather than fully automated raw-data pipelines.

11. MI and Fisher-NB style exploratory modules remain insufficiently benchmarked and should not be presented as core validated PGAA contributions.
