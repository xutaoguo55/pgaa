# Communications Medicine Portal Inputs

## Article Type

Article

## Title

A distribution-aware framework for prioritizing heterogeneous disease-relevant responses in single-cell perturbation data

## Short Title

Distribution-aware perturbation prioritization

## Corresponding Author

Xutao Guo

Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China

Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China

Email: guoxutao@smu.edu.cn

## Abstract

Patient-derived single-cell datasets and disease-model perturbation screens often contain responder states that are confined to a subset of cells, making target-prioritization difficult when analyses focus only on average expression changes. We present PGAA, a distribution-aware framework for prioritizing heterogeneous transcriptional responses in single-cell perturbation data and marker-anchored disease-state contrasts. PGAA combines a Wasserstein statistic for full-expression-distribution shifts with a persistent-homology statistic for responder-associated expression-shape changes, both accompanied by permutation calibration and Storey pi0-hat diagnostics. Across five disease-relevant observational scRNA-seq datasets, Wasserstein recovered known pathway markers with 2.1-5.8x top-100 enrichment, including B-cell receptor signaling in chronic lymphocytic leukemia (AUROC 0.87), interpreted as disease-state marker prioritization rather than causal validation. In a small independent Adamson 2016 unfolded-protein-response CRISPRi benchmark, Wasserstein achieved mean AUROC 0.786 across five perturbations, outperforming Wilcoxon, t-test, and MAST in this benchmark. Norman 2019 CEBPE CRISPRa illustrates the narrower use case for persistence: ELANE ranked 57/2012, but this is ranking evidence rather than FDR-controlled discovery and does not recover the complete CEBPE target program. PGAA is intended for translational hypothesis prioritization, not bedside diagnosis or treatment recommendation, and is provided as Python/R software with a public code-only repository and a submitted supplementary reproducibility archive.

## Keywords

single-cell RNA-seq; Perturb-seq; disease heterogeneity; Wasserstein distance; persistent homology; CRISPR screening

## Data Availability

Norman 2019: GSE133344. Adamson 2016: GSE90546. CLL: GSE111014. Sepsis: GSE167363. RA: GSE159117. IBD: GSE116222. PBMC: 10x Genomics 3k demo.

## Code Availability

Public code-only repository: https://github.com/xutaoguo55/pgaa. GitHub release: https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code. Zenodo DOI: https://doi.org/10.5281/zenodo.20681141. Software Heritage archive SWHID: swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f. Manuscript-specific source-data tables, figure-reproduction scripts, runtime documentation, and PDF build files are provided in the submitted supplementary software archive rather than in the public code-only repository.

## Transfer Note

This submission follows an editorial transfer recommendation from Nature Methods. The manuscript has been reframed for Communications Medicine to emphasize the method's relevance to heterogeneous disease-associated transcriptional responses in single-cell perturbation and patient-derived scRNA-seq analyses.

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
