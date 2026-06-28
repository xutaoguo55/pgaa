# Figure Regeneration Prompts for PGAA Manuscript

All source data is in this folder (`figure_source_data/`). Generate each figure as a high-resolution PNG (300 dpi). Use colorblind-friendly colors. Each figure should have panel labels (A), (B), etc., and all panels should have axis labels.

---

## Supplementary Figure S6: PGAA Workflow Schematic

No data file needed. Create a clean, professional flowchart with 6-7 boxes:

```
Input (expression matrix + perturbation labels)
  ↓
Preprocessing (QC, log(CPM+1), HVG, K-means k=5)
  ↓
Covariate Residualization (X - Z(ZᵀZ)⁻¹ZᵀX)
  ↙              ↘
Wasserstein Test    PGAA-H histogram-shape diagnostic
(PGAA-W, 2000 perms)   (PGAA-H, n_bins=20, 500 perms)
  ↘              ↙
Output (Gene rankings, p-values, Storey upper-tail ratio, Combined z)
```

Use different colors for different stages. Add a subtitle: "Permutation calibration + upper-tail ratio diagnostic throughout". Clean sans-serif font. Avoid cluttered arrows.

---

## Figure 1: Multi-dataset Wasserstein Validation

**Data**: `fig2_multidataset.csv`
Columns: Dataset, POS_enrichment, NEG_enrichment, ratio, cells, AUROC

Three panels:
- **(A)** Grouped bar chart: POS (blue) vs NEG (orange) enrichment for 5 datasets (CLL, Sepsis, RA, PBMC, IBD). Y-axis: "Known markers in top 100".
- **(B)** Bar chart: POS/NEG ratio for each dataset. Red dashed line at 2.0 (2× enrichment threshold). Gray dashed at 1.0 (random). Label each bar with the ratio value and cell count.
- **(C)** Method comparison on CLL: bar chart showing Wasserstein (AUROC 0.87), t-test, Mann-Whitney, Spearman. Two y-axes: POS/NEG ratio (left, blue bars) and AUROC (right, purple bars).

---

## Figure 2: Norman 2019 CEBPE CRISPRa

**Data**: `fig3_norman_s2_volcano.csv` (2012 rows: gene, PGAA-H, p_value_perm), `fig3_elane_ranks.csv`

Three panels:
- **(A)** Volcano plot: x=PGAA-H value, y=-log10(p_value_perm). Gray dots for most genes. Highlight 9 known CEBPE targets (ELANE, AZU1, MPO, LYZ, CTSG, GFI1, PRTN3, DEFA1, RNASE2) in red/magenta with gene labels. Red dashed line at -log10(0.05).
- **(B)** Bar chart: ELANE rank for SCEPTRE (1761, gray), Wasserstein (1452, orange), PGAA-H (57, blue). Label each bar with exact rank and p-value. Add "25× better" label above the PGAA-H bar. Horizontal dashed line at 2012 (total genes). Title: "ELANE rank improvement".
- **(C)** Summary table: Method | ELANE rank | ELANE p | n_sig | Calibration. Rows: SCEPTRE, Wasserstein, PGAA-H histogram-shape diagnostic. Highlight the PGAA-H row in green.

---

## Figure 3: Calibration Across Six Perturbations

**Data**: `fig4_calibration.csv`, `fig4_heatmap.csv`

Three panels:
- **(A)** Scatter plot: n_sig (x-axis, log scale) vs Storey upper-tail ratio (y-axis). Each point is one perturbation (KLF1, CBL, SLC4A1, DUSP9, CEBPE, BAK1), labeled. Color by calibration quality: green (well-calibrated R_lambda>0.9), yellow (0.5-0.9), red (<0.5). Horizontal dashed line at R_lambda=1.0 (ideal). Point size proportional to cell count.
- **(B)** Heatmap: rows=9 CEBPE target genes, columns=6 perturbations. Color = p-value (green=low/red=high). Annotate cells with p<0.05 with asterisk. Title: "CEBPE target gene p-values across perturbations".
- **(C)** Bar chart: number of CEBPE targets with p<0.05 for each perturbation. CEBPE bar in red (expected), others in blue. Y-axis: "# CEBPE target genes sig (p<0.05)". Title: "CEBPE target leakage across perturbations".

---

## Figure 4: CLL 20k — Wasserstein and PGAA-H histogram-shape Complementarity

**Data**: `fig5_cll_s1_top100.csv`, `fig5_cll_s2_top100.csv`, `fig5_overlap.txt`

Three panels:
- **(A)** Line/scatter: BCR and TCR gene ranks across methods. Show CD79A, CD79B, MS4A1, CD24 (BCR) in red and TRBV7-6, TRAV12-1, CD3E, CD3D (TCR) in blue, with lines connecting their ranks from PGAA-W to PGAA-H. Y-axis: rank (log scale, lower is better). Title: "BCR & TCR marker ranks".
- **(B)** Horizontal bar chart: top 30 genes by combined score (PGAA-W+PGAA-H). Color bars: red for BCR genes, blue for TCR genes, gray for others. X-axis: -log10(p). Label BCR/TCR genes with asterisks. Legend: BCR*, TCR†, Other.
- **(C)** Grouped bar chart: number of significant (p<0.05) BCR and TCR genes for PGAA-W alone, PGAA-H alone, and PGAA-W+PGAA-H combined. BCR in red, TCR in blue. Title: "BCR & TCR recovery by method".

Overlap info: Top-100 overlap between PGAA-W and PGAA-H is only 6/100. Combined z recovers 3 BCR + 11 TCR.

---

## Figure 5: Adamson 2016 UPR CRISPRi Independent Validation

**Data**: `fig6_adamson_results.csv`
Columns: target, n_pert, auroc_s1, auprc_s1, auroc_s2, auprc_s2, auroc_wilcox, auprc_wilcox, auroc_ttest, auprc_ttest, auroc_mast, auprc_mast

Five panels:
- **(A)** Text box summarizing benchmark design: "Adamson 2016 UPR CRISPRi (GSE90546)\n5,680 K562 cells after QC\n5 UPR perturbations (468–686 cells each)\n1,759 non-targeting controls\ncurated UPR marker set (13 genes in HVGs)". 
- **(B)** Grouped bar chart: mean AUROC for Wasserstein (0.786), PGAA-H (0.748), Wilcoxon (0.529), t-test (0.523), MAST (0.406). Color: PGAA methods in blue/green, baselines in gray. Red dashed line at 0.5 (random). Label each bar with value. Title: "Mean AUROC across 5 perturbations".
- **(C)** Bar chart: mean AUPRC for Wasserstein (0.0191), PGAA-H (0.0253), Random baseline (0.0065). Add text annotations: "2.9× random" and "3.9× random". Title: "AUPRC vs random baseline".
- **(D)** Grouped bar chart: per-perturbation AUROC. X-axis: SPI1, ZNF326, BHLHE40, CREB1, DDIT3. Three bars per perturbation: Wasserstein (blue), PGAA-H (green), Wilcoxon (gray). Red dashed at 0.5. Title: "Per-perturbation AUROC".
- **(E)** BHLHE40 highlight bar chart: Wasserstein (0.788), PGAA-H (0.833), Wilcoxon, t-test, MAST for BHLHE40 only. Title: "BHLHE40: PGAA-H wins". Annotate PGAA-H bar with "0.833".

---

## Figure 6: Simulation Ablation

**Data**: `fig7_simulation.csv`
Columns: type (A/B/C), theta, rep, TPR_PGAA-W, TPR_PGAA-H, TPR_comb

Three panels (one per perturbation type):
- **(A)** Type A (mean shift): TPR vs theta for PGAA-W (orange), PGAA-H (blue), Combined z (green). Error bars showing ±1 SE across 3 replicates. Y-axis: "TPR @ FPR=0.05". X-axis: "Effect size θ". Title: "(A) Mean shift".
- **(B)** Type B (partial bimodality, 40%): Same format. Title: "(B) Partial bimodality (40%)". Add note: "PGAA-H advantage emerges under stronger bimodality (see Norman 2019)".
- **(C)** Type C (mixed): Same format. Title: "(C) Mixed".

Common y-axis limits [0, 1.1]. Legend in panel A only.

---

## Supplementary Figure PGAA-W: QQ Plot

Generate from the data in `fig3_norman_s2_volcano.csv` (p_value_perm column):
- Left panel: QQ plot (-log10 observed vs -log10 expected). Gray dots, black diagonal line.
- Right panel: p-value histogram with uniform reference line.

---

## Style Guidelines

- Font: Arial or Helvetica, 10-12pt for labels
- Colors: Use colorblind-friendly palette (e.g., `#2196F3` blue, `#4CAF50` green, `#FF9800` orange, `#E91E63` red/magenta, `#9E9E9E` gray)
- DPI: 300
- Format: PNG for preview, PDF/SVG for final
- Remove top and right spines on all plots
- Add light gridlines where helpful
- Panel labels: bold, top-left corner of each panel
- Figure title: centered above all panels, 14pt bold
