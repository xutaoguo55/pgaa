# EGFR T790M Cross-System Replication Audit

Verdict: `CROSS_SYSTEM_NOT_REPLICATED_DIRECTION_DISCORDANT_UNDERPOWERED`

## Results

- GSE112274 same-cell pilot: EGFR mean log1p(FPKM) was 6.8168 in T790M-high and 7.6059 in T790M-low cells (high-minus-low -0.7891).
- GSE129221 clone-level stress test: EGFR mean log1p(FPKM) was 4.4284 in T790M-positive PC9GR and 4.1601 in T790M-negative parental PC9 (positive-minus-negative 0.2683; raw FPKM fold change 1.314).
- Exact label permutations across the six clone-level replicates gave one-sided directional p=0.050 and Wasserstein p=0.100.
- The direction is discordant between systems, and the clone-level distribution test does not pass 0.05.

## Claim Boundary

GSE129221 is an independent acquired-resistance model with matched clone-level genotype and expression, not same-cell DNA plus RNA. T790M status is confounded with the evolved PC9GR clone and prolonged gefitinib exposure. The result therefore falsifies a simple directionally invariant EGFR-expression interpretation but cannot falsify every distributional T790M effect.

The claim-state compiler must retain this as a failed or unresolved cross-system replication state. It does not support causal, immune, antigen-presentation, or T-cell claims.
