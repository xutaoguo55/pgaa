# GSE193258 Drug-Screen Source Audit

The public GSE193258 screen package is source-table-backed. Supplementary Data 1 provides replicate-level AUC values, Supplementary Data 2 provides averaged screen values plus hit calls, and the frozen expression matrix is also present locally for branch assignment. The current branch calibration is still sample-size limited because only four cell lines overlap with the frozen branch assignments, but the screen itself is not a black box.

## Source Tables

| Table | Role | Artifact | Status | Rows | Columns | Cell lines | Drugs | Screen formats | Matched branch lines | Screen-only lines |
|---|---|---|---|---:|---:|---:|---:|---|---|---|
| Supplementary_Data_1 | replicate_level_source | GSE193258/41698_2022_337_MOESM2_ESM.xlsx | present | 520 | 9 | 7 | 73 | sequential, upfront | H1975, HCC2935, HCC827, PC9 | HCC2279, HCC4006, II-18 |
| Supplementary_Data_2 | summary_level_source | GSE193258/41698_2022_337_MOESM3_ESM.xlsx | present | 317 | 12 | 7 | 24 | sequential, upfront | H1975, HCC2935, HCC827, PC9 | HCC2279, HCC4006, II-18 |
| GSE193258_RNAseq | frozen_branch_assignment_source | GSE193258/GSE193258_RNAseq_log2TPM_abundance.tsv.gz | present | 19712 | 60 | 4 | 0 | n/a | H1975, HCC2935, HCC827, PC9 | n/a |

## Target Breadth

The GSE193258 screen spans a broad target landscape rather than a single-target assay. ATM and HDAC are highlighted because they are the branch-linked candidates used in the manuscript, but they sit inside a panel that includes many other target classes.

### Supplementary_Data_1

| Rank | Target class | Rows | Cell lines | Drugs | Highlight |
|---|---|---:|---:|---:|---|
| 1 | AXL | 32 | 7 | 4 | no |
| 2 | BRD4 | 24 | 7 | 2 | no |
| 3 | PIK3CB | 22 | 7 | 1 | no |
| 4 | HDAC | 22 | 7 | 2 | yes |
| 5 | AURKB | 21 | 7 | 1 | no |
| 6 | GPX4 | 20 | 7 | 2 | no |
| 7 | PIK3CA | 20 | 7 | 2 | no |
| 8 | SRC | 20 | 7 | 3 | no |
| 9 | CDK4/6 | 20 | 7 | 2 | no |
| 10 | IGF-IR | 20 | 7 | 1 | no |

- Highlight targets in this table: HDAC (rank 4, rows 22), ATM (rank 17, rows 18)

### Supplementary_Data_2

| Rank | Target class | Rows | Cell lines | Drugs | Highlight |
|---|---|---:|---:|---:|---|
| 1 | AURKA | 15 | 7 | 2 | no |
| 2 | CDK4/6 | 14 | 7 | 1 | no |
| 3 | AXL | 14 | 7 | 1 | no |
| 4 | GPX4 | 14 | 7 | 1 | no |
| 5 | SHP2 | 14 | 7 | 1 | no |
| 6 | HDAC | 14 | 7 | 1 | yes |
| 7 | PARP | 14 | 7 | 1 | no |
| 8 | PRMT5 | 14 | 7 | 1 | no |
| 9 | SRC | 14 | 7 | 2 | no |
| 10 | ALK | 14 | 7 | 1 | no |

- Highlight targets in this table: HDAC (rank 6, rows 14), ATM (rank 19, rows 14)

## Source-Coverage Notes

- Replicate table coverage includes ATM rows (18) and HDAC-related rows (18).
- Summary table coverage includes ATM rows (14) and HDAC-related rows (14).
- The frozen RNA-seq matrix is also present locally and is the source basis for the prospective branch assignment layer.
- The matched branch calibration still uses only PC9, HCC827, H1975, and HCC2935 because the frozen branch scores are available only for those four transcriptome-matched models.
- The screen-only cell lines are HCC2279, HCC4006, and II-18; they are part of the public screen source package but remain outside the frozen branch calibration contract.

## Detail Check

| Table | Drug | Cell line | Rows |
|---|---|---|---:|
| Supplementary_Data_1 | AZD0156 | H1975 | 2 |
| Supplementary_Data_1 | AZD0156 | HCC2279 | 2 |
| Supplementary_Data_1 | AZD0156 | HCC2935 | 2 |
| Supplementary_Data_1 | AZD0156 | HCC4006 | 2 |
| Supplementary_Data_1 | AZD0156 | HCC827 | 2 |
| Supplementary_Data_1 | AZD0156 | II-18 | 2 |
| Supplementary_Data_1 | AZD0156 | PC9 | 6 |
| Supplementary_Data_1 | Quisinostat | H1975 | 2 |
| Supplementary_Data_1 | Quisinostat | HCC2279 | 2 |
| Supplementary_Data_1 | Quisinostat | HCC2935 | 2 |
| Supplementary_Data_1 | Quisinostat | HCC4006 | 2 |
| Supplementary_Data_1 | Quisinostat | HCC827 | 2 |
| Supplementary_Data_1 | Quisinostat | II-18 | 2 |
| Supplementary_Data_1 | Quisinostat | PC9 | 6 |
| Supplementary_Data_2 | AZD0156 | H1975 | 2 |
| Supplementary_Data_2 | AZD0156 | HCC2279 | 2 |
| Supplementary_Data_2 | AZD0156 | HCC2935 | 2 |
| Supplementary_Data_2 | AZD0156 | HCC4006 | 2 |
| Supplementary_Data_2 | AZD0156 | HCC827 | 2 |
| Supplementary_Data_2 | AZD0156 | II-18 | 2 |
| Supplementary_Data_2 | AZD0156 | PC9 | 2 |
| Supplementary_Data_2 | Quisinostat | H1975 | 2 |
| Supplementary_Data_2 | Quisinostat | HCC2279 | 2 |
| Supplementary_Data_2 | Quisinostat | HCC2935 | 2 |
| Supplementary_Data_2 | Quisinostat | HCC4006 | 2 |
| Supplementary_Data_2 | Quisinostat | HCC827 | 2 |
| Supplementary_Data_2 | Quisinostat | II-18 | 2 |
| Supplementary_Data_2 | Quisinostat | PC9 | 2 |

## Interpretation

This source audit does not change the branch-vulnerability ceiling. It does make the calibration traceable: the GSE193258 drug-screen result is sourced from explicit supplementary tables and a local RNA-seq matrix, not inferred from the manuscript figure alone. The remaining limitation is the four-model branch matching, not the absence of public source tables.
