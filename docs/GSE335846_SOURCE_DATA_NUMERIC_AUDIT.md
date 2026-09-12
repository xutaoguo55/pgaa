# GSE335846 Source-Data Numerical Audit

## Verdict

The public materials now support the current RNA-seq branch-induction analysis with a local source table, but they do not expose source numerical tables for the replication-origin polarity and ATM-combination response panels. The preprint data-availability statement points to the super-series accession `GSE335848`, while the accessible GEO family record in this package is `GSE335846`; the official GEO accession viewer for `GSE335848` states that supplementary data files are not provided, so the dynamic drug-response association remains rank-level figure-digitized evidence until the source values are obtained.

| Source | Numerical status | Usable now | Local artifact | Missing upgrade item |
|---|---|---|---|---|
| gse335846_geo_family | rna_seq_source_table_available_for_branch_axis | branch_induction | present | Figure 3B replication-origin polarity and Figure 4F confluence source values. |
| gse335846_branch_axis_projection | fixed_branch_axis_projection_available | source_axis_projection | present | Dynamic drug-response source tables for confluence, EdU, and regrowth remain missing. |
| gse335848_superseries | geo_accession_available | public_accession_trace | present | Official GEO viewer for GSE335848 states that supplementary data files are not provided, so drug-combination source tables are not public. |
| gse335848_geo_ceiling | no_public_supplementary_files | source_ceiling_trace | not_applicable_public_ceiling | Replicate-level dynamic drug-response tables are not publicly available. |
| biorxiv_preprint_v1 | figure_only_for_drug_response | rank_level_digitization | present | Underlying time-point replicate values for confluence, EdU, regrowth, and replication-origin polarity. |

## Data Request Target

| Requested table | Minimum fields | Purpose |
|---|---|---|
| PC9_Figure3B_replication_polarity | day, replicate, initiation_zone_id_or_bin, polarity_or_directionality_metric | replace figure-digitized replication-branch strength with source numerical values |
| PC9_Figure4F_confluence | day, replicate, treatment, confluence_percent_or_normalized_cell_number | test branch-strength versus AZD1390 added benefit using replicate-level values |
| PC9_Figure4G_EdU | day, replicate, treatment, edu_positive_fraction | triangulate ATM benefit with replication-readout suppression |
| PC9_Figure4H_regrowth | withdrawal_day, replicate, treatment, time_to_100_percent_confluence_or_auc | test whether branch strength predicts delayed resistance regrowth |
| HCC4006_SupplementaryFigure4B_D | day, replicate, treatment, confluence_or_edu_or_regrowth_metric | check whether the PC9 dynamic gradient generalizes to a second EGFR-mutant line |

## Claim Boundary

Use the fifth system as independent dynamic preclinical support, not as a source-table-level pharmacology result. The branch-axis RNA-seq component is now source-table backed; the remaining upgrade target is replicate-level PC9 and HCC4006 values for Figures 3B, 4F, 4G, 4H, and Supplementary Figure 4B-D. Local source artifacts are retained with checksums in the TSV audit so the public-source search can be traced, and the accession split between the preprint and GEO family record is recorded explicitly so the evidence chain stays auditable.
