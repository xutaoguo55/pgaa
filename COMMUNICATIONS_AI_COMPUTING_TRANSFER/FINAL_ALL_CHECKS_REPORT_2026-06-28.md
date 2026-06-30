# Final all-check report

Date: 2026-06-28

Scope: final Communications AI & Computing PGAA submission package in `COMMUNICATIONS_AI_COMPUTING_TRANSFER`.

## Verdict

PASS for final machine-assisted submission checks. No new manuscript-analysis results were added.

One internal consistency issue was found and corrected: `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md` still contained an older, longer abstract and older keyword wording. It now matches the manuscript abstract and keywords exactly, and the copy under `UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING/` was synchronized.

One later non-manual presubmission issue was also corrected: the cover letter was updated to include the Springer Nature-standard statement that the manuscript has not been published elsewhere and is not under consideration by another journal. The cover letter DOCX/PDF/TEX were regenerated from source; the final cover letter PDF is 1 page and contains the Transparent Peer Review opt-in phrase in stable extracted text. Details are recorded in `NON_MANUAL_PRESUBMISSION_CHECKS_2026-06-28.md`.

Native Microsoft Word GUI inspection was not performed from this terminal session. Instead, the final Word file was converted with LibreOffice headless and rendered visually; that compatibility check passed.

## Upload package consistency

| Check | Status | Evidence |
|---|---|---|
| `strict_caic_final_audit.py` | passed | 28 checks passed; wrote `STRICT_CAIC_FINAL_AUDIT_2026-06-27.md` and `REFERENCE_VERIFICATION_TABLE_2026-06-27.tsv` |
| `final_upload_strict_audit_2026_06_25.py` | passed | wrote `FINAL_UPLOAD_STRICT_AUDIT_2026-06-25.md` |
| `verify_caic_transfer_ready.py` | passed | final CAIC transfer readiness check passed |
| Final upload folder contains only required files | passed | `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING` contains exactly cover letter PDF, `MANUSCRIPT.docx`, `SUPPLEMENTARY.pdf`, and `PGAA_supplementary_code.zip` |
| Journal-upload zip contains only required files | passed | `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` contains exactly the same four files under `JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING/` |
| Upload folder vs journal zip byte identity | passed | all four files hash-matched after zip extraction |
| DOCX zip integrity | passed previously in final hardening run | `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` |
| Code zip integrity | passed previously in final hardening run | `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` |
| Journal zip integrity | passed previously in final hardening run | `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` |

## Word/PDF compatibility and visual QC

| Check | Status | Evidence |
|---|---|---|
| Final DOCX text extraction | passed | `FINAL_ALL_CHECKS_2026_06_28/text/manuscript_docx_plain.txt` |
| Final DOCX to PDF conversion via LibreOffice | passed | generated `FINAL_ALL_CHECKS_2026_06_28/visual/docx_soffice/MANUSCRIPT.pdf`, 20 pages |
| Main manuscript PDF render | passed | 20-page contact sheet: `FINAL_ALL_CHECKS_2026_06_28/visual/main_pdf_contact.png` |
| Supplementary PDF render | passed | 19-page contact sheet: `FINAL_ALL_CHECKS_2026_06_28/visual/supp_pdf_contact.png` |
| Cover letter PDF render | passed | 1-page contact sheet: `FINAL_ALL_CHECKS_2026_06_28/visual/cover_pdf_contact.png` |
| Supplementary Table 7 visual check | passed | table spans pages 12-13; no raw LaTeX command or clipped table tail |
| Bad export-pattern scan | passed | no raw `begin/end{landscape}`, `S2 persistence`, placeholders, or empty parentheses in final extracted text |

## Figure and table citation order

| Artifact | Main figures | Main tables | Supplementary figures | Supplementary tables |
|---|---:|---:|---:|---:|
| Final DOCX text | 1-5 passed | 1-3 passed | 1-7 passed | 1-7 passed |
| Main PDF text | 1-5 passed | 1-3 passed | 1-7 passed | 1-7 passed |
| Supplementary PDF text | main Figure 1-5 only in source mapping, acceptable | main Table 3 note only, acceptable | 1-7 passed | 1-7 passed |

## Reference truth and numbering

| Check | Status | Evidence |
|---|---|---|
| Reference count | passed | 35 references extracted from `MANUSCRIPT_CAIC.md` |
| Reference numbering in DOCX | passed | references numbered 1-35 sequentially |
| Reference numbering in PDF | passed | references numbered 1-35 sequentially; not all displayed as 1 |
| Crossref bibliographic query | passed with manual review for books/no-DOI items | `FINAL_ALL_CHECKS_2026_06_28/crossref_reference_verification.tsv` |
| Final reference truth table | passed | `FINAL_ALL_CHECKS_2026_06_28/reference_truth_audit.tsv`; all 35 rows have PASS-class status |

Notes: book/proceedings references such as MacQueen 1967, Villani 2009, Efron and Tibshirani 1993, and Edelsbrunner and Harer 2010 were treated as bibliographic/manual-pass items rather than ordinary journal DOI matches. JMLR and key single-cell-method references were web-checked where Crossref matching was weak.

## Supplementary code archive smoke checks

Clean archive root: `FINAL_ALL_CHECKS_2026_06_28/code_smoke/pgaa_caic_supplementary`.

| Command/check | Status |
|---|---|
| `python3 -m pip install -e .` | passed |
| `python3 scripts/run_toy_example.py` | passed |
| `python3 scripts/test_python_pkg.py` | passed |
| `Rscript scripts/test_r_pkg.R` | passed |
| `python3 -m pytest tests/test_cli.py -q` | passed |
| `python3 scripts/verify_dataset_manifest.py` | passed |

Detailed logs: `FINAL_ALL_CHECKS_2026_06_28/code_smoke/*.log` and `FINAL_ALL_CHECKS_2026_06_28/repro_smoke_commands.tsv`.

## Portal-field consistency

| Field | Status |
|---|---|
| Title | passed |
| Short title | passed |
| Corresponding author | passed |
| Abstract | corrected and passed; now exact manuscript abstract |
| Keywords | corrected and passed; now exact manuscript keywords with semicolon separators |
| Data availability | passed |
| Code availability | passed |
| Journal fit note | passed; bounded computational-method framing |
| Funding, competing interests, ethics, author contributions | passed |

## Claim-control scan

| Check | Status | Evidence |
|---|---|---|
| `S2 persistence` / `histogram-persistence` residue | passed | no active artifact hits |
| `revised` / `reframed` cover-letter residue | passed | no cover-letter hits |
| Clinical/biomarker/causal overclaim scan | passed after review | hits are negated or bounded, e.g. "not causal", "not clinical biomarker evidence" |
| Discovery/FDR/genome-wide scan | passed after review | hits are limitations, reference titles, or explicit "not FDR-controlled discovery" statements |
| Superiority language | passed after review | statements are bounded, e.g. "not uniformly superior" |

Full scan table: `FINAL_ALL_CHECKS_2026_06_28/overclaim_scan.tsv`.

## Figure quality

| Artifact | Embedded figure count | Minimum effective resolution | Status |
|---|---:|---:|---|
| Main manuscript PDF | 5 | 495 ppi | passed |
| Supplementary PDF | 7 | 580 ppi | passed |

Evidence: `FINAL_ALL_CHECKS_2026_06_28/main_pdf_images.txt` and `FINAL_ALL_CHECKS_2026_06_28/supp_pdf_images.txt`.

## Remaining risks

- Native Microsoft Word GUI rendering was not performed; LibreOffice conversion and PDF render were used as the practical compatibility check.
- Full raw GEO-to-final-figure reproduction remains outside this final hardening pass; the package remains positioned as source-data reproducibility plus partial raw Adamson sanity rerun and processed Norman rerun when `NORMAN2019_H5AD` is supplied.
- Scientific limitations remain as already stated in the manuscript: small Adamson benchmark, sparse target positives, curated Norman target panels, PGAA-H bin sensitivity, and need for broader SCEPTRE-family/scPerturb-scale evaluation.

## Final status

The manuscript package is coherent, claim-controlled, visually checked, reference-checked, code-smoke-tested from the submitted archive, and ready for final human review before submission.
