Dear Editors,

We are pleased to submit our manuscript, "A distribution-aware framework for prioritizing heterogeneous disease-relevant responses in single-cell perturbation data," for consideration as an Article in *Communications Medicine*. This submission is made through the Nature Portfolio transfer service following the transfer recommendation associated with our previous *Nature Methods* submission, NMETH-A66354, originally entitled "PGAATRACE for clinical single-cell virtual perturbation maps."

We have revised and retitled the manuscript specifically for *Communications Medicine*. The revised manuscript presents PGAA, a Python/R software framework for prioritizing heterogeneous transcriptional responses in single-cell perturbation data and marker-anchored disease-state contrasts. We believe the study fits *Communications Medicine* because it addresses a practical translational problem: patient-derived single-cell datasets and disease-model perturbation screens often contain responder states confined to subsets of cells, whereas standard mean-focused analyses can under-rank such signals. PGAA provides a transparent distribution-aware prioritization layer, supported by disease-relevant marker-recovery analyses, Perturb-seq benchmarks, calibration diagnostics, and explicit limitations.

The manuscript distinguishes observational marker recovery from experimental perturbation validation. Across five disease-relevant observational scRNA-seq datasets, PGAA recovers known marker programs, including B-cell receptor signaling in chronic lymphocytic leukemia; these analyses are interpreted conservatively as disease-state marker prioritization rather than causal validation. In experimental Perturb-seq benchmarks, the Adamson 2016 unfolded-protein-response CRISPRi dataset provides a small independent validation setting in which the Wasserstein statistic outperforms Wilcoxon, t-test and MAST, whereas the Norman 2019 CEBPE CRISPRa analysis is presented as a narrow persistence-ranking example rather than broad target-program recovery.

The work is intended to support translational hypothesis prioritization for follow-up in disease models, patient-derived systems, or perturbation screens. We do not claim new clinical biomarkers, direct treatment recommendations, or bedside diagnostic utility from the public observational datasets.

The public code-only repository is available at https://github.com/xutaoguo55/pgaa. Release v0.1.0-code is archived at Zenodo (DOI: https://doi.org/10.5281/zenodo.20681141) and by Software Heritage (SWHID: swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f). Manuscript-specific source-data tables, figure-reproduction scripts, runtime documentation, and PDF build files are provided in the submitted supplementary software archive.

All authors have approved the manuscript. We declare no competing interests and no external funding. We opt in to Transparent Peer Review.

Thank you for considering our manuscript.

Sincerely,

Xutao Guo, on behalf of all authors

Department of Hematology, Nanfang Hospital, Southern Medical University

Clinical Medical Research Center of Hematological Diseases of Guangdong Province

Email: guoxutao@smu.edu.cn
