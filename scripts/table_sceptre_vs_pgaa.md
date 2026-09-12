# SCEPTRE vs PGAA comparison on Norman 2019 CEBPE

| method                             |   elane_rank |   elane_p |   n_sig |   auroc |    auprc | known_hits   | top100_hits   |
|:-----------------------------------|-------------:|----------:|--------:|--------:|---------:|:-------------|:--------------|
| SCEPTRE                            |         1761 |    0.92   |      30 |   0.469 | nan      | 0/9          | N/A           |
| PGAA-W Wasserstein                 |         1452 |    0.2234 |    1083 |   0.337 |   0.0035 | 1/9          | 0/9           |
| PGAA-H histogram-shape (n_bins=20) |           57 |    0.0399 |      66 |   0.476 |   0.0076 | 1/9          | 2/9           |
| PGAA-W+PGAA-H combined z           |          427 |    0.0378 |     473 |   0.424 |   0.0044 | 3/9          | 0/9           |

`known_hits` counts known targets with nominal permutation p < 0.05; `top100_hits` counts known targets ranked in the top 100 of 2012 genes (counted only when the whole tie block falls inside rank 100).

## Key takeaways
- **SCEPTRE**: 0/9 known targets at p<0.05, AUROC ≈ 0.47 (random); AUPRC and top-100 count not recomputed because raw SCEPTRE gene-level output is not in this archive
- **PGAA-W**: 1/9 at p<0.05, 0/9 in top 100, ELANE rank 1452, AUROC 0.337, AUPRC 0.0035
- **PGAA-H**: 1/9 at p<0.05, 2/9 in top 100, ELANE rank 57 in the pre-specified n_bins=20 run, AUROC 0.476, AUPRC 0.0076
- **PGAA Combined**: 3/9 at p<0.05, 0/9 in top 100, ELANE rank 427, AUROC 0.424, AUPRC 0.0044

PGAA-H gives the strongest ELANE ranking in this pre-specified CEBPE analysis; the result is ranking evidence, not genome-wide FDR-controlled discovery.
