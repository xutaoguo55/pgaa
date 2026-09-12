# Immune Evidence Claim Audit

## Summary

- Total candidates: 5830
- Presented candidates: 2077
- Exact public ligand matches: 603
- Overlap public ligand matches: 1474
- Peptide/region T-cell evidence: 4000
- Mean candidate match rate: 1.000
- Mean decoy match rate: 1.000
- Decoy enrichment gate: failed_candidate_not_above_decoy

## Tier Counts

- Tier A: 225
- Tier B: 1813
- Tier C: 0
- Tier D: 3792

## Allowed Headline Claim

Public immune-evidence enrichment is not supported because the candidate match rate does not exceed the matched-decoy rate; retain the event-peptide results as a domain-transfer sensitivity analysis.

## Prohibited Phrases

- validated antigen
- experimentally confirmed presentation
- demonstrated T-cell activation
- therapeutic target validated by this study

## Frequent Missing Evidence Flags

- no_public_ligand;weak_or_missing_binding_prediction: 3373
- weak_or_missing_binding_prediction;no_tcell_function: 1801
- weak_or_missing_binding_prediction: 225
- no_public_ligand;weak_or_missing_binding_prediction;synthesis-caution: 191
- no_public_ligand;weak_or_missing_binding_prediction;synthesis-risk: 189
- weak_or_missing_binding_prediction;synthesis-risk;no_tcell_function: 23
- weak_or_missing_binding_prediction;synthesis-risk: 16
- weak_or_missing_binding_prediction;synthesis-caution: 6

## Claim Boundary

This report audits public evidence and assay-readiness only. It does not provide new wet-lab immunopeptidome evidence, synthetic peptide assay results, or T-cell functional validation.
