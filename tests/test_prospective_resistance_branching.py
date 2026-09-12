import numpy as np
import pandas as pd

from pgaa.core.prospective_resistance_branching import (
    CELL_LINES,
    STATES,
    classify_gse193258_branches,
    predict_branch_vulnerabilities,
)


def test_frozen_classifier_assigns_adaptive_branch() -> None:
    pc9 = [f"P{index}" for index in range(200)]
    h4006 = [f"H{index}" for index in range(200)]
    background = [f"B{index}" for index in range(600)]
    genes = pd.DataFrame(
        {
            "gene_symbol": pc9 + h4006,
            "dtc_pc9_minus_h4006": np.r_[np.arange(200, 0, -1), -np.arange(1, 201)],
        }
    )
    columns = []
    for cell_line in CELL_LINES:
        for state in ("DMSO",) + STATES:
            columns.extend(f"{cell_line}_{state}_{replicate}" for replicate in (1, 2, 3))
    expression = pd.DataFrame(
        10.0, index=pc9 + h4006 + background, columns=columns
    )
    for cell_line in CELL_LINES:
        expression.loc[pc9, [f"{cell_line}_osi_DTP_{r}" for r in (1, 2, 3)]] += 3
        expression.loc[h4006, [f"{cell_line}_osi_DTP_{r}" for r in (1, 2, 3)]] -= 3
    assignments, trajectories = classify_gse193258_branches(
        genes, expression, permutations=99, seed=5
    )
    assert (assignments["assigned_branch"] == "adaptive_stress").all()
    assert (assignments["assignment_gate"] == "pass").all()
    assert len(trajectories) == len(CELL_LINES) * len(STATES)
    vulnerabilities = predict_branch_vulnerabilities(assignments)
    assert set(vulnerabilities["target_class"]) == {"TEAD", "BRD4", "MEK1/2"}
