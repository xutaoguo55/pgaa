# GSE335846 External Dynamic Corroboration

## Result

An independent 2026 PC9 osimertinib-DTP preprint supports the same dynamic resistance logic used in the manuscript: the DTP state is not static, PC9 cells continue to cycle under osimertinib, and low-dose ATM inhibition and low-dose ATR inhibition both reduce DTP survival and return-to-growth behavior. The same paper also reports the related phenotype in HCC4006, which makes it a useful independent corroboration layer.
The preprint's data-availability statement points to GEO accession GSE335848, but the publicly accessible accession viewer does not provide supplementary data files, so replicate-level drug-response source tables remain unavailable in the public record.

## Evidence anchors

| Evidence layer | Preprint line refs | Support statement | Manuscript role | Claim boundary |
|---|---|---|---|---|
| pc9_dynamic_dtp_replication | 40-47; 416-425; 1434-1442 | PC9 keeps cycling under osimertinib, the DTP state is unexpectedly dynamic, and the time-course readouts document repeated EdU positivity and regrowth. | Independent dynamic corroboration | corroboration_only_not_source_table_upgrade |
| atm_sensitivity | 653-677; 1434-1442 | Low-dose ATM inhibition with AZD1390 reduces cell number, replication, and return-to-growth behavior in the PC9 DTP system. | Reinforces the ATM lead | corroboration_only_not_source_table_upgrade |
| atr_sensitivity | 638-677; 1568-1570 | Low-dose ATR inhibition with ceralasertib reduces DTP survival and shows the same DDR logic is not ATM-only. | Shows the DDR logic extends beyond ATM | corroboration_only_not_source_table_upgrade |
| hcc4006_bridge | 124-129; 433-433; 657-657; 1476-1477; 1577-1580 | The same dynamic DTP logic is reproduced in HCC4006, which makes the preprint useful as a second EGFR-mutant bridge. | Secondary generalization bridge | corroboration_only_not_source_table_upgrade |

## Source ceiling snapshot

The corroboration layer does not upgrade the public source ceiling. The current source audit still distinguishes RNA-seq source-table availability from the missing replicate-level dynamic drug-response tables.

source_id	source_numerical_status	usable_for_current_analysis	missing_for_upgrade
gse335846_geo_family	rna_seq_source_table_available_for_branch_axis	branch_induction	Figure 3B replication-origin polarity and Figure 4F confluence source values.
gse335848_superseries	geo_accession_available	public_accession_trace	Official GEO viewer for GSE335848 states that supplementary data files are not provided, so drug-combination source tables are not public.
biorxiv_preprint_v1	figure_only_for_drug_response	rank_level_digitization	Underlying time-point replicate values for confluence, EdU, regrowth, and replication-origin polarity.

## Boundary

This preprint is not a substitute for replicate-level source numerical tables. It strengthens the dynamic ATM branch logic, but it remains below the source-table ceiling and therefore cannot close the submission-grade gap on its own.
