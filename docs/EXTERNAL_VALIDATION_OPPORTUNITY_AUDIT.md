# PGAA External Same-Context Validation Opportunity Audit

Responder-state units audited: 8
Units still needing external same-context evidence: 8

## Priority Summary

| Priority | External status | Local status | Units |
|---|---|---|---:|
| tier1_replication_candidate | external_same_context_needed | local_same_context_absent | 4 |
| tier2_dependency_stress_test | external_same_context_needed | local_same_context_absent | 1 |
| tier3_provisional_state_test | external_same_context_needed | local_same_context_absent | 3 |

## Tier 1 External Replication Candidates

| Unit | Target | Stability | Required external modality | Manifest hint |
|---|---|---|---|---|
| `adamson_decision_benchmark::BHLHE40_pDS258` | BHLHE40 | leave_one_method_stable | independent K562 CRISPRi or comparable UPR perturbation screen | no current DATASET_MANIFEST row names this target |
| `adamson_decision_benchmark::CREB1_pDS269` | CREB1 | leave_one_method_stable | independent K562 CRISPRi or comparable UPR perturbation screen | no current DATASET_MANIFEST row names this target |
| `adamson_decision_benchmark::DDIT3_pDS263` | DDIT3 | leave_one_method_stable | independent K562 CRISPRi or comparable UPR perturbation screen | no current DATASET_MANIFEST row names this target |
| `adamson_decision_benchmark::ZNF326_pDS262` | ZNF326 | leave_one_method_stable | independent K562 CRISPRi or comparable UPR perturbation screen | no current DATASET_MANIFEST row names this target |

## Manuscript Use

This audit is a worklist, not replication evidence. A responder-state unit must remain `no_cross_dataset_same_context` until an external dataset with the same target/context is added and the claim-state compiler is rerun on that dataset.

Top-journal priority should start with Tier 1 units because they are already supported and leave-one-method stable internally. Tier 2 and Tier 3 units are better used as stress tests or provisional-state adjudication.
