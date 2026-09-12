# GSE112274 Matched Event-Expression Audit

Verdict: `READY_MATCHED_EVENT_EXPRESSION_ASSOCIATION_PILOT`

## Imported Evidence

- Same-cell PC-9 expression and EGFR T790M allele fractions: 507 cells.
- Locked comparison: 156 event-high versus 274 event-low cells.
- Excluded before analysis: 77 transition and 0 low-depth cells.
- CLI matrix: 5000 genes after `log1p_FPKM` and the recorded variance filter.

## Claim Boundary

This is a matched event-expression association test from observational same-cell data. It is not a perturbation experiment, causal replication, antigen-presentation assay, or T-cell validation. HLA and peptide evidence must remain separate annotations.

The manuscript mainline remains the claim-state compiler. This pilot may test whether the compiler can ingest a real event-linked expression state without promoting an immune claim.
