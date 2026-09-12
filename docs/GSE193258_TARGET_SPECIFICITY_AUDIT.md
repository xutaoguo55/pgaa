# GSE193258 Target Specificity Audit

The matched-screen package spans a broad target landscape. This audit asks whether ATM is merely one positive hit or the cleanest positive target-class signal in the screen package.

## Target-Class Ranking

| Rank | Target class | Lead drug | Spearman rho | Exact p | Positive tier | Specificity role | Replicate rows | Summary rows |
|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | ATM | AZD0156 | 1.000 | 0.0417 | 1 | lead_exact_significant_positive | 18 | 14 |
| 2 | ALK | Crizotinib | 0.800 | 0.1667 | 2 | runner_up_positive_tier | 16 | 14 |
| 3 | HDAC | Quisinostat | 0.800 | 0.1667 | 2 | runner_up_positive_tier | 22 | 14 |
| 4 | PIK3CA | AZD8835 | 0.600 | 0.2083 | 3 | weaker_positive_tier | 20 | 14 |
| 5 | FGFR | AZD4547 | 0.400 | 0.3750 | 4 | weaker_positive_tier | 16 | 14 |
| 6 | PRMT5 | GSK591 | 0.200 | 0.4583 | 5 | weaker_positive_tier | 14 | 14 |
| 7 | MEK1/2 | Selumetinib | 0.200 | 0.4583 | 5 | weaker_positive_tier | 18 | 14 |
| 8 | IGF-IR | BMS-754807 | 0.000 | 0.5417 | NA | negative_or_inverse | 20 | 14 |
| 9 | CDK4/6 | Abemaciclib | 0.000 | 0.5417 | NA | negative_or_inverse | 20 | 14 |
| 10 | AURKB | AZD2811 | 0.000 | 0.5417 | NA | negative_or_inverse | 21 | 14 |
| 11 | AKT | Capivasertib | 0.000 | 0.5417 | NA | negative_or_inverse | 18 | 14 |
| 12 | PIK3CB | AZD8186 | -0.200 | 0.6250 | NA | negative_or_inverse | 22 | 14 |
| 13 | PARP | Olaparib | -0.200 | 0.6250 | NA | negative_or_inverse | 16 | 14 |
| 14 | JAK1 | AZD4205 | -0.400 | 0.7917 | NA | negative_or_inverse | 14 | 14 |
| 15 | GPX4 | RSL3 | -0.600 | 0.8333 | NA | negative_or_inverse | 20 | 14 |
| 16 | AURKA | LY3298176 | -0.800 | 0.9583 | NA | negative_or_inverse | 19 | 15 |
| 17 | AXL | AZ'5845 | -0.800 | 0.9583 | NA | negative_or_inverse | 32 | 14 |
| 18 | SHP2 | RMC-4550 | -0.800 | 0.9583 | NA | negative_or_inverse | 16 | 14 |
| 19 | BRD4 | AZD5153 | -1.000 | 1.0000 | NA | negative_or_inverse | 24 | 14 |

## Specificity Contrast

| Contrast | Lead target | Runner-up target classes | Lead rho | Runner-up rho | Rho margin | Positive targets | Exact-significant positives | Total target classes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| ATM_vs_runner_up_positive_tier | ATM | ALK, HDAC | 1.000 | 0.800 | 0.200 | 7 | 1 | 19 |

## Interpretation Boundary

ATM is the only exact-significant positive target class in the screen landscape. ALK and HDAC occupy the runner-up positive tier; the remaining positive classes are weaker, and the negative classes fall below zero. That makes ATM the cleanest positive branch-linked target-class signal inside the broad GSE193258 screen package.

- Positive target classes: 7
- Exact-significant positive target classes: 1
- Exact-significant positive target classes named explicitly: ATM
- Total target classes in the audit: 19
- Target classes with source-table coverage across the screen package: 19

This tightens the manuscript claim to a lead-target specificity statement without promoting ATM to general clinical validation.
