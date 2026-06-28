# SCEPTRE vs PGAA comparison on Norman 2019 CEBPE

| method                             |   elane_rank |   elane_p |   n_sig |   auroc | known_hits   |
|:-----------------------------------|-------------:|----------:|--------:|--------:|:-------------|
| SCEPTRE                            |         1761 |    0.92   |      30 |   0.469 | 0/9          |
| PGAA-W Wasserstein                 |         1452 |    0.2234 |    1083 |   0.337 | 1/9          |
| PGAA-H histogram-shape (n_bins=20) |           57 |    0.0399 |      66 |   0.476 | 1/9          |
| PGAA-W+PGAA-H combined z           |          427 |    0.0378 |     473 |   0.424 | 3/9          |

## Key takeaways
- **SCEPTRE**: 0/9 known targets, AUROC ≈ 0.47 (random)
- **PGAA-W**: 1/9 known targets, ELANE rank 1452, AUROC 0.337
- **PGAA-H**: 1/9 known targets, ELANE rank 57 in the pre-specified n_bins=20 run, AUROC 0.476
- **PGAA Combined**: 3/9 known targets, ELANE rank 427, AUROC 0.424

PGAA-H gives the strongest ELANE ranking in this pre-specified CEBPE analysis; the result is ranking evidence, not genome-wide FDR-controlled discovery.
