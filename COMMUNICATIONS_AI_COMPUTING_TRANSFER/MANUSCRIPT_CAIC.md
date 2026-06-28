# A distribution-aware computational framework for prioritizing heterogeneous responses in single-cell perturbation data

**Authors**: Xiaolei Wei<sup>1†</sup>, Haiqing Zheng<sup>2†</sup>, Junwei Huang<sup>1†</sup>, Qi Wei<sup>1</sup>, Yongqiang Wei<sup>1</sup>, Ru Feng<sup>1</sup>, Xutao Guo<sup>1,3\*</sup>

<sup>1</sup> Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>2</sup> Department of Nosocomial Infection Management, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>3</sup> Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China  

<sup>†</sup> These authors contributed equally to this work.  
<sup>\*</sup> Correspondence: Xutao Guo (guoxutao@smu.edu.cn)

## Abstract

Single-cell perturbation screens often produce subset-confined responses that are poorly captured by mean-shift tests. We present PGAA, a distribution-aware computational framework for ranking heterogeneous transcriptional responses. PGAA combines two complementary statistics with shared permutation calibration: PGAA-W Wasserstein, a quantile-grid statistic for full-distribution shifts, and PGAA-H, a histogram-shape diagnostic for responder-associated expression changes. Calibration is assessed by Storey upper-tail diagnostics. In a proof-of-principle unfolded-protein-response CRISPRi benchmark, PGAA-W achieved mean AUROC 0.786 across five perturbations and mean AUPRC 0.0191 (random baseline 0.0065). A Norman 2019 multi-perturbation CRISPRa extension supported PGAA-W as the default ranking statistic, while a focused CEBPE analysis illustrated the narrower role of PGAA-H (ELANE rank 57/2012 as ranking evidence, not FDR-controlled discovery). Observational single-cell datasets provided bounded marker-recovery checks. PGAA is implemented in Python and R, with public code, a reproducibility archive, and a CLI for standard expression/metadata inputs.

**Keywords**: single-cell RNA-seq; Perturb-seq; computational biology; Wasserstein distance; histogram-shape statistic; distributional ranking; CRISPR screening


## 1. Introduction

Single-cell perturbation screens \textsuperscript{1--4} provide a scalable way to connect genetic or transcriptional perturbations to cellular phenotypes. A central computational task in these datasets is to rank genes or response programs whose expression differs between perturbed and control cells. The standard analysis compares mean expression of each non-target gene between groups. This works well when a perturbation produces a uniform transcriptional shift: knock out a transcription factor, its targets drop, and a t-test, Wilcoxon test, MAST, or SCEPTRE can detect the difference \textsuperscript{5,6}. Together with preprocessing workflows in Seurat \textsuperscript{7,8} and Scanpy \textsuperscript{9}, these methods form the standard Perturb-seq analysis toolkit.

Many perturbation responses, however, are not well summarized by a mean shift. CRISPRa \textsuperscript{10} can activate a target in only a fraction of cells. A weak perturbation may shift variance, create responder and non-responder subpopulations, or change the shape of an expression distribution while leaving the mean only modestly changed. Similar response structures can also appear in marker-anchored contrasts from patient-derived single-cell data, where disease-associated programs often mark subsets of malignant, immune, stromal, or inflammatory cells rather than an entire population. A method that only asks whether average expression changed can under-rank such signals and can make downstream prioritization less interpretable.

Few existing Perturb-seq methods make distribution-shape changes a primary output, although heterogeneity-aware approaches are emerging \textsuperscript{11}. This leaves a gap between calibrated mean-shift testing and the practical need to rank heterogeneous responses for follow-up experiments. The gap is computational rather than only biological: users need statistics that compare full expression distributions, calibration diagnostics that reveal when a ranking is trustworthy, and software that can be applied consistently across perturbation screens and marker-anchored single-cell contrasts.

We present **PGAA**, a distribution-aware framework and software implementation for heterogeneous single-cell response prioritization. PGAA uses two complementary statistics sharing a common calibration infrastructure: the PGAA-W Wasserstein quantile-grid statistic captures one-dimensional distributional shifts, and the S2 histogram-shape statistic (PGAA-H) ranks expression-shape changes consistent with responder-associated heterogeneity. The mathematical target is to rank non-target genes by perturbation-associated distributional discrepancy after coarse cell-state and library-size adjustment. The novelty is not the invention of Wasserstein distance or histogram peak scoring; it is their calibration-aware adaptation into a reproducible single-cell perturbation ranking layer with explicit evidence boundaries. Additional modules for conditional MI and Fisher NB scoring are provided as software extensions. All statistics are accompanied by Storey upper-tail calibration diagnostics that let users assess reliability on their own data before interpreting results. Figure 1a illustrates the response regimes motivating PGAA, and Figure 1b summarizes the analysis workflow.

**Contribution.** PGAA is not a new distance metric, a new statistical test, or a new mathematical theorem. It is a principled integration of existing distributional tools (1D Wasserstein, histogram peak analysis, permutation calibration) into a transparent, guardrailed ranking protocol for heterogeneous perturbation responses—a computational decision-support component, not a new algorithm. The protocol has three layers: (1) two complementary statistics sharing a common permutation calibration infrastructure; (2) explicit guardrails (Storey upper-tail diagnostic, pilot n_bins sweep, negative-control requirement for PGAA-H) that define when a ranking can be trusted and when it cannot; and (3) a reproducible Python/R implementation with a command-line interface, source-data rebuild scripts, and a locked evidence-source registry. The contribution is the integration, the guardrails, and the documentation of failure modes—not the individual statistical components.

We evaluate PGAA across experimental Perturb-seq benchmarks, simulation ablations, distribution-aware comparators, and external marker-recovery stress checks. Adamson 2016 UPR CRISPRi and Norman 2019 CRISPRa provide real perturbation benchmarks with complementary response regimes. The Norman analyses include a multi-perturbation PGAA-W extension across KLF1, CEBPE, and CEBPA with KS as an additional distribution-aware baseline, followed by a focused CEBPE PGAA-H example. Simulations define the operating regimes of the Wasserstein and S2 histogram-shape statistic (PGAA-H). A processed-source-data MMD-PSM comparison is included as an additional distribution-aware baseline for the Norman CEBPE contrast. Observational scRNA-seq datasets in chronic lymphocytic leukemia (CLL), sepsis, rheumatoid arthritis, inflammatory bowel disease, and PBMCs are used only to ask whether distributional ranking can recover known marker biology in medically relevant single-cell contexts. These analyses support marker recovery rather than causal interpretation, and Table 1 states the evidence level assigned to each analysis class.

Table 1. Evidence levels across PGAA evaluations.

| Evidence class | Datasets or analyses | Purpose | Boundary |
|---|---|---|---|
| Perturb-seq proof-of-principle benchmark | Adamson 2016 UPR CRISPRi | Test PGAA-W/PGAA-H ranking behavior in a small curated real perturbation benchmark | Insufficient for method-level validation (5 perturbations, 13 positives, one cell line). Larger-scale evaluation (Replogle 2020/2022, scPerturb) required before general Perturb-seq claims. Restricted to proof-of-principle. |
| Multi-perturbation CRISPRa extension | Norman 2019 KLF1, CEBPE, CEBPA | Compare PGAA-W Wasserstein against KS, Welch t, and Wilcoxon on curated target-program panels | Curated panel recovery rather than original genome-wide DEG gold standard; top-rank recovery remains sparse |
| Narrow PGAA-H ranking example | Norman 2019 CEBPE CRISPRa | Test whether PGAA-H can prioritize a responder-associated expression-shape target | ELANE/PRTN3 ranking evidence only; full target-program recovery is weak |
| Processed-source-data distributional check (single contrast) | MMD-PSM on Norman 2019 CEBPE | Single-contrast sensitivity check against a distributional null | Not a systematic comparator; one perturbation, one target set. Included because distribution-aware baselines are scarce in Perturb-seq tools. |
| External marker recovery | CLL, sepsis, rheumatoid arthritis, inflammatory bowel disease, PBMC | Bounded recovery check of known marker biology in public scRNA-seq data | Observational marker prioritization only; not causal or clinical biomarker evidence |
| Calibration and operating-regime checks | Simulations, null controls, PGAA-H bin sweep, Storey upper-tail diagnostics | Define when the statistics are interpretable | Guardrail evidence; not a replacement for experimental follow-up |

This separation is used throughout the manuscript: perturbation benchmarks assess ranking behavior, observational datasets are used only as marker-recovery stress checks, and calibration analyses define when a score should be interpreted. With these evidence boundaries stated, Figure 1 gives the conceptual overview of the response regimes and the PGAA workflow.

The statistics in PGAA are deliberately assigned different roles. PGAA-W Wasserstein measures location, spread and other one-dimensional distributional shifts and is the default score. KS measures the maximum empirical CDF discrepancy and is used as a distribution-aware comparator. MMD-PSM and related energy or kernel methods test broader distributional discrepancies but can be computationally heavier and depend on implementation choices. S2 histogram-shape measures peak-structure changes, including responder-associated expression-shape shifts, and is treated as a secondary diagnostic. Mean-based tests remain useful when the response is dominated by a location shift but can under-rank subset-confined or shape-changing responses.

**[Figure 1]**


## 2. Results

### 2.1 Framework overview and evidence boundaries

PGAA is designed as a modular computational ranking layer for heterogeneous single-cell responses. The Wasserstein statistic is the primary starting score for full-distribution shifts, whereas the S2 histogram-shape statistic (PGAA-H) is a secondary diagnostic for responder-associated expression-shape changes. The framework first adjusts expression for coarse cell-state and library-size effects, then ranks genes by distributional discrepancy between perturbed and control cells. Within-cluster permutation is used to provide empirical ranking evidence, and the Storey upper-tail diagnostic is used as a guardrail for calibration rather than as a guarantee of genome-wide discovery.

Figure 1 summarizes the response-regime problem and the analysis workflow. The figure intentionally separates the default PGAA-W score from the secondary PGAA-H statistic, because the benchmarks below support a hierarchy rather than two interchangeable discovery tests.

### 2.2 Independent Perturb-seq benchmark in unfolded-protein-response biology

To test PGAA on a small independent Perturb-seq dataset with a complementary perturbation modality and a disease-relevant stress-response pathway, we applied both statistics to the Adamson et al. (2016) UPR CRISPRi screen (GSE90546). After QC, 5,680 K562 cells were retained across five well-characterized sgRNA perturbations targeting UPR genes (SPI1, ZNF326, BHLHE40, CREB1, DDIT3; 468-686 cells each) and a non-targeting control (1,759 cells). The reference positive set was a curated UPR marker set covering IRE1, PERK, ATF6, ERAD, and chaperone branches, of which 13 markers were present in the 2,000-gene HVG subset (Supplementary Table 1).

Across the five perturbations, PGAA-W achieved a mean AUROC of 0.786 (range 0.767-0.806, mean AUPRC 0.0191) for recovering known UPR genes (Table 2). By comparison, Wilcoxon, t-test, and MAST achieved mean AUROCs of 0.529, 0.523, and 0.406 respectively in the same benchmark. SCEPTRE was not rerun in the Adamson benchmark because this proof-of-principle analysis used a compact curated source-data benchmark rather than a full raw guide-level association workflow. We therefore treat the Adamson comparison as a limited baseline comparison and use the Norman 2019 CEBPE analysis in Section 2.4 as a direct SCEPTRE reference point. Broader SCEPTRE-family benchmarking across genome-scale Perturb-seq datasets remains an important limitation. The S2 histogram-shape statistic (PGAA-H) achieved a mean AUROC of 0.748 (range 0.658-0.833, mean AUPRC 0.0253). For the BHLHE40 knockdown, this histogram-shape statistic had the highest AUROC and AUPRC among the compared methods (AUROC 0.833, AUPRC 0.0594 vs. Wasserstein AUROC 0.788), consistent with a heterogeneous responder-associated expression pattern (Supplementary Figure 1). Because only 13 of the 2,000 HVGs were UPR positives, the random AUPRC baseline was 0.0065; observed AUPRC values correspond to 2.9x and 3.9x enrichment over random expectation for the Wasserstein and histogram-shape statistics, respectively. PGAA-H mean AUPRC is strongly influenced by the BHLHE40 perturbation (per-perturbation AUPRC 0.0594); across the remaining four perturbations, mean PGAA-H AUPRC is approximately 0.0167. These perturbations were selected a priori based on UPR annotation in the original study and a minimum cell-count threshold of at least 400 cells, not based on PGAA performance (Supplementary Table 2). The Adamson benchmark supports proof-of-principle prioritization in a small curated UPR setting, but it does not establish general performance across perturbation modalities, cell types, or disease models.

Table 2 reports the aggregate method-level performance. The accompanying figure then separates the benchmark design, average AUROC, AUPRC relative to the random positive-rate baseline, and perturbation-level heterogeneity.

Table 2. Adamson 2016 UPR CRISPRi benchmark summary.

| Method | Mean AUROC | AUROC range or 95% CI | Mean AUPRC | AUPRC 95% CI | Main readout |
|---|---:|---|---:|---|---|
| PGAA-W Wasserstein | 0.786 | 0.767-0.806 | 0.0191 | 0.0160-0.0222 | Highest mean AUROC |
| PGAA-H histogram-shape | 0.748 | 0.658-0.833 | 0.0253 | 0.0010-0.0495 | Higher AUPRC in responder-like cases |
| Wilcoxon rank-sum | 0.529 | 0.415-0.643 | 0.0089 | 0.0048-0.0131 | Rank-based baseline |
| t-test | 0.523 | 0.430-0.616 | 0.0085 | 0.0050-0.0120 | Mean-shift baseline |
| MAST | 0.406 | 0.354-0.458 | 0.0014 | 0.0012-0.0016 | Single-cell DE baseline |

The table shows that PGAA-W has the strongest mean AUROC, whereas PGAA-H can be competitive when the response is responder-like. Figure 2 provides the corresponding visual breakdown and shows that performance varies across individual perturbations.

**[Figure 2]**

### 2.3 A Norman multi-perturbation extension supports PGAA-W as the default ranking statistic

To broaden the real Perturb-seq evaluation beyond the small Adamson UPR benchmark, we added a Norman 2019 multi-perturbation CRISPRa extension covering KLF1, CEBPE, and CEBPA. Each perturbation was compared with non-targeting controls using 2,000 HVGs plus forced inclusion of the pre-specified target-panel genes. This forced-inclusion step is important: none of the KLF1, CEBPE, or CEBPA positive-panel genes were marked as HVGs in the processed Norman h5ad file, so a strict HVG-only benchmark would have silently removed the evaluation genes. The script reports a panel audit, gene-level scores, and a metadata table in the supplementary software archive.

Across the three perturbations, PGAA-W Wasserstein produced higher target-panel AUROC than the KS statistic, Welch t statistic, or Wilcoxon rank-sum score in this curated-panel benchmark (Supplementary Table 3). We emphasize that this benchmark evaluates relative ranking of a pre-specified gene panel under different statistics, not de novo target discovery from an unbiased genome-wide screen. Because target-panel genes were force-included (they were absent from the processed HVG set), the benchmark measures whether PGAA-W ranks a known gene set more favorably than comparators—not whether PGAA-W can discover targets from unlabeled data. Only 1-2 positive genes appeared in the top 100 for each PGAA-W run, and AUPRC values must be read against random baselines of 0.0045-0.0079. The result is therefore useful as a broader perturbation-level ranking check for PGAA-W, not as a substitute for genome-scale perturbation validation or original-study DEG benchmarking.

### 2.4 PGAA-H: a case-study-level diagnostic with limited demonstrated scope

Norman *et al.* (2019) used CRISPRa to activate CEBPE in a K562 Perturb-seq screen \textsuperscript{3}; K562 is a human leukemia cell line \textsuperscript{12}. CEBPE is a myeloid transcription factor whose known targets include nine neutrophil granule proteins: ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, and RNASE2 \textsuperscript{13,14}. This benchmark is not a clinical disease cohort, but it is relevant to hematologic differentiation biology and tests the response regime that motivated PGAA: a regulator is activated, but the downstream expression response may be heterogeneous across cells.

SCEPTRE and PGAA-W rank this target poorly. SCEPTRE places ELANE at rank 1761/2012 (p = 0.92). PGAA-W places it at rank 1452/2012 (p = 0.223). Neither method ranks ELANE among its strongest CEBPE candidates in this analysis. As an additional distributional check, an MMD-PSM analysis on the same processed CEBPE contrast returned target-set AUROC 0.499 and 0/9 nominal CEBPE target hits. This is a single-contrast processed-source-data sensitivity check—not a systematic comparator—included because distribution-aware baselines are scarce in the Perturb-seq tool landscape.

The S2 histogram-shape statistic (PGAA-H) (n_bins = 20, 500 permutations) ranks ELANE at position 57 (p = 0.04), a 25-fold rank improvement over PGAA-W (Table 3). With 500 permutations, this p-value is interpreted as ranking evidence rather than genome-wide significance, and no FDR-controlled CEBPE gene discovery is claimed. The p-value distribution is acceptable in this pre-specified setting (uncapped Storey upper-tail ratio = 1.32 with 200 permutations in the sensitivity run; approximately 1.0 with 500 permutations). The top genes by raw PGAA-H value (SLC45A1, DLX2, ATP5E) are not known CEBPE targets; ELANE's stronger rank by permutation p-value reflects its favorable null distribution relative to other genes. Across the full nine-gene CEBPE target set, only ELANE reaches p < 0.05 in the PGAA-H analysis; PRTN3 is also within the top 100 by permutation p-value but does not pass the nominal threshold (p = 0.068). The AUROC is 0.476 and AUPRC is 0.0076. Thus, the Norman result should be read as a focused ELANE/PRTN3 ranking signal, not broad recovery of the complete granulocytic target program. As a calibration check, we applied PGAA-H to all six perturbations using the CEBPE target gene set as the reference positive set. ELANE was ranked strongly for CEBPE and also for the severely over-sensitive BAK1 perturbation, where the tail ratio was 0.10. For the well-calibrated KLF1 perturbation, ELANE was not supported (p = 0.70, uncapped tail ratio = 1.15). For CBL, SLC4A1, and DUSP9, ELANE p-values were 0.58, 0.16, and 0.90 respectively. This analysis is treated as perturbation-level calibration context rather than specificity proof; over-sensitive perturbations should not be interpreted as formal discoveries. Target-level details are provided in Supplementary Table 4.

Table 3. Norman 2019 CEBPE ranking and calibration summary. PGAA-W denotes the Wasserstein statistic; PGAA-H denotes the histogram-shape diagnostic.

| Analysis | Method or perturbation | Key result | Interpretation |
|---|---|---|---|
| ELANE ranking | SCEPTRE | rank 1761/2012; p=0.92 | Not prioritized |
| ELANE ranking | PGAA-W | rank 1452/2012; p=0.223 | Weak distributional signal |
| ELANE ranking | PGAA-H | rank 57/2012; p=0.04 | Ranking evidence only |
| CEBPE target set | PGAA-H | AUROC 0.476; AUPRC 0.0076; 1/9 targets in top 100 | No broad program recovery |
| Single-contrast distributional check | MMD-PSM | AUROC 0.499; 0/9 nominal target hits | Single-data-point sensitivity; not a systematic comparator |
| Negative check | KLF1 perturbation | uncapped tail ratio 1.15; ELANE p = 0.70 | Well calibrated |
| Over-sensitive check | BAK1 perturbation | tail ratio 0.10; ELANE p = 0.005 | Not specificity evidence |

This summary motivates the narrower visual analysis in Figure 3. CRISPRa can produce heterogeneous target activation: the gRNA does not guarantee protein-level CEBPE expression in every cell, and the resulting responder/non-responder expression pattern is the regime PGAA-H was designed to rank (Supplementary Figure 2). K562 is an erythroleukemia line, not a neutrophil progenitor; while it retains granulocytic differentiation capacity upon CEBPE activation, not all nine targets may be transcriptionally responsive in this system.

The broader PGAA-H evidence is limited to two case-study-level examples: the CEBPE CRISPRa ELANE/PRTN3 signal reported here, and the BHLHE40 CRISPRi case in the Adamson benchmark (PGAA-H per-perturbation AUROC 0.833, Section 2.2). In the observational CLL setting, PGAA-H was uninformative (AUROC 0.460, Section 2.8). The simulation (Section 2.7) showed PGAA-H TPR of only 0.12 under partial bimodality. PGAA-H currently has limited demonstrated utility beyond these two specific cases; broader evaluation across multiple perturbations, cell types, and response modalities is required before it can be recommended as a general-purpose diagnostic. This scope limitation is central to the PGAA-H guardrail protocol.

**[Figure 3]**

### 2.5 Perturbation-specific calibration defines guardrails for PGAA-H ranking

Applying PGAA-H to six different perturbations from the Norman 2019 screen reveals that calibration is far from consistent. The uncapped Storey upper-tail ratio ranges from 1.15 for KLF1, a well-calibrated erythroid transcription-factor perturbation, to 0.10 for BAK1, a severely over-sensitive perturbation. Intermediate cases include CBL (tail ratio = 0.72), SLC4A1 (0.67), DUSP9 (0.68), and CEBPE in the n_bins = 50 calibration run (0.25). Figure 4 shows the full calibration pattern.

KLF1 drives a clean erythroid program. CEBPE CRISPRa and BAK1 do not. The calibration spread reflects this biology, and the practical takeaway is simple: include a negative control perturbation and check the upper-tail calibration diagnostic before interpreting PGAA-H ranks. Importantly, the CEBPE tail ratio of 0.25 reported here comes from a calibration run with n_bins = 50 and n_perms = 200; the main analysis in Section 2.4 uses n_bins = 20 and n_perms = 500, which yields an upper-tail ratio approximately 1.0-1.3 before capping. The corresponding QQ plot and permutation p-value histogram are provided in Supplementary Figure 3. The discrepancy illustrates how strongly calibration depends on both bin count and permutation depth, reinforcing the need for the pilot sweep recommended in Section 2.6.

**[Figure 4]**

### 2.6 Sensitivity to histogram bin count

The S2 histogram-shape statistic (PGAA-H) depends on the number of histogram bins, and the dependence is non-trivial. We tested n_bins values of 20, 30, 50, 75, 100 and 150 on Norman 2019 CEBPE, using 200 permutations for the sensitivity sweep; the main CEBPE result uses 500 permutations. The full sweep is reported in Supplementary Table 5. In brief, ELANE ranks well at n_bins = 20 (rank 32, p = 0.025, uncapped tail ratio = 1.32 in the 200-permutation sweep), collapses at n_bins = 30 (rank 1807, p=0.672), and larger bin counts produce many nominally significant genes with low tail-ratio values (0.23-0.25). The n_bins = 20 to 30 transition is not an arbitrary tuning artifact: ELANE is a lowly expressed granulocyte gene in K562 cells (an erythroleukemia line). At n_bins = 20 (~0.03-0.05 log-CPM units per bin for these expression levels), the histogram resolution captures the bimodal expression pattern expected from partial CRISPRa activation. At n_bins = 30, the bin width falls below the natural expression variability of low-expressed genes in this system, merging the weak responder peak into the non-responder-dominated mode—a peak-merging failure mode detectable by the pilot sweep. The practical recommendation is to identify this failure mode via pilot sweep on a negative-control perturbation before interpreting the perturbation of interest; n_bins should never be tuned to optimize a target-gene rank. We recommend n_bins = 20 as the manuscript starting setting, with a pilot sweep over n_bins = 10, 20, 30 and 50 on a control or null perturbation to verify that the chosen value does not fall into a peak-merging failure mode.

### 2.7 Simulation ablation maps each statistic to its regime

To systematically assess when each statistic performs best, we simulated three perturbation types at seven effect sizes from theta = 0.1 to theta = 1.0, with three replicates each (63 conditions total). These simulations are intended as operating-regime diagnostics rather than a full generative model of scRNA-seq count data.

Type A (pure mean shift) is the Wasserstein statistic's home territory (TPR = 0.97 at theta = 1.0). Type C (mean + bimodality) favors the Wasserstein statistic as well. The most informative condition is Type B, where only 40% of perturbed cells respond. Here the Wasserstein statistic and the exploratory combined z-score are competitive (TPR = 0.52-0.85 depending on theta), while PGAA-H reaches only TPR = 0.12. This simulation uses *partial* bimodality--the two modes overlap in the 40%-response regime. The Norman 2019 CEBPE analysis therefore should not be read as broad evidence that PGAA-H prioritizes all heterogeneous responses; rather, it illustrates a narrower ranking use case in which a responder-associated expression pattern can improve the rank of selected targets.

These results support a simple analysis hierarchy. The Wasserstein statistic is the starting ranking score for standard knockout or overexpression screens and for unknown response modes. The S2 histogram-shape statistic (PGAA-H) should be used only as a secondary diagnostic when discrete responder states are biologically plausible, and only after negative-control calibration and bin-sensitivity checks. The combined z-score can be used as an exploratory ranking score when both mean/distributional shift and shape change are expected, but it is not treated as an inferential discovery test here.

The full simulation plot is provided in Supplementary Figure 4.

### 2.8 Observational marker-recovery stress checks remain secondary evidence

As an external stress check outside curated perturbation benchmarks, Wasserstein enriches known pathway markers 2.1-5.8x over background across five observational single-cell datasets with clinical or disease relevance (CLL 4.0x, Sepsis 2.1x, RA 2.5x, PBMC 2.9x, IBD 5.8x). On CLL, the B-cell receptor signaling gene set (CD79A, CD79B, MS4A1, CD24, BANK1, LYN, BLNK, SYK, BTK, PLCG2, PIK3CD, CD19, CD22) appears prominently in the top 100, with AUROC 0.958 for known-marker recovery (Supplementary Table 6). This result is biologically coherent because B-cell receptor signaling is a central axis in CLL, but the analysis should be read as marker prioritization from public observational data rather than as causal or biomarker evidence.

These five datasets are observational--the "perturbation" is defined by binning cells on endogenous marker or pathway-associated expression, not by an experimental intervention--so the results demonstrate marker recovery rather than causal interpretation. In the CLL marker-recovery setting, the only observational dataset where full raw inputs are bundled for systematic recomputation (cll20k_4method.py), PGAA-W was not uniformly superior to conventional baselines: t-test AUROC 0.966 versus PGAA-W AUROC 0.958, while PGAA-H AUROC 0.460 was not informative in this TCL1A-anchored contrast. Conventional baselines (t-test, Wilcoxon) are not reported for Sepsis, RA, PBMC, and IBD because the submitted archive does not contain the full raw data needed for independent recomputation; these four datasets are included as source-data enrichment summaries only (Supplementary Table 6). PGAA-W's value in observational settings is as a distribution-aware prioritization score for heterogeneous disease-state contrasts, not as a replacement for standard marker-ranking methods.

The CLL TCL1A case shows how the two distributional statistics can prioritize different marker programs. Among the top 100 genes ranked by each statistic, only six overlap. PGAA-W enriches B-cell receptor markers (CD79A rank 9, CD79B rank 48, MS4A1 rank 53), matching the malignant B-cell biology of CLL. The S2 histogram-shape statistic (PGAA-H) picks up T-cell receptor genes (TRBV7-6, TRAV12-1, CD3E, CD3D) that Wasserstein misses entirely, consistent with a distinct immune-context signal rather than the same B-cell receptor program. The exploratory combined z-score recovers 3 BCR and 11 TCR genes at nominal p < 0.05, versus 4+3 for Wasserstein alone and 0+7 for PGAA-H alone; these nominal combined scores are used only to illustrate rank complementarity.

The CLL analysis uses rank-based inverse-normal scores (Supplementary Methods, CLL rank-score analysis) rather than full permutation calibration--a lighter-weight approach appropriate when only relative gene ordering matters rather than formal significance testing (Supplementary Figure 5). The cross-dataset marker-recovery source data and CLL comparator results are retained in Supplementary Table 6. We do not use these observational datasets as causal or clinical evidence. Figure 5 summarizes the external marker-recovery stress checks and the CLL comparator analysis.

**[Figure 5]**


## 3. Discussion

We set out to assess whether distribution-aware statistics could improve computational prioritization of single-cell perturbation programs when the signal is heterogeneous rather than a simple mean shift. Across these benchmarks, PGAA-W Wasserstein ranked curated positive-set genes above mean-shift comparators, while PGAA-H showed utility in narrow responder-associated settings but required perturbation-specific calibration checks. Observational stress checks confirmed marker-recovery potential without supporting causal claims.

These results suggest a practical two-pronged strategy for distribution-aware single-cell perturbation analysis. PGAA-W is a useful starting distributional score when the perturbation type is unknown, including when marker-anchored scRNA-seq contrasts are used to prioritize candidate response programs for follow-up. The S2 histogram-shape statistic (PGAA-H) fills a narrower niche--CRISPRa screens, weak-effect perturbations, and any setting where the response is expected to be heterogeneous--but requires the user to verify calibration via the Storey upper-tail diagnostic and to run a pilot n_bins sweep before committing to results. PGAA-H's strong dependence on histogram bin count (values at n_bins = 20 and n_bins = 50 correlate at only r = 0.12) means it should be treated as a ranking tool rather than a formal discovery procedure unless substantially more permutations are used.

**Practical use recommendation.** In a new analysis, we recommend: (1) run PGAA-W first as the default ranking score for unknown or broad response modes; (2) run PGAA-H only when a responder-associated or histogram-shape change is biologically plausible; (3) before interpreting PGAA-H ranks, verify calibration on a negative-control perturbation or unrelated target, check the Storey upper-tail diagnostic, and run a pilot n_bins sweep (e.g., 10, 20, 30, and 50 bins) on null conditions—a chosen n_bins should not fall into a peak-merging failure mode; (4) in observational marker-anchored analyses without experimental perturbations, treat PGAA output as marker-recovery or hypothesis-generation evidence, not causal inference; and (5) interpret PGAA-H permutation p-values as ranking evidence unless substantially deeper permutation depth (≥40,000) is used. The CLI (`pgaa-run`) accepts a normalized expression matrix and a metadata file with perturbation labels, optional covariates, and cluster labels, and returns a ranked gene table with PGAA-W score, PGAA-H score, permutation p-values, ranks, and calibration diagnostics.

Several limitations should be noted. First, the most relevant comparator, SCEPTRE, was not run on the Adamson benchmark because this proof-of-principle analysis uses a compact curated source-data benchmark rather than a full raw guide-level association workflow; SCEPTRE-family comparisons across Adamson-scale data require raw guide-level inputs that exceed the scope of this source-data reproducibility archive. The Norman CEBPE ELANE comparison provides a direct SCEPTRE reference point, but broader genome-scale SCEPTRE-family evaluation remains a critical gap. Second, the Adamson 2016 benchmark itself is small and has a sparse positive set (5 perturbations, 13 positives among 2,000 HVGs, one cell line), so it is insufficient for method-level validation; larger-scale evaluation on Replogle 2020/2022 or scPerturb-scale collections is required before general Perturb-seq claims. Third, PGAA-H currently has limited demonstrated utility beyond two specific cases (BHLHE40 CRISPRi per-perturbation AUROC 0.833 and CEBPE CRISPRa ELANE/PRTN3 ranking); broader evaluation across multiple perturbations, cell types, and response modalities is required before PGAA-H can be recommended as a general-purpose diagnostic. Fourth, the Norman multi-perturbation extension uses curated target-program panels rather than an original-study genome-wide DEG gold standard, and target-panel genes were not selected as HVGs in the processed Norman h5ad input; they were force-included to enable the benchmark. This means the benchmark evaluates relative ranking of a pre-specified gene panel rather than de novo target discovery. The sparse top-rank recovery should be viewed as ranking enrichment, not strong discovery performance. Fifth, PGAA-H calibration is perturbation-specific; the six-perturbation check showed uncapped upper-tail ratios from 0.10 (BAK1, over-sensitive) to 1.15 (KLF1, well-calibrated), so a negative control perturbation is essential. Sixth, the MI and Fisher NB modules are provided as software extensions but have not been benchmarked. Seventh, our simulation uses Gaussian noise for computational efficiency; we verified that PGAA-H does not spuriously increase under a zero-inflated negative-binomial null (mean PGAA-H = 0.031 with 30% dropout; Supplementary Methods), consistent with evidence that droplet-based scRNA-seq data are well-modeled by the negative binomial without explicit zero-inflation \textsuperscript{15}. Eighth, all primary benchmarks use K-means (k = 5) as a cell-state proxy; a sensitivity analysis on CLL 20k with k = 3, 5, 10 and no residualization found that PGAA-W AUROC was stable at 0.96 across all four conditions. Ninth, observational baseline comparisons (t-test, Wilcoxon) are reported only for the CLL dataset, where they are fully recomputable from included source files; the other four observational datasets lack bundled raw inputs for systematic conventional-baseline recomputation. Finally, the observational disease datasets do not establish new causal disease mechanisms or clinical biomarkers; instead, they show how PGAA can prioritize disease-relevant heterogeneous transcriptional responses for experimental follow-up.

PGAA fits into the growing ecosystem of Perturb-seq analysis tools and addresses a complementary computational use case. The pertpy framework \textsuperscript{11} provides an end-to-end pipeline into which PGAA's statistics could be integrated as modular ranking components. Mixscape \textsuperscript{16} handles the complementary problem of identifying cells with failed perturbations, while scMAGeCK \textsuperscript{17} operates at the CRISPR screen level. SCEPTRE \textsuperscript{5} and its robust extension \textsuperscript{18} set a high standard for calibrated permutation testing of mean shifts; PGAA extends this paradigm to distributional and histogram-shape shifts that may matter when only a subset of cells responds. Recent perturbation-response scoring methods quantify heterogeneous response strength at the single-cell level, whereas PGAA operates at the non-target-gene ranking level after coarse cell-state and library-size adjustment \textsuperscript{19}. Large curated resources such as scPerturb make broader cross-dataset benchmarking feasible, but this submission restricts itself to source-data-supported proof-of-principle and curated target-panel checks \textsuperscript{20}. Thus, PGAA should be read as a calibrated gene-level distributional ranking component that can sit alongside perturbation-quality, single-cell response-strength, and formal association-testing methods rather than as a replacement for them.

The most immediate priority is broader genome-scale evaluation on scPerturb-scale collections, including Replogle 2020/2022 and additional perturbation screens, where thousands of perturbations would allow a systematic assessment of calibration behavior and the identification of perturbation-level features that predict whether PGAA-W or PGAA-H will prove more informative. The main value of PGAA is not to replace mechanistic validation, but to provide a transparent and reproducible ranking layer for heterogeneous responses that can be followed up in perturbation screens, disease models, patient-derived systems, or therapeutic perturbation experiments.

## 4. Methods

### 4.1 Setup and residualization

We work with expression matrices normalized to 10,000 counts per cell and transformed with log1p. After standard QC and highly-variable gene selection (2,000 genes), each cell i has a perturbation label D_i in {0,1} and covariates Z_i. Before applying any statistic, we remove cell-type and library-size effects by ordinary least-squares residualization:

`X_tilde = X_res = (I - H_Z) X`

`H_Z = Z (Z^T Z)^+ Z^T`

where H_Z is the projection matrix for the covariate design matrix Z, X_tilde (also denoted X_res) is the residualized expression matrix, and (Z^T Z)^+ denotes the Moore--Penrose pseudoinverse used for numerical stability. The matrix Z contains an intercept, k - 1 K-means cluster dummy variables (k = 5, one reference cluster) \textsuperscript{21}, and standardized library size. This step is applied to the PGAA-W and PGAA-H statistics; the MI and Fisher NB exploratory scores operate on the original normalized matrix. The value of k is fixed throughout the benchmark as a coarse cell-state proxy rather than estimated from the data.

For a target perturbation g*, each non-target gene g is ranked by its perturbation-associated distributional discrepancy, measured as the quantile-grid Wasserstein distance (PGAA-W, Section 4.2) or the RMS histogram-peak-prominence distance (PGAA-H, Section 4.3).

To make notation consistent across Results and Supplementary Methods, we define the manuscript score functions as

`S1(g) = PGAA-W(g)` and `S2(g) = PGAA-H(g)`,

where each score uses the same residualized expression matrix `X_res`, the same perturbation labels `D_i`, and within-cluster permutations. For permutation testing, we use `B` permutations and report `p_perm`.

### 4.2 PGAA-W: 99-point quantile-grid Wasserstein approximation

We approximate the one-dimensional Wasserstein distance by comparing empirical quantile functions on a fixed 99-point percentile grid (r/100 for r = 1, …, 99). Throughout, "PGAA-W" refers to this quantile-grid approximation, not the exact continuous Wasserstein distance \(W_1 = \int_0^1 |F_1^{-1}(t) - F_0^{-1}(t)| dt\). Let Q_hat_{g,d}(u) denote the empirical u-quantile of residualized expression for gene g among cells with perturbation indicator D_i = d. The score is

`PGAA-W(g) = (1/99) sum_{r=1}^{99} |Q_hat_{g,1}(r/100) - Q_hat_{g,0}(r/100)|`

The 1D Wasserstein distance provides a non-parametric way to compare full one-dimensional distributions and can respond to changes in location, spread, or shape. This makes the statistic useful when the biological signal is not limited to a mean shift. The 1D case has an efficient quantile-based computation \textsuperscript{22,23}.

We compute p-values via within-cluster permutation \textsuperscript{24,25}. For B permutations, we shuffle D within each K-means cluster, recompute the Wasserstein statistic, and use the plus-one estimator

`p_perm = [1 + sum_{b=1}^{B} I{S_b >= S_obs}] / (B + 1)`

where S_obs is the observed statistic and S_b is the statistic from permutation b. The cluster-stratified shuffle preserves cell-type composition while randomizing the perturbation assignment. Although K-means cluster effects are already removed by the residualization step (Section 4.1), within-cluster permutation provides an additional nonparametric safeguard against residual cluster-level confounding that may survive the linear adjustment.

We do not z-standardize genes after residualization. PGAA-W is intended to preserve expression-scale information: genes with larger perturbation-induced expression shifts are typically of greater biological interest, and removing per-gene variance would discard this information. Users who wish to rank by distributional shape alone, independent of expression magnitude, may optionally standardize residuals to unit variance before applying PGAA-W; this option is not explored in the present benchmarks. Gene-level z-standardization sensitivity remains a limitation.

A note on numerical consistency. The observed and permuted W1 statistics are computed with the same 99-quantile approximation. This is essential because permutation p-values compare the observed statistic directly with its empirical null distribution. We confirmed approximate calibration under idealized Gaussian null conditions (2000 null gene-level tests across 10 simulations, N = 200 cells per simulation; empirical false positive rate 0.055, 95% CI [0.045, 0.065]). Real-data calibration may differ; the Storey upper-tail diagnostic (Section 4.6) provides a per-analysis calibration check.

### 4.3 PGAA-H histogram-shape diagnostic

The S2 histogram-shape statistic (PGAA-H) summarizes peak-structure changes in the one-dimensional expression histogram, such as the emergence or disappearance of modes. For each gene g, we compute histograms of the residualized expression for perturbed and control cells using n_bins = 20 equally spaced bins over the gene's pooled expression range. Histograms are normalized to probability mass (density) before peak-prominence calculation so that PGAA-H is invariant to different numbers of perturbed and control cells. Within each histogram, we identify local maxima (peaks) and compute the vertical drop from each peak to the higher of the two nearest minima on either side (peak prominence). This construction captures how sharply a peak stands out from the surrounding histogram terrain; a tall isolated peak has high prominence, whereas a broad plateau yields low prominence. For each condition, the three largest peak prominences are collected into a vector v_{g,d} (zero-padded when fewer than three peaks are present). Theoretical connections to one-dimensional persistent homology (Elder Rule) are noted in the references \textsuperscript{26--29} but the computation reduces to histogram binning and local-extremum annotation. Peak-prominence values depend on bin-edge placement as well as bin count. The recommended pilot n_bins sweep (Section 2.6) assesses whether peak-prominence results are stable under variation in bin count and, by extension, bin-edge location; using equal-width bins over the pooled expression range minimizes edge-placement artifacts in practice.

The PGAA-H statistic is the root-mean-square distance between the top-3 peak-prominence vectors:

`PGAA-H(g) = sqrt((1/3) * sum_{r=1}^{3} (v_{g,1,r} - v_{g,0,r})^2)`

where v_{g,d,r} is the r-th largest peak-prominence value for gene g in condition d (d = 1 for perturbed, d = 0 for control). This plain-text notation keeps the formula stable during DOCX and PDF conversion.

When a CRISPRa perturbation activates a gene in only a fraction of cells, the expression histogram can shift from a unimodal pattern to a bimodal one. The emergence of a second mode increases the top peak-prominence values, yielding larger PGAA-H scores. A pure mean shift that preserves the histogram shape leaves PGAA-H comparatively unchanged, making it complementary to the Wasserstein statistic. PGAA-H is interpreted here as a ranking and diagnostic statistic rather than a standalone genome-wide discovery test.

The choice of n_bins matters. Our sensitivity analysis (Section 2.6) tests n_bins values of 20, 30, 50, 75, 100, and 150. The manuscript starting setting, n_bins = 20, is acceptably calibrated in the Norman 2019 CEBPE run (uncapped upper-tail ratio approximately 1.0-1.3 depending on permutation depth). Larger values can produce more nominal hits at the cost of over-sensitive calibration. For new analyses, we recommend a guarded PGAA-H workflow: pre-specify a small n_bins grid such as 10, 20, 30 and 50; evaluate the grid on a negative-control, null, or unrelated perturbation; keep a setting only if the upper-tail diagnostic is acceptable and the p-value histogram is not over-sensitive; and then apply the chosen setting unchanged to the perturbation of interest. We use 500 within-cluster permutations for the null. With 500 permutations, the minimum attainable p-value is 1/501, approximately 0.0020, which is above the Bonferroni threshold for 2,000 genes (2.5e-5). The PGAA-H permutation p-values therefore support ranking-based evaluation (AUROC) rather than formal FDR-controlled discovery; for genome-wide significance, we recommend n_perms >= 40,000.

### 4.4 Additional modules

Two additional scoring modules are included in the software package as extensions. The conditional MI module explores whether perturbation alters gene-gene dependency structure via k-NN entropy estimators \textsuperscript{30}. The Fisher NB module explores perturbation-induced shifts using the Fisher information metric on the negative binomial family. These modules are not benchmarked or claimed as primary contributions; they are provided for users who wish to explore dependency or count-model effects. Algorithm details are given in the Supplementary Methods.

### 4.5 Combined exploratory z-score

Under independence and correct calibration, the combined exploratory z-score is

`z_comb = (1/sqrt(k)) sum_{j=1}^{k} Phi^{-1}(1 - p_j)`.

This score is asymptotically standard normal under H0. We use k = 2 (Wasserstein + PGAA-H) as an exploratory rank-combination score. Because both statistics are computed from the same expression distributions, the independence assumption is unlikely to hold exactly; formal combined-score inference would require an empirical covariance adjustment, Brown's method, or a permutation-calibrated combination. In this manuscript, the combined score is used only for exploratory ranking. For Norman 2019 CEBPE, PGAA-H alone ranked ELANE higher than the combination.

### 4.6 Calibration diagnostics

For calibration, PGAA reports the Storey upper-tail diagnostic \textsuperscript{31,32}. Let p_i be the permutation p-value for ranked gene i, let m be the number of ranked genes, and set lambda = 0.5. The uncapped upper-tail calibration ratio is

`R_lambda = #{i: p_i > lambda} / [(1 - lambda) * m]`.

The capped Storey null-fraction estimate is `pi0_hat(lambda) = min(1, R_lambda)`. The uncapped ratio R_lambda is reported separately as a calibration diagnostic: values near or above 1 indicate no obvious excess of small p-values, whereas values far below 1 indicate over-sensitivity or anti-conservative behavior. This wording avoids the mathematically incorrect implication that the null fraction pi0 itself can exceed 1. We also recommend running PGAA-H on an unrelated target gene from the same screen (e.g., KLF1 from Norman 2019) as a negative perturbation control, and verifying that the calibration diagnostic remains acceptable.

### 4.7 Datasets

We use seven publicly available datasets: five observational scRNA-seq datasets for marker-recovery stress checks and two Perturb-seq datasets for method benchmarking. The observational analyses include CLL (GSE111014; 36,601 cells, subsampled to 20,000; TCL1A high/low grouping with B-cell receptor markers), sepsis (GSE167363; 64,244 cells, subsampled to 20,000; TCR pathway markers), rheumatoid arthritis (GSE159117; 10,499 cells; cytokine pathway markers), the 10x Genomics 3k demo PBMC dataset \textsuperscript{33} (2,700 cells; multi-lineage markers), and inflammatory bowel disease (GSE116222; 11,175 cells; gut epithelial disease-associated markers).

The perturbation benchmarks are Norman 2019 (GSE133344) and Adamson 2016 (GSE90546). For Norman 2019, we use the K562 CRISPRa screen for the CEBPE ranking example, the six-perturbation PGAA-H calibration check, and the multi-perturbation PGAA-W extension across KLF1, CEBPE, and CEBPA. The six PGAA-H calibration perturbations are CEBPE, KLF1, SLC4A1, BAK1, DUSP9, and CBL; the CEBPE target set is ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, and RNASE2. The Norman multi-perturbation extension uses curated target-program panels for KLF1, CEBPE, and CEBPA, 2,000 HVGs plus forced inclusion of the panel genes, and non-targeting controls sampled at up to a 3:1 control-to-perturbed ratio. The comparator scores in that extension are PGAA-W Wasserstein, two-sample KS statistic, absolute Welch t statistic, and Wilcoxon -log10(p). For Adamson 2016, we analyze five pre-specified UPR-associated CRISPRi perturbations (SPI1, ZNF326, BHLHE40, CREB1, and DDIT3) against non-targeting controls, using the curated UPR marker set in Supplementary Table 1.

All datasets are normalized to 10,000 counts per cell and log-transformed after quality control. Analyses use 2,000 highly variable genes, with forced inclusion of target genes where needed.

### 4.8 Implementation

PGAA is implemented in Python and R. The Python package (`pgaa/`) depends on NumPy, SciPy, Pandas, Scanpy \textsuperscript{9}, and scikit-learn; the R package (`pgaa_r/`) uses only base R plus the MASS library. The submitted package includes Python and R smoke/regression checks for the core Wasserstein and PGAA-H calculations. On a single CPU core, the Wasserstein statistic processes 2,000 genes with 2,000 permutations in about five minutes; PGAA-H with 500 permutations takes under two minutes. Preprocessing follows standard scRNA-seq workflows \textsuperscript{34,35}, and the end-to-end ranking workflow is summarized in Supplementary Figure 6.






## Data availability

The study uses public datasets from Norman 2019 (GSE133344), Adamson 2016 (GSE90546), CLL (GSE111014), sepsis (GSE167363), rheumatoid arthritis (GSE159117), inflammatory bowel disease (GSE116222), and the 10x Genomics 3k demo PBMC dataset \textsuperscript{33}.

## Code availability

The public code-only repository is available under the MIT license at https://github.com/xutaoguo55/pgaa, with release `v0.1.0-code` at https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code. The public code-only release is archived at Zenodo, DOI https://doi.org/10.5281/zenodo.20681141, and by Software Heritage with SWHID `swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f`. The submitted supplementary software archive contains manuscript-specific source-data tables, figure-reproduction scripts, PDF build scripts, and additional reproducibility files for peer review. Norman 2019 CEBPE summaries are provided as processed source-data CSV files because full rerun requires setting `NORMAN2019_H5AD` to the processed Norman h5ad input used in this study; with that input available, we verified clean-archive reruns of the MMD-PSM comparator and the Norman multi-perturbation extension. The Adamson 2016 benchmark table is rebuilt from the accompanying curated source-data CSV by `scripts/rebuild_adamson_full_results.py`; `scripts/benchmark_adamson2016.py` also performs a raw GSE90546/GSM2406675 10X001 sanity rerun for the five selected perturbations. Implementation settings, reproducibility status, and comparator coverage are summarized in Supplementary Table 7. All random processes use `random_state=42` or equivalent fixed seeds.

## AI Tool Use

AI-assisted tools were used for language editing. The authors reviewed and approved the final text, analyses, and conclusions.

## Ethics statement

This study re-analyzes publicly available and previously published datasets. No new human participants, human samples, animals, or identifiable private information were collected for this study. Ethics approval and participant consent were handled by the original studies.

## Acknowledgements

The authors thank the investigators and database maintainers who generated and shared the public single-cell perturbation and disease datasets re-analyzed in this study.

## Author Contributions

X.W., H.Z., and J.H. contributed equally. X.G. conceived the study and designed the framework. X.W., H.Z., and J.H. implemented the software and performed the analyses. Q.W., Y.W., and R.F. contributed to data collection and biological interpretation. All authors wrote and approved the manuscript.

## Funding

No external funding was received for this work.

## Competing interests

None declared.



## Supplementary Information

The supplementary information contains Supplementary Figures 1-6, Supplementary Tables 1-7, and Supplementary Methods. These files include the Adamson UPR marker set and per-perturbation benchmark details, Norman multi-perturbation benchmark details, CEBPE target-level benchmark details, PGAA-H bin-sensitivity analysis, multi-dataset marker-recovery summary, implementation settings, reproducibility status, and additional implementation details.

## References

1. Dixit, A. et al. Perturb-Seq: dissecting molecular circuits with scalable single-cell RNA profiling of pooled genetic screens. *Cell* **167**, 1853--1866.e17 (2016).
2. Adamson, B. et al. A multiplexed single-cell CRISPR screening platform enables systematic dissection of the unfolded protein response. *Cell* **167**, 1867--1882.e21 (2016).
3. Norman, T. M. et al. Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. *Science* **365**, 786--793 (2019).
4. Replogle, J. M. et al. Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. *Cell* **185**, 2559--2575.e28 (2022).
5. Barry, T., Wang, X., Morris, J. A., Roeder, K. & Katsevich, E. SCEPTRE improves calibration and sensitivity in single-cell CRISPR screen analysis. *Genome Biol.* **22**, 344 (2021).
6. Finak, G. et al. MAST: a flexible statistical framework for assessing transcriptional changes and characterizing heterogeneity in single-cell RNA sequencing data. *Genome Biol.* **16**, 278 (2015).
7. Stuart, T. et al. Comprehensive integration of single-cell data. *Cell* **177**, 1888--1902.e21 (2019).
8. Hao, Y. et al. Integrated analysis of multimodal single-cell data. *Cell* **184**, 3573--3587.e29 (2021).
9. Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. *Genome Biol.* **19**, 15 (2018).
10. Gilbert, L. A. et al. Genome-scale CRISPR-mediated control of gene repression and activation. *Cell* **159**, 647--661 (2014).
11. Heumos, L. et al. Pertpy: an end-to-end framework for perturbation analysis. *Nat. Methods* **23**, 350--359 (2026).
12. Lozzio, C. B. & Lozzio, B. B. Human chronic myelogenous leukemia cell-line with positive Philadelphia chromosome. *Blood* **45**, 321--334 (1975).
13. Park, D. J. et al. CCAAT/enhancer binding protein epsilon is a potential retinoid target gene in acute promyelocytic leukemia treatment. *J. Clin. Invest.* **103**, 1399--1408 (1999).
14. Friedman, A. D. Transcriptional control of granulocyte and monocyte development. *Oncogene* **26**, 6816--6828 (2007).
15. Svensson, V. Droplet scRNA-seq is not zero-inflated. *Nat. Biotechnol.* **38**, 147--150 (2020).
16. Papalexi, E. et al. Characterizing the molecular regulation of inhibitory immune checkpoints with multimodal single-cell screens. *Nat. Genet.* **53**, 322--331 (2021).
17. Yang, L. et al. scMAGeCK links genotypes with multiple phenotypes in single-cell CRISPR screens. *Genome Biol.* **21**, 19 (2020).
18. Barry, T., Mason, K., Roeder, K. & Katsevich, E. Robust differential expression testing for single-cell CRISPR screens at low multiplicity of infection. *Genome Biol.* **25**, 124 (2024).
19. Song, B. et al. Decoding heterogeneous single-cell perturbation responses. *Nat. Cell Biol.* **27**, 493--504 (2025).
20. Peidli, S. et al. scPerturb: harmonized single-cell perturbation data. *Nat. Methods* **21**, 531--540 (2024).
21. MacQueen, J. Some methods for classification and analysis of multivariate observations. In *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability* Vol. 1, 281--297 (University of California Press, 1967).
22. Villani, C. *Optimal Transport: Old and New* (Springer, 2009).
23. Ramdas, A., Garcia Trillos, N. & Cuturi, M. On Wasserstein two-sample testing and related families of nonparametric tests. *Entropy* **19**, 47 (2017).
24. Good, P. I. *Permutation, Parametric, and Bootstrap Tests of Hypotheses*, 3rd edn (Springer, 2005).
25. Efron, B. & Tibshirani, R. J. *An Introduction to the Bootstrap* (Chapman & Hall, 1993).
26. Edelsbrunner, H. & Harer, J. *Computational Topology: An Introduction* (American Mathematical Society, 2010).
27. Bubenik, P. Statistical topological data analysis using persistence landscapes. *J. Mach. Learn. Res.* **16**, 77--102 (2015).
28. Zomorodian, A. & Carlsson, G. Computing persistent homology. *Discrete Comput. Geom.* **33**, 249--274 (2005).
29. Carlsson, G. Topology and data. *Bull. Am. Math. Soc.* **46**, 255--308 (2009).
30. Kraskov, A., Stogbauer, H. & Grassberger, P. Estimating mutual information. *Phys. Rev. E* **69**, 066138 (2004).
31. Storey, J. D. A direct approach to false discovery rates. *J. R. Stat. Soc. Ser. B* **64**, 479--498 (2002).
32. Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J. R. Stat. Soc. Ser. B* **57**, 289--300 (1995).
33. Zheng, G. X. Y. et al. Massively parallel digital transcriptional profiling of single cells. *Nat. Commun.* **8**, 14049 (2017).
34. Luecken, M. D. & Theis, F. J. Current best practices in single-cell RNA-seq analysis: a tutorial. *Mol. Syst. Biol.* **15**, e8746 (2019).
35. Lun, A. T. L., McCarthy, D. J. & Marioni, J. C. A step-by-step workflow for low-level analysis of single-cell RNA-seq data with Bioconductor. *F1000Research* **5**, 2122 (2016).
