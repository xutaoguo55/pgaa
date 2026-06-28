# Reproducibility Checklist

Date: 2026-06-27

## Submission Artifacts

- Main manuscript DOCX: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx`
- Supplementary PDF: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf`
- Supplementary code archive: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip`
- Cover letter PDF: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`
- Clean journal upload zip: `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

## Rebuild Status

| Item | Rebuild Source | Status |
|---|---|---|
| Main manuscript DOCX | `MANUSCRIPT_CAIC.md`, `build_caic_docx.py` | Passed |
| Main manuscript PDF | `MANUSCRIPT_CAIC.md`, `build_caic_pdf.py` | Passed |
| Supplementary PDF | `SUPPLEMENTARY_CAIC.md`, `build_caic_supplementary_pdf.py` | Passed |
| Supplementary code zip | repository code, scripts, source data, `build_caic_supplementary_zip.py` | Passed |
| Journal upload package | `build_caic_journal_upload_packet.py` | Passed |
| Adamson summary tables | `figure_source_data/fig6_adamson_results.csv`, `scripts/rebuild_adamson_full_results.py` | Passed |
| MMD-PSM comparator summary | `scripts/mmd_psm_summary.csv` | Passed; full 1000-permutation rerun completed after vectorizing the same statistic |
| Norman multi-perturbation benchmark | `scripts/benchmark_norman_multi_perturbation.py` and `scripts/norman_multi_perturbation_*.csv` | Passed; KLF1/CEBPE/CEBPA completed with S1, KS, Welch t, and Wilcoxon scores |

## Tests and Audits Run

| Check | Result | Notes |
|---|---|---|
| `python3 -m pytest tests -q` | Passed | 14 passed |
| `python3 scripts/test_python_pkg.py` | Passed | 9 core tests passed |
| `Rscript scripts/test_r_pkg.R` | Passed | 18 R tests passed |
| `python3 scripts/run_toy_example.py` | Passed | Synthetic smoke test passed |
| `python3 scripts/rebuild_adamson_full_results.py` | Passed | Rebuilt Adamson full results and AUPRC comparison |
| `python3 scripts/verify_dataset_manifest.py` | Passed | Dataset manifest check passed |
| `python3 build_caic_pdf.py` | Passed | Main manuscript PDF, 17 pages |
| `python3 build_caic_docx.py` | Passed | Main manuscript DOCX generated |
| `python3 build_caic_supplementary_pdf.py` | Passed | Supplementary PDF, 13 pages |
| `python3 build_caic_supplementary_zip.py` | Passed | Supplementary code zip rebuilt |
| `python3 build_caic_journal_upload_packet.py` | Passed | Four-file clean upload packet rebuilt |
| `python3 verify_caic_transfer_ready.py` | Passed | CAIC transfer check passed |
| `python3 final_upload_strict_audit_2026_06_25.py` | Passed | 28 checks passed |
| `python3 strict_caic_final_audit.py` | Passed | 28 checks passed |
| `python3 deep_current_submission_audit_2026_06_25.py` | Passed | 6 deep audit checks passed |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | Passed | DOCX archive integrity OK |
| `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | Passed | Upload zip integrity OK |
| `python3 scripts/benchmark_mmd_psm.py` | Passed | Full 1000-permutation CEBPE run and full 1000-permutation GAPDH negative-control run completed |
| `python3 scripts/benchmark_norman_multi_perturbation.py --targets KLF1 CEBPE CEBPA` | Passed | Completed on processed Norman h5ad; wrote summary, gene-score, panel-audit, and metadata CSV files |
| `python3 scripts/verify_upload_file_manifest.py` | Not applicable to CAIC packet | Script checks old Communications Medicine upload paths and failed on that stale packet |
| `python3 scripts/verify_manuscript_consistency.py` | Not applicable to CAIC packet | Legacy Bioinformatics/Communications Medicine consistency gate; not aligned with current CAIC transfer files |

## Reproduction Boundary

- The manuscript is reproducible from the included code, source-data CSV files, and public accession metadata for the reported figures/tables.
- A complete raw GEO-to-final-figure rerun is not fully available for every dataset in the current package.
- Norman MMD-PSM full 1000-permutation rerun completed after vectorizing the same per-gene matched-Wasserstein calculation. The rerun produced AUROC 0.499, 0/9 CEBPE target hits and 0 GAPDH negative-control hits.
- Norman KLF1/CEBPE/CEBPA multi-perturbation extension completed from the processed Norman h5ad. It supports S1 as the stronger ranking score in this curated-panel setting, but top-100 positive recovery remains sparse and the benchmark is not an original-study DEG gold-standard evaluation.
