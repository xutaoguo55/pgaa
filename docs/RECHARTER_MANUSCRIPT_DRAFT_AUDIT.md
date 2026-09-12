# PGAA Recharter Manuscript Draft Claim Audit

Verdict: `CLAIM_SAFE_READY_FOR_STYLE_REVISION`

| Status | Rows |
|---|---:|
| pass | 26 |
| fail | 0 |
| warning | 0 |

## Audit Rows

| Check | Status | Severity | Detail |
|---|---|---|---|
| `section:draft_status` | pass | error | required section present: ## Draft Status |
| `section:title` | pass | error | required section present: ## Title |
| `section:abstract_draft` | pass | error | required section present: ## Abstract Draft |
| `section:introduction_draft` | pass | error | required section present: ## Introduction Draft |
| `section:results_draft` | pass | error | required section present: ## Results Draft |
| `section:discussion_draft` | pass | error | required section present: ## Discussion Draft |
| `section:methods_draft` | pass | error | required section present: ## Methods Draft |
| `section:still-blocked_evidence` | pass | error | required section present: ## Still-Blocked Evidence |
| `section:forbidden_phrases_for_this_draft` | pass | error | required section present: ## Forbidden Phrases For This Draft |
| `reference:evidence/result_claim_states.tsv` | pass | error | required evidence reference present: evidence/result_claim_states.tsv |
| `reference:evidence/responder_state_units.tsv` | pass | error | required evidence reference present: evidence/responder_state_units.tsv |
| `reference:evidence/responder_state_stability_summary.tsv` | pass | error | required evidence reference present: evidence/responder_state_stability_summary.tsv |
| `reference:evidence/external_responder_state_stability_summary.tsv` | pass | error | required evidence reference present: evidence/external_responder_state_stability_summary.tsv |
| `reference:evidence/main_figure_source_data.tsv` | pass | error | required evidence reference present: evidence/main_figure_source_data.tsv |
| `reference:figures_png/figure1_recharter_decision_object.png` | pass | error | required evidence reference present: figures_png/figure1_recharter_decision_object.png |
| `reference:docs/RECHARTER_READINESS_AUDIT.md` | pass | error | required evidence reference present: docs/RECHARTER_READINESS_AUDIT.md |
| `boundary:not yet a submission-ready manuscript` | pass | error | required claim-boundary phrase present: not yet a submission-ready manuscript |
| `boundary:Claim boundary` | pass | error | required claim-boundary phrase present: Claim boundary |
| `boundary:same_context_replication_ceiling` | pass | error | same-context replication ceiling is explicit |
| `unsupported_phrase:validated antigen` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `unsupported_phrase:immunogenic peptide validated by T cells` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `unsupported_phrase:same-context replicated responder state` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `unsupported_phrase:experimentally confirmed presentation` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `unsupported_phrase:synthetic peptide validation` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `unsupported_phrase:validated T-cell function` | pass | error | unsupported phrase absent outside forbidden-phrase list |
| `readiness_consistency:ready` | pass | info | readiness audit reports all required artifacts ready |

## Interpretation

The draft is claim-safe against the current audit and can proceed to style revision.
