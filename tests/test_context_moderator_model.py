import numpy as np
import pandas as pd

from pgaa.core.context_moderator_model import (
    FEATURE_COLUMNS,
    build_training_table,
    classify_state,
    fit_final_models,
    leave_one_platform_out,
    predict_from_serialized,
    serialize_models,
    state_probabilities,
    summarize_lopo,
)


def _inputs():
    ids = [f"d{i}" for i in range(10)]
    states = ["stable_and_specific"] * 6 + ["specific_but_not_stable"] + ["neither_stable_nor_specific"] * 3
    gates = pd.DataFrame(
        {
            "dataset_id": ids,
            "method": ["pgaa_w"] * 10,
            "stability_gate_pass": [True] * 6 + [False] * 4,
            "specificity_gate_pass": [True] * 7 + [False] * 3,
            "dual_gate_state": states,
        }
    )
    contracts = pd.DataFrame(
        {
            "candidate_id": ids,
            "n_recorded_split_levels": [2, 3, 4, 8, 2, 4, 3, 6, 2, 8],
            "minimum_equal_group_size": [20, 25, 30, 35, 40, 45, 30, 50, 22, 55],
            "maximum_equal_group_size": [70] * 10,
        }
    )
    moderators = pd.DataFrame(
        {
            "candidate_id": ids,
            "genetic_perturbation": [0, 1] * 5,
            "primary_or_in_vivo": [1, 0, 0, 1, 1, 0, 1, 0, 0, 0],
            "mouse_system": [0, 1, 1, 0, 1, 1, 0, 0, 0, 0],
            "split_independence_tier": [2, 1, 2, 1, 0, 2, 2, 0, 1, 2],
        }
    )
    return gates, contracts, moderators


def test_training_table_derives_only_frozen_contract_features():
    table = build_training_table(*_inputs())
    assert len(table) == 10
    assert set(FEATURE_COLUMNS).issubset(table.columns)
    assert np.isclose(table.loc[0, "log2_recorded_split_levels"], 1.0)
    assert table["minimum_equal_group_fraction"].between(0, 1).all()


def test_state_composition_is_complete_and_thresholded():
    probabilities = state_probabilities(0.8, 0.25)
    assert np.isclose(sum(probabilities.values()), 1.0)
    assert classify_state(0.8, 0.25) == "stable_but_not_specific"
    assert classify_state(0.2, 0.75) == "specific_but_not_stable"


def test_lopo_is_strictly_out_of_platform_and_serializable():
    table = build_training_table(*_inputs())
    predictions = leave_one_platform_out(table)
    assert len(predictions) == 10
    assert predictions["predicted_state"].notna().all()
    assert predictions.filter(like="state_probability_").sum(axis=1).round(10).eq(1.0).all()
    metrics = summarize_lopo(predictions)
    assert set(metrics["metric_scope"]) == {"joint_primary", "stability", "specificity"}
    models, coefficients = fit_final_models(table)
    payload = serialize_models(models)
    assert payload["feature_order"] == list(FEATURE_COLUMNS)
    assert len(coefficients) == 2 * (len(FEATURE_COLUMNS) + 1)
    prospective = table.rename(columns={"dataset_id": "candidate_id"})
    predicted = predict_from_serialized(prospective, payload)
    assert len(predicted) == 10
    assert predicted["locked_predicted_state"].notna().all()
