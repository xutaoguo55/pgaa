from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.gse193258_target_specificity_audit import (
    build_gse193258_target_specificity_audit,
    write_gse193258_target_specificity_audit_package,
)


def _build_drug_associations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "drug": "AZD0156",
                "putative_target": "ATM",
                "spearman_rho": 1.0,
                "exact_one_sided_p": 1 / 24,
                "response_z_range": 2.15,
                "total_hit_calls": 3,
                "association_rank": 1,
            },
            {
                "drug": "Crizotinib",
                "putative_target": "ALK",
                "spearman_rho": 0.8,
                "exact_one_sided_p": 1 / 6,
                "response_z_range": 2.63,
                "total_hit_calls": 3,
                "association_rank": 2,
            },
            {
                "drug": "Quisinostat",
                "putative_target": "HDAC",
                "spearman_rho": 0.8,
                "exact_one_sided_p": 1 / 6,
                "response_z_range": 2.30,
                "total_hit_calls": 1,
                "association_rank": 3,
            },
            {
                "drug": "AZD8835",
                "putative_target": "PIK3CA",
                "spearman_rho": 0.6,
                "exact_one_sided_p": 5 / 24,
                "response_z_range": 1.46,
                "total_hit_calls": 3,
                "association_rank": 4,
            },
            {
                "drug": "AZD5153",
                "putative_target": "BRD4",
                "spearman_rho": -0.8,
                "exact_one_sided_p": 1.0,
                "response_z_range": 2.16,
                "total_hit_calls": 2,
                "association_rank": 5,
            },
        ]
    )


def _build_target_context() -> pd.DataFrame:
    rows = []
    for table_id in ["Supplementary_Data_1", "Supplementary_Data_2"]:
        for target_class, n_rows, n_drugs in [
            ("ATM", 18, 1),
            ("ALK", 12, 1),
            ("HDAC", 22, 1),
            ("PIK3CA", 10, 1),
            ("BRD4", 8, 1),
        ]:
            rows.append(
                {
                    "table_id": table_id,
                    "target_class": target_class,
                    "n_rows": n_rows,
                    "n_unique_cell_lines": 4,
                    "n_unique_drugs": n_drugs,
                }
            )
    return pd.DataFrame(rows)


def test_gse193258_target_specificity_audit_identifies_atm_as_unique_exact_hit() -> None:
    summary, contrast = build_gse193258_target_specificity_audit(
        _build_drug_associations(), _build_target_context()
    )

    atm = summary[summary["target_class"].eq("ATM")].iloc[0]
    alk = summary[summary["target_class"].eq("ALK")].iloc[0]
    hdac = summary[summary["target_class"].eq("HDAC")].iloc[0]

    assert atm["specificity_role"] == "lead_exact_significant_positive"
    assert atm["positive_tier"] == 1
    assert round(float(atm["positive_tier_margin_to_next"]), 3) == 0.2
    assert bool(atm["exact_significant_positive"])
    assert alk["specificity_role"] == "runner_up_positive_tier"
    assert hdac["specificity_role"] == "runner_up_positive_tier"
    assert int(contrast.iloc[0]["exact_significant_positive_count"]) == 1
    assert contrast.iloc[0]["runner_up_target_classes"] == "ALK, HDAC"


def test_gse193258_target_specificity_audit_package_rebuilds_outputs(tmp_path: Path) -> None:
    evidence_out = tmp_path / "evidence/gse193258_target_specificity.tsv"
    report_out = tmp_path / "docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md"
    figure_out = tmp_path / "figures_png/gse193258_target_specificity_map.png"
    caption_out = tmp_path / "docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md"
    paths = write_gse193258_target_specificity_audit_package(
        drug_associations=_build_drug_associations(),
        evidence_out=evidence_out,
        report_out=report_out,
        target_context=_build_target_context(),
        figure_out=figure_out,
        figure_pdf_out=tmp_path / "figures_png/gse193258_target_specificity_map.pdf",
        caption_out=caption_out,
    )

    summary = pd.read_csv(evidence_out, sep="\t")
    contrast = pd.read_csv(
        tmp_path / "evidence/gse193258_target_specificity_contrast.tsv", sep="\t"
    )

    assert paths["evidence"] == evidence_out
    assert paths["contrast"] == tmp_path / "evidence/gse193258_target_specificity_contrast.tsv"
    assert paths["report"] == report_out
    assert paths["figure"] == figure_out
    assert paths["figure"].exists()
    assert paths["figure"].stat().st_size > 0
    assert paths["figure_pdf"] == tmp_path / "figures_png/gse193258_target_specificity_map.pdf"
    assert paths["caption"] == caption_out
    assert caption_out.read_text(encoding="utf-8").startswith(
        "# GSE193258 Target Specificity Figure Support Text"
    )
    assert set(summary["target_class"]).issuperset({"ATM", "ALK", "HDAC"})
    assert int(contrast.iloc[0]["positive_target_count"]) == 4
    assert report_out.read_text(encoding="utf-8").startswith(
        "# GSE193258 Target Specificity Audit"
    )
    assert "only exact-significant positive target class" in report_out.read_text(
        encoding="utf-8"
    )
