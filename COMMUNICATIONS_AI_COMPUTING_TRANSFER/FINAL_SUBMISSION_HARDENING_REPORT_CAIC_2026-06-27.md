# Final Submission-Hardening Report

Date: 2026-06-27

Target package: Communications AI & Computing

Authoritative upload folder: `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

Final upload zip: `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

## Short Change Log

- Removed the draft-like cover-letter fragment `PGAA is a computational framework.`
- Rebuilt the cover letter PDF/DOCX from the Markdown source.
- Fixed supplementary code archive consistency:
  - included `scripts/table1_datasets_summary.csv`, matching `DATASET_MANIFEST.tsv`;
  - included `scripts/rebuild_adamson_full_results.py`, matching the README and reproducibility notes;
  - included CAIC-specific figure files, including `figures_png/figure_caic_entry.png`, `figure_adamson_benchmark.png`, and `figure_norman_main_caic.png`;
  - changed README installation command from `pip install -e .` to `python3 -m pip install -e .`;
  - synchronized README/script terminology from persistent-homology/TDA wording to `S2 histogram-shape`;
  - removed a stale simulation-script output path that could overwrite the current CAIC `figure_5.png`.
- Corrected Supplementary Table 6 figure-source mapping after the final main-figure order:
  - Figure 1 framework;
  - Figure 2 Adamson benchmark;
  - Figure 3 Norman CEBPE S2 example;
  - Figure 4 S2 calibration;
  - Figure 5 observational marker-recovery stress checks.
- Rebuilt `MANUSCRIPT.docx`, `SUPPLEMENTARY.pdf`, `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`, `PGAA_supplementary_code.zip`, and the final journal upload zip.
- Added a DOCX normalization step to `build_caic_docx.py` so the postprocessed OOXML is re-saved through `python-docx` before upload packaging; this fixed LibreOffice's prior `source file could not be loaded` conversion failure.
- Compacted the long DOCX Table 4 using smaller table text and tighter row spacing while preserving the three-line table style and avoiding hard page breaks.

## Manuscript QA Table

| Area checked | Hard error found | Correction | Status |
|---|---|---|---|
| Cover letter | Isolated draft fragment: `PGAA is a computational framework.` | Removed the fragment and tightened the surrounding computational-method paragraph. | Passed |
| Cover letter terminology | Wasserstein/S2 wording was less specific than the manuscript. | Updated to `S1 Wasserstein`, `S2 histogram-shape statistic`, and `Storey upper-tail diagnostics`. | Passed |
| Supplementary Table 6 | Figure-source mapping still reflected an older figure order. | Updated Figure 2-5 mapping to Adamson, Norman CEBPE, S2 calibration, and observational stress checks. | Passed |
| Supplementary archive manifest | `DATASET_MANIFEST.tsv` referenced `scripts/table1_datasets_summary.csv`, but the zip builder excluded it. | Removed the exclusion and made the file required in `build_caic_supplementary_zip.py`. | Passed |
| Supplementary archive README | README referenced `scripts/rebuild_adamson_full_results.py`, but the prior zip did not include it. | Made the script a required archive entry. | Passed |
| Figure-source mapping | Figure 1 mapping referenced `figures_png/figure_caic_entry.png`, but the prior archive lacked this CAIC-specific image. | Explicitly copied CAIC figure files into the archive. | Passed |
| Script terminology | Archive scripts printed `S2 persistence` or `TDA` labels. | Updated output labels to `S2 histogram-shape`. | Passed |
| Script side effect | `scripts/figure_simulation.py` could write to the current CAIC `figure_5.png`, conflicting with the final Figure 5 observational panel. | Removed the stale CAIC output path and kept only `figures_png/figure_simulation_powers.png`. | Passed |
| Broken math / placeholders | Final DOCX/PDF/source scan for empty variables, empty parentheses, missing p-value patterns, TODO/TBD/FIXME, and known broken phrases. | No matches after rebuild. | Passed |
| References | Final audits checked references 1-33 and citation ranges. | No uncited or out-of-range reference numbers found. | Passed |
| DOCX processor compatibility | Final `MANUSCRIPT.docx` initially opened with `python-docx` but failed LibreOffice PDF conversion after manual OOXML repacking. | Added builder-level DOCX normalization through `python-docx`; final upload DOCX now converts to PDF with LibreOffice. | Passed |
| Long main table layout | DOCX-derived PDF showed Table 4 continuing across pages 8-9. | Tightened Table 4 font and row spacing without adding hard page breaks. The table still spans two pages, but no overflow or clipped cells were observed. | Passed with residual cosmetic risk |
| Path/source-data mapping | Manuscript and supplement referenced scripts, figure-source CSVs, and CAIC figure files. | Checked referenced source paths against the source tree and final supplementary archive; no missing file references remain. | Passed |

## Reproducibility Check Report

| Check or script | Status | Reason if failed or not run | File or command to fix |
|---|---|---|---|
| `python3 -m pip install -e .` from final code archive | Passed | Installed editable package from the clean extracted final zip. | `README.md` |
| `python3 scripts/run_toy_example.py` from final code archive | Passed | Toy example completed. | None |
| `python3 scripts/test_python_pkg.py` from final code archive | Passed | 9 core tests passed. | None |
| `Rscript scripts/test_r_pkg.R` from final code archive | Passed | 18 R tests passed. | None |
| `python3 -m pytest tests/test_cli.py -q` from final code archive | Passed | 1 CLI test passed. | None |
| `python3 scripts/verify_dataset_manifest.py` from final code archive | Passed | Manifest paths and required fields checked. | None |
| `python3 scripts/rebuild_adamson_full_results.py` from final code archive | Passed | Rebuilt Adamson source-data summary; S1 mean AUROC 0.786 and mean AUPRC 0.0191 reproduced. | None |
| `python3 scripts/table_sceptre_vs_pgaa.py` from final code archive | Passed | Rebuilt Norman CEBPE comparison table with ELANE rank 57 and S2 AUROC 0.476. | None |
| `python3 scripts/figure_simulation.py` from final code archive | Passed | Wrote `figures_png/figure_simulation_powers.png` without touching CAIC main Figure 5. | None |
| `python3 -m pytest tests -q --import-mode=importlib` from root | Passed | 14 active tests passed. | None |
| `python3 scripts/benchmark_norman_multi_perturbation.py` | Passed | Rebuilt KLF1/CEBPE/CEBPA processed-data benchmark summaries. | None |
| `python3 scripts/benchmark_mmd_psm.py` | Passed | Rebuilt processed-source-data MMD-PSM comparator; AUROC 0.499 and 0/9 target hits reproduced. | None |
| `python3 scripts/benchmark_adamson2016.py` | Not run | Raw archive `adamson2016_RAW.tar` was not present and `ADAMSON2016_RAW_TAR` was not set. | Provide the GSE90546 raw tar and rerun with `--tar` or `ADAMSON2016_RAW_TAR`. |
| `python3 verify_caic_transfer_ready.py` | Passed | Packet and upload folder checks passed; manuscript 18 pages, supplement 13 pages. | None |
| `python3 deep_current_submission_audit_2026_06_25.py` | Passed | Upload, DOCX, Markdown, supplement, references, and archive checks passed. | None |
| `python3 strict_caic_final_audit.py` | Passed | Reference and strict final checks passed. | None |
| `python3 final_upload_strict_audit_2026_06_25.py` | Passed | 28 final-upload checks passed. | None |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | Passed | DOCX archive integrity OK. | None |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | Passed | Supplementary code zip integrity OK. | None |
| `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | Passed | Final journal zip integrity OK. | None |
| LibreOffice conversion of final `MANUSCRIPT.docx` | Passed | Converted to an 18-page PDF in `qc_final_2026_06_27/docx_pdf_check/MANUSCRIPT.pdf`. | None |
| DOCX-derived visual contact sheet | Passed | `qc_final_2026_06_27/docx_pdf_check/MANUSCRIPT_docx_contact.png` showed no blank pages, missing figures, clipped tables, or obvious overlap. | None |
| Figure/table/reference order audit | Passed | Main Figure first-reference order is 1-5; main Table first-reference order is 1-4; bibliography references 1-33 are sequential. | None |

## Final Risk Register

| Risk | Status before submission |
|---|---|
| Adamson benchmark is small | Still present; framed as proof-of-principle rather than broad validation. |
| Positive sets are sparse | Still present; AUPRC values are interpreted against random baselines. |
| Norman multi-perturbation benchmark uses curated target panels | Still present; not described as a genome-wide truth benchmark. |
| Top-100 positive recovery remains sparse | Still present; explicitly described in Results and limitations. |
| S2 depends strongly on `n_bins` | Still present; calibration and bin-sensitivity guardrails are visible. |
| S2 500 permutations cannot support genome-wide FDR discovery | Still present; manuscript treats S2 p-values as ranking evidence only. |
| Raw-to-final reproducibility is incomplete | Still present; final package claims source-data reproducibility plus partial raw Adamson sanity rerun, not full raw GEO-to-final-figure reproducibility. |
| Raw Adamson sanity rerun cannot be executed locally | Still present; missing `adamson2016_RAW.tar` is reported as not run. |
| Broader Replogle/SCEPTRE-family evaluation not completed | Still present; listed as future work / residual limitation. |
| Observational datasets may be overread biologically | Controlled; manuscript and cover letter call them marker-recovery stress checks only. |

## Final Upload Contents

`FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/` contains exactly:

- `MANUSCRIPT.docx`
- `SUPPLEMENTARY.pdf`
- `PGAA_supplementary_code.zip`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`

No internal audit files, portal-helper drafts, or old-journal files are present in the final upload folder.
