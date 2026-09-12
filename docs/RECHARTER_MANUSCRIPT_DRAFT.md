# PGAA Recharter Manuscript Draft

## Draft Status

This is a claim-bounded working draft generated from current evidence tables. It is not yet a submission-ready manuscript. The real-event readiness gate passes, enabling bounded public domain-transfer analysis while wet-lab presentation and T-cell validation claims remain blocked.

Recommended route: `stable_resistance_state_bifurcation` (Stable resistance-state bifurcation). The claim-state compiler remains the governance layer, but the mainline route is the stable resistance-state bifurcation program.

## Title

Stable resistance-state bifurcation: claim-controlled single-cell perturbation response analysis

## Abstract Draft

Single-cell perturbation methods often report ranked genes or scores without preserving the evidentiary state of each result. This creates a practical problem for method comparison: positive, descriptive, unstable, and failed outcomes can be mixed into the same narrative. We recharter PGAA around the `stable_resistance_state_bifurcation` route (Stable resistance-state bifurcation), while using a failure-preserving benchmark engine to compile perturbation-response outputs into claim states, responder-state units, and stability gates. In the current evidence package, 53 benchmark and guardrail rows are compiled into 10 comparative-support rows, 11 descriptive-only rows, 4 restricted-use rows, 3 calibration-support rows, and 25 failure-or-guardrail rows. Decision-benchmark rows further define 8 responder-state units, including 5 supported and 3 provisional units. Leave-one-method checks identify 4 stable units and 4 method-sensitive or PGAA-dependent units. An external Replogle K562 GWPS claim-state layer adds 4 bounded computational same-context concordant units, while 4 units remain external blocked, 0 discordant, and 0 unresolved. The resulting object turns failure handling and claim control into primary method outputs rather than after-the-fact caveats.

## Introduction Draft

Distribution-aware perturbation analysis is useful only when the reported result can be interpreted at the same level of rigor as the downstream claim. A ranked response score may be adequate for exploratory prioritization, but it is not sufficient for deciding whether a result supports a comparative claim, a descriptive observation, a parameter guardrail, or a failure mode. This gap is especially visible in heterogeneous single-cell perturbation settings, where different statistics can emphasize different response features and where calibration or parameter sensitivity can change the allowed interpretation.

The current recharter therefore changes the method object. Instead of asking only which genes rank highly, PGAA is framed as a compiler from benchmark evidence into explicit claim states and responder-state units. This framing does not hide negative or unstable outcomes. It makes them part of the output and uses them to constrain manuscript language.

## Results Draft

### PGAA benchmark evidence can be compiled into explicit claim states

We first converted benchmark and guardrail rows into manuscript-facing claim states. The compiled evidence contains 10 comparative-support rows, 11 descriptive-only rows, 3 calibration-support rows, 4 restricted-use rows, and 25 failure-or-guardrail rows. This distribution is important because it prevents the manuscript from treating every numerical output as equally claim-bearing. Rows assigned to failure or restricted states remain visible and are used to define the ceiling of allowed interpretation.

Evidence source: `evidence/result_claim_states.tsv`.

Claim boundary: no broad superiority claim should be made from descriptive, restricted, or failure-or-guardrail rows.

### Decision rows define responder-state units rather than isolated method scores

Decision-benchmark rows were aggregated into context-level responder-state units. The current table contains 8 units. Supported units occur in BHLHE40_pDS258, CREB1_pDS269, DDIT3_pDS263, SPI1_pDS255, ZNF326_pDS262; provisional units occur in CEBPA, CEBPE, KLF1. Across units, primary metric values range from 0.644 to 0.833. The supported units can carry bounded comparative interpretation, whereas the provisional units should be reported as descriptive responder-state hypotheses rather than as validated discoveries.

Evidence source: `evidence/responder_state_units.tsv`.

Claim boundary: provisional Norman units remain hypothesis-generating and should not be described as replicated responder states.

### Stability gates separate robust units from method-sensitive units

We next evaluated whether the responder-state labels survive leave-one-method omission. Four units remain leave-one-method stable (BHLHE40_pDS258, CREB1_pDS269, DDIT3_pDS263, ZNF326_pDS262), whereas method-sensitive or PGAA-dependent units occur in CEBPA, CEBPE, KLF1, SPI1_pDS255. These gates make dependency visible: a result can be useful as a benchmark finding while still being too method-sensitive for strong biological interpretation.

Evidence source: `evidence/responder_state_stability_summary.tsv` and `evidence/external_responder_state_stability_summary.tsv`.

Claim boundary: external same-context evidence supports only bounded computational replication for 4 concordant units; 4 blocked units remain internal-only, and no row supports wet-lab, immune-presentation, synthetic-peptide, or T-cell-function claims.

### Figure 1 exposes the claim-control object rather than decorating the workflow

Figure 1 is rendered from a 27-row source table rather than assembled as a manual schematic. The figure displays claim-state distribution, responder-state units, and the stability/replication gate in a single object. This design makes the method claim auditable: the figure shows both where PGAA supports bounded interpretation and where evidence remains provisional, sensitive, or missing.

Evidence source: `evidence/main_figure_source_data.tsv` and `figures_png/figure1_recharter_decision_object.png`.

Claim boundary: Figure 1 is not evidence of wet-lab validation or immune presentation.

### Public real-event evidence enables a bounded domain-transfer analysis

The event-peptide route now contains real altered-sequence contexts, candidate peptides, public ligand and T-cell evidence, decoys, tiers, claim audit, panel summaries, and threshold robustness. This is public domain-transfer evidence, not a direct link between PGAA-ranked perturbations and experimental antigen evidence. Candidates separate from composition-shuffled and cross-event decoys but not from same-context non-event windows. This mixed decoy sensitivity fails the global enrichment gate and keeps strong immune-evidence claims blocked. A same-cell GSE112274 pilot now links EGFR T790M allele fraction to expression: PGAA-W detects an EGFR distributional association (2,000-permutation p=0.0005), whereas PGAA-H does not place EGFR among its leading scores. The observation is non-causal and does not establish antigen presentation or T-cell recognition. An independent GSE129221 clone-level stress test does not replicate a directionally invariant association: EGFR is lower in T790M-high CORTAD-seq cells but 1.31-fold higher in T790M-positive PC9GR replicates, with exact Wasserstein p=0.10. This discordant, underpowered result is retained as a failed or unresolved cross-system state. A GSE75602 evolutionary stress test further shows that both early GR2 and late GR3 T790M-positive states exceed parental EGFR expression, while late GR3 falls below the drug-tolerant precursor and early GR2. With two replicates per state and a minimum one-sided exact p=0.167, this is descriptive evidence that evolutionary path and comparator modulate direction, not a rescue of cross-system replication. Moving from the single marker to a locked distributed state program produces a positive result: a GSE75602-derived 50-gene down-regulated resistance module transfers to GSE129221 with exact p=0.05 and 62% gene-direction concordance, and the direction remains supported for every prespecified size from 10 to 200 genes. The corresponding up-regulated route fails size robustness. Source-group-adjusted testing in CORTAD-seq also fails, so the selected module is framed as a transferable resistance-state program rather than a T790M-specific mechanism.

Evidence source: `docs/RECHARTER_READINESS_AUDIT.md`, `docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md`, and `evidence/threshold_robustness_summary.tsv`.

Claim boundary: do not claim event-peptide presentation, synthetic-peptide wet-lab confirmation, or T-cell function.

## Discussion Draft

The rechartered PGAA object is strongest where it changes the unit of method evaluation. Rather than presenting only ranked outputs, it reports whether each output supports a claim, requires restriction, or exposes a failure mode. This is a defensible methodological contribution because it turns calibration, negative results, method sensitivity, and external concordance or blockage into primary outputs. The current evidence can now support a bounded computational same-context replication statement for the external concordant units, but it still does not support a strong immune-discovery paper. The strongest honest submission path is therefore a claim-controlled computational method paper centered on failure-preserving benchmarking.

The main remaining weakness is no longer a total absence of externality, but the narrowness and claim ceiling of that externality. The Replogle layer is useful because it creates real concordant and blocked external claim states, yet it is still computational same-context evidence rather than wet-lab or immune validation. A top-tier method paper would be stronger if additional external contexts produced the locked resistance-state module in a third independent PC9 evolution system and resolved its currently fragmented pathway interpretation. The local PC9 drug perturbation candidates do not yet close that gap: Aissa2021 is blocked by a single-batch metadata contract error, and Chang2021 is below the minimum selected-unit gate. The transferable down module is biologically coherent rather than purely statistical: its annotated members and pathway enrichment concentrate on iron handling and transport, carbonic-anhydrase and pH-adaptation genes, and epithelial stress or differentiation markers. CP, SLC40A1, HFE, TFRC, and STEAP4 anchor the iron-homeostasis theme; CA9, CA12, and CA2 anchor the carbonic-anhydrase theme; and RARRES1, STC1, PSCA, HOPX, ELF5, MUC6, and KRT4/KRT13 support a broader epithelial stress-state interpretation. This is best framed as a transferable resistance-state program with iron/pH/differentiation features rather than a T790M-specific mechanism.

## Methods Draft

Failure-mode audit. Existing calibration, parameter-sensitivity, Norman, and Adamson benchmark outputs were compiled into failure-mode states. Each row was assigned an internal failure state, severity, recommended action, and allowed technical interpretation.

Claim-state compilation. Failure-mode rows were converted into manuscript-facing claim states. The compiler assigns each row to comparative support, descriptive only, calibration support, restricted use, or failure/guardrail status and stores the allowed claim language alongside the source table.

Responder-state units. Decision-benchmark claim rows were aggregated by context into responder-state units. Each unit records the primary method, primary metric, supporting methods, descriptive methods, failure/guardrail methods, and allowed manuscript use.

External responder-state stability integration. External Replogle K562 GWPS claim-state rows were integrated with internal leave-one-method stability. The integrated status separates external_same_context_concordant rows from external_same_context_blocked, external_same_context_discordant, or external_same_context_unresolved rows before any replication language is written.

Figure and text generation. Figure 1 and the draft manuscript text were generated from source tables and route/readiness audits. This prevents unsupported claim language from being introduced manually during manuscript assembly.

## Current Worklist State

Benchmark matrix rows: 35.

| Status | Rows |
|---|---:|
| complete | 35 |

## Still-Blocked Evidence

| Missing item | Artifact | Detail |
|---|---|---|

## Forbidden Phrases For This Draft

- validated antigen
- immunogenic peptide validated by T cells
- same-context replicated responder state
- wet-lab validated responder state
- experimentally confirmed presentation
- synthetic peptide validation
- validated T-cell function
