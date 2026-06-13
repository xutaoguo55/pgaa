# Communications Medicine Portal Inputs

## Article Type

Article

## Title

Distribution-aware single-cell perturbation analysis for heterogeneous disease-relevant transcriptional responses

## Short Title

Distribution-aware single-cell perturbation analysis

## Corresponding Author

Xutao Guo

Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China

Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China

Email: guoxutao@smu.edu.cn

## Abstract

Single-cell perturbation screens are increasingly used to nominate disease mechanisms and therapeutic targets, but many analyses emphasize average expression changes and can miss heterogeneous cellular responses. We present PGAA, a distribution-aware framework for ranking perturbation-associated transcriptional responses using a Wasserstein statistic for full-expression-distribution shifts and a persistent-homology statistic for responder-associated expression-shape changes. Across five disease-relevant observational scRNA-seq datasets, Wasserstein recovered known pathway markers with 2.1-5.8x top-100 enrichment, including B-cell receptor signaling in chronic lymphocytic leukemia (AUROC 0.87), interpreted as marker recovery rather than causal validation. In Norman 2019 CEBPE CRISPRa, persistence ranked ELANE 57/2012, compared with 1761 and 1452 for SCEPTRE and Wasserstein; this is ranking evidence, not FDR-controlled discovery. A small independent Adamson 2016 unfolded-protein-response CRISPRi benchmark, calibration analyses, and simulations define operating regimes and limitations.

## Keywords

single-cell RNA-seq; Perturb-seq; disease heterogeneity; Wasserstein distance; persistent homology; CRISPR screening

## Data Availability

Norman 2019: GSE133344. Adamson 2016: GSE90546. CLL: GSE111014. Sepsis: GSE167363. RA: GSE159117. IBD: GSE116222. PBMC: 10x Genomics 3k demo.

## Code Availability

Public code-only repository: https://github.com/xutaoguo55/pgaa. GitHub release: https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code. Software Heritage archive SWHID: swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f. Manuscript-specific source-data tables, figure-reproduction scripts, runtime documentation, and PDF build files are provided in the submitted supplementary software archive rather than in the public code-only repository.

## Transfer Note

This submission follows an editorial transfer recommendation from Nature Methods. The manuscript has been reframed for Communications Medicine to emphasize the method's relevance to heterogeneous disease-associated transcriptional responses in single-cell perturbation and patient-derived scRNA-seq analyses.

## Competing Interests

The authors declare no competing interests.

## Funding

No external funding was received for this work.

## Open Peer Review Preference

OPT OUT of publication of reviewer reports if the manuscript is accepted.
