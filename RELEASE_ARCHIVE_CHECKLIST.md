# PGAA Release and Archive Checklist

Use this checklist before final Communications Medicine transfer submission or
before revision resubmission. Nature Portfolio journals expect supporting code
and data to be available from stable URLs when they are central to the
manuscript, so this is a submission gate rather than an optional post-acceptance
task.

## Repository

- Confirm that the public repository URL is final:
  `https://github.com/xutaoguo55/pgaa`.
- Confirm that `MANUSCRIPT.md`, `SUPPLEMENTARY.md`, source-data CSVs, Python/R
  package code, tests, and build scripts are present.
- Confirm that public-release files are tracked in Git, especially:
  `tests/`, `pgaa/cli.py`, `CITATION.cff`, `codemeta.json`, `.zenodo.json`,
  `DATASET_MANIFEST.tsv`, `UPLOAD_FILE_MANIFEST.tsv`, `figure_source_data/`,
  `figures_png/figure_pgaa_workflow.png`, and
  `COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py`.
- Keep generated or submission-only files out of the public repository:
  `BIOINFORMATICS_UPLOAD_PACKET/`, `PGAA_supplementary_code.zip`,
  `PORTAL_INPUTS.md`, cover letters, internal review/audit files, HTML/PDF/DOCX
  build outputs, and deprecated workflow-figure assets.
- Confirm that the deprecated workflow PNG is not referenced by the manuscript,
  README, or supplementary software archive.
- Run:

```bash
python3 scripts/verify_manuscript_consistency.py
python3 scripts/verify_upload_file_manifest.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py
python3 scripts/run_toy_example.py
python3 -m pytest tests -q
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R
python3 build_pdf.py
pandoc SUPPLEMENTARY.md -o SUPPLEMENTARY.tex --from markdown --standalone && Rscript -e "tinytex::xelatex('SUPPLEMENTARY.tex')"
python3 scripts/build_submission_zip.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_supplementary_zip.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_journal_upload_packet.py
```

## Version Tag

- Create a release tag such as `v0.1.0-cm-transfer`.
- Make sure `pyproject.toml`, `CITATION.cff`, and `codemeta.json` use the same
  version.
- Attach `PGAA_supplementary_code.zip` to the release if the journal permits
  supplementary software archives.

## Permanent Archive

- Preferred: connect the GitHub repository to Zenodo and archive the release.
- Alternative: archive via Figshare, Software Heritage, or Code Ocean.
- Before final submission, after the DOI or persistent identifier is assigned,
  update:
  - `COMMUNICATIONS_MEDICINE_TRANSFER/MANUSCRIPT_CM.md` Data and Code availability.
  - `COMMUNICATIONS_MEDICINE_TRANSFER/SUPPLEMENTARY_CM.md` software availability table.
  - `COMMUNICATIONS_MEDICINE_TRANSFER/PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md` Code Availability URL field.
  - `COMMUNICATIONS_MEDICINE_TRANSFER/COVER_LETTER_COMMUNICATIONS_MEDICINE.md` archive-DOI placeholder.
  - `CITATION.cff` if a software DOI is issued.
  - `codemeta.json` software identifier.
  - `.zenodo.json` related identifier if a final DOI should be cross-linked.
  - `COMMUNICATIONS_MEDICINE_TRANSFER/CM_SUBMISSION_READINESS_AUDIT.md`.
- Use `scripts/finalize_archive_metadata.py` to synchronize the final
  repository and archive identifiers across manuscript, portal draft, cover
  letter draft, and metadata files.
- Run `python3 COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py`;
  final upload should not proceed until the remaining public repository/archive
  blocker has been resolved and the placeholders have been replaced.

## Author-Only Portal Fields

- Confirm final author metadata and ORCID IDs.
- Confirm funding statement and conflict-of-interest text.
- Confirm suggested and opposed reviewers if requested by the submission portal.
