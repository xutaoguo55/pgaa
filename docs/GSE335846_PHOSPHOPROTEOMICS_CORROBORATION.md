# GSE335846 Companion Phosphoproteomics Corroboration

## Result

A companion Springernature phosphoproteomics workbook from the same osimertinib-tolerant persister study provides source-table-backed corroboration for the DTP logic. The workbook contains 1,006 quantified proteins and 3,142 unique phosphosites across DMSO, Osi_5min, Osi_10min, Osi_6h, DTP, DTP-24h, and DTP-7d.
In the selected protein panel, the DTP state suppresses canonical proliferation markers (CDK1, MCM2, MCM5, MKI67, PCNA, RB1) and leaves EGFR / RPA2 / CCND1 on the positive side of the selected panel (EGFR, RPA2, CCND1).
In the selected phosphosite panel, the DTP state shows source-backed changes in ATR-adjacent and replication-stress phosphosites, with negative DTP shifts for ATR_S435, EGFR_T693, CDK1_Y15, MCM2_S27, MKI67_S357, RB1_T821, SAMHD1_T592, YAP1_T361, CCNE1_S100 and positive DTP shifts for BAD_S99.
This workbook strengthens the dynamic DTP / replication-stress narrative, but the quick exact-gene scan does not surface ATM as a usable source-table row, so it remains corroboration rather than ATM source-table closure.

## Workbook summary

Source workbook: `/Users/guoxutao/.openclaw/workspace/PGAA_method_paper/sources/gse335846_dynamic_atm/source_ev1.xlsx`

| Sheet | Summary | Selected hits | Role |
|---|---|---:|---|
| Prot_IDs | 1,006 quantified proteins | 9 | protein-level corroboration |
| Phos_IDs | 3,142 unique phosphosites | 10 | phosphosite-level corroboration |

## Boundary scan

| Gene | Protein exact hits | Phosphosite exact hits | Status |
|---|---:|---:|---|
| ATM | 0 | 0 | no_exact_hit_in_quick_scan |
| ATR | 0 | 2 | exact_hit_in_phosphoproteome |

## Claim boundary

The workbook is useful because it is source-table-backed and it captures the same DTP / replication-stress logic that the manuscript uses for external corroboration. It is not a substitute for replicate-level ATM pharmacology source tables, and it does not change the current claim ceiling.
