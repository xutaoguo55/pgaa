# PGAA External Rerun Readiness Gate

This report is a preflight gate for an external single-cell PGAA/comparator rerun. It is not replication evidence; replication requires a completed PGAA/comparator rerun and an audited external claim-state table.

## Summary

| Gate status | Target/control gate | Allowed use | Rows |
|---|---|---|---:|
| ready_for_external_claim_state_rerun | passed | rerun_readiness_not_replication | 1 |

## File Check

| Dataset | h5ad | Exists | Read status | Matrix level | n_obs | n_vars |
|---|---|---:|---|---|---:|---:|
| replogle_2022_k562_gwps | K562_gwps_raw_singlecell_01.h5ad | True | readable | single_cell_h5ad | 1989578 | 8248 |

## Metadata Check

| Required targets | Found targets | Missing targets | Control rows | Label columns checked |
|---|---|---|---:|---|
| BHLHE40;CREB1;DDIT3;ZNF326 | BHLHE40;CREB1;DDIT3;ZNF326 |  | 75328 | obs_names;gene;gene_id;transcript;gene_transcript;sgID_AB |

## Next Action

Run PGAA/comparator external claim-state and stability workflows from this h5ad; only then consider a replication claim.

The manuscript claim ceiling must remain unchanged until this gate reaches `ready_for_external_claim_state_rerun` and the downstream PGAA/comparator rerun produces external claim-state evidence.
