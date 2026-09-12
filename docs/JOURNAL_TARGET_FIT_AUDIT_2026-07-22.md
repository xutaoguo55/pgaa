# Journal Target Fit Audit

Date checked: 2026-07-22

## Verdict

The primary target is now **Bioinformatics**, as an **Original Paper** framed around a computational claim-state compiler for perturbation transcriptomics. This is a higher-upside target than NAR Genomics and Bioinformatics, but it requires stronger method positioning, explicit comparator fairness, and ablation logic.

The safest fallback remains **NAR Genomics and Bioinformatics**. The highest-upside time-sensitive alternative is **Patterns**, using its active **Reanalysis** call, but this is higher desk-risk because the paper would need to be reframed from a bioinformatics method paper into a broad data-science reanalysis story by the 2026-08-01 deadline.

## Ranked Targets

| Rank | Journal | Recommended article type | Fit | Acceptance plausibility | Best hook | Main risk |
|---:|---|---|---|---|---|---|
| 1 | Bioinformatics | Original Paper | strong | moderate-to-realistic if method-first | claim-state compiler for perturbation transcriptomics with formal false-promotion metrics, comparator contracts, ablations, and a branch-vulnerability use case | must look like a computational methods advance, not a collection of biological reanalyses |
| 2 | NAR Genomics and Bioinformatics | Methods Paper or Standard Paper | strongest scope fit | highest fallback probability | reproducible genomics/bioinformatics method that compiles public perturbation evidence into bounded claim states and branch-specific therapeutic hypotheses | lower strategic ceiling than Bioinformatics |
| 3 | Patterns | Reanalysis submission | strong but narrow window | moderate-to-low | creative reanalysis of high-impact public perturbation and EGFR-resistance datasets that converts static public data into actionable claim states | broad data-science framing and 2026-08-01 call deadline create high execution pressure |
| 4 | PLOS Computational Biology | Methods or Software | good | moderate | open-source method/software of broad utility that yields biological insight from public single-cell and perturbation data | must demonstrate exceptional importance and broad adoption potential |
| 5 | Genome Biology | Methodology or Software | prestigious but risky | low-to-moderate | genomic/post-genomic method with real-data utility and state-of-the-art comparisons | current evidence ceiling and limited ATM validation are likely desk-review weaknesses |
| 6 | Cell Reports Methods | Methodological Article | partial | low-to-moderate | robust reproducible analytical framework with translational demonstration | Cell Press threshold for transformative, broadly interesting methods is high |
| 7 | Bioinformatics Advances | Original Paper | safe fallback | high | same as Bioinformatics but with broader acceptance aperture | lower strategic upside than NAR Genomics and Bioinformatics |

## Best Submission Angle

Title direction:

**A reproducible claim-state compiler for public perturbation transcriptomics identifies branch-specific vulnerabilities in EGFR-mutant drug tolerance**

Core selling point:

PGAA should be presented as a reproducible evidence compiler that prevents unsupported biological promotion while still producing positive, testable hypotheses. The strongest manuscript case is the EGFR-resistance branch-to-ATM vulnerability arc: state bifurcation, frozen external assignment, matched drug-screen calibration, fifth-system dynamic support, and a prospective promotion gate.

## Fit Notes From Current Journal Information

| Journal | Relevant public information checked | Implication for this manuscript |
|---|---|---|
| NAR Genomics and Bioinformatics | Interdisciplinary genomics and bioinformatics journal focused on large-scale data analysis; publishes Application Notes, Standard Papers, Methods Papers, Methods and Benchmark Surveys, and Opinion Articles; reproducibility is a strong focus. URL: https://academic.oup.com/nargab | Best direct match: reproducible genomics/bioinformatics method plus source-data and benchmark discipline. |
| Bioinformatics | Publishes new developments in bioinformatics and computational biology; author guidance includes Application Notes for novel software or algorithm implementations, with software availability requirements. URLs: https://academic.oup.com/bioinformatics/ and https://academic.oup.com/bioinformatics/pages/author-guidelines | Good match only if positioned as an Original Paper with clear algorithmic novelty and comparator benchmarking, not as a short Application Note. |
| Patterns | Active Reanalysis call requests compelling and creative reanalyses of prior high-importance, broad-impact works; listed deadline: 2026-08-01. URL: https://www.cell.com/patterns/special-issues/call-for-papers/reanalysis | Timely opportunity if rapidly reframed as a data-science reanalysis of public perturbation atlases; not the lowest-risk route. |
| PLOS Computational Biology | Publishes Research, Methods, and Software articles; Methods/Software should be outstanding and able to provide new biological insights with broad adoption potential. URLs: https://journals.plos.org/ploscompbiol/s/journal-information and https://journals.plos.org/ploscompbiol/s/submission-guidelines | Solid second-tier computational biology target if the manuscript emphasizes broad software utility and biological insight. |
| Genome Biology | Publishes genomic/post-genomic research, methods, and software; Methodology and Software articles should be clear advances over state-of-the-art, ideally with side-by-side same-dataset demonstrations and real-data utility. URLs: https://link.springer.com/journal/13059/submission-guidelines/methodology and https://link.springer.com/journal/13059/submission-guidelines/software | Possible stretch target only after strengthening same-dataset comparator benchmarks and source-level biological validation. |
| Cell Reports Methods | Publishes transformative methods, platforms, and analytical frameworks; primary criterion is a robust, reproducible method that spurs scientific progress. URL: https://www.cell.com/cell-reports-methods/aims | Fit exists, but the current manuscript may look too specialized unless the branch-vulnerability compiler is generalized beyond EGFR and single-cell examples. |

## Practical Recommendation

Submit first to **Bioinformatics** after completing the method-first restructuring in `docs/BIOINFORMATICS_METHOD_POSITIONING.md`. Use **NAR Genomics and Bioinformatics** as the fallback if the Bioinformatics package cannot clearly demonstrate methodological novelty beyond ranking.

For Bioinformatics, the manuscript should not lead with ATM as if it were a pharmacology paper. It should lead with a formal claim-state compiler, quantitative false-promotion benchmarks, fair comparator contracts, and ablations; ATM should appear later as the strongest biological demonstration of why claim-state compilation matters.
