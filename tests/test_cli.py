"""Tests for the PGAA CSV command-line interface."""
from argparse import Namespace

import numpy as np
import pandas as pd

from pgaa.cli import run


def test_cli_csv_runner_writes_s1_s2_outputs(tmp_path):
    rng = np.random.default_rng(42)
    n_perturbed = 24
    n_control = 48
    n_cells = n_perturbed + n_control
    genes = ["TARGET", "S1_SHIFT", "S2_BIMODAL"] + [f"NULL_{i:02d}" for i in range(6)]
    cells = [f"cell_{i:03d}" for i in range(n_cells)]

    X = rng.normal(0.0, 0.25, size=(n_cells, len(genes)))
    X[:n_perturbed, genes.index("S1_SHIFT")] += 2.0
    half = n_perturbed // 2
    bimodal_col = genes.index("S2_BIMODAL")
    X[:half, bimodal_col] -= 1.8
    X[half:n_perturbed, bimodal_col] += 1.8

    expression = pd.DataFrame(X, index=cells, columns=genes)
    metadata = pd.DataFrame({
        "cell_id": cells,
        "group": ["perturbed"] * n_perturbed + ["control"] * n_control,
        "cell_type": np.resize(["ct1", "ct2"], n_cells),
        "library_size": np.full(n_cells, 10000.0),
    })
    expr_path = tmp_path / "expression.csv"
    meta_path = tmp_path / "metadata.csv"
    expression.to_csv(expr_path)
    metadata.to_csv(meta_path, index=False)

    args = Namespace(
        expression=expr_path,
        metadata=meta_path,
        target="TARGET",
        out_prefix=tmp_path / "pgaa_results",
        group_column="group",
        perturbed_value="perturbed",
        control_value="control",
        cell_type_column="cell_type",
        library_size_column="library_size",
        n_perms=39,
        n_bins=18,
        skip_s1=False,
        skip_s2=False,
        random_state=42,
    )
    s1_path, s2_path = run(args)

    assert s1_path.exists()
    assert s2_path.exists()
    s1 = pd.read_csv(s1_path).sort_values(
        ["p_value_perm", "W_observed"], ascending=[True, False]
    )
    s2 = pd.read_csv(s2_path).sort_values("S2", ascending=False)
    assert "S1_SHIFT" in set(s1.head(3)["gene"])
    assert "S2_BIMODAL" in set(s2.head(3)["gene"])
