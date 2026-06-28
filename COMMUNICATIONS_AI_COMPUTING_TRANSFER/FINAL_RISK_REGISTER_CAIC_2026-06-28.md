# Final risk register

Date: 2026-06-28

| Risk | Current handling |
|---|---|
| Adamson benchmark is small | Manuscript labels it as proof-of-principle and reports sparse positives, random AUPRC baseline, AUROC, AUPRC, and top-rank limitations. |
| Positive sets are sparse | AUPRC is interpreted against random baselines, and top-100 recovery is reported where available. |
| Norman multi-perturbation extension uses curated target panels | Manuscript frames this as target-panel ranking extension, not genome-wide truth or full perturbation-method validation. |
| Norman CEBPE PGAA-H result is narrow | Manuscript presents ELANE/PRTN3 as a narrow ranking example and states that full target-program recovery is weak. |
| PGAA-H histogram-bin sensitivity | Manuscript and supplement now define a guarded workflow: pre-specify a small n_bins pilot grid, choose the setting on a negative-control/null/unrelated perturbation, check the upper-tail diagnostic, and do not tune n_bins to improve target-gene ranks. |
| PGAA-H permutation p-values cannot support genome-wide FDR at 500 permutations | Manuscript states that PGAA-H p-values are ranking evidence only and gives the minimum attainable p-value limitation. |
| Storey diagnostic could be misread as pi0 greater than 1 | Methods now distinguish uncapped upper-tail ratio from capped `pi0_hat(lambda)`. |
| MMD-PSM and Norman full recomputation require processed Norman input | Clean-archive reruns passed when `/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad` was supplied via `NORMAN2019_H5AD`; the h5ad is not bundled in the supplementary archive because of size. |
| Raw-to-final reproducibility is incomplete | Manuscript and reports state source-data reproducibility plus processed-data Norman reruns and partial Adamson raw sanity rerun, not a unified raw GEO-to-final-figure workflow. |
| Broader scPerturb-scale, Replogle-scale, and SCEPTRE-family evaluation is not completed | Manuscript now positions PGAA relative to perturbation-response scoring and scPerturb-scale resources, but treats broader evaluation as future work; no unsupported superiority claim is made. |
| Observational datasets may be overinterpreted | Manuscript, supplement, and cover letter call them marker-recovery stress checks only, not causal or clinical biomarker evidence. |
| Supplementary Table 7 is dense | Visual QC shows no overflow; retained because it carries implementation/reproducibility context. |

## Submission readiness judgment

No unresolved formatting or package-integrity blocker remains from this hardening pass. The remaining risks are scientific-scope limitations that are now disclosed in the manuscript and should be reviewed by the authors before submission.
