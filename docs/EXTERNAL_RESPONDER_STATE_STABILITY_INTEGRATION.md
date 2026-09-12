# PGAA External Responder-State Stability Integration Report

This report integrates external claim-state rows with internal responder-state stability. It can upgrade a unit only to bounded computational same-context replication; it cannot support immune presentation, synthetic-peptide validation, or T-cell function.

## Summary

| Integrated stability class | Cross-dataset status | Claim ceiling | Units |
|---|---|---|---:|
| method_sensitive_external_blocked | external_same_context_blocked | internal_only_no_external_replication_claim | 3 |
| pgaa_support_dependent_external_blocked | external_same_context_blocked | internal_only_no_external_replication_claim | 1 |
| leave_one_method_stable_external_concordant | external_same_context_concordant | bounded_computational_same_context_replication_allowed | 4 |

## Integrated Units

| Unit | External target | External claim state | Concordance | Integrated status | Claim ceiling |
|---|---|---|---|---|---|
| adamson_decision_benchmark::BHLHE40_pDS258 | BHLHE40 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | external_same_context_concordant | bounded_computational_same_context_replication_allowed |
| adamson_decision_benchmark::CREB1_pDS269 | CREB1 | external_pgaa_w_h_support_observed | external_concordant_with_internal_supported_unit | external_same_context_concordant | bounded_computational_same_context_replication_allowed |
| adamson_decision_benchmark::DDIT3_pDS263 | DDIT3 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | external_same_context_concordant | bounded_computational_same_context_replication_allowed |
| adamson_decision_benchmark::ZNF326_pDS262 | ZNF326 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | external_same_context_concordant | bounded_computational_same_context_replication_allowed |
| norman_decision_benchmark::CEBPA |  | missing_external_claim_state | not_assessable | external_same_context_blocked | internal_only_no_external_replication_claim |
| norman_decision_benchmark::CEBPE |  | missing_external_claim_state | not_assessable | external_same_context_blocked | internal_only_no_external_replication_claim |
| norman_decision_benchmark::KLF1 |  | missing_external_claim_state | not_assessable | external_same_context_blocked | internal_only_no_external_replication_claim |
| adamson_decision_benchmark::SPI1_pDS255 |  | missing_external_claim_state | not_assessable | external_same_context_blocked | internal_only_no_external_replication_claim |

## Claim Boundary

Rows with `external_same_context_blocked` or `external_same_context_unresolved` remain internal-only. Rows with `external_same_context_concordant` still support only computational replication language and must not be described as wet-lab or immune validation.
