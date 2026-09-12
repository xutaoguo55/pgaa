# PGAA top-journal recharter

Date: 2026-07-16

## Blunt starting point

The current PGAA manuscript is a competent distribution-aware Perturb-seq method, but that is not enough for a Cell, Nature Methods, or Cell Systems style method paper. The main weakness is not the name. The weakness is that the current method answers a familiar question with a useful but incremental statistic:

> Which genes shift in a heterogeneous single-cell perturbation comparison?

Top method papers usually do something stronger:

> They create a new measurable object, make old analyses visibly inadequate, and prove that the new object changes biological decisions across multiple independent settings.

The immune-evidence rescue work should therefore not be treated as a small validation add-on. It should become the rechartered method object:

> A failure-preserving evidence compiler that converts perturbation-ranked molecular events into auditable event-peptide-HLA-immune evidence units.

This changes the paper from "a statistic for distribution shifts" to "a compiler from single-cell perturbation effects to experimentally actionable immune-candidate evidence."

## New central problem

Current computational pipelines often stop at gene-level or pathway-level hits. For immune or translational follow-up, that is the wrong unit. A perturbation-ranked gene is not directly testable in immunopeptidomics, peptide synthesis, or T-cell assays. The testable unit is an event-peptide-HLA evidence object with explicit missing evidence.

The new problem statement:

> Given a ranked perturbation/event signal and public molecular evidence, infer and audit which event-derived peptide-HLA candidates are actionable enough for follow-up, while preserving every missing validation layer.

This is more defensible than claiming antigen discovery without experiments, and it is more novel than another distributional test.

## Required method object

The method must operate on a candidate table where each row is a testable evidence unit:

| Field group | Required content | Why it matters |
|---|---|---|
| PGAA signal | source dataset, perturbation, score, rank, effect class | Links candidate to the perturbation evidence. |
| Molecular event | event type, gene, coordinate, altered residue or junction | Prevents gene-level storytelling. |
| Peptide object | exact peptide, event position in peptide, HLA class, HLA allele | Defines the wet-lab-testable object. |
| Presentation evidence | exact ligand, overlap ligand, source IDs, compatible HLA | Separates presentation from binding prediction. |
| Prediction evidence | binding, stability, cleavage/TAP if applicable | Useful only after public evidence is separated. |
| Assay-readiness | synthesis flags, chemistry liabilities, control suitability | Replaces missing synthetic peptide work with transparent readiness triage. |
| T-cell evidence | exact peptide, region, source-protein, immune-context support | Separates immune plausibility from functional validation. |
| Negative controls | matched decoys, source-protein decoys, database-hit background | Protects against public database coincidence. |
| Claim gate | tier, allowed claim, prohibited claim flags | Prevents overclaiming in the manuscript. |

If the project cannot construct this table for real candidates, it remains a PGAA software paper, not a rechartered immune-method paper.

## Proposed method identity

The rechartered method has three layers:

1. **PGAA-Rank**: distribution-aware perturbation or event prioritization.
2. **Event-Peptide Compiler**: deterministic conversion from ranked molecular events to peptide-HLA candidate units.
3. **Evidence Ladder**: public ligand, binding, synthesis-readiness, T-cell evidence, decoy background, and claim control.

The current repository now has an early Evidence Ladder implementation. The missing top-journal layer is the Event-Peptide Compiler plus serious cross-dataset benchmarking.

## What would be genuinely new

The strongest novelty is not "we use public databases." Many papers do that. The novelty must be:

1. **Unit conversion**: transform perturbation-ranked molecular events into explicit peptide-HLA evidence units rather than stopping at genes.
2. **Failure preservation**: unmatched candidates and missing layers remain first-class results, not filtered-away failures.
3. **Claim compilation**: the method outputs the strongest allowed scientific claim for each candidate and blocks unsupported language.
4. **Decoy-calibrated public evidence**: public ligand/T-cell matches are interpreted against matched negative candidate sets.
5. **Decision-level benchmarking**: show that the method changes follow-up panels compared with gene-level, binding-only, or expression-only prioritization.

If these five pieces are all implemented and validated on real datasets, the work has a credible methods-level identity.

## Minimum benchmark package for a serious methods paper

The benchmark must prove decision value, not just produce attractive candidate tables.

| Benchmark | Required comparator | Required endpoint | Pass condition |
|---|---|---|---|
| Event-to-peptide conversion audit | gene-level PGAA only | number of auditable peptide-HLA units | All candidates have coordinates, exact peptides, and HLA fields. |
| Public ligand evidence retrieval | binding-only ranking | exact and overlap ligand support over decoys | Candidate hit rate exceeds matched decoys in a predeclared analysis. |
| T-cell evidence retrieval | ligand-only ranking | exact/region/source/context T-cell support | Evidence levels are separated; no "immunogenic" claim without exact evidence. |
| Follow-up panel design | PGAA rank alone, binding rank alone | top 20-50 candidate panel quality | Panel includes positives, controls, HLA diversity, and synthesis-ready candidates. |
| Robustness | alternative decoys and evidence thresholds | tier stability | Tier A/B conclusions are stable under conservative thresholds. |
| Negative result handling | filtered-only reporting | unmatched candidate reporting | Missing evidence is reported in full. |

## Figure architecture for a rechartered manuscript

### Figure 1: New object and workflow

Show the transition:

single-cell perturbation response -> ranked event/gene signal -> event-peptide-HLA object -> evidence ladder -> allowed claim.

This figure must visually distinguish:

- prediction;
- public presentation support;
- assay readiness;
- public T-cell support;
- missing validation.

### Figure 2: Event-peptide compiler

Show real candidate construction:

- event coordinates;
- peptide window generation;
- HLA allele assignment;
- candidate and decoy generation;
- reproducibility checks.

This is the figure that makes the method feel new rather than a post hoc table.

### Figure 3: Evidence ladder benchmark

Show exact/overlap ligand evidence, T-cell evidence, synthesis categories, and decoy background. The key panel should be candidate-vs-decoy match rate, not only a heatmap.

### Figure 4: Decision impact

Compare follow-up panels selected by:

- PGAA rank alone;
- binding prediction alone;
- public ligand evidence alone;
- full evidence ladder.

The top-journal question is whether the full method changes decisions in a biologically sensible and auditable way.

### Extended Data

- full candidate table;
- full decoy table;
- threshold sensitivity;
- dataset-by-dataset performance;
- failed candidates and missing evidence flags.

## Claim ceiling by evidence state

| Current evidence state | Claim ceiling |
|---|---|
| Existing PGAA distribution tests only | Distribution-aware Perturb-seq ranking method. |
| Evidence Ladder smoke examples only | Software infrastructure for future immune-evidence auditing. |
| Real candidate_event_peptides table without public evidence enrichment | Honest negative audit; not a strong immune discovery paper. |
| Real candidates with ligand enrichment over decoys but little T-cell support | Computational immunology prioritization method. |
| Multiple exact ligand and exact/region T-cell public matches, stable over decoys | Strong public-evidence-supported follow-up framework. |
| New wet-lab immunopeptidomics and T-cell assays | True antigen-discovery/translational paper. |

Without wet-lab work, the honest ceiling is a computational method paper. A top-tier submission would require exceptional breadth, transparent negative controls, and a clear decision improvement over existing prioritization strategies.

## Red-team questions reviewers will ask

1. Why is this not just PGAA plus database annotation?
2. Are candidate peptides generated from real events or from gene names?
3. Are exact ligand matches separated from overlap/source-protein matches?
4. Are decoy match rates shown for the same query rules?
5. Does the method ever call a candidate "validated" without new experiments?
6. Does the method beat binding-only or expression-only prioritization at the decision level?
7. Are negative and unmatched candidates reported?
8. Can another lab reproduce every row from raw candidate events?
9. Does the claim gate prevent manuscript overstatement?
10. Is the method useful if no candidates have public T-cell evidence?

The current rescue framework answers questions 3, 4, 5, 7, and 9 in prototype form. It does not yet answer questions 1, 2, 6, 8, or 10 strongly enough.

## Immediate build priorities

Priority 1: create a real `evidence/candidate_event_peptides.tsv`.

- Do not use smoke rows.
- Each row must have event coordinate, exact peptide, HLA allele, PGAA rank, and source dataset.
- If only gene-level PGAA outputs exist, explicitly label this as a blocker and do not invent event-level peptides.
- Current audit status: `scripts/audit_event_sources.py` inspects the available Norman, Adamson, and CEBPE PGAA outputs and reports 0 event-ready source tables in `docs/EVENT_SOURCE_AUDIT.md`. These files are gene-level ranking sources only. They must not be treated as altered peptide events.

Priority 2: implement an Event-Peptide Compiler script.

- Input: event table with gene, mutation/splice/fusion/editing coordinate, altered sequence context, HLA allele.
- Output: candidate peptide windows plus matched decoys.
- Required check: every emitted peptide contains the event residue or junction.
- Prototype status: `scripts/compile_event_peptides.py` now compiles altered amino-acid sequence contexts into event-containing peptide/HLA candidates and same-context non-event decoys. This is infrastructure only until real event rows replace `evidence/event_sequence_contexts_template.tsv`.
- Source-control status: `scripts/audit_event_sources.py` now classifies candidate input tables before compilation. This prevents accidental conversion of gene-level PGAA scores into unsupported event-peptide claims.

Priority 3: add a benchmark matrix.

- Track dataset, candidate source, comparator, endpoint, pass condition, current status, and blocking file.
- Use it as the worklist for a real methods paper.

Priority 4: build a decision-impact panel.

- Show how the full ladder changes a top-N follow-up panel compared with PGAA rank alone and binding-only ranking.
- Prototype status: `scripts/compare_followup_panels.py` compares full-ladder selection against PGAA-rank, binding-only, and ligand-only baselines. It currently demonstrates the metric plumbing on smoke tier tables; manuscript use still requires a real `immune_evidence_tiers.tsv`.

Priority 5: stress-test threshold robustness.

- Recompute tiers under exact-match-only and decoy-guarded rules.
- Report how many default Tier A/B candidates are retained or lost.
- Prototype status: `scripts/check_threshold_robustness.py` produces adjusted tier rows and scenario summaries from a tier table. It is ready for real `immune_evidence_tiers.tsv`, but current outputs are smoke-only.

Priority 6: run the recharter readiness audit before any manuscript rewrite.

- Command: `python3 scripts/audit_recharter_readiness.py --audit-out evidence/recharter_readiness_audit.tsv --markdown-out docs/RECHARTER_READINESS_AUDIT.md`.
- The audit must return `READY_FOR_RECHARTER_MANUSCRIPT_DRAFT` before a top-journal recharter manuscript is drafted.
- Any `missing`, `incomplete`, or `smoke_or_template` row means the current state is infrastructure-only, not a real immune-method result.

Priority 7: rewrite the manuscript only after real candidate evidence exists.

- Rewriting first would create a polished but unsupported story.

## Go/no-go gate for top-journal attempt

Proceed toward a high-risk top-journal submission only if all are true:

1. `candidate_event_peptides.tsv` contains real non-smoke event-peptide-HLA rows.
2. At least one independent public ligand or T-cell evidence source is queried with reproducible rules.
3. Candidate-vs-decoy enrichment is reported.
4. Decision impact is shown against at least two simpler baselines.
5. Claim audit contains no prohibited wet-lab validation phrasing.
6. A reviewer can reproduce the candidate table from source inputs.
7. `docs/RECHARTER_READINESS_AUDIT.md` reports `READY_FOR_RECHARTER_MANUSCRIPT_DRAFT`.

If any of these are false, the project should stay in a lower-risk computational-method venue while the infrastructure matures.

## Current route decision after source audit

The inspected repository state does not yet support the event-peptide top-journal story. The strongest honest statement is:

> PGAA currently has infrastructure for an event-peptide immune-evidence compiler, but the available PGAA result tables are gene-level perturbation rankings and cannot themselves provide altered peptide events.

There are therefore two defensible routes:

1. **Continue the event-peptide recharter only after adding a real sequence-changing event source.** Acceptable inputs include missense variants, splice junctions, fusions, RNA-editing events, or experimentally reported altered proteins with exact altered amino-acid context and HLA information.
2. **Reframe away from event-peptide antigen claims.** If no event source can be added, the top-journal attempt should pivot to a different methods object, such as failure-preserving distributional perturbation benchmarking, responder-state discovery, or decision-calibrated perturbation ranking. That route is less translational, but avoids a fatal claim mismatch.

## Current non-event route selected for immediate work

`scripts/select_recharter_route.py` ranks five candidate routes in `evidence/recharter_route_options.tsv`. Under the current evidence state, the selected immediate route is:

> Failure-preserving perturbation benchmark engine.

This is not as flashy as the event-peptide immune compiler, but it is evidence-backed now. The central object becomes:

> A benchmark failure mode and calibration object that travels with every PGAA result and states whether a statistic is interpretable, restricted, or rejected for primary claims.

The first concrete artifact for this route is `docs/FAILURE_MODE_AUDIT.md`, generated by `scripts/build_failure_mode_audit.py`. It converts existing S2 calibration, bin-sensitivity, Norman decision-benchmark, and Adamson decision-benchmark results into explicit interpretation states. In the current run, 49 rows are audited and 25 are high-risk or critical. Those failures should be shown as part of the method, not hidden as limitations after the fact.

The second concrete artifact is `docs/RESULT_CLAIM_STATE_REPORT.md`, generated by `scripts/build_result_claims.py`. It compiles every audit row into a manuscript-facing `result_claim_state`, figure panel, and allowed claim sentence. The current result has 9 `comparative_support` decision-benchmark rows, 11 `descriptive_only` rows, 17 decision-benchmark `failure_or_guardrail` rows, and additional calibration/parameter guardrail rows. This means the method object is no longer just a ranked output; it is a claim-control compiler that says what each benchmark row is allowed to support.

The third concrete artifact is `docs/CLAIM_PANEL_SOURCE_REPORT.md`, generated by `scripts/build_claim_panel_sources.py`. It turns the 49 claim-state rows into figure-ready source data: 37 rows for a Figure 1 decision-benchmark panel and 12 rows for Figure 2 calibration/parameter guardrail panels. Positive benchmark claims should come only from the 9 `comparative_support` rows; failure and guardrail rows stay visible as method behavior.

The fourth concrete artifact is `docs/RESPONDER_STATE_DECISION_UNITS.md`, generated by `scripts/build_responder_state_units.py`. It aggregates the decision-benchmark rows into 8 context-level responder-state units: 5 Adamson units are `supported_responder_state`, while 3 Norman units are `provisional_responder_state`. Each unit preserves the supporting methods, descriptive methods, failure/guardrail methods, primary metric, and allowed manuscript use. This is the first layer where PGAA is framed as a decision-state compiler rather than a ranked-gene generator.

The fifth concrete artifact is `docs/RESPONDER_STATE_STABILITY_REPORT.md`, generated by `scripts/check_responder_state_stability.py`. It performs 37 leave-one-method checks across the 8 responder-state units. Four Adamson units are `leave_one_method_stable`; SPI1 is `pgaa_support_dependent`; the three Norman provisional units are `method_sensitive` because removing the PGAA descriptive row changes the state. Every unit is currently `no_cross_dataset_same_context`, so same-context cross-dataset replication remains absent and must not be claimed.

The sixth concrete artifact is `docs/MAIN_FIGURE_SOURCE_REPORT.md`, generated by `scripts/build_main_figure_sources.py`. It compiles the claim-state distribution, responder-state units, and stability diagnostics into a 27-row Figure 1 source table: 11 claim/guardrail rows, 8 responder-state unit rows, and 8 stability rows. This makes the main figure auditable from the generated evidence chain rather than manually assembled from selected examples.

The seventh concrete artifact is `docs/MAIN_FIGURE_RENDER_REPORT.md`, generated by `scripts/render_main_figure1.py`. It renders the 27-row source table into `figures_png/figure1_recharter_decision_object.png` and `figures_png/figure1_recharter_decision_object.pdf`. This is now a source-driven Figure 1 draft rather than a manual schematic. The figure still preserves the current limitation: all 8 stability rows are `no_cross_dataset_same_context`, so the manuscript cannot claim same-context replicated responder states without adding external or reprocessed same-context evidence.

The eighth concrete artifact is `docs/FIGURE1_CAPTION_AND_RESULTS_DRAFT.md`, generated by `scripts/draft_figure1_text.py`. It turns the same Figure 1 source table into claim-bounded figure caption and Results text. The text explicitly blocks same-context cross-dataset replication, immune presentation, peptide validation, and T-cell function claims because those layers are not supported by the current evidence package.

The ninth concrete artifact is `docs/RECHARTER_MANUSCRIPT_SKELETON.md`, generated by `scripts/draft_recharter_manuscript_skeleton.py`. It expands the route decision into a manuscript skeleton with five Results sections, allowed/prohibited claim boundaries, a reviewer-risk map, benchmark-matrix status counts, and missing readiness artifacts. This is the current safest manuscript structure for the failure-preserving benchmark route because every section points back to a generated evidence table or report.

The tenth concrete artifact is `docs/RECHARTER_MANUSCRIPT_DRAFT.md`, generated by `scripts/draft_recharter_manuscript.py`. It expands the skeleton into claim-bounded manuscript sections: title, abstract, introduction, results, discussion, methods, current worklist state, blocked-evidence table, and forbidden phrases. This draft is not submission-ready prose, but it is the first manuscript-level object that preserves the failure-preserving route without inventing replication, immune-presentation, synthetic-peptide, or T-cell-function claims.

The eleventh concrete artifact is `docs/RECHARTER_MANUSCRIPT_DRAFT_AUDIT.md`, generated by `scripts/audit_recharter_manuscript_draft.py`. It audits the manuscript draft for required sections, required evidence references, claim-boundary phrases, forbidden unsupported phrases outside the explicit forbidden-phrase list, and consistency with `evidence/recharter_readiness_audit.tsv`. The current verdict is `CLAIM_SAFE_WITH_BLOCKERS`: the draft is language-safe, but it remains blocked for submission-readiness because real event/immune validation evidence is still missing.

The twelfth concrete artifact is `docs/RECHARTER_JOURNAL_STYLE_DRAFT.md`, generated by `scripts/draft_recharter_journal_style_manuscript.py`, with its companion audit `docs/RECHARTER_JOURNAL_STYLE_DRAFT_AUDIT.md`. This version rewrites the safe internal draft into a more journal-facing manuscript argument: PGAA is positioned as a claim-state compiler for failure-preserving single-cell perturbation benchmarking. The current audit verdict remains `CLAIM_SAFE_WITH_BLOCKERS`. This is an expression and framing upgrade, not a new evidence layer; the draft still cannot claim same-context replication, immune presentation, peptide wet-lab confirmation, or T-cell function.

The thirteenth concrete artifact is `docs/EXTERNAL_VALIDATION_OPPORTUNITY_AUDIT.md`, generated by `scripts/audit_external_validation_opportunities.py`. It converts the vague instruction "add external evidence" into a ranked same-context validation worklist. In the current run, all 8 responder-state units still need external same-context evidence. Four internally supported and leave-one-method-stable Adamson units are Tier 1 replication candidates: BHLHE40, CREB1, DDIT3, and ZNF326. SPI1 is Tier 2 because it is PGAA-support dependent, and the Norman CEBPA/CEBPE/KLF1 units are Tier 3 because they are provisional and method-sensitive. This audit does not create replication evidence; it defines the next external data acquisition target without relaxing the claim ceiling.

The fourteenth concrete artifact is `docs/EXTERNAL_DATASET_CANDIDATE_AUDIT.md`, generated by `scripts/audit_external_dataset_candidates.py`. It takes the Tier 1/Tier 2 worklist and classifies public external-data candidates before any import. The strongest current lead is the Replogle et al. K562 genome-scale CRISPRi Perturb-seq processed-data route. After the target-coverage audit below, it is now a target-verified candidate for import planning, not replication evidence.

The fifteenth concrete artifact is `docs/EXTERNAL_TARGET_COVERAGE_REPLOGLE_K562_GWPS.md`, generated by `scripts/check_external_target_coverage.py` from `K562_gwps_raw_bulk_01.h5ad`. This verifies that BHLHE40, CREB1, DDIT3, ZNF326, and SPI1 are present in the Replogle K562 GWPS h5ad observation metadata and that non-targeting/core-control metadata exists. This is a real improvement over dataset-level searching, but it is still not an external replication result: the verified file is pseudobulk, so PGAA distributional replication requires importing the matching single-cell h5ad and rerunning the full claim-state gate.

The sixteenth concrete artifact is `docs/EXTERNAL_SINGLECELL_IMPORT_PLAN_REPLOGLE_K562_GWPS.md`, generated by `scripts/plan_external_singlecell_import.py`. It prevents the next step from becoming an unsafe manual download. The preferred Replogle `K562_gwps_raw_singlecell_01.h5ad` file is about 61.31 GiB. On the current scratch volume, nominal free space exceeds the file size but does not meet the predeclared 1.25x safety margin, so the correct next action is external storage or cloud scratch rather than downloading into the repository or a nearly full system volume.

The seventeenth concrete artifact is `docs/EXTERNAL_RERUN_READINESS_REPLOGLE_K562_GWPS.md`, generated by `scripts/check_external_rerun_readiness.py`. It is the preflight gate immediately before any external PGAA/comparator rerun. In the current run, target/control prerequisites are carried forward from the verified Replogle metadata, but the matching single-cell h5ad is not present locally, so the gate status is `blocked_waiting_for_singlecell_h5ad`. This is a useful hard boundary: it prevents a pseudobulk metadata audit or a planned download from being described as external replication evidence.

The eighteenth concrete artifact is `docs/EXTERNAL_CLAIM_STATE_CONTRACT_REPLOGLE_K562_GWPS.md`, generated by `scripts/build_external_claim_state_contract.py`. It converts the readiness gate into a per-target execution contract for the four Tier 1 candidates: BHLHE40, CREB1, DDIT3, and ZNF326. In the current state, all four rows are `blocked_by_readiness_gate`; once the single-cell h5ad is present and the readiness gate reaches `ready_for_external_claim_state_rerun`, the same contract becomes the auditable source for PGAA input files, PGAA-W/PGAA-H output files, and the external claim-state output expected for each target.

The nineteenth concrete artifact is `docs/EXTERNAL_PGAA_INPUT_EXTRACTION_REPLOGLE_K562_GWPS.md`, generated by `scripts/extract_external_pgaa_inputs.py`. It is the bridge from a ready external contract to actual PGAA CLI inputs. The gate writes expression and metadata CSVs only after a per-target contract reaches `ready_for_pgaa_input_extraction`; in the current state, all four Tier 1 rows are `blocked_by_contract_status`. This prevents a manual h5ad-to-CSV conversion from becoming an undocumented and unreviewable step.

The twentieth concrete artifact is `docs/EXTERNAL_PGAA_EXECUTION_MANIFEST_REPLOGLE_K562_GWPS.md`, generated by `scripts/build_external_pgaa_execution_manifest.py`. It audits whether the predeclared external PGAA input files, PGAA-W/PGAA-H outputs, and per-target external claim-state outputs actually exist. In the current state, all four Tier 1 rows are still `blocked_by_contract_status`; the manifest therefore contains no runnable PGAA command and no replication claim. Once the h5ad is present and input extraction succeeds, this manifest becomes the handoff object between PGAA CLI execution and external claim-state compilation.

The twenty-first concrete artifact is `docs/EXTERNAL_CLAIM_STATE_COMPILER_REPLOGLE_K562_GWPS.md`, generated by `scripts/compile_external_claim_states.py`. It aligns each external Replogle target to the predeclared internal Adamson responder-state unit and compiles PGAA-W/PGAA-H output files into conservative external claim states. In the current state, BHLHE40, CREB1, DDIT3, and ZNF326 all map to supported internal responder-state units, but all four external rows are `blocked_by_external_execution_status` because external PGAA outputs do not yet exist. This makes the future replication claim boundary explicit: even a concordant row would support only bounded computational same-context replication, not immune presentation, synthetic-peptide validation, or T-cell function.

The twenty-second concrete artifact is `docs/EXTERNAL_RESPONDER_STATE_STABILITY_INTEGRATION.md`, generated by `scripts/integrate_external_responder_state_stability.py`. It integrates the external claim-state rows with the existing internal leave-one-method stability summary. In the current state, all 8 responder-state units remain `external_same_context_blocked`: four Tier 1 Adamson units have matched Replogle target rows but blocked external execution, while SPI1 and the three Norman units have no external claim-state row in this Replogle Tier 1 pass. The claim ceiling for every unit remains `internal_only_no_external_replication_claim`.

The next build step for this route is to render the figure and decide whether to add external same-context data:

1. import the matching Replogle K562 GWPS single-cell h5ad on external storage or cloud scratch now that target/control metadata has been verified in the bulk file;
2. rerun `scripts/check_external_rerun_readiness.py` until it reaches `ready_for_external_claim_state_rerun`;
3. rerun `scripts/build_external_claim_state_contract.py` so the per-target command and output contract switches from blocked to ready;
4. rerun `scripts/extract_external_pgaa_inputs.py` so the PGAA CLI expression and metadata inputs are generated from the h5ad under audit;
5. rerun `scripts/build_external_pgaa_execution_manifest.py` to verify which target inputs are ready for PGAA CLI execution and which PGAA/claim-state outputs are still absent;
6. run the predeclared PGAA CLI commands and rerun `scripts/compile_external_claim_states.py` so PGAA-W/PGAA-H outputs become external target-level claim states;
7. rerun `scripts/integrate_external_responder_state_stability.py` so concordant, discordant, unresolved, or blocked external rows update unit-level claim ceilings;
8. rerun responder-state stability and Figure 1/source-data gates on the imported external source before any replication claim;
9. preserve the immune route as blocked until real sequence-changing event sources exist;
10. keep every manuscript claim routed through `result_claim_states.tsv`, `claim_panel_source_data.tsv`, `responder_state_units.tsv`, `responder_state_stability_summary.tsv`, `external_claim_states_replogle_k562_gwps.tsv`, `external_responder_state_stability_integrated.tsv`, and `main_figure_source_data.tsv`.
