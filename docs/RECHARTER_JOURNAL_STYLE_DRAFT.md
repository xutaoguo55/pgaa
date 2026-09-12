# PGAA Recharter Journal-Style Draft

## Draft Status

This journal-style draft is generated from the current evidence chain and is not yet a submission-ready manuscript. The real-event readiness audit passes, so the draft includes a bounded public domain-transfer event-peptide benchmark; wet-lab presentation, synthetic-peptide, and T-cell validation claims remain blocked. Recommended route: `stable_resistance_state_bifurcation`; the claim-state compiler stays as the governance layer, not the mainline biological route.

## Title

Stable resistance-state bifurcation: claim-state control in single-cell perturbation analysis

## Abstract Draft

Single-cell perturbation analyses produce heterogeneous evidence, but standard benchmarking usually compresses that evidence into ranks or aggregate performance scores. This creates evidentiary inflation when descriptive shifts, restricted results, calibration failures, and method-sensitive findings are reported as if they licensed the same claim. Claim-state compilation controls evidentiary inflation by acting as a claim-controlled benchmark compiler rather than a score-only ranker. We reframe PGAA as a claim-state compiler that maps perturbation evidence to typed interpretation states and explicit claim ceilings. The current implementation converts 53 benchmark and guardrail rows into explicit claim states: 10 comparative-support, 11 descriptive-only, 4 restricted-use, 3 calibration-support, and 25 failure-or-guardrail rows. These rows define 8 context-level responder-state units, of which 5 are supported and 3 are provisional under the present evidence. Leave-one-method analysis identifies 4 stable units and 4 method-sensitive or PGAA-dependent units, thereby testing stability of the allowed interpretation rather than score stability alone. External Replogle K562 GWPS integration identifies 4 bounded computational same-context concordant units, with 4 external-blocked, 0 discordant, and 0 unresolved units. An executable formal audit tested 12 compiler invariants; 12 passed with 0 observed violations, including counterfactual checks against illegal claim promotion. Across 960 exhaustive finite-state scenarios, the compiler had a 0.0% contract-defined false-promotion rate, compared with 70.4% for a state-blind frozen-output baseline and 19.2% for an external-only gate. A locked 16-target Replogle essential-gene panel completed 16/16 runs; PGAA-W and PGAA-H placed the perturbed target in the top decile for 16/16 and 10/16 targets, respectively. Simple mean-shift and Welch baselines also reached 16/16 and 16/16, preventing a target-recovery superiority claim. In a held-out-batch non-target response benchmark, PGAA-W showed 82.0% top-100 overlap versus 72.5% for mean shift, but matched control-versus-control overlap was 81.0%; its 1.5% specificity margin was not significant after Holm correction (p=0.140). PGAA-H had only 3.0% absolute overlap despite a 1.5% specificity margin (Holm p=0.00932). Across 5 independent perturbation datasets, the same dual-gate design identified recurrent stability-specificity decoupling for `pgaa_w`; the tested stability-floor limit of recurrence was `pgaa_w` through 0.25, and no method survived every leave-one-platform-out deletion. The resulting method object preserves support, restrictions, failures, typed replication states, and claim ceilings in one auditable representation. The contribution is not a new biological claim, but computational control over how evidence is translated into one.

## Introduction Draft

Perturbation-response methods are usually evaluated by whether they recover known targets or rank plausible genes highly. That convention is useful for benchmarking, but it does not solve a more basic reporting problem: methods produce outputs with different evidentiary meanings. Some rows support a bounded comparison, some describe a pattern without a decisive comparator, some expose a calibration limit, and some should be treated as failures for primary interpretation. Collapsing these states into a single ranking makes a method look cleaner than it is and makes manuscript claims difficult to audit.

The rechartered PGAA analysis treats this translation problem as the method object. PGAA's distribution-aware scores enter a compiler that assigns each benchmark row to an allowed claim state, aggregates compatible rows into responder-state decision units, and types their replication status as concordant, discordant, unresolved, or blocked. The benchmark question therefore changes from whether one statistic wins to whether every result carries a defensible, stable, and auditable claim.

## Results Draft

### A claim-state compiler turns heterogeneous evidence into typed manuscript decisions

We treated every benchmark and guardrail row as a typed evidence object with a source metric, an admissible interpretation, and an explicit claim ceiling. Compilation produced 10 comparative-support rows, 11 descriptive-only rows, 3 calibration-support rows, 4 restricted-use rows, and 25 failure-or-guardrail rows. Rather than maximizing the apparent positive fraction, the compiler preserves restricted and failed rows as first-class outputs. Because the claim ceiling travels with the originating evidence row into figures and prose, a descriptive shift cannot silently become comparative support and a computationally concordant state cannot silently become biological validation. This evidence-to-claim translation, rather than rank production alone, defines the rechartered method.

Evidence source: `evidence/result_claim_states.tsv`.

Claim boundary: descriptive, restricted, calibration, and failure-or-guardrail rows cannot support a broad method-superiority claim.

### Executable invariants make evidence-to-claim translation falsifiable

We represented the compiler as a finite permission system linking row-level claim states, responder decisions, omission stability, and typed external evidence. The audit evaluated 12 invariants and recorded 12 passes with 0 violations. Tested conditions included deterministic action-to-state mapping, preservation of failure rows during aggregation, witness requirements for supported and provisional units, stability-label consistency, external-concordance preconditions, and rejection of five counterfactual illegal promotions. The compiler can therefore fail explicitly when evidence and permission diverge.

Evidence source: `evidence/claim_state_invariant_audit.tsv`, `evidence/claim_transition_rules.tsv`, and `docs/CLAIM_STATE_COMPILER_FORMALIZATION.md`.

Claim boundary: passing software invariants establishes internal contract consistency, not empirical correctness or biological validation.

### Exhaustive state mutation quantifies unsupported claim promotion

We exhaustively enumerated 960 decision-by-stability-by-external-state scenarios over the observed units and compared four reporting strategies against the predeclared permission contract. The claim-state compiler produced a 0.0% false-promotion rate. A state-blind frozen-output baseline produced 70.4% false promotions, whereas an external-only baseline that ignored internal support and stability produced 19.2%. A decision-only baseline avoided false promotion but had 0.0% replication sensitivity, showing that indiscriminate claim suppression is not equivalent to faithful permission compilation.

Evidence source: `evidence/claim_promotion_benchmark_summary.tsv` and `docs/CLAIM_PROMOTION_ERROR_BENCHMARK.md`.

Claim boundary: the oracle is the declared compiler contract. This stress test verifies contract fidelity under evidence-state mutation; it is not independent biological ground truth or evidence that the contract is empirically optimal.

### A locked cross-target panel separates execution generality from superiority

We selected 16 targets from 1,164 eligible perturbations using expression-blind cell-count strata and retained every locked target in the denominator. All 16/16 runs completed. PGAA-W placed the perturbed gene in the top decile for 16/16 targets and PGAA-H did so for 10/16. However, post-pilot absolute mean-shift and Welch baselines reached the same threshold for 16/16 and 16/16 targets. The panel therefore supports cross-target execution generality and transparent failure accounting, but direct target recovery does not distinguish PGAA from simple conventional summaries.

Evidence source: `evidence/replogle_essential_generality_results.tsv` and `evidence/replogle_essential_generality_baseline_comparison.tsv`.

Claim boundary: this is one K562 experiment, not independent biological replication, and the exploratory baselines do not support method superiority.

### A pseudo-perturbation gate separates reproducibility from response specificity

We next excluded each directly perturbed gene and compared discovery-versus-validation top-100 response rankings across a locked 24/24 batch split. PGAA-W initially appeared strongest, with median overlap 0.820, compared with 0.725 for absolute mean shift; PGAA-H overlap was 0.030. This apparent PGAA-W advantage did not survive a matched control-versus-control stress test. Across five deterministic equal-size repeats, the PGAA-W pseudo overlap was 0.810, leaving a median specificity margin of 0.015 (Holm p=0.1399). The high Wasserstein overlap therefore largely reflects reproducible gene-wise distributional properties rather than demonstrated perturbation-specific response. PGAA-H showed a statistically positive but small margin (0.015; Holm p=0.009317) against a low absolute overlap of 0.030, which is insufficient for a useful stability claim. Under the resulting stability-specificity dual gate, absolute mean shift was the only method to pass both gates; PGAA-W was stable but not response-specific, whereas PGAA-H and Welch were specificity-positive but insufficiently stable.

Evidence source: `evidence/replogle_essential_response_replication.tsv` and `evidence/replogle_essential_response_specificity_summary.tsv`; compiled decision states: `evidence/response_stability_specificity_dual_gate.tsv`.

Claim boundary: this post-result stress test is within one experiment. It rejects a PGAA-W response-specific superiority interpretation and does not establish biological correctness.

### The dual gate exposes recurrent cross-platform decoupling

We applied one result-blind contract to independent CRISPRi, CRISPRa, conventional CRISPR and multiplexed drug perturbation datasets. Perturbation units were selected by available cell count, while equal group size, five deterministic repeats, top-100 ranking, pseudo-target controls and Holm correction were shared. At the nominal 0.20 stability floor, the observed states were: datlinger2017_jurkat_crispr: absolute_mean_shift=neither_stable_nor_specific, pgaa_h=neither_stable_nor_specific, pgaa_w=neither_stable_nor_specific, welch_abs_t=neither_stable_nor_specific; nadig2024_hepg2_crispri: absolute_mean_shift=stable_and_specific, pgaa_h=neither_stable_nor_specific, pgaa_w=stable_and_specific, welch_abs_t=specific_but_not_stable; norman2019_k562_crispra: absolute_mean_shift=stable_and_specific, pgaa_h=neither_stable_nor_specific, pgaa_w=stable_and_specific, welch_abs_t=stable_and_specific; replogle2022_k562_crispri: absolute_mean_shift=stable_and_specific, pgaa_h=specific_but_not_stable, pgaa_w=stable_but_not_specific, welch_abs_t=specific_but_not_stable; sciplex3_a549_drug: absolute_mean_shift=stable_but_not_specific, pgaa_h=stable_but_not_specific, pgaa_w=stable_but_not_specific, welch_abs_t=neither_stable_nor_specific. Recurrent stable-but-not-specific behavior occurred for `pgaa_w`. Across stability floors 0.10-0.30, methods retaining that recurrence at every threshold were none.

No method retained recurrence after every platform deletion. Accordingly, the nominal recurrence is treated as platform-sensitive rather than platform-robust.

Evidence source: `evidence/cross_platform_dual_gate_states.tsv`, `evidence/cross_platform_dual_gate_synthesis.tsv` and `evidence/cross_platform_dual_gate_threshold_sensitivity.tsv`; deletion and interval audit: `evidence/cross_platform_dual_gate_leave_one_out.tsv` and `evidence/cross_platform_dual_gate_platform_uncertainty.tsv`.

Claim boundary: this is a cross-platform empirical recurrence in the sampled systems, not proof of a universal law. The stability floor was not preregistered, platform splits differ in strength, and specificity here is statistical rather than biological validation.

### Responder-state units turn row-level scores into decision objects

Decision-benchmark rows are then collapsed by biological or perturbation context into 8 responder-state units. Supported units occur in BHLHE40_pDS258, CREB1_pDS269, DDIT3_pDS263, SPI1_pDS255, ZNF326_pDS262; provisional units occur in CEBPA, CEBPE, KLF1. Primary metric values span 0.644 to 0.833. This aggregation makes the manuscript unit match the decision unit: a context can be supported, provisional, or restricted depending on how many methods support it and how much failure evidence travels with it.

Evidence source: `evidence/responder_state_units.tsv`.

Claim boundary: provisional units are responder-state hypotheses, not replicated responder states.

### Stability gates identify which units depend on method choice

We next asked whether each responder-state unit survives leave-one-method omission. Stable units occur in BHLHE40_pDS258, CREB1_pDS269, DDIT3_pDS263, ZNF326_pDS262; method-sensitive or PGAA-dependent units occur in CEBPA, CEBPE, KLF1, SPI1_pDS255. The integrated external layer records 4 external_same_context_concordant units and keeps the remaining 4 external_same_context_blocked units internal-only. This allows bounded computational replication language for concordant rows without converting them into biological validation.

Evidence source: `evidence/responder_state_stability_summary.tsv` and `evidence/external_responder_state_stability_summary.tsv`.

Claim boundary: external_same_context_concordant rows support only bounded computational same-context replication; external_same_context_blocked rows remain internal-only.

### A source-driven figure makes the claim-control object inspectable

The main figure is built from a 27-row source table that combines claim-state counts, responder-state units, internal stability, and typed external states. It functions as an executable decision object rather than a workflow schematic: each visual mark traces to a generated evidence row, and each row carries the interpretive ceiling used by the manuscript.

Evidence source: `evidence/main_figure_source_data.tsv` and `figures_png/figure1_recharter_decision_object.png`.

Claim boundary: Figure 1 is a benchmark and claim-control figure, not evidence of wet-lab validation or immune presentation.

### Public real-event evidence activates a bounded domain-transfer benchmark

The event-peptide extension now contains real altered-sequence contexts, candidate peptides, public ligand and T-cell evidence, matched decoys, tier assignments, panel comparisons, and threshold-robustness outputs. These artifacts establish an auditable public-data domain-transfer benchmark, not a direct link between PGAA-ranked perturbation outputs and antigen evidence. Candidates separate from composition-shuffled and cross-event controls but not from same-context non-event windows. This mixed decoy sensitivity blocks a global enrichment claim and is retained as a central limitation. A same-cell GSE112274 pilot now connects EGFR T790M allele fraction with expression. PGAA-W detects an EGFR distributional association (2,000-permutation p=0.0005), whereas PGAA-H does not rank EGFR among its leading scores. This observational result is neither causal replication nor evidence of antigen presentation or T-cell recognition. An independent GSE129221 clone-level stress test does not reproduce a directionally invariant association: EGFR is lower in T790M-high CORTAD-seq cells but 1.31-fold higher in T790M-positive PC9GR replicates, with exact Wasserstein p=0.10. The compiler therefore retains this as a failed or unresolved cross-system state. A GSE75602 evolutionary stress test shows that early GR2 and late GR3 T790M-positive states both exceed parental EGFR expression, whereas late GR3 falls below the drug-tolerant precursor and early GR2. With two replicates per state and a minimum one-sided exact p=0.167, this supports comparator- and path-dependent modulation but does not rescue cross-system replication. A locked shift from the single marker to a distributed state program yields a positive external result: the GSE75602-derived 50-gene down-regulated resistance module transfers to GSE129221 with exact p=0.05 and 62% gene-direction concordance, with the same direction across all prespecified 10- to 200-gene modules. The up-regulated route is not size-robust, and source-group-adjusted CORTAD-seq transfer fails; the positive result is therefore a resistance-state program, not a T790M-specific mechanism.

Evidence source: `docs/RECHARTER_READINESS_AUDIT.md`, `docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md`, and `evidence/threshold_robustness_summary.tsv`.

Claim boundary: do not claim event-peptide presentation, synthetic-peptide wet-lab confirmation, or T-cell function.

## Discussion Draft

The rechartered method addresses a general failure mode in computational biology: evidence types are often heterogeneous when generated but homogeneous when narrated. By compiling scores, restrictions, failures, stability results, and external states into typed claim objects, PGAA makes evidentiary inflation measurable and testable. This shifts the contribution from another perturbation score to a computational governance layer for evidence-to-claim translation.

The limitation is also explicit. The new external layer reduces the earlier externality gap, but it does not remove the claim ceiling. Replogle K562 GWPS provides concordant same-context computational claim states for the stable supported Adamson units, while blocked rows remain visible rather than silently promoted. The strongest local PC9 drug-perturbation candidates still do not close the third-system gap: Aissa2021 is blocked by a single-batch metadata contract error, and Chang2021 is below the minimum selected-unit gate. The transferable down module is biologically coherent rather than purely statistical: its annotated members and pathway enrichment concentrate on iron handling and transport, carbonic-anhydrase and pH-adaptation genes, and epithelial stress or differentiation markers. CP, SLC40A1, HFE, TFRC, and STEAP4 anchor the iron-homeostasis theme; CA9, CA12, and CA2 anchor the carbonic-anhydrase theme; and RARRES1, STC1, PSCA, HOPX, ELF5, MUC6, and KRT4/KRT13 support a broader epithelial stress-state interpretation. That keeps the result framed as a transferable resistance-state program with iron/pH/differentiation features rather than a T790M-specific mechanism. The locked generality panel further shows that strong direct target recovery is shared by simple baselines, so it cannot be used as a PGAA superiority argument. The held-out response analysis adds a more general warning: reproducible rankings can arise from stable null distributional properties unless a matched pseudo-perturbation gate is applied. A real public event source now activates the peptide-evidence compiler as a bounded domain-transfer benchmark. Matched event-expression data are now connected in one observational pilot; an independent clone-level stress test is directionally discordant, and the stage-resolved evolution series indicates comparator-dependent modulation rather than a fixed T790M effect. A distributed down-regulated resistance-state module does transfer across the two clone-level systems, establishing a bounded positive result while T790M-specific replication and new wet-lab validation remain absent. The next decisive upgrade is a third independent PC9 evolution system tested with the module frozen.

## Methods Draft

Failure-mode and claim-state compilation. Calibration, parameter-sensitivity, Norman, and Adamson benchmark outputs were first converted into failure-mode states and then into manuscript-facing claim states. Each row retains its source, metric, allowed interpretation, and figure-panel assignment.

Responder-state aggregation. Decision-benchmark rows were grouped by context. For each context, the compiler records the primary method, primary metric, supporting methods, descriptive methods, failure/guardrail methods, and allowed manuscript use.

External responder-state integration. Replogle K562 GWPS PGAA-W and PGAA-H outputs were compiled into target-level external claim states and joined to the internal responder-state stability table. Concordant rows were assigned external_same_context_concordant and a bounded computational replication ceiling; missing or unexecuted external claim states remained external_same_context_blocked.

Formal permission system. The compiler defines finite vocabularies for row claims, responder decisions, stability states, and external states. A unit receives bounded computational same-context replication permission if and only if it is internally supported, leave-one-method stable, and externally concordant. Blocked, unresolved, discordant, provisional, and unstable inputs cannot emit replication permission, and no computational state can emit biological-validation permission. These constraints are evaluated as executable invariants and counterfactual transition tests.

Claim-promotion stress test. For each observed decision unit, we enumerated the complete finite product of six decision states, four stability states, and five external states. False promotion was defined as a predicted permission rank above the predeclared contract ceiling; under-promotion was the converse. We also measured exact permission agreement, replication false-positive rate among ineligible states, and replication sensitivity among eligible states. The state-blind comparator freezes the observed permission as a favorable proxy for reporting that does not update after evidence changes; it is not presented as a universal raw-score threshold.

Cross-target generality audit. Targets were selected from metadata alone using four target-cell abundance strata and deterministic hashing. All target cells, a shared deterministic 1,000-control subsample, and all measured genes entered PGAA-W and PGAA-H. The locked denominator included failures. Primary recovery endpoints were target permutation p values and target rank percentiles; absolute mean shift and absolute Welch statistics were explicitly post-pilot exploratory baselines.

Held-out response stability and specificity. Source batches 1-48 were deterministically divided into 24 discovery and 24 validation batches. The perturbed target gene was excluded, and top-100 overlap, Jaccard index, all-gene Spearman correlation, and hypergeometric overlap were computed for PGAA-W, PGAA-H, absolute mean shift, and absolute Welch t. A post-result specificity stress test then repeated each comparison five times with equal-size pseudo-target and matched-control groups drawn only from controls. Repeat-level results were aggregated within target before one-sided Wilcoxon testing and Holm correction.

Cross-platform dual-gate benchmark. Dataset-specific adapters defined perturbation, control and replicate metadata only. The statistical contract then selected up to 16 count-ranked units per dataset, capped equal groups at 70 cells, excluded direct targets for gene perturbations, evaluated 5,000 features, and compared observed with pseudo-target top-100 overlap across five deterministic repeats. Target-level median specificity margins were tested by one-sided Wilcoxon tests with within-dataset Holm correction. Stability floors from 0.10 to 0.30 were reported because 0.20 was a post-result decision threshold.

Figure, text, and claim audit. Figure 1, this draft, and the claim-safety report are generated from source tables and readiness audits. The manuscript audit scans required evidence references, blocked-evidence disclosure, boundary language, and unsupported phrases before style revision.

## Current Worklist State

The framing spine is tracked in `evidence/novelty_upgrade_map.tsv` (120 upgrade points; 70 tier-1 thesis points).

Benchmark matrix rows: 35.

| Status | Rows |
|---|---:|
| complete | 35 |

## Still-Blocked Evidence

| Missing item | Artifact | Detail |
|---|---|---|
| v3_external_source_availability | `evidence/expansion_v3_ready_panel_execution_plan.tsv` | 14/14 frozen v3 sources are unavailable; prospective cross-platform scoring remains unexecuted |

## Forbidden Phrases For This Draft

- validated antigen
- immunogenic peptide validated by T cells
- same-context replicated responder state
- experimentally confirmed presentation
- synthetic peptide validation
- validated T-cell function
