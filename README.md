# PGAA: distribution-aware single-cell perturbation analysis

PGAA is a Python and R software package for prioritizing heterogeneous single-cell transcriptional responses. It implements a Wasserstein statistic for full-distribution shifts and a persistent-homology statistic for responder-associated expression-shape changes. The Communications Medicine transfer materials are included under `communications_medicine/` when this archive is unpacked.

## Archive Contents

- `pgaa/`: Python implementation and command-line interface.
- `pgaa_r/`: R implementation.
- `scripts/`: reproducibility scripts, toy example, source-data table rebuilds, and figure-generation helpers.
- `figure_source_data/`: CSV files used to rebuild manuscript figure panels and benchmark summaries.
- `figures_png/`: final figure images used by the manuscript and supplementary PDF.
- `communications_medicine/MANUSCRIPT_CM.pdf`: submitted manuscript PDF.
- `communications_medicine/SUPPLEMENTARY_CM.pdf`: submitted supplementary PDF.
- `communications_medicine/MANUSCRIPT_CM.md` and `SUPPLEMENTARY_CM.md`: manuscript sources.
- `communications_medicine/build_cm_pdf.py`: PDF builder for the main manuscript.
- `DATASET_MANIFEST.tsv`: public dataset accessions, analysis roles, and reproduction status.
- `UPLOAD_FILE_MANIFEST.tsv`: map of journal-upload, supplementary-archive, and internal-only files for the Communications Medicine transfer package.
- `CITATION.cff`, `codemeta.json`, `.zenodo.json`: software citation and archive metadata.

## Install

Install the Python dependencies before running any smoke test:

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

The script generates a small synthetic Perturb-seq-like matrix, runs S1 and S2, and checks that planted distributional and heterogeneous responses rank near the top.

Optional package checks:

```bash
python3 scripts/test_python_pkg.py
Rscript scripts/test_r_pkg.R
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

## Reproduce Key Source-Data Tables

```bash
python3 scripts/rebuild_adamson_full_results.py
python3 scripts/table_sceptre_vs_pgaa.py
python3 scripts/figure_simulation.py
```

`scripts/rebuild_adamson_full_results.py` rebuilds the Adamson benchmark summary from `figure_source_data/fig6_adamson_results.csv`. Some Norman analyses require the processed Norman 2019 h5ad input used in the manuscript workflow and therefore are documented as source-data or processed-data reproducibility rather than a one-command raw GEO-to-final-figure workflow.

## Rebuild Manuscript PDFs

```bash
cd communications_medicine
python3 build_cm_pdf.py
pandoc SUPPLEMENTARY_CM.md -o SUPPLEMENTARY_CM.tex --from markdown --standalone
Rscript -e "tinytex::xelatex('SUPPLEMENTARY_CM.tex')"
```

## Public Data

The manuscript uses public datasets GSE133344, GSE90546, GSE111014, GSE167363, GSE159117, GSE116222, and the 10x Genomics PBMC 3k demo dataset. See `DATASET_MANIFEST.tsv` for accessions, analysis roles, included source-data files, reproduction commands, and limitations.

## License

MIT.

## Citation and Archive Status

Use `CITATION.cff` for software citation metadata. Before final journal submission, the repository should be made public and the permanent Zenodo, Figshare, Software Heritage, or Code Ocean DOI/persistent identifier should be inserted into `CITATION.cff`, `codemeta.json`, `.zenodo.json`, the manuscript availability statement, and the submission portal.
