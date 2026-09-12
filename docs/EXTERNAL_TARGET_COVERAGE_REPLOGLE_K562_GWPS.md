# PGAA External Target-Coverage Audit

This report verifies target coverage and control metadata in a candidate external h5ad file. It is not replication evidence: replication requires importing the matrix, rerunning PGAA and comparator gates, and obtaining a matching external claim state.

## Summary

| Target coverage | Control metadata | Import status | Allowed use | Targets |
|---|---|---|---|---:|
| verified_present | verified_controls_present | target_verified_pseudobulk_singlecell_required | target_coverage_verified_not_replication | 5 |

## Target-Level Evidence

| Target | Candidate dataset | Source file | Matching obs rows | Controls | Import status |
|---|---|---|---:|---:|---|
| BHLHE40 | replogle_2022_k562_gwps | K562_gwps_raw_bulk_01.h5ad | 2 | 1099 | target_verified_pseudobulk_singlecell_required |
| CREB1 | replogle_2022_k562_gwps | K562_gwps_raw_bulk_01.h5ad | 1 | 1099 | target_verified_pseudobulk_singlecell_required |
| DDIT3 | replogle_2022_k562_gwps | K562_gwps_raw_bulk_01.h5ad | 1 | 1099 | target_verified_pseudobulk_singlecell_required |
| ZNF326 | replogle_2022_k562_gwps | K562_gwps_raw_bulk_01.h5ad | 1 | 1099 | target_verified_pseudobulk_singlecell_required |
| SPI1 | replogle_2022_k562_gwps | K562_gwps_raw_bulk_01.h5ad | 1 | 1099 | target_verified_pseudobulk_singlecell_required |

## Next Action

Use the verified h5ad metadata as target-coverage evidence. For a PGAA distributional replication, import the matching single-cell matrix and rerun the PGAA/comparator claim-state gates. The manuscript claim ceiling should remain unchanged until the external PGAA/comparator rerun produces audited claim-state rows.
