import numpy as np
import pandas as pd

from pgaa.core.external_generality_baselines import (
    compile_generality_baselines,
    render_generality_baseline_report,
    summarize_generality_baselines,
)


def test_baseline_audit_is_explicitly_exploratory(tmp_path):
    expression = pd.DataFrame(
        {"A": [5, 6, 0, 1], "B": [1, 1, 1, 1]},
        index=["c1", "c2", "c3", "c4"],
    )
    metadata = pd.DataFrame(
        {"cell_id": expression.index, "group": ["perturbed", "perturbed", "control", "control"]}
    )
    expression.to_csv(tmp_path / "expression.csv")
    metadata.to_csv(tmp_path / "metadata.csv", index=False)
    contract = pd.DataFrame(
        [{"target_gene": "A", "expression_csv": tmp_path / "expression.csv", "metadata_csv": tmp_path / "metadata.csv"}]
    )
    pgaa = pd.DataFrame(
        [{"target_gene": "A", "pgaa_w_rank": 1, "pgaa_w_percentile": 0.5, "pgaa_h_rank": 1, "pgaa_h_percentile": 0.5}]
    )
    comparison = compile_generality_baselines(contract, pgaa)
    summary = summarize_generality_baselines(comparison)
    report = render_generality_baseline_report(comparison, summary)

    assert comparison.iloc[0]["absolute_mean_shift_rank"] == 1
    assert comparison.iloc[0]["welch_abs_t_rank"] == 1
    assert comparison.iloc[0]["analysis_role"] == "post_pilot_exploratory_baseline_audit"
    assert "not preregistered primary endpoints" in report
    assert "not PGAA superiority" in report
