# Raw GEO rerun audit snapshot

## GEO supplementary files visible in saved accession pages
- GSE111014: GSE111014_barcodes.tsv.gz, GSE111014_genes.tsv.gz, GSE111014_matrix.mtx.gz
- GSE116222: GSE116222_Expression_matrix.txt.gz
- GSE133344: GSE133344_RAW.tar, GSE133344_filtered_barcodes.tsv.gz, GSE133344_filtered_cell_identities.csv.gz, GSE133344_filtered_genes.tsv.gz, GSE133344_filtered_matrix.mtx.gz, GSE133344_raw_barcodes.tsv.gz, GSE133344_raw_cell_identities.csv.gz, GSE133344_raw_genes.tsv.gz, GSE133344_raw_matrix.mtx.gz
- GSE159117: GSE159117_RAW.tar
- GSE167363: GSE167363_RAW.tar
- GSE90546: GSE90546_RAW.tar

## Local input inventory
- Norman2019 / GSE133344_filtered_matrix.mtx.gz: (33694, 111668, 362199631) (filtered MatrixMarket)
- Norman2019 / GSE133344_filtered_barcodes.tsv.gz: 111668 (line count)
- Norman2019 / GSE133344_filtered_genes.tsv.gz: 33694 (line count)
- Norman2019 / GSE133344_filtered_cell_identities.csv.gz: 111446 (line count)
- Norman2019 / norman2019_with_symbols.h5ad: (13123, 33694) (processed h5ad)
- Norman2019 / norman2019_full_log.h5ad: (111668, 33693) (processed h5ad)
- Adamson2016 / GSM2406675_10X001_matrix.mtx.txt.gz: (35635, 5768, 14751450) (MatrixMarket)
- Adamson2016 / GSM2406675_10X001_barcodes.tsv.gz: 5768 (line count)
- Adamson2016 / GSM2406675_10X001_genes.tsv.gz: 35635 (line count)
- Adamson2016 / GSM2406675_10X001_cell_identities.csv.gz: 5759 (line count)
- Adamson2016 / GSM2406677_10X005_matrix.mtx.txt.gz: (32738, 15006, 63553399) (MatrixMarket)
- Adamson2016 / GSM2406677_10X005_barcodes.tsv.gz: 15006 (line count)
- Adamson2016 / GSM2406677_10X005_genes.tsv.gz: 32738 (line count)
- Adamson2016 / GSM2406677_10X005_cell_identities.csv.gz: 14857 (line count)
- Adamson2016 / GSM2406681_10X010_matrix.mtx.txt.gz: (32738, 65337, 237812947) (MatrixMarket)
- Adamson2016 / GSM2406681_10X010_barcodes.tsv.gz: 65337 (line count)
- Adamson2016 / GSM2406681_10X010_genes.tsv.gz: 32738 (line count)
- Adamson2016 / GSM2406681_10X010_cell_identities.csv.gz: 65258 (line count)
- CLL2018 / cll_counts.mtx: (36601, 36568, 86825974) (local raw/metadata)
- CLL2018 / cll_genes.txt: 36601 (local raw/metadata)
- CLL2018 / cll_barcodes.txt: 36568 (local raw/metadata)
- CLL2018 / cll_meta.csv: 36569 (local raw/metadata)

## Output-table consistency
- PASS: check=Norman S2 known_hits from current per-gene table; computed=1/9; reported_in_table_sceptre_vs_pgaa=1/9
- PASS: check=Norman S2 ELANE rank by p-value; computed=57; reported_in_table_sceptre_vs_pgaa=57
- INFO: manuscript rank is permutation-p rank: check=Norman S2 ELANE rank by raw S2 score; computed=93; reported_in_table_sceptre_vs_pgaa=57
- PASS: check=Norman S2 summary known_hits; computed=1/9; reported_in_summary=1/9
- PASS: check=Adamson selected perturbation count; computed=5; reported=5
- PASS: check=Adamson mean AUROC S1; computed=0.786; reported=0.786 approx
- PASS: check=Adamson mean AUPRC S1; computed=0.0191; reported=0.0188 approx
- PASS: check=Adamson raw 10X001 sanity rerun mean AUROC S1; computed=0.787; reported=0.786 approx
- PASS: check=Adamson raw 10X001 sanity rerun selected perturbations; computed=5; reported=5
