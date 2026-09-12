import pandas as pd
import pytest

from pgaa.core import external_singlecell_import_plan as plan_mod
from pgaa.core.external_singlecell_import_plan import (
    build_external_singlecell_import_plan,
    render_external_singlecell_import_plan_report,
    summarize_external_singlecell_import_plan,
)


def _coverage() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "target_gene": "BHLHE40",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_coverage_status": "verified_present",
                "matched_control_status": "verified_controls_present",
                "external_import_status": "target_verified_pseudobulk_singlecell_required",
            }
        ]
    )


def _files() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "file_role": "raw_singlecell",
                "file_name": "K562_gwps_raw_singlecell_01.h5ad",
                "download_url": "https://example.org/raw.h5ad",
                "size_bytes": 100,
                "matrix_level": "single_cell_h5ad",
                "preferred_for_pgaa": "true",
            },
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "file_role": "raw_pseudobulk",
                "file_name": "K562_gwps_raw_bulk_01.h5ad",
                "download_url": "https://example.org/bulk.h5ad",
                "size_bytes": 10,
                "matrix_level": "pseudobulk_h5ad",
                "preferred_for_pgaa": "false",
            },
        ]
    )


class _Usage:
    def __init__(self, free: int):
        self.total = 1000
        self.used = 1000 - free
        self.free = free


def test_singlecell_import_plan_blocks_low_margin(monkeypatch, tmp_path):
    monkeypatch.setattr(plan_mod.shutil, "disk_usage", lambda _: _Usage(free=110))
    plan = build_external_singlecell_import_plan(
        _coverage(), _files(), tmp_path, safety_multiplier=1.25
    )
    raw = plan[plan["file_role"] == "raw_singlecell"].iloc[0]

    assert raw["singlecell_import_status"] == "download_not_recommended_margin_too_low"
    assert raw["target_control_gate"] == "passed"
    assert raw["claim_use"] == "import_planning_not_replication"


def test_singlecell_import_plan_allows_sufficient_scratch(monkeypatch, tmp_path):
    monkeypatch.setattr(plan_mod.shutil, "disk_usage", lambda _: _Usage(free=200))
    plan = build_external_singlecell_import_plan(
        _coverage(), _files(), tmp_path, safety_multiplier=1.25
    )
    raw = plan[plan["file_role"] == "raw_singlecell"].iloc[0]

    assert raw["singlecell_import_status"] == "download_allowed_with_scratch_margin"


def test_singlecell_import_plan_report_is_claim_safe(monkeypatch, tmp_path):
    monkeypatch.setattr(plan_mod.shutil, "disk_usage", lambda _: _Usage(free=110))
    plan = build_external_singlecell_import_plan(
        _coverage(), _files(), tmp_path, safety_multiplier=1.25
    )
    summary = summarize_external_singlecell_import_plan(plan)
    report = render_external_singlecell_import_plan_report(plan, summary)

    assert int(summary["n_files"].sum()) == 2
    assert "not replication evidence" in report
    assert "Do not download large h5ad files into the repository" in report


def test_singlecell_import_plan_requires_manifest_schema(tmp_path):
    with pytest.raises(ValueError, match="file manifest is missing columns"):
        build_external_singlecell_import_plan(
            _coverage(), _files().drop(columns=["download_url"]), tmp_path
        )
