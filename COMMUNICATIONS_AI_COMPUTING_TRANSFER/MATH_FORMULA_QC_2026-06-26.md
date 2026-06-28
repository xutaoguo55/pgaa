# Math Formula QC, 2026-06-26

Scope: checked the PGAA manuscript formulas against the Python/R implementation and regenerated upload package.

## Result

The displayed formulas are now mathematically defensible as written:

- S1 is defined as a 99-point quantile-grid approximation to the one-dimensional Wasserstein distance, not as an exact continuous integral.
- The permutation p-value uses the standard plus-one estimator.
- S2 is defined as a custom root-mean-square distance between top-3 persistence-value vectors, not as a standard bottleneck distance or full persistence-landscape distance.
- The combined z-score is explicitly restricted to exploratory ranking because the independence assumption is not guaranteed.
- Storey calibration is described as an upper-tail diagnostic. Values above 1 are reported only as uncapped tail ratios; the capped value is the valid null-fraction estimate.

## Corrections Made

- Reworded manuscript abstract, introduction, Methods, Results, Discussion, and Supplementary Table 1 header to use "Storey upper-tail ratio/diagnostic" instead of treating values above 1 as a null fraction.
- Added the correct Storey denominator, `(1 - lambda) * m`, in the R utility function. This does not change current lambda = 0.5 results but fixes the general formula.
- Reworded S2 in the manuscript and software comments as a top-persistence RMS statistic.
- Updated Python S2 helper to use gene-specific pooled bin edges, matching the manuscript and R implementation.

## Validation

- `python3 -m py_compile ../pgaa/core/prt_s2.py ../pgaa/core/prt.py`
- `Rscript` parse checks for `../pgaa_r/R/utils.R`, `../pgaa_r/R/prt_s1.R`, and `../pgaa_r/R/prt_s2.R`
- Rebuilt `MANUSCRIPT_CAIC.docx`, `MANUSCRIPT_CAIC.pdf`, `SUPPLEMENTARY_CAIC.pdf`, `PGAA_supplementary_code.zip`, and both final upload zip files.
- `verify_caic_transfer_ready.py`: passed.
- `final_upload_strict_audit_2026_06_25.py`: passed.
- `deep_current_submission_audit_2026_06_25.py`: passed.
- `unzip -t` passed for both final upload zip files and the supplementary code archive.
- Upload DOCX XML contains Word math fraction nodes, confirming formulas were exported as Word math rather than only plain text.
