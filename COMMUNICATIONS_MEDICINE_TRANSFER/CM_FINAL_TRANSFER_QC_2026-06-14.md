# Communications Medicine Final Transfer QC

Date: 2026-06-14

## Final upload folder

`FILES_TO_UPLOAD_COMMUNICATIONS_MEDICINE/`

Files:

- `MANUSCRIPT.pdf`
- `SUPPLEMENTARY.pdf`
- `PGAA_supplementary_code.zip`
- `COVER_LETTER_COMMUNICATIONS_MEDICINE.pdf`

## Key fixes completed

- Supplementary tables are now restricted to real, sequential tables S1-S11.
- Removed stale/nonexistent `Supplementary Table S12` and `Result reproduction map` references.
- Reworked Supplementary Table S10 into two readable tables: direct comparators and related/background tools.
- Shortened wide table cells in S4, S6, S8, and S9 to prevent paragraph-like table rendering and orphan table rows.
- Shortened the final reproducibility note to remove the orphan final page in the supplementary PDF.
- Added deliberate page breaks before large supplementary table blocks so S4-S11 render as real tables rather than cramped fragments.
- Added an Ethics statement for public-data reanalysis.
- Confirmed Author Contributions, Funding, Competing interests, Data availability, Code availability, AI Tool Use, and open peer-review preference are present.
- Confirmed portal abstract and manuscript abstract body match.

## Verification evidence

- `python3 verify_cm_transfer_ready.py`: PASSED.
- Manuscript PDF: 14 pages, 5 main figures, no main tables.
- Supplementary PDF: 13 pages, S1-S11 only.
- Cover letter PDF: 1 page.
- Final upload folder contains exactly 4 files.
- `PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip`: unzip test passed.
- `PGAA_supplementary_code.zip`: unzip test passed.
- Smoke tests from extracted supplementary zip passed:
  - `python3 scripts/run_toy_example.py`
  - `python3 scripts/test_python_pkg.py`
  - `python3 -m pytest tests -q`
  - `Rscript scripts/test_r_pkg.R`
- Text scans found no stale `planned`, `will be supplied`, `before submission`, `Supplementary Table S12`, `Result reproduction map`, `PGAATRACE`, or old-journal submission residue in the final PDFs.

## Public identifiers

- Public code-only repository: https://github.com/xutaoguo55/pgaa
- GitHub release: https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code
- Zenodo DOI: https://doi.org/10.5281/zenodo.20681141
- Software Heritage SWHID: `swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f`

## Remaining author-only portal checks

- Confirm author order, affiliations, equal-contribution markers, and corresponding-author email.
- Confirm all authors approved transfer submission.
- Enter ORCID(s) if requested by the portal.
