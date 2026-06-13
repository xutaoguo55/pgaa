# PGAA

PGAA is a Python and R software package for distribution-aware analysis of single-cell perturbation data. It provides statistics for full expression-distribution shifts and responder-associated expression-shape changes.

This public repository contains code only: package source, tests, installation files, license, citation metadata, and a toy smoke-test script. Manuscript drafts, submission files, figures, source-data tables, and review materials are not included in this public code repository.

## Contents

- `pgaa/`: Python implementation and command-line interface.
- `pgaa_r/`: R implementation.
- `tests/`: Python tests.
- `scripts/run_toy_example.py`: self-contained synthetic smoke test.
- `scripts/test_python_pkg.py`: Python package smoke test.
- `scripts/test_r_pkg.R`: R package smoke test.
- `pyproject.toml`, `requirements.txt`, `environment.yml`, `Dockerfile`: installation and environment files.
- `CITATION.cff`, `codemeta.json`, `.zenodo.json`: software citation metadata.

## Install

Install the Python package and dependencies:

```bash
pip install -e .
```

Alternatively, create the supplied conda environment:

```bash
conda env create -f environment.yml
conda activate pgaa
pip install -e .
```

For R usage, source the files under `pgaa_r/R/` or install the R package from `pgaa_r/`.

## Quick Smoke Test

After installation, run the self-contained toy example:

```bash
python3 scripts/run_toy_example.py
```

Optional package checks:

```bash
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R
python3 -m pytest tests/test_cli.py -q
```

## Command-Line Example

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

The expression CSV should have cells as rows, genes as columns, and the first column as cell IDs. The metadata CSV must contain `cell_id` and a group column. The command writes `results/MYC.s1.csv` and `results/MYC.s2.csv`.

## License

MIT.
