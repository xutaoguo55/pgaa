# PGAA immune-evidence claim rewrite guide

## Purpose

Use this guide when revising any antigen, peptide, HLA, or T-cell language in the manuscript after the no-wet-lab rescue analysis. The goal is to raise rigor without implying validation that was not performed.

## Claim levels

| Evidence status | Do write | Do not write |
|---|---|---|
| PGAA score only | PGAA prioritized event-derived candidates for immune-evidence follow-up. | PGAA identified validated antigens. |
| Binding predictor only | The peptide was predicted to be HLA-compatible. | The peptide is presented by HLA. |
| Public ligand match | Public ligand resources support presentation of the same peptide or event region. | We confirmed peptide presentation. |
| Synthesis-ready triage | The peptide is suitable for future synthesis and immune testing. | Synthetic peptide validation confirmed the candidate. |
| Public T-cell response | Public evidence supports T-cell recognition of this peptide-HLA pair. | We demonstrated T-cell activation. |
| Immune-context only | The candidate occurs in an immune-active context. | The peptide is immunogenic. |

## Abstract-safe wording

If the evidence ladder is completed but no wet-lab validation is added:

> We further introduce a failure-preserving immune-evidence ladder that maps PGAA-ranked event-derived peptides to public ligand evidence, HLA-compatibility predictions, synthesis-readiness features, and public T-cell recognition evidence. This analysis prioritizes candidates for experimental follow-up and explicitly labels missing presentation or T-cell support; it does not constitute de novo peptide or T-cell validation.

If public exact peptide/T-cell matches are absent:

> Most candidates lacked exact public immunopeptidome or T-cell response evidence, indicating that PGAA should currently be interpreted as a prioritization framework rather than a validated antigen-discovery assay.

## Results-section structure

Recommended subsection title:

**A public-evidence ladder prioritizes event-derived immune candidates while preserving missing validation layers**

Recommended paragraph order:

1. State why gene-level PGAA hits were converted into event-peptide-HLA units.
2. Report the number of candidate units and decoys.
3. Report exact presentation evidence first, then overlap evidence, then binding-only evidence.
4. Report synthesis-readiness categories.
5. Report exact T-cell evidence first, then region/source/context support.
6. Report integrated Tier A-D counts.
7. End with limitations: no new immunopeptidomics, synthetic peptide, or T-cell functional experiment was performed.

## Figure/table plan

| Item | Content | Reviewer purpose |
|---|---|---|
| Main Figure panel | Evidence heatmap for top candidates across presentation, binding, synthesis, and T-cell layers | Shows the workflow is candidate-specific, not gene-level storytelling |
| Main Figure panel | Candidate-vs-decoy match-rate comparison | Controls against public-database coincidence |
| Supplementary Table | Full `candidate_event_peptides.tsv` | Makes peptide/HLA/event definitions auditable |
| Supplementary Table | Full `immune_evidence_tiers.tsv` | Makes tier assignment reproducible |
| Supplementary Note | Query rules, exact/overlap definitions, and failed candidates | Prevents selective reporting concerns |

## Journal-fit interpretation after rescue

No-wet-lab completion can improve the paper from a software/statistical-method story to a computational immunology prioritization story only if the analysis is strict and negative results are retained.

| Final evidence pattern | Fit interpretation |
|---|---|
| Mostly PGAA-only with weak immune evidence | Keep as software/statistical method; avoid immunology-heavy journal framing. |
| Clear public ligand enrichment over decoys but little T-cell evidence | Bioinformatics, computational biology, or translational informatics framing is plausible. |
| Multiple same-event ligand matches plus public T-cell recognition | Computational immunology framing becomes stronger, but still not equivalent to papers with new assays. |
| No public ligand or T-cell evidence after audit | Strong honesty, but lower novelty; position as method plus negative validation audit. |

## Reviewer-risk checklist

- Does every use of "presented" require ligand evidence rather than only binding prediction?
- Does every use of "immunogenic" require exact peptide-level T-cell response evidence?
- Are synthetic-peptide statements phrased as readiness, not validation?
- Are unmatched and negative candidates reported?
- Are decoy/background match rates shown?
- Are public-database matches separated into exact, overlap, source-protein, and context-only evidence?
- Is the final claim still true if all wet-lab-related words are interpreted literally?

