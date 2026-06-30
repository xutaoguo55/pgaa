# Final upload strict audit

Date: 2026-06-25

Scope: current final Communications AI & Computing upload directory, clean journal-upload ZIP, final DOCX, generated manuscript PDF, supplementary PDF, supplementary code ZIP, figure embedding, references, figure/table labels, and stale-text leakage.

Overall status: PASS

## Checks

| Check | Status | Detail |
|---|---|---|
| upload_exact_file_set | PASS | COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf, MANUSCRIPT.docx, PGAA_supplementary_code.zip, SUPPLEMENTARY.pdf |
| journal_dir_exact_file_set | PASS | COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf, MANUSCRIPT.docx, PGAA_supplementary_code.zip, SUPPLEMENTARY.pdf |
| upload_and_journal_dirs_synced | PASS | all SHA256 values match |
| journal_zip_integrity | PASS | None |
| journal_zip_exact_file_set | PASS | COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf, MANUSCRIPT.docx, PGAA_supplementary_code.zip, SUPPLEMENTARY.pdf |
| journal_zip_matches_upload_dir | PASS | all ZIP payload hashes match upload dir |
| docx_zip_integrity | PASS | None |
| docx_embedded_media_count | PASS | 5 media files: word/media/rId30.png, word/media/rId24.png, word/media/rId15.png, word/media/rId10.png, word/media/rId20.png |
| docx_no_comments_or_tracked_changes | PASS | no comments or tracked-change markup |
| figure1_embedded_png_hash_match | PASS | word/media/rId10.png |
| docx_required_text_present | PASS | 14 required phrases present |
| docx_no_forbidden_text | PASS | no stale placeholders or wrong-journal residue |
| main_figure_caption_sequence | PASS | [1, 2, 3, 4, 5] |
| main_table_caption_sequence | PASS | [1, 2, 3] |
| reference_count_final_docx | PASS | 35 references |
| reference_number_sequence_final_docx | PASS | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35] |
| docx_no_empty_value_patterns | PASS | no empty parentheses or missing numeric-value patterns |
| docx_title_heading_styles_black | PASS | Title and heading styles are black |
| manuscript_pdf_pages | PASS | 20 pages |
| supplementary_pdf_pages | PASS | 20 pages |
| manuscript_pdf_contains_new_figure1_text | PASS | Figure 1 citation and legend present |
| supplementary_figure_sequence_pdf | PASS | [1, 2, 3, 4, 5, 6, 7] |
| supplementary_table_sequence_pdf | PASS | [1, 2, 3, 4, 5, 6, 7] |
| no_old_supplementary_s_labels | PASS | no S-numbered old labels |
| dataset_accessions_present_final_files | PASS | GSE111014, GSE167363, GSE159117, GSE116222, GSE133344, GSE90546, 10x Genomics |
| supplementary_code_zip_integrity | PASS | None |
| supplementary_code_required_entries | PASS | required reproducibility entries present |
| supplementary_code_no_forbidden_internal_entries | PASS | no forbidden internal entries |
