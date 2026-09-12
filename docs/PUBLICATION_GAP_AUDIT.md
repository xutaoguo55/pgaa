# PGAA Publication Gap Audit

Date: 2026-08-03

## Purpose

This audit answers a narrower but necessary question: what is still missing before the current PGAA recharter can be treated as a directly publishable manuscript rather than a claim-safe draft?

The current state is stronger than a routine benchmark paper. It is not yet a submission-finished paper because the mainline biological route still lacks the final source-level and prospective closure that would make the story reviewer-hardened.

## What is already proven

| Requirement | Evidence | Status | Interpretation |
|---|---|---|---|
| Real-event readiness exists | `docs/RECHARTER_READINESS_AUDIT.md` | proven | The core real-event artifact chain is present and smoke-free. |
| Claim-safe drafting exists | `docs/RECHARTER_MANUSCRIPT_DRAFT_AUDIT.md` and `docs/RECHARTER_JOURNAL_STYLE_DRAFT_AUDIT.md` | proven | The manuscript text stays inside explicit claim ceilings. |
| External same-context replication exists | `docs/EXTERNAL_CLAIM_STATE_COMPILER_REPLOGLE_K562_GWPS.md`, `docs/EXTERNAL_CLAIM_STATES_REPLOGLE_K562_GWPS.md`, and `evidence/external_claim_states_replogle_k562_gwps.tsv` | proven | Four Replogle K562 GWPS targets are externally concordant and four rows remain blocked, so the compiler carries bounded computational same-context replication without wet-lab promotion. |
| Route selection is explicit | `docs/RECHARTER_ROUTE_DECISION.md` | proven | The current route is `stable_resistance_state_bifurcation`, with governance support from claim-state compilation. |
| Manuscript skeleton is aligned | `docs/RECHARTER_MANUSCRIPT_SKELETON.md` | proven | The skeleton now matches the selected route instead of drifting back to the governance layer. |
| Style-ready wording exists | `docs/RECHARTER_MANUSCRIPT_DRAFT.md` and `docs/RECHARTER_JOURNAL_STYLE_DRAFT.md` | proven | The draft is structured and ready for style revision, not yet submission. |
| Independent dynamic DTP corroboration exists | `docs/GSE335846_DYNAMIC_ATM_VALIDATION.md` and `sources/gse335846_dynamic_atm/preprint_733326.txt` | proven | The linked 2026 preprint reports PC9 dynamic DTP replication defects, ATM sensitivity, HCC4006 bridge support, and low-dose ATR sensitivity, but it still does not expose replicate-level source tables. |
| Dynamic corroboration support figure exists | `docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md`, `figures_png/gse335846_dynamic_corroboration_scorecard.png`, and `figures_png/gse335846_dynamic_corroboration_scorecard.pdf` | proven | Supplementary Figure S5 condenses the figure-digitized dynamic gradient, the source-axis projection, and the marker-shift context into one reviewer-facing visual while keeping the source ceiling unchanged. |
| Phosphoproteomics corroboration exists | `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md`, `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md`, `figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png`, and `figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf` | proven | The companion phosphoproteomics workbook is source-table-backed and strengthens the DTP / replication-stress narrative at the protein and phosphosite level, but exact ATM gene-symbol hits are still absent so the public source ceiling does not change. |
| GSE193258 matched drug screen is source-table-backed | `docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md`, `docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md`, and `figures_png/gse193258_target_specificity_map.png` | proven | The matched drug screen now points to explicit Supplementary Data 1 and 2 tables plus the frozen RNA-seq matrix, and the companion specificity audit plus support figure show ATM as the only exact-significant positive target class. The calibration is traceable even though the matched-model count stays fixed at four. |

## What is still missing for direct submission

| Gap | Current status | Why it matters | Evidence needed to close it |
|---|---|---|---|
| Source-level reinforcement of `GSE335846` drug-response panels | missing | The RNA-seq branch axis is now source-table-backed, but the dynamic ATM support still relies on digitized figure values. GEO currently exposes only `matrix/`, `soft/`, and `miniml/` for `GSE335848`, and the official accession viewer states that supplementary data files are not provided, so no replicate-level source tables are public. | Source tables or a prospective ATM dose-response across branch-weak and branch-strong DTP states. |
| Third independent PC9 evolution system | partially supported | `GSE255958` adds an independent PC9 evolution series and supports the adaptive-stress branch axis, but the frozen down-module route remains mixed rather than cleanly preserved. | A third independent PC9 evolution system that preserves the frozen module without re-ranking or a source-level/dose-response upgrade that supersedes the module route. |
| Strongest local PC9 evolution candidate | partially supported | `GSE150949` maps 45/50 frozen down-module genes and keeps the late day-14 subtype groups below day 0, but day 3 and day 7 remain mixed so it still does not close the third-system contract. | `docs/GSE150949_PC9_EVOLUTION_AUDIT.md` |
| Existing local PC9 drug candidates | blocked | `aissa2021_pc9_drug` fails the batch contract because it has a single recorded batch; `chang2021_pc9_drug` is below the minimum selected-unit gate. | `docs/PC9_THIRD_SYSTEM_BLOCKER_AUDIT.md` |
| Additional local PC9 tolerance candidate | partially supported | `GSE103350` has real raw-count tables and a meaningful PC9/HCC827 tolerance structure, but the frozen adaptive-stress minus replication axis stays negative across all samples. | `docs/GSE103350_PC9_TOLERANCE_AUDIT.md` |
| Explicit mainline biological closure | missing | The route is publishable as a decision paper, but not yet closed as a fully self-contained biological story. | A final source-level checkpoint that confirms the mainline branch axis and preserves the current claim ceiling. |
| Secondary-route containment | partially proven | HDAC remains a secondary branch and immune/event-peptide remains a future track, but these still need to stay visibly subordinate in the final manuscript package. | Continue to keep `HDAC` and immune/event-peptide in subordinate roles unless independent support appears. |

## Direct-publishability verdict

Current verdict: `CLAIM_SAFE_READY_FOR_STYLE_REVISION`, not yet `DIRECTLY_SUBMISSION_READY`.

That is a meaningful state. It means:

1. the paper can be written without unsupported claim inflation;
2. the route choice is no longer ambiguous;
3. the current draft is reviewer-safe;
4. the remaining gap is evidentiary closure, not cleanup.

## What would move the paper up one level

The next publication-level upgrade is not another layer of prose. It is one of these two evidence moves:

1. source-level reinforcement of the dynamic branch-vulnerability readout through `GSE335846` drug-response tables or a prospective ATM dose-response;
2. a third independent PC9 evolution system that preserves the locked resistance-module route, or an equivalent source-level/prospective upgrade that makes the module route unnecessary.

If either is completed cleanly, the manuscript becomes materially more submission-stable.
If both are completed, the paper moves from claim-safe to genuinely review-resistant.
The currently available local PC9 drug candidates do not satisfy that upgrade path, and `GSE255958` only partially helps because it supports the branch axis but does not cleanly preserve the frozen down-module route. `GSE150949` is the strongest local PC9 evolution candidate because it carries 45 of the 50 frozen down-module genes and keeps the late day-14 subtype groups below day 0, but the early day 3 and day 7 states remain mixed and therefore do not close the third-system contract. `GSE103350` adds a real tolerance dataset, but it remains a partial candidate because it stays on the negative side of the frozen axis rather than closing the third-system contract. `GSE193258` now closes the source-table side of the matched-screen calibration and sharpens target specificity, but the matched-model count still limits the strength of the pharmacology claim.

## Submission-Facing Gap Package

The current missing-evidence package is already prepared as five concrete artifacts:

1. `docs/AUTHOR_DATA_REQUEST_GSE335846.md` requests the replicate-level source tables needed to replace figure-digitized branch-response values.
2. `docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md` predeclares the branch-stratified ATM validation experiment with mixed-model analysis, mechanistic readouts, and batch control.
3. `docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md` provides the claim-bounded caption and Results text for the lead-target support figure.
4. `docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md` provides the claim-bounded caption and Results text for the strongest local third-system candidate.
5. `docs/SUBMISSION_PACKAGE_INDEX.md` provides the one-page navigation layer for the full submission package, including `docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md` and `docs/GSE150949_PC9_EVOLUTION_AUDIT.md`.

These attachments let the paper move toward submission without changing the claim ceiling or reopening the mainline narrative.

## What not to do

- Do not reopen the manuscript around the failure-preserving benchmark engine as the mainline biological route.
- Do not merge the immune/event-peptide track into the main story unless it is matched to event-expression evidence.
- Do not call the current state submission-ready just because the draft audits pass.
- Do not widen the scope to weaker auxiliary routes instead of closing the branch-axis and module-route gaps.

## Bottom line

The current project has crossed the threshold from "interesting analysis" to "claim-safe manuscript package."
It has not yet crossed the threshold from "claim-safe" to "directly submission-ready" because the mainline resistance-state route still needs one more source-level or prospective treatment-response evidence layer.
