from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.gse335846_external_dynamic_corroboration import (
    build_external_dynamic_corroboration_summary,
    render_external_dynamic_corroboration,
    write_external_dynamic_corroboration_package,
    write_external_dynamic_corroboration_assets,
)


ROOT = Path(__file__).resolve().parents[1]


def test_external_dynamic_corroboration_summary_anchors_preprint() -> None:
    preprint = ROOT / "sources/gse335846_dynamic_atm/preprint_733326.txt"
    summary = build_external_dynamic_corroboration_summary(preprint)

    assert list(summary["evidence_layer"]) == [
        "pc9_dynamic_dtp_replication",
        "atm_sensitivity",
        "atr_sensitivity",
        "hcc4006_bridge",
    ]
    assert "40-47" in summary.iloc[0]["line_refs"]
    assert "1434-1442" in summary.iloc[0]["line_refs"]
    assert "653-677" in summary.iloc[1]["line_refs"]
    assert "1577-1580" in summary.iloc[3]["line_refs"]
    assert summary.iloc[1]["manuscript_role"] == "Reinforces the ATM lead"
    assert summary.iloc[2]["manuscript_role"] == "Shows the DDR logic extends beyond ATM"
    assert summary.iloc[3]["manuscript_role"] == "Secondary generalization bridge"
    assert set(summary["claim_boundary"]) == {
        "corroboration_only_not_source_table_upgrade"
    }


def test_external_dynamic_corroboration_report_preserves_boundary_language() -> None:
    preprint = ROOT / "sources/gse335846_dynamic_atm/preprint_733326.txt"
    source_audit = pd.DataFrame(
        [
            {
                "source_id": "gse335846_geo_family",
                "source_numerical_status": "rna_seq_source_table_available_for_branch_axis",
                "usable_for_current_analysis": "branch_induction",
                "missing_for_upgrade": "Figure 3B replication-origin polarity and Figure 4F confluence source values.",
            },
            {
                "source_id": "gse335848_superseries",
                "source_numerical_status": "geo_accession_available",
                "usable_for_current_analysis": "public_accession_trace",
                "missing_for_upgrade": "Official GEO viewer for GSE335848 states that supplementary data files are not provided, so drug-combination source tables are not public.",
            },
            {
                "source_id": "biorxiv_preprint_v1",
                "source_numerical_status": "figure_only_for_drug_response",
                "usable_for_current_analysis": "rank_level_digitization",
                "missing_for_upgrade": "Underlying time-point replicate values for confluence, EdU, regrowth, and replication-origin polarity.",
            },
        ]
    )

    report = render_external_dynamic_corroboration(
        build_external_dynamic_corroboration_summary(preprint),
        source_audit,
    )

    assert "source ceiling snapshot" in report.lower()
    assert "corroboration_only_not_source_table_upgrade" in report
    assert "gse335848_superseries" in report
    assert "figure_only_for_drug_response" in report
    assert "replicate-level source numerical tables" in report


def test_write_external_dynamic_corroboration_package_rebuilds_outputs(tmp_path: Path) -> None:
    source_dir = ROOT / "sources/gse335846_dynamic_atm"
    summary_out = tmp_path / "evidence/gse335846_external_dynamic_corroboration.tsv"
    report_out = tmp_path / "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md"
    paths = write_external_dynamic_corroboration_package(
        source_dir=source_dir,
        preprint_path=ROOT / "sources/gse335846_dynamic_atm/preprint_733326.txt",
        summary_out=summary_out,
        report_out=report_out,
    )

    summary = pd.read_csv(summary_out, sep="\t")
    assert paths["summary"] == summary_out
    assert paths["report"] == report_out
    assert len(summary) == 4
    assert report_out.read_text(encoding="utf-8").startswith(
        "# GSE335846 External Dynamic Corroboration"
    )


def test_write_external_dynamic_corroboration_assets_builds_figure_and_support_text(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path
    paths = write_external_dynamic_corroboration_assets(
        source_dir=ROOT / "sources/gse335846_dynamic_atm",
        preprint_path=ROOT / "sources/gse335846_dynamic_atm/preprint_733326.txt",
        summary_out=output_dir / "evidence/gse335846_external_dynamic_corroboration.tsv",
        report_out=output_dir / "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md",
        timecourse_path=ROOT / "evidence/gse335846_dynamic_atm_timecourse.tsv",
        branch_scores_path=ROOT / "evidence/gse335846_rna_seq_branch_axis_scores.tsv",
        marker_summary_path=ROOT / "evidence/gse335846_rna_seq_branch_axis_source_summary.tsv",
        association_path=ROOT / "evidence/gse335846_dynamic_atm_association.tsv",
        figure_out=output_dir / "figures_png/gse335846_dynamic_corroboration_scorecard.png",
        figure_pdf_out=output_dir / "figures_png/gse335846_dynamic_corroboration_scorecard.pdf",
        support_text_out=output_dir / "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md",
    )

    assert paths["figure"].exists()
    assert paths["figure_pdf"].exists()
    assert paths["support_text"].exists()
    support_text = paths["support_text"].read_text(encoding="utf-8")
    assert "Supplementary Figure S5" in support_text
    assert "corroboration layer" in support_text
