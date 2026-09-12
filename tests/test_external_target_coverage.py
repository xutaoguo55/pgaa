import pandas as pd
import pytest

from pgaa.core.external_target_coverage import (
    build_external_target_coverage,
    render_external_target_coverage_report,
    summarize_external_target_coverage,
)


def _candidate_audit() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "target_gene": "BHLHE40",
                "unit_id": "adamson::BHLHE40_pDS258",
                "validation_priority": "tier1_replication_candidate",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "same_context_class": "same_context_candidate_metadata_required",
            },
            {
                "target_gene": "CREB1",
                "unit_id": "adamson::CREB1_pDS269",
                "validation_priority": "tier1_replication_candidate",
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "same_context_class": "same_context_candidate_metadata_required",
            },
        ]
    )


def _obs() -> pd.DataFrame:
    return pd.DataFrame(
        {"core_control": [False, False, True, False]},
        index=[
            "830_BHLHE40_P1P2_ENSG00000134107",
            "1857_CREB1_P1P2_ENSG00000118260",
            "10747_non-targeting_non-targeting_non-targeting",
            "10748_non-targeting_non-targeting_non-targeting",
        ],
    )


def test_external_target_coverage_verifies_targets_and_controls():
    coverage = build_external_target_coverage(
        _candidate_audit(),
        _obs(),
        "replogle_2022_k562_gwps",
        "K562_gwps_raw_bulk_01.h5ad",
        "https://example.org/file",
    )

    assert set(coverage["target_coverage_status"]) == {"verified_present"}
    assert set(coverage["matched_control_status"]) == {"verified_controls_present"}
    assert set(coverage["external_import_status"]) == {
        "target_verified_pseudobulk_singlecell_required"
    }
    assert "not_replication" in coverage.iloc[0]["claim_use"]


def test_external_target_coverage_report_is_claim_safe():
    coverage = build_external_target_coverage(
        _candidate_audit(),
        _obs(),
        "replogle_2022_k562_gwps",
        "K562_gwps_raw_bulk_01.h5ad",
        "https://example.org/file",
    )
    summary = summarize_external_target_coverage(coverage)
    report = render_external_target_coverage_report(coverage, summary)

    assert int(summary["n_targets"].sum()) == 2
    assert "not replication evidence" in report
    assert "external PGAA/comparator rerun" in report
    assert "matching single-cell matrix" in report


def test_external_target_coverage_marks_missing_target_unusable():
    audit = _candidate_audit()
    audit.loc[0, "target_gene"] = "MISSING"
    coverage = build_external_target_coverage(
        audit,
        _obs(),
        "replogle_2022_k562_gwps",
        "K562_gwps_raw_bulk_01.h5ad",
        "https://example.org/file",
    )

    missing = coverage[coverage["target_gene"] == "MISSING"].iloc[0]
    assert missing["target_coverage_status"] == "not_found_in_obs_metadata"
    assert missing["external_import_status"] == "not_import_ready_for_this_target"


def test_external_target_coverage_requires_candidate_schema():
    with pytest.raises(ValueError, match="candidate audit table is missing columns"):
        build_external_target_coverage(
            _candidate_audit().drop(columns=["unit_id"]),
            _obs(),
            "replogle_2022_k562_gwps",
            "K562_gwps_raw_bulk_01.h5ad",
            "https://example.org/file",
        )
