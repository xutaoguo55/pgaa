# Communications AI & Computing Portal Inputs

## Article Type

Article

## Title

PGAA: distribution-aware ranking of heterogeneous single-cell perturbation responses

## Short Title

Distribution-aware perturbation prioritization

## Corresponding Author

Xutao Guo

Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China

Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China

Email: guoxutao@smu.edu.cn

## Abstract

Single-cell perturbation screens often produce subset-confined responses that are poorly captured by mean-shift tests. We present PGAA, a distribution-aware ranking method for heterogeneous single-cell perturbation responses. PGAA provides two statistics: PGAA-W, a 99-point quantile-grid Wasserstein approximation for full-distribution shifts, and PGAA-H, an exploratory histogram-shape diagnostic for responder-associated expression changes—both with shared permutation calibration and Storey upper-tail diagnostics. In a proof-of-principle unfolded-protein-response CRISPRi benchmark (5 perturbations, 13 positives), PGAA-W achieved mean AUROC 0.786 and mean AUPRC 0.0191 (random baseline 0.0065). A Norman 2019 multi-perturbation CRISPRa extension supported PGAA-W as the recommended starting statistic in curated target-panel checks. PGAA-H showed limited demonstrated utility: ELANE ranked 57/2012 as ranking evidence in one CEBPE CRISPRa example, and one perturbation (BHLHE40) showed per-perturbation AUROC 0.833 in the Adamson benchmark. Systematic comparison against other distributional tests (KS, energy distance) is not performed and is a key limitation. PGAA is implemented in Python and R, with public code, a reproducibility archive, and a CLI.

## Keywords

single-cell RNA-seq; Perturb-seq; computational biology; Wasserstein distance; histogram-shape statistic; distributional ranking; CRISPR screening

## Data Availability

Norman 2019: GSE133344. Adamson 2016: GSE90546. CLL: GSE111014. Sepsis: GSE167363. RA: GSE159117. IBD: GSE116222. PBMC: 10x Genomics 3k demo.

## Code Availability

Public code-only repository: https://github.com/xutaoguo55/pgaa. GitHub release: https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code. Zenodo DOI: https://doi.org/10.5281/zenodo.20681141. Software Heritage archive SWHID: swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f. Manuscript-specific source-data tables, figure-reproduction scripts, runtime documentation, and PDF build files are provided in the submitted supplementary software archive rather than in the public code-only repository.

## Journal Fit Note

The manuscript emphasizes the computational framework, benchmarking, calibration diagnostics, software implementation, and reproducibility package. The disease-related observational datasets are presented as marker-recovery stress checks rather than causal disease validation or clinical biomarker evidence.

## Competing Interests

The authors declare no competing interests.

## Funding

No external funding was received for this work.

## Ethics Statement

This study re-analyzes publicly available and previously published datasets. No new human participants, human samples, animals, or identifiable private information were collected for this study. Ethics approval and participant consent were handled by the original studies.

## Author Contributions

X.W., H.Z., and J.H. contributed equally. X.G. conceived the study and designed the framework. X.W., H.Z., and J.H. implemented the software and performed the analyses. Q.W., Y.W., and R.F. contributed to data collection and biological interpretation. All authors wrote and approved the manuscript.

## Open Peer Review Preference

OPT IN to Transparent Peer Review / publication of reviewer reports if the manuscript is accepted.
