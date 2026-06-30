# PGAA: distribution-aware ranking of heterogeneous single-cell perturbation responses

PGAA is a Python and R software package for prioritizing heterogeneous single-cell transcriptional responses. It implements PGAA-W Wasserstein for full-distribution shifts and the PGAA-H histogram-shape statistic for responder-associated expression-shape changes. The Communications AI & Computing manuscript-support materials are included under `communications_ai_computing/` when this archive is unpacked.

## Archive Contents

- `pgaa/`: Python implementation and command-line interface.
- `pgaa_r/`: R implementation.
- `scripts/`: reproducibility scripts, toy example, source-data table rebuilds, and figure-generation helpers.
- `figure_source_data/`: CSV files used to rebuild manuscript figure panels and benchmark summaries.
- `figures_png/`: final figure images used by the manuscript and supplementary PDF.
- `communications_ai_computing/MANUSCRIPT_CAIC.pdf`: submitted manuscript PDF.
- `communications_ai_computing/SUPPLEMENTARY_CAIC.pdf`: submitted supplementary PDF.
- `communications_ai_computing/MANUSCRIPT_CAIC.md` and `SUPPLEMENTARY_CAIC.md`: manuscript sources.
- `communications_ai_computing/build_caic_pdf.py`: PDF builder for the main manuscript.
- `DATASET_MANIFEST.tsv`: public dataset accessions, analysis roles, and reproduction status.
- `CITATION.cff`, `codemeta.json`, `.zenodo.json`: software citation and archive metadata.

## Install

Install the Python dependencies before running any smoke test:

```bash
python3 -m pip install -e .
```

Alternatively, create the supplied conda environment:

```bash
conda env create -f environment.yml
conda activate pgaa
python3 -m pip install -e .
```

For R usage, source the files under `pgaa_r/R/` or install the R package from `pgaa_r/`.

## Quick Smoke Test

After installation, run the self-contained toy example:

```bash
python3 scripts/run_toy_example.py
```

The script generates a small synthetic Perturb-seq-like matrix, runs PGAA-W and PGAA-H, and checks that planted distributional and heterogeneous responses rank near the top.

Optional package checks:

```bash
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R    # requires R and Rscript; not runnable in R-free environments
python3 -m pytest tests/test_cli.py -q
python3 scripts/verify_dataset_manifest.py
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

Naming note: historical code outputs and filenames use `s1` and `s2` for backward compatibility. In the manuscript terminology, `s1` corresponds to PGAA-W and `s2` corresponds to PGAA-H.

## Reproduce Key Source-Data Tables

```bash
python3 scripts/rebuild_adamson_full_results.py
python3 scripts/table_sceptre_vs_pgaa.py
python3 scripts/figure_simulation.py
```

`scripts/rebuild_adamson_full_results.py` rebuilds the Adamson benchmark summary from `figure_source_data/fig6_adamson_results.csv`. `scripts/benchmark_adamson2016.py` provides a raw GSE90546/GSM2406675 10X001 sanity rerun for the five selected Adamson perturbations and reproduces the reported AUROC scale, but the final PDF table remains rebuilt from the curated source-data CSV. Some Norman analyses require the processed Norman 2019 h5ad input used in the manuscript workflow and therefore are documented as source-data or processed-data reproducibility rather than a one-command raw GEO-to-final-figure workflow. Full MMD-PSM and Norman multi-perturbation recomputation require setting `NORMAN2019_H5AD` to the processed Norman 2019 h5ad file; clean-archive reruns of both scripts have been verified when that input is supplied. Without that input, the archive still supports processed-source-data summaries and manifest checks rather than a full rerun.

## Reproducibility Status

| Check | Expected status |
|---|---|
| `python3 -m pip install -e .` | Should pass |
| `python3 scripts/run_toy_example.py` | Should pass without external data |
| `python3 scripts/test_python_pkg.py` | Should pass (may take ~20 s) |
| `python3 -m pytest tests/test_cli.py -q` | Should pass |
| `python3 scripts/verify_dataset_manifest.py` | Should pass |
| `python3 scripts/rebuild_adamson_full_results.py` | Should pass |
| `python3 scripts/benchmark_mmd_psm.py` | Requires `NORMAN2019_H5AD` |
| `python3 scripts/benchmark_norman_multi_perturbation.py` | Requires `NORMAN2019_H5AD` |
| `Rscript scripts/test_r_pkg.R` | Requires R ≥ 4.0 and Rscript on PATH; not runnable in R-free environments |

## Docker

```bash
docker build -t pgaa .
docker run --rm -v $(pwd):/data pgaa \
  python3 -m pgaa.cli \
  --expression /data/expression.csv \
  --metadata /data/metadata.csv \
  --target MYC \
  --out-prefix /data/results/MYC
```

## Expected Output

The CLI writes two ranked gene tables:

- `<prefix>.s1.csv`: PGAA-W (Wasserstein) scores — `gene`, `W_observed`, `p_value_perm`, rank
- `<prefix>.s2.csv`: PGAA-H (histogram-shape) scores — `gene`, `S2`, `p_value_perm`, rank

Columns: gene identifier, observed score, permutation p-value (plus-one estimator), null mean, null SD, z-score. Supplementary Table 7 (submission supplement) and the supplement CLI schema provide full input/output documentation.

## Troubleshooting

- **`pgaa-run: command not found`**: ensure the pip install location is on PATH, or use `python3 -m pgaa.cli` instead.
- **`ImportError: No module named 'pgaa'`**: run `pip install -e .` from the repository root.
- **`ValueError: Input contains NaN values`**: check that the expression matrix has been normalized (10,000 counts per cell, log1p) before calling PGAA.
- **R tests**: `test_r_pkg.R` requires R ≥ 4.0 and `Rscript` on PATH. Skip if R is not available.
- **MMD-PSM / Norman full rerun**: these scripts require the processed Norman 2019 h5ad input. Set `NORMAN2019_H5AD=/path/to/norman2019_full_log.h5ad` before running. See Supplementary Table 7.

## Rebuild Manuscript PDFs

```bash
cd communications_ai_computing
python3 build_caic_pdf.py
pandoc SUPPLEMENTARY_CAIC.md -o SUPPLEMENTARY_CAIC.tex --from markdown --standalone
Rscript -e "tinytex::xelatex('SUPPLEMENTARY_CAIC.tex')"
```

## Public Data

The manuscript uses public datasets GSE133344, GSE90546, GSE111014, GSE167363, GSE159117, GSE116222, and the 10x Genomics PBMC 3k demo dataset. See `DATASET_MANIFEST.tsv` for accessions, analysis roles, included source-data files, reproduction commands, and limitations.

## License

MIT.

## Citation and Archive Status

Use `CITATION.cff` for software citation metadata. The public code-only repository is available at https://github.com/xutaoguo55/pgaa, the archived software release is available at https://doi.org/10.5281/zenodo.20681141, and the Software Heritage snapshot identifier is `swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f`.
