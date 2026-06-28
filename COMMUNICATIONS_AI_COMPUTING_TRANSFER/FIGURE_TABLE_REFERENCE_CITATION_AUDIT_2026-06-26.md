# Figure, Table, Supplementary Item, and Reference Citation Audit

Date: 2026-06-26

Scope:
- `MANUSCRIPT_CAIC.md`
- `MANUSCRIPT_CAIC.docx`
- `MANUSCRIPT_CAIC.pdf`
- `SUPPLEMENTARY_CAIC.md`
- `SUPPLEMENTARY.pdf`
- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

## Verdict

PASS after correction.

All main figures, main tables, supplementary figures, supplementary tables, and references are cited. Reference numbers 1-33 are all used, no out-of-range reference number is present, and the first-use order is 1 through 33.

## Corrections made

Four supplementary items previously had only weak/general coverage or internal supplementary coverage. They now have explicit main-text citations:

- Supplementary Figure 4: cited in Section 2.4 for the CEBPE QQ plot and permutation p-value histogram.
- Supplementary Figure 5: cited in Section 2.2 for Adamson 2016 BHLHE40 gene-level and distribution details.
- Supplementary Figure 6: cited in Section 4.8 for the end-to-end PGAA testing workflow.
- Supplementary Table 6: cited in Code availability for implementation settings, reproducibility status, and comparator coverage.

## Main Figures

- Figure 1: cited before the figure; caption describes panels a and b.
- Figure 2: cited before the figure; caption describes panels a, b, and c.
- Figure 3: cited before the figure; caption describes panels a, b, c, and d.
- Figure 4: cited before the figure; caption describes panels a and b.
- Figure 5: cited before the figure; caption describes panels a, b, and c.

## Main Tables

- Table 1: cited before the table; used for evidence-level framing.
- Table 2: cited before the table; used for Adamson 2016 aggregate benchmark performance.
- Table 3: cited before the table; used for Norman 2019 CEBPE ranking and calibration summary.

## Supplementary Figures

- Supplementary Figure 1: cited in the Norman 2019 CEBPE result text; caption describes panels a and b.
- Supplementary Figure 2: cited in the CLL complementary analysis text; caption describes panels a, b, and c.
- Supplementary Figure 3: cited in the simulation-ablation text; caption describes panels a, b, and c.
- Supplementary Figure 4: cited in the calibration-guardrail text; caption describes panels a and b.
- Supplementary Figure 5: cited in the Adamson/BHLHE40 text; caption describes panels a and b.
- Supplementary Figure 6: cited in the implementation text; this is a single workflow schematic and therefore does not require panel labels.

## Supplementary Tables

- Supplementary Table 1: cited for persistence hyperparameter sensitivity.
- Supplementary Table 2: cited for marker-recovery datasets and CLL marker-recovery details.
- Supplementary Table 3: cited for the Adamson 2016 UPR marker set.
- Supplementary Table 4: cited for Norman 2019 CEBPE target-level details.
- Supplementary Table 5: cited for Adamson 2016 per-perturbation benchmark and a priori perturbation selection.
- Supplementary Table 6: cited for implementation settings, reproducibility status, and comparator coverage.

## References

- Bibliography contains references 1-33.
- Text cites references 1-33.
- Missing references: none.
- Out-of-range references: none.
- First-use order: 1, 2, 3, ..., 33.

## Build and Package Checks

The following checks passed after rebuilding the corrected files:

- `python3 build_caic_docx.py`
- `python3 build_caic_pdf.py`
- `python3 build_caic_journal_upload_packet.py`
- `python3 final_upload_strict_audit_2026_06_25.py`
- `python3 verify_caic_transfer_ready.py`
- `python3 deep_current_submission_audit_2026_06_25.py`
- `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

Final upload folder:

- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

