# Bioinformatics Submission Position

## Target

Article type: Original Paper.

Lead pitch: PGAA is a claim-state compiler for perturbation transcriptomics. It transforms score, stability, external replication, source provenance, and promotion gates into auditable claim states so manuscript claims stay bounded without discarding positive biological hypotheses.

## What Makes It A Bioinformatics Paper

- bioinfo_01_problem_reframing: Reframe the method as a claim-state compiler that controls unsupported promotion from scores to biological claims.
- bioinfo_02_claim_promotion_metric: Promote false-promotion rate, exact-permission rate, under-promotion rate, and replication false-positive rate as formal reporting metrics.
- bioinfo_03_empirical_anchor: Separate contract-stress tests from empirical anchors: Norman, Adamson, Replogle, and EGFR-resistance branch-vulnerability examples.
- bioinfo_04_comparator_fairness: Make comparator fairness explicit: conventional recovery metrics are reported, but the primary endpoint is claim-state correctness.
- bioinfo_05_ablation_stack: Add ablations removing stability, external evidence, source provenance, and branch-vulnerability promotion gates.
- bioinfo_06_branch_vulnerability_use_case: Use ATM as a bounded demonstration of branch-specific vulnerability hypothesis compilation, not as a validated drug claim.
- bioinfo_07_software_contract: Expose one-command scripts, CLI smoke tests, source-data manifest, and full pytest status as the software contract.
- bioinfo_08_manuscript_figure_order: Reorder figures around method logic: compiler, claim-promotion benchmark, empirical anchors, branch-vulnerability case, reproducibility package.
- bioinfo_09_target_specificity_scorecard: Render the GSE193258 target-specificity audit as a dedicated lead-target scorecard figure and carry it as a support figure in the submission package.

## Comparator Contract

- PGAA_claim_state_compiler: claim-promotion correctness and bounded biological-use-case support
- state_blind_frozen_reporting: false-promotion rate under evidence-gate mutation
- decision_only_reporting: under-promotion and replication sensitivity
- external_only_reporting: replication false-positive rate
- SCEPTRE_or_CPT: known-target recovery or ranking concordance
- Welch_or_mean_shift: known-target recovery, rank overlap, and claim-state after compiler wrapping

## Ablation Logic

- remove_stability_gate: unstable internal units can be promoted as reproducible
- remove_external_gate: same-context replication claims cannot be distinguished from internal-only support
- remove_source_gate: figure-level or missing-source evidence can be promoted beyond traceable numerical support
- remove_branch_promotion_gate: ATM and HDAC can be promoted to the same claim level despite unequal evidence
- score_only_reporting: ranked outputs become manuscript claims without evidence-state permissions

## Figure Spine

- Figure 1: PGAA as a claim-state compiler
- Figure 2: False-promotion benchmark and ablation stack
- Figure 3: Empirical perturbation transcriptomics anchors
- Figure 4: EGFR-resistance branch-vulnerability demonstration
- Figure 5: Reproducibility and source-data audit
- Supplementary Figure S4: GSE193258 target-class specificity scorecard
- Supplementary Figure S5: GSE335846 dynamic corroboration scorecard
- Supplementary Figure S6: GSE150949 PC9 evolution scorecard
- Supplementary Figure S7: GSE335846 phosphoproteomics corroboration scorecard

## Current Submission Package

- `docs/SUBMISSION_PACKAGE_INDEX.md`
- `docs/AUTHOR_DATA_REQUEST_GSE335846.md`
- `docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md`
- `docs/PUBLICATION_GAP_AUDIT.md`
- `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md`
- `figures_png/gse193258_target_specificity_map.png`
- `docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md`
- `figures_png/gse335846_dynamic_corroboration_scorecard.png`
- `docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md`
- `figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png`
- `figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf`
- `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md`
- `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md`
- `evidence/gse335846_phosphoproteomics_corroboration.tsv`
- `evidence/gse335846_phosphoproteomics_selected_markers.tsv`
- `evidence/gse335846_phosphoproteomics_boundary_scan.tsv`
- `figures_png/gse150949_pc9_evolution_scorecard.png`
- `docs/GSE150949_PC9_EVOLUTION_AUDIT.md`
- `docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md`

## Claim Ceiling

Do claim: PGAA compiles auditable claim states and produces a bounded branch-vulnerability demonstration.

Do not claim: ATM pharmacology is definitively validated, source-level dynamic response tables have been recovered, or the manuscript is ready for direct submission.
