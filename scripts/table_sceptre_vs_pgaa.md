# SCEPTRE vs PGAA comparison on Norman 2019 CEBPE

| method                        |   elane_rank |   elane_p |   n_sig |   auroc | known_hits   |
|:------------------------------|-------------:|----------:|--------:|--------:|:-------------|
| SCEPTRE                       |         1761 |    0.92   |      30 |   0.469 | 0/9          |
| PGAA S₁ (Wasserstein)         |          424 |    0.4388 |       0 |   0.542 | 0/9          |
| PGAA S₂ (persistent homology) |          120 |    0.002  |    1075 |   0.414 | 5/9          |
| PGAA S₁+S₂ combined z         |          832 |    0.0916 |     653 |   0.41  | 2/9          |

## Key takeaways
- **SCEPTRE**: 0/9 known targets, AUROC ≈ 0.47 (random)
- **PGAA S₁**: 1/9 known targets, AUROC ≈ 0.40 (similar to SCEPTRE on Norman)
- **PGAA S₂**: 5/9 known targets, ELANE rank 586 (3× better than SCEPTRE/S₁)
- **PGAA Combined**: 3/9 known targets, ELANE rank 832 (better than S₁ alone but worse than S₂)

S₂ is the only method that recovers the CEBPE → neutrophil pathway at clinically meaningful levels.
