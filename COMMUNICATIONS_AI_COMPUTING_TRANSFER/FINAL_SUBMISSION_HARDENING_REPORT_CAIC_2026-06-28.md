# Final submission-hardening report

Date: 2026-06-28

Scope: Communications AI & Computing submission package in `COMMUNICATIONS_AI_COMPUTING_TRANSFER`.

## Files changed

- `MANUSCRIPT_CAIC.md`
- `SUPPLEMENTARY_CAIC.md`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md`
- `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md`
- `UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING/PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md`
- `../README.md`
- `build_caic_docx.py`
- `build_caic_pdf.py`
- `build_caic_supplementary_pdf.py`
- `build_caic_supplementary_zip.py`
- `scripts_generate_caic_norman_figure.py`
- `scripts_generate_caic_melanoma_figure.py`
- `scripts_generate_caic_entry_figure.py`
- `deep_current_submission_audit_2026_06_25.py`
- `strict_caic_final_audit.py`
- `final_upload_strict_audit_2026_06_25.py`
- `../scripts/figure_adamson_benchmark.py`
- `../scripts/figure_s2_calibration_multitarget.py`
- `../scripts/figure_pgaa_workflow.py`
- `../scripts/rebuild_adamson_full_results.py`
- `../scripts/sensitivity_s2_bins.py`
- `../scripts/verify_manuscript_consistency.py`
- `../pgaa/core/prt.py`
- `../pgaa/core/prt_s2.py`
- `../pgaa/cli.py`
- `../pgaa_r/R/prt_s1.R`
- `../pgaa_r/R/prt_s2.R`
- `../pgaa_r/R/utils.R`
- `../pgaa_r/README.md`
- `../pgaa_r/DESCRIPTION`

## Errors fixed

| Area | Fix |
|---|---|
| Methods 4.3 | Rewrote PGAA-H as stable plain-text notation using `X_tilde[, g]`, `D_i`, `n_bins`, peak-prominence vectors, and `PGAA-H(g) = sqrt((1/3) * sum_{r=1}^{3} (v_{g,1,r} - v_{g,0,r})^2)`. |
| Methods 4.6 | Defined the uncapped Storey upper-tail ratio `R_lambda` and the capped estimate `pi0_hat(lambda) = min(1, R_lambda)` without implying that `pi0` can exceed 1. |
| Results order | Moved the Norman multi-perturbation PGAA-W extension before the narrow CEBPE PGAA-H example. |
| Main Table 4 | Moved the Norman multi-perturbation table out of the main manuscript; after final figure/table ordering, it is Supplementary Table 3. |
| Terminology | Harmonized captions and scripts to `PGAA-H histogram-shape diagnostic`; removed stale `S2 persistence` and `histogram-persistence` labels from active submission artifacts. Historical code output columns retain `s1`/`s2` only for compatibility and are documented as PGAA-W/PGAA-H. |
| Abstract | Shortened and removed detailed negative-comparator numbers from the abstract. |
| Cover letter | Removed revised/reframed language and made the letter read as a direct first submission to Communications AI & Computing. |
| Code archive boundary | README and Supplementary Table 7 now state that full MMD-PSM and Norman multi-perturbation recomputation require `NORMAN2019_H5AD`. |
| Reproducibility remediation | Located the local processed Norman input and verified clean-archive reruns of `scripts/benchmark_norman_multi_perturbation.py` and `scripts/benchmark_mmd_psm.py` with `NORMAN2019_H5AD` set. |
| PGAA-H guardrail remediation | Strengthened PGAA-H wording from a limitation into an explicit guarded workflow: pre-specified n_bins pilot grid, negative-control/null/unrelated-perturbation calibration, upper-tail diagnostic review, and no target-rank tuning. |
| Literature positioning | Added current perturbation-response scoring and scPerturb benchmark-resource context to position PGAA as gene-level distributional ranking alongside response-strength, perturbation-quality, and formal association-testing methods rather than as a replacement for them. |
| Figure synchronization | Updated figure scripts so Adamson, PGAA-H calibration, Figure 1 workflow, Norman, and observational stress-check figures use current terminology and are written into the CAIC figure directory used by the manuscript build. |
| Audit scripts | Updated expected structure to 3 main tables and Supplementary Tables 1-7. |
| Figure/table citation order | Renumbered supplementary figures and tables by first main-text citation and updated Figure 2 caption/build scripts so final DOCX/PDF cite Main Figure 1-5, Main Table 1-3, Supplementary Figure 1-7, and Supplementary Table 1-7 in order. |
| Supplementary Table 7 rendering | Fixed a late-stage supplementary PDF defect where a raw `\end{landscape}` command printed and the dense implementation/reproducibility table was clipped. Supplementary Table 7 now uses a paginating longtable and renders across pages 12-13. |

## Rebuilt deliverables

- `MANUSCRIPT_CAIC.docx`
- `MANUSCRIPT_CAIC.pdf`
- `SUPPLEMENTARY_CAIC.pdf`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`
- `UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip`
- `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`
- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

## Additional remediation after risk review

- Found processed Norman h5ad input at `/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad`.
- Verified `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_norman_multi_perturbation.py` from a clean unpacked supplementary archive. The rerun reproduced the KLF1, CEBPE, and CEBPA PGAA-W AUROC/AUPRC values used in the manuscript.
- Verified `NORMAN2019_H5AD=/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad python3 scripts/benchmark_mmd_psm.py` from a clean unpacked supplementary archive. The rerun reproduced MMD-PSM AUROC 0.499, 0/9 nominal CEBPE target hits, and 0 GAPDH negative-control hits.
- Updated the manuscript, supplement, README, reproducibility report, and risk register to state that the processed h5ad is not bundled but full Norman/MMD-PSM reruns have been verified when `NORMAN2019_H5AD` is supplied.

## Final upload directory

`FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING` contains exactly:

- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`
- `MANUSCRIPT.docx`
- `PGAA_supplementary_code.zip`
- `SUPPLEMENTARY.pdf`

## SHA256

| File | SHA256 |
|---|---|
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf` | `073f5397ae784dcf363a4516336e62c37c51e7d3ae215b5de64b45a2e4795006` |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | `3a91125a4e52b26e7e804f76a280fd0ded8f1785de5d1a3dc0c09d906baf547d` |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | `893817dfcbc8ad62169731c549de57de9c3a4ba5a31324ae73cc8c3bd949e779` |
| `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf` | `dfaae366b6861edaa3da278bbd4e74ed9a876be3d0c69426ed044601ecff5abf` |
| `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | `3284bb0487723fd11491d4395bc2e461a0cbeedb176f4ce38a507deab5757191` |

## Visual QC

- Rendered upload DOCX-to-PDF pages to `qc_final_2026_06_28/docx_pdf_check/`.
- Rendered manuscript PDF pages to `qc_final_2026_06_28/main/`.
- Rendered supplementary PDF pages to `qc_final_2026_06_28/supp/`.
- Rendered cover letter PDF pages to `qc_final_2026_06_28/cover/`.
- Contact sheets:
  - `qc_final_2026_06_28/manuscript_contact_sheet.png`
  - `qc_final_2026_06_28/page_check_after_remediation/manuscript_contact_after_remediation.png`
  - `qc_final_2026_06_28/docx_pdf_check/MANUSCRIPT_docx_contact.png`
  - `qc_final_2026_06_28/supplement_contact_sheet.png`
  - `qc_final_2026_06_28/cover_contact_sheet.png`
- Visual result: after PGAA-H guardrail, Norman rerun remediation, and Supplementary Table 7 longtable remediation, the source manuscript PDF rendered as 20 pages; supplementary PDF rendered as 19 pages; cover letter PDF rendered as 1 page. The 20-page manuscript contact sheet showed no blank pages, no clipped figures, and no obvious table overflow. Supplementary Table 7 spans pages 12-13 and remains dense but readable.

## Final status

The final package is internally consistent, claim-controlled, and ready for final human review before submission.
