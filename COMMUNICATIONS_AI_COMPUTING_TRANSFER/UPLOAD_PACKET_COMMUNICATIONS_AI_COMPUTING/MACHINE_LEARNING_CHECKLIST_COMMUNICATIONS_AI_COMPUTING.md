# Machine Learning Checklist for Communications AI & Computing

Corresponding author: Xutao Guo  
Last updated by author: 2026-06-23  
Manuscript: A distribution-aware computational framework for prioritizing heterogeneous responses in single-cell perturbation data

This completed text version follows the Nature Portfolio Machine Learning Checklist V 1.1. PGAA is primarily a statistical and computational ranking framework, not a trained predictive machine-learning model; items concerning train/validation/test splits and pretrained models are therefore answered as not applicable with an explanation.

## 1. Availability and reproducibility of code and data

- [ ] Code will be included in a Code Ocean capsule.
- [x] Source code is included in the submission and available in a public repository: https://github.com/xutaoguo55/pgaa
- [ ] A compiled standalone version of the software is included in the submission or available in a public repository. Explanation: PGAA is distributed as Python/R source code rather than as compiled standalone software.
- [x] A test dataset and instructions/scripts for replicating results are included in the submitted supplementary software archive and public repository.
- [x] A README file with installation and running instructions is included in the submitted supplementary software archive and public repository.
- [x] The code is made available to reviewers during review via the submitted supplementary software archive and public repository.
- [ ] Pretrained models are used in the study and accessible through: no pretrained models are used.
- [ ] Pretrained models are used in the study and are not accessible.
- [x] The paper contains information on how to obtain code and data after publication. See the Data availability and Code availability statements.

## 2. Datasets

A. All data sources are listed in the paper.

- [x] Yes. The manuscript lists Norman 2019 (GSE133344), Adamson 2016 (GSE90546), CLL (GSE111014), Sepsis (GSE167363), RA (GSE159117), IBD (GSE116222), and the 10x Genomics PBMC 3k demo dataset.
- [ ] No.

B. Train, test and validation datasets are publicly available and links/accession numbers are provided.

- [x] Yes, with qualification. This study evaluates statistical ranking methods rather than training a predictive model, so formal train/validation/test splits are not used. Public dataset accessions are provided in the manuscript.
- [ ] No.

C. Potential dataset biases are reported and discussed.

- [x] Yes. The manuscript discusses limited benchmark breadth, use of K562 perturbation screens, observational marker-recovery stress checks, cell-type proxy limitations, and the absence of causal claims from observational datasets.
- [ ] No.

D. Data cleaning and preprocessing steps are clearly described.

- [x] Yes. Methods describe QC filters, normalization to 10K CPM, log1p transformation, HVG selection, target-gene forced inclusion, residualization, and cluster-stratified permutations.
- [ ] No.

E. Combining data from multiple sources is clearly identified.

- [x] Yes. Datasets are analyzed as separate benchmarks or bounded marker-recovery checks; the manuscript does not pool unrelated datasets into one trained model.
- [ ] No.

## 3. Model and training

A. Model architecture.

No trained predictive model is introduced. PGAA consists of distribution-aware statistical ranking modules: Wasserstein distance, persistent-homology histogram-shape ranking, conditional mutual information, Fisher negative-binomial distance, and an exploratory combined z-score.

B. A model card is provided.

- [ ] Yes.
- [x] No. No pretrained or deployed ML model is released; this item is not applicable to the submitted statistical software framework.

C. The model clearly splits data into training, validation and testing sets.

- [ ] Yes.
- [x] No, not applicable. No model is trained or selected using train/validation/test splits.

D. The method of data splitting is clearly stated.

- [x] Yes, not applicable. The manuscript states that PGAA is evaluated by benchmark and simulation analyses rather than predictive-model training splits.
- [ ] No.

E. Data splitting mimics anticipated real-world applications.

- [ ] Yes.
- [x] No, not applicable. The framework ranks genes within a given perturbation contrast; it does not learn a model intended for deployment on future samples.

F. The data splitting procedure avoids data leakage.

- [x] Yes, not applicable. There is no trained model and no hyperparameter optimization using held-out labels. Perturbation labels are permuted within clusters for calibration.
- [ ] No.

G. Interpretability of the model has been studied and validated.

- [x] Yes. PGAA outputs gene-level ranking statistics, permutation p-values, and Storey pi0 diagnostics; interpretation is tied directly to distributional shifts and histogram-shape changes.
- [ ] No.

## 4. Evaluation

A. Performance metrics are described and justified.

- [x] Yes. AUROC, AUPRC, enrichment ratios, permutation p-values, Storey pi0 diagnostics, and simulation TPR are described in the manuscript and supplement.
- [ ] No.

B. Cross-validation of the results is included.

- [ ] Yes.
- [x] No, not applicable. No predictive model is trained. Robustness is evaluated through independent benchmarks, simulations, negative-control calibration, and bin-count sensitivity checks.

C. Community-accepted benchmark datasets/tasks are used for comparisons.

- [x] Yes. Adamson 2016 UPR CRISPRi and Norman 2019 CEBPE CRISPRa are used as Perturb-seq benchmarks, with public accession numbers.
- [ ] No.

D. Baseline comparisons to simple/trivial models are provided.

- [x] Yes. PGAA is compared with Wilcoxon, t-test, MAST, SCEPTRE where available, housekeeping negative controls, and random positive-rate AUPRC baselines.
- [ ] No.

E. Benchmarks with current state-of-the-art are provided.

- [x] Yes, with limitation. Comparisons include common single-cell differential-expression and Perturb-seq tools; broader genome-scale validation against additional SCEPTRE-family and perturbation-specific methods is identified as future work.
- [ ] No.

F. Ablation experiments are included.

- [x] Yes. Simulation ablations and histogram-bin sensitivity analyses are included.
- [ ] No.

G. The model has been tested on a fully independent dataset.

- [x] Yes. The Adamson 2016 UPR CRISPRi benchmark is independent of the Norman 2019 CEBPE CRISPRa ranking example and the observational stress-test datasets.
- [ ] No.

## 5. Computational resources

A. The paper contains information on hardware/computing resources.

- [x] Yes. Runtime is reported for a single CPU core in the Implementation section.
- [ ] No.

B. The paper includes information on computational costs.

- [x] Yes. The manuscript reports representative runtimes for 2,000 genes and stated permutation counts; the supplementary software archive includes runnable smoke/regression checks.
- [ ] No.
