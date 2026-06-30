# Final submission-hardening report

Date: 2026-06-30

Target package: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

Final journal upload zip: `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

## Files changed in this pass

| File | Change |
|---|---|
| `MANUSCRIPT_CAIC.md` | Reduced defensive self-description, clarified PGAA-W/PGAA-H naming, softened PGAA-H bin-sensitivity mechanism language, normalized p-value formatting, and kept limitations explicit. |
| `SUPPLEMENTARY_CAIC.md` | Fixed CLI output suffixes from `.pgaw/.pgah` to `.s1/.s2`; stabilized Supplement title line break; retained Figures 1-7, Tables 1-7, CLI schema, and Supplementary Methods. |
| `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md` | Rewritten as a direct first-submission cover letter with positive method framing and without "revised/reframed" or "not a new metric" language. |
| `build_caic_docx.py` | Updated Figure 1 caption text to use PGAA-W as the primary starting score. |
| `../scripts/table_sceptre_vs_pgaa.py` | Added direct AUPRC output so the Norman CEBPE PGAA-H AUPRC 0.0076 is traceable in the source CSV. |
| `../scripts/verify_dataset_manifest.py` | Included the Communications AI & Computing manuscript/supplement sources in manifest checking. |
| `verify_caic_transfer_ready.py`, `final_upload_strict_audit_2026_06_25.py` | Updated audit expectations to match the current PGAA-W/PGAA-H terminology and complete Supplementary Figure 1-7 set. |
| `FINAL_NUMERIC_AND_SOURCE_TRACE_AUDIT_2026-06-29.md` | Updated the prior CEBPE AUPRC trace issue from NEEDS REVIEW to PASS. |

## Build outputs refreshed

| Output | Status |
|---|---|
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | refreshed |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf` | refreshed |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf` | refreshed |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | refreshed |
| `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | refreshed |

## Reproducibility and package checks

| Check or command | Status | Reason if failed or not run | File or command to fix |
|---|---|---|---|
| `python3 build_caic_docx.py` | passed | Built manuscript DOCX and copied upload DOCX. | none |
| `python3 build_caic_pdf.py` | passed | Built 20-page manuscript PDF. | none |
| `python3 build_caic_supplementary_pdf.py` | passed | Built 20-page Supplementary PDF with Supplementary Figures 1-7 and Tables 1-7. | none |
| `pandoc COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md` plus `tinytex::xelatex()` | passed | Rebuilt cover letter PDF from source Markdown. | none |
| `python3 build_caic_supplementary_zip.py` | passed | Built supplementary code archive with 153 entries. | none |
| `python3 build_caic_journal_upload_packet.py` | passed | Built clean 4-file journal upload directory and zip. | none |
| `python3 verify_caic_transfer_ready.py` | passed | Packet, clean upload, pages, repository DOI, and SWHID checks passed. | none |
| `python3 deep_current_submission_audit_2026_06_25.py` | passed | Upload contents, DOCX structure, citations, Supplement, references, and code archive checks passed. | none |
| `python3 strict_caic_final_audit.py` | passed | 28 strict audit checks passed. | none |
| `python3 final_upload_strict_audit_2026_06_25.py` | passed | 28 final upload checks passed. | none |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | passed | DOCX archive integrity OK. | none |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | passed | Code archive integrity OK. | none |
| `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | passed | Final journal zip integrity OK. | none |
| DOCX/PDF text bad-pattern scan | passed | No empty parentheses, stale `.pgaw/.pgah`, broken p-value fragments, placeholder tokens, or "S2 persistence" labels found. | none |
| Supplementary PDF content scan | passed | Supplementary Figure 7, Supplementary Table 7, CLI schema, and Supplementary Methods all present in extracted text. | none |
| `python3 -m pip install -e .` in clean extracted code archive | passed | Editable install completed. | none |
| `python3 scripts/run_toy_example.py` | passed | Toy example completed. | none |
| `python3 scripts/test_python_pkg.py` | passed | Core Python tests passed. | none |
| `Rscript scripts/test_r_pkg.R` | passed | 18 R tests passed. | none |
| `python3 -m pytest tests/test_cli.py -q` | passed | 1 CLI test passed. | none |
| `python3 scripts/verify_dataset_manifest.py` | passed | Dataset manifest check passed. | none |
| `python3 scripts/table_sceptre_vs_pgaa.py` | passed | Regenerated source table with direct AUPRC column; PGAA-H AUPRC 0.0076 is traceable. | none |
| `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_mmd_psm.py` in a clean extracted final code archive | passed | Reproduced MMD-PSM AUROC 0.499, 0/9 nominal CEBPE target hits, and 0 GAPDH negative-control hits. Log: `qc_repro_2026_06_30/mmd_psm_rerun_2026_06_30.log`. | none |
| `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_norman_multi_perturbation.py` in a clean extracted final code archive | passed | Rebuilt KLF1, CEBPE, and CEBPA summaries with expected PGAA-W AUROC/AUPRC values: KLF1 0.684/0.0252, CEBPE 0.644/0.0154, CEBPA 0.665/0.1244. Log: `qc_repro_2026_06_30/norman_multi_rerun_2026_06_30.log`. | none |
| LibreOffice DOCX-to-PDF conversion of final upload `MANUSCRIPT.docx` | passed | Converted to `qc_visual_2026_06_30/docx_pdf/MANUSCRIPT.pdf`; 20 pages, letter size, no PDF syntax warnings. | none |
| Rendered-page visual QC for manuscript, supplement, cover letter, and DOCX-converted manuscript | passed | Rendered 61 PNG pages and generated contact sheets in `qc_visual_2026_06_30/`; low-content pages were inspected individually and correspond to natural sparse page breaks, figure-only pages, or table/CLI continuation pages, not blank pages or clipping. | none |
| DOCX-converted PDF and Supplementary PDF strict text scan | passed | No empty parentheses, broken Methods math fragments, missing variable phrases, placeholders, "S2 persistence", "not a new metric", or "computational contribution collapses" strings found. | none |
| Figure/table citation order scan from source manuscript | passed | Main Figures 1-5, Main Tables 1-3, Supplementary Figures 1-6, and Supplementary Tables 1-7 are all cited; first unique citation order is sequential for main figures, main tables, supplementary figures, and supplementary tables. | none |
| Final upload zip listing and integrity check | passed | Final zip contains exactly four upload files and `unzip -t` reports no compressed-data errors. | none |

## Final risk register

| Risk | Current mitigation | Remaining risk |
|---|---|---|
| Small Adamson benchmark | Framed as proof-of-principle with sparse positive set and explicit random AUPRC baseline. | Does not establish broad Perturb-seq performance. |
| Sparse curated target panels | Norman KLF1/CEBPE/CEBPA extension reports positives/ranked genes, random AUPRC baselines, AUROC, AUPRC, and top-100 hits. | Curated panel recovery is not genome-wide truth. |
| PGAA-H bin sensitivity | Main text and Supplement require calibration and pilot n_bins sweep; wording no longer claims one bin count is universally optimal. | PGAA-H remains diagnostic and should not be interpreted as formal discovery. |
| Incomplete raw-to-final reproducibility | Archive supports source-data rebuilds, clean smoke tests, manifest checks, raw Adamson sanity rerun documentation, and clean-archive Norman/MMD reruns when `NORMAN2019_H5AD` is supplied. | The processed Norman h5ad input is not bundled, so reviewers need to provide that external file for full Norman/MMD recomputation. |
| Comparator coverage | KS included in Norman multi-perturbation extension; MMD-PSM included as single-contrast processed-source-data sensitivity check. | Energy distance, Cramer-von Mises, broader MMD, SCEPTRE-family genome-scale benchmarks remain future work. |
| Observational datasets | Kept as marker-recovery stress checks only. | No causal, clinical, or biomarker claims should be inferred. |
| Figure readability in DOCX | Main DOCX embeds figures and code archive includes figure PNGs/source data. | Final human review should still visually inspect the portal-rendered files and upload separate high-resolution figures if the submission portal requests them. |

## Final package status

The clean upload directory contains exactly four files:

- `MANUSCRIPT.docx`
- `SUPPLEMENTARY.pdf`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`
- `PGAA_supplementary_code.zip`

All machine checks above passed. The processed Norman h5ad input is not bundled in the upload archive, but the two Norman/MMD recomputation scripts were run successfully from a clean extracted final code archive after supplying the local `NORMAN2019_H5AD` path.
