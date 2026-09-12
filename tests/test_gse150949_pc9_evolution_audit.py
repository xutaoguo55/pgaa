from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pgaa.core.gse150949_pc9_evolution_audit import (
    build_gse150949_pc9_evolution_audit,
    write_gse150949_pc9_evolution_assets,
)


ROOT = Path(__file__).resolve().parents[1]


def test_gse150949_pc9_evolution_audit_supports_partial_third_system() -> None:
    package = build_gse150949_pc9_evolution_audit(
        state_modules_path=ROOT / "evidence/gse75602_resistance_state_modules.tsv",
        annotation_path=ROOT / "evidence/gse75602_resistance_down_module_ensembl_annotation.tsv",
        metadata_path=ROOT / "data/gse150949/GSE150949_metaData_with_lineage.txt.gz",
        matrix_path=ROOT / "data/gse150949/GSE150949_pc9_count_matrix.csv.gz",
    )

    coverage = package["coverage"]
    sample_summary = package["sample_summary"]
    group_summary = package["group_summary"]

    assert len(coverage) == 50
    assert int(coverage["present_in_matrix"].sum()) == 45
    assert set(package["missing_symbols"]) == {
        "LINC01819",
        "SLC60A1",
        "UBBP4",
        "CPP",
        "MAB21L4",
    }
    assert set(sample_summary["sample_type"]) == {
        "0",
        "3",
        "7",
        "14_high",
        "14_med",
        "14_low",
    }

    timepoint_rows = []
    for time_point, frame in group_summary.groupby("time_point", sort=True):
        weights = frame["n_cells"].astype(float).to_numpy()
        means = frame["mean_route_score"].astype(float).to_numpy()
        timepoint_rows.append(
            {
                "time_point": int(time_point),
                "n_cells": int(weights.sum()),
                "mean_route_score": float(np.average(means, weights=weights)),
            }
        )
    timepoint_summary = pd.DataFrame(timepoint_rows)
    day0 = timepoint_summary[timepoint_summary["time_point"].eq(0)].iloc[0]
    day3 = timepoint_summary[timepoint_summary["time_point"].eq(3)].iloc[0]
    day7 = timepoint_summary[timepoint_summary["time_point"].eq(7)].iloc[0]
    day14 = timepoint_summary[timepoint_summary["time_point"].eq(14)].iloc[0]
    day14_high = group_summary[group_summary["sample_type"].eq("14_high")].iloc[0]
    day14_med = group_summary[group_summary["sample_type"].eq("14_med")].iloc[0]
    day14_low = group_summary[group_summary["sample_type"].eq("14_low")].iloc[0]

    assert float(day0["mean_route_score"]) == pytest.approx(0.122830, abs=1e-6)
    assert float(day3["mean_route_score"]) == pytest.approx(-0.038804, abs=1e-6)
    assert float(day7["mean_route_score"]) == pytest.approx(0.072553, abs=1e-6)
    assert float(day14["mean_route_score"]) == pytest.approx(-0.032463, abs=1e-6)
    assert float(day14_high["mean_route_score"]) == pytest.approx(-0.013755, abs=1e-6)
    assert float(day14_med["mean_route_score"]) == pytest.approx(-0.032302, abs=1e-6)
    assert float(day14_low["mean_route_score"]) == pytest.approx(-0.062288, abs=1e-6)
    assert float(day14_low["mean_route_score"]) < float(day0["mean_route_score"])
    assert float(day14_high["mean_route_score"]) < float(day0["mean_route_score"])
    assert float(day14_med["mean_route_score"]) < float(day0["mean_route_score"])


def test_write_gse150949_pc9_evolution_assets_builds_outputs(tmp_path: Path) -> None:
    paths = write_gse150949_pc9_evolution_assets(
        state_modules_path=ROOT / "evidence/gse75602_resistance_state_modules.tsv",
        annotation_path=ROOT / "evidence/gse75602_resistance_down_module_ensembl_annotation.tsv",
        metadata_path=ROOT / "data/gse150949/GSE150949_metaData_with_lineage.txt.gz",
        matrix_path=ROOT / "data/gse150949/GSE150949_pc9_count_matrix.csv.gz",
        figure_out=tmp_path / "figures_png/gse150949_pc9_evolution_scorecard.png",
        figure_pdf_out=tmp_path / "figures_png/gse150949_pc9_evolution_scorecard.pdf",
        audit_out=tmp_path / "docs/GSE150949_PC9_EVOLUTION_AUDIT.md",
        support_text_out=tmp_path / "docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md",
        coverage_out=tmp_path / "evidence/gse150949_pc9_module_coverage.tsv",
        route_scores_out=tmp_path / "evidence/gse150949_pc9_route_scores.tsv",
        sample_summary_out=tmp_path / "evidence/gse150949_pc9_sample_summary.tsv",
        group_summary_out=tmp_path / "evidence/gse150949_pc9_group_summary.tsv",
    )

    assert paths["figure"].exists()
    assert paths["figure_pdf"].exists()
    assert paths["audit"].exists()
    assert paths["support_text"].exists()
    assert paths["coverage"].exists()
    assert paths["route_scores"].exists()
    assert paths["sample_summary"].exists()
    assert paths["group_summary"].exists()

    audit_text = paths["audit"].read_text(encoding="utf-8")
    support_text = paths["support_text"].read_text(encoding="utf-8")
    assert "# GSE150949 PC9 Evolution Audit" in audit_text
    assert "45 of the 50 genes" in audit_text
    assert "Supplementary Figure S6" in support_text
    assert "claim ceiling" in support_text
