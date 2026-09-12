# Novelty and Prior-Art Audit

Date checked: 2026-07-22

## Bottom Line

The current Bioinformatics-first direction is **not already done as a single, directly overlapping method**, but several components are heavily occupied. The paper will be vulnerable if it claims novelty in perturbation effect testing, single-cell perturbation workflows, evidence tiers, or biomedical claim verification. The defensible novelty is narrower and stronger:

**PGAA is an executable claim-state compiler for perturbation transcriptomics: it converts score outputs, stability checks, external evidence, source provenance, and promotion gates into bounded manuscript claim states, with false-promotion and under-promotion as explicit method endpoints.**

## What Is Not Novel

| Area | Existing work | Consequence |
|---|---|---|
| Calibrated single-cell CRISPR association testing | SCEPTRE and SCEPTRE low-MOI already focus on calibrated association testing, power, and false-positive control. | Do not claim PGAA is the main advance in calibrated perturbation-gene testing. |
| Single-cell perturbation analysis frameworks | pertpy, scPerturb, Mixscape, and Augur already cover harmonized perturbation resources, perturbation distances, response prioritization, perturbation signatures, and workflow infrastructure. | Do not position PGAA as a general perturbation-analysis toolkit. |
| Evidence levels and evidence grading | CIViC, ACMG/AMP, and OncoKB already formalize evidence categories and clinical/preclinical/inferential interpretation layers. | Do not claim evidence tiering itself is new. |
| Scientific claim verification | SciFact/CliVER-style and biomedical claim-verification systems already retrieve evidence and judge natural-language claim support. | Do not claim PGAA invented scientific claim verification. |
| Perturbation benchmarking | CausalBench, PerturBench, scPerturb, and recent single-cell perturbation benchmarks already establish benchmark datasets and performance metrics. | Do not claim benchmark standardization alone is new. |

## What Still Looks Novel Enough

| Candidate novelty | Current strength | Why it appears distinguishable |
|---|---|---|
| Executable claim-state compiler for perturbation transcriptomics | Strongest | Existing perturbation tools produce scores, associations, distances, predictions, or workflows; they generally do not compile those outputs into auditable manuscript claim ceilings. |
| False-promotion benchmark as a method endpoint | Strong | Prior perturbation benchmarks emphasize calibration, prediction, recovery, or distance metrics; the explicit endpoint here is whether a reporting method promotes claims above the evidence ceiling. |
| Multi-gate manuscript permission system | Moderate-to-strong | Evidence grading exists in clinical variant interpretation, but the PGAA object is an executable gate over perturbation/transcriptomic analysis outputs, stability, external evidence, source provenance, and branch-vulnerability promotion. |
| Branch-vulnerability use case with bounded claim ceiling | Moderate | EGFR-resistance/ATM biology is not enough as novelty by itself, but it is a useful biological demonstration of the compiler because it shows a positive hypothesis without overclaiming pharmacology. |

## Closest Prior-Art Classes Checked

| Prior-art class | Representative sources checked | Relevance to PGAA |
|---|---|---|
| Single-cell CRISPR association testing | SCEPTRE 2021; SCEPTRE low-MOI 2024 | Closest if PGAA is framed as perturbation testing. These papers own calibration/power/false-positive association testing. |
| Perturbation workflow/resource frameworks | pertpy; scPerturb; Mixscape; Augur | Closest if PGAA is framed as a broad perturbation workflow. These tools already cover much of that surface. |
| Scientific/biomedical claim verification | CliVER; SciClaims; MedRAGChecker; graph-based claim verification | Conceptually adjacent, but mostly NLP/literature verification rather than transcriptomic evidence-state compilation. |
| Clinical evidence tier systems | CIViC evidence levels; ACMG/AMP; OncoKB | Conceptual precedent for evidence levels and claim ceilings. This reduces novelty if PGAA claims evidence grading broadly. |
| Perturbation prediction/benchmark suites | CausalBench; PerturBench; scPerturb | Adjacent around benchmarking, but endpoints differ from claim-promotion correctness. |

## Novelty Risk Rating

| Claim | Risk | Verdict |
|---|---|---|
| PGAA is a new perturbation association test | Very high | Do not claim. |
| PGAA is a new single-cell perturbation analysis framework | High | Too broad; likely overlaps with pertpy/scPerturb/Mixscape/Augur. |
| PGAA introduces evidence levels for biomedical claims | High | Already covered by CIViC/ACMG-style frameworks. |
| PGAA verifies scientific claims from literature | High | Already covered by scientific claim-verification/NLP literature. |
| PGAA compiles perturbation-transcriptomic evidence into executable manuscript claim states | Moderate-to-low | Best defensible novelty lane. |
| PGAA quantifies false claim promotion as a method endpoint | Moderate-to-low | Good Bioinformatics-facing methodological angle if formalized and benchmarked. |
| PGAA identifies ATM branch-specific vulnerability | Moderate | Useful demonstration, not standalone method novelty. |

## Required Repositioning

1. The title and abstract must lead with **claim-state compilation**, not PGAA ranking, ATM, or EGFR resistance.
2. Related Work must explicitly say SCEPTRE/Mixscape/pertpy/scPerturb solve upstream perturbation analysis; PGAA solves downstream claim permission.
3. CIViC/ACMG/OncoKB must be cited as evidence-tier precedents, not competitors.
4. Scientific claim-verification systems must be cited as NLP/literature-verification precedents; PGAA is different because it operates on structured analysis artifacts.
5. Figure 2 must make false-promotion and under-promotion quantitative, otherwise the method novelty may look like editorial bookkeeping.
6. ATM must remain a bounded biological use case after the method benchmark, not the opening claim.

## Search Notes

Targeted web searches were run for exact and adjacent phrases including `claim-state compiler perturbation transcriptomics`, `unsupported claim promotion bioinformatics benchmark`, `scientific claim verification biomedical evidence graph`, `Perturb-seq analysis method benchmark SCEPTRE Mixscape`, `scPerturb pertpy perturbation framework`, and `CIViC evidence level genomic claims`.

No direct prior work was found that combines perturbation-transcriptomic score outputs, reproducibility/source provenance, external validation gates, branch-vulnerability promotion gates, and manuscript claim ceilings into a single executable compiler. This is a targeted novelty audit, not a full systematic review.
