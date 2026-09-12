# PGAA Release and Archive Checklist

Use this checklist before final Bioinformatics submission or before revision
resubmission. Oxford University Press expects supporting code and data to be
available from stable URLs when they are central to the manuscript, so this is a
submission gate rather than an optional post-acceptance task.

## Repository

- Confirm that the public repository URL is final:
  `https://github.com/xutaoguo55/pgaa`.
- Confirm that `MANUSCRIPT.md`, `SUPPLEMENTARY.md`, source-data CSVs, Python/R
  package code, tests, and build scripts are present.
- Confirm that public-release files are tracked in Git, especially:
  `tests/`, `pgaa/cli.py`, `CITATION.cff`, `codemeta.json`, `.zenodo.json`,
  `DATASET_MANIFEST.tsv`, `UPLOAD_FILE_MANIFEST.tsv`, `figure_source_data/`,
  and `figures_png/figure_pgaa_workflow.png`.
- Keep generated or submission-only files out of the public repository:
  `BIOINFORMATICS_UPLOAD_PACKET/`, `PGAA_supplementary_code.zip`,
  `PORTAL_INPUTS.md`, cover letters, internal review/audit files, HTML/PDF/DOCX
  build outputs, and deprecated workflow-figure assets. The frozen
  `COMMUNICATIONS_MEDICINE_TRANSFER/` and `COMMUNICATIONS_AI_COMPUTING_TRANSFER/`
  directories are historical packages for earlier journal submissions; they are
  not part of the Bioinformatics upload and are verified by their own
  `verify_cm_transfer_ready.py` gate.
- Confirm that the deprecated workflow PNG is not referenced by the manuscript,
  README, or supplementary software archive.
- Run:

```bash
python3 scripts/verify_manuscript_consistency.py
python3 scripts/verify_upload_file_manifest.py
python3 scripts/verify_bioinformatics_upload_ready.py --allow-pending
python3 scripts/run_toy_example.py
python3 -m pytest tests -q
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R
python3 build_pdf.py
pandoc SUPPLEMENTARY.md -o SUPPLEMENTARY.tex --from markdown --standalone && Rscript -e "tinytex::xelatex('SUPPLEMENTARY.tex')"
python3 scripts/build_submission_zip.py
python3 scripts/build_bioinformatics_upload_packet.py
```

## Version Tag

- Create a release tag such as `v0.1.0`.
- Make sure `pyproject.toml`, `CITATION.cff`, and `codemeta.json` use the same
  version.
- Attach `PGAA_supplementary_code.zip` to the release if the journal permits
  supplementary software archives.

## Permanent Archive

- Preferred: connect the GitHub repository to Zenodo and archive the release.
- Alternative: archive via Figshare, Software Heritage, or Code Ocean.
- Before final submission, after the DOI or persistent identifier is assigned,
  update:
  - `MANUSCRIPT.md` Data and Code availability.
  - `SUPPLEMENTARY.md` software availability table.
  - `PORTAL_INPUTS.md` Code Availability URL field.
  - `COVER_LETTER_BIOINFORMATICS.md` archive-DOI placeholder.
  - `CITATION.cff` if a software DOI is issued.
  - `codemeta.json` software identifier.
  - `.zenodo.json` related identifier if a final DOI should be cross-linked.
  - `SUBMISSION_READINESS_AUDIT.md`.
- Use `scripts/finalize_archive_metadata.py` to synchronize the final
  repository and archive identifiers across manuscript, portal draft, cover
  letter draft, and metadata files.
- Run `python3 scripts/verify_bioinformatics_upload_ready.py`; final upload
  should not proceed until the public repository resolves and the archive
  placeholders have been replaced. The gate exits non-zero until then; pass
  `--allow-pending` only for author-review checks.

## Author-Only Portal Fields

- Confirm final author metadata and ORCID IDs.
- Confirm funding statement and conflict-of-interest text.
- Confirm suggested and opposed reviewers if requested by the submission portal.
