# Change Log: Communications AI & Computing Computational Revision

Date: 2026-06-27

## Scope Repositioning

- Reframed the manuscript as a computational methods paper for heterogeneous single-cell perturbation ranking.
- Removed the cancer-treatment-response validation narrative from the main story.
- Rewrote the title, abstract, keywords, introduction, results order, discussion, cover letter, and portal abstract around a distribution-aware ranking framework.
- Preserved disease-related observational datasets only as marker-recovery stress checks, not as causal, clinical, or biomarker evidence.

## Methodological Framing

- Clarified that PGAA is a hypothesis-generating ranking layer, not a causal discovery method or clinical biomarker tool.
- Positioned S1 Wasserstein as the default statistic for full-distribution shifts.
- Repositioned S2 as a secondary histogram-shape diagnostic for responder-associated expression-shape changes.
- Replaced over-strong language around persistence, discovery, FDR-controlled inference, and pi0 with cautious ranking and calibration wording.
- Standardized Storey terminology as an uncapped upper-tail calibration ratio / diagnostic rather than a pi0 estimate that can exceed 1.

## Benchmark and Comparator Changes

- Added the processed-source-data MMD-PSM comparator summary to the Norman CEBPE section and Table 3.
- Added a Norman 2019 multi-perturbation CRISPRa extension across KLF1, CEBPE, and CEBPA, including a KS distribution-aware baseline plus Welch t and Wilcoxon comparators.
- Added Table 4 for the Norman multi-perturbation target-panel benchmark and kept the interpretation bounded to curated-panel ranking enrichment.
- Rewrote the Adamson 2016 benchmark as proof-of-principle, explicitly noting 13 positives among 2,000 HVGs and interpreting AUPRC relative to the 0.0065 random baseline.
- Rewrote the Norman 2019 CEBPE/ELANE result as a narrow S2 ranking example, not broad target-program recovery.
- Kept full CEBPE program recovery and S2 bin sensitivity limitations explicit.

## Reproducibility and Package Hygiene

- Rebuilt the main manuscript DOCX/PDF, supplementary PDF, supplementary code zip, and clean four-file journal upload package.
- Regenerated the cover letter PDF from the revised computational-methods cover letter.
- Updated the CAIC strict audit scripts to match the current four-file upload packet, Supplementary Tables 1-6, and more robust DOI resolution behavior.
- Updated CLI and toy-example smoke tests so they check S2 behavior under a clearly separated synthetic setting without overstating S2 stability in small samples.

## Figure and Table Handling

- Preserved Figure 1 as a simple two-panel response-regime and workflow figure.
- Updated legends to emphasize ranking, calibration, and evidence boundaries.
- Kept Supplementary Tables 1-6 in the supplementary file and added one main-text benchmark table for the Norman multi-perturbation extension.
- Added figure-to-source-data mapping information in the supplementary materials.

## Files Updated for Submission

- `MANUSCRIPT_CAIC.md`
- `MANUSCRIPT_CAIC.docx`
- `MANUSCRIPT_CAIC.pdf`
- `SUPPLEMENTARY_CAIC.md`
- `SUPPLEMENTARY_CAIC.pdf`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`
- `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md`
- `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`
- `PGAA_COMMUNICATIONS_AI_COMPUTING_TRANSFER_PACKET.zip`
- `FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`
