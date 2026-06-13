# Communications Medicine Transfer Requirements Audit

Date: 2026-06-13

## Official Scope

Communications Medicine publishes clinical, translational, and public health research. Its aims and scope state that primary research should represent a significant advance in preventing, diagnosing, or treating human disease, and that the journal covers translational research integrating biomarkers, molecular data, non-clinical data, clinical data, and clinical outcomes. The scope also includes intersections of medicine with computational science when the central advance is of interest to the medical community, and explicitly includes new methods, technologies, or resources of significant translational or clinical relevance.

Sources checked:

- https://www.nature.com/commsmed/aims
- https://www.nature.com/commsmed/submit/content-types
- https://www.nature.com/commsmed/submit/guide-to-authors
- https://www.nature.com/commsmed/submit/submission-guidelines

## Article Type

Target type: Article.

Rationale: Communications Medicine Articles are original research studies of high quality and interest to a specific research community. PGAA is not a Review, Perspective, or Comment. It is best framed as a computational method/resource with translational relevance to single-cell disease perturbation analysis.

## Required Reframing for PGAA

The Bioinformatics version framed PGAA primarily as a Perturb-seq software/methods paper. The Communications Medicine transfer version reframes the same evidence around a medical problem: single-cell disease studies and perturbation screens often contain heterogeneous responder-associated transcriptional responses that mean-focused analysis may under-rank.

Changes made in `MANUSCRIPT_CM.md`:

- Title changed from a Bioinformatics-style software title to a disease-relevant single-cell perturbation title.
- Abstract now starts from heterogeneous disease-relevant responses and target-prioritization needs rather than from the algorithm alone.
- Introduction now foregrounds oncology, immunology, infection, inflammatory disease, patient-derived scRNA-seq, and translational perturbation response.
- Observational CLL, sepsis, RA, IBD, and PBMC datasets are described as disease-relevant marker-recovery contexts, not causal perturbation validation.
- Norman and Adamson are retained as experimental Perturb-seq benchmarks.
- Discussion now states that observational datasets do not establish new causal mechanisms or clinical biomarkers, but show how PGAA prioritizes disease-relevant heterogeneous responses for follow-up.
- Figure 1 is now a clinical/translational entry schematic rather than a methods-only benchmark figure.

## Fit Assessment

Current fit after reframing: moderate.

Strengths:

- The method addresses a real translational single-cell analysis problem: heterogeneous cellular response.
- Disease-relevant public datasets are included, especially CLL, sepsis, RA, and IBD.
- Two real Perturb-seq benchmarks remain as technical validation.
- Software, tests, source data, reproducibility scripts, and supplementary archive exist.
- Nature Methods editor-recommended transfer should be mentioned in the cover letter.

Residual risks:

- The manuscript is still primarily computational and does not report a new validated clinical biomarker, therapy, or disease mechanism.
- CLL/sepsis/RA/IBD analyses are observational marker recovery, not experimental perturbation or clinical-outcome validation.
- The most distinctive persistence result remains a focused Norman CEBPE/ELANE ranking signal.
- Persistent homology calibration remains sensitive to histogram bin count and perturbation context.
- Public repository and permanent archive DOI are still not finalized.

## Submission Blockers

Hard blocker before final upload:

- Make `https://github.com/xutaoguo55/pgaa` publicly reachable or replace with a final accessible repository URL.
- Archive the exact submitted software version with Zenodo, Figshare, Software Heritage, or Code Ocean.
- Replace repository/DOI placeholders in manuscript, cover letter, and portal text.

Author-level final checks:

- Confirm whether the transfer will use the Nature Portfolio transfer link and whether previous reviewer/editor materials will be transferred.
- Confirm open peer-review preference if the portal asks.
- Confirm author metadata, ORCID, funding, conflict-of-interest, and reviewer suggestions/exclusions.

## Current Recommendation

Proceed with a Communications Medicine transfer only using the CM-specific manuscript and cover letter, not the original Bioinformatics version. The transfer is defensible because Communications Medicine explicitly considers methods, technologies, and resources with significant translational or clinical relevance, but the cover letter must clearly explain why PGAA matters to disease-focused single-cell perturbation studies.
