# Figure, table, and reference citation audit

Date: 2026-06-24

Scope: final CAIC upload manuscript and supplementary material.

Files checked:

- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx`
- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf`
- `MANUSCRIPT_CAIC.md`
- `SUPPLEMENTARY_CAIC.md`
- `PGAA_supplementary_code.zip`
- `STRICT_CAIC_FINAL_AUDIT_2026-06-24.md`
- `REFERENCE_VERIFICATION_TABLE_2026-06-24.tsv`

## Result

Overall status: PASS

## References

- Reference list contains 33 entries.
- All reference numbers 1-33 are cited in the final manuscript.
- No out-of-range reference number was detected.
- First-appearance order in the final Word manuscript is exactly 1-33.
- DOI-bearing references were checked against Crossref metadata in `REFERENCE_VERIFICATION_TABLE_2026-06-24.tsv`.

Parsed first-appearance order from `MANUSCRIPT.docx`:

`1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33`

## Main Figures

- Main text cites Figures 1-5.
- No undefined main figure reference was detected.
- All expected main figure files are present in `COMMUNICATIONS_AI_COMPUTING_TRANSFER/figures_png/`.
- The final Word manuscript contains 5 embedded main figure media files according to `strict_caic_final_audit.py`.
- `PGAA_supplementary_code.zip` contains `figures_png/figure_1.png` through `figures_png/figure_5.png`.

## Supplementary Figures

- Main text cites Supplementary Figures 1-6.
- Supplementary material defines Supplementary Figures 1-6.
- No `Supplementary Figure S#` stale label was detected by the strict CAIC audit.

## Supplementary Tables

- Main text cites Supplementary Tables 1-11.
- Supplementary material defines Supplementary Tables 1-11.
- No undefined supplementary table reference was detected.
- No `Supplementary Table S#` stale label was detected by the strict CAIC audit.

## Commands used

- `python3 strict_caic_final_audit.py`
- Direct XML parsing of `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` for superscript reference order.
- Regex scan of `MANUSCRIPT_CAIC.md` and `SUPPLEMENTARY_CAIC.md` for figure/table references and definitions.
- Zip inventory check of `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip`.

## Residual note

No citation-order, unreferenced-reference, undefined-figure, or undefined-table issue was found in the final CAIC upload package.
