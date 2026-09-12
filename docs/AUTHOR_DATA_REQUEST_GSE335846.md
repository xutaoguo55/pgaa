Subject: Request for source numerical data for GSE335846 / osimertinib DTP preprint

Dear GSE335846 authors,

We are reusing your public GSE335846 RNA-seq dataset to study replication-defective drug-tolerant persister states in EGFR-mutant lung cancer. The GEO RNA-seq matrix is available and sufficient for our transcriptomic branch analysis, but we would like to replace figure-level digitization with source numerical values for the replication and ATM-inhibitor response analyses.

If available, a flat CSV, TSV, or XLSX table with one row per biological replicate would be ideal. We only need source numerical values and the minimal sample metadata required to trace each measurement back to its figure panel and replicate.

Would you be willing to share the source numerical tables for:

- PC9_Figure3B_replication_polarity: day, replicate, initiation_zone_id_or_bin, polarity_or_directionality_metric [preferred format: CSV, TSV, or XLSX; shared metadata: cell_line, sample_id, plate_id, passage_number, treatment_state, osimertinib_concentration_nM, normalization_method]
- PC9_Figure4F_confluence: day, replicate, treatment, confluence_percent_or_normalized_cell_number [preferred format: CSV, TSV, or XLSX; shared metadata: cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, imaging_timepoint]
- PC9_Figure4G_EdU: day, replicate, treatment, edu_positive_fraction [preferred format: CSV, TSV, or XLSX; shared metadata: cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, EdU_pulse_hours]
- PC9_Figure4H_regrowth: withdrawal_day, replicate, treatment, time_to_100_percent_confluence_or_auc [preferred format: CSV, TSV, or XLSX; shared metadata: cell_line, sample_id, plate_id, withdrawal_day, passage_number, post_withdrawal_observation_window, osimertinib_concentration_nM]
- HCC4006_SupplementaryFigure4B_D: day, replicate, treatment, confluence_or_edu_or_regrowth_metric [preferred format: CSV, TSV, or XLSX; shared metadata: cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, assay_label]

If the figures are split across multiple worksheets or files, we can reconstruct the merged table ourselves as long as the row-level values and identifiers are present. We would cite the preprint and GEO accession directly, preserve the preprint and non-peer-reviewed status, and use the values only for a bounded computational validation of branch-specific ATM sensitivity.

Best regards,
