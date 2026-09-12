import numpy as np
import pandas as pd
import pytest

ad = pytest.importorskip("anndata")

from pgaa.core.external_rerun_readiness import (
    build_external_rerun_readiness,
    render_external_rerun_readiness_report,
    summarize_external_rerun_readiness,
)


def _coverage() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "target_gene": "BHLHE40",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "validation_priority": "tier1",
                "target_coverage_status": "verified_present",
                "matched_control_status": "verified_controls_present",
            },
            {
                "target_gene": "CREB1",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "validation_priority": "tier1_replication_candidate",
                "target_coverage_status": "verified_present",
                "matched_control_status": "verified_controls_present",
            },
            {
                "target_gene": "SPI1",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "validation_priority": "tier2_dependency_stress_test",
                "target_coverage_status": "verified_present",
                "matched_control_status": "verified_controls_present",
            },
        ]
    )


def _import_plan() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "file_name": "K562_gwps_raw_singlecell_01.h5ad",
                "matrix_level": "single_cell_h5ad",
                "preferred_for_pgaa": "true",
                "singlecell_import_status": "download_not_recommended_margin_too_low",
                "target_control_gate": "passed",
            }
        ]
    )


def _write_h5ad(path, perturbations: list[str]) -> None:
    obs = pd.DataFrame(
        {"perturbation": perturbations},
        index=[f"cell_{i}" for i in range(len(perturbations))],
    )
    var = pd.DataFrame(index=["GATA1", "MYC", "STAT1"])
    ad.AnnData(np.ones((len(perturbations), 3)), obs=obs, var=var).write_h5ad(path)


def test_external_rerun_readiness_blocks_missing_h5ad(tmp_path):
    readiness = build_external_rerun_readiness(
        _import_plan(), _coverage(), tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    )

    row = readiness.iloc[0]
    assert row["singlecell_gate_status"] == "blocked_waiting_for_singlecell_h5ad"
    assert row["claim_use"] == "rerun_readiness_not_replication"
    assert row["targets_missing"] == "BHLHE40;CREB1"
    assert row["required_targets"] == "BHLHE40;CREB1"


def test_external_rerun_readiness_accepts_valid_singlecell_metadata(tmp_path):
    h5ad = tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    _write_h5ad(h5ad, ["BHLHE40", "CREB1", "non-targeting", "BHLHE40"])

    readiness = build_external_rerun_readiness(_import_plan(), _coverage(), h5ad)
    row = readiness.iloc[0]

    assert row["singlecell_gate_status"] == "ready_for_external_claim_state_rerun"
    assert row["targets_found"] == "BHLHE40;CREB1"
    assert row["n_control_rows"] == 1
    assert "perturbation" in row["label_columns_checked"]


def test_external_rerun_readiness_rejects_bulk_named_h5ad(tmp_path):
    h5ad = tmp_path / "K562_gwps_raw_bulk_01.h5ad"
    _write_h5ad(h5ad, ["BHLHE40", "CREB1", "non-targeting"])

    readiness = build_external_rerun_readiness(_import_plan(), _coverage(), h5ad)

    assert readiness.iloc[0]["singlecell_gate_status"] == "not_singlecell_matrix"


def test_external_rerun_readiness_report_is_claim_safe(tmp_path):
    readiness = build_external_rerun_readiness(
        _import_plan(), _coverage(), tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    )
    summary = summarize_external_rerun_readiness(readiness)
    report = render_external_rerun_readiness_report(readiness, summary)

    assert int(summary["n_rows"].sum()) == 1
    assert "not replication evidence" in report
    assert "ready_for_external_claim_state_rerun" in report
