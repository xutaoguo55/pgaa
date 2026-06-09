# Paper Tables


## Table 1. PGAA performance across six datasets

| Dataset           | Best PGAA statistic   | POS/NEG enrichment (top 100)   |   AUROC (known markers) | Key known targets hit   | S₁ ELANE-rank   | S₂ ELANE-rank             |
|:------------------|:----------------------|:-------------------------------|------------------------:|:------------------------|:----------------|:--------------------------|
| CLL 20k           | S₁                    | 4.0×                           |                   0.87  | CD79A, CD79B, MS4A1     | n/a             | n/a                       |
| Sepsis 20k        | S₁                    | 2.1×                           |                   0.87  | TCR pathway             | n/a             | n/a                       |
| RA 10k            | S₁                    | 2.5×                           |                   0.87  | Cytokine pathway        | n/a             | n/a                       |
| PBMC 3k           | S₁                    | 2.9×                           |                   0.87  | Multi-lineage           | n/a             | n/a                       |
| IBD 10k           | S₁                    | 5.8×                           |                   0.92  | Gut immune              | n/a             | n/a                       |
| Norman 2019 CEBPE | S₂                    | n/a                            |                   0.476 | ELANE rank 57/2012      | 1452/2012       | 57/2012 (25× improvement) |


## Table 2. S₂ calibration across six Perturb-seq perturbations (Norman 2019)

| Perturbation   |   n_perturbed cells |   n_sig (p<0.05) |   Storey π̂₀ | Calibration verdict             | Recommended use      |
|:---------------|--------------------:|-----------------:|------------:|:--------------------------------|:---------------------|
| KLF1           |                1197 |               54 |       1.148 | well-calibrated                 | S₂ + S₁              |
| CBL            |                 663 |              173 |       0.715 | acceptable                      | S₂ + S₁              |
| SLC4A1         |                1000 |              222 |       0.665 | mild over-sensitive             | S₁ preferred         |
| DUSP9          |                 731 |              460 |       0.679 | over-sensitive                  | S₁ only              |
| CEBPE          |                 566 |             1063 |       0.246 | severely over-sensitive         | S₂ only with caution |
| BAK1           |                 687 |             1789 |       0.104 | catastrophically over-sensitive | S₁ only              |


## Table 3. Decision rule for choosing S₁, S₂, or combined z

| Perturbation type                              | Signal type                                    | Recommended statistic                                      | Calibration check                                         | Validated on                                           |
|:-----------------------------------------------|:-----------------------------------------------|:-----------------------------------------------------------|:----------------------------------------------------------|:-------------------------------------------------------|
| Mean shift (KO/OE of TF)                       | All perturbed cells shift by α                 | S₁ alone (Wasserstein)                                     | Negative control: GAPDH perturbation → π̂₀ > 0.5           | CLL/Sepsis/RA/PBMC/IBD (5 datasets), simulation Type A |
| Bimodality shift (CRISPRa, weak-effect)        | Fraction of cells shift; mean may be unchanged | S₂ alone (persistent homology) with calibration diagnostic | Multi-perturbation diagnostic: π̂₀ should be > 0.5 on null | Norman 2019 CEBPE (ELANE rank 57/2012)                 |
| Mixed (multi-signal, heterogeneous population) | Mean shift + bimodality + dependencies         | Combined z = (z_S₁ + z_S₂)/√2                              | Both statistics should be informative before combining    | CLL 20k TCL1A (3 BCR + 11 TCR)                         |
| Unknown a priori                               | Need to test                                   | S₁ first; add S₂ if S₁ finds nothing                       | Always run S₂ on a null perturbation first                | Norman 2019 (KLF1 π̂₀=1.15 as good null)                |