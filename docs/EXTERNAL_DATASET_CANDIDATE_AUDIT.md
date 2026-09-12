# PGAA External Dataset Candidate Audit

This is candidate-data triage, not replication evidence. No row in this report should be cited as external validation until target coverage, controls, and rerunnable single-cell matrices are verified and the PGAA/comparator gates are rerun.

Priority targets screened: 5 (BHLHE40, CREB1, DDIT3, SPI1, ZNF326)
Candidate public sources screened: 4

## Claim-Safe Summary

| Same-context class | PGAA rerun feasibility | Allowed use | Target-candidate pairs |
|---|---|---|---:|
| near_context_limited_panel | metadata_access_check_required | background_candidate_only_not_replication | 10 |
| processed_signature_or_index_only | not_pgaa_rerunnable | source_discovery_only_not_replication | 5 |
| same_context_candidate_target_verified | rerun_feasible_after_import | candidate_for_external_rerun_not_yet_replication | 5 |

## Highest-Priority Metadata Checks

| Target | Candidate source | Candidate class | Required next check |
|---|---|---|---|
| none | none | none | none |

## Target-Verified Import Candidates

| Target | Candidate source | Candidate class | Required next check |
|---|---|---|---|
| BHLHE40 | Replogle et al. 2022 K562 genome-scale Perturb-seq processed datasets | same_context_candidate_target_verified | import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates |
| CREB1 | Replogle et al. 2022 K562 genome-scale Perturb-seq processed datasets | same_context_candidate_target_verified | import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates |
| DDIT3 | Replogle et al. 2022 K562 genome-scale Perturb-seq processed datasets | same_context_candidate_target_verified | import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates |
| ZNF326 | Replogle et al. 2022 K562 genome-scale Perturb-seq processed datasets | same_context_candidate_target_verified | import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates |
| SPI1 | Replogle et al. 2022 K562 genome-scale Perturb-seq processed datasets | same_context_candidate_target_verified | import expression matrix and perturbation metadata; rerun PGAA and comparator claim-state gates |

## Guardrail

The correct next action is metadata verification and import planning, not manuscript promotion. A candidate becomes replication evidence only after the target perturbation is present, matched controls are usable, the single-cell matrix can be rerun, and the external claim-state matches the internal unit under the predeclared gates.
