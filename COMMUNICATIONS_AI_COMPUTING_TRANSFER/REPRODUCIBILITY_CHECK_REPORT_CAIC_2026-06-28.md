# Reproducibility check report

Date: 2026-06-28

## Checks

| Check or script | Status | Reason if failed or not run | File or command to fix |
|---|---|---|---|
| `python3 build_caic_docx.py` | passed | Built `MANUSCRIPT_CAIC.docx` and copied final `MANUSCRIPT.docx` to upload directory. | None |
| `python3 build_caic_pdf.py` | passed | Built 18-page manuscript PDF; 5 main figures found. | None |
| `python3 build_caic_supplementary_pdf.py` | passed | Built 14-page supplement; Supplementary Figures 1-6 and Supplementary Tables 1-7 detected. | None |
| Cover letter DOCX/PDF build | passed | `pandoc` and LibreOffice conversion completed; final PDF is 1 page. | None |
| `python3 build_caic_supplementary_zip.py` | passed | Built `PGAA_supplementary_code.zip`; required entries present. | None |
| `python3 build_caic_journal_upload_packet.py` | passed | Final upload directory and journal zip contain exactly four files. | None |
| `pandoc + libreoffice -> COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx/pdf` | passed | Updated cover letter converted and copied into upload packet. | `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md` |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | passed | No compressed-data errors. | None |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | passed | No compressed-data errors. | None |
| `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | passed | No compressed-data errors. | None |
| DOCX/PDF bad-pattern scan | passed | No broken formula patterns, placeholders, empty threshold patterns, stale `S2 persistence`, or draft markers found in final text extraction. The active manuscript labels the statistics as PGAA-W and PGAA-H; legacy `s1`/`s2` survives only as code-output compatibility. | None |
| PDF visual render/contact sheets | passed | Upload DOCX-to-PDF, manuscript PDF, supplementary PDF, and cover letter PDF rendered without blank pages or obvious clipping. | None |
| `python3 verify_caic_transfer_ready.py` | passed | Transfer packet and upload files passed. | None |
| `python3 deep_current_submission_audit_2026_06_25.py` | passed | DOCX, references, supplement, and code archive passed. | None |
| `python3 strict_caic_final_audit.py` | passed | 28 strict checks passed. | None |
| `python3 final_upload_strict_audit_2026_06_25.py` | passed | 28 final-upload checks passed. | None |
| Clean-archive `python3 -m pip install -e .` | passed | Editable install from `/tmp/pgaa_caic_check_6DAx31/pgaa_caic_supplementary` succeeded. | None |
| Clean-archive `python3 scripts/run_toy_example.py` | passed | Toy example completed. | None |
| Clean-archive `python3 scripts/test_python_pkg.py` | passed | All 9 core Python checks passed. | None |
| Clean-archive `Rscript scripts/test_r_pkg.R` | passed | All 18 R checks passed. | None |
| Clean-archive `python3 -m pytest tests/test_cli.py -q` | passed | 1 test passed. | None |
| Clean-archive `python3 scripts/verify_dataset_manifest.py` | passed | Dataset manifest check passed. | None |
| Clean-archive `python3 scripts/rebuild_adamson_full_results.py` | passed | Rebuilt Adamson full results and reproduced mean AUROC/AUPRC values used in the manuscript. | None |
| Clean-archive `python3 scripts/table_sceptre_vs_pgaa.py` | passed | Rebuilt CEBPE ELANE comparator table used for the SCEPTRE/PGAA ranking summary. | None |
| `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_mmd_psm.py` | passed | Reproduced MMD-PSM AUROC 0.499, 0/9 nominal CEBPE target hits, and 0 GAPDH negative-control hits. | None |
| `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_norman_multi_perturbation.py` | passed | Rebuilt KLF1, CEBPE, and CEBPA summary outputs with expected ranks and values (KLF1 0.684/0.0252; CEBPE 0.644/0.0154; CEBPA 0.665/0.1244). | None |
| Clean-archive Norman/MMD scripts without `NORMAN2019_H5AD` | not run (no processed input) | The archive is not bundled with the 1.2 GB processed h5ad; without it, only source-data summaries are reproducible. | Provide processed Norman 2019 h5ad via `NORMAN2019_H5AD` or `--data`. |
| Full raw GEO-to-final-figure workflow | not run | Not claimed as complete; package supports source-data reproducibility plus partial Adamson raw sanity rerun. | Would require full raw/processed inputs for every figure. |
| Broader Replogle/SCEPTRE-family benchmark expansion | not run | Outside final hardening scope and not supported by current local inputs. | Add only in future work with complete inputs and scripts. |

## Boundary statement

The archive supports source-data reproducibility, package smoke tests, manifest verification, processed-data Norman reruns when `NORMAN2019_H5AD` is supplied, and partial raw Adamson sanity rerun. The processed Norman 2019 h5ad is not bundled in the supplementary archive because of size; reviewers can reproduce the full Norman/MMD-PSM scripts by setting `NORMAN2019_H5AD`.
