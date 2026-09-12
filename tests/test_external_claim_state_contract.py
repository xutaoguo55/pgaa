import pandas as pd
import pytest

from pgaa.core.external_claim_state_contract import (
    build_external_claim_state_contract,
    render_external_claim_state_contract_report,
    summarize_external_claim_state_contract,
)


def _readiness(status: str = "blocked_waiting_for_singlecell_h5ad") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "singlecell_h5ad": "/tmp/K562_gwps_raw_singlecell_01.h5ad",
                "target_control_gate": "passed",
                "required_targets": "BHLHE40;CREB1",
                "singlecell_gate_status": status,
                "claim_use": "rerun_readiness_not_replication",
            }
        ]
    )


def test_external_claim_state_contract_blocks_when_readiness_not_ready(tmp_path):
    contract = build_external_claim_state_contract(_readiness(), tmp_path / "external")

    assert set(contract["target_gene"]) == {"BHLHE40", "CREB1"}
    assert set(contract["contract_status"]) == {"blocked_by_readiness_gate"}
    assert set(contract["pgaa_command"]) == {""}
    assert set(contract["claim_use"]) == {"execution_contract_not_replication"}


def test_external_claim_state_contract_emits_pgaa_commands_when_ready(tmp_path):
    contract = build_external_claim_state_contract(
        _readiness("ready_for_external_claim_state_rerun"),
        tmp_path / "external",
        n_perms=50,
        n_bins=10,
    )

    row = contract.set_index("target_gene").loc["BHLHE40"]
    assert row["contract_status"] == "ready_for_pgaa_input_extraction"
    assert "python3 -m pgaa.cli" in row["pgaa_command"]
    assert "--target BHLHE40" in row["pgaa_command"]
    assert "--n-perms 50" in row["pgaa_command"]
    assert "--target-only-permutation-p" in row["pgaa_command"]
    assert row["pgaa_s1_out"].endswith("BHLHE40.s1.csv")
    assert row["external_claim_state_out"].endswith("external_claim_state.tsv")


def test_external_claim_state_contract_report_is_claim_safe(tmp_path):
    contract = build_external_claim_state_contract(_readiness(), tmp_path / "external")
    summary = summarize_external_claim_state_contract(contract)
    report = render_external_claim_state_contract_report(contract, summary)

    assert int(summary["n_targets"].sum()) == 2
    assert "not replication evidence" in report
    assert "does not authorize a manuscript replication claim" in report


def test_external_claim_state_contract_requires_readiness_schema(tmp_path):
    with pytest.raises(ValueError, match="readiness table is missing columns"):
        build_external_claim_state_contract(
            _readiness().drop(columns=["singlecell_gate_status"]), tmp_path
        )
