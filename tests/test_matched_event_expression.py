import pandas as pd

from pgaa.core.matched_event_expression import (
    T790M_VARIANT_ID,
    prepare_gse112274_event_expression,
    render_gse112274_audit,
)


def test_prepare_event_expression_creates_locked_groups_and_cli_matrix():
    cells = ["PC9_LOW_AF_1", "PC9_LOW_AF_2", "PC9_HIGH_AF_1", "PC9_HIGH_AF_2", "PC9_G3_early_1"]
    expression = pd.DataFrame(
        {
            cell: [index + offset for index in range(3)]
            for offset, cell in enumerate(cells)
        },
        index=["ENSG1__EGFR", "ENSG2__STAT1", "ENSG3__B2M"],
    )
    af = pd.DataFrame([[0.001, 0.01, 0.2, 0.8, 0.05]], index=[T790M_VARIANT_ID], columns=cells)
    dp = pd.DataFrame([[1000] * 5], index=[T790M_VARIANT_ID], columns=cells)

    cli_expression, metadata, summary = prepare_gse112274_event_expression(
        expression,
        af,
        dp,
        min_detected_cells=1,
        n_variable_genes=2,
    )

    assert cli_expression.shape == (4, 2)
    assert "EGFR" in cli_expression.columns
    assert set(metadata["group"]) == {"perturbed", "control"}
    assert summary.iloc[0]["n_event_high"] == 2
    assert summary.iloc[0]["n_event_low"] == 2
    assert summary.iloc[0]["n_excluded_transition"] == 1
    assert "not a perturbation experiment" in render_gse112274_audit(summary)


def test_prepare_event_expression_rejects_misaligned_cells():
    expression = pd.DataFrame({"c1": [1]}, index=["ENSG1__EGFR"])
    af = pd.DataFrame([[0.2]], index=[T790M_VARIANT_ID], columns=["c2"])
    dp = pd.DataFrame([[1000]], index=[T790M_VARIANT_ID], columns=["c2"])

    try:
        prepare_gse112274_event_expression(expression, af, dp)
    except ValueError as error:
        assert "cell columns must match" in str(error)
    else:
        raise AssertionError("misaligned cells should fail")


def test_prepare_event_expression_reorders_matching_cell_sets():
    expression = pd.DataFrame({"c1": [1], "c2": [2]}, index=["ENSG1__EGFR"])
    af = pd.DataFrame([[0.2, 0.001]], index=[T790M_VARIANT_ID], columns=["c2", "c1"])
    dp = pd.DataFrame([[1000, 1000]], index=[T790M_VARIANT_ID], columns=["c2", "c1"])

    cli_expression, metadata, _ = prepare_gse112274_event_expression(
        expression, af, dp, min_detected_cells=1, n_variable_genes=1
    )

    assert list(cli_expression.index) == ["c1", "c2"]
    assert list(metadata["event_state"]) == ["event_low", "event_high"]
