import pandas as pd
import pytest

from pgaa.core.external_pgaa_execution_manifest import (
    build_external_pgaa_execution_manifest,
    render_external_pgaa_execution_manifest_report,
    summarize_external_pgaa_execution_manifest,
)


def _contract(tmp_path, status="ready_for_pgaa_input_extraction") -> pd.DataFrame:
    prefix = tmp_path / "BHLHE40" / "BHLHE40"
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_gene": "BHLHE40",
                "contract_status": status,
                "pgaa_s1_out": str(prefix.with_suffix(".s1.csv")),
                "pgaa_s2_out": str(prefix.with_suffix(".s2.csv")),
                "external_claim_state_out": str(tmp_path / "BHLHE40" / "external_claim_state.tsv"),
                "pgaa_command": f"python3 -m pgaa.cli --target BHLHE40 --out-prefix {prefix}",
            }
        ]
    )


def _extraction(tmp_path, status="extracted_pgaa_cli_inputs") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_gene": "BHLHE40",
                "extraction_status": status,
                "expression_csv": str(tmp_path / "BHLHE40" / "expression.csv"),
                "metadata_csv": str(tmp_path / "BHLHE40" / "metadata.csv"),
                "n_perturbed_cells": 12,
                "n_control_cells": 10,
                "n_genes": 3,
            }
        ]
    )


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x\n", encoding="utf-8")


def test_external_pgaa_execution_manifest_blocks_by_contract(tmp_path):
    manifest = build_external_pgaa_execution_manifest(
        _contract(tmp_path, status="blocked_by_readiness_gate"),
        _extraction(tmp_path, status="blocked_by_contract_status"),
    )

    row = manifest.iloc[0]
    assert row["execution_status"] == "blocked_by_contract_status"
    assert row["pgaa_command"] == ""
    assert row["claim_use"] == "execution_manifest_not_replication"


def test_external_pgaa_execution_manifest_ready_when_inputs_exist(tmp_path):
    extraction = _extraction(tmp_path)
    _touch(tmp_path / "BHLHE40" / "expression.csv")
    _touch(tmp_path / "BHLHE40" / "metadata.csv")

    manifest = build_external_pgaa_execution_manifest(_contract(tmp_path), extraction)

    row = manifest.iloc[0]
    assert row["execution_status"] == "ready_for_pgaa_cli_execution"
    assert bool(row["has_expression_csv"]) is True
    assert bool(row["has_metadata_csv"]) is True
    assert "python3 -m pgaa.cli" in row["pgaa_command"]


def test_external_pgaa_execution_manifest_detects_pgaa_outputs(tmp_path):
    extraction = _extraction(tmp_path)
    _touch(tmp_path / "BHLHE40" / "expression.csv")
    _touch(tmp_path / "BHLHE40" / "metadata.csv")
    _touch(tmp_path / "BHLHE40" / "BHLHE40.s1.csv")
    _touch(tmp_path / "BHLHE40" / "BHLHE40.s2.csv")

    manifest = build_external_pgaa_execution_manifest(_contract(tmp_path), extraction)

    assert manifest.iloc[0]["execution_status"] == "pgaa_outputs_present_waiting_claim_state_compilation"
    assert bool(manifest.iloc[0]["has_pgaa_s1_out"]) is True
    assert bool(manifest.iloc[0]["has_pgaa_s2_out"]) is True


def test_external_pgaa_execution_manifest_detects_claim_state(tmp_path):
    extraction = _extraction(tmp_path)
    _touch(tmp_path / "BHLHE40" / "expression.csv")
    _touch(tmp_path / "BHLHE40" / "metadata.csv")
    _touch(tmp_path / "BHLHE40" / "BHLHE40.s1.csv")
    _touch(tmp_path / "BHLHE40" / "BHLHE40.s2.csv")
    _touch(tmp_path / "BHLHE40" / "external_claim_state.tsv")

    manifest = build_external_pgaa_execution_manifest(_contract(tmp_path), extraction)
    summary = summarize_external_pgaa_execution_manifest(manifest)
    report = render_external_pgaa_execution_manifest_report(manifest, summary)

    assert manifest.iloc[0]["execution_status"] == "external_claim_state_present"
    assert int(summary["n_targets"].sum()) == 1
    assert "not replication evidence" in report
    assert "Ready PGAA Commands" not in report


def test_external_pgaa_execution_manifest_requires_columns(tmp_path):
    with pytest.raises(ValueError, match="contract table is missing columns"):
        build_external_pgaa_execution_manifest(pd.DataFrame(), _extraction(tmp_path))
