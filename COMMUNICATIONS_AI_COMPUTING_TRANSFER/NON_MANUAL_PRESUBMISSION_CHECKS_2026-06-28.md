# Non-manual presubmission checks

Date: 2026-06-28

Scope: Communications AI & Computing PGAA final package, excluding final human Microsoft Word review.

## Summary verdict

PASS after one cover-letter correction. No new analyses or numerical claims were added.

## Issues found and fixed

| Issue | Status | Fix |
|---|---|---|
| Cover letter did not explicitly state that the manuscript has not been published elsewhere and is not under consideration by another journal | fixed | Added the Springer Nature-standard exclusivity and author-approval sentence to `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md` |
| Regenerated cover letter initially became a 2-page PDF with address spillover | fixed | Shortened the cover letter and regenerated it with a cover-letter-specific 0.75 inch margin |
| Cover-letter PDF text extraction split the Transparent Peer Review phrase across a line | fixed | Rephrased as a short standalone sentence: "In addition, we opt in to Transparent Peer Review." |
| Old intermediate `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.tex` contained stale revised/reframed language | fixed | Regenerated the `.tex`, `.docx`, and `.pdf` from the current Markdown source |

## Checks completed

| Check | Status | Evidence |
|---|---|---|
| Communications AI & Computing article type | passed | CAIC accepts Article submissions; the portal input uses `Article` |
| Initial-submission format risk | passed | CAIC states that initial submissions do not need to adhere to final formatting requirements; current package provides a Word manuscript, supplementary PDF, cover letter PDF, and code zip |
| Reference style risk | passed | Existing strict audit confirms references 1-35 are sequential, all cited, and DOI-bearing references match Crossref metadata |
| Figure/table numbering risk | passed | Existing figure/table audit confirms main Figure 1-5, main Table 1-3, Supplementary Figure 1-6, and Supplementary Table 1-7 order |
| Cover-letter required statements | passed | Final PDF text contains journal name, article framing, no-other-journal statement, author approval, no competing interests, no external funding, and Transparent Peer Review opt-in |
| Cover-letter page count | passed | Final `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf` is 1 page |
| Upload folder file set | passed | `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING` contains exactly 4 files |
| Journal upload zip synchronization | passed | Rebuilt by `build_caic_journal_upload_packet.py`; strict upload audit passed |
| CAIC transfer readiness | passed | `verify_caic_transfer_ready.py` passed after cover-letter rebuild |
| Strict CAIC final audit | passed | `strict_caic_final_audit.py` passed 28 checks |
| Portal abstract | passed | `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md` abstract matches manuscript abstract |
| Portal keywords | passed | Portal keywords match manuscript keywords in semicolon-separated portal format |
| Portal administrative fields | passed | Corresponding author, data availability, code availability, competing interests, funding, ethics, author contributions, and open peer review preference are present and non-placeholder |
| Public GitHub repository | passed | `https://github.com/xutaoguo55/pgaa` returned HTTP 200 |
| GitHub release | passed | `https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code` returned HTTP 200 |
| Zenodo DOI | passed | `https://doi.org/10.5281/zenodo.20681141` resolved to Zenodo with HTTP 200 |
| Software Heritage SWHID | passed | Software Heritage resolve API returned HTTP 200 for `swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f` |
| GEO accessions | passed | GSE111014, GSE167363, GSE159117, GSE116222, GSE133344, and GSE90546 returned HTTP 200 from NCBI GEO |
| 10x PBMC demo | passed | 10x Genomics 3k PBMC dataset page returned HTTP 200 |

## Commands rerun after cover-letter fix

| Command | Status |
|---|---|
| `pandoc COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md -o COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx` | passed |
| `pandoc COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md -o COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.tex --standalone -V geometry:margin=0.75in` | passed |
| `Rscript -e "tinytex::xelatex('COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.tex')"` | passed |
| `python3 build_caic_journal_upload_packet.py` | passed |
| `python3 final_upload_strict_audit_2026_06_25.py` | passed |
| `python3 verify_caic_transfer_ready.py` | passed |
| `python3 strict_caic_final_audit.py` | passed |

## Remaining human-only checks

- Open `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` in Microsoft Word and inspect page layout, figures, tables, equation rendering, and reference display.
- Enter portal metadata manually and compare each field with `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md`.
- Confirm author order, affiliations, corresponding-author details, funding statement, and author-contribution wording with all coauthors.
- Confirm inside the live submission system whether any optional separate figure upload or checklist upload is requested at the first-submission step.

