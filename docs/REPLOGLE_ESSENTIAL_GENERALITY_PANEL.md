# Replogle Essential Cross-target Generality Panel

This panel was selected from metadata only in backed, read-only mode. No expression result or PGAA score was used for target selection, and the source h5ad was not copied, modified, or deleted.

- Source: `/Volumes/MOVESPEED/claude code大电脑备份data/data/data/replogle_2022_k562_essential.h5ad`
- Shape: 310385 cells x 8563 features
- Excluded current targets: BHLHE40, CEBPA, CEBPE, CREB1, DDIT3, KLF1, SPI1, ZNF326
- Eligibility: target gene measured and at least 100 target cells
- Eligible targets: 1164; locked panel: 16
- Selection: four abundance strata; four targets per stratum; deterministic SHA-256 ordering with seed `pgaa-generality-v1`

| Stratum | Target | Target cells | Target batches | Control cells | Control batches |
|---|---|---:|---:|---:|---:|
| `Q1` | `DERL2` | 124 | 42 | 10691 | 48 |
| `Q1` | `GMPS` | 123 | 44 | 10691 | 48 |
| `Q1` | `RPLP1` | 117 | 44 | 10691 | 48 |
| `Q1` | `VMP1` | 106 | 42 | 10691 | 48 |
| `Q2` | `DICER1` | 158 | 46 | 10691 | 48 |
| `Q2` | `HECTD1` | 130 | 45 | 10691 | 48 |
| `Q2` | `ILF3` | 138 | 47 | 10691 | 48 |
| `Q2` | `RPUSD3` | 164 | 45 | 10691 | 48 |
| `Q3` | `CWC15` | 184 | 48 | 10691 | 48 |
| `Q3` | `EIF3D` | 186 | 47 | 10691 | 48 |
| `Q3` | `UBA2` | 172 | 47 | 10691 | 48 |
| `Q3` | `USP5` | 199 | 48 | 10691 | 48 |
| `Q4` | `ABCF1` | 329 | 48 | 10691 | 48 |
| `Q4` | `BCAS2` | 227 | 46 | 10691 | 48 |
| `Q4` | `DNTTIP2` | 264 | 48 | 10691 | 48 |
| `Q4` | `LSM2` | 357 | 48 | 10691 | 48 |

## Claim Boundary

This panel can test cross-target computational generality within the Replogle K562 essential-gene experiment. It is not a second biological source, does not replicate the existing responder states for the current targets, and cannot support wet-lab, immunopeptidomic, synthetic-peptide, or T-cell functional claims.

Panel membership is locked before expression extraction. Targets must remain in the denominator after execution failures; failed targets may not be silently replaced.
