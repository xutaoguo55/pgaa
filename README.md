# PGAA: claim-state compilation for perturbation transcriptomics

PGAA is a Python and R software package for compiling perturbation-transcriptomic analysis outputs into bounded manuscript claim states. The Bioinformatics-first manuscript positions PGAA as an executable claim-state compiler that combines score outputs, stability checks, external evidence, source-data provenance, and promotion gates to control unsupported claim promotion. PGAA-W Wasserstein and PGAA-H histogram-shape statistics remain available as upstream scoring modules for heterogeneous single-cell transcriptional responses. The manuscript, its figures, and the frozen submission packages are deliberately not hosted in this repository: it carries the software, its tests, the reproduction scripts, and the dataset and evidence metadata only. The reviewer-facing archive that contains the article is assembled separately by `scripts/build_submission_zip.py`.

## Archive Contents

- `pgaa/`: Python implementation and command-line interface.
- `pgaa_r/`: R implementation.
- `scripts/`: reproducibility scripts, toy example, source-data table rebuilds, and figure-generation helpers.
- `evidence/`, `docs/`: machine-readable evidence artifacts and the claim-state decision records behind them.
- `ZENODO_CODE_ONLY_RELEASE/`: the code-only archives deposited on Zenodo, built by `scripts/build_zenodo_code_only.py`.

Deliberately absent: the manuscript (`MANUSCRIPT.md`, `MANUSCRIPT.docx`, `SUPPLEMENTARY.md`), the figure images under `figures_png/`, the figure source-data tables under `figure_source_data/`, and the frozen `COMMUNICATIONS_*_TRANSFER/` packages from earlier submissions. They stay in the working copy, so `scripts/build_pdf.py` and `scripts/build_submission_zip.py` still build the reviewer archive from a checkout that has them.
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

The expression CSV should have cells as rows, genes as columns, and the first column as cell IDs. The metadata CSV must contain `cell_id` and a group column. The command writes `results/MYC.s1.csv` (PGAA-W: scores + permutation p-values) and `results/MYC.s2.csv` (PGAA-H: histogram-shape scores only; no permutation p-values). The lightweight CLI does not compute PGAA-H permutation p-values or Storey calibration diagnostics. Calibrated PGAA-H analyses are provided by the dedicated benchmark scripts and source-data tables. Historical output suffixes (`s1`, `s2`) are retained for backward compatibility; `s1` corresponds to PGAA-W and `s2` to PGAA-H.

Naming note: historical code outputs and filenames use `s1` and `s2` for backward compatibility. In the manuscript terminology, `s1` corresponds to PGAA-W and `s2` corresponds to PGAA-H.

## Matched Event-Expression Pilot

GSE112274 provides same-cell PC-9 targeted mutation and expression measurements. The importer locks EGFR T790M-high (`AF >= 0.10`) and T790M-low (`AF <= 0.01`) groups, excludes transition cells, applies `log1p(FPKM)`, and writes a 5,000-gene CLI matrix. This is an observational association input, not a perturbation or immune-validation experiment.

```bash
python3 scripts/import_gse112274_event_expression.py \
  --expression data/external/GSE112274/GSE112274_cell_gene_FPKM.csv.gz \
  --mutation-af data/external/GSE112274/GSE112274_cell_mutation_AF.csv.gz \
  --mutation-dp data/external/GSE112274/GSE112274_cell_mutation_DP.csv.gz \
  --expression-out data/external/GSE112274/processed/t790m_expression_log1p_fpkm_top5000.csv.gz \
  --metadata-out data/external/GSE112274/processed/t790m_metadata.csv \
  --summary-out evidence/gse112274_event_expression_summary.tsv \
  --audit-out docs/GSE112274_MATCHED_EVENT_EXPRESSION_AUDIT.md

python3 -m pgaa.cli \
  --expression data/external/GSE112274/processed/t790m_expression_log1p_fpkm_top5000.csv.gz \
  --metadata data/external/GSE112274/processed/t790m_metadata.csv \
  --target EGFR --out-prefix evidence/gse112274_t790m_pgaa \
  --library-size-column library_size_fpkm --n-perms 2000 \
  --target-only-permutation-p
```

An independent clone-level stress test uses GSE129221 parental PC9 and acquired T790M-positive PC9GR RNA-seq replicates. It tests cross-system direction and exact label-permutation support without treating bulk clone replicates as same-cell evidence.

```bash
python3 scripts/audit_t790m_cross_system_replication.py \
  --cortad-expression data/external/GSE112274/processed/t790m_expression_log1p_fpkm_top5000.csv.gz \
  --cortad-metadata data/external/GSE112274/processed/t790m_metadata.csv \
  --replication-fpkm data/external/GSE129221/GSE129221_fpkm.txt.gz \
  --summary-out evidence/t790m_cross_system_replication_summary.tsv \
  --audit-out docs/T790M_CROSS_SYSTEM_REPLICATION_AUDIT.md
```

GSE75602 adds a stage-resolved PC9 evolutionary stress test. It compares vehicle-state parental, drug-tolerant, early T790M-positive GR2, and late T790M-positive GR3 samples. With only two replicates per state, the exact directional tests are descriptive; the analysis tests comparator and evolutionary-path dependence rather than claiming replication.

```bash
python3 scripts/audit_t790m_evolution_trajectory.py \
  --cpm data/external/GSE75602/GSE75602_CPM.txt.gz \
  --stages-out evidence/gse75602_t790m_evolution_stages.tsv \
  --contrasts-out evidence/gse75602_t790m_evolution_contrasts.tsv \
  --audit-out docs/GSE75602_T790M_EVOLUTION_TRAJECTORY_AUDIT.md

python3 scripts/audit_gse75602_resistance_module_biology.py \
  --annotation evidence/gse75602_resistance_down_module_ensembl_annotation.tsv \
  --pathway-enrichment evidence/gse75602_resistance_down_module_pathway_enrichment.tsv \
  --summary-out evidence/gse75602_resistance_down_module_biology_summary.tsv \
  --report-out docs/GSE75602_RESISTANCE_MODULE_BIOLOGY_AUDIT.md

python3 scripts/audit_gse335846_source_data_numeric.py \
  --source-dir sources/gse335846_dynamic_atm \
  --evidence-out evidence/gse335846_source_data_numeric_audit.tsv \
  --report-out docs/GSE335846_SOURCE_DATA_NUMERIC_AUDIT.md

python3 scripts/audit_gse335846_external_dynamic_corroboration.py \
  --source-dir sources/gse335846_dynamic_atm \
  --preprint sources/gse335846_dynamic_atm/preprint_733326.txt \
  --summary-out evidence/gse335846_external_dynamic_corroboration.tsv \
  --report-out docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md
```

The resistance-state analysis moves from a fixed single-event effect to a distributed module. GSE75602 defines replicate-separated early/late modules; GSE129221 validates the down module without gene re-ranking. A subsequent locked test in GSE249721 falsifies universal directional transfer: the main PC9 contexts reverse direction. A sign-invariant aggregate separation endpoint passes mean-variance-matched decoys, but it was selected after observing heterogeneity and remains exploratory rather than confirmatory.

```bash
python3 scripts/audit_resistance_state_modules.py \
  --discovery-cpm data/external/GSE75602/GSE75602_CPM.txt.gz \
  --validation-fpkm data/external/GSE129221/GSE129221_fpkm.txt.gz \
  --annotation evidence/gse75602_resistance_down_module_ensembl_annotation.tsv \
  --cortad-expression data/external/GSE112274/processed/t790m_expression_log1p_fpkm_top5000.csv.gz \
  --cortad-metadata data/external/GSE112274/processed/t790m_metadata.csv \
  --modules-out evidence/gse75602_resistance_state_modules.tsv \
  --validation-out evidence/gse129221_resistance_module_validation.tsv \
  --routes-out evidence/resistance_state_route_scores.tsv \
  --cortad-out evidence/gse112274_resistance_module_adjusted_validation.tsv \
  --reframe-routes-out evidence/resistance_reframe_route_competition.tsv \
  --audit-out docs/RESISTANCE_STATE_MODULE_ROUTE_AUDIT.md

python3 scripts/audit_resistance_state_separation.py \
  --modules evidence/gse75602_resistance_state_modules.tsv \
  --expression data/external/GSE249721/GSE249721_all_samples_processed_data.tsv.gz \
  --contexts-out evidence/gse249721_resistance_state_separation.tsv \
  --summary-out evidence/gse249721_resistance_state_separation_summary.tsv \
  --audit-out docs/RESISTANCE_STATE_SEPARATION_AUDIT.md \
  --decoys 2000 --seed 249721

python3 scripts/audit_resistance_branching.py \
  --expression data/external/GSE249721/GSE249721_all_samples_processed_data.tsv.gz \
  --effects-out evidence/gse249721_resistance_context_effects.tsv.gz \
  --genes-out evidence/gse249721_resistance_branch_genes.tsv \
  --validation-out evidence/gse249721_resistance_branch_validation.tsv \
  --summary-out evidence/gse249721_resistance_branch_summary.tsv \
  --audit-out docs/RESISTANCE_STATE_BIFURCATION_AUDIT.md

python3 scripts/enrich_resistance_branches.py \
  --genes evidence/gse249721_resistance_branch_genes.tsv \
  --out evidence/gse249721_resistance_branch_enrichment.tsv

python3 scripts/classify_gse193258_resistance_branches.py \
  --branch-genes evidence/gse249721_resistance_branch_genes.tsv \
  --expression data/external/GSE193258/GSE193258_RNAseq_log2TPM_abundance.tsv.gz \
  --assignments-out evidence/gse193258_prospective_branch_assignments.tsv \
  --trajectories-out evidence/gse193258_branch_trajectories.tsv \
  --vulnerabilities-out evidence/gse193258_branch_vulnerability_predictions.tsv \
  --audit-out docs/GSE193258_PROSPECTIVE_BRANCH_AUDIT.md

python3 scripts/calibrate_gse193258_branch_vulnerabilities.py \
  --screen data/external/GSE193258/41698_2022_337_MOESM3_ESM.xlsx \
  --assignments evidence/gse193258_prospective_branch_assignments.tsv \
  --normalized-out evidence/gse193258_drug_screen_normalized.tsv \
  --associations-out evidence/gse193258_branch_drug_associations.tsv \
  --lead-out evidence/gse193258_lead_atm_interaction.tsv \
  --audit-out docs/GSE193258_BRANCH_VULNERABILITY_CALIBRATION.md

python3 scripts/audit_gse193258_drug_screen_source.py \
  --source-dir data/external/GSE193258 \
  --evidence-out evidence/gse193258_drug_screen_source_audit.tsv \
  --report-out docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md

python3 scripts/validate_dynamic_atm_system.py \
  --branch-genes evidence/gse249721_resistance_branch_genes.tsv \
  --expression data/external/GSE335846/GSE335846_RNA-seq_for_GEO.txt.gz \
  --timecourse evidence/gse335846_dynamic_atm_timecourse.tsv \
  --phase-out evidence/gse335846_day28_branch_induction.tsv \
  --association-out evidence/gse335846_dynamic_atm_association.tsv \
  --audit-out docs/GSE335846_DYNAMIC_ATM_VALIDATION.md

python3 scripts/build_atm_hdac_upgrade_package.py

python3 scripts/build_branch_vulnerability_promotion_gate.py

python3 scripts/build_bioinformatics_method_upgrade.py

python3 scripts/render_atm_hdac_branch_map.py
```

The prospective branch assignment now connects prediction to phenotype without treating the result as definitive pharmacology. Across four transcriptome-matched EGFR-mutant models and both upfront and sequential combination screens, the frozen adaptive-stress score shows a directionally complete but sample-size-limited rank association with AZD0156/ATM activity (Spearman rho 1.0; exact one-sided permutation p = 1/24). A companion target-specificity audit and its figure asset show that ATM is the only exact-significant positive target-class signal in the broad GSE193258 screen landscape, while ALK and HDAC form the runner-up positive tier. A fifth independent PC9 dynamic DTP system then supports the same direction at rank level: stronger replication-defective branch time points show greater added benefit from AZD1390/ATM inhibition (Spearman rho 1.0; exact one-sided permutation p = 1/24). The fifth-system time-course values are figure-digitized rank-level evidence from a preprint, so they upgrade dynamic preclinical support without replacing the claim-state compiler as the manuscript's main conclusion. The ATM/HDAC upgrade package records that public GSE335846 materials expose the RNA-seq matrix but not source numerical tables for the replication-polarity and drug-response figures; it therefore adds local source-artifact checksums, an author data-request template, a prospective branch-stratified ATM dose-response design, a self-audit, an ATM/HDAC branch-vulnerability map, a source-table-backed GSE193258 matched-screen audit, and a target-specificity audit that keeps ATM as the clean lead target.
The same study's companion phosphoproteomics workbook adds source-table-backed corroboration at the protein and phosphosite level, with DTP suppression of canonical proliferation markers and ATR-adjacent phosphosite shifts, but it still does not surface exact ATM gene-symbol source tables or change the public source ceiling.

The branch-vulnerability promotion gate makes the forward direction explicit: PGAA is presented as a branch-specific therapeutic-hypothesis compiler with ATM as the primary positive demonstration. The gate permits a branch-specific preclinical ATM vulnerability hypothesis, keeps HDAC secondary, and blocks definitive pharmacology or clinical claims until source-level GSE335846 tables or a prospective branch-by-treatment ATM interaction are available.

The Bioinformatics-first method upgrade reframes the submission as an Original Paper on claim-state compilation. It adds a comparator contract, ablation plan, and figure order in which false-promotion control is the primary methodological endpoint and the ATM branch-vulnerability arc is a later biological use case.

### Submission-Facing Support Assets

The PNG/PDF support figures for Supplementary Figures S4-S7 are rendered into `figures_png/`, which is not hosted in this repository; the scripts that render them and the caption text that accompanies them are listed below.

- `docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md`: caption and Results text for the support figure
- `docs/SUBMISSION_PACKAGE_INDEX.md`: navigation layer for the submission-facing package
- `docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md`: caption and Results text for the third-system support figure
- `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md`: phosphoproteomics corroboration audit
- `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md`: caption and Results text for Supplementary Figure S7
- `evidence/gse335846_phosphoproteomics_corroboration.tsv`: machine-readable phosphoproteomics corroboration summary
- `evidence/gse335846_phosphoproteomics_selected_markers.tsv`: selected marker summary
- `evidence/gse335846_phosphoproteomics_boundary_scan.tsv`: ATM/ATR boundary scan

## Reproduce Key Source-Data Tables

```bash
python3 scripts/rebuild_adamson_full_results.py
python3 scripts/table_sceptre_vs_pgaa.py
python3 scripts/figure_simulation.py
```

`scripts/rebuild_adamson_full_results.py` rebuilds the Adamson benchmark summary from `figure_source_data/fig6_adamson_results.csv`. `scripts/benchmark_adamson2016.py` provides a raw GSE90546/GSM2406675 10X001 sanity rerun for the five selected Adamson perturbations and reproduces the reported AUROC scale, but the final PDF table remains rebuilt from the curated source-data CSV. Some Norman analyses require the processed Norman 2019 h5ad input used in the manuscript workflow and therefore are documented as source-data or processed-data reproducibility rather than a one-command raw GEO-to-final-figure workflow. Norman multi-perturbation recomputation requires setting `NORMAN2019_H5AD` to the processed Norman 2019 h5ad file; a clean-archive rerun of that script has been verified when the input is supplied. Without that input, the archive still supports processed-source-data summaries and manifest checks rather than a full rerun.

## Immune-Evidence Ladder

The optional immune-evidence rescue workflow converts event-derived peptide/HLA candidates into public-evidence tiers for presentation support, synthesis readiness, and T-cell evidence. This is a prioritization audit, not wet-lab validation.

To compile altered event sequence contexts into event-containing peptide/HLA candidate units and matched non-event decoys:

```bash
python3 scripts/audit_event_sources.py \
  --manifest evidence/event_source_manifest.tsv \
  --audit-out evidence/event_source_audit.tsv \
  --markdown-out docs/EVENT_SOURCE_AUDIT.md
```

```bash
python3 scripts/compile_event_peptides.py \
  --events evidence/event_sequence_contexts_template.tsv \
  --candidates-out evidence/event_compiler_smoke_candidates.tsv \
  --decoys-out evidence/event_compiler_smoke_decoys.tsv \
  --allow-smoke
```

```bash
python3 scripts/build_immune_evidence_ladder.py \
  --candidates evidence/candidate_event_peptides_template.tsv \
  --output evidence/immune_evidence_tiers_smoke.tsv \
  --claim-audit docs/IMMUNO_EVIDENCE_CLAIM_AUDIT_SMOKE.md \
  --allow-smoke
```

To exercise local ligand/T-cell evidence matching and decoy background rates:

```bash
python3 scripts/build_immune_evidence_ladder.py \
  --candidates evidence/immune_evidence_smoke_candidates.tsv \
  --ligand-evidence evidence/public_ligand_evidence_template.tsv \
  --tcell-evidence evidence/public_tcell_evidence_template.tsv \
  --decoys evidence/decoy_peptides_template.tsv \
  --annotated-candidates evidence/immune_evidence_smoke_annotated.tsv \
  --output evidence/immune_evidence_tiers_smoke.tsv \
  --claim-audit docs/IMMUNO_EVIDENCE_CLAIM_AUDIT_SMOKE.md \
  --allow-smoke
```

To compare follow-up panels selected by the full ladder and simpler baselines:

```bash
python3 scripts/compare_followup_panels.py \
  --tiers evidence/followup_panel_decision_smoke_tiers.tsv \
  --panel-out evidence/followup_panel_smoke.tsv \
  --summary-out evidence/followup_panel_summary_smoke.tsv \
  --top-n 1 \
  --allow-smoke
```

To stress-test tiers under exact-match-only and decoy-guarded rules:

```bash
python3 scripts/check_threshold_robustness.py \
  --tiers evidence/followup_panel_decision_smoke_tiers.tsv \
  --adjusted-out evidence/threshold_robustness_adjusted_smoke.tsv \
  --summary-out evidence/threshold_robustness_summary_smoke.tsv \
  --top-n 2 \
  --allow-smoke
```

To compare candidates against composition, cross-event, and same-context decoy families:

```bash
python3 scripts/build_multilevel_decoy_enrichment.py \
  --candidates evidence/candidate_event_peptides.tsv \
  --existing-decoys evidence/decoy_peptides.tsv \
  --ligand-evidence evidence/public_ligand_evidence.tsv \
  --tcell-evidence evidence/public_tcell_evidence.tsv \
  --decoys-out evidence/multilevel_decoy_peptides.tsv \
  --summary-out evidence/multilevel_decoy_enrichment_summary.tsv \
  --audit-out docs/MULTILEVEL_DECOY_ENRICHMENT_AUDIT.md
```

To audit whether the rechartered manuscript has enough real non-smoke evidence artifacts to start rewriting:

```bash
python3 scripts/audit_recharter_readiness.py \
  --audit-out evidence/recharter_readiness_audit.tsv \
  --markdown-out docs/RECHARTER_READINESS_AUDIT.md
```

To score recharter routes and build the currently supported failure-mode audit:

```bash
python3 scripts/select_recharter_route.py \
  --routes evidence/recharter_route_options.tsv \
  --scored-out evidence/recharter_route_scores.tsv \
  --report-out docs/RECHARTER_ROUTE_DECISION.md

python3 scripts/build_failure_mode_audit.py \
  --audit-out evidence/failure_mode_audit.tsv \
  --summary-out evidence/failure_mode_summary.tsv \
  --report-out docs/FAILURE_MODE_AUDIT.md

python3 scripts/build_result_claims.py \
  --claims-out evidence/result_claim_states.tsv \
  --summary-out evidence/result_claim_summary.tsv \
  --report-out docs/RESULT_CLAIM_STATE_REPORT.md

# This also compiles the held-out stability and pseudo-perturbation specificity
# results into evidence/response_stability_specificity_dual_gate.tsv.

python3 scripts/build_claim_panel_sources.py \
  --panel-source-out evidence/claim_panel_source_data.tsv \
  --summary-out evidence/claim_panel_summary.tsv \
  --report-out docs/CLAIM_PANEL_SOURCE_REPORT.md

python3 scripts/build_responder_state_units.py \
  --units-out evidence/responder_state_units.tsv \
  --summary-out evidence/responder_state_summary.tsv \
  --report-out docs/RESPONDER_STATE_DECISION_UNITS.md

python3 scripts/check_responder_state_stability.py \
  --detail-out evidence/responder_state_stability_detail.tsv \
  --summary-out evidence/responder_state_stability_summary.tsv \
  --report-out docs/RESPONDER_STATE_STABILITY_REPORT.md

python3 scripts/audit_external_validation_opportunities.py \
  --opportunities-out evidence/external_validation_opportunities.tsv \
  --summary-out evidence/external_validation_summary.tsv \
  --report-out docs/EXTERNAL_VALIDATION_OPPORTUNITY_AUDIT.md

python3 scripts/audit_external_dataset_candidates.py \
  --audit-out evidence/external_dataset_candidate_audit.tsv \
  --summary-out evidence/external_dataset_candidate_summary.tsv \
  --report-out docs/EXTERNAL_DATASET_CANDIDATE_AUDIT.md

python3 scripts/check_external_target_coverage.py \
  --candidate-dataset-id replogle_2022_k562_gwps \
  --h5ad /tmp/pgaa_replogle/K562_gwps_raw_bulk_01.h5ad \
  --source-url https://ndownloader.figshare.com/files/35774443 \
  --coverage-out evidence/external_target_coverage_replogle_k562_gwps.tsv \
  --summary-out evidence/external_target_coverage_replogle_k562_gwps_summary.tsv \
  --report-out docs/EXTERNAL_TARGET_COVERAGE_REPLOGLE_K562_GWPS.md

python3 scripts/plan_external_singlecell_import.py \
  --scratch-dir /tmp/pgaa_replogle \
  --plan-out evidence/external_singlecell_import_plan_replogle_k562_gwps.tsv \
  --summary-out evidence/external_singlecell_import_plan_replogle_k562_gwps_summary.tsv \
  --report-out docs/EXTERNAL_SINGLECELL_IMPORT_PLAN_REPLOGLE_K562_GWPS.md

python3 scripts/build_main_figure_sources.py \
  --figure-source-out evidence/main_figure_source_data.tsv \
  --summary-out evidence/main_figure_source_summary.tsv \
  --report-out docs/MAIN_FIGURE_SOURCE_REPORT.md

python3 scripts/render_main_figure1.py \
  --png-out figures_png/figure1_recharter_decision_object.png \
  --pdf-out figures_png/figure1_recharter_decision_object.pdf \
  --report-out docs/MAIN_FIGURE_RENDER_REPORT.md

python3 scripts/draft_figure1_text.py \
  --text-out docs/FIGURE1_CAPTION_AND_RESULTS_DRAFT.md

python3 scripts/draft_recharter_manuscript_skeleton.py \
  --out docs/RECHARTER_MANUSCRIPT_SKELETON.md

python3 scripts/draft_recharter_manuscript.py \
  --out docs/RECHARTER_MANUSCRIPT_DRAFT.md

python3 scripts/audit_recharter_manuscript_draft.py \
  --audit-out evidence/recharter_manuscript_draft_audit.tsv \
  --report-out docs/RECHARTER_MANUSCRIPT_DRAFT_AUDIT.md

python3 scripts/draft_recharter_journal_style_manuscript.py \
  --out docs/RECHARTER_JOURNAL_STYLE_DRAFT.md

python3 scripts/benchmark_claim_promotion.py

python3 scripts/audit_local_external_h5ad_candidates.py

python3 scripts/build_replogle_essential_generality_panel.py

python3 scripts/build_replogle_essential_generality_contract.py

python3 scripts/extract_external_pgaa_inputs.py \
  --contract evidence/replogle_essential_generality_contract.tsv \
  --label-column gene \
  --exact-label-matching \
  --max-control-cells 1000 \
  --control-sampling-seed pgaa-generality-controls-v1 \
  --metadata-column batch \
  --extraction-out evidence/replogle_essential_generality_extraction.tsv \
  --summary-out evidence/replogle_essential_generality_extraction_summary.tsv \
  --report-out docs/REPLOGLE_ESSENTIAL_GENERALITY_EXTRACTION.md

python3 scripts/run_replogle_essential_generality.py

python3 scripts/compile_replogle_essential_generality_results.py

python3 scripts/compare_replogle_essential_generality_baselines.py

python3 scripts/benchmark_replogle_essential_response_replication.py

python3 scripts/stress_test_replogle_essential_response_specificity.py

# Apply one locked dual-gate design to independent CRISPRa, CRISPR and drug
# perturbation platforms. Raw h5ad sources and the verbose run log stay on USB.
python3 scripts/benchmark_cross_platform_dual_gate.py

# Rebuild gate states, cross-platform synthesis and threshold sensitivity from
# existing evidence tables without rescoring the h5ad matrices.
python3 scripts/benchmark_cross_platform_dual_gate.py --compile-only

# Add or refresh one frozen platform without rescoring completed datasets.
python3 scripts/benchmark_cross_platform_dual_gate.py \
  --dataset-id nadig2024_hepg2_crispri --merge-existing

# The compile step also writes leave-one-platform-out influence results, exact
# platform-state intervals and docs/CROSS_PLATFORM_DUAL_GATE_ROBUSTNESS.md.
python3 scripts/render_cross_platform_robustness.py

# Compile the frozen ten-platform metadata contract. Raw h5ad files remain on
# /Volumes/MOVESPEED and expression values are not inspected during this step.
python3 scripts/compile_expansion_v2_contracts.py

# Score one frozen platform and merge it with completed expansion-v2 results.
python3 scripts/benchmark_expansion_v2.py \
  --dataset-id sunshine2023_calu3_crispri --merge-existing

# Rebuild the primary claim state and complete four-state landscape without
# rescoring the USB-backed matrices, then render the manuscript-facing report.
python3 scripts/benchmark_expansion_v2.py --compile-only
python3 scripts/render_expansion_v2_landscape.py

# Validate the prospective v3 endpoint, candidate queue, and model lock.
python3 scripts/validate_expansion_v3_protocol.py

# Rebuild the v2-only context model and its strict leave-one-platform-out audit.
python3 scripts/train_context_moderator_model.py

# After exactly ten v3 platforms pass metadata eligibility, lock their state
# predictions before creating any v3 expression-derived outcome table.
python3 scripts/freeze_expansion_v3_predictions.py \
  evidence/expansion_v3_eligible_context_contract.tsv

python3 scripts/audit_recharter_manuscript_draft.py \
  --draft docs/RECHARTER_JOURNAL_STYLE_DRAFT.md \
  --audit-out evidence/recharter_journal_style_draft_audit.tsv \
  --report-out docs/RECHARTER_JOURNAL_STYLE_DRAFT_AUDIT.md
```

The templates and claim-control guidance are in `evidence/` and `docs/IMMUNO_VALIDATION_RESCUE_PLAN_2026-07-16.md`. Smoke rows are examples only and are not manuscript candidates. For real manuscript analyses, omit `--allow-smoke`; the script then fails if template or smoke tokens are still present. The higher-risk method recharter and benchmark worklist are in `docs/TOP_JOURNAL_RECHARTER_2026-07-16.md` and `evidence/top_journal_benchmark_matrix_template.tsv`.

## Reproducibility Status

| Check | Expected status |
|---|---|
| `python3 -m pip install -e .` | Should pass |
| `python3 scripts/run_toy_example.py` | Should pass without external data |
| `python3 scripts/test_python_pkg.py` | Should pass (may take ~20 s) |
| `python3 -m pytest tests/test_cli.py -q` | Should pass |
| `python3 scripts/verify_dataset_manifest.py` | Should pass |
| `python3 scripts/rebuild_adamson_full_results.py` | Should pass |
| `python3 scripts/audit_event_sources.py --manifest evidence/event_source_manifest.tsv --audit-out evidence/event_source_audit.tsv --markdown-out docs/EVENT_SOURCE_AUDIT.md` | Should pass and currently report one event-ready public source plus four non-event-ready gene-level/template sources |
| `python3 scripts/compile_event_peptides.py --events evidence/event_sequence_contexts_template.tsv --candidates-out evidence/event_compiler_smoke_candidates.tsv --decoys-out evidence/event_compiler_smoke_decoys.tsv --allow-smoke` | Should pass; demonstrates event-containing peptide and matched decoy generation on a smoke row |
| `python3 scripts/build_immune_evidence_ladder.py --candidates evidence/candidate_event_peptides_template.tsv --output evidence/immune_evidence_tiers_smoke.tsv --claim-audit docs/IMMUNO_EVIDENCE_CLAIM_AUDIT_SMOKE.md --allow-smoke` | Should pass; template output is intentionally Tier D until placeholder peptide sequences are replaced |
| `python3 scripts/build_immune_evidence_ladder.py --candidates evidence/immune_evidence_smoke_candidates.tsv --ligand-evidence evidence/public_ligand_evidence_template.tsv --tcell-evidence evidence/public_tcell_evidence_template.tsv --decoys evidence/decoy_peptides_template.tsv --annotated-candidates evidence/immune_evidence_smoke_annotated.tsv --output evidence/immune_evidence_tiers_smoke.tsv --claim-audit docs/IMMUNO_EVIDENCE_CLAIM_AUDIT_SMOKE.md --allow-smoke` | Should pass; demonstrates exact, overlap, decoy evidence matching, and claim-audit generation on smoke rows |
| `python3 scripts/compare_followup_panels.py --tiers evidence/followup_panel_decision_smoke_tiers.tsv --panel-out evidence/followup_panel_smoke.tsv --summary-out evidence/followup_panel_summary_smoke.tsv --top-n 1 --allow-smoke` | Should pass; demonstrates decision-impact summaries against PGAA-rank, binding-only, and ligand-only baselines |
| `python3 scripts/check_threshold_robustness.py --tiers evidence/followup_panel_decision_smoke_tiers.tsv --adjusted-out evidence/threshold_robustness_adjusted_smoke.tsv --summary-out evidence/threshold_robustness_summary_smoke.tsv --top-n 2 --allow-smoke` | Should pass; demonstrates tier stability checks under exact-match-only and decoy-guarded rules |
| `python3 scripts/audit_recharter_readiness.py --audit-out evidence/recharter_readiness_audit.tsv --markdown-out docs/RECHARTER_READINESS_AUDIT.md` | Should pass with all nine real non-smoke evidence artifacts ready and verdict `READY_FOR_RECHARTER_MANUSCRIPT_DRAFT` |
| `python3 scripts/select_recharter_route.py --routes evidence/recharter_route_options.tsv --scored-out evidence/recharter_route_scores.tsv --report-out docs/RECHARTER_ROUTE_DECISION.md` | Should pass; currently selects the failure-preserving benchmark route as the best immediate recharter path |
| `python3 scripts/build_failure_mode_audit.py --audit-out evidence/failure_mode_audit.tsv --summary-out evidence/failure_mode_summary.tsv --report-out docs/FAILURE_MODE_AUDIT.md` | Should pass; converts current calibration and parameter-sensitivity artifacts into explicit interpretation/failure states |
| `python3 scripts/build_result_claims.py --claims-out evidence/result_claim_states.tsv --summary-out evidence/result_claim_summary.tsv --report-out docs/RESULT_CLAIM_STATE_REPORT.md` | Should pass; compiles failure states into manuscript-facing claim states and allowed claim language |
| `python3 scripts/build_claim_state_formalization.py` | Should pass; builds the finite claim-permission state space, allowed/forbidden transition contract, unit-level compiled ceilings, and a 12-invariant audit with counterfactual illegal-promotion checks |
| `python3 scripts/benchmark_claim_promotion.py` | Should pass; exhaustively evaluates 960 finite-state scenarios and reports false promotion, under-promotion, exact permission, replication false-positive rate, and replication sensitivity for the compiler and three state-ablation baselines |
| `python3 scripts/audit_local_external_h5ad_candidates.py` | Should pass when the USB is mounted; detects duplicate h5ad representations and separates same-target replication candidates from cross-target generality candidates without modifying source files |
| `python3 scripts/build_replogle_essential_generality_panel.py` | Should pass when the USB is mounted; locks 16 expression-blind targets across four target-cell abundance strata and excludes current responder-state targets |
| `python3 scripts/build_replogle_essential_generality_contract.py` | Should pass; writes a 16-target USB-backed execution contract whose allowed role is cross-target generality, not replication |
| `python3 scripts/run_replogle_essential_generality.py` | Should pass after signed input extraction; checkpoints each target, skips valid outputs, retains failures in the locked denominator, and writes per-target logs on the USB |
| `python3 scripts/compile_replogle_essential_generality_results.py` | Should pass; currently compiles 16/16 complete targets, with PGAA-W top-10% recovery for 16/16 and PGAA-H for 10/16 |
| `python3 scripts/compare_replogle_essential_generality_baselines.py` | Should pass; shows that mean-shift and Welch baselines also recover 16/16 targets in the top 10%, blocking a PGAA target-recovery superiority claim |
| `python3 scripts/validate_expansion_v3_protocol.py` | Should pass; validates the prospective stable-and-specific endpoint, ordered 10+4 expression-unseen queue, context-model specification, and SHA-256 locks |
| `python3 scripts/train_context_moderator_model.py` | Should pass; reproduces the v2-only two-axis model and its negative leave-one-platform-out result without using v3 outcomes |
| `python3 scripts/freeze_expansion_v3_predictions.py evidence/expansion_v3_eligible_context_contract.tsv` | Requires exactly ten metadata-eligible v3 platforms and must run before any v3 outcome table exists; writes state probabilities and a prediction digest |
| `python3 scripts/build_claim_panel_sources.py --panel-source-out evidence/claim_panel_source_data.tsv --summary-out evidence/claim_panel_summary.tsv --report-out docs/CLAIM_PANEL_SOURCE_REPORT.md` | Should pass; compiles claim states into figure-ready source data for decision and guardrail panels |
| `python3 scripts/build_responder_state_units.py --units-out evidence/responder_state_units.tsv --summary-out evidence/responder_state_summary.tsv --report-out docs/RESPONDER_STATE_DECISION_UNITS.md` | Should pass; aggregates decision-benchmark rows into context-level responder-state decision units |
| `python3 scripts/check_responder_state_stability.py --detail-out evidence/responder_state_stability_detail.tsv --summary-out evidence/responder_state_stability_summary.tsv --report-out docs/RESPONDER_STATE_STABILITY_REPORT.md` | Should pass; audits responder-state units with leave-one-method and same-context cross-dataset checks |
| `python3 scripts/audit_external_validation_opportunities.py --opportunities-out evidence/external_validation_opportunities.tsv --summary-out evidence/external_validation_summary.tsv --report-out docs/EXTERNAL_VALIDATION_OPPORTUNITY_AUDIT.md` | Should pass; currently reports 4 Tier 1 external replication candidates and 8 units still needing external same-context evidence |
| `python3 scripts/audit_external_dataset_candidates.py --audit-out evidence/external_dataset_candidate_audit.tsv --summary-out evidence/external_dataset_candidate_summary.tsv --report-out docs/EXTERNAL_DATASET_CANDIDATE_AUDIT.md` | Should pass; classifies public dataset candidates as metadata-check leads only, not replication evidence |
| `python3 scripts/check_external_target_coverage.py --candidate-dataset-id replogle_2022_k562_gwps --h5ad /tmp/pgaa_replogle/K562_gwps_raw_bulk_01.h5ad --source-url https://ndownloader.figshare.com/files/35774443 --coverage-out evidence/external_target_coverage_replogle_k562_gwps.tsv --summary-out evidence/external_target_coverage_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_TARGET_COVERAGE_REPLOGLE_K562_GWPS.md` | Should pass when the Replogle K562 GWPS bulk h5ad has been downloaded; verifies priority target/control metadata but still requires matching single-cell import before PGAA replication |
| `python3 scripts/plan_external_singlecell_import.py --scratch-dir /tmp/pgaa_replogle --plan-out evidence/external_singlecell_import_plan_replogle_k562_gwps.tsv --summary-out evidence/external_singlecell_import_plan_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_SINGLECELL_IMPORT_PLAN_REPLOGLE_K562_GWPS.md` | Should pass; reports whether the current scratch volume has enough safety margin for the Replogle K562 GWPS single-cell h5ad import |
| `python3 scripts/check_external_rerun_readiness.py --singlecell-h5ad /tmp/pgaa_replogle/K562_gwps_raw_singlecell_01.h5ad --readiness-out evidence/external_rerun_readiness_replogle_k562_gwps.tsv --summary-out evidence/external_rerun_readiness_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_RERUN_READINESS_REPLOGLE_K562_GWPS.md` | Should pass; reports whether a readable matching single-cell h5ad is present and whether target/control metadata are sufficient for the external PGAA/comparator rerun; this is readiness, not replication evidence |
| `python3 scripts/build_external_claim_state_contract.py --readiness evidence/external_rerun_readiness_replogle_k562_gwps.tsv --output-dir external_rerun/replogle_k562_gwps --contract-out evidence/external_claim_state_contract_replogle_k562_gwps.tsv --summary-out evidence/external_claim_state_contract_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_CLAIM_STATE_CONTRACT_REPLOGLE_K562_GWPS.md` | Should pass; builds the per-target external PGAA execution contract and remains blocked until the readiness gate reaches `ready_for_external_claim_state_rerun` |
| `python3 scripts/extract_external_pgaa_inputs.py --contract evidence/external_claim_state_contract_replogle_k562_gwps.tsv --extraction-out evidence/external_pgaa_input_extraction_replogle_k562_gwps.tsv --summary-out evidence/external_pgaa_input_extraction_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_PGAA_INPUT_EXTRACTION_REPLOGLE_K562_GWPS.md` | Should pass; extracts PGAA CLI expression/metadata CSVs only after the contract is ready, and otherwise records blocked input-extraction status |
| `python3 scripts/build_external_pgaa_execution_manifest.py --contract evidence/external_claim_state_contract_replogle_k562_gwps.tsv --extraction evidence/external_pgaa_input_extraction_replogle_k562_gwps.tsv --manifest-out evidence/external_pgaa_execution_manifest_replogle_k562_gwps.tsv --summary-out evidence/external_pgaa_execution_manifest_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_PGAA_EXECUTION_MANIFEST_REPLOGLE_K562_GWPS.md` | Should pass; audits whether external PGAA input files, PGAA-W/PGAA-H outputs, and claim-state outputs exist without treating execution readiness as replication evidence |
| `python3 scripts/compile_external_claim_states.py --manifest evidence/external_pgaa_execution_manifest_replogle_k562_gwps.tsv --internal-units evidence/responder_state_units.tsv --claim-states-out evidence/external_claim_states_replogle_k562_gwps.tsv --summary-out evidence/external_claim_states_replogle_k562_gwps_summary.tsv --report-out docs/EXTERNAL_CLAIM_STATE_COMPILER_REPLOGLE_K562_GWPS.md` | Should pass; compiles external PGAA-W/PGAA-H outputs into target-level claim states and aligns them to internal responder-state units while preserving non-wet-lab claim boundaries |
| `python3 scripts/integrate_external_responder_state_stability.py --internal-stability evidence/responder_state_stability_summary.tsv --external-claim-states evidence/external_claim_states_replogle_k562_gwps.tsv --integrated-out evidence/external_responder_state_stability_integrated.tsv --summary-out evidence/external_responder_state_stability_summary.tsv --report-out docs/EXTERNAL_RESPONDER_STATE_STABILITY_INTEGRATION.md` | Should pass; integrates external claim states with internal responder-state stability to update cross-dataset status and claim ceilings without allowing unsupported wet-lab or immune-validation language |
| `python3 scripts/build_main_figure_sources.py --figure-source-out evidence/main_figure_source_data.tsv --summary-out evidence/main_figure_source_summary.tsv --report-out docs/MAIN_FIGURE_SOURCE_REPORT.md` | Should pass; compiles claim, responder-state, and stability artifacts into Figure 1 source data |
| `python3 scripts/render_main_figure1.py --png-out figures_png/figure1_recharter_decision_object.png --pdf-out figures_png/figure1_recharter_decision_object.pdf --report-out docs/MAIN_FIGURE_RENDER_REPORT.md` | Should pass; renders the source-driven Figure 1 PNG/PDF draft while keeping same-context replication limitations visible |
| `python3 scripts/draft_figure1_text.py --text-out docs/FIGURE1_CAPTION_AND_RESULTS_DRAFT.md` | Should pass; drafts claim-bounded Figure 1 caption and Results text from the same source-data table |
| `python3 scripts/draft_recharter_manuscript_skeleton.py --out docs/RECHARTER_MANUSCRIPT_SKELETON.md` | Should pass; drafts the claim-bounded manuscript skeleton and reviewer-risk map from route, benchmark, figure, and readiness evidence |
| `python3 scripts/draft_recharter_manuscript.py --out docs/RECHARTER_MANUSCRIPT_DRAFT.md` | Should pass; drafts claim-bounded manuscript sections from claim-state, responder-unit, stability, route, and readiness evidence |
| `python3 scripts/audit_recharter_manuscript_draft.py --audit-out evidence/recharter_manuscript_draft_audit.tsv --report-out docs/RECHARTER_MANUSCRIPT_DRAFT_AUDIT.md` | Should pass; the verdict depends on the selected draft, while the journal-style draft currently reaches `CLAIM_SAFE_READY_FOR_STYLE_REVISION` |
| `python3 scripts/draft_recharter_journal_style_manuscript.py --out docs/RECHARTER_JOURNAL_STYLE_DRAFT.md` | Should pass; drafts a journal-style version of the claim-bounded manuscript while retaining blocked-evidence disclosure |
| `python3 scripts/audit_recharter_manuscript_draft.py --draft docs/RECHARTER_JOURNAL_STYLE_DRAFT.md --audit-out evidence/recharter_journal_style_draft_audit.tsv --report-out docs/RECHARTER_JOURNAL_STYLE_DRAFT_AUDIT.md` | Should pass; currently reports `CLAIM_SAFE_READY_FOR_STYLE_REVISION` for the journal-style draft |
| `python3 scripts/check_top_journal_benchmark_matrix.py --matrix evidence/top_journal_benchmark_matrix_template.tsv` | Should pass; checks that the recharter benchmark worklist remains actionable |
| `python3 scripts/benchmark_norman_multi_perturbation.py` | Requires `NORMAN2019_H5AD`; writes the Norman summary, gene-score, panel-audit, metadata, and PGAA-W adjustment-ablation CSV files |
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

The CLI writes two gene tables:

- `<prefix>.s1.csv`: PGAA-W (Wasserstein) output with `gene`, `W_observed`, `W_std_observed`, `W_null_mean`, `W_null_std`, `z_score`, and `p_value_perm`
- `<prefix>.s2.csv`: PGAA-H (histogram-shape) output with `gene`, `S2`, and `n_peaks_on`

The lightweight CLI computes permutation p-values for PGAA-W only. It reports PGAA-H histogram-shape scores without PGAA-H permutation calibration, ranks, or Storey upper-tail diagnostics. The calibrated PGAA-H analyses reported in the manuscript are reproduced by the dedicated benchmark scripts and source-data tables. Supplementary Table 7 and the supplement CLI schema provide full input/output documentation.

## Troubleshooting

- **`pgaa-run: command not found`**: ensure the pip install location is on PATH, or use `python3 -m pgaa.cli` instead.
- **`ImportError: No module named 'pgaa'`**: run `pip install -e .` from the repository root.
- **`ValueError: Input contains NaN values`**: check that the expression matrix has been normalized (10,000 counts per cell, log1p) before calling PGAA.
- **R tests**: `test_r_pkg.R` requires R ≥ 4.0 and `Rscript` on PATH. Skip if R is not available.
- **Norman multi-perturbation full rerun**: this script requires the processed Norman 2019 h5ad input. Set `NORMAN2019_H5AD=/path/to/norman2019_full_log.h5ad` before running. See Supplementary Table 7.

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

Use `CITATION.cff` for software citation metadata. The public code-only repository is available at https://github.com/xutaoguo55/pgaa, the archived software release is available at https://doi.org/10.5281/zenodo.22720271.
