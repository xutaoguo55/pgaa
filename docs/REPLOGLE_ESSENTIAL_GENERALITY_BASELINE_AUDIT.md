# Replogle Essential Generality Baseline Audit

This is a post-pilot exploratory comparator audit. Absolute mean shift and absolute Welch t-statistic were added after the locked panel run to test whether direct target recovery alone distinguishes PGAA from conventional summaries; they are not preregistered primary endpoints.

| Metric | Targets / locked | Fraction |
|---|---:|---:|
| `pgaa_w_top10pct` | 16/16 | 100.0% |
| `pgaa_h_top10pct` | 10/16 | 62.5% |
| `absolute_mean_shift_top10pct` | 16/16 | 100.0% |
| `welch_abs_t_top10pct` | 16/16 | 100.0% |
| `pgaa_w_beats_both_baselines` | 1/16 | 6.2% |
| `pgaa_h_beats_both_baselines` | 2/16 | 12.5% |

| Target | W pct | H pct | Mean-shift pct | Welch pct | W beats both | H beats both |
|---|---:|---:|---:|---:|---|---|
| `DERL2` | 0.083 | 0.000 | 0.064 | 0.000 | False | False |
| `GMPS` | 0.007 | 0.370 | 0.006 | 0.000 | False | False |
| `RPLP1` | 0.000 | 0.982 | 0.000 | 0.000 | True | False |
| `VMP1` | 0.077 | 0.503 | 0.058 | 0.004 | False | False |
| `DICER1` | 0.032 | 0.000 | 0.030 | 0.000 | False | True |
| `HECTD1` | 0.009 | 0.007 | 0.006 | 0.000 | False | False |
| `ILF3` | 0.003 | 0.144 | 0.002 | 0.000 | False | False |
| `RPUSD3` | 0.022 | 0.000 | 0.019 | 0.000 | False | True |
| `CWC15` | 0.039 | 0.004 | 0.038 | 0.000 | False | False |
| `EIF3D` | 0.024 | 0.199 | 0.022 | 0.000 | False | False |
| `UBA2` | 0.011 | 0.098 | 0.012 | 0.000 | False | False |
| `USP5` | 0.088 | 0.002 | 0.067 | 0.000 | False | False |
| `ABCF1` | 0.009 | 0.081 | 0.008 | 0.000 | False | False |
| `BCAS2` | 0.029 | 0.001 | 0.027 | 0.000 | False | False |
| `DNTTIP2` | 0.025 | 0.003 | 0.024 | 0.000 | False | False |
| `LSM2` | 0.016 | 0.512 | 0.015 | 0.000 | False | False |

## Interpretation Boundary

A high target-recovery rate shared by simple baselines demonstrates assay signal, not PGAA superiority. Method-specific value requires better ranks, complementary recovery, calibration, or claim-control behavior beyond these baselines. This audit uses one experiment and cannot establish independent biological replication.
