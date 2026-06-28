# Code and Software Submission Checklist for Communications AI & Computing

Corresponding author: Xutao Guo  
Last updated by author: 2026-06-23  
Manuscript: A distribution-aware computational framework for prioritizing heterogeneous responses in single-cell perturbation data

This completed text version follows the Nature Portfolio guidance for submitting code and software. The submitted work contains new custom software central to the manuscript, so the relevant materials are provided in the public code repository and the submitted supplementary software archive.

## Software identity

- Software name: PGAA
- Version referenced in the manuscript: v0.1.0-code
- License: MIT
- Public repository: https://github.com/xutaoguo55/pgaa
- Release: https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code
- Persistent archive: https://doi.org/10.5281/zenodo.20681141
- Software Heritage archive: swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f

## Required documentation for peer review

### Source code and version details

Provided. The source code is included in the submitted `PGAA_supplementary_code.zip` archive and in the public repository. The manuscript identifies release `v0.1.0-code`.

### README and documentation

Provided. The public repository and supplementary software archive include README and package metadata files describing installation, dependencies, example usage and reproducibility materials.

### Installation guide

Provided. The repository includes Python packaging metadata, `requirements.txt`, `environment.yml`, and Dockerfile materials. The R implementation is included under `pgaa_r/`.

### Operating system and programming language

PGAA is implemented in Python and R. The code is intended for standard Unix-like scientific-computing environments and can be run from source. The submitted archive includes environment files for dependency reconstruction.

### Dependencies

The Python package depends on NumPy, SciPy, Pandas, Scanpy and scikit-learn. The R package uses base R plus MASS. Full dependency files are provided in the repository and supplementary software archive.

### Non-standard hardware

No non-standard hardware is required. The manuscript reports representative runtimes on a single CPU core.

### Typical installation time

Typical installation time is expected to be minutes on a current workstation when dependencies are available through standard package managers. No GPU or specialized accelerator is required.

### Demo and test dataset

Provided. The supplementary software archive and repository include smoke/regression checks and toy/example scripts, including:

- `scripts/run_toy_example.py`
- `scripts/test_python_pkg.py`
- `tests/`
- `scripts/test_r_pkg.R`

### Typical run time

The manuscript reports that PGAA-W Wasserstein processes 2,000 genes with 2,000 permutations in about five minutes on a single CPU core, and PGAA-H histogram-shape with 500 permutations takes under two minutes.

### Open repository and DOI

Provided. The code is public on GitHub and archived with a Zenodo DOI. Software Heritage archival identifier is also provided.

### License

Provided. PGAA is released under the MIT license. The license is stated in the repository, supplementary software archive and Code availability statement.

### Independent testing before submission

The submitted package includes automated smoke/regression checks for the Python and R implementations. The package has been built and checked locally before submission. External colleague testing is recommended before final acceptance but has not been separately documented here.

## Information included in manuscript or Methods

### Key operations performed by the software

The manuscript describes Wasserstein distributional ranking, persistent-homology histogram-shape ranking, conditional mutual information, Fisher negative-binomial distance, permutation calibration and Storey pi0 diagnostics.

### Fundamental task and general approach

PGAA ranks heterogeneous transcriptional responses in single-cell perturbation and marker-anchored contrast data. It compares full expression distributions and responder-associated shape changes rather than relying only on mean shifts.

### Software characteristics

PGAA is a Python/R source-code package with command-line and script-level usage, reproducibility scripts, source-data tables and figure-reproduction materials.

### Test dataset

The submitted materials include toy/example data for smoke tests and processed source-data tables used for figure reproduction. Public datasets used in the manuscript are identified by accession number.

### Reproducibility of test results

Smoke and regression checks are included. Manuscript-specific figure-reproduction scripts and processed source-data tables are supplied in the supplementary software archive.

## Code availability statement support

The manuscript states how code is available, identifies the public repository and DOI, describes the MIT license and clarifies that manuscript-specific source-data and figure-reproduction materials are included in the submitted supplementary software archive for peer review.
