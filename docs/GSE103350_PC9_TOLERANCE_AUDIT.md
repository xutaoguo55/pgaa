# GSE103350 PC9 Tolerance Audit

Date: 2026-08-03

## Purpose

This audit records why `GSE103350` is informative but still insufficient to close the manuscript's remaining third independent PC9 evolution-system gap.

## Data Source

`GSE103350` is a real local supplementary package with raw-count tables for:

- `raw_count_tolerance`
- `raw_count_MIR21`
- `raw_count_MIR149B`

The `read_summary` sheet includes PC9 parental, gefitinib-treated PC9, osimertinib-treated PC9, and HCC827 control/treatment states.

## Frozen-axis summary

The current route uses the frozen contrast:

- adaptive branch: `PC9_adaptive_stress`
- reference branch: `H4006_replication`

Using the top 50 genes from each branch and a log1p mean-difference axis, all `GSE103350` samples remain on the negative side of the frozen axis.

### `raw_count_tolerance`

| Sample | Axis |
|---|---:|
| `VEH_PC9_parental` | `-1.9122` |
| `GEF_PC9_G01` | `-0.5463` |
| `AZD_PC9_A01` | `-0.4377` |
| `VEH_HCC827` | `-1.0792` |
| `GEF_HCC827` | `-0.3762` |
| `AZD_HCC827` | `-0.3808` |

### `raw_count_MIR21`

| Sample | Axis |
|---|---:|
| `Ctrl_PC9` | `-1.5419` |
| `MIR21_PC9` | `-1.5202` |
| `Antictrl_PC9ER` | `-1.1946` |
| `AntiMIR21_PC9ER` | `-1.4085` |
| `Ctrl_HCC827` | `-0.8772` |
| `MIR21_HCC827` | `-0.8081` |
| `Antictrl_H1975` | `-1.5039` |
| `AntiMIR21_H1975` | `-1.6713` |
| `Scr_AALE` | `-2.0394` |
| `MIR21_AALE` | `-2.0367` |

### `raw_count_MIR149B`

The same qualitative pattern holds: the values remain negative on the frozen axis.

## Interpretation

`GSE103350` supports the idea that EGFR-TKI perturbation moves PC9/HCC827-related states toward the adaptive side of the axis, but it does not cross or stabilize the locked third-system route.

That means this dataset is:

- useful as a partial reinforcement of the branch-axis story;
- not sufficient as a clean third independent PC9 evolution system;
- best treated as a negative or mixed candidate unless the route definition is changed.

## Manuscript use

This dataset should not be counted as direct closure evidence for the current manuscript. It can only be cited as an evaluated local candidate that fails to meet the frozen-axis contract.
