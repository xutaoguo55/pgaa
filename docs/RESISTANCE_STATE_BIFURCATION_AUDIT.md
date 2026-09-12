# Stable Resistance-State Bifurcation Audit

## Positive Finding

PC9 and H4006 follow stable, opposing transcriptional resistance branches. A branch axis discovered only from drug-tolerant-cell contrasts reproduces in held-out expanded resistant cells.

- Genome-wide DTC-to-DTEC branch correlation: Spearman rho=0.741.
- All prespecified signature sizes pass: `True`.
- Minimum held-out gene-direction concordance: 0.992.

## Held-Out DTEC Validation

| Genes per branch | DTEC margin | Permutation p | Direction concordance | Gate |
|---:|---:|---:|---:|---|
| 25 | 6.432 | 0.0002 | 1.000 | pass |
| 50 | 6.560 | 0.0002 | 1.000 | pass |
| 100 | 6.526 | 0.0002 | 1.000 | pass |
| 200 | 6.458 | 0.0002 | 1.000 | pass |
| 500 | 6.276 | 0.0002 | 0.992 | pass |

## Biological Model

The PC9 branch is enriched for hormone-responsive, environmental-stress, and unfolded-protein-response programs. The H4006 branch is enriched for DNA replication, S phase, and double-strand-break repair. This supports a positive model in which EGFR-inhibitor resistance can stabilize through an adaptive-stress branch or a replication-maintaining branch rather than one universal expression direction.

The next value-adding experiment is prospective branch assignment in an independent cell line or patient-derived model, followed by branch-specific vulnerability testing.
