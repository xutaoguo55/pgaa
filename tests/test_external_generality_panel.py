from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import pytest

from pgaa.core.external_generality_panel import (
    build_generality_execution_contract,
    build_generality_panel,
    build_generality_panel_from_h5ad,
    render_generality_panel_report,
)


def _metadata() -> tuple[pd.DataFrame, pd.Index]:
    rows = []
    for batch in ["b1", "b2"]:
        rows.extend([{"gene": "non-targeting", "batch": batch}] * 5)
    for i in range(20):
        rows.extend([{"gene": f"G{i:02d}", "batch": f"b{j % 2 + 1}"} for j in range(10 + i)])
    return pd.DataFrame(rows), pd.Index([f"G{i:02d}" for i in range(20)])


def test_panel_is_stratified_deterministic_and_excludes_current_targets():
    obs, var_names = _metadata()
    first_candidates, first = build_generality_panel(
        obs, var_names, {"G00"}, min_target_cells=10, per_stratum=2
    )
    _, second = build_generality_panel(
        obs, var_names, {"G00"}, min_target_cells=10, per_stratum=2
    )

    assert first["target_gene"].tolist() == second["target_gene"].tolist()
    assert len(first) == 8
    assert first.groupby("selection_stratum").size().eq(2).all()
    assert "G00" not in set(first["target_gene"])
    assert first_candidates.loc[
        first_candidates["target_gene"] == "G00", "excluded_current_target"
    ].item()
    assert first["allowed_claim_role"].eq(
        "cross_target_generality_only_not_same_target_replication"
    ).all()


def test_backed_h5ad_and_report_preserve_claim_boundary(tmp_path: Path):
    obs, var_names = _metadata()
    path = tmp_path / "panel.h5ad"
    ad.AnnData(
        np.zeros((len(obs), len(var_names)), dtype="float32"),
        obs=obs,
        var=pd.DataFrame(index=var_names),
    ).write_h5ad(path)
    candidates, panel, shape = build_generality_panel_from_h5ad(
        path, set(), min_target_cells=10, per_stratum=1
    )
    report = render_generality_panel_report(panel, candidates, path, shape, set(), 10)

    assert shape == (len(obs), len(var_names))
    assert len(panel) == 4
    assert "not a second biological source" in report
    assert "failed targets may not be silently replaced" in report


def test_missing_controls_is_rejected():
    obs, var_names = _metadata()
    with pytest.raises(ValueError, match="Control label"):
        build_generality_panel(obs[obs["gene"] != "non-targeting"], var_names, set())


def test_execution_contract_keeps_generality_distinct_from_replication(tmp_path: Path):
    obs, var_names = _metadata()
    _, panel = build_generality_panel(
        obs, var_names, set(), min_target_cells=10, per_stratum=1
    )
    contract = build_generality_execution_contract(
        panel, tmp_path / "source.h5ad", tmp_path / "outputs"
    )

    assert len(contract) == 4
    assert contract["claim_use"].eq(
        "cross_target_generality_execution_not_replication"
    ).all()
    assert contract["denominator_rule"].eq(
        "all_4_locked_targets_including_failures"
    ).all()
    assert contract["pgaa_command"].str.contains("--target-only-permutation-p").all()
