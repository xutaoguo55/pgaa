"""Frozen prospective endpoint rules for PGAA expansion v3."""
from __future__ import annotations

import pandas as pd
from statsmodels.stats.proportion import proportion_confint


MIN_PROSPECTIVE_PLATFORMS = 10
MIN_PRIMARY_EVENTS = 4
MIN_EVENT_MECHANISM_CLASSES = 3
MIN_EVENT_CELL_CONTEXT_CLASSES = 4
MIN_LEAVE_ONE_OUT_EVENTS = 3


def evaluate_expansion_v3_endpoint(
    gates: pd.DataFrame,
    platform_metadata: pd.DataFrame,
) -> pd.DataFrame:
    required_gates = {"dataset_id", "method", "dual_gate_state"}
    required_meta = {"candidate_id", "perturbation_mechanism", "cell_context_class"}
    if missing := sorted(required_gates - set(gates.columns)):
        raise ValueError(f"gate table is missing columns: {missing}")
    if missing := sorted(required_meta - set(platform_metadata.columns)):
        raise ValueError(f"platform metadata is missing columns: {missing}")
    primary = gates[gates["method"].eq("pgaa_w")].merge(
        platform_metadata[list(required_meta)],
        left_on="dataset_id",
        right_on="candidate_id",
        how="left",
        validate="one_to_one",
    )
    if primary[["perturbation_mechanism", "cell_context_class"]].isna().any().any():
        raise ValueError("one or more v3 platforms lack frozen metadata")
    n_platforms = primary["dataset_id"].nunique()
    events = primary[primary["dual_gate_state"].eq("stable_and_specific")]
    n_events = len(events)
    n_mechanisms = events["perturbation_mechanism"].nunique()
    n_contexts = events["cell_context_class"].nunique()
    low, high = proportion_confint(n_events, n_platforms, alpha=0.05, method="beta")
    min_loo = max(0, n_events - 1) if n_platforms >= MIN_PROSPECTIVE_PLATFORMS else 0
    recurrent = (
        n_platforms >= MIN_PROSPECTIVE_PLATFORMS
        and n_events >= MIN_PRIMARY_EVENTS
        and n_mechanisms >= MIN_EVENT_MECHANISM_CLASSES
        and n_contexts >= MIN_EVENT_CELL_CONTEXT_CLASSES
    )
    robust = recurrent and min_loo >= MIN_LEAVE_ONE_OUT_EVENTS
    if n_platforms < MIN_PROSPECTIVE_PLATFORMS:
        claim_state = "incomplete_prospective_cohort"
    elif robust:
        claim_state = "platform_robust_cross_context_joint_portability"
    elif recurrent:
        claim_state = "cross_context_joint_portability"
    else:
        claim_state = "joint_portability_not_confirmed"
    return pd.DataFrame(
        [
            {
                "primary_method": "pgaa_w",
                "primary_event": "stable_and_specific",
                "minimum_prospective_platforms": MIN_PROSPECTIVE_PLATFORMS,
                "minimum_primary_events": MIN_PRIMARY_EVENTS,
                "minimum_event_mechanism_classes": MIN_EVENT_MECHANISM_CLASSES,
                "minimum_event_cell_context_classes": MIN_EVENT_CELL_CONTEXT_CLASSES,
                "minimum_leave_one_platform_out_event_gate": MIN_LEAVE_ONE_OUT_EVENTS,
                "n_prospective_platforms": n_platforms,
                "event_count": n_events,
                "event_fraction": n_events / n_platforms if n_platforms else float("nan"),
                "clopper_pearson_95_low": low,
                "clopper_pearson_95_high": high,
                "event_mechanism_classes": n_mechanisms,
                "event_cell_context_classes": n_contexts,
                "minimum_leave_one_platform_out_events": min_loo,
                "primary_claim_state": claim_state,
            }
        ]
    )
