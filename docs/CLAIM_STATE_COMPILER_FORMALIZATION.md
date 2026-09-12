# PGAA Claim-State Compiler Formalization

Invariant verdict: `PASS` (12/12 passed).

## Formal Object

The compiler is a finite permission system over four linked layers: row-level claim state, context-level responder decision, leave-one-method stability, and typed external evidence. Its output is not a truth label. It is the maximum interpretation licensed by the currently compiled evidence.

For a unit u, let D(u) be its responder decision, S(u) its omission stability, and X(u) its external state. The computational replication permission is emitted if and only if D(u) is supported, S(u) is leave-one-method stable, and X(u) is external same-context concordant. Every other combination retains or lowers the internal claim ceiling. No state emitted by this compiler licenses biological validation.

## State Space

| Layer | State | Family | Permission rank | Maximum interpretation |
|---|---|---|---:|---|
| row_claim | `failure_or_guardrail` | failure | 0 | `failure_or_guardrail_only` |
| row_claim | `manual_review_required` | unresolved | 0 | `manual_review_required` |
| row_claim | `restricted_use` | guardrail | 1 | `restricted_or_diagnostic_use` |
| row_claim | `calibration_support` | guardrail | 1 | `calibration_statement_only` |
| row_claim | `descriptive_only` | decision | 1 | `descriptive_statement` |
| row_claim | `comparative_support` | decision | 2 | `bounded_comparative_support` |
| decision | `failed_or_limited_state` | failure | 0 | `no_positive_claim` |
| decision | `manual_review_state` | unresolved | 0 | `manual_review_required` |
| decision | `descriptive_comparator_state` | decision | 1 | `descriptive_statement` |
| decision | `provisional_responder_state` | decision | 1 | `descriptive_statement` |
| decision | `comparator_supported_state` | decision | 2 | `bounded_comparator_support` |
| decision | `supported_responder_state` | decision | 2 | `bounded_comparative_support` |
| external | `external_same_context_blocked` | replication | 2 | `internal_ceiling_only` |
| external | `external_same_context_unresolved` | replication | 2 | `internal_ceiling_only` |
| external | `external_same_context_discordant` | replication | 2 | `replication_claim_blocked` |
| external | `external_same_context_concordant` | replication | 3 | `bounded_computational_same_context_replication` |
| validation | `direct_biological_validation` | wet_lab | 4 | `outside_current_compiler` |

## Transition Contract

| Rule | Source | Target | Allowed | Condition or reason |
|---|---|---|---|---|
| T01 | `recommended_action:mapped_action` | `row_claim:mapped_claim_state` | true | action is present in the declared mapping |
| T02 | `row_claim:comparative_support` | `decision:supported_responder_state` | true | at least one PGAA comparative-support witness exists |
| T03 | `row_claim:descriptive_only` | `decision:provisional_responder_state` | true | PGAA descriptive evidence exists and no comparative witness exists |
| T04 | `decision:supported_responder_state` | `stability:leave_one_method_stable` | true | all leave-one-method perturbations preserve the decision state |
| T05 | `stability:leave_one_method_stable` | `external:external_same_context_concordant` | true | the internal unit is supported and the aligned external claim state is concordant |
| T06 | `external:external_same_context_concordant` | `permission:bounded_computational_same_context_replication` | true | supported and leave-one-method stable preconditions both hold |
| T07 | `external:external_same_context_blocked` | `permission:bounded_computational_same_context_replication` | false | missing external evidence cannot increase permission |
| T08 | `external:external_same_context_unresolved` | `permission:bounded_computational_same_context_replication` | false | unresolved evidence cannot increase permission |
| T09 | `external:external_same_context_discordant` | `permission:bounded_computational_same_context_replication` | false | discordant evidence blocks replication language |
| T10 | `decision:provisional_responder_state` | `permission:bounded_computational_same_context_replication` | false | descriptive internal evidence cannot be promoted by external status alone |
| T11 | `stability:method_sensitive` | `permission:bounded_computational_same_context_replication` | false | an unstable decision cannot receive the replication ceiling |
| T12 | `permission:bounded_computational_same_context_replication` | `validation:direct_biological_validation` | false | computational concordance is not wet-lab evidence |

## Current Decision Objects

| Unit | Decision | Stability | External state | Compiled ceiling | Rank |
|---|---|---|---|---|---:|
| adamson_decision_benchmark::BHLHE40_pDS258 | `supported_responder_state` | `leave_one_method_stable` | `external_same_context_concordant` | `bounded_computational_same_context_replication` | 3 |
| adamson_decision_benchmark::CREB1_pDS269 | `supported_responder_state` | `leave_one_method_stable` | `external_same_context_concordant` | `bounded_computational_same_context_replication` | 3 |
| adamson_decision_benchmark::DDIT3_pDS263 | `supported_responder_state` | `leave_one_method_stable` | `external_same_context_concordant` | `bounded_computational_same_context_replication` | 3 |
| adamson_decision_benchmark::SPI1_pDS255 | `supported_responder_state` | `pgaa_support_dependent` | `external_same_context_blocked` | `bounded_comparative_support` | 2 |
| adamson_decision_benchmark::ZNF326_pDS262 | `supported_responder_state` | `leave_one_method_stable` | `external_same_context_concordant` | `bounded_computational_same_context_replication` | 3 |
| norman_decision_benchmark::CEBPA | `provisional_responder_state` | `method_sensitive` | `external_same_context_blocked` | `descriptive_statement` | 1 |
| norman_decision_benchmark::CEBPE | `provisional_responder_state` | `method_sensitive` | `external_same_context_blocked` | `descriptive_statement` | 1 |
| norman_decision_benchmark::KLF1 | `provisional_responder_state` | `method_sensitive` | `external_same_context_blocked` | `descriptive_statement` | 1 |

## Invariant Audit

| Invariant | Status | Checked | Violations | Definition |
|---|---|---:|---:|---|
| I01 | pass | 53 | 0 | Every claim row has a declared claim state. |
| I02 | pass | 53 | 0 | Action-to-claim compilation is deterministic and mapping-faithful. |
| I03 | pass | 25 | 0 | Failure rows cannot carry positive or replication permission. |
| I04 | pass | 8 | 0 | Supported units require a PGAA comparative-support witness. |
| I05 | pass | 8 | 0 | Provisional units require PGAA descriptive evidence and no comparative witness. |
| I06 | pass | 8 | 0 | Responder aggregation preserves row-level support, descriptive, and failure counts. |
| I07 | pass | 4 | 0 | Stable units preserve state under every leave-one-method perturbation. |
| I08 | pass | 1 | 0 | PGAA-dependent units contain an observed PGAA-omission state change. |
| I09 | pass | 4 | 0 | External concordance requires a supported and internally stable unit. |
| I10 | pass | 8 | 0 | Typed external states map to their declared replication ceilings. |
| I11 | pass | 8 | 0 | The computational compiler cannot emit biological-validation permission. |
| I12 | pass | 5 | 0 | Blocked, unresolved, discordant, provisional, or unstable counterfactuals cannot gain replication permission. |

## Falsifiability

The method fails its formal contract if any source action compiles nondeterministically, a supported unit lacks a PGAA comparative witness, aggregation drops failure rows, a stable label hides an omission-induced state change, or a non-concordant or unstable unit receives computational replication permission. These failures are emitted as audit rows rather than being repaired in manuscript prose.

## Claim Boundary

Permission rank 3 is bounded computational same-context replication. Permission rank 4 is direct biological validation and lies outside the current compiler. The present evidence therefore cannot establish immune presentation, synthetic-peptide validation, or T-cell function.
