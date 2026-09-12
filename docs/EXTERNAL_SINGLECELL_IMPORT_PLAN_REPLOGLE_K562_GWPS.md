# PGAA External Single-Cell Import Plan

This report plans import of external single-cell matrices after target/control metadata has been verified. It is not replication evidence; replication requires a completed import and a rerun of PGAA/comparator claim-state gates.

## Summary

| Target/control gate | Import status | Preferred | Allowed use | Files |
|---|---|---:|---|---:|
| passed | not_singlecell_matrix | False | import_planning_not_replication | 1 |
| passed | secondary_singlecell_option | False | import_planning_not_replication | 1 |
| passed | download_allowed_with_scratch_margin | True | import_planning_not_replication | 1 |

## File-Level Plan

| File | Role | Size GiB | Available GiB | Required GiB | Status | Next action |
|---|---|---:|---:|---:|---|---|
| K562_gwps_raw_singlecell_01.h5ad | raw_singlecell | 61.31 | 295.16 | 76.64 | download_allowed_with_scratch_margin | Download to scratch outside the repository, verify the h5ad opens, then run the external PGAA gate. |
| K562_gwps_normalized_singlecell_01.h5ad | normalized_singlecell | 61.31 | 295.16 | 76.64 | secondary_singlecell_option | Keep as an alternate only; prioritize the preferred raw single-cell matrix. |
| K562_gwps_raw_bulk_01.h5ad | raw_pseudobulk | 0.35 | 295.16 | 0.44 | not_singlecell_matrix | Do not use this file as the primary PGAA distributional replication matrix. |

## Gate

Do not download large h5ad files into the repository. If current scratch space lacks margin, use external storage or cloud scratch, then run the external PGAA/comparator gate from the downloaded single-cell h5ad.
