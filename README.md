# PGAA: distribution-aware testing for single-cell perturbation screens

PGAA is a Python and R framework for Perturb-seq analysis using two
distribution-aware tests:

- S1: a Wasserstein distance statistic for distributional shifts.
- S2: a persistent-homology statistic for heterogeneous or bimodal responses.

The repository supports a Communications Medicine transfer package and retains
the earlier Bioinformatics manuscript sources for provenance. The active
transfer-ready files are under `COMMUNICATIONS_MEDICINE_TRANSFER/`; the software
archive contains the PGAA Python/R code, source data for figures and tables,
tests, build scripts, and reproducibility checks.

## Main Files

- `COMMUNICATIONS_MEDICINE_TRANSFER/MANUSCRIPT_CM.md`: Communications Medicine
  manuscript source.
- `COMMUNICATIONS_MEDICINE_TRANSFER/MANUSCRIPT_CM.pdf`: compiled Communications
  Medicine manuscript.
- `COMMUNICATIONS_MEDICINE_TRANSFER/SUPPLEMENTARY_CM.md`: Communications
  Medicine supplementary source.
- `COMMUNICATIONS_MEDICINE_TRANSFER/SUPPLEMENTARY_CM.pdf`: compiled
  Communications Medicine supplementary material.
- `MANUSCRIPT.md` and `SUPPLEMENTARY.md`: earlier Bioinformatics-oriented
  manuscript sources retained for provenance.
- `build_pdf.py`: Pandoc/TinyTeX build script for the main PDF.
- `scripts/verify_manuscript_consistency.py`: focused manuscript-package audit.
- `COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py`: transfer
  package gate for manuscript, supplementary, code archive, portal inputs, and
  cover letter.
- `COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_journal_upload_packet.py`: creates
  the clean journal-upload directory and zip. This packet excludes internal
  audits and portal-helper files.
- `COMMUNICATIONS_MEDICINE_TRANSFER/PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip`:
  clean Communications Medicine upload packet containing only the manuscript
  PDF, supplementary PDF, supplementary software archive, and cover letter.
- `COMMUNICATIONS_MEDICINE_TRANSFER/PGAA_COMMUNICATIONS_MEDICINE_TRANSFER_PACKET.zip`:
  author-facing transfer-preparation packet that also includes portal text and
  internal readiness audits.
- `scripts/verify_bioinformatics_upload_ready.py`: earlier Bioinformatics
  upload gate retained for provenance.
- `scripts/finalize_archive_metadata.py`: synchronizes the final repository URL
  and archive DOI/persistent identifier across manuscript and metadata files.
- `scripts/rebuild_adamson_full_results.py`: rebuilds the Adamson benchmark
  table from figure source data.
- `DATASET_MANIFEST.tsv`: machine-readable accession, analysis-role, and
  reproduction-status map for all public datasets used in the manuscript.
- `UPLOAD_FILE_MANIFEST.tsv`: upload/include/exclude map for manuscript,
  supplementary, figure, portal, cover-letter, and internal audit files.
- `COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_supplementary_zip.py`: builds a
  CM-specific supplementary software archive without older Bioinformatics
  manuscript PDFs.
- `scripts/build_bioinformatics_upload_packet.py`: earlier Bioinformatics upload
  packet builder retained for provenance.
- `CITATION.cff` and `codemeta.json`: software citation and metadata files for
  GitHub/Zenodo-style archival records.
- `RELEASE_ARCHIVE_CHECKLIST.md`: final release, DOI, and portal-field checklist.

## Install

```bash
pip install -e .
```

For R usage, source the files under `pgaa_r/R/` or install the R package from
`pgaa_r/`.

## Quick Start

Run the self-contained toy example:

```bash
python3 scripts/run_toy_example.py
```

The script generates a small synthetic Perturb-seq-like matrix, runs S1 and S2,
and checks that the planted shift and bimodal responses rank near the top.

Run PGAA from CSV files:

```bash
python3 -m pgaa.cli \
  --expression expression.csv \
  --metadata metadata.csv \
  --target MYC \
  --out-prefix results/MYC \
  --group-column group \
  --perturbed-value perturbed \
  --control-value control \
  --cell-type-column cell_type \
  --library-size-column library_size
```

The expression CSV should have cells as rows, genes as columns, and the first
column as cell IDs. The metadata CSV must contain `cell_id` and a group column.
The command writes `results/MYC.s1.csv` and `results/MYC.s2.csv`.

```python
from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import s2_test

res_s1 = prt_s1_test(
    X, genes, target="MYC",
    perturbed_idx=perturbed_idx,
    control_idx=control_idx,
    n_perms=2000,
    random_state=42,
)

res_s2 = s2_test(
    X, genes, target="MYC",
    perturbed_idx=perturbed_idx,
    control_idx=control_idx,
    n_bins=20,
)
```

## Reproduce Key Tables

```bash
python3 scripts/compare_combinations.py
python3 scripts/table_sceptre_vs_pgaa.py
python3 scripts/rebuild_adamson_full_results.py
python3 scripts/verify_manuscript_consistency.py
python3 scripts/verify_dataset_manifest.py
python3 scripts/verify_upload_file_manifest.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py
python3 build_pdf.py
python3 scripts/build_submission_zip.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_supplementary_zip.py
python3 COMMUNICATIONS_MEDICINE_TRANSFER/build_cm_journal_upload_packet.py
```

`scripts/compare_combinations.py` requires the local Norman 2019 h5ad file used
in the manuscript workflow. `scripts/rebuild_adamson_full_results.py` rebuilds
the Adamson manuscript table from `figure_source_data/fig6_adamson_results.csv`.
The supplementary material also includes dataset-role, parameter, software
availability, runtime/memory, and result-reproduction tables so reviewers can
distinguish raw-data reproduction from source-data reproduction.

## Tests

```bash
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R
python3 -m pytest tests/test_cli.py -q
```

## Public Data

The manuscript uses public datasets: GSE133344, GSE90546, GSE111014, GSE167363,
GSE159117, GSE116222, and the 10x Genomics PBMC 3k demo dataset. See
`DATASET_MANIFEST.tsv` for landing pages, analysis roles, included source-data
files, reproduction commands, and limitations for each dataset.

## License

MIT.

## Citation

Use `CITATION.cff` for software citation metadata. Before final Communications
Medicine submission, make the repository public and add the permanent archive
DOI or persistent URL to `CITATION.cff`, the manuscript availability statement,
and the submission portal after Zenodo, Figshare, Software Heritage, or Code
Ocean deposition.

Run `python3 COMMUNICATIONS_MEDICINE_TRANSFER/verify_cm_transfer_ready.py`
immediately before final upload. It currently permits the explicit repository
and archive placeholder, but the final upload should proceed only after the
GitHub repository is public and an archive DOI or persistent URL has been added.
After the final identifiers are available, run:

```bash
python3 scripts/finalize_archive_metadata.py \
  --repo-url https://github.com/xutaoguo55/pgaa \
  --archive-url https://doi.org/10.xxxx/example
```
