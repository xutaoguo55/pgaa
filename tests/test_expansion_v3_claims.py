import pandas as pd

from pgaa.core.expansion_v3_claims import evaluate_expansion_v3_endpoint


def test_v3_endpoint_is_stable_and_specific_and_uses_frozen_span_rule():
    ids = [f"d{i}" for i in range(14)]
    gates = pd.DataFrame(
        {
            "dataset_id": ids,
            "method": ["pgaa_w"] * 14,
            "dual_gate_state": ["stable_and_specific"] * 4 + ["neither_stable_nor_specific"] * 10,
        }
    )
    metadata = pd.DataFrame(
        {
            "candidate_id": ids,
            "perturbation_mechanism": ["crispr", "drug", "cytokine", "crispr"] + ["drug"] * 10,
            "cell_context_class": [f"context{i}" for i in range(14)],
        }
    )
    endpoint = evaluate_expansion_v3_endpoint(gates, metadata).iloc[0]
    assert endpoint["primary_event"] == "stable_and_specific"
    assert endpoint["minimum_prospective_platforms"] == 10
    assert endpoint["event_count"] == 4
    assert endpoint["minimum_leave_one_platform_out_events"] == 3
    assert endpoint["primary_claim_state"] == "platform_robust_cross_context_joint_portability"


def test_v3_endpoint_does_not_promote_incomplete_cohort():
    gates = pd.DataFrame(
        {
            "dataset_id": [f"d{i}" for i in range(9)],
            "method": ["pgaa_w"] * 9,
            "dual_gate_state": ["stable_and_specific"] * 9,
        }
    )
    metadata = pd.DataFrame(
        {
            "candidate_id": [f"d{i}" for i in range(9)],
            "perturbation_mechanism": [f"m{i}" for i in range(9)],
            "cell_context_class": [f"c{i}" for i in range(9)],
        }
    )
    endpoint = evaluate_expansion_v3_endpoint(gates, metadata).iloc[0]
    assert endpoint["primary_claim_state"] == "incomplete_prospective_cohort"
