# Strict regression audit, 2026-06-26

Scope: Communications AI & Computing transfer package after terminology, figure/table, DOCX, and supplementary-layout cleanup.

## Issues found and corrected

1. The DOCX build source still contained old Figure 1 and Figure 2 captions. The build scripts now use "primary starting score" rather than "default score" and "marker-recovery stress checks" rather than "stress tests".
2. The generated DOCX contained an empty `word/comments.xml` part and a comments relationship. The DOCX postprocessor now removes the empty comments part, the comments relationship, and the content-type entry.
3. Supplementary Table 5 and Supplementary Table 6 were placed in consecutive `landscape` environments, which generated a blank supplementary page. The tables now share one landscape block with an internal page break.
4. The deep audit now fails if a DOCX contains comments/tracked-change markup or if the main/supplementary PDF contains a page with only a page number.

## Final validation evidence

- `python3 verify_caic_transfer_ready.py`: PASS.
- `python3 final_upload_strict_audit_2026_06_25.py`: PASS, 28 checks.
- `python3 deep_current_submission_audit_2026_06_25.py`: PASS, including no comments/tracked-change markup and no blank PDF pages.
- `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`: PASS.
- `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip`: PASS.
- `unzip -t MANUSCRIPT_CAIC.docx`: PASS.
- Final manuscript PDF: 17 pages.
- Final supplementary PDF: 13 pages.
- Final upload ZIP contains exactly four files: `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`, `MANUSCRIPT.docx`, `PGAA_supplementary_code.zip`, and `SUPPLEMENTARY.pdf`.
- `MANUSCRIPT_CAIC.docx`, `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx`, and `JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` have identical SHA256 hashes.
- `SUPPLEMENTARY_CAIC.pdf`, `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf`, and `JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING/SUPPLEMENTARY.pdf` have identical SHA256 hashes.

## Visual QC artifacts

- Main manuscript contact sheet: `qc_strict_2026_06_26/main_contact.png`.
- Supplementary PDF contact sheet after blank-page fix: `qc_strict_2026_06_26/supp_contact_final.png`.

