---
header-includes:
  - \usepackage{graphicx}
---

# Supplementary Information

## Supplementary Figures

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_elane_histogram.png}

\textbf{Supplementary Figure S1.} ELANE heterogeneous expression pattern in Norman 2019 CEBPE CRISPRa.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_4.png}

\textbf{Supplementary Figure S2.} CLL 20k exploratory complementarity analysis comparing Wasserstein and persistence rankings. This observational pseudo-perturbation analysis is used for marker-program ranking only.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_5.png}

\textbf{Supplementary Figure S3.} Simulation ablation across mean-shift, heterogeneous-response, and mixed-response regimes. These simulations are operating-regime diagnostics rather than a full generative model of scRNA-seq counts.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.85\textwidth]{figures_png/figure_s2_calibration_qq.png}

\textbf{Supplementary Figure S4.} Persistence-test calibration QQ plot and p-value histogram for the pre-specified Norman 2019 CEBPE $n_{\text{bins}} = 20$ analysis.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_s2_bhlhe40.png}

\textbf{Supplementary Figure S5.} Adamson 2016 BHLHE40 perturbation details: gene-level S1 versus S2 scores with UPR markers highlighted, and expression distributions for representative UPR genes.
\end{center}

\clearpage

\begin{center}
\includegraphics[width=0.95\textwidth]{figures_png/figure_pgaa_workflow.png}

\textbf{Supplementary Figure S6.} PGAA distribution-aware Perturb-seq testing workflow. The schematic summarizes the input data, preprocessing, S1 Wasserstein statistic, S2 persistence statistic, permutation calibration, and outputs.
\end{center}

\clearpage

## Supplementary Table S1. Persistence hyperparameter sensitivity

Norman 2019 CEBPE sensitivity sweep. These runs use 200 permutations for speed and are used to evaluate bin-count sensitivity, not to claim genome-wide significance.

| n_bins | ELANE rank | ELANE p | n_sig at p<0.05 | Storey pi0 | Known hits |
|---:|---:|---:|---:|---:|---:|
| 20 | 32 | 0.0249 | 66 | 1.321 | 1/9 |
| 30 | 1807 | 0.6716 | 387 | 0.407 | 0/9 |
| 50 | 489 | 0.0050 | 1063 | 0.246 | 3/9 |
| 75 | 460 | 0.0050 | 1087 | 0.227 | 4/9 |
| 100 | 468 | 0.0050 | 1087 | 0.226 | 5/9 |
| 150 | 446 | 0.0050 | 1073 | 0.225 | 4/9 |

## Supplementary Table S2. Marker-recovery datasets

The five observational datasets are used for marker recovery rather than causal inference. The top-100 enrichment compares known positive marker recovery against background ranking.

| Dataset | Statistic | Top-100 enrichment | AUROC | Key known targets hit |
|---|---|---:|---:|---|
| CLL 20k | S1 Wasserstein | 4.0x | 0.87 | CD79A, CD79B, MS4A1 |
| Sepsis 20k | S1 Wasserstein | 2.1x | 0.87 | TCR pathway |
| RA 10k | S1 Wasserstein | 2.5x | 0.87 | Cytokine pathway |
| PBMC 3k | S1 Wasserstein | 2.9x | 0.87 | Multi-lineage markers |
| IBD 10k | S1 Wasserstein | 5.8x | 0.92 | Gut immune markers |

## Supplementary Table S3. Adamson 2016 UPR marker set

The Adamson benchmark uses a curated UPR marker set covering IRE1, PERK, ATF6, ERAD, and chaperone branches. Thirteen markers were retained in the 2,000-HVG benchmark universe used for AUROC/AUPRC calculation.

| Branch | Genes considered |
|---|---|
| IRE1 | ERN1, XBP1, HSPA5, DNAJB9, DNAJC3, SEC61A1 |
| PERK | EIF2AK3, ATF4, DDIT3, PPP1R15A, TRIB3, CHAC1 |
| ATF6 | ATF6, MBTPS1, MBTPS2, CALR, PDIA4, HYOU1 |
| ERAD | EDEM1, SYVN1, SEL1L, HERPUD1, DERL1 |
| Chaperones | HSPA5, HSP90B1, CALR, PDIA3, PDIA6, ERP29 |

\clearpage

## Supplementary Table S4. Norman 2019 CEBPE comparison and specificity checks

The main Norman 2019 CEBPE comparison uses the pre-specified $n_{\text{bins}} = 20$ persistence run. The p-values are interpreted as ranking evidence because 500 permutations cannot support genome-wide FDR-controlled discovery.

| Method | ELANE rank | ELANE p | Notes |
|---|---:|---:|---|
| SCEPTRE | 1761/2012 | 0.92 | Mean-shift calibrated comparator |
| S1 Wasserstein | 1452/2012 | 0.223 | Distributional statistic, weak for ELANE |
| S2 persistence | 57/2012 | 0.04 | Main $n_{\text{bins}} = 20$ ranking result |

Performance across all nine curated CEBPE targets:

| Method | AUROC | AUPRC | Top-100 targets | Interpretation |
|---|---:|---:|---:|---|
| S1 Wasserstein | 0.337 | 0.0035 | 0/9 | No broad recovery |
| S2 persistence | 0.476 | 0.0076 | 2/9 | ELANE/PRTN3 only |

Target-level ranks in the pre-specified CEBPE analysis:

| Target | S1 rank | S1 p | S2 rank | S2 p | S2 score |
|---|---:|---:|---:|---:|---:|
| ELANE | 1452 | 0.223 | 57 | 0.040 | 0.004125 |
| AZU1 | 500 | 0.001 | 856 | 0.597 | 0.001582 |
| MPO | 1752 | 0.529 | 1727 | 1.000 | 0.000000 |
| LYZ | 1372 | 0.172 | 928 | 0.643 | 0.001415 |
| CTSG | 1911 | 0.759 | 1727 | 1.000 | 0.000000 |
| GFI1 | 1178 | 0.078 | 1506 | 0.950 | 0.000707 |
| PRTN3 | 1364 | 0.163 | 97 | 0.068 | 0.004245 |
| DEFA1 | 1109 | 0.058 | 1185 | 0.872 | 0.000707 |
| RNASE2 | 1316 | 0.141 | 1105 | 0.776 | 0.001415 |

Cross-perturbation ELANE checks using the CEBPE target set as the specificity reference:

| Perturbation | Storey pi0 | ELANE p | Interpretation |
|---|---:|---:|---|
| CEBPE | approx. 1.0-1.3 | 0.04 | Main result |
| KLF1 | 1.15 | 0.70 | Negative check |
| SLC4A1 | 0.67 | 0.16 | Not supported |
| BAK1 | 0.10 | 0.005 | Over-sensitive; not interpreted |
| DUSP9 | 0.68 | 0.90 | Not supported |
| CBL | 0.72 | 0.58 | Not supported |

\clearpage

## Supplementary Table S5. Adamson 2016 UPR CRISPRi benchmark

Random AUPRC baseline = 0.0065.

PGAA distribution-aware statistics:

| Perturbation | n_pert | S1 AUROC | S1 AUPRC | S2 AUROC | S2 AUPRC |
|---|---:|---:|---:|---:|---:|
| SPI1_pDS255 | 686 | 0.806 | 0.0223 | 0.658 | 0.0110 |
| ZNF326_pDS262 | 555 | 0.767 | 0.0160 | 0.700 | 0.0144 |
| BHLHE40_pDS258 | 542 | 0.788 | 0.0178 | 0.833 | 0.0594 |
| CREB1_pDS269 | 499 | 0.772 | 0.0208 | 0.781 | 0.0202 |
| DDIT3_pDS263 | 468 | 0.799 | 0.0184 | 0.769 | 0.0213 |

Baseline AUROC values:

| Perturbation | Wilcoxon | t-test | MAST |
|---|---:|---:|---:|
| SPI1_pDS255 | 0.687 | 0.650 | 0.439 |
| ZNF326_pDS262 | 0.526 | 0.531 | 0.391 |
| BHLHE40_pDS258 | 0.466 | 0.475 | 0.365 |
| CREB1_pDS269 | 0.498 | 0.482 | 0.461 |
| DDIT3_pDS263 | 0.468 | 0.476 | 0.375 |

## Supplementary Table S6. Dataset roles and evidence level

This table separates causal perturbation benchmarks from observational marker-recovery analyses. The observational datasets are included to assess whether S1 produces biologically coherent rankings, not to validate causal effects.

| Dataset | Evidence class | Manuscript role | Main limitation |
|---|---|---|---|
| Norman 2019 K562 CRISPRa (GSE133344) | Experimental Perturb-seq | CEBPE case example; S2 calibration checks | Narrow ELANE/PRTN3 ranking signal; no FDR-controlled discovery |
| Adamson 2016 K562 CRISPRi (GSE90546) | Experimental Perturb-seq | Independent UPR benchmark | Five pre-specified sgRNAs; 13 UPR positives in the HVG universe |
| CLL 20k (GSE111014) | Observational scRNA-seq | Disease-state marker recovery; S1/S2 complementarity | Virtual TCL1A grouping is not an intervention |
| Sepsis 20k (GSE167363) | Observational scRNA-seq | Marker recovery | Marker enrichment only |
| RA 10k (GSE159117) | Observational scRNA-seq | Marker recovery | Marker enrichment only |
| PBMC 3k (10x Genomics demo) | Observational scRNA-seq | Scale and marker recovery | Demo dataset; not a perturbation screen |
| IBD 10k (GSE116222) | Observational scRNA-seq | Marker recovery | Marker enrichment only |

\clearpage

## Supplementary Table S7. Main parameter settings

| Component | Value used | Rationale or caution |
|---|---|---|
| Normalization | CPM target sum 10,000 followed by log1p | Standard scRNA-seq scale used across analyses. |
| Feature set | 2,000 HVGs with target inclusion | Keeps the benchmark universe fixed; target inclusion is reported to avoid leakage concerns. |
| Cell-state residualization | K-means clusters, $k = 5$ | Fixed coarse proxy, not optimized per dataset. |
| Library-size residualization | Standardized library-size covariate | Controls broad depth effects. |
| S1 quantiles | 0.01 to 0.99, 99 points | Same statistic used for observed and permuted data. |
| S1 permutations | 2,000 | Adequate for ranking and moderate p-values, not extreme genome-wide thresholds. |
| S2 binning | $n_{\text{bins}} = 20$ | Pre-specified default in Norman CEBPE; sensitivity sweep required. |
| S2 permutations | 500 | Ranking evidence only; not FDR-controlled genome-wide discovery. |
| S2 vector | Top 3 peaks, zero-padded | Captures dominant histogram-shape differences. |
| Random seed | 42 | Fixed for reproducibility. |

## Supplementary Table S8. Software availability and reproducibility status

| Item | Status |
|---|---|
| Python implementation | Included under `pgaa/`; install with `pip install -e .`. |
| R implementation | Included under `pgaa_r/`; smoke/regression tests included. |
| License | MIT; `LICENSE` file included. |
| Public repository | Code-only repository: https://github.com/xutaoguo55/pgaa. |
| Archived version | GitHub release `v0.1.0-code`; Zenodo DOI https://doi.org/10.5281/zenodo.20681141; Software Heritage identifier in manuscript metadata. |
| Supplementary software file | `PGAA_supplementary_code.zip`. |
| Environment | `requirements.txt`, `environment.yml`, `Dockerfile`, and R package files. |
| Automated tests | Python toy example, package tests, pytest suite, and R smoke tests. |
| Dataset manifest check | Included as `scripts/verify_dataset_manifest.py`. |
| Figure rebuild scripts | Adamson and simulation scripts included under `scripts/`. |
| Raw-data-to-figure status | Partial: Norman uses processed h5ad input; Adamson tables use curated source-data CSVs. |

## Supplementary Table S9. Runtime and memory summary

Runtime depends on cell count, gene count, and permutation depth. The timings below are single-core approximate values from the manuscript workflow and are intended as practical guidance rather than hardware-independent benchmarks. Local checks were run on macOS with Python 3.11, R 4.x, dependencies from `requirements.txt`, and package version `pgaa 0.1.0`.

| Task | Input/setting | Runtime/memory note |
|---|---|---|
| S1 Wasserstein full run | 2,000 genes; matched cells; 2,000 permutations; one CPU core | About 5 min; RAM scales mainly with cells x genes |
| S2 persistence full run | 2,000 genes; matched cells; 500 permutations; one CPU core | Under 2 min; lower memory pressure than repeated model fitting |
| Adamson benchmark summary | Five perturbations; 13 UPR positives; Python 3.11 | Seconds; rebuilds summary from curated source-data CSV |

\clearpage

## Supplementary Table S10. Comparator status

Direct comparators included in benchmark analyses:

| Comparator | Benchmark used | Result or role |
|---|---|---|
| SCEPTRE [Barry *et al.*, 2021] | Norman CEBPE CRISPRa | ELANE rank 1761/2012; $p = 0.92$; AUROC 0.469; 0/9 targets in top 100 |
| Wilcoxon rank-sum | Adamson UPR CRISPRi | Mean AUROC 0.529 across five perturbations |
| t-test | Adamson UPR CRISPRi | Mean AUROC 0.523 across five perturbations |
| MAST [Finak *et al.*, 2015] | Adamson UPR CRISPRi | Mean AUROC 0.406 across five perturbations |

Related tools or background comparators not directly benchmarked:

| Tool or reference | Status | Reason for inclusion |
|---|---|---|
| Robust SCEPTRE [Barry *et al.*, 2024] | Discussed | Same broad class of calibrated single-cell CRISPR-screen testing |
| pertpy [Heumos *et al.*, 2026] | Discussed | Perturbation-analysis ecosystem and integration framework |
| Mixscape [Papalexi *et al.*, 2021] | Discussed | Responder/non-responder assignment in perturbation screens |
| scMAGeCK [Yang *et al.*, 2020] | Discussed | Genotype-phenotype and screen-level modeling |
| DESeq2 [Love *et al.*, 2014] and SCDE [Kharchenko *et al.*, 2014] | Background | RNA-seq and single-cell differential-expression context |

\clearpage

## Supplementary Table S11. Adamson descriptive intervals

Intervals are 95% t intervals across the five pre-specified Adamson perturbations. They summarize between-perturbation variability in this focused benchmark and should not be interpreted as population-level uncertainty over all possible Perturb-seq screens. S1 denotes Wasserstein; S2 denotes persistence.

| Method | n | Mean AUROC | AUROC 95% CI | Mean AUPRC | AUPRC 95% CI |
|---|---:|---:|---:|---:|---:|
| S1 | 5 | 0.786 | 0.766-0.807 | 0.0191 | 0.0160-0.0222 |
| S2 | 5 | 0.748 | 0.662-0.834 | 0.0253 | 0.0010-0.0495 |
| Wilcoxon | 5 | 0.529 | 0.415-0.643 | 0.0089 | 0.0048-0.0131 |
| t-test | 5 | 0.523 | 0.430-0.616 | 0.0085 | 0.0050-0.0120 |
| MAST | 5 | 0.406 | 0.354-0.458 | 0.0014 | 0.0012-0.0016 |

## Supplementary Methods S1. Additional modules

The Python and R packages include conditional mutual information and Fisher negative-binomial modules as exploratory extensions. These modules are not benchmarked as primary manuscript contributions. They are provided so users can explore perturbation effects on dependency structure or count-model dispersion, but the manuscript's claims are restricted to S1 Wasserstein and S2 persistence.

## Supplementary Methods S2. Permutation calibration

For S1 and S2, perturbation labels are permuted within K-means clusters where cluster labels are available. This preserves coarse cell-state composition while disrupting the association between perturbation and expression. The observed statistic and each permuted statistic are computed using the same numerical definition. For S1 this is the 99-quantile Wasserstein approximation. For S2 this is the top-3 persistence-vector distance with the specified histogram bin count.

## Supplementary Methods S3. CLL rank-score analysis

The CLL TCL1A analysis is an observational marker-recovery experiment, not an experimental perturbation. To avoid over-interpreting formal p-values in this setting, we use rank-based inverse-normal scores to compare gene orderings among S1, S2, and the combined score. The analysis supports complementarity between BCR-oriented S1 hits and TCR-oriented S2 hits, but it is not used as causal evidence.

## Supplementary Methods S4. Simulation and zero-inflation controls

The simulation evaluates three response types across seven effect sizes and three replicates: pure mean shift, partial heterogeneous response, and mean-plus-bimodality. The simulation is designed to map operating regimes, not to exhaustively model all Perturb-seq count distributions. A negative-binomial null with 30% dropout was used as an additional control for zero-inflation; the persistence statistic did not show systematic bimodality inflation in this null setting (mean S2 = 0.031).

## Reproducibility Notes

All analyses use public data and fixed random seeds (`random_state=42` or the R equivalent). The public code-only repository contains the PGAA Python/R package, installation files, tests, and toy smoke-test scripts. The submitted supplementary archive contains manuscript-specific benchmark scripts and CSV source-data files for table and figure rebuilds. `scripts/compare_combinations.py` regenerates the Norman 2019 CEBPE summaries from the processed h5ad input used in this study, and `scripts/rebuild_adamson_full_results.py` regenerates the Adamson 2016 benchmark table from `figure_source_data/fig6_adamson_results.csv`. This is source-data reproducibility, not a one-command raw GEO-to-final-figure workflow.
