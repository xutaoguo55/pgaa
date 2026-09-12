from __future__ import annotations

import pandas as pd

from pgaa.core.gse75602_resistance_module_biology import (
    build_module_biology_summary,
    render_module_biology_audit,
    write_module_biology_audit_package,
)


def _build_annotation_frame() -> pd.DataFrame:
    genes = [
        "CP",
        "SLC40A1",
        "HFE",
        "TFRC",
        "STEAP4",
        "CA9",
        "CA12",
        "CA2",
        "CYP24A1",
        "RARRES1",
        "STC1",
        "PSCA",
        "HOPX",
        "ELF5",
        "MUC6",
        "KRT4",
        "KRT13",
        "BCAS1",
        "SERPINE1",
        "LRG1",
        "CYP26A1",
    ]
    return pd.DataFrame(
        {
            "gene_id": [f"ENSG{i:011d}" for i in range(len(genes))],
            "display_name": genes,
            "description": [f"{gene} description" for gene in genes],
            "source": ["synthetic"] * len(genes),
        }
    )


def _build_pathway_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source": ["REAC", "REAC", "WP"],
            "native": [
                "REAC:R-HSA-917937",
                "REAC:R-HSA-1475029",
                "WP:WP2877",
            ],
            "name": [
                "Iron uptake and transport",
                "Reversible hydration of carbon dioxide",
                "Vitamin D receptor pathway",
            ],
            "p_value": [0.020301154645609238, 0.009343358237921259, 0.031766334054338964],
            "term_size": [51, 7, 134],
            "query_size": [50, 50, 50],
            "intersection_size": [3, 2, 4],
            "effective_domain_size": [15922, 15922, 15922],
            "intersection": ["", "", ""],
        }
    )


def test_module_biology_summary_uses_evidence_tables() -> None:
    summary = build_module_biology_summary(_build_annotation_frame(), _build_pathway_frame())

    assert list(summary["theme"]) == [
        "iron_handling",
        "carbonic_anhydrase_and_pH",
        "vdr_axis",
        "epithelial_stress_state",
        "redox_or_metabolic_state",
    ]
    assert summary.set_index("theme").loc["iron_handling", "p_value"] == "0.020301"
    assert summary.set_index("theme").loc["carbonic_anhydrase_and_pH", "p_value"] == "0.009343"
    assert summary.set_index("theme").loc["vdr_axis", "p_value"] == "0.031766"
    assert summary.set_index("theme").loc["epithelial_stress_state", "p_value"] == "n/a"


def test_module_biology_report_includes_transferable_program_language() -> None:
    summary = build_module_biology_summary(_build_annotation_frame(), _build_pathway_frame())
    report = render_module_biology_audit(summary, _build_pathway_frame())

    assert "transferable resistance-state program" in report
    assert "Iron uptake and transport" in report
    assert "Vitamin D receptor pathway" in report
    assert "shared_resistance_down_module" in report


def test_write_module_biology_audit_package_rebuilds_outputs(tmp_path) -> None:
    annotation_path = tmp_path / "annotation.tsv"
    pathway_path = tmp_path / "pathway.tsv"
    summary_out = tmp_path / "summary.tsv"
    report_out = tmp_path / "report.md"
    _build_annotation_frame().to_csv(annotation_path, sep="\t", index=False)
    _build_pathway_frame().to_csv(pathway_path, sep="\t", index=False)

    paths = write_module_biology_audit_package(
        annotation_path=annotation_path,
        pathway_enrichment_path=pathway_path,
        summary_out=summary_out,
        report_out=report_out,
    )

    assert paths["summary"] == summary_out
    assert paths["report"] == report_out
    rebuilt = pd.read_csv(summary_out, sep="\t")
    assert not rebuilt.empty
    assert "iron_handling" in set(rebuilt["theme"])
    assert report_out.read_text(encoding="utf-8").startswith("# GSE75602 Resistance Module Biology Audit")
