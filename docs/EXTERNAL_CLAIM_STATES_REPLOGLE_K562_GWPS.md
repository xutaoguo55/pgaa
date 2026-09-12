# PGAA External Claim-State Compiler Report

This report compiles external PGAA-W/PGAA-H outputs into target-level claim states. It is not wet-lab validation, immune-presentation evidence, synthetic-peptide validation, or T-cell functional validation.

## Summary

| External claim state | Concordance state | Allowed use | Targets |
|---|---|---|---:|
| external_pgaa_w_h_support_observed | external_concordant_with_internal_supported_unit | external_claim_state_not_wet_lab_validation | 1 |
| external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | external_claim_state_not_wet_lab_validation | 3 |

## Target Claim States

| Target | Internal unit | External claim state | Concordance | PGAA-W rank | PGAA-H rank |
|---|---|---|---|---:|---:|
| BHLHE40 | adamson_decision_benchmark::BHLHE40_pDS258 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | 314 | 8182 |
| CREB1 | adamson_decision_benchmark::CREB1_pDS269 | external_pgaa_w_h_support_observed | external_concordant_with_internal_supported_unit | 723 | 1 |
| DDIT3 | adamson_decision_benchmark::DDIT3_pDS263 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | 210 | 8116 |
| ZNF326 | adamson_decision_benchmark::ZNF326_pDS262 | external_single_pgaa_mode_support_observed | external_concordant_with_internal_supported_unit | 104 | 1345 |

## Claim Boundary

A concordant external claim-state row can support only a computational same-context replication statement after the predeclared PGAA outputs exist. It still cannot support immune-presentation, synthetic-peptide, or T-cell-function claims.
