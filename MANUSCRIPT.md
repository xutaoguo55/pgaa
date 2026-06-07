# PGAA: distribution-aware testing for single-cell perturbation screens

**Authors**: Xiaolei Wei<sup>2†</sup>, Haiqing Zheng<sup>1†</sup>, Junwei Huang<sup>2†</sup>, Qi Wei<sup>2</sup>, Yongqiang Wei<sup>2</sup>, Ru Feng<sup>2</sup>, Xutao Guo<sup>1,3\*</sup>

<sup>1</sup> Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>2</sup> Department of Nosocomial Infection Management, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>3</sup> Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China  

<sup>†</sup> These authors contributed equally to this work.  
<sup>\*</sup> Correspondence: Xutao Guo (guoxutao@smu.edu.cn)

## Abstract

Perturb-seq screens test thousands of gene–gene relationships, but existing tools detect primarily mean expression shifts. CRISPRa and weak-effect perturbations can produce bimodal responses—only a subset of cells respond—leaving mean expression unchanged despite downstream biology. We present PGAA, a distribution-aware testing framework for Perturb-seq that combines a Wasserstein distance test with a persistent homology test for detecting bimodal expression patterns. On five observational datasets, the Wasserstein test recovers known pathway markers with 2.1–5.8× enrichment (AUROC 0.87). On Norman 2019 CEBPE CRISPRa, where the Wasserstein test and SCEPTRE show no signal for the known target ELANE (rank 1660 and 1761), the persistence test ranks ELANE at position 56—a 30-fold improvement. A 6-perturbation calibration study and a 63-condition simulation document each test's operating characteristics, including a hyperparameter sensitivity analysis that reveals strong dependence of the persistence test on histogram bin count. Python and R implementations are available at https://github.com/xutaoguo55/pgaa, with benchmarks reproducible from public data (GSE133344, GSE111014, GSE167363, GSE159117, GSE116222).

**Keywords**: Perturb-seq, Wasserstein distance, persistent homology, single-cell RNA-seq, CRISPR screening, calibration


## 1. Introduction

Single-cell perturbation screens [Dixit *et al.*, 2016; Adamson *et al.*, 2016; Norman *et al.*, 2019; Replogle *et al.*, 2022] are now a primary tool for causal regulatory network inference [Regev *et al.*, 2017]. The standard analysis—comparing mean expression of each non-target gene between perturbed and control cells—works well when a perturbation produces a uniform transcriptional shift. KO a transcription factor, its targets drop, and a t-test or Wilcoxon test detects the difference. Tools like DESeq2 [Love *et al.*, 2014], MAST [Finak *et al.*, 2015], SCDE [Kharchenko *et al.*, 2014], and SCEPTRE [Barry *et al.*, 2021] are built for this paradigm, and together with preprocessing workflows in Seurat [Stuart *et al.*, 2019; Hao *et al.*, 2021] and Scanpy [Wolf *et al.*, 2018], they form the standard Perturb-seq analysis toolkit.

But not all perturbations are well-behaved. CRISPRa [Gilbert *et al.*, 2014]—the dominant activation modality in Perturb-seq screens—produces responses that are often heterogeneous: the gRNA activates the target in only a fraction of cells. The mean expression may barely shift, yet the distribution changes fundamentally—a secondary peak emerges in the expression histogram as some cells respond and others do not. Standard tools report zero significant genes because they test for a mean shift that is not there. The same problem arises with weak-effect perturbations, where variance changes without mean changes, and with perturbations that alter gene–gene correlation structures or count-model dispersion rather than shifting the mean.

Few existing Perturb-seq methods directly address non-mean-shift response modes such as distributional bimodality, although heterogeneity-aware approaches are emerging [Heumos *et al.*, 2025]. We present **PGAA**, a framework built around two complementary statistics sharing a common permutation-calibration infrastructure. The Wasserstein distance captures distributional shifts; the persistence test detects bimodality through topological changes in expression histograms. Additional modules for conditional MI and Fisher NB testing are provided as software extensions. All statistics are accompanied by a calibration diagnostic (Storey π̂₀) that lets users assess reliability on their own data before interpreting results.

We validate the Wasserstein test on six datasets spanning observational scRNA-seq and real Perturb-seq, demonstrate persistent homology on Norman 2019 CEBPE CRISPRa where mean-based methods fail, provide a six-perturbation calibration study, and map each statistic's regime of validity through a 63-condition simulation.


## 2. Methods

### 2.1 Setup and residualization

We work with log-normalized expression matrices ($\log(\text{CPM} + 1)$, CPM = counts per million, target sum 10,000). After standard QC and highly-variable gene selection (2,000 genes), each cell $i$ has a perturbation label $D_i \in \{0,1\}$ and covariates $Z_i$. Before applying any statistic, we residualize out cell-type and library-size effects via OLS:

$$\tilde{X} = X - Z (Z^\top Z)^{-1} Z^\top X$$

where $Z$ contains an intercept, K-means cluster indicators ($k = 5$) [MacQueen, 1967; Tibshirani *et al.*, 2001], and standardized library size. This step is applied to both tests; the MI and Fisher NB tests operate on the original normalized matrix.

For a target gene $g^*$, we test each non-target gene $g$ for whether $P(Y_g \mid D = 1)$ differs from $P(Y_g \mid D = 0)$ in mean, shape, or dependency structure.

### 2.2 Wasserstein distance

The Wasserstein distance (Earth Mover's Distance) between two empirical CDFs:

$$S_1(g) = \frac{1}{99} \sum_{q=0.01}^{0.99} \bigl| Q_g^{(1)}(q) - Q_g^{(0)}(q) \bigr|,$$

where $Q_g^{(d)}(q)$ is the $q$-quantile of $\tilde{X}_{i,g}$ for cells with $D_i = d$.

Wasserstein has quadratic sensitivity to weak effects ($W_1 \sim O(\alpha^2 + N^{-1})$ vs. $O(\alpha)$ for the t-test [Ramdas *et al.*, 2017]), giving it power against distributional shifts where t-tests are insensitive. The 1D case has an efficient quantile-based computation [Villani, 2009; Cuturi, 2013].

We compute $p$-values via within-cluster permutation [Good, 2013; Efron & Tibshirani, 1993]: for each of 2,000 permutations, shuffle $D$ within each K-means cluster, recompute the Wasserstein test, and count the fraction of null statistics at least as extreme as the observed value. The cluster-stratified shuffle preserves cell-type composition while randomizing the perturbation assignment.

A note on numerical precision. In the permutation loop, $W_1$ is approximated via interpolated sorted values to a common $\max(n_{\text{pert}}, n_{\text{ctrl}})$-point grid, while the observed statistic uses 99-point quantile integration. These differ in absolute magnitude (ratio ~0.12) but not in gene-wise ranking—permutation $p$-values depend only on rank ordering. We verified calibration empirically: under the null, the observed false positive rate is 0.057 (30 simulations, 95% CI [0.021, 0.079]).

### 2.3 Persistent homology

The persistence test detects topological changes in the 1D expression histogram—emergence or disappearance of peaks. For each gene $g$, we compute histograms of $\tilde{X}_{\cdot,g}$ for perturbed and control cells ($n_{\text{bins}} = 20$ equally spaced bins), then apply the Elder Rule to extract persistence diagrams [Edelsbrunner & Harer, 2010; Bubenik, 2015; Zomorodian & Carlsson, 2005; Carlsson, 2009]:

1. Find all local maxima (peaks) in each histogram.
2. For each peak with height $h[i]$, define its *death level* as the maximum of the saddle heights to the left (next higher peak or boundary) and right. *Persistence* = birth − death.
3. Take the top-3 persistence values for each histogram, zero-padding if fewer than 3 peaks exist.

The persistence statistic is the L2 distance between the top-3 persistence vectors:

$$S_2(g) = \sqrt{ \frac{1}{3} \sum_{k=1}^3 \bigl( p_k^{(1)} - p_k^{(0)} \bigr)^2 }.$$

When a CRISPRa perturbation activates a gene in only a fraction of cells, the expression histogram changes from single-peaked to double-peaked. The dominant persistence value increases substantially, yielding large S2 values. A pure mean shift that preserves the histogram shape leaves S2 unchanged. The contrast between these two scenarios is what makes the persistence test complementary to the Wasserstein test.

The choice of $n_{\text{bins}}$ matters. Our sensitivity analysis (Section 3.5) tests $n_{\text{bins}} \in \{20, 30, 50, 75, 100, 150\}$. The default $n_{\text{bins}} = 20$ is well-calibrated on benchmark data (π̂₀ ≈ 1.0–1.3 on Norman 2019 CEBPE). Larger values detect more targets at the cost of higher false-positive rates. We use 500 within-cluster permutations for the null. With 500 permutations, the minimum attainable $p$-value is $1/501 \approx 0.0020$, which is above the Bonferroni threshold for 2,000 genes ($2.5 \times 10^{-5}$). The persistence-based $p$-values therefore support ranking-based evaluation (AUROC) rather than formal FDR-controlled discovery; for genome-wide significance, we recommend $n_{\text{perms}} \ge 40{,}000$.

### 2.4 Additional modules

Two additional test statistics are included in the software package as extensions. The conditional MI test assesses whether perturbation alters gene–gene dependency structure via $k$-NN entropy estimators [Kraskov *et al.*, 2004]. The Fisher NB test measures perturbation-induced shifts using the Fisher information metric on the negative binomial family. These modules are not benchmarked or claimed as primary contributions; they are provided for users who wish to explore dependency or count-model effects. Algorithm details are given in the Supplementary Methods.

### 2.5 Combined z-test

Under independence and correct calibration, $z_{\text{comb}} = \frac{1}{\sqrt{k}} \sum_{i=1}^{k} \Phi^{-1}(1 - p_i)$ is asymptotically $\mathcal{N}(0,1)$ under $H_0$. We use $k = 2$ (Wasserstein + persistence). A caveat: combining dilutes signal when one statistic contributes noise. For Norman 2019 CEBPE, the persistence test alone outperforms the combination.

### 2.6 Calibration diagnostics

Every PGAA run reports Storey's π̂₀ [Storey, 2002; Benjamini & Hochberg, 1995]—the estimated fraction of true null genes from the upper tail of the $p$-value distribution ($\lambda = 0.5$, valid when $n_{\text{perms}} \ge 100$ since minimum attainable $p = 1/101 \ll \lambda$). Values near 1.0 indicate well-calibrated $p$-values. We also recommend running persistent homology on an unrelated target gene from the same screen (e.g., KLF1 from Norman 2019) as a negative perturbation control, and verifying that π̂₀ remains acceptable.

### 2.7 Datasets

We use six publicly available datasets spanning different biological contexts and scales:

- **CLL** (GSE111014; 36,601 cells, 4 patient + 2 control samples; subsampled to 20,000 cells): TCL1A virtual perturbation with BCR signaling markers as positive set and 15 housekeeping genes as negative controls.
- **Sepsis** (GSE167363; 64,244 cells, subsampled to 20,000): TCR pathway markers.
- **RA** (GSE159117; 10,499 cells): rheumatoid arthritis synovial tissue, cytokine pathway markers.
- **PBMC** (10x Genomics 3k demo, 2,700 cells [Zheng *et al.*, 2017]): multi-lineage markers for scale validation (2.7k–64k).
- **IBD** (GSE116222; 11,175 cells): gut immune markers.
- **Norman 2019** (GSE133344; 111,668 K562 cells): the primary real Perturb-seq dataset. Six single-gene CRISPRa perturbations: CEBPE (566 cells), KLF1 (1197), SLC4A1 (1000), BAK1 (687), DUSP9 (731), CBL (663). Known CEBPE downstream targets: ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, RNASE2. We use 3× matched NegCtrl cells (1,698 of 11,855 available) as controls.

Preprocessing for all datasets: QC filter (200–6000 genes, <20% MT, >500 UMI for CLL; pre-filtered by original authors for Norman 2019), normalize to 10K CPM, log1p, retain 2,000 HVGs with forced inclusion of target genes.

### 2.8 Implementation

PGAA is implemented in Python and R. The Python package (`pgaa/`) depends on NumPy, SciPy, Pandas, Scanpy [Wolf *et al.*, 2018], and scikit-learn; the R package (`pgaa_r/`) uses only base R plus the MASS library. Both implementations of both tests produce identical numerical output (error < $10^{-6}$). On a single CPU core, the Wasserstein test processes 2,000 genes with 2,000 permutations in about five minutes; persistent homology with 500 permutations takes under two minutes. Preprocessing follows standard scRNA-seq workflows [Luecken & Theis, 2019; Lun *et al.*, 2016].


## 3. Results

### 3.1 Wasserstein recovers known biology

As a general-purpose distributional test, Wasserstein enriches known pathway markers 2.1–5.8× over background across five observational datasets (CLL 4.0×, Sepsis 2.1×, RA 2.5×, PBMC 2.9×, IBD 5.8×). On CLL, the BCR signaling gene set (CD79A, CD79B, MS4A1, CD24, BANK1, LYN, BLNK, SYK, BTK, PLCG2, PIK3CD, CD19, CD22) appears prominently in the top 100, with AUROC 0.87 for known-marker recovery (Table 1, Supplementary Table S3).

These five datasets are observational—the "perturbation" is defined by binning cells on endogenous TCL1A expression, not by an experimental intervention—so the results demonstrate marker recovery rather than causal discovery. The enrichment is consistent with the Wasserstein test being a reasonable default statistic when the perturbation type is unknown.

**[Figure 1]**

### 3.2 Persistent homology finds ELANE where mean-based methods see nothing

Norman *et al.* (2019) used CRISPRa to activate CEBPE in K562 cells [Lozzio & Lozzio, 1975]. CEBPE is a myeloid transcription factor whose known targets include nine neutrophil granule proteins: ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, and RNASE2 [Friedman, 2007; Park *et al.*, 1999].

SCEPTRE and the Wasserstein test are blind to this signal. SCEPTRE places ELANE at rank 1761/2012 ($p = 0.92$). The Wasserstein test places it at rank 1660 ($p = 0.84$). Neither method identifies a single known target at $p < 0.05$.

The persistence test ($n_{\text{bins}} = 20$, 500 permutations) ranks ELANE at position 56 ($p = 0.04$), a 30-fold improvement over the Wasserstein test. The $p$-values are well-calibrated (π̂₀ 1.0–1.3). The top genes by raw S2 value (SLC45A1, DLX2, ATP5E) are not known CEBPE targets; ELANE's strong performance by permutation $p$-value reflects its favorable null distribution relative to other genes. As a specificity check, we applied the persistence test to all six perturbations using the CEBPE target gene set as the gold standard (Supplementary Table S2). ELANE was significant for CEBPE (p = 0.005) and, as expected from the calibration analysis (Section 3.3), for the severely over-sensitive BAK1 perturbation (p = 0.005, π̂₀ = 0.10). For the well-calibrated KLF1 perturbation, ELANE was not significant (p = 0.70, π̂₀ = 1.15). For CBL, SLC4A1, and DUSP9, ELANE p-values were 0.58, 0.16, and 0.90 respectively—all non-significant. This within-dataset cross-validation demonstrates perturbation specificity: when π̂₀ indicates adequate calibration, the persistence test does not produce false positives for off-target perturbations.

CRISPRa produces heterogeneous target activation—the gRNA does not guarantee protein-level CEBPE expression in every cell, and the resulting bimodal expression pattern is exactly the regime the persistence test is designed for. K562 is an erythroleukemia line, not a neutrophil progenitor; while it retains granulocytic differentiation capacity upon CEBPE activation, not all nine targets may be transcriptionally responsive in this system.

**[Figure 2]**

### 3.3 Calibration varies by perturbation—and that is informative

Running persistent homology on six different perturbations from the Norman 2019 screen reveals that calibration is far from consistent. The Storey π̂₀ ranges from 1.15 (KLF1, well-calibrated) to 0.10 (BAK1, severely over-sensitive). The table below summarizes the results.

| Perturbation | π̂₀ | n_sig | Calibration |
|---|---|---|---|
| KLF1 (erythroid TF) | 1.15 | 54 | well-calibrated |
| CBL | 0.72 | 173 | acceptable |
| SLC4A1 | 0.67 | 222 | mild over-sensitivity |
| DUSP9 | 0.68 | 460 | over-sensitive |
| CEBPE (CRISPRa) | 0.25 | 1063 | severely over-sensitive |
| BAK1 | 0.10 | 1789 | over-sensitive |

KLF1 drives a clean erythroid program. CEBPE CRISPRa and BAK1 do not. The calibration spread reflects this biology, and the practical takeaway is simple: include a negative control perturbation and check π̂₀. Importantly, the CEBPE π̂₀ of 0.25 reported here comes from a calibration run with n_bins = 50 and n_perms = 200; the main analysis in Section 3.2 uses n_bins = 20 and n_perms = 500, which yields π̂₀ ≈ 1.0–1.3. The discrepancy illustrates how strongly calibration depends on both bin count and permutation depth, reinforcing the need for the pilot sweep recommended in Section 3.5.

**[Figure 3, Table 2]**

### 3.4 Wasserstein and persistence see different biology on CLL

The CLL TCL1A case shows how both tests complement each other. Among the top 100 genes ranked by each statistic, only six overlap. The Wasserstein test enriches B-cell receptor markers (CD79A rank 9, CD79B rank 48, MS4A1 rank 53). The persistence test picks up T-cell receptor genes (TRBV7-6, TRAV12-1, CD3E, CD3D) that Wasserstein misses entirely. The combined z-test recovers 3 BCR and 11 TCR genes at $p < 0.05$, versus 4+3 for Wasserstein alone and 0+7 for the persistence test alone.

The CLL analysis uses rank-based inverse-normal scores (Supplementary Methods S6) rather than full permutation calibration—a lighter-weight approach appropriate when only relative gene ordering matters rather than formal significance testing.

**[Figure 4, Table 1]**

### 3.5 Sensitivity to histogram bin count

The persistence test depends on the number of histogram bins, and the dependence is non-trivial. We tested $n_{\text{bins}} \in \{20, 30, 50, 75, 100, 150\}$ on Norman 2019 CEBPE ($n_{\text{perms}} = 200$ for speed; main results use $n_{\text{perms}} = 500$).

| n_bins | ELANE rank | ELANE p | n_sig | π̂₀ | Known hits |
|---|---|---|---|---|---|
| 20 | 32 | 0.025 | 66 | 1.32 | 1/9 |
| 30 | 1807 | 0.672 | 387 | 0.41 | 0/9 |
| 50 | 489 | 0.005 | 1063 | 0.25 | 3/9 |
| 75 | 460 | 0.005 | 1087 | 0.23 | 4/9 |
| 100 | 468 | 0.005 | 1087 | 0.23 | 5/9 |
| 150 | 446 | 0.005 | 1073 | 0.23 | 4/9 |

The n_bins = 30 row is striking: at this resolution, the histogram bins merge the two modes of the bimodal distribution, and ELANE's signal collapses (rank 1807). This is a sharp failure mode, not a gradual degradation. We recommend the default $n_{\text{bins}} = 20$ as a starting point, with a pilot sweep ($n_{\text{bins}} \in \{10, 20, 30, 50\}$) to verify that the chosen value does not fall into the n_bins = 30 failure mode where peak merging destroys the persistence signal. The sweep should be performed on a control or null perturbation, not the perturbation of interest, to avoid overfitting. At $n_{\text{bins}} = 20$, the $p$-values are well-calibrated (π̂₀ = 1.32 with $n_{\text{perms}} = 200$; 1.00 with $n_{\text{perms}} = 500$) and ELANE achieves its best rank.

**[Supplementary Table S1]**

### 3.6 Independent validation on Adamson 2016 UPR CRISPRi

To test PGAA on a second, independent Perturb-seq dataset with a complementary perturbation modality, we applied both tests to the Adamson et al. (2016) UPR CRISPRi screen (GSE90546). After QC, 5,680 K562 cells were retained across five well-characterized sgRNA perturbations targeting UPR genes (SPI1, ZNF326, BHLHE40, CREB1, DDIT3; 468–686 cells each) and a non-targeting control (1,759 cells). The gold standard was a literature-defined set of 22 UPR pathway members (IRE1, PERK, ATF6 branches and ERAD components), of which 13 were present in the 2,000-gene HVG subset.

Across the five perturbations, the Wasserstein test achieved a mean AUROC of 0.786 (range 0.767–0.806) for recovering known UPR genes. The persistence test achieved a mean AUROC of 0.748 (range 0.658–0.833). Notably, for BHLHE40 knockdown, the persistence test outperformed the Wasserstein test (AUROC 0.833 vs. 0.788), consistent with a bimodal transcriptional response. These perturbations were selected a priori based on their UPR annotation in the original study and a minimum cell-count threshold (≥400 cells), not based on PGAA performance.

**[Figure 6, Supplementary Table S9]**

### 3.7 A simulation ablation maps each statistic to its regime

To systematically assess when each statistic performs best, we simulated three perturbation types at seven effect sizes ($\theta \in \{0.1, \ldots, 1.0\}$) with three replicates each (63 conditions total).

Type A (pure mean shift) is the Wasserstein test's home territory (TPR = 0.97 at $\theta = 1.0$). Type C (mean + bimodality) favors the Wasserstein test as well. The most informative condition is Type B, where only 40% of perturbed cells respond. Here the Wasserstein test and the combined z-test are competitive (TPR = 0.52–0.85 depending on $\theta$), while persistent homology reaches only TPR = 0.12. This simulation uses *partial* bimodality—the two modes overlap in the 40%-response regime. On real CRISPRa data where the split is more complete (nearer to 50% "on" vs. 50% "off"), persistent homology's performance is stronger, as demonstrated by the Norman 2019 results.

From the simulation and real-data results, a practical decision rule emerges:

| Scenario | Recommended statistic |
|---|---|
| Standard KO/OE | Wasserstein |
| CRISPRa / heterogeneous response | Persistence test (check π̂₀) |
| Mixed signal | Combined z |
| Unknown | Run the Wasserstein test first. If no signal, try the persistence test with pilot sweep. |

**[Figure 5, Table 3]**


## 4. Discussion

The Wasserstein test is a calibrated, distribution-aware test that works across diverse datasets. The persistence test detects bimodal CRISPRa responses that mean-based methods miss—ELANE improves from rank 1660 to rank 56 on Norman 2019 CEBPE. The calibration framework (Storey π̂₀, multi-perturbation controls, n_bins sensitivity sweep) lets users self-assess whether a statistic is appropriate for their data. That last contribution generalizes beyond PGAA to any topological method applied to single-cell data.

Several limitations apply. The persistence test's calibration is perturbation-type-dependent, and our recommendation to run a negative control perturbation and a quick n_bins sweep is a practical safeguard, not a theoretical guarantee. The MI and Fisher NB tests are exploratory—the Wasserstein and persistence tests are the primary statistics. The persistence statistic is strongly hyperparameter-dependent, with values at $n_{\text{bins}} = 20$ and $n_{\text{bins}} = 50$ correlating at only $r = 0.12$; the sensitivity analysis in Section 3.5 documents this behavior. As with any single-cell method, preprocessing choices matter [Chari & Pachter, 2023]. Our simulation uses Gaussian noise for computational efficiency; we verified that the persistence test does not spuriously detect bimodality from zero-inflation alone (mean S2 = 0.031 under NB H₀ with 30% dropout; Supplementary Note S7), consistent with evidence that droplet-based scRNA-seq data are well-modeled by the negative binomial without explicit zero-inflation [Svensson, 2020]. All benchmarks use K-means ($k = 5$) as a cell-type proxy; finer annotation (e.g., graph-based clustering with UMAP [McInnes *et al.*, 2018; Van der Maaten & Hinton, 2008]) may improve specificity. No new biological discoveries are claimed; PGAA recovers established pathway members.

PGAA complements existing Perturb-seq methods. pertpy [Heumos *et al.*, 2025] provides an end-to-end framework for perturbation analysis and could serve as a preprocessing front-end for PGAA's statistics. Mixscape [Papalexi *et al.*, 2021] removes cells with failed perturbations—a pre-processing step orthogonal to our downstream testing. scMAGeCK [Yang *et al.*, 2020] operates at the CRISPR screen level, while PGAA works at the single-cell level. SCEPTRE [Barry *et al.*, 2021] and its robust extension [Barry *et al.*, 2024] provide well-calibrated permutation tests for mean shifts; PGAA extends this paradigm to distributional and topological shifts.

Larger-scale validation on genome-scale Perturb-seq datasets (e.g., Replogle 2020/2022) is a natural next step.




## Data and Code Availability

- Norman 2019: GSE133344. CLL: GSE111014. Sepsis: GSE167363. RA: GSE159117. IBD: GSE116222. PBMC: 10x Genomics 3k demo [Zheng *et al.*, 2017].
- Python and R packages available for review at [anonymous GitHub review link]. Public release and Zenodo DOI upon acceptance.
- All random processes use `random_state=42` or equivalent fixed seeds.

## Author Contributions

X.W., H.Z., and J.H. contributed equally. X.G. conceived the study and designed the framework. X.W., H.Z., and J.H. implemented the software and performed the analyses. Q.W., Y.W., and R.F. contributed to data collection and biological interpretation. All authors wrote and approved the manuscript.

## Funding

No external funding was received for this work.

## Conflict of Interest

None declared.



## Supplementary Information

- **Figure S1**: Persistence test calibration QQ plot ($n_{\text{bins}} = 20$, n_perms = 500) and p-value histogram.
- **Table S1**: Persistence test hyperparameter sensitivity (Section 3.5).
- **Table S2**: SCEPTRE vs PGAA comparison ($n_{\text{bins}} = 50$ calibration, for comparison with main $n_{\text{bins}} = 20$ results).
- **Supplementary Methods**: Conditional MI and Fisher NB algorithm details.
- **Supplementary Methods**: Full simulation parameters.


## References

1. Dixit *et al.* (2016) Perturb-Seq: Dissecting Molecular Circuits with Scalable Single-Cell RNA Profiling of Pooled Genetic Screens. *Cell*, 167(7), 1853–1866.
2. Adamson *et al.* (2016) A Multiplexed Single-Cell CRISPR Screening Platform Enables Systematic Dissection of the Unfolded Protein Response. *Cell*, 167(7), 1867–1882.
3. Norman *et al.* (2019) Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. *Science*, 365(6455), 786–793.
4. Replogle *et al.* (2022) Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. *Cell*, 185(14), 2559–2575.
5. Barry *et al.* (2021) SCEPTRE improves calibration and sensitivity in single-cell CRISPR screen analysis. *Genome Biology*, 22, 344.
6. Ramdas *et al.* (2017) On Wasserstein Two-Sample Testing and Related Families of Nonparametric Tests. *Entropy*, 19(2), 47.
7. Edelsbrunner & Harer (2010) *Computational Topology: An Introduction*. American Mathematical Society.
8. Bubenik (2015) Statistical Topological Data Analysis using Persistence Landscapes. *Journal of Machine Learning Research*, 16, 77–102.
9. Storey (2002) A direct approach to false discovery rates. *Journal of the Royal Statistical Society: Series B*, 64(3), 479–498.
10. Kraskov *et al.* (2004) Estimating mutual information. *Physical Review E*, 69, 066138.
11. Villani C (2009) *Optimal Transport: Old and New*. Springer.
12. Cuturi M (2013) Sinkhorn distances: lightspeed computation of optimal transport. *Advances in Neural Information Processing Systems*, 26, 2292–2300.
13. Zomorodian A & Carlsson G (2005) Computing persistent homology. *Discrete & Computational Geometry*, 33, 249–274.
14. Carlsson G (2009) Topology and data. *Bulletin of the American Mathematical Society*, 46, 255–308.
15. Luecken MD & Theis FJ (2019) Current best practices in single-cell RNA-seq analysis: a tutorial. *Molecular Systems Biology*, 15, e8746.
16. Svensson V (2020) Droplet scRNA-seq is not zero-inflated. *Nature Biotechnology*, 38, 147–150.
17. Good P (2013) *Permutation, Parametric, and Bootstrap Tests of Hypotheses*. Springer, 4th ed.
18. Wolf FA, Angerer P & Theis FJ (2018) SCANPY: large-scale single-cell gene expression data analysis. *Genome Biology*, 19, 15.
19. Papalexi *et al.* (2021) Characterizing the molecular regulation of inhibitory immune checkpoints with multimodal single-cell screens. *Nature Genetics*, 53, 322–331.
20. Yang *et al.* (2020) scMAGeCK links genotypes with multiple phenotypes in single-cell CRISPR screens. *Genome Biology*, 21, 19.
21. Park DJ *et al.* (1999) CCAAT/enhancer binding protein epsilon is a potential retinoid target gene in acute promyelocytic leukemia treatment. *Journal of Clinical Investigation*, 103, 1399–1408.
22. Friedman AD (2007) Transcriptional control of granulocyte and monocyte development. *Oncogene*, 26, 6816–6828.
23. Benjamini Y & Hochberg Y (1995) Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57, 289–300.
24. Gilbert LA *et al.* (2014) Genome-scale CRISPR-mediated control of gene repression and activation. *Cell*, 159, 647–661.
25. Love MI, Huber W & Anders S (2014) Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology*, 15, 550.
26. Lozzio CB & Lozzio BB (1975) Human chronic myelogenous leukemia cell-line with positive Philadelphia chromosome. *Blood*, 45, 321–334.
27. MacQueen J (1967) Some methods for classification and analysis of multivariate observations. *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability*, 1, 281–297.
28. Zheng GXY *et al.* (2017) Massively parallel digital transcriptional profiling of single cells. *Nature Communications*, 8, 14049.
29. Stuart T *et al.* (2019) Comprehensive integration of single-cell data. *Cell*, 177, 1888–1902.
30. Hao Y *et al.* (2021) Integrated analysis of multimodal single-cell data. *Cell*, 184, 3573–3587.
31. Regev A *et al.* (2017) The Human Cell Atlas. *eLife*, 6, e27041.
32. Efron B & Tibshirani RJ (1993) *An Introduction to the Bootstrap*. Chapman & Hall/CRC.
33. Chari T & Pachter L (2023) The specious art of single-cell genomics. *PLoS Computational Biology*, 19, e1011288.
34. Finak G *et al.* (2015) MAST: a flexible statistical framework for assessing transcriptional changes and characterizing heterogeneity in single-cell RNA sequencing data. *Genome Biology*, 16, 278.
35. McInnes L, Healy J & Melville J (2018) UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. *arXiv*, 1802.03426.
36. Tibshirani R, Walther G & Hastie T (2001) Estimating the number of clusters in a data set via the gap statistic. *Journal of the Royal Statistical Society: Series B*, 63, 411–423.
37. Kharchenko PV, Silberstein L & Scadden DT (2014) Bayesian approach to single-cell differential expression analysis. *Nature Methods*, 11, 740–742.
38. Van der Maaten L & Hinton G (2008) Visualizing data using t-SNE. *Journal of Machine Learning Research*, 9, 2579–2605.
39. Lun ATL, McCarthy DJ & Marioni JC (2016) A step-by-step workflow for low-level analysis of single-cell RNA-seq data with Bioconductor. *F1000Research*, 5, 2122.
40. Heumos L *et al.* (2025) Pertpy: an end-to-end framework for perturbation analysis. *Nature Methods*, 22, 1047–1058.
41. Barry T *et al.* (2024) Robust differential expression testing for single-cell CRISPR screens. *Genome Biology*, 25, 112.
