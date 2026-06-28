# Reference truthfulness audit

Date: 2026-06-28

Scope: `MANUSCRIPT_CAIC.md` references 1-35 after the Communications AI & Computing hardening pass.

## Verdict

No fabricated, unresolvable, or mismatched references were found.

The final reference list contains 35 references:

- 29 DOI-bearing references were checked through exact Crossref DOI metadata and DOI resolution.
- 6 book, proceedings, or DOI-sparse records were checked against publisher, society, library, or journal pages.
- All references are cited in the manuscript.
- First citation order is sequential: 1-35.

## Automated checks

| Check | Result | Evidence |
|---|---|---|
| Reference count | PASS | 35 references in final DOCX/source. |
| Reference numbering | PASS | 1-35 without gaps or duplicates. |
| All references cited | PASS | `uncited=[]; missing=[]` in `STRICT_CAIC_FINAL_AUDIT_2026-06-27.md`. |
| First appearance order | PASS | First citation sequence is 1-35. |
| DOI metadata | PASS | 29 DOI-bearing references match exact Crossref `/works/{doi}` title metadata. |
| DOI resolution | PASS | 29 DOI-bearing references resolve. |

The detailed machine table is `REFERENCE_VERIFICATION_TABLE_2026-06-27.tsv`.

## DOI-bearing references

| Refs | Status | Notes |
|---|---|---|
| 1-20 | PASS | Perturb-seq, single-cell, perturbation-method, and biology references match Crossref DOI title metadata. The newly added references 19 and 20 resolve to Song et al. 2025 Nature Cell Biology and Peidli et al. 2024 Nature Methods, respectively. |
| 23, 28-35 | PASS | Mathematical, statistical, and preprocessing references match Crossref DOI title metadata and resolve. |

Crossref returned single-hyphen page ranges, while the manuscript uses Nature-style double hyphens in Markdown source before typesetting. These are formatting differences, not bibliographic mismatches.

## Manual-source references

| Ref | Manuscript record | External verification |
|---|---|---|
| 21 | MacQueen, J. Some methods for classification and analysis of multivariate observations. In Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability Vol. 1, 281-297 (University of California Press, 1967). | Verified against Project Euclid and Berkeley Library records for the same title, author, proceedings volume, and page range. |
| 22 | Villani, C. Optimal Transport: Old and New (Springer, 2009). | Verified against Springer/Google Books/Semantic Scholar records for the Springer 2009 book; DOI record exists as `10.1007/978-3-540-71050-9`. |
| 24 | Good, P. I. Permutation, Parametric, and Bootstrap Tests of Hypotheses, 3rd edn (Springer, 2005). | Verified against Springer and Google Books records for the 3rd edition, Springer, 2005. |
| 25 | Efron, B. & Tibshirani, R. J. An Introduction to the Bootstrap (Chapman & Hall, 1993). | Verified against Taylor & Francis/Cambridge/Google Books records for the Chapman & Hall book. Some electronic records list later eBook metadata, but the 1993 Chapman & Hall print citation is standard. |
| 26 | Edelsbrunner, H. & Harer, J. Computational Topology: An Introduction (American Mathematical Society, 2010). | Verified against the AMS book page and AMS endmatter/ISBN record. |
| 27 | Bubenik, P. Statistical topological data analysis using persistence landscapes. J. Mach. Learn. Res. 16, 77-102 (2015). | Verified against the official JMLR article page and PDF. |

## External spot checks used

- Crossref exact DOI lookup for all DOI-bearing references.
- DOI resolution through the strict audit script.
- Project Euclid / Berkeley Library for MacQueen 1967.
- Springer / Google Books / Semantic Scholar for Villani 2009.
- Springer / Google Books for Good 2005.
- Taylor & Francis / Cambridge / Google Books for Efron and Tibshirani 1993.
- AMS for Edelsbrunner and Harer 2010.
- JMLR for Bubenik 2015.

## Residual caveats

- The manuscript does not include DOIs in the formatted reference list. This is acceptable if the target journal style does not require DOI display, but DOIs are available for many references.
- Reference 25 has common print-year versus electronic-record differences: the manuscript uses the standard 1993 Chapman & Hall citation, while some modern platform pages expose later eBook metadata.
- Book/proceedings records were manually checked rather than DOI-verified in the automated table.

## Conclusion

The reference list is truthful and internally consistent. No reference needs removal for being fabricated, untraceable, or mismatched. The only remaining decision is stylistic: whether to display DOIs in the reference list if the journal or author prefers them.
