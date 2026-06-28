# Strict CAIC final audit

Date: 2026-06-27

Scope: final CAIC upload package, Word manuscript, references, figure/table cross-references, and code/upload packet hygiene.

Overall status: PASS

## Checks

| Check | Status | Detail |
|---|---|---|
| reference_count | PASS | 35 references |
| reference_numbering | PASS | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35] |
| all_references_cited | PASS | uncited=[]; missing=[] |
| first_appearance_order | PASS | first sequence=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35] |
| crossref_exact_doi_metadata_match | PASS | all DOI-bearing references match exact Crossref DOI metadata |
| doi_resolution | PASS | 29 DOI-bearing references resolve |
| main_figure_sequence | PASS | [1, 2, 3, 4, 5] |
| supplementary_figure_sequence | PASS | [1, 2, 3, 4, 5, 6] |
| supplementary_table_sequence | PASS | [1, 2, 3, 4, 5, 6, 7] |
| supplementary_labels_nature_style | PASS | no Supplementary Figure/Table S# labels |
| main_figure_files_present | PASS | all mapped main figure files present |
| docx_zip_integrity | PASS | None |
| docx_no_stale_text_or_placeholders | PASS | no stale venue text or figure/table placeholders |
| docx_section_Data availability | PASS | Data availability |
| docx_section_Code availability | PASS | Code availability |
| docx_section_Acknowledgements | PASS | Acknowledgements |
| docx_section_Author contributions | PASS | Author contributions |
| docx_section_Competing interests | PASS | Competing interests |
| docx_section_Supplementary information | PASS | Supplementary information |
| docx_section_References | PASS | References |
| docx_heading_styles_black | PASS | Heading/Title styles are 000000 |
| docx_embedded_main_figures | PASS | 5 embedded media files |
| clean_upload_exact_file_set | PASS | COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf, MANUSCRIPT.docx, PGAA_supplementary_code.zip, SUPPLEMENTARY.pdf |
| journal_zip_integrity | PASS | None |
| journal_zip_exact_file_set | PASS | COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf, MANUSCRIPT.docx, PGAA_supplementary_code.zip, SUPPLEMENTARY.pdf |
| supplementary_code_zip_integrity | PASS | None |
| supplementary_code_zip_no_stale_text | PASS | no stale venue text or old Supplementary S# labels |
| dataset_accessions_present | PASS | GSE111014, GSE167363, GSE159117, GSE116222, GSE133344, GSE90546, 10x Genomics 3k demo |

## Reference Verification

Reference verification table: `REFERENCE_VERIFICATION_TABLE_2026-06-27.tsv`.

DOI-bearing references were checked against exact Crossref `/works/{doi}` metadata and doi.org resolution. Book/chapter or DOI-sparse references are marked as manual-source records and require no renumbering change.

## Dataset Verification

Dataset accessions present in the manuscript: GSE111014, GSE167363, GSE159117, GSE116222, GSE133344, GSE90546, 10x Genomics 3k demo. GEO/10x identity was spot-checked in the previous strict audit; this script verifies no accession was dropped from the final source.
