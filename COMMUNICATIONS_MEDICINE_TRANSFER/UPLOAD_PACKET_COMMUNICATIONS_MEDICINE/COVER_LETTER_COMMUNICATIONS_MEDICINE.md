Dear Editors,

Following the editorial recommendation from Nature Methods, we are pleased to submit our manuscript, "A distribution-aware framework for prioritizing heterogeneous disease-relevant responses in single-cell perturbation data," for consideration as an Article in Communications Medicine.

Single-cell perturbation screens and patient-derived single-cell datasets are increasingly used to nominate disease mechanisms and therapeutic targets, but many analyses still prioritize average expression changes. This can under-rank responses that occur in only a subset of cells, a pattern that is common in heterogeneous malignancies, immune responses, inflammatory tissues, and CRISPRa perturbation systems. PGAA addresses this problem by providing a distribution-aware framework for prioritizing heterogeneous transcriptional responses in perturbation data and marker-anchored disease-state contrasts.

We believe the manuscript fits Communications Medicine because it presents a computational method and software resource with translational relevance to disease-focused single-cell perturbation analysis. In five disease-relevant observational scRNA-seq datasets, PGAA recovers known marker programs, including B-cell receptor signaling in chronic lymphocytic leukemia. We interpret these analyses conservatively as marker recovery rather than causal validation. We then benchmark the method in two experimental Perturb-seq datasets: Norman 2019 CEBPE CRISPRa, where persistent homology improves ELANE ranking relative to SCEPTRE and Wasserstein, and Adamson 2016 unfolded-protein-response CRISPRi, where the Wasserstein statistic outperforms Wilcoxon, t-test, and MAST in a small independent benchmark. Calibration and simulation analyses define the method's operating regimes and limitations.

The manuscript has been revised specifically for Communications Medicine. We have foregrounded the medical problem of heterogeneous disease-relevant transcriptional responses, clarified the distinction between observational marker recovery and experimental perturbation validation, and avoided claiming new causal disease mechanisms or clinical biomarkers from public observational datasets. Instead, the manuscript positions PGAA as a transparent prioritization layer for heterogeneous responses that can be followed up in disease models, patient-derived systems, or therapeutic perturbation experiments.

The software is implemented in Python and R and is accompanied by source data, test scripts, figure-reproduction scripts, runtime documentation, and a supplementary software archive for editors and reviewers. All authors have approved the manuscript. We declare no competing interests.

Thank you for considering our manuscript.

Sincerely,

Xutao Guo, on behalf of all authors

Department of Hematology, Nanfang Hospital, Southern Medical University

Clinical Medical Research Center of Hematological Diseases of Guangdong Province

Email: guoxutao@smu.edu.cn
