# GSE335846 External Dynamic Corroboration Support Text

Supplementary Figure S5 summarizes the fifth-system evidence in three bounded panels. Panel A keeps the dynamic DTP time-course at figure-digitized rank level, while Panels B and C show the source-table-backed RNA-seq branch-axis projection and the associated marker shifts. The linked preprint's data-availability statement points to GEO accession GSE335848, but the accession viewer does not expose supplementary data files, so the dynamic drug-response source tables are still not public.

## Supplementary Figure S5

Supplementary Figure S5. GSE335846 dynamic corroboration scorecard. (A) The linked preprint reports a monotonic increase in replication-branch strength from day 0 to day 28 and a larger ATM added benefit at the late DTP time point. (B) The public GSE335846 RNA-seq source table projects onto the frozen branch axis without re-ranking genes; the sample-level source-axis contrast shifts from a negative day-0 mean toward a less negative day-28 mean. (C) The same source table shows concordant marker shifts, including positive ATM and EGFR movement and negative proliferation/replication markers such as MKI67, MCM2, MCM5, PCNA, RAD51, RPA2, and CDK1. The figure therefore strengthens dynamic corroboration while preserving the public source ceiling.

## Evidence Summary

### Dynamic Time Course

| Day | Replication-branch strength | ATM added benefit | Osimertinib confluence | +AZD1390 confluence |
|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.0 | 72.0 | 72.0 |
| 7 | 0.333 | 7.0 | 42.0 | 35.0 |
| 14 | 0.476 | 8.0 | 32.0 | 24.0 |
| 28 | 0.643 | 32.0 | 55.0 | 23.0 |

Spearman rho = 1.000; one-sided exact permutation p = 0.0417; n = 4 time points.

### Source-Axis Projection

| Day | Samples | Mean source-axis contrast | Min | Max |
|---:|---:|---:|---:|---:|
| 0 | 5 | -1.971 | -2.175 | -1.661 |
| 28 | 4 | -0.393 | -1.212 | 0.355 |

### Marker Shifts

| Feature | Day 0 mean | Day 28 mean | Delta (28 - 0) |
|---|---:|---:|---:|
| EGFR | 12.184 | 13.667 | +1.483 |
| ATM | 8.277 | 9.594 | +1.316 |
| CDKN1A | 8.080 | 8.237 | +0.157 |
| CCND1 | 11.549 | 10.830 | -0.719 |
| E2F1 | 11.049 | 10.097 | -0.953 |
| HDAC1 | 13.371 | 12.227 | -1.144 |
| RPA2 | 10.913 | 9.592 | -1.322 |
| RAD51 | 9.586 | 8.002 | -1.584 |
| PCNA | 15.269 | 13.332 | -1.937 |
| MKI67 | 13.581 | 11.371 | -2.210 |
| CDK1 | 13.423 | 11.159 | -2.265 |
| MCM5 | 11.293 | 8.612 | -2.681 |
| MCM2 | 10.571 | 7.675 | -2.896 |

Representative upward-shifted markers: EGFR, ATM, CDKN1A.
Representative downward-shifted markers: MCM2, MCM5, CDK1.

## Boundary

This figure is a corroboration layer, not a source-table-level pharmacology result. The dynamic branch-strength and ATM-benefit values remain figure-digitized; only the RNA-seq branch-axis projection and marker shifts are source-table backed. The figure is therefore useful for reviewer-facing explanation, but it does not close the replicate-level source-table gap on its own.
