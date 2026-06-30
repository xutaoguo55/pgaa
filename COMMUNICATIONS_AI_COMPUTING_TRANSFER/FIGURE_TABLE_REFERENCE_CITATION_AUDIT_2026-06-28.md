# Figure and table reference audit

Date: 2026-06-28

Scope: final Communications AI & Computing PGAA submission package in `COMMUNICATIONS_AI_COMPUTING_TRANSFER`.

## Verdict

PASS after remediation.

Main Figure 1-5, main Table 1-3, Supplementary Figure 1-7, and Supplementary Table 1-7 are now cited in first-appearance order in the source manuscript, final upload DOCX text extraction, and manuscript PDF text extraction. The supplementary PDF contains Supplementary Figure 1-7 and Supplementary Table 1-7 in numeric order.

## Corrections made

| Area | Previous issue | Correction |
|---|---|---|
| Supplementary figures | First citation order was Supplementary Figure 5, 1, 4, 3, 2, 6, 7. | Renumbered and reordered supplementary figures by first main-text citation: BHLHE40 details, ELANE histogram, calibration QQ, simulation, CLL complementarity, PGAA workflow, external marker-recovery stress checks. |
| Supplementary tables | First citation order was Supplementary Table 6, 4, 5, 1, 2, 3, 7. | Renumbered and reordered supplementary tables by first main-text citation: Adamson UPR marker set, Adamson per-perturbation benchmark, Norman multi-perturbation benchmark, Norman CEBPE target details, PGAA-H bin sensitivity, marker-recovery datasets, implementation/reproducibility status. |
| Figure 2 caption | Caption still pointed panel d values to old Supplementary Table 6. | Updated the DOCX and PDF build scripts so Figure 2 points to Supplementary Table 2. |
| Supplementary Methods | BHLHE40 figure-rebuild note still pointed to old Supplementary Figure 5. | Updated to Supplementary Figure 1. |
| Supplementary Table 7 rendering | The supplementary PDF printed a raw `\end{landscape}` command and then clipped the dense implementation/reproducibility table because `tabularx` could not paginate. | Added the missing landscape opening, converted Supplementary Table 7 to a paginating `longtable`, rebuilt the PDF, and verified that the table now spans pages 12-13 without clipped rows or raw LaTeX commands. |

## Final main-text order

| Item type | First unique order in source Markdown | Final DOCX text | Final manuscript PDF text |
|---|---|---|---|
| Main figures | 1, 2, 3, 4, 5 | 1, 2, 3, 4, 5 | 1, 2, 3, 4, 5 |
| Main tables | 1, 2, 3 | 1, 2, 3 | 1, 2, 3 |
| Supplementary figures | 1, 2, 3, 4, 5, 6, 7 | 1, 2, 3, 4, 5, 6, 7 | 1, 2, 3, 4, 5, 6, 7 |
| Supplementary tables | 1, 2, 3, 4, 5, 6, 7 | 1, 2, 3, 4, 5, 6, 7 | 1, 2, 3, 4, 5, 6, 7 |

## Final mapping

### Main figures

| Figure | First main-text citation | Build source | Evidence class |
|---|---|---|---|
| Figure 1 | Framework overview | `figures_png/figure_caic_entry.png` | Conceptual framework and workflow |
| Figure 2 | Adamson benchmark | `figures_png/figure_adamson_benchmark.png` | Perturb-seq proof-of-principle benchmark |
| Figure 3 | Norman CEBPE PGAA-H example | `figures_png/figure_norman_main_caic.png` | Narrow CEBPE ranking example |
| Figure 4 | Norman PGAA-H calibration | `figures_png/figure_3.png` | Calibration guardrail |
| Figure 5 | Observational marker recovery | `figures_png/figure_1.png` | Marker-recovery stress check |

### Supplementary figures

| Supplementary figure | Content | Source image |
|---|---|---|
| Supplementary Figure 1 | Adamson BHLHE40 perturbation details | `figures_png/figure_s2_bhlhe40.png` |
| Supplementary Figure 2 | Norman CEBPE ELANE histogram | `figures_png/figure_elane_histogram.png` |
| Supplementary Figure 3 | PGAA-H calibration QQ and p-value histogram | `figures_png/figure_s2_calibration_qq.png` |
| Supplementary Figure 4 | Simulation ablation | `figures_png/figure_5.png` |
| Supplementary Figure 5 | CLL complementarity analysis | `figures_png/figure_4.png` |
| Supplementary Figure 6 | PGAA workflow | `figures_png/figure_pgaa_workflow.png` |
| Supplementary Figure 7 | External marker-recovery stress checks | `figures_png/figure_1.png` |

### Main tables

| Table | Content |
|---|---|
| Table 1 | Evidence levels across PGAA evaluations |
| Table 2 | Adamson 2016 UPR CRISPRi benchmark summary |
| Table 3 | Norman 2019 CEBPE ranking and calibration summary |

### Supplementary tables

| Supplementary table | Content |
|---|---|
| Supplementary Table 1 | Adamson 2016 UPR marker set |
| Supplementary Table 2 | Adamson 2016 UPR CRISPRi per-perturbation benchmark |
| Supplementary Table 3 | Norman 2019 multi-perturbation CRISPRa target-panel benchmark |
| Supplementary Table 4 | Norman 2019 CEBPE target-level details |
| Supplementary Table 5 | PGAA-H histogram-bin sensitivity |
| Supplementary Table 6 | Marker-recovery datasets |
| Supplementary Table 7 | Implementation, reproducibility, and comparator status |

## Commands run

| Check | Status |
|---|---|
| `python3 build_caic_docx.py` | passed |
| `python3 build_caic_pdf.py` | passed |
| `python3 build_caic_supplementary_pdf.py` | passed; reported Supplementary figures 1-7 and Supplementary tables 1-7 |
| `python3 build_caic_supplementary_zip.py` | passed |
| `python3 build_caic_journal_upload_packet.py` | passed |
| DOCX text extraction with `pandoc` | passed |
| Main and supplementary PDF text extraction with `pdftotext` | passed |
| Source/DOCX/PDF figure-table first-unique order script | passed |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/MANUSCRIPT.docx` | passed |
| `unzip -t FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING/PGAA_supplementary_code.zip` | passed |
| `unzip -t PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip` | passed |
| `python3 strict_caic_final_audit.py` | passed |
| `python3 final_upload_strict_audit_2026_06_25.py` | passed |
| `python3 verify_caic_transfer_ready.py` | passed |
| Supplementary PDF visual render after Table 7 remediation | passed; Supplementary Table 7 spans pages 12-13 and Supplementary Methods starts on page 14 |

## Notes

- A naive regex can still report plain `Figure 1-5` inside Supplementary Table 7 because that table maps the five main figures to source data. This is intentional and not a main-text ordering problem.
- A plain `Table 3` mention inside Supplementary Table 4 states that the main Norman CEBPE result is summarized in main Table 3. This is intentional and not a supplementary-table numbering error.
- The final upload directory remains the four-file journal packet: cover letter PDF, manuscript DOCX, supplementary PDF, and supplementary code ZIP.
