# Prospective EGFR Resistance-Branch Assignment

## Fourth-System Result

The GSE249721 classifier was frozen before GSE193258 expression was downloaded. All four osimertinib DTP models project to the adaptive-stress branch, with no external gene re-ranking.

| Cell line | DTP branch score | Assignment | Permutation p | Gate |
|---|---:|---|---:|---|
| PC9 | 2.714 | adaptive_stress | 0.0002 | pass |
| HCC827 | 0.758 | adaptive_stress | 0.0002 | pass |
| H1975 | 1.208 | adaptive_stress | 0.0002 | pass |
| HCC2935 | 0.535 | adaptive_stress | 0.0002 | pass |

## Branch-Specific Vulnerability Prediction

The adaptive-stress assignment prioritizes TEAD, BRD4, and MEK inhibition. These are not generic annotations: the source study's independent combination screens identified TEAD, BRD4, and MEK inhibitors among recurrent osimertinib-DTP vulnerabilities.

| Cell line | Priority | Target | Candidate intervention |
|---|---:|---|---|
| PC9 | 1 | TEAD | K-975 |
| PC9 | 2 | BRD4 | AZD5153 |
| PC9 | 3 | MEK1/2 | selumetinib_or_trametinib |
| HCC827 | 1 | TEAD | K-975 |
| HCC827 | 2 | BRD4 | AZD5153 |
| HCC827 | 3 | MEK1/2 | selumetinib_or_trametinib |
| H1975 | 1 | TEAD | K-975 |
| H1975 | 2 | BRD4 | AZD5153 |
| H1975 | 3 | MEK1/2 | selumetinib_or_trametinib |
| HCC2935 | 1 | TEAD | K-975 |
| HCC2935 | 2 | BRD4 | AZD5153 |
| HCC2935 | 3 | MEK1/2 | selumetinib_or_trametinib |

## Positive Interpretation

The fourth dataset converts the bifurcation model into a prospective prediction: prolonged osimertinib exposure repeatedly enters the adaptive-stress branch across distinct EGFR-mutant backgrounds, and that branch points to a convergent TEAD-BRD4-MEK vulnerability program. PC9 has the strongest branch projection and is therefore the lead model for branch-score-versus-drug-response calibration.

## Source-Audit Link

The underlying RNA-seq matrix is also covered by `docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md`, which records the local source artifacts and keeps the prospective branch assignment layer auditable.
