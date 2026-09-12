# Local External h5ad Candidate Audit

This audit is read-only. No source file was copied, modified, or deleted.

Priority targets: BHLHE40, CEBPA, CEBPE, CREB1, DDIT3, KLF1, SPI1, ZNF326.

Readable candidates: 4/4. Logical duplicate groups: 1. Replication-eligible distinct matrices: 1.

| Candidate | Shape | Target hits | Controls | Logical group | Independence | Allowed role |
|---|---:|---|---|---|---|---|
| `replogle_essential_compact` | 310385 x 8563 | none | True | `logical_group_03` | `duplicate_representation_not_independent` | `cross_target_generality_candidate` |
| `replogle_essential_large` | 310385 x 8563 | none | True | `logical_group_03` | `duplicate_representation_not_independent` | `cross_target_generality_candidate` |
| `replogle_exp6` | 27104 x 5019 | none | True | `logical_group_02` | `distinct_logical_matrix` | `cross_target_generality_candidate` |
| `replogle_k562_gwps_reference` | 1989578 x 8248 | BHLHE40;CEBPA;CEBPE;CREB1;DDIT3;KLF1;SPI1;ZNF326 | True | `logical_group_01` | `distinct_logical_matrix` | `same_target_replication_candidate` |

## Claim Boundary

Different file sizes do not establish dataset independence. Files with matching cell identities, feature identities, perturbation metadata, and sampled matrix values are treated as duplicate representations. A distinct matrix without priority-target overlap may support future cross-target generality analysis, but it cannot be counted as same-target replication for the current responder states.
