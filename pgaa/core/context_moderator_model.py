"""Pre-outcome context model for the four PGAA dual-gate states."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = (
    "genetic_perturbation",
    "primary_or_in_vivo",
    "mouse_system",
    "split_independence_tier",
    "log2_recorded_split_levels",
    "minimum_equal_group_fraction",
)

STATE_ORDER = (
    "stable_and_specific",
    "stable_but_not_specific",
    "specific_but_not_stable",
    "neither_stable_nor_specific",
)


@dataclass(frozen=True)
class ModeratorModelSpec:
    c_value: float = 0.25
    threshold: float = 0.5
    random_state: int = 73021


def build_training_table(
    gates: pd.DataFrame,
    contracts: pd.DataFrame,
    moderators: pd.DataFrame,
) -> pd.DataFrame:
    """Join outcome-free context descriptors to the frozen v2 PGAA-W outcomes."""
    primary = gates.loc[
        gates["method"].eq("pgaa_w"),
        ["dataset_id", "stability_gate_pass", "specificity_gate_pass", "dual_gate_state"],
    ].copy()
    if primary["dataset_id"].duplicated().any():
        raise ValueError("PGAA-W gate table must contain one row per platform")

    contract_columns = [
        "candidate_id",
        "n_recorded_split_levels",
        "minimum_equal_group_size",
        "maximum_equal_group_size",
    ]
    missing_contract = sorted(set(contract_columns) - set(contracts.columns))
    if missing_contract:
        raise ValueError(f"contract table is missing columns: {missing_contract}")
    missing_moderators = sorted(
        {
            "candidate_id",
            "genetic_perturbation",
            "primary_or_in_vivo",
            "mouse_system",
            "split_independence_tier",
        }
        - set(moderators.columns)
    )
    if missing_moderators:
        raise ValueError(f"moderator table is missing columns: {missing_moderators}")

    contract_features = contracts[contract_columns].rename(columns={"candidate_id": "dataset_id"})
    moderator_features = moderators.rename(columns={"candidate_id": "dataset_id"})
    table = primary.merge(
        contract_features,
        on="dataset_id",
        how="left",
        validate="one_to_one",
    ).merge(
        moderator_features,
        on="dataset_id",
        how="left",
        validate="one_to_one",
    )
    if len(table) != 10:
        raise ValueError(f"expected 10 frozen v2 platforms, observed {len(table)}")
    table["log2_recorded_split_levels"] = np.log2(table["n_recorded_split_levels"].astype(float))
    table["minimum_equal_group_fraction"] = (
        table["minimum_equal_group_size"].astype(float)
        / table["maximum_equal_group_size"].astype(float)
    )
    table["stability_gate_pass"] = table["stability_gate_pass"].astype(int)
    table["specificity_gate_pass"] = table["specificity_gate_pass"].astype(int)
    if table[list(FEATURE_COLUMNS)].isna().any().any():
        raise ValueError("one or more v2 platforms lack a frozen context descriptor")
    if not table["split_independence_tier"].between(0, 2).all():
        raise ValueError("split_independence_tier must be 0, 1, or 2")
    return table.sort_values("dataset_id").reset_index(drop=True)


def _new_axis_model(spec: ModeratorModelSpec) -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "logistic",
                LogisticRegression(
                    C=spec.c_value,
                    penalty="l2",
                    solver="liblinear",
                    class_weight="balanced",
                    random_state=spec.random_state,
                ),
            ),
        ]
    )


def state_probabilities(stability: float, specificity: float) -> dict[str, float]:
    """Combine two marginal gate probabilities using the frozen product rule."""
    return {
        "stable_and_specific": stability * specificity,
        "stable_but_not_specific": stability * (1.0 - specificity),
        "specific_but_not_stable": (1.0 - stability) * specificity,
        "neither_stable_nor_specific": (1.0 - stability) * (1.0 - specificity),
    }


def classify_state(stability: float, specificity: float, threshold: float = 0.5) -> str:
    stable = stability >= threshold
    specific = specificity >= threshold
    if stable and specific:
        return "stable_and_specific"
    if stable:
        return "stable_but_not_specific"
    if specific:
        return "specific_but_not_stable"
    return "neither_stable_nor_specific"


def leave_one_platform_out(
    table: pd.DataFrame,
    spec: ModeratorModelSpec = ModeratorModelSpec(),
) -> pd.DataFrame:
    """Produce strictly out-of-platform predictions and prevalence comparators."""
    rows: list[dict[str, object]] = []
    x_all = table.loc[:, FEATURE_COLUMNS].astype(float)
    for held_out in range(len(table)):
        train_mask = np.arange(len(table)) != held_out
        x_train = x_all.loc[train_mask]
        x_test = x_all.iloc[[held_out]]
        row: dict[str, object] = {
            "dataset_id": table.iloc[held_out]["dataset_id"],
            "observed_state": table.iloc[held_out]["dual_gate_state"],
            "observed_stability": int(table.iloc[held_out]["stability_gate_pass"]),
            "observed_specificity": int(table.iloc[held_out]["specificity_gate_pass"]),
        }
        axis_probabilities: dict[str, float] = {}
        for axis, outcome in (
            ("stability", "stability_gate_pass"),
            ("specificity", "specificity_gate_pass"),
        ):
            y_train = table.loc[train_mask, outcome].astype(int)
            model = _new_axis_model(spec).fit(x_train, y_train)
            probability = float(model.predict_proba(x_test)[0, 1])
            prevalence = float((y_train.sum() + 1.0) / (len(y_train) + 2.0))
            axis_probabilities[axis] = probability
            row[f"predicted_{axis}_probability"] = probability
            row[f"prevalence_{axis}_probability"] = prevalence
        probabilities = state_probabilities(
            axis_probabilities["stability"], axis_probabilities["specificity"]
        )
        row.update({f"state_probability_{state}": value for state, value in probabilities.items()})
        row["predicted_state"] = classify_state(
            axis_probabilities["stability"],
            axis_probabilities["specificity"],
            spec.threshold,
        )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_lopo(predictions: pd.DataFrame) -> pd.DataFrame:
    """Summarize the frozen primary and secondary model performance metrics."""
    axis_rows = []
    per_platform_model = np.zeros(len(predictions), dtype=float)
    per_platform_null = np.zeros(len(predictions), dtype=float)
    for axis in ("stability", "specificity"):
        observed = predictions[f"observed_{axis}"].astype(int).to_numpy()
        predicted = predictions[f"predicted_{axis}_probability"].to_numpy()
        comparator = predictions[f"prevalence_{axis}_probability"].to_numpy()
        per_platform_model += (predicted - observed) ** 2 / 2.0
        per_platform_null += (comparator - observed) ** 2 / 2.0
        axis_rows.append(
            {
                "metric_scope": axis,
                "model_brier": brier_score_loss(observed, predicted),
                "prevalence_brier": brier_score_loss(observed, comparator),
                "balanced_accuracy": balanced_accuracy_score(observed, predicted >= 0.5),
                "roc_auc": roc_auc_score(observed, predicted),
                "exact_state_accuracy": np.nan,
                "paired_wilcoxon_one_sided_p": np.nan,
            }
        )
    try:
        paired_p = float(
            wilcoxon(
                per_platform_null - per_platform_model,
                alternative="greater",
                method="exact",
            ).pvalue
        )
    except ValueError:
        paired_p = 1.0
    model_brier = float(per_platform_model.mean())
    prevalence_brier = float(per_platform_null.mean())
    state_accuracy = float(
        predictions["predicted_state"].eq(predictions["observed_state"]).mean()
    )
    confirmation_pass = model_brier < prevalence_brier and state_accuracy >= 0.60 and paired_p < 0.05
    joint = {
        "metric_scope": "joint_primary",
        "model_brier": model_brier,
        "prevalence_brier": prevalence_brier,
        "balanced_accuracy": np.nan,
        "roc_auc": np.nan,
        "exact_state_accuracy": state_accuracy,
        "paired_wilcoxon_one_sided_p": paired_p,
        "confirmation_rule_pass": confirmation_pass,
    }
    summary = pd.DataFrame([joint, *axis_rows])
    summary["confirmation_rule_pass"] = summary["confirmation_rule_pass"].astype("boolean")
    return summary


def fit_final_models(
    table: pd.DataFrame,
    spec: ModeratorModelSpec = ModeratorModelSpec(),
) -> tuple[dict[str, Pipeline], pd.DataFrame]:
    """Fit the frozen model to all v2 platforms and expose standardized coefficients."""
    x = table.loc[:, FEATURE_COLUMNS].astype(float)
    models: dict[str, Pipeline] = {}
    coefficient_rows = []
    for axis, outcome in (
        ("stability", "stability_gate_pass"),
        ("specificity", "specificity_gate_pass"),
    ):
        model = _new_axis_model(spec).fit(x, table[outcome].astype(int))
        models[axis] = model
        logistic = model.named_steps["logistic"]
        for feature, coefficient in zip(FEATURE_COLUMNS, logistic.coef_[0]):
            coefficient_rows.append(
                {"axis": axis, "term": feature, "standardized_log_odds_coefficient": coefficient}
            )
        coefficient_rows.append(
            {"axis": axis, "term": "intercept", "standardized_log_odds_coefficient": logistic.intercept_[0]}
        )
    return models, pd.DataFrame(coefficient_rows)


def serialize_models(
    models: dict[str, Pipeline],
    spec: ModeratorModelSpec = ModeratorModelSpec(),
) -> dict[str, object]:
    """Serialize enough parameters to reproduce inference without a pickle."""
    axes: dict[str, object] = {}
    for axis, model in models.items():
        scaler = model.named_steps["scale"]
        logistic = model.named_steps["logistic"]
        axes[axis] = {
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
            "coefficient": logistic.coef_[0].tolist(),
            "intercept": float(logistic.intercept_[0]),
        }
    return {
        "model_family": "two_axis_l2_logistic_regression",
        "feature_order": list(FEATURE_COLUMNS),
        "state_order": list(STATE_ORDER),
        "c_value": spec.c_value,
        "class_weight": "balanced",
        "decision_threshold": spec.threshold,
        "state_probability_rule": "product_of_axis_probabilities",
        "random_state": spec.random_state,
        "axes": axes,
    }


def predict_from_serialized(
    features: pd.DataFrame,
    payload: dict[str, object],
) -> pd.DataFrame:
    """Apply the JSON-serialized model to a pre-outcome v3 context contract."""
    feature_order = payload["feature_order"]
    missing = sorted(set(feature_order) - set(features.columns))
    if missing:
        raise ValueError(f"prediction table is missing features: {missing}")
    if "candidate_id" not in features:
        raise ValueError("prediction table is missing candidate_id")
    x = features.loc[:, feature_order].astype(float).to_numpy()
    probabilities: dict[str, np.ndarray] = {}
    for axis in ("stability", "specificity"):
        axis_payload = payload["axes"][axis]
        mean = np.asarray(axis_payload["scaler_mean"], dtype=float)
        scale = np.asarray(axis_payload["scaler_scale"], dtype=float)
        coefficient = np.asarray(axis_payload["coefficient"], dtype=float)
        linear = ((x - mean) / scale) @ coefficient + float(axis_payload["intercept"])
        probabilities[axis] = 1.0 / (1.0 + np.exp(-linear))
    rows = []
    threshold = float(payload["decision_threshold"])
    for index, candidate_id in enumerate(features["candidate_id"]):
        stability = float(probabilities["stability"][index])
        specificity = float(probabilities["specificity"][index])
        state_probs = state_probabilities(stability, specificity)
        rows.append(
            {
                "candidate_id": candidate_id,
                "predicted_stability_probability": stability,
                "predicted_specificity_probability": specificity,
                **{f"state_probability_{state}": value for state, value in state_probs.items()},
                "locked_predicted_state": classify_state(stability, specificity, threshold),
            }
        )
    return pd.DataFrame(rows)
