import pandas as pd
import pytest

from pgaa.core.external_claim_state_compiler import (
    compile_external_claim_states,
    render_external_claim_state_report,
    summarize_external_claim_states,
)


def _manifest(tmp_path, target="BHLHE40", status="pgaa_outputs_present_waiting_claim_state_compilation"):
    prefix = tmp_path / target / target
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_gene": target,
                "execution_status": status,
                "pgaa_s1_out": str(prefix.with_suffix(".s1.csv")),
                "pgaa_s2_out": str(prefix.with_suffix(".s2.csv")),
                "external_claim_state_out": str(tmp_path / target / "external_claim_state.tsv"),
            }
        ]
    )


def _units(target="BHLHE40") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": f"adamson_decision_benchmark::{target}_pDS258",
                "evidence_type": "adamson_decision_benchmark",
                "context": f"{target}_pDS258",
                "decision_state": "supported_responder_state",
                "primary_method": "PGAA-H histogram-shape",
                "supporting_methods": "PGAA-H histogram-shape;PGAA-W Wasserstein",
            }
        ]
    )


def _write_outputs(tmp_path, target="BHLHE40", target_rank=1):
    out_dir = tmp_path / target
    out_dir.mkdir(parents=True, exist_ok=True)
    genes = ["G1", "G2", "G3", "G4"]
    genes.insert(target_rank - 1, target)
    pd.DataFrame(
        {
            "gene": genes,
            "W_std_observed": list(reversed(range(1, len(genes) + 1))),
            "p_value_perm": [0.20] * len(genes),
        }
    ).to_csv(out_dir / f"{target}.s1.csv", index=False)
    pd.DataFrame(
        {
            "gene": genes,
            "S2": list(reversed(range(1, len(genes) + 1))),
        }
    ).to_csv(out_dir / f"{target}.s2.csv", index=False)


def test_external_claim_state_compiler_blocks_without_outputs(tmp_path):
    manifest = _manifest(tmp_path, status="blocked_by_contract_status")

    claim_states = compile_external_claim_states(manifest, _units(), write_files=True)

    row = claim_states.iloc[0]
    assert row["external_claim_state"] == "blocked_by_external_execution_status"
    assert row["concordance_state"] == "not_assessable"
    assert not (tmp_path / "BHLHE40" / "external_claim_state.tsv").exists()


def test_external_claim_state_compiler_compiles_concordant_support(tmp_path):
    _write_outputs(tmp_path, target_rank=1)

    claim_states = compile_external_claim_states(_manifest(tmp_path), _units(), top_n=2)

    row = claim_states.iloc[0]
    assert row["external_claim_state"] == "external_pgaa_w_h_support_observed"
    assert row["concordance_state"] == "external_concordant_with_internal_supported_unit"
    assert row["pgaa_w_rank"] == 1
    assert row["pgaa_h_rank"] == 1
    assert (tmp_path / "BHLHE40" / "external_claim_state.tsv").exists()


def test_external_claim_state_compiler_detects_external_support_not_observed(tmp_path):
    _write_outputs(tmp_path, target_rank=5)

    claim_states = compile_external_claim_states(_manifest(tmp_path), _units(), top_n=2)

    assert claim_states.iloc[0]["external_claim_state"] == "external_support_not_observed"
    assert (
        claim_states.iloc[0]["concordance_state"]
        == "external_discordant_with_internal_supported_unit"
    )


def test_external_claim_state_compiler_blocks_missing_internal_unit(tmp_path):
    _write_outputs(tmp_path)

    claim_states = compile_external_claim_states(_manifest(tmp_path), _units("CREB1"), top_n=2)

    assert claim_states.iloc[0]["external_claim_state"] == "blocked_missing_internal_unit"
    assert claim_states.iloc[0]["internal_unit_id"] == ""


def test_external_claim_state_compiler_report_is_claim_safe(tmp_path):
    manifest = _manifest(tmp_path, status="blocked_by_contract_status")
    claim_states = compile_external_claim_states(manifest, _units())
    summary = summarize_external_claim_states(claim_states)
    report = render_external_claim_state_report(claim_states, summary)

    assert int(summary["n_targets"].sum()) == 1
    assert "not wet-lab validation" in report
    assert "T-cell functional validation" in report


def test_external_claim_state_compiler_requires_columns(tmp_path):
    with pytest.raises(ValueError, match="execution manifest is missing columns"):
        compile_external_claim_states(pd.DataFrame(), _units())
