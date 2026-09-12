from pathlib import Path

import pandas as pd

from pgaa.core.external_generality_results import (
    compile_generality_results,
    render_generality_results_report,
    summarize_generality_results,
)


def test_compiler_keeps_missing_target_in_locked_denominator(tmp_path: Path):
    complete = tmp_path / "complete"
    complete.mkdir()
    pd.DataFrame(
        {"gene": ["A", "B"], "W_observed": [2.0, 1.0], "p_value_perm": [0.01, None]}
    ).to_csv(complete / "A.s1.csv", index=False)
    pd.DataFrame({"gene": ["B", "A"], "S2": [2.0, 1.0]}).to_csv(
        complete / "A.s2.csv", index=False
    )
    contract = pd.DataFrame(
        [
            {"target_gene": "A", "pgaa_s1_out": complete / "A.s1.csv", "pgaa_s2_out": complete / "A.s2.csv", "denominator_rule": "all_2_locked_targets_including_failures"},
            {"target_gene": "MISSING", "pgaa_s1_out": tmp_path / "missing.s1.csv", "pgaa_s2_out": tmp_path / "missing.s2.csv", "denominator_rule": "all_2_locked_targets_including_failures"},
        ]
    )
    results = compile_generality_results(contract)
    summary = summarize_generality_results(results)
    report = render_generality_results_report(results, summary)

    assert len(results) == 2
    assert results.loc[1, "execution_status"] == "failed_or_incomplete"
    assert summary.set_index("metric").loc["execution_complete", "n_success"] == 1
    assert summary["n_locked_targets"].eq(2).all()
    assert "not independent biological replicates" in report
