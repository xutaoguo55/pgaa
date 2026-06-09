# PGAA: distribution-aware testing for single-cell perturbation screens

**Authors**: Xiaolei Wei<sup>1†</sup>, Haiqing Zheng<sup>2†</sup>, Junwei Huang<sup>1†</sup>, Qi Wei<sup>1</sup>, Yongqiang Wei<sup>1</sup>, Ru Feng<sup>1</sup>, Xutao Guo<sup>1,3\*</sup>

<sup>1</sup> Department of Hematology, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>2</sup> Department of Nosocomial Infection Management, Nanfang Hospital, Southern Medical University, Guangzhou, China  
<sup>3</sup> Clinical Medical Research Center of Hematological Diseases of Guangdong Province, Guangzhou, China  

<sup>†</sup> These authors contributed equally to this work.  
<sup>\*</sup> Correspondence: Xutao Guo (guoxutao@smu.edu.cn)

## Abstract

**Motivation:** Perturb-seq workflows often emphasize mean shifts, but CRISPRa and weak-effect perturbations can create heterogeneous or bimodal responses. **Results:** We present PGAA, a distribution-aware Perturb-seq framework combining a Wasserstein statistic with a persistent-homology statistic for expression-shape changes. Across five observational scRNA-seq datasets, Wasserstein recovers known pathway markers with 2.1-5.8x top-100 enrichment (CLL AUROC 0.87), interpreted as marker recovery rather than causal validation. In Norman 2019 CEBPE CRISPRa, persistence ranks ELANE 57/2012, versus 1761 and 1452 for SCEPTRE and Wasserstein; this is ranking evidence, not FDR-controlled discovery. Adamson 2016 UPR CRISPRi, calibration, and simulation analyses define broader utility and limitations. **Availability and implementation:** Python/R code, source data, tests, and build scripts are supplied; repository and archive identifier to be inserted before final submission. **Contact:** guoxutao@smu.edu.cn. **Supplementary information:** Supplementary data are available with the manuscript.

**Keywords**: Perturb-seq, Wasserstein distance, persistent homology, single-cell RNA-seq, CRISPR screening, calibration


## 1. Introduction

Single-cell perturbation screens [Dixit *et al.*, 2016; Adamson *et al.*, 2016; Norman *et al.*, 2019; Replogle *et al.*, 2022] are now a primary tool for causal regulatory network inference [Regev *et al.*, 2017]. The standard analysis—comparing mean expression of each non-target gene between perturbed and control cells—works well when a perturbation produces a uniform transcriptional shift. KO a transcription factor, its targets drop, and a t-test or Wilcoxon test detects the difference. Tools like DESeq2 [Love *et al.*, 2014], MAST [Finak *et al.*, 2015], SCDE [Kharchenko *et al.*, 2014], and SCEPTRE [Barry *et al.*, 2021] are built for this paradigm, and together with preprocessing workflows in Seurat [Stuart *et al.*, 2019; Hao *et al.*, 2021] and Scanpy [Wolf *et al.*, 2018], they form the standard Perturb-seq analysis toolkit.

But not all perturbations are well-behaved. CRISPRa [Gilbert *et al.*, 2014] can produce heterogeneous responses: the gRNA activates the target in only a fraction of cells. The mean expression may change only modestly, yet the distribution changes substantially--for example, a secondary peak may emerge in the expression histogram as some cells respond and others do not. Mean-focused tools can miss such signals. The same problem can arise with weak-effect perturbations, variance changes without mean changes, and perturbations that alter gene-gene correlation structures or count-model dispersion rather than shifting the mean.

Few existing Perturb-seq methods directly address non-mean-shift response modes such as distributional bimodality, although heterogeneity-aware approaches are emerging [Heumos *et al.*, 2026]. We present **PGAA**, a framework built around two complementary statistics sharing a common permutation-calibration infrastructure. The Wasserstein distance captures distributional shifts; the persistence test detects bimodality through topological changes in expression histograms. Additional modules for conditional MI and Fisher NB testing are provided as software extensions. All statistics are accompanied by a calibration diagnostic (Storey π̂₀) that lets users assess reliability on their own data before interpreting results.

We validate the Wasserstein statistic on five observational scRNA-seq datasets, benchmark both statistics on two Perturb-seq datasets, demonstrate persistent homology on Norman 2019 CEBPE CRISPRa, provide a six-perturbation calibration study, and map each statistic's regime of validity through a 63-condition simulation.


## 2. Methods

### 2.1 Setup and residualization

We work with log-normalized expression matrices ($\log(\text{CPM} + 1)$, CPM = counts per million, target sum 10,000). After standard QC and highly-variable gene selection (2,000 genes), each cell $i$ has a perturbation label $D_i \in \{0,1\}$ and covariates $Z_i$. Before applying any statistic, we residualize out cell-type and library-size effects via OLS:

$$\tilde{X} = X - Z (Z^\top Z)^{-1} Z^\top X$$

where $Z$ contains an intercept, K-means cluster indicators ($k = 5$) [MacQueen, 1967], and standardized library size. This step is applied to both tests; the MI and Fisher NB tests operate on the original normalized matrix. The value of $k$ is fixed throughout the benchmark as a coarse cell-state proxy rather than estimated from the data.

For a target gene $g^*$, we test each non-target gene $g$ for whether $P(Y_g \mid D = 1)$ differs from $P(Y_g \mid D = 0)$ in mean, shape, or dependency structure.

### 2.2 Wasserstein distance

The Wasserstein distance (Earth Mover's Distance) between two empirical CDFs:

$$S_1(g) = \frac{1}{99} \sum_{q=0.01}^{0.99} \bigl| Q_g^{(1)}(q) - Q_g^{(0)}(q) \bigr|,$$

where $Q_g^{(d)}(q)$ is the $q$-quantile of $\tilde{X}_{i,g}$ for cells with $D_i = d$.

Wasserstein distances provide a non-parametric way to compare full one-dimensional distributions and can respond to changes in location, spread, or shape. This makes the statistic useful when the biological signal is not limited to a mean shift. The 1D case has an efficient quantile-based computation [Villani, 2009; Ramdas *et al.*, 2017].

We compute $p$-values via within-cluster permutation [Good, 2005; Efron & Tibshirani, 1993]: for each of 2,000 permutations, shuffle $D$ within each K-means cluster, recompute the Wasserstein test, and count the fraction of null statistics at least as extreme as the observed value. The cluster-stratified shuffle preserves cell-type composition while randomizing the perturbation assignment.

A note on numerical consistency. The observed and permuted $W_1$ statistics are computed with the same 99-quantile approximation. This is essential because permutation $p$-values compare the observed statistic directly with its empirical null distribution. We verified calibration empirically: under the null, the observed false positive rate is 0.057 (30 simulations, 95% CI [0.021, 0.079]).

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

We use seven publicly available datasets (five observational scRNA-seq datasets for marker-recovery validation and two real Perturb-seq datasets for method benchmarking):

- **CLL** (GSE111014; 36,601 cells, 4 patient + 2 control samples; subsampled to 20,000 cells): TCL1A virtual perturbation with BCR signaling markers as positive set and 15 housekeeping genes as negative controls.
- **Sepsis** (GSE167363; 64,244 cells, subsampled to 20,000): TCR pathway markers.
- **RA** (GSE159117; 10,499 cells): rheumatoid arthritis synovial tissue, cytokine pathway markers.
- **PBMC** (10x Genomics 3k demo, 2,700 cells [Zheng *et al.*, 2017]): multi-lineage markers for scale validation (2.7k–64k).
- **IBD** (GSE116222; 11,175 cells): gut immune markers.
- **Norman 2019** (GSE133344; 111,668 K562 cells): the primary real Perturb-seq dataset. Six single-gene CRISPRa perturbations: CEBPE (566 cells), KLF1 (1197), SLC4A1 (1000), BAK1 (687), DUSP9 (731), CBL (663). Known CEBPE downstream targets: ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, RNASE2. We use 3× matched NegCtrl cells (1,698 of 11,855 available) as controls.
- **Adamson 2016** (GSE90546; K562 cells, CRISPRi UPR screen): 5,680 cells after QC. Five sgRNAs targeting UPR genes (SPI1, ZNF326, BHLHE40, CREB1, DDIT3; 468-686 cells each) selected a priori based on UPR annotation, with 1,759 non-targeting controls. Gold standard: a curated UPR marker set covering IRE1, PERK, ATF6, ERAD, and chaperone branches (Supplementary Table S3), with 13 markers present in the HVG benchmark universe.

Preprocessing for all datasets: QC filter (200–6000 genes, <20% MT, >500 UMI for CLL; pre-filtered by original authors for Norman 2019), normalize to 10K CPM, log1p, retain 2,000 HVGs with forced inclusion of target genes.

### 2.8 Implementation

PGAA is implemented in Python and R. The Python package (`pgaa/`) depends on NumPy, SciPy, Pandas, Scanpy [Wolf *et al.*, 2018], and scikit-learn; the R package (`pgaa_r/`) uses only base R plus the MASS library. Both implementations of both tests produce identical numerical output (error < $10^{-6}$). On a single CPU core, the Wasserstein test processes 2,000 genes with 2,000 permutations in about five minutes; persistent homology with 500 permutations takes under two minutes. Preprocessing follows standard scRNA-seq workflows [Luecken & Theis, 2019; Lun *et al.*, 2016].


## 3. Results

### 3.1 Wasserstein recovers known biology

As a general-purpose distributional statistic, Wasserstein enriches known pathway markers 2.1-5.8x over background across five observational datasets (CLL 4.0x, Sepsis 2.1x, RA 2.5x, PBMC 2.9x, IBD 5.8x). On CLL, the BCR signaling gene set (CD79A, CD79B, MS4A1, CD24, BANK1, LYN, BLNK, SYK, BTK, PLCG2, PIK3CD, CD19, CD22) appears prominently in the top 100, with AUROC 0.87 for known-marker recovery (Supplementary Table S2).

These five datasets are observational—the "perturbation" is defined by binning cells on endogenous TCL1A expression, not by an experimental intervention—so the results demonstrate marker recovery rather than causal discovery. The enrichment is consistent with the Wasserstein test being a reasonable default statistic when the perturbation type is unknown.

**[Figure 1]**

### 3.2 Persistent homology improves ELANE ranking

Norman *et al.* (2019) used CRISPRa to activate CEBPE in K562 cells [Lozzio & Lozzio, 1975]. CEBPE is a myeloid transcription factor whose known targets include nine neutrophil granule proteins: ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, and RNASE2 [Friedman, 2007; Park *et al.*, 1999].

SCEPTRE and the Wasserstein statistic rank this target poorly. SCEPTRE places ELANE at rank 1761/2012 ($p = 0.92$). The Wasserstein statistic places it at rank 1452/2012 ($p = 0.223$). Neither method ranks ELANE among its strongest CEBPE candidates in this analysis.

The persistence statistic ($n_{\text{bins}} = 20$, 500 permutations) ranks ELANE at position 57 ($p = 0.04$), a 25-fold rank improvement over the Wasserstein statistic. With 500 permutations, this p-value is interpreted as ranking evidence rather than genome-wide significance, and no FDR-controlled CEBPE gene discovery is claimed. The $p$-value distribution is acceptable in this pre-specified setting (π̂₀ = 1.32 with 200 permutations in the sensitivity run; approximately 1.0 with 500 permutations). The top genes by raw S2 value (SLC45A1, DLX2, ATP5E) are not known CEBPE targets; ELANE's stronger rank by permutation $p$-value reflects its favorable null distribution relative to other genes. As a specificity check, we applied the persistence statistic to all six perturbations using the CEBPE target gene set as the gold standard (Supplementary Table S4). ELANE was ranked strongly for CEBPE and also for the severely over-sensitive BAK1 perturbation, where π̂₀ = 0.10. For the well-calibrated KLF1 perturbation, ELANE was not supported ($p = 0.70$, π̂₀ = 1.15). For CBL, SLC4A1, and DUSP9, ELANE p-values were 0.58, 0.16, and 0.90 respectively. This analysis supports perturbation specificity only when the calibration diagnostic is acceptable; over-sensitive perturbations should not be interpreted as formal discoveries.

CRISPRa produces heterogeneous target activation—the gRNA does not guarantee protein-level CEBPE expression in every cell, and the resulting bimodal expression pattern is exactly the regime the persistence test is designed for. K562 is an erythroleukemia line, not a neutrophil progenitor; while it retains granulocytic differentiation capacity upon CEBPE activation, not all nine targets may be transcriptionally responsive in this system.

**[Figure 2]**

### 3.3 Calibration varies by perturbation

Running persistent homology on six different perturbations from the Norman 2019 screen reveals that calibration is far from consistent. The Storey π̂₀ ranges from 1.15 (KLF1, well-calibrated) to 0.10 (BAK1, severely over-sensitive). The table below summarizes the results.

| Perturbation | π̂₀ | n_sig | Calibration |
|---|---|---|---|
| KLF1 (erythroid TF) | 1.15 | 54 | well-calibrated |
| CBL | 0.72 | 173 | acceptable |
| SLC4A1 | 0.67 | 222 | mild over-sensitivity |
| DUSP9 | 0.68 | 460 | over-sensitive |
| CEBPE (CRISPRa) | 0.25 | 1063 | severely over-sensitive |
| BAK1 | 0.10 | 1789 | over-sensitive |

Table: **Table 1.** Persistence test calibration across six Norman 2019 perturbations.

KLF1 drives a clean erythroid program. CEBPE CRISPRa and BAK1 do not. The calibration spread reflects this biology, and the practical takeaway is simple: include a negative control perturbation and check π̂₀. Importantly, the CEBPE π̂₀ of 0.25 reported here comes from a calibration run with n_bins = 50 and n_perms = 200; the main analysis in Section 3.2 uses n_bins = 20 and n_perms = 500, which yields π̂₀ ≈ 1.0–1.3. The discrepancy illustrates how strongly calibration depends on both bin count and permutation depth, reinforcing the need for the pilot sweep recommended in Section 3.5.

**[Figure 3]**

### 3.4 Wasserstein and persistence see different biology on CLL

The CLL TCL1A case shows how both tests complement each other. Among the top 100 genes ranked by each statistic, only six overlap. The Wasserstein test enriches B-cell receptor markers (CD79A rank 9, CD79B rank 48, MS4A1 rank 53). The persistence test picks up T-cell receptor genes (TRBV7-6, TRAV12-1, CD3E, CD3D) that Wasserstein misses entirely. The combined z-test recovers 3 BCR and 11 TCR genes at $p < 0.05$, versus 4+3 for Wasserstein alone and 0+7 for the persistence test alone.

The CLL analysis uses rank-based inverse-normal scores (Supplementary Methods S3) rather than full permutation calibration--a lighter-weight approach appropriate when only relative gene ordering matters rather than formal significance testing.

**[Figure 4]**

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

Table: **Table 2.** Persistence test hyperparameter sensitivity on Norman 2019 CEBPE.

The n_bins = 30 row is striking: at this resolution, the histogram bins merge the two modes of the bimodal distribution, and ELANE's signal collapses (rank 1807). This is a sharp failure mode, not a gradual degradation. We recommend the default $n_{\text{bins}} = 20$ as a starting point, with a pilot sweep ($n_{\text{bins}} \in \{10, 20, 30, 50\}$) to verify that the chosen value does not fall into the n_bins = 30 failure mode where peak merging destroys the persistence signal. The sweep should be performed on a control or null perturbation, not the perturbation of interest, to avoid overfitting. At $n_{\text{bins}} = 20$, the $p$-values are well-calibrated (π̂₀ = 1.32 with $n_{\text{perms}} = 200$; 1.00 with $n_{\text{perms}} = 500$) and ELANE achieves its best rank.

**[Supplementary Table S1]**

### 3.6 Independent validation on Adamson 2016 UPR CRISPRi

To test PGAA on a second, independent Perturb-seq dataset with a complementary perturbation modality, we applied both tests to the Adamson et al. (2016) UPR CRISPRi screen (GSE90546). After QC, 5,680 K562 cells were retained across five well-characterized sgRNA perturbations targeting UPR genes (SPI1, ZNF326, BHLHE40, CREB1, DDIT3; 468-686 cells each) and a non-targeting control (1,759 cells). The gold standard was a curated UPR marker set covering IRE1, PERK, ATF6, ERAD, and chaperone branches, of which 13 markers were present in the 2,000-gene HVG subset.

Across the five perturbations, the Wasserstein test achieved a mean AUROC of 0.786 (range 0.767-0.806, mean AUPRC 0.0191) for recovering known UPR genes. By comparison, Wilcoxon, t-test, and MAST achieved mean AUROCs of 0.529, 0.523, and 0.406 respectively in the same benchmark. The persistence test achieved a mean AUROC of 0.748 (range 0.658-0.833, mean AUPRC 0.0253). Descriptive 95% t intervals across the five pre-specified perturbations are reported in Supplementary Table S12; these intervals quantify between-perturbation variability and are not a substitute for a larger independent benchmark panel. For the BHLHE40 knockdown, the persistence test was the strongest method overall (AUROC 0.833, AUPRC 0.0594 vs. Wasserstein AUROC 0.788), consistent with a bimodal transcriptional response. Because only 13 of the 2,000 HVGs were UPR positives, the random AUPRC baseline was 0.0065; observed AUPRC values correspond to 2.9x and 3.9x enrichment over random expectation for the Wasserstein and persistence tests, respectively. These perturbations were selected a priori based on UPR annotation in the original study and a minimum cell-count threshold ($\ge 400$ cells), not based on PGAA performance (Supplementary Table S5).

**[Figure 5]**

### 3.7 Simulation ablation maps each statistic to its regime

To systematically assess when each statistic performs best, we simulated three perturbation types at seven effect sizes ($\theta \in \{0.1, \ldots, 1.0\}$) with three replicates each (63 conditions total).

Type A (pure mean shift) is the Wasserstein test's home territory (TPR = 0.97 at $\theta = 1.0$). Type C (mean + bimodality) favors the Wasserstein test as well. The most informative condition is Type B, where only 40% of perturbed cells respond. Here the Wasserstein test and the combined z-test are competitive (TPR = 0.52–0.85 depending on $\theta$), while persistent homology reaches only TPR = 0.12. This simulation uses *partial* bimodality—the two modes overlap in the 40%-response regime. On real CRISPRa data where the split is more complete (nearer to 50% "on" vs. 50% "off"), persistent homology's performance is stronger, as demonstrated by the Norman 2019 results.

From the simulation and real-data results, a practical decision rule emerges:

| Scenario | Recommended statistic |
|---|---|
| Standard KO/OE | Wasserstein |
| CRISPRa / heterogeneous response | Persistence test (check π̂₀) |
| Mixed signal | Combined z |
| Unknown | Run the Wasserstein test first. If no signal, try the persistence test with pilot sweep. |

Table: **Table 3.** Practical decision rule for statistic selection.

**[Figure 6]**


## 4. Discussion

We set out to test whether distribution-aware statistics could detect Perturb-seq responses that mean-based methods miss. The answer, based on two independent Perturb-seq datasets with complementary perturbation modalities, is cautiously positive. On Norman 2019 CEBPE CRISPRa, the persistence statistic ranked the known neutrophil granule target ELANE at position 57, while SCEPTRE and the Wasserstein statistic placed it at 1761 and 1452. On Adamson 2016 UPR CRISPRi, the Wasserstein statistic achieved a mean AUROC of 0.786 across five perturbations, outperforming Wilcoxon (0.529), t-test (0.523), and MAST (0.406) in this benchmark. In the BHLHE40 knockdown case, the persistence statistic was the strongest method overall (AUROC 0.833), consistent with a heterogeneous, potentially bimodal transcriptional response.

These results suggest a practical two-pronged strategy for Perturb-seq analysis. The Wasserstein statistic is a useful default distributional score when the perturbation type is unknown. The persistence statistic fills a narrower niche--CRISPRa screens, weak-effect perturbations, and any setting where the response is expected to be heterogeneous--but requires the user to verify calibration via the Storey pi0 diagnostic and to run a pilot n_bins sweep before committing to results. The persistence statistic's strong dependence on histogram bin count (values at n_bins = 20 and n_bins = 50 correlate at only r = 0.12) means it should be treated as a ranking tool rather than a formal discovery procedure unless substantially more permutations are used.

Several limitations should be noted. First, the persistence test is calibrated differently for different perturbations; the six-perturbation calibration study showed pi0 ranging from 0.10 (BAK1, over-sensitive) to 1.15 (KLF1, well-calibrated), so a negative control perturbation is essential. Second, the MI and Fisher NB modules are provided as software extensions but have not been benchmarked. Third, our simulation uses Gaussian noise for computational efficiency; we verified that the persistence test does not spuriously detect bimodality from zero-inflation (mean S2 = 0.031 under NB H0 with 30% dropout; Supplementary Methods S4), consistent with evidence that droplet-based scRNA-seq data are well-modeled by the negative binomial without explicit zero-inflation [Svensson, 2020]. Fourth, all benchmarks use K-means (k = 5) as a cell-type proxy; finer annotation may improve specificity. Fifth, broader genome-scale validation against SCEPTRE-family and perturbation-specific methods remains necessary. No new biological discoveries are claimed.

PGAA fits into the growing ecosystem of Perturb-seq analysis tools. The pertpy framework [Heumos *et al.*, 2026] provides an end-to-end pipeline into which PGAA's statistics could be integrated as modular test components. Mixscape [Papalexi *et al.*, 2021] handles the complementary problem of identifying cells with failed perturbations, while scMAGeCK [Yang *et al.*, 2020] operates at the CRISPR screen level. SCEPTRE [Barry *et al.*, 2021] and its robust extension [Barry *et al.*, 2024] set a high standard for calibrated permutation testing of mean shifts; PGAA extends this paradigm to distributional and topological shifts.

The most immediate priority is genome-scale validation on Replogle 2020/2022, where thousands of perturbations would allow a systematic assessment of calibration behavior and the identification of perturbation-level features that predict whether Wasserstein or persistence will prove more informative.




## Data and Code Availability

- Norman 2019: GSE133344. Adamson 2016: GSE90546. CLL: GSE111014. Sepsis: GSE167363. RA: GSE159117. IBD: GSE116222. PBMC: 10x Genomics 3k demo [Zheng *et al.*, 2017].
- Source code, documentation, environment files, tests, benchmark source-data files, and PDF build scripts are prepared under the MIT license. A supplementary software archive is supplied with the submission. The planned public repository is https://github.com/xutaoguo55/pgaa; this URL must be publicly reachable, and a permanent Zenodo, Figshare, Software Heritage, or Code Ocean identifier must be added, before final submission to satisfy the journal's software-archiving policy.
- The Norman 2019 S1 full permutation benchmark is regenerated by `scripts/compare_combinations.py` from the local processed Norman h5ad input used in this study. The Adamson 2016 benchmark table used in the PDF is rebuilt from the accompanying curated source-data CSV by `scripts/rebuild_adamson_full_results.py`; this is source-data reproducibility rather than a full raw GEO-to-table workflow. Manuscript-level consistency checks are run with `scripts/verify_manuscript_consistency.py`.
- All random processes use `random_state=42` or equivalent fixed seeds.

## AI Tool Use

AI-assisted tools were used for language editing, code review, and consistency checking. The authors reviewed and approved all text, code, analyses, and conclusions.

## Author Contributions

X.W., H.Z., and J.H. contributed equally. X.G. conceived the study and designed the framework. X.W., H.Z., and J.H. implemented the software and performed the analyses. Q.W., Y.W., and R.F. contributed to data collection and biological interpretation. All authors wrote and approved the manuscript.

## Funding

No external funding was received for this work.

## Conflict of Interest

None declared.



## Supplementary Information

- **Figure S1**: Persistence test calibration QQ plot ($n_{\text{bins}} = 20$, n_perms = 500) and p-value histogram.
- **Figure S2**: Adamson 2016 BHLHE40 perturbation details: gene-level S1 vs S2 scores with UPR markers highlighted, and expression distributions.
- **Figure S3**: PGAA distribution-aware Perturb-seq testing workflow.
- **Table S1**: Persistence test hyperparameter sensitivity (Section 3.5).
- **Table S2**: Multi-dataset marker-recovery summary.
- **Table S3**: Adamson 2016 UPR gold-standard genes.
- **Table S4**: SCEPTRE vs PGAA comparison and six-perturbation specificity checks.
- **Table S5**: Adamson 2016 per-perturbation benchmark.
- **Table S6**: Dataset roles and evidence level.
- **Table S7**: Main parameter settings.
- **Table S8**: Software availability and reproducibility status.
- **Table S9**: Runtime and memory summary.
- **Table S10**: Result reproduction map.
- **Table S11**: Comparator and benchmark status.
- **Table S12**: Adamson 2016 method-level descriptive confidence intervals.
- **Supplementary Methods S1-S4**: Additional modules, CLL rank-score analysis, simulation parameters, and zero-inflation control.


## References

1. Dixit A, Parnas O, Li B, Chen J, Fulco CP, Jerby-Arnon L, et al. (2016) Perturb-Seq: Dissecting molecular circuits with scalable single-cell RNA profiling of pooled genetic screens. *Cell*, 167(7), 1853–1866.e17.
2. Adamson B, Norman TM, Jost M, Cho MY, Nunez JK, Chen Y, et al. (2016) A multiplexed single-cell CRISPR screening platform enables systematic dissection of the unfolded protein response. *Cell*, 167(7), 1867–1882.e21.
3. Norman TM, Horlbeck MA, Replogle JM, Ge AY, Xu A, Jost M, et al. (2019) Exploring genetic interaction manifolds constructed from rich single-cell phenotypes. *Science*, 365(6455), 786–793.
4. Replogle JM, Saunders RA, Pogson AN, Hussmann JA, Lenail A, Guna A, et al. (2022) Mapping information-rich genotype-phenotype landscapes with genome-scale Perturb-seq. *Cell*, 185(14), 2559–2575.e28.
5. Barry T, Wang X, Morris JA, Roeder K, Katsevich E. (2021) SCEPTRE improves calibration and sensitivity in single-cell CRISPR screen analysis. *Genome Biology*, 22, 344.
6. Ramdas A, Garcia Trillos N, Cuturi M. (2017) On Wasserstein two-sample testing and related families of nonparametric tests. *Entropy*, 19(2), 47.
7. Edelsbrunner H, Harer J. (2010) *Computational Topology: An Introduction*. Providence, RI: American Mathematical Society.
8. Bubenik P. (2015) Statistical topological data analysis using persistence landscapes. *Journal of Machine Learning Research*, 16(3), 77–102.
9. Storey JD. (2002) A direct approach to false discovery rates. *Journal of the Royal Statistical Society: Series B*, 64(3), 479–498.
10. Kraskov A, Stogbauer H, Grassberger P. (2004) Estimating mutual information. *Physical Review E*, 69(6), 066138.
11. Villani C. (2009) *Optimal Transport: Old and New*. Grundlehren der mathematischen Wissenschaften, Vol. 338. Berlin: Springer.
12. Zomorodian A, Carlsson G. (2005) Computing persistent homology. *Discrete & Computational Geometry*, 33, 249–274.
13. Carlsson G. (2009) Topology and data. *Bulletin of the American Mathematical Society*, 46(2), 255–308.
14. Luecken MD, Theis FJ. (2019) Current best practices in single-cell RNA-seq analysis: a tutorial. *Molecular Systems Biology*, 15(6), e8746.
15. Svensson V. (2020) Droplet scRNA-seq is not zero-inflated. *Nature Biotechnology*, 38(2), 147–150.
16. Good PI. (2005) *Permutation, Parametric, and Bootstrap Tests of Hypotheses* (3rd ed.). New York: Springer.
17. Wolf FA, Angerer P, Theis FJ. (2018) SCANPY: large-scale single-cell gene expression data analysis. *Genome Biology*, 19, 15.
18. Papalexi E, Mimitou EP, Butler AW, Foster S, Bracken B, Mauck WM, et al. (2021) Characterizing the molecular regulation of inhibitory immune checkpoints with multimodal single-cell screens. *Nature Genetics*, 53(3), 322–331.
19. Yang L, Zhu Y, Yu H, Cheng X, Chen S, Chu Y, et al. (2020) scMAGeCK links genotypes with multiple phenotypes in single-cell CRISPR screens. *Genome Biology*, 21, 19.
20. Park DJ, Chumakov AM, Vuong PT, Chih DY, Gombart AF, Miller WH Jr, Koeffler HP. (1999) CCAAT/enhancer binding protein epsilon is a potential retinoid target gene in acute promyelocytic leukemia treatment. *Journal of Clinical Investigation*, 103(10), 1399–1408.
21. Friedman AD. (2007) Transcriptional control of granulocyte and monocyte development. *Oncogene*, 26(47), 6816–6828.
22. Benjamini Y, Hochberg Y. (1995) Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289–300.
23. Gilbert LA, Horlbeck MA, Adamson B, Villalta JE, Chen Y, Whitehead EH, et al. (2014) Genome-scale CRISPR-mediated control of gene repression and activation. *Cell*, 159(3), 647–661.
24. Love MI, Huber W, Anders S. (2014) Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology*, 15, 550.
25. Lozzio CB, Lozzio BB. (1975) Human chronic myelogenous leukemia cell-line with positive Philadelphia chromosome. *Blood*, 45(3), 321–334.
26. MacQueen J. (1967) Some methods for classification and analysis of multivariate observations. In L. M. Le Cam & J. Neyman, eds., *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, Volume 1: Statistics* (pp. 281–297). Berkeley, CA: University of California Press.
27. Zheng GXY, Terry JM, Belgrader P, Ryvkin P, Bent ZW, Wilson R, et al. (2017) Massively parallel digital transcriptional profiling of single cells. *Nature Communications*, 8, 14049.
28. Stuart T, Butler A, Hoffman P, Hafemeister C, Papalexi E, Mauck WM III, et al. (2019) Comprehensive integration of single-cell data. *Cell*, 177(7), 1888–1902.e21.
29. Hao Y, Hao S, Andersen-Nissen E, Mauck WM III, Zheng S, Butler A, et al. (2021) Integrated analysis of multimodal single-cell data. *Cell*, 184(13), 3573–3587.e29.
30. Regev A, Teichmann SA, Lander ES, Amit I, Benoist C, Birney E, et al. (2017) The Human Cell Atlas. *eLife*, 6, e27041.
31. Efron B, Tibshirani RJ. (1993) *An Introduction to the Bootstrap*. New York: Chapman & Hall.
32. Finak G, McDavid A, Yajima M, Deng J, Gersuk V, Shalek AK, et al. (2015) MAST: a flexible statistical framework for assessing transcriptional changes and characterizing heterogeneity in single-cell RNA sequencing data. *Genome Biology*, 16, 278.
33. Kharchenko PV, Silberstein L, Scadden DT. (2014) Bayesian approach to single-cell differential expression analysis. *Nature Methods*, 11(7), 740–742.
34. Lun ATL, McCarthy DJ, Marioni JC. (2016) A step-by-step workflow for low-level analysis of single-cell RNA-seq data with Bioconductor [version 2; peer review: 3 approved, 2 approved with reservations]. *F1000Research*, 5, 2122.
35. Heumos L, Ji Y, May L, Green TD, Peidli S, Zhang X, et al. (2026) Pertpy: an end-to-end framework for perturbation analysis. *Nature Methods*, 23, 350–359.
36. Barry T, Mason K, Roeder K, Katsevich E. (2024) Robust differential expression testing for single-cell CRISPR screens at low multiplicity of infection. *Genome Biology*, 25, 124.
