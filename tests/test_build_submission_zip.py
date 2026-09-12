from __future__ import annotations

import zipfile
from pathlib import Path

import scripts.build_submission_zip as build_submission_zip


def test_build_submission_zip_includes_source_ceiling_traces(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "PGAA_supplementary_code.zip"
    monkeypatch.setattr(build_submission_zip, "OUT", out)

    zpath = build_submission_zip.build()
    n_entries, total_size = build_submission_zip.validate(zpath)

    assert zpath == out
    assert n_entries > 0
    assert total_size > 0

    with zipfile.ZipFile(zpath) as zf:
        names = set(zf.namelist())

    assert "pgaa_supplementary/evidence/gse335846_source_data_numeric_audit.tsv" in names
    assert "pgaa_supplementary/evidence/gse335846_external_dynamic_corroboration.tsv" in names
    assert "pgaa_supplementary/docs/SUBMISSION_PACKAGE_INDEX.md" in names
    assert (
        "pgaa_supplementary/docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md"
        in names
    )
    assert (
        "pgaa_supplementary/figures_png/gse335846_dynamic_corroboration_scorecard.png"
        in names
    )
    assert (
        "pgaa_supplementary/figures_png/gse335846_dynamic_corroboration_scorecard.pdf"
        in names
    )
