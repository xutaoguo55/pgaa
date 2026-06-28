# Communications AI & Computing transfer package

Status: technically ready for portal transfer/upload after author-side portal checks.

## Upload folder

Use:

`FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

Contents:

1. `MANUSCRIPT.pdf`
2. `SUPPLEMENTARY.pdf`
3. `PGAA_supplementary_code.zip`
4. `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf`

Equivalent clean upload zip:

`PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

## Author helper files

Author-facing packet:

`UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING/`

This includes the same upload PDFs/ZIP plus:

- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md`
- `COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx`
- `PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md`

Do not upload the author helper files unless the portal specifically asks for pasted metadata or editable cover-letter text.

## Reframing completed

- Title changed to: `A distribution-aware computational framework for prioritizing heterogeneous responses in single-cell perturbation data`.
- Abstract now leads with the computational problem of heterogeneous single-cell perturbation responses.
- Introduction now foregrounds Perturb-seq analysis, distribution-shape changes, calibration diagnostics, and software reproducibility.
- Observational disease datasets are framed as external marker-recovery stress tests, not causal validation.
- Cover letter explicitly states that this transfer follows the Communications Medicine desk rejection and editorial recommendation, while positioning the revised manuscript for Communications AI & Computing.

## QC run

Command:

```bash
python3 verify_caic_transfer_ready.py
```

Result:

```text
CAIC TRANSFER CHECK PASSED
Packet files: 7
Clean journal-upload files: 4
Manuscript pages: 14
Supplement pages: 17
Public code-only repository, Zenodo DOI, and Software Heritage SWHID are present
```

Additional checks:

- `PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` unzip test passed.
- Final upload PDFs: cover letter 2 pages, manuscript 14 pages, supplementary 17 pages.
- Main manuscript text scan found the CAIC computational framing and did not find `Communications Medicine` or `Bioinformatics`.
