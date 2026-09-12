# Replogle Essential Cross-target Generality Results

The denominator is the complete locked 16-target panel, including execution failures. The endpoints were fixed after the one-target pipeline pilot and before executing the remaining targets: PGAA-W target permutation p <= 0.05, PGAA-W target top 10%, PGAA-H target top 10%, and joint top-10% recovery.

| Endpoint | Success / locked | Fraction |
|---|---:|---:|
| `execution_complete` | 16/16 | 100.0% |
| `pgaa_w_significant_0_05` | 16/16 | 100.0% |
| `pgaa_w_top10pct` | 16/16 | 100.0% |
| `pgaa_h_top10pct` | 10/16 | 62.5% |
| `joint_top10pct` | 10/16 | 62.5% |

| Target | Status | W rank | W percentile | W p | H rank | H percentile | Joint top 10% |
|---|---|---:|---:|---:|---:|---:|---|
| `DERL2` | complete | 714 | 0.083 | 0.0004998 | 2 | 0.000 | True |
| `GMPS` | complete | 60 | 0.007 | 0.0004998 | 3167 | 0.370 | False |
| `RPLP1` | complete | 1 | 0.000 | 0.0004998 | 8413 | 0.982 | False |
| `VMP1` | complete | 657 | 0.077 | 0.01049 | 4304 | 0.503 | False |
| `DICER1` | complete | 273 | 0.032 | 0.0004998 | 1 | 0.000 | True |
| `HECTD1` | complete | 79 | 0.009 | 0.0004998 | 57 | 0.007 | True |
| `ILF3` | complete | 27 | 0.003 | 0.0004998 | 1236 | 0.144 | False |
| `RPUSD3` | complete | 185 | 0.022 | 0.0004998 | 1 | 0.000 | True |
| `CWC15` | complete | 338 | 0.039 | 0.0004998 | 31 | 0.004 | True |
| `EIF3D` | complete | 206 | 0.024 | 0.0004998 | 1703 | 0.199 | False |
| `UBA2` | complete | 98 | 0.011 | 0.0004998 | 841 | 0.098 | True |
| `USP5` | complete | 757 | 0.088 | 0.0004998 | 14 | 0.002 | True |
| `ABCF1` | complete | 81 | 0.009 | 0.0004998 | 697 | 0.081 | True |
| `BCAS2` | complete | 248 | 0.029 | 0.0004998 | 12 | 0.001 | True |
| `DNTTIP2` | complete | 213 | 0.025 | 0.0004998 | 26 | 0.003 | True |
| `LSM2` | complete | 136 | 0.016 | 0.0004998 | 4381 | 0.512 | False |

## Claim Boundary

These endpoints quantify target recovery across a locked panel within one K562 essential-gene Perturb-seq experiment. Targets share an experiment and a fixed control subsample, so target rows are not independent biological replicates. Results do not establish same-target cross-dataset replication, immune presentation, synthetic-peptide validation, or T-cell function.
