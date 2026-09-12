from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.gse335846_phosphoproteomics_corroboration import (
    build_phosphoproteomics_corroboration,
    write_phosphoproteomics_corroboration_assets,
)


ROOT = Path(__file__).resolve().parents[1]


def test_phosphoproteomics_corroboration_summary_and_boundary_scan() -> None:
    workbook = ROOT / "sources/gse335846_dynamic_atm/source_ev1.xlsx"
    data = build_phosphoproteomics_corroboration(workbook)

    selected = data["selected_markers"]
    boundary = data["boundary_scan"]
    counts = data["counts"]

    assert counts["quantified_proteins"] == "1,006"
    assert counts["unique_phosphosites"] == "3,142"
    assert list(selected["panel"].unique()) == ["protein", "phosphosite"]
    assert len(selected) == 19
    assert selected.loc[selected["gene_symbol"].eq("CDK1"), "DTP_minus_DMSO"].iloc[0] < 0
    assert selected.loc[selected["gene_symbol"].eq("EGFR"), "DTP_minus_DMSO"].iloc[0] > 0
    assert boundary.loc[boundary["gene_symbol"].eq("ATM"), "protein_exact_hits"].iloc[0] == 0
    assert boundary.loc[boundary["gene_symbol"].eq("ATM"), "phosphosite_exact_hits"].iloc[0] == 0
    assert boundary.loc[boundary["gene_symbol"].eq("ATR"), "phosphosite_exact_hits"].iloc[0] > 0


def test_write_phosphoproteomics_corroboration_assets_rebuilds_outputs(tmp_path: Path) -> None:
    paths = write_phosphoproteomics_corroboration_assets(
        source_dir=ROOT / "sources/gse335846_dynamic_atm",
        workbook_path=ROOT / "sources/gse335846_dynamic_atm/source_ev1.xlsx",
        summary_out=tmp_path / "evidence/gse335846_phosphoproteomics_corroboration.tsv",
        report_out=tmp_path / "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md",
        selected_out=tmp_path / "evidence/gse335846_phosphoproteomics_selected_markers.tsv",
        boundary_out=tmp_path / "evidence/gse335846_phosphoproteomics_boundary_scan.tsv",
        figure_out=tmp_path / "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png",
        figure_pdf_out=tmp_path / "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf",
        support_text_out=tmp_path / "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md",
    )

    assert paths["figure"].exists()
    assert paths["figure_pdf"].exists()
    assert paths["support_text"].exists()
    assert paths["report"].exists()
    assert paths["summary"].exists()
    assert paths["boundary_scan"].exists()
    assert paths["selected_markers"].exists()
    selected = pd.read_csv(paths["selected_markers"], sep="\t")
    boundary = pd.read_csv(paths["boundary_scan"], sep="\t")
    support_text = paths["support_text"].read_text(encoding="utf-8")
    report = paths["report"].read_text(encoding="utf-8")
    assert len(selected) == 19
    assert "Supplementary Figure S7" in support_text
    assert "ATM exact scan" in support_text
    assert "phosphoproteomics corroboration" in report.lower()
    assert boundary.loc[boundary["gene_symbol"].eq("ATM"), "protein_exact_hits"].iloc[0] == 0

