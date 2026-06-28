# Raw GEO/local-matrix rerun conclusions

Date: 2026-06-24

## Scope

This audit checked the manuscript analyses against locally available GEO-derived raw or processed public inputs, without re-downloading large archives because the machine had limited free disk space. GEO accession pages were saved under `geo_pages/` and local file inventories were recorded in `raw_input_inventory.csv`.

## Reruns completed

### Norman 2019 CEBPE, GSE133344

Available input: local GSE133344 filtered MatrixMarket files and the processed `norman2019_full_log.h5ad` used by the manuscript workflow.

Commands:

- `python3 scripts/benchmark_prt_s2_nbins20.py`
- `python3 scripts/benchmark_prt_s1.py`
- `python3 scripts/table_sceptre_vs_pgaa.py`

Key rerun results:

- SCEPTRE: ELANE rank 1761/2012, p = 0.92, 30 nominal genes, 0/9 known targets.
- PGAA S1: ELANE rank 1452/2012, p = 0.2234, 1083 nominal genes, 1/9 known targets, AUROC = 0.337.
- PGAA S2, n_bins = 20: ELANE rank 57/2012 by permutation p-value, p = 0.0399, 66 nominal genes, 1/9 known targets at p < 0.05, AUROC = 0.476.
- Combined S1+S2 z: ELANE rank 427/2012, p = 0.0378, 473 nominal genes, 3/9 known targets, AUROC = 0.424.

Correction made:

- `scripts/table_sceptre_vs_pgaa.csv`, `SUPPLEMENTARY.md`, `COMMUNICATIONS_AI_COMPUTING_TRANSFER/SUPPLEMENTARY_CAIC.md`, and the CAIC manuscript text were corrected so S2 nominal known-target hits are `1/9`, not `2/9`.
- The manuscript now distinguishes ELANE at p < 0.05 from PRTN3 being a top-100 ranking signal with p = 0.0679.

### Adamson 2016 UPR CRISPRi, GSE90546

Available input: local `adamson2016_RAW.tar` and extracted GSM MatrixMarket files.

Commands:

- initial failing check: `python3 scripts/benchmark_adamson2016.py`
- fixed raw sanity rerun: `python3 scripts/benchmark_adamson2016.py`

Issue found and fixed:

- The original script tried to call `scanpy.read_10x_mtx()` on prefixed GEO files and failed because the archive contains names such as `GSM2406675_10X001_matrix.mtx.txt.gz`, not `matrix.mtx.gz`.
- The fixed script manually loads `GSM2406675_10X001`, uses `62(mod)_pBA581` as the control, selects the five pre-specified manuscript perturbations, and uses sgRNA labels only for cell selection while using target genes for PGAA.

Raw sanity rerun result:

- Five selected perturbations ran successfully.
- Mean raw sanity AUROC S1 = 0.787, matching the curated manuscript table scale of approximately 0.786.
- This remains a raw sanity rerun, not the canonical final-table builder; the final manuscript table is still rebuilt from `figure_source_data/fig6_adamson_results.csv`.

### CLL 20k local matrix, GSE111014-derived files

Available input: local `cll_counts.mtx`, `cll_genes.txt`, `cll_barcodes.txt`, and `cll_meta.csv`.

Command:

- `python3 scripts/cll20k_4method.py`

Rerun result:

- 20,000-cell HVG rerun completed.
- TCL1A high/low split: high = 5000, low = 10611.
- BCR top-100 hits and AUROC:
  - t-test: 4/13, AUROC = 0.966.
  - S1: 4/13, AUROC = 0.958.
  - S2: 0/13, AUROC = 0.655.
  - S3: 2/13, AUROC = 0.694.

Interpretation:

- The local-matrix CLL rerun supports the qualitative BCR recovery claim for S1, but the AUROC is not the same as the `fig2_multidataset.csv` summary value of 0.87, indicating a metric/universe difference between the full 4-method CLL script and the manuscript summary table.
- This CLL rerun was saved in the audit directory but was not pushed into the final CAIC upload package because the summary-table口径 difference needs a separate reconciliation pass before changing submitted source-data.

## Not fully rerun from raw in this pass

The following datasets did not have local raw matrices in the working tree at the time of this audit, so the current package remains source-data reproducible for them:

- Sepsis, GSE167363.
- RA, GSE159117.
- IBD, GSE116222.
- PBMC 3k 10x demo.

GEO pages for these accessions were reachable and saved under `geo_pages/`, but raw archive download and full preprocessing were not attempted because of limited free disk space and because the current manuscript package documents these analyses as source-data/marker-recovery reproductions.

## Final CAIC package status after fixes

The CAIC upload package was rebuilt after the Norman/Adamson fixes and before the exploratory CLL output was allowed to alter the upload bundle.

Passed checks:

- `python3 verify_caic_transfer_ready.py`
- `python3 strict_caic_final_audit.py`

Final upload folder:

- `COMMUNICATIONS_AI_COMPUTING_TRANSFER/FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/`

Final clean upload zip:

- `COMMUNICATIONS_AI_COMPUTING_TRANSFER/PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip`

Residual risk:

- A complete raw-GEO-to-final-figure workflow is still not available for every observational dataset.
- CLL full-script rerun uses a different evaluation口径 from the manuscript summary CSV and should be reconciled before any further claim strengthening.
