# Fifth-System Dynamic ATM Validation

## Result

An independent 2026 PC9 osimertinib-DTP system supports the directional claim that a stronger replication-defective branch carries greater added benefit from ATM inhibition. The frozen GSE249721 branch contrast is induced after 28 days in every cell-cycle compartment, while the largest AZD1390 benefit appears at the late DTP time point.

| Phase | Day-28 branch induction | Day-0 replicates | Day-28 replicates |
|---|---:|---:|---:|
| G1 | 2.028 | 2 | 2 |
| S | 0.982 | 2 | 1 |
| G2 | 1.191 | 1 | 1 |

## Dynamic Gradient

| Day | Replication-branch strength | Osimertinib confluence | +AZD1390 confluence | ATM added benefit |
|---:|---:|---:|---:|---:|
| 0 | 0.000 | 72.0 | 72.0 | 0.0 |
| 7 | 0.333 | 42.0 | 35.0 | 7.0 |
| 14 | 0.476 | 32.0 | 24.0 | 8.0 |
| 28 | 0.643 | 55.0 | 23.0 | 32.0 |

Spearman rho = 1.000; one-sided exact permutation p = 0.0417; n = 4 time points.

The local GSE335846 RNA-seq matrix at `data/external/GSE335846/GSE335846_RNA-seq_for_GEO.txt.gz` is a source table with nine Day 0/Day 28 sample columns. A compact local summary shows Day 28 increases in `ATM` and `EGFR`, and decreases in proliferation/replication markers such as `MKI67`, `MCM2`, `MCM5`, `PCNA`, `RAD51`, `RPA2`, and `CDK1`, which is consistent with a replication-defective branch shift.

The linked preprint's data-availability statement points to GEO accession GSE335848, but the public accession viewer does not provide supplementary data files, so the dynamic drug-response source tables remain unavailable publicly.

## Source-Axis Projection

The same source table was projected onto the frozen GSE249721 branch axis without re-ranking genes. The resulting sample-level branch contrast is recorded in `evidence/gse335846_rna_seq_branch_axis_scores.tsv`.

| Day | Samples | Mean source-axis contrast | Min | Max | Spearman rho vs day | Exact p |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5 | -1.971 | -2.175 | -1.661 | 0.866 | 0.0025 |
| 28 | 4 | -0.393 | -1.212 | 0.355 | 0.866 | 0.0025 |

## Evidence Boundary

Branch induction is computed from the public GSE335846 RNA-seq source table without re-ranking genes. Dynamic replication-branch strength and confluence values are still digitized from Figures 3B and 4F of the linked CC-BY preprint and are therefore rank-level evidence, not substitutes for source numerical tables. The paper independently reports significant AZD1390 effects on PC9 confluence, EdU incorporation, and regrowth, and extends the same DDR sensitivity logic to HCC4006 plus low-dose ATR inhibition. This fifth system upgrades ATM from a single-screen association to an independent dynamic DTP replication, while retaining the claim-state compiler as the manuscript's main conclusion.
