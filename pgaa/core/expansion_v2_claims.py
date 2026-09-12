"""Machine-checkable confirmatory claim rules for expansion v2."""
from __future__ import annotations

import pandas as pd
from statsmodels.stats.proportion import proportion_confint


DUAL_GATE_STATES = (
    "stable_and_specific",
    "stable_but_not_specific",
    "specific_but_not_stable",
    "neither_stable_nor_specific",
)


def evaluate_expansion_v2_claim(gates: pd.DataFrame, platform_metadata: pd.DataFrame) -> pd.DataFrame:
    required_gates = {"dataset_id", "method", "dual_gate_state"}
    required_meta = {"candidate_id", "perturbation_mechanism", "cell_context_class"}
    if missing := sorted(required_gates - set(gates.columns)):
        raise ValueError(f"gate table is missing columns: {missing}")
    if missing := sorted(required_meta - set(platform_metadata.columns)):
        raise ValueError(f"platform metadata is missing columns: {missing}")
    primary = gates[gates["method"].eq("pgaa_w")].copy()
    primary = primary.merge(
        platform_metadata[list(required_meta)],
        left_on="dataset_id",
        right_on="candidate_id",
        how="left",
        validate="one_to_one",
    )
    if primary[["perturbation_mechanism", "cell_context_class"]].isna().any().any():
        raise ValueError("one or more scored platforms lack frozen metadata")

    events = primary[primary["dual_gate_state"].eq("stable_but_not_specific")]
    n_platforms = primary["dataset_id"].nunique()
    n_events = len(events)
    n_mechanisms = events["perturbation_mechanism"].nunique()
    n_contexts = events["cell_context_class"].nunique()
    complete = n_platforms == 10
    recurrence = complete and n_events >= 4 and n_mechanisms >= 3 and n_contexts >= 4

    loo_counts = []
    if complete:
        for omitted in primary["dataset_id"]:
            loo_counts.append(int((events["dataset_id"] != omitted).sum()))
    minimum_loo_events = min(loo_counts) if loo_counts else 0
    robust = recurrence and minimum_loo_events >= 3
    if not complete:
        state = "incomplete_confirmatory_cohort"
    elif robust:
        state = "platform_robust_cross_context_recurrence"
    elif recurrence:
        state = "cross_context_recurrence"
    else:
        state = "recurrence_not_confirmed"
    return pd.DataFrame(
        [
            {
                "primary_method": "pgaa_w",
                "n_confirmatory_platforms": n_platforms,
                "n_stable_but_not_specific": n_events,
                "event_fraction": n_events / n_platforms if n_platforms else float("nan"),
                "event_mechanism_classes": n_mechanisms,
                "event_cell_context_classes": n_contexts,
                "minimum_leave_one_study_out_events": minimum_loo_events,
                "confirmatory_claim_state": state,
            }
        ]
    )


def summarize_expansion_v2_landscape(
    gates: pd.DataFrame, platform_metadata: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize the pre-specified four-state space without replacing the primary estimand."""
    required_gates = {"dataset_id", "method", "dual_gate_state"}
    required_meta = {"candidate_id", "perturbation_mechanism", "cell_context_class"}
    if missing := sorted(required_gates - set(gates.columns)):
        raise ValueError(f"gate table is missing columns: {missing}")
    if missing := sorted(required_meta - set(platform_metadata.columns)):
        raise ValueError(f"platform metadata is missing columns: {missing}")
    unknown = sorted(set(gates["dual_gate_state"]) - set(DUAL_GATE_STATES))
    if unknown:
        raise ValueError(f"unknown dual-gate states: {unknown}")

    merged = gates.merge(
        platform_metadata[list(required_meta)],
        left_on="dataset_id",
        right_on="candidate_id",
        how="left",
        validate="many_to_one",
    )
    if merged[["perturbation_mechanism", "cell_context_class"]].isna().any().any():
        raise ValueError("one or more scored platforms lack frozen metadata")

    rows: list[dict[str, object]] = []
    for method, method_rows in merged.groupby("method", sort=True):
        n_platforms = method_rows["dataset_id"].nunique()
        for state in DUAL_GATE_STATES:
            state_rows = method_rows[method_rows["dual_gate_state"].eq(state)]
            count = len(state_rows)
            low, high = proportion_confint(count, n_platforms, alpha=0.05, method="beta")
            rows.append(
                {
                    "method": method,
                    "dual_gate_state": state,
                    "n_platforms": n_platforms,
                    "state_count": count,
                    "state_fraction": count / n_platforms if n_platforms else float("nan"),
                    "clopper_pearson_95_low": low,
                    "clopper_pearson_95_high": high,
                    "mechanism_classes": state_rows["perturbation_mechanism"].nunique(),
                    "cell_context_classes": state_rows["cell_context_class"].nunique(),
                    "minimum_leave_one_study_out_count": max(0, count - 1),
                }
            )
    landscape = pd.DataFrame(rows)

    pgaa = merged[merged["method"].eq("pgaa_w")]
    joint = pgaa[pgaa["dual_gate_state"].eq("stable_and_specific")]
    n_platforms = pgaa["dataset_id"].nunique()
    n_joint = len(joint)
    n_mechanisms = joint["perturbation_mechanism"].nunique()
    n_contexts = joint["cell_context_class"].nunique()
    min_loo = max(0, n_joint - 1) if n_platforms == 10 else 0
    recurrence = n_platforms == 10 and n_joint >= 4 and n_mechanisms >= 3 and n_contexts >= 4
    robust = recurrence and min_loo >= 3
    if n_platforms != 10:
        state = "incomplete_secondary_state_landscape"
    elif robust:
        state = "platform_robust_cross_context_joint_portability"
    elif recurrence:
        state = "cross_context_joint_portability"
    else:
        state = "joint_portability_not_recurrent"
    low, high = proportion_confint(n_joint, n_platforms, alpha=0.05, method="beta")
    portability = pd.DataFrame(
        [
            {
                "method": "pgaa_w",
                "state_of_interest": "stable_and_specific",
                "n_confirmatory_platforms": n_platforms,
                "state_count": n_joint,
                "state_fraction": n_joint / n_platforms if n_platforms else float("nan"),
                "clopper_pearson_95_low": low,
                "clopper_pearson_95_high": high,
                "mechanism_classes": n_mechanisms,
                "cell_context_classes": n_contexts,
                "minimum_leave_one_study_out_count": min_loo,
                "secondary_state": state,
                "analysis_status": "post_outcome_symmetric_rule_application",
                "claim_scope": "secondary_state_landscape_not_frozen_primary_estimand",
            }
        ]
    )
    return landscape, portability
