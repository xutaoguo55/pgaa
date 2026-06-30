---
header-includes:
  - \usepackage{graphicx}
  - \usepackage{pdflscape}
  - \usepackage{tabularx}
  - \usepackage{longtable}
  - \usepackage{array}
---

# Supplementary Information

**Manuscript title:** PGAA: distribution-aware ranking of heterogeneous \mbox{single-cell} perturbation responses

**Authors:** Xiaolei Wei, Haiqing Zheng, Junwei Huang, Qi Wei, Yongqiang Wei, Ru Feng, Xutao Guo

## Supplementary Figures

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_s2_bhlhe40.png}

\textbf{Supplementary Figure 1.} Adamson 2016 BHLHE40 perturbation details. a, Gene-level PGAA-W Wasserstein versus PGAA-H histogram-shape statistic scores with UPR markers highlighted. b, Control and BHLHE40-perturbed expression distributions for representative UPR genes.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_elane_histogram.png}

\textbf{Supplementary Figure 2.} ELANE heterogeneous expression pattern in Norman 2019 CEBPE CRISPRa. a, ELANE expression distribution across control and CEBPE-perturbed cells using 20 histogram bins. b, Histogram profiles used for the PGAA-H histogram-shape statistic comparison.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.85\textwidth]{figures_png/figure_s2_calibration_qq.png}

\textbf{Supplementary Figure 3.} PGAA-H calibration for the pre-specified Norman 2019 CEBPE n-bins = 20 analysis. a, QQ plot of observed versus expected -log10(p) values. b, Histogram of permutation p-values.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_5.png}

\textbf{Supplementary Figure 4.} Simulation ablation across mean-shift, heterogeneous-response, and mixed-response regimes. a, Mean-shift regime. b, Bimodality-shift regime. c, Mixed mean-plus-bimodality regime. These simulations are operating-regime diagnostics rather than a full generative model of scRNA-seq counts.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_4.png}

\textbf{Supplementary Figure 5.} CLL 20k exploratory complementarity analysis comparing Wasserstein and PGAA-H rankings. a, BCR and TCR marker ranks by method. b, Top genes by the combined PGAA-W+PGAA-H mean-z ranking. c, BCR and TCR marker recovery under alternative ranking summaries. This observational pseudo-perturbation analysis is used for marker-program ranking only.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_pgaa_workflow.png}

\textbf{Supplementary Figure 6.} PGAA distribution-aware Perturb-seq ranking workflow. The schematic summarizes the input data, preprocessing, PGAA-W Wasserstein statistic, PGAA-H histogram-shape statistic, permutation calibration, and outputs.
\end{center}

\clearpage
\begin{center}
\includegraphics[width=1.0\textwidth]{figures_png/figure_1.png}

\textbf{Supplementary Figure 7.} External marker-recovery stress checks across five observational single-cell datasets. a, Recovery of known marker sets compared with housekeeping negative controls in the top-100 PGAA-W ranking. b, Positive-to-negative enrichment ratios, with 1x as the random expectation and 2x as a practical enrichment threshold. c, CLL comparator analysis showing that PGAA-W produced coherent BCR-axis rankings but was not uniformly superior to all conventional ranking baselines. These analyses assess marker recovery rather than causal perturbation effects. All panels use source data from \texttt{figure\_source\_data/fig2\_multidataset.csv}.
\end{center}
\clearpage

## Supplementary Table 1. Adamson 2016 UPR marker set

The Adamson benchmark uses a curated UPR marker set covering IRE1, PERK, ATF6, ERAD, and chaperone branches. Thirteen markers were retained in the 2,000-HVG benchmark universe used for AUROC/AUPRC calculation.

| Branch | Genes considered |
|---|---|
| IRE1 | ERN1, XBP1, HSPA5, DNAJB9, DNAJC3, SEC61A1 |
| PERK | EIF2AK3, ATF4, DDIT3, PPP1R15A, TRIB3, CHAC1 |
| ATF6 | ATF6, MBTPS1, MBTPS2, CALR, PDIA4, HYOU1 |
| ERAD | EDEM1, SYVN1, SEL1L, HERPUD1, DERL1 |
| Chaperones | HSPA5, HSP90B1, CALR, PDIA3, PDIA6, ERP29 |

\clearpage

\begin{landscape}
\section*{Supplementary Table 2. Adamson 2016 UPR CRISPRi per-perturbation benchmark}
Random AUPRC baseline = 0.0065.

\begin{center}
\begin{tabular}{lrrrrrrrr}
\hline
Perturbation & n & PGAA-W AUROC & PGAA-W AUPRC & PGAA-H AUROC & PGAA-H AUPRC & Wilcoxon AUROC & t-test AUROC & MAST AUROC \\
\hline
SPI1\_pDS255 & 686 & 0.806 & 0.0223 & 0.658 & 0.0110 & 0.687 & 0.650 & 0.439 \\
ZNF326\_pDS262 & 555 & 0.767 & 0.0160 & 0.700 & 0.0144 & 0.526 & 0.531 & 0.391 \\
BHLHE40\_pDS258 & 542 & 0.788 & 0.0178 & 0.833 & 0.0594 & 0.466 & 0.475 & 0.365 \\
CREB1\_pDS269 & 499 & 0.772 & 0.0208 & 0.781 & 0.0202 & 0.498 & 0.482 & 0.461 \\
DDIT3\_pDS263 & 468 & 0.799 & 0.0184 & 0.769 & 0.0213 & 0.468 & 0.476 & 0.375 \\
\hline
\end{tabular}
\end{center}

\normalsize
\end{landscape}

\begin{landscape}
\section*{Supplementary Table 3. Norman 2019 multi-perturbation CRISPRa target-panel benchmark}
The main text summarizes the Norman multi-perturbation extension. PGAA-W is supported as the default ranking statistic. The benchmark uses processed Norman h5ad input, 2,000 HVGs plus forced inclusion of target-panel genes, and non-targeting controls sampled at up to a 3:1 control-to-perturbed ratio. For CEBPA, comparator AUROCs below 0.5 are reported descriptively and do not establish a signed biological inversion; the limited conclusion is that PGAA-W ranked this curated target panel more favorably than the tested comparators under the same preprocessing and panel definition.

\begin{center}
\begin{tabular}{llrrrrr}
\hline
Target & Method & AUROC & AUPRC & Random AUPRC baseline & Top-100 positive hits & Positive genes / ranked genes \\
\hline
KLF1 & PGAA-W Wasserstein & 0.684 & 0.0252 & 0.0079 & 1 & 16/2016 \\
KLF1 & KS statistic & 0.537 & 0.0153 & 0.0079 & 1 & 16/2016 \\
KLF1 & Welch t & 0.424 & 0.0073 & 0.0079 & 0 & 16/2016 \\
KLF1 & Wilcoxon & 0.496 & 0.0173 & 0.0079 & 1 & 16/2016 \\
CEBPE & PGAA-W Wasserstein & 0.644 & 0.0154 & 0.0045 & 2 & 9/2009 \\
CEBPE & KS statistic & 0.497 & 0.0054 & 0.0045 & 0 & 9/2009 \\
CEBPE & Welch t & 0.570 & 0.0054 & 0.0045 & 0 & 9/2009 \\
CEBPE & Wilcoxon & 0.484 & 0.0054 & 0.0045 & 0 & 9/2009 \\
CEBPA & PGAA-W Wasserstein & 0.665 & 0.1244 & 0.0045 & 2 & 9/2009 \\
CEBPA & KS statistic & 0.249 & 0.0032 & 0.0045 & 0 & 9/2009 \\
CEBPA & Welch t & 0.381 & 0.0038 & 0.0045 & 0 & 9/2009 \\
CEBPA & Wilcoxon & 0.262 & 0.0034 & 0.0045 & 0 & 9/2009 \\
\hline
\end{tabular}
\end{center}

\normalsize
\end{landscape}

\begin{landscape}
\section*{Supplementary Table 4. Norman 2019 CEBPE target-level details}
The main Norman CEBPE result is summarized in Table 3. This table gives target-level ranks and p-values for the curated nine-gene CEBPE target set in the pre-specified n-bins = 20 PGAA-H analysis. The p-values are interpreted as ranking evidence because 500 permutations cannot support genome-wide FDR-controlled discovery.

\begin{center}
\begin{tabular}{lrrrrrl}
\hline
Target & PGAA-W rank & PGAA-W p & PGAA-H rank & PGAA-H p & PGAA-H score & Note \\
\hline
ELANE & 1452 & 0.223 & 57 & 0.040 & 0.004125 & Main PGAA-H signal \\
AZU1 & 500 & 0.001 & 856 & 0.597 & 0.001582 & PGAA-W only \\
MPO & 1752 & 0.529 & 1727 & 1.000 & 0.000000 & Not recovered \\
LYZ & 1372 & 0.172 & 928 & 0.643 & 0.001415 & Not recovered \\
CTSG & 1911 & 0.759 & 1727 & 1.000 & 0.000000 & Not recovered \\
GFI1 & 1178 & 0.078 & 1506 & 0.950 & 0.000707 & Not recovered \\
PRTN3 & 1364 & 0.163 & 97 & 0.068 & 0.004245 & Secondary PGAA-H signal \\
DEFA1 & 1109 & 0.058 & 1185 & 0.872 & 0.000707 & Not recovered \\
RNASE2 & 1316 & 0.141 & 1105 & 0.776 & 0.001415 & Not recovered \\
\hline
\end{tabular}
\end{center}

\normalsize
\end{landscape}

## Supplementary Table 5. PGAA-H histogram-bin sensitivity

Norman 2019 CEBPE sensitivity sweep. These runs use 200 permutations for speed and are used to evaluate bin-count sensitivity, not to claim genome-wide significance.

| n-bins | ELANE rank | ELANE p | n-sig at p<0.05 | Storey upper-tail ratio | Known hits |
|---:|---:|---:|---:|---:|---:|
| 20 | 32 | 0.0249 | 66 | 1.321 | 1/9 |
| 30 | 1807 | 0.6716 | 387 | 0.407 | 0/9 |
| 50 | 489 | 0.0050 | 1063 | 0.246 | 3/9 |
| 75 | 460 | 0.0050 | 1087 | 0.227 | 4/9 |
| 100 | 468 | 0.0050 | 1087 | 0.226 | 5/9 |
| 150 | 446 | 0.0050 | 1073 | 0.225 | 4/9 |

## Supplementary Table 6. Marker-recovery datasets

The five observational datasets are used for marker recovery rather than causal or clinical inference. The top-100 enrichment compares known marker recovery against background ranking. The CLL AUROC is computed against the 13-gene BCR marker set; AUROC values for other datasets are not reported here because the submitted archive does not bundle the full raw data needed for independent recomputation and the primary metric is enrichment ratio.

| Dataset | Statistic | Top-100 enrichment | AUROC (where available) | Key known targets hit |
|---|---|---:|---:|---|
| CLL 20k | PGAA-W Wasserstein | 4.0x | 0.958 | CD79A, CD79B, MS4A1 |
| Sepsis 20k | PGAA-W Wasserstein | 2.1x | — | TCR pathway |
| RA 10k | PGAA-W Wasserstein | 2.5x | — | PBMC/monocyte-associated cytokine pathway |
| PBMC 3k | PGAA-W Wasserstein | 2.9x | — | Multi-lineage markers |
| IBD 10k | PGAA-W Wasserstein | 5.8x | — | Gut epithelial disease-associated markers |

\newpage

\begin{landscape}

\section*{Supplementary Table 7. Implementation, reproducibility, and comparator status}

\scriptsize

\setlength{\LTleft}{0pt}
\setlength{\LTright}{0pt}
\begin{longtable}{>{\raggedright\arraybackslash}p{0.13\linewidth}>{\raggedright\arraybackslash}p{0.17\linewidth}>{\raggedright\arraybackslash}p{0.31\linewidth}>{\raggedright\arraybackslash}p{0.31\linewidth}}
\hline
Category & Item & Status or value & Rationale or caution \\
\hline
\endfirsthead
\hline
Category & Item & Status or value & Rationale or caution \\
\hline
\endhead
Preprocessing & Normalization & CPM target sum 10,000 followed by log1p & Standard scRNA-seq scale used across analyses \\
Preprocessing & Feature set & 2,000 HVGs with target inclusion & Keeps benchmark universe fixed; target inclusion is reported to avoid leakage concerns \\
Residualization & Cell-state proxy & K-means clusters, k = 5 & Fixed coarse proxy, not optimized per dataset \\
Residualization & Library-size covariate & Standardized library-size covariate & Controls broad depth effects \\
PGAA-W setting & Quantile grid & 0.01 to 0.99, 99 points & Same statistic used for observed and permuted data \\
PGAA-W setting & Permutations & 2,000 & Adequate for ranking and moderate p-values, not extreme genome-wide thresholds \\
PGAA-H setting & Histogram bins & n-bins = 20 manuscript starting setting & Pre-specify a small pilot grid such as 10, 20, 30 and 50; choose the setting using a negative-control, null, or unrelated perturbation, not by tuning the target-gene rank \\
PGAA-H setting & Permutations & 500 & Ranking evidence only; not FDR-controlled genome-wide discovery \\
Software & Python implementation & Included under \texttt{pgaa/} & Install with \texttt{pip install -e .} \\
Software & R implementation & Included under \texttt{pgaa\_r/} & Smoke/regression tests included \\
Software & License and archive & MIT; GitHub release \texttt{v0.1.0-code}; Zenodo DOI https://doi.org/10.5281/zenodo.20681141 & Software Heritage identifier is provided in manuscript metadata \\
Reproducibility & Automated checks & Python toy example, package tests, pytest suite, and R smoke tests & Included in the supplementary software archive \\
Reproducibility & Runtime guidance & PGAA-W about 5 min for 2,000 genes/2,000 permutations; PGAA-H under 2 min for 2,000 genes/500 permutations on one CPU core & Approximate workflow timings, not hardware-independent benchmarks \\
Comparator & SCEPTRE [Barry \textit{et al.}, 2021] & Direct Norman CEBPE benchmark & ELANE rank 1761/2012; p = 0.92 \\
Comparator & Wilcoxon, t-test, MAST & Direct Adamson UPR benchmark & Mean AUROCs 0.529, 0.523, and 0.406 \\
Comparator & MMD-PSM & Processed-source-data Norman CEBPE distribution-aware baseline & AUROC 0.499; 0/9 nominal CEBPE target hits; included as a distributional comparator, not a full benchmark suite. Clean-archive recomputation was verified when the processed Norman 2019 h5ad input was supplied via \texttt{NORMAN2019\_H5AD}. \\
Comparator & KS statistic & Norman KLF1/CEBPE/CEBPA multi-perturbation extension & Included as a distribution-aware two-sample baseline; PGAA-W Wasserstein had higher AUROC in all three curated target-panel contrasts \\
Reproducibility & Norman multi-perturbation extension & \texttt{scripts/benchmark\_norman\_multi\_perturbation.py} plus summary, gene-score, panel-audit, and metadata CSV files & Clean-archive recomputation was verified with \texttt{NORMAN2019\_H5AD}; target-panel genes are force-included because the processed HVG mask excludes all positive-panel genes \\
Comparator & Robust SCEPTRE, pertpy, Mixscape, scMAGeCK, DESeq2, SCDE, perturbation-response scoring, Augur, scPerturb & Discussed only & Related methods and ecosystem context; PGAA is positioned as gene-level distributional ranking, not as a replacement for formal association testing, perturbation-quality modeling, single-cell response-strength scoring, cell-type prioritization, or large benchmark resources \\
Figure-source mapping & Figure 1 & Generated from \texttt{figures\_png/figure\_caic\_entry.png} by the CAIC build scripts & Conceptual schematic; no numeric source table required \\
Figure-source mapping & Figure 2 & Rebuilt from Adamson benchmark CSV source data & Source-data reproducibility plus raw GSE90546/GSM2406675 sanity rerun script \\
Figure-source mapping & Figure 3 & Rebuilt from processed Norman CEBPE CSV summaries & Processed-source-data reproducibility; full recomputation requires \texttt{NORMAN2019\_H5AD} and has been verified from a clean archive when that input is supplied \\
Figure-source mapping & Figure 4 & Rebuilt from six-perturbation PGAA-H calibration CSV summaries & Processed-source-data reproducibility; full recomputation requires \texttt{NORMAN2019\_H5AD} and has been verified for the Norman multi-perturbation and MMD-PSM scripts when that input is supplied \\
Figure-source mapping & Figure 5 & Rebuilt from cross-dataset marker-recovery and CLL comparator CSV summaries & Source-data reproducibility from included CSV files \\
Reproducibility boundary & Raw GEO-to-final-figure rerun & Partial & Adamson raw sanity rerun is included; Norman and observational final figures rely on processed source-data CSV files in the review archive. Full Norman/MMD-PSM recomputation requires \texttt{NORMAN2019\_H5AD}; clean-archive reruns were verified when that processed input was available. \\
\hline
\end{longtable}

\normalsize
\end{landscape}

\newpage

## CLI Input/Output Schema

The PGAA command-line interface (\texttt{pgaa-run}) accepts the following inputs and produces the following outputs.

\subsection*{Input (required)}

\begin{center}
\begin{tabular}{ll>{\raggedright\arraybackslash}p{0.55\linewidth}}
\hline
Field & Type & Description \\
\hline
\texttt{-\/-expression} & CSV/TSV path & Normalized expression matrix (cells × genes, or genes × cells with \texttt{-\/-transpose}) \\
\texttt{-\/-metadata} & CSV/TSV path & Cell-level metadata; must contain columns for perturbation label and cell identifier \\
\texttt{-\/-target} & string & Target perturbation identifier (e.g., gene name or sgRNA label) \\
\texttt{-\/-out-prefix} & string & Output file prefix (writes \texttt{<prefix>.s1.csv} and \texttt{<prefix>.s2.csv}; \texttt{s1} corresponds to PGAA-W and \texttt{s2} corresponds to PGAA-H) \\
\hline
\end{tabular}
\end{center}

\subsection*{Input (optional)}

\begin{center}
\begin{tabular}{lll>{\raggedright\arraybackslash}p{0.44\linewidth}}
\hline
Field & Type & Default & Description \\
\hline
\texttt{-\/-group-column} & string & \texttt{group} & Column name for perturbation/control group labels \\
\texttt{-\/-perturbed-value} & string & \texttt{perturbed} & Value in group column marking perturbed cells \\
\texttt{-\/-control-value} & string & \texttt{control} & Value in group column marking control cells \\
\texttt{-\/-cell-type-column} & string & (none) & Column name for cell-type or cluster labels for within-cluster permutation \\
\texttt{-\/-library-size-column} & string & (none) & Column name for library size (for residualization) \\
\texttt{-\/-n-perms} & int & 2000 & Number of within-cluster permutations for PGAA-W \\
\texttt{-\/-n-perms-s2} & int & 500 & Number of within-cluster permutations for PGAA-H \\
\texttt{-\/-n-bins} & int & 20 & Number of histogram bins for PGAA-H \\
\texttt{-\/-top-n} & int & 2000 & Number of top-ranked genes to output \\
\texttt{-\/-seed} & int & 42 & Random seed for permutation reproducibility \\
\hline
\end{tabular}
\end{center}

\subsection*{Output}

\begin{center}
\begin{tabular}{ll>{\raggedright\arraybackslash}p{0.55\linewidth}}
\hline
Column & Type & Description \\
\hline
\texttt{gene} & string & Gene identifier \\
\texttt{PGAA-W score} & float & Quantile-grid Wasserstein distance (observed) \\
\texttt{PGAA-W p\_value\_perm} & float & Within-cluster permutation p-value (plus-one estimator) \\
\texttt{PGAA-W rank} & int & Rank by PGAA-W score (1 = highest) \\
\texttt{PGAA-H score} & float & RMS distance between top-3 peak-prominence vectors \\
\texttt{PGAA-H p\_value\_perm} & float & Within-cluster permutation p-value \\
\texttt{PGAA-H rank} & int & Rank by PGAA-H score \\
\texttt{storey\_upper\_tail\_ratio} & float & Uncapped Storey calibration diagnostic (R\_lambda; lambda=0.5) \\
\hline
\end{tabular}
\end{center}

\subsection*{Example}

\begin{verbatim}
pgaa-run \
  --expression expression.csv \
  --metadata metadata.csv \
  --target CEBPE \
  --group-column group \
  --perturbed-value CEBPE_sgRNA \
  --control-value NT_sgRNA \
  --cell-type-column cluster \
  --library-size-column library_size \
  --n-perms 2000 \
  --n-bins 20 \
  --out-prefix results/CEBPE
\end{verbatim}

Writes \texttt{results/CEBPE.s1.csv} and \texttt{results/CEBPE.s2.csv}. The historical output suffixes are retained for backward compatibility: \texttt{s1} corresponds to PGAA-W and \texttt{s2} corresponds to PGAA-H.

\newpage

## Supplementary Methods

### Additional modules

The Python and R packages include conditional mutual information and Fisher negative-binomial modules as exploratory extensions. These modules are not benchmarked as primary manuscript contributions. They are provided so users can explore perturbation effects on dependency structure or count-model dispersion, but the manuscript's claims are restricted to PGAA-W Wasserstein and the PGAA-H histogram-shape statistic.

### Permutation calibration

For PGAA-W and PGAA-H, perturbation labels are permuted within K-means clusters where cluster labels are available. This preserves coarse cell-state composition while disrupting the association between perturbation and expression. The observed statistic and each permuted statistic are computed using the same numerical definition. For PGAA-W this is the 99-quantile Wasserstein approximation. For PGAA-H this is the RMS distance between top-3 one-dimensional histogram peak-prominence values with the specified histogram bin count.

### CLL rank-score analysis

The CLL TCL1A analysis is an observational marker-recovery experiment, not an experimental perturbation. To avoid over-interpreting formal p-values in this setting, we use rank-based inverse-normal scores to compare gene orderings among PGAA-W, PGAA-H, and the combined score. The analysis supports complementarity between BCR-oriented PGAA-W hits and TCR-oriented PGAA-H hits, but it is not used as causal evidence.

### Simulation and zero-inflation controls

The simulation evaluates three response types across seven effect sizes and three replicates: pure mean shift, partial heterogeneous response, and mean-plus-bimodality. The simulation is designed to map operating regimes, not to exhaustively model all Perturb-seq count distributions. A negative-binomial null with 30% dropout was used as an additional control for zero-inflation; PGAA-H did not show systematic bimodality inflation in this null setting (mean PGAA-H = 0.031).

## Reproducibility Notes

All analyses use public data and fixed random seeds (`random_state=42` or the R equivalent). The public code-only repository contains the PGAA Python/R package, installation files, tests, and toy smoke-test scripts. The submitted supplementary archive contains manuscript-specific benchmark scripts and CSV source-data files for table and figure rebuilds. The Norman 2019 CEBPE summaries are provided as processed source-data CSV files because the full rerun requires the processed Norman h5ad input used in this study. `scripts/rebuild_adamson_full_results.py` regenerates the Adamson 2016 benchmark table from `figure_source_data/fig6_adamson_results.csv`; `scripts/figure_bhlhe40_details.py` rebuilds Supplementary Figure 1 from `figure_source_data/adamson_gene_level_scores.csv` and `figure_source_data/adamson_bhlhe40_distribution.csv`; `scripts/benchmark_adamson2016.py` additionally performs a raw GSE90546/GSM2406675 10X001 sanity rerun for the five selected perturbations. `scripts/benchmark_mmd_psm.py` documents the processed-source-data MMD-PSM comparator, and full recomputation requires setting `NORMAN2019_H5AD` to the processed Norman h5ad input. `scripts/benchmark_norman_multi_perturbation.py` documents the Norman KLF1/CEBPE/CEBPA multi-perturbation extension and writes summary, gene-score, panel-audit, and metadata CSV files; full recomputation also requires `NORMAN2019_H5AD`. Clean-archive reruns of both scripts were verified with the processed Norman h5ad input available. This is source-data reproducibility plus processed-data Norman reruns and a raw Adamson sanity rerun, not a fully unified raw GEO-to-final-figure workflow.
