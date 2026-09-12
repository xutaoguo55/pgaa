import pandas as pd

from pgaa.core.expansion_v2_claims import (
    evaluate_expansion_v2_claim,
    summarize_expansion_v2_landscape,
)


def _metadata() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "candidate_id": [f"d{i}" for i in range(10)],
            "perturbation_mechanism": ["crispr", "drug", "cytokine", "crispr", "drug"] * 2,
            "cell_context_class": [f"context{i}" for i in range(10)],
        }
    )


def test_claim_requires_complete_cohort_and_cross_context_span():
    gates = pd.DataFrame(
        {
            "dataset_id": [f"d{i}" for i in range(10)],
            "method": ["pgaa_w"] * 10,
            "dual_gate_state": ["stable_but_not_specific"] * 4 + ["stable_and_specific"] * 6,
        }
    )
    claim = evaluate_expansion_v2_claim(gates, _metadata()).iloc[0]
    assert claim["confirmatory_claim_state"] == "platform_robust_cross_context_recurrence"
    assert claim["minimum_leave_one_study_out_events"] == 3

    incomplete = evaluate_expansion_v2_claim(gates.iloc[:9], _metadata()).iloc[0]
    assert incomplete["confirmatory_claim_state"] == "incomplete_confirmatory_cohort"


def test_claim_rejects_event_concentrated_in_too_few_mechanisms():
    gates = pd.DataFrame(
        {
            "dataset_id": [f"d{i}" for i in range(10)],
            "method": ["pgaa_w"] * 10,
            "dual_gate_state": ["stable_but_not_specific" if i in (0, 1, 3, 5) else "stable_and_specific" for i in range(10)],
        }
    )
    claim = evaluate_expansion_v2_claim(gates, _metadata()).iloc[0]
    assert claim["event_mechanism_classes"] == 2
    assert claim["confirmatory_claim_state"] == "recurrence_not_confirmed"


def test_landscape_preserves_zero_states_and_types_secondary_portability():
    gates = pd.DataFrame(
        {
            "dataset_id": [f"d{i}" for i in range(10)],
            "method": ["pgaa_w"] * 10,
            "dual_gate_state": ["stable_and_specific"] * 6
            + ["specific_but_not_stable"]
            + ["neither_stable_nor_specific"] * 3,
        }
    )
    landscape, portability = summarize_expansion_v2_landscape(gates, _metadata())
    stable_null = landscape[landscape["dual_gate_state"].eq("stable_but_not_specific")].iloc[0]
    assert stable_null["state_count"] == 0
    secondary = portability.iloc[0]
    assert secondary["state_count"] == 6
    assert secondary["minimum_leave_one_study_out_count"] == 5
    assert secondary["secondary_state"] == "platform_robust_cross_context_joint_portability"
    assert secondary["claim_scope"] == "secondary_state_landscape_not_frozen_primary_estimand"
