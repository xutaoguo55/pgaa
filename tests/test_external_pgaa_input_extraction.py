import numpy as np
import pandas as pd
import pytest

ad = pytest.importorskip("anndata")

from pgaa.cli import _read_expression, _read_metadata
from pgaa.core.external_pgaa_input_extraction import (
    extract_external_pgaa_inputs,
    render_external_pgaa_input_extraction_report,
    summarize_external_pgaa_input_extraction,
)


def _contract(tmp_path, status: str = "ready_for_pgaa_input_extraction") -> pd.DataFrame:
    h5ad = tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_gene": "BHLHE40",
                "singlecell_h5ad": str(h5ad),
                "contract_status": status,
                "expression_csv": str(tmp_path / "BHLHE40" / "expression.csv"),
                "metadata_csv": str(tmp_path / "BHLHE40" / "metadata.csv"),
            },
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "target_gene": "CREB1",
                "singlecell_h5ad": str(h5ad),
                "contract_status": status,
                "expression_csv": str(tmp_path / "CREB1" / "expression.csv"),
                "metadata_csv": str(tmp_path / "CREB1" / "metadata.csv"),
            },
        ]
    )


def _write_h5ad(path) -> None:
    obs = pd.DataFrame(
        {"perturbation": ["BHLHE40", "BHLHE40", "CREB1", "non-targeting", "non-targeting"]},
        index=[f"cell_{i}" for i in range(5)],
    )
    var = pd.DataFrame(index=["BHLHE40", "CREB1", "STAT1"])
    X = np.arange(15, dtype=float).reshape(5, 3)
    ad.AnnData(X, obs=obs, var=var).write_h5ad(path)


def _write_h5ad_with_gene_symbols(path) -> None:
    obs = pd.DataFrame(
        {"perturbation": ["BHLHE40", "BHLHE40", "non-targeting", "non-targeting"]},
        index=[f"cell_symbol_{i}" for i in range(4)],
    )
    var = pd.DataFrame(
        {"gene_name": ["BHLHE40", "CREB1", "TBCE", "TBCE"]},
        index=["ENSG_BHLHE40", "ENSG_CREB1", "ENSG_TBCE_1", "ENSG_TBCE_2"],
    )
    X = np.arange(16, dtype=float).reshape(4, 4)
    ad.AnnData(X, obs=obs, var=var).write_h5ad(path)


def test_external_pgaa_input_extraction_blocks_without_ready_contract(tmp_path):
    contract = _contract(tmp_path, status="blocked_by_readiness_gate")
    extraction = extract_external_pgaa_inputs(contract)

    assert set(extraction["extraction_status"]) == {"blocked_by_contract_status"}
    assert not (tmp_path / "BHLHE40" / "expression.csv").exists()
    assert set(extraction["claim_use"]) == {"input_extraction_not_replication"}


def test_external_pgaa_input_extraction_writes_cli_inputs(tmp_path):
    contract = _contract(tmp_path)
    _write_h5ad(tmp_path / "K562_gwps_raw_singlecell_01.h5ad")

    extraction = extract_external_pgaa_inputs(contract, label_column="perturbation")
    row = extraction.set_index("target_gene").loc["BHLHE40"]

    assert row["extraction_status"] == "extracted_pgaa_cli_inputs"
    assert row["n_perturbed_cells"] == 2
    assert row["n_control_cells"] == 2
    assert row["n_genes"] == 3

    X, genes, cells = _read_expression(tmp_path / "BHLHE40" / "expression.csv")
    meta = _read_metadata(
        tmp_path / "BHLHE40" / "metadata.csv",
        cells,
        group_column="group",
        cell_type_column=None,
        library_size_column=None,
    )
    assert X.shape == (4, 3)
    assert genes == ["BHLHE40", "CREB1", "STAT1"]
    assert set(meta["group"]) == {"perturbed", "control"}


def test_external_pgaa_input_extraction_reuses_existing_cli_inputs(tmp_path, monkeypatch):
    contract = _contract(tmp_path).iloc[[0]].copy()
    _write_h5ad(tmp_path / "K562_gwps_raw_singlecell_01.h5ad")
    output_dir = tmp_path / "BHLHE40"
    output_dir.mkdir()
    pd.DataFrame({"BHLHE40": [1.0]}, index=["cell_0"]).to_csv(
        output_dir / "expression.csv"
    )
    pd.DataFrame({"cell_id": ["cell_0"], "group": ["perturbed"]}).to_csv(
        output_dir / "metadata.csv", index=False
    )

    monkeypatch.setattr(
        "pgaa.core.external_pgaa_input_extraction._matrix_to_dense_frame",
        lambda *args, **kwargs: pytest.fail("existing inputs should be reused"),
    )
    extraction = extract_external_pgaa_inputs(contract, label_column="perturbation")

    assert extraction.iloc[0]["extraction_status"] == "extracted_pgaa_cli_inputs"
    assert "audit" in extraction.iloc[0]["next_action"]


def test_external_pgaa_input_extraction_uses_gene_name_symbols(tmp_path):
    contract = _contract(tmp_path).iloc[[0]].copy()
    _write_h5ad_with_gene_symbols(tmp_path / "K562_gwps_raw_singlecell_01.h5ad")

    extraction = extract_external_pgaa_inputs(contract, label_column="perturbation")

    assert extraction.iloc[0]["extraction_status"] == "extracted_pgaa_cli_inputs"
    X, genes, _ = _read_expression(tmp_path / "BHLHE40" / "expression.csv")
    assert X.shape == (4, 4)
    assert "BHLHE40" in genes
    assert "CREB1" in genes
    assert "TBCE|ENSG_TBCE_1" in genes
    assert "TBCE|ENSG_TBCE_2" in genes


def test_external_pgaa_input_extraction_blocks_missing_target_gene(tmp_path):
    contract = _contract(tmp_path)
    contract.loc[0, "target_gene"] = "MISSING"
    _write_h5ad(tmp_path / "K562_gwps_raw_singlecell_01.h5ad")

    extraction = extract_external_pgaa_inputs(contract, label_column="perturbation")

    assert extraction.iloc[0]["extraction_status"] == "blocked_target_gene_missing_from_expression"


def test_external_pgaa_input_extraction_report_is_claim_safe(tmp_path):
    contract = _contract(tmp_path, status="blocked_by_readiness_gate")
    extraction = extract_external_pgaa_inputs(contract)
    summary = summarize_external_pgaa_input_extraction(extraction)
    report = render_external_pgaa_input_extraction_report(extraction, summary)

    assert int(summary["n_targets"].sum()) == 2
    assert "not replication evidence" in report
    assert "Extracted CSV files are inputs only" in report


def test_control_subsampling_is_deterministic_and_exact(tmp_path):
    contract = _contract(tmp_path).iloc[[0]].copy()
    obs = pd.DataFrame(
        {
            "perturbation": [
                "BHLHE40",
                "BHLHE40-AS1",
                "non-targeting",
                "non-targeting",
                "non-targeting",
                "non-targeting",
            ]
        },
        index=[f"cell_{i}" for i in range(6)],
    )
    var = pd.DataFrame(index=["BHLHE40", "STAT1"])
    ad.AnnData(np.arange(12).reshape(6, 2), obs=obs, var=var).write_h5ad(
        tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    )

    extraction = extract_external_pgaa_inputs(
        contract,
        label_column="perturbation",
        max_control_cells=2,
        control_sampling_seed="locked",
        exact_label_matching=True,
    )
    metadata = pd.read_csv(tmp_path / "BHLHE40" / "metadata.csv")

    assert extraction.iloc[0]["n_perturbed_cells"] == 1
    assert extraction.iloc[0]["n_control_cells"] == 2
    assert extraction.iloc[0]["n_control_cells_available"] == 4
    assert (metadata["group"] == "control").sum() == 2
    assert extraction.iloc[0]["control_sampling"] == "sha256:locked:max=2:exact=True"
    assert metadata["extraction_sampling_signature"].eq(
        "sha256:locked:max=2:exact=True"
    ).all()


def test_external_pgaa_input_extraction_retains_requested_metadata(tmp_path):
    contract = _contract(tmp_path).iloc[[0]].copy()
    obs = pd.DataFrame(
        {
            "perturbation": ["BHLHE40", "BHLHE40", "non-targeting", "non-targeting"],
            "batch": ["1", "2", "1", "2"],
        },
        index=[f"cell_batch_{i}" for i in range(4)],
    )
    var = pd.DataFrame(index=["BHLHE40", "STAT1"])
    ad.AnnData(np.arange(8).reshape(4, 2), obs=obs, var=var).write_h5ad(
        tmp_path / "K562_gwps_raw_singlecell_01.h5ad"
    )

    extract_external_pgaa_inputs(
        contract,
        label_column="perturbation",
        max_control_cells=2,
        control_sampling_seed="locked",
        exact_label_matching=True,
        metadata_columns=["batch"],
    )
    metadata = pd.read_csv(tmp_path / "BHLHE40" / "metadata.csv", dtype=str)

    assert set(metadata["source_batch"]) == {"1", "2"}
    assert metadata["extraction_sampling_signature"].eq(
        "sha256:locked:max=2:exact=True:metadata=batch"
    ).all()


def test_external_pgaa_input_extraction_rejects_missing_requested_metadata(tmp_path):
    contract = _contract(tmp_path).iloc[[0]].copy()
    _write_h5ad(tmp_path / "K562_gwps_raw_singlecell_01.h5ad")

    with pytest.raises(ValueError, match="requested metadata columns"):
        extract_external_pgaa_inputs(
            contract,
            label_column="perturbation",
            metadata_columns=["batch"],
        )
