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
| S1 Wasserstein | 0.337 | 0.0035 | 0/9 | No broad target-set recovery |
| S2 persistence | 0.476 | 0.0076 | 2/9 | Focused ELANE/PRTN3 ranking signal; not broad target-set recovery |

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
| CEBPE | approximately 1.0-1.3 in $n_{\text{bins}}=20$ runs | 0.04 | Main ranking result |
| KLF1 | 1.15 | 0.70 | Negative specificity check |
| SLC4A1 | 0.67 | 0.16 | Not supported |
| BAK1 | 0.10 | 0.005 | Over-sensitive; not interpretable as specificity |
| DUSP9 | 0.68 | 0.90 | Not supported |
| CBL | 0.72 | 0.58 | Not supported |

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

| Dataset | Evidence level | Role and main limitation |
|---|---|---|
| Norman 2019 K562 CRISPRa (GSE133344) | Experimental Perturb-seq | CEBPE case study and S2 calibration checks. The S2 result is mainly an ELANE ranking signal; 500 permutations do not support genome-wide FDR-controlled discovery. |
| Adamson 2016 K562 CRISPRi (GSE90546) | Experimental Perturb-seq | Independent UPR benchmark. The scope is small: five pre-specified sgRNAs and 13 UPR positives in the HVG universe. |
| CLL 20k (GSE111014) | Observational scRNA-seq | S1 marker recovery and S1/S2 complementarity. Virtual TCL1A grouping is not an intervention. |
| Sepsis 20k (GSE167363) | Observational scRNA-seq | S1 marker recovery; marker enrichment only. |
| RA 10k (GSE159117) | Observational scRNA-seq | S1 marker recovery; marker enrichment only. |
| PBMC 3k (10x Genomics demo) | Observational scRNA-seq | Scale and marker recovery; demo dataset, not a perturbation screen. |
| IBD 10k (GSE116222) | Observational scRNA-seq | S1 marker recovery; marker enrichment only. |

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
| Python implementation | Included under `pgaa/`; installable with `pip install -e .`. |
| R implementation | Included under `pgaa_r/`; tested with the local R smoke/regression suite. |
| License | MIT; `LICENSE` file included. |
| Public repository | Code-only repository at https://github.com/xutaoguo55/pgaa. |
| Archived version | GitHub release `v0.1.0-code`; Zenodo DOI https://doi.org/10.5281/zenodo.20681141; Software Heritage identifier supplied in the manuscript and metadata. |
| Supplementary software file | `PGAA_supplementary_code.zip` supplied with the submission package. |
| Environment | Python requirements, R package files, `environment.yml`, and `Dockerfile` are included. |
| Automated tests | Python toy example, package tests, pytest suite, and R smoke tests are included. |
| Dataset manifest check | Included as `scripts/verify_dataset_manifest.py`. |
| Main PDF build | Included as `communications_medicine/build_cm_pdf.py`. |
| Figure rebuild scripts | Adamson and simulation figure scripts are included in `scripts/`. |
| Raw-data-to-figure status | Partial; Norman S1 uses processed h5ad input, whereas Adamson tables use curated source-data CSVs. |

## Supplementary Table S9. Runtime and memory summary

Runtime depends on cell count, gene count, and permutation depth. The timings below are single-core approximate values from the manuscript workflow and are intended as practical guidance rather than hardware-independent benchmarks. Local checks were run on macOS with Python 3.11, R 4.x, dependencies from `requirements.txt`, and package version `pgaa 0.1.0`.

| Task | Input and setting | Runtime and memory note |
|---|---|---|
| S1 Wasserstein full run | 2,000 genes; matched perturbation/control cells; 2,000 permutations; single CPU core. | About 5 minutes. Fits in memory for processed benchmark matrices; RAM depends mainly on cells x genes. |
| S2 persistence full run | 2,000 genes; matched perturbation/control cells; 500 permutations; single CPU core. | Under 2 minutes. Histogram-based and lower memory pressure than repeated model fitting. |
| Adamson table rebuild | 5 perturbations and 13 UPR positives; Python 3.11. | Seconds. Rebuilds from curated source-data CSV, not raw GEO. |
| Norman consistency audit | Manuscript package; Python 3.11. | Seconds. Checks current values and required assets. |
| Main PDF build | Manuscript plus 5 main figures; Pandoc plus TinyTeX/XeLaTeX. | About 1 minute; requires local LaTeX installation. |

## Supplementary Table S10. Result reproduction map

| Manuscript item | Reproduction status |
|---|---|
| Figure 1 schematic | Rebuild with `scripts_generate_cm_entry_figure.py`. |
| Figure 2 and Table S2 | Reproduced from included dataset-summary CSV and figure source files; observational marker recovery only. |
| Figure 3 and Table S5 | Rebuild Adamson source table, then rebuild the Adamson benchmark figure. |
| Table S12 | Rebuild with the Adamson full-results script. |
| Figure 4 and Table S4 | Rebuild Norman comparison tables and figure; narrow CEBPE ranking use case. |
| Figure 5 and Table S4 | Reproduced from six-perturbation calibration outputs; calibration guardrails, not discovery claims. |
| Supplementary Figure S1 | Reproduced from ELANE histogram source files and CSVs. |
| Supplementary Figure S2 | Reproduced from CLL processed source data; observational rank-score analysis only. |
| Supplementary Figure S3 | Rebuild with `scripts/figure_simulation.py`. |
| Supplementary Figure S4 and Table S1 | Reproduced from S2 bin-sensitivity source data and QQ-plot source files. |
| Supplementary Figure S5 | Reproduced from Adamson BHLHE40 source data and figure source files. |
| Main and supplementary PDFs | Main PDF built with `build_cm_pdf.py`; supplementary PDF built from `SUPPLEMENTARY_CM.md`. |

## Supplementary Table S11. Comparator and benchmark status

This table separates methods that were directly benchmarked in this manuscript from related tools that are discussed as adjacent or complementary. It is included to avoid implying that every cited method was run in every benchmark.

Directly benchmarked comparators:

| Method | Benchmark evidence | Interpretation |
|---|---|---|
| SCEPTRE [Barry *et al.*, 2021] | Norman CEBPE CRISPRa: ELANE rank 1761/2012, $p = 0.92$; AUROC 0.469; 0/9 CEBPE targets in top 100. | Direct comparator for the CEBPE case; not a general claim that SCEPTRE performs poorly. |
| Wilcoxon rank-sum | Adamson UPR CRISPRi: mean AUROC 0.529 across five perturbations. | Simple location-shift baseline. |
| t-test | Adamson UPR CRISPRi: mean AUROC 0.523 across five perturbations. | Simple mean-shift baseline. |
| MAST [Finak *et al.*, 2015] | Adamson UPR CRISPRi: mean AUROC 0.406 across five perturbations. | Differential-expression comparator in this focused benchmark. |

Discussed but not directly benchmarked:

| Tool or method | Role or remaining gap |
|---|---|
| Robust SCEPTRE [Barry *et al.*, 2024] | Same broad problem class; direct robust-SCEPTRE benchmarking remains necessary. |
| pertpy [Heumos *et al.*, 2026] | Integration ecosystem rather than a single statistic comparator. |
| Mixscape [Papalexi *et al.*, 2021] | Complementary responder/non-responder assignment method. |
| scMAGeCK [Yang *et al.*, 2020] | Complementary genotype-phenotype and screen-level method. |
| DESeq2 [Love *et al.*, 2014] and SCDE [Kharchenko *et al.*, 2014] | Background references; not prioritized for direct non-mean distributional benchmarking. |

## Supplementary Table S12. Adamson 2016 method-level descriptive confidence intervals

Intervals are 95% t intervals across the five pre-specified Adamson perturbations. They summarize between-perturbation variability in this focused benchmark and should not be interpreted as population-level uncertainty over all possible Perturb-seq screens.

| Method | n perturbations | Mean AUROC | AUROC 95% CI | Mean AUPRC | AUPRC 95% CI |
|---|---:|---:|---:|---:|---:|
| S1 Wasserstein | 5 | 0.786 | 0.766-0.807 | 0.0191 | 0.0160-0.0222 |
| S2 persistence | 5 | 0.748 | 0.662-0.834 | 0.0253 | 0.0010-0.0495 |
| Wilcoxon rank-sum | 5 | 0.529 | 0.415-0.643 | 0.0089 | 0.0048-0.0131 |
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

All analyses use public data and fixed random seeds (`random_state=42` or the R equivalent). The public code-only repository contains the PGAA Python/R package, installation files, tests, and toy smoke-test scripts. The submitted supplementary software archive contains the manuscript-specific benchmark scripts and CSV files used to generate the manuscript tables and figures. For the Norman 2019 CEBPE analysis, `scripts/compare_combinations.py` regenerates the full S1 permutation table and combined-method summaries from the processed h5ad input used in this study. For the Adamson 2016 benchmark, `scripts/rebuild_adamson_full_results.py` regenerates the manuscript table from the curated figure source-data file `figure_source_data/fig6_adamson_results.csv`. This should be described as source-data reproducibility, not a one-command raw GEO-to-final-figure workflow. The supplementary archive is designed for package smoke tests, source-data table rebuilds, and manuscript PDF rebuilds.
