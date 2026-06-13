# Communications Medicine Submission Readiness Audit

Date: 2026-06-14

## Verdict

The Communications Medicine transfer package is technically upload-ready after final author/portal checks. The public code-only repository is available at `https://github.com/xutaoguo55/pgaa`; the code-only software release is archived at Zenodo DOI `https://doi.org/10.5281/zenodo.20681141` and Software Heritage SWHID `swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f`.

## Files Created

- `MANUSCRIPT_CM.md`
- `MANUSCRIPT_CM.pdf`
- `SUPPLEMENTARY_CM.md`
- `SUPPLEMENTARY_CM.pdf`
- `COVER_LETTER_COMMUNICATIONS_MEDICINE.md`
- `PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md`
- `CM_REQUIREMENTS_AUDIT.md`
- `UPLOAD_PACKET_COMMUNICATIONS_MEDICINE/`

## Communications Medicine Alignment

The manuscript has been reframed around a Communications Medicine-compatible premise: heterogeneous disease-relevant transcriptional responses in single-cell perturbation and patient-derived scRNA-seq analyses. The CM version keeps the computational contribution but presents it as a method/resource with translational relevance rather than as a pure bioinformatics software paper.

Main changes:

- Title now foregrounds disease-relevant heterogeneous transcriptional responses.
- Abstract now starts from disease mechanisms, therapeutic target nomination, and heterogeneous cellular response.
- Introduction now explicitly discusses oncology, immunology, infection, inflammatory disease, patient-derived scRNA-seq, and target prioritization.
- CLL, sepsis, RA, IBD, and PBMC analyses are framed as disease-relevant marker recovery, not causal validation.
- Norman and Adamson remain as experimental Perturb-seq benchmarks.
- Discussion no longer says "No new biological discoveries are claimed"; it now states that observational datasets do not establish new causal mechanisms or clinical biomarkers, but demonstrate prioritization of disease-relevant heterogeneous responses for follow-up.
- Cover letter explicitly states that the submission follows a Nature Methods editorial transfer recommendation.
- Figure 1 is now a Communications Medicine entry schematic: clinical problem -> PGAA distribution-aware statistics -> calibrated translational output.
- Cover letter and portal inputs state an OPT OUT preference for Transparent Peer Review report publication.
- `UPLOAD_PACKET_COMMUNICATIONS_MEDICINE/PGAA_supplementary_code.zip` is now built by the CM-specific archive builder and contains the CM manuscript/supplementary files, not the older Bioinformatics manuscript PDFs.
- `JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE/` and `PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip` are the clean journal-upload artifacts. They contain only `MANUSCRIPT.pdf`, `SUPPLEMENTARY.pdf`, `PGAA_supplementary_code.zip`, and `COVER_LETTER_COMMUNICATIONS_MEDICINE.md`.
- `UPLOAD_PACKET_COMMUNICATIONS_MEDICINE/` and `PGAA_COMMUNICATIONS_MEDICINE_TRANSFER_PACKET.zip` are author-facing transfer-preparation artifacts and include portal text plus internal audit files; do not upload the audit files to the journal portal.

## Verification

Passed:

- `python3 build_cm_pdf.py`
- `pandoc SUPPLEMENTARY_CM.md -o SUPPLEMENTARY_CM.tex --from markdown --standalone`
- `Rscript -e "tinytex::xelatex('SUPPLEMENTARY_CM.tex')"`
- `python3 ../scripts/verify_manuscript_consistency.py`
- `python3 ../scripts/verify_dataset_manifest.py`
- `python3 ../scripts/verify_upload_file_manifest.py`

PDF checks:

- `MANUSCRIPT_CM.pdf`: 14 pages, with line numbers.
- `SUPPLEMENTARY_CM.pdf`: 20 pages.
- Main text before references: approximately 4,915 words, consistent with the Communications Medicine Article guide of approximately 5,000 words.
- First-page render checked visually.
- Figure 1 render checked visually after the clinical/translational entry schematic was added.

Search checks:

- No `Bioinformatics` string in `MANUSCRIPT_CM.md`.
- No `No new biological discoveries` string in `MANUSCRIPT_CM.md`.
- No old structured Bioinformatics abstract labels such as `Motivation:` or `Availability and implementation:` in `MANUSCRIPT_CM.md`.

## Remaining Author/Portal Checks

Before final upload:

- Use the Nature Portfolio transfer link so the Nature Methods editorial recommendation and any transferred materials are visible to Communications Medicine.
- Confirm that OPT OUT is the desired open peer-review preference; if not, change both the cover letter and portal inputs before upload.
- Confirm author metadata, ORCID, funding/conflict statements, and reviewer suggestions/exclusions in the submission portal.
- Revoke the temporary Zenodo access token used to create the DOI.

## Residual Editorial Risk

The manuscript remains a computational method/resource paper. Communications Medicine scope permits new methods, technologies, or resources with significant translational or clinical relevance, but the package will be strongest if the cover letter clearly argues that PGAA serves disease-focused single-cell perturbation and patient-derived scRNA-seq analysis. The principal scientific limitation is unchanged: the disease datasets support marker recovery rather than causal disease mechanisms, and the persistence statistic remains a ranking/diagnostic module with calibration sensitivity.
