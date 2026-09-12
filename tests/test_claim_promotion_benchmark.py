import pandas as pd
import pytest

from pgaa.core.claim_promotion_benchmark import (
    build_claim_promotion_scenarios,
    render_claim_promotion_benchmark_report,
    summarize_claim_promotion_benchmark,
)


def _objects() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "u1",
                "decision_state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "external_state": "external_same_context_concordant",
                "permission_rank": 3,
            }
        ]
    )


def test_exhaustive_benchmark_detects_baseline_claim_promotion():
    scenarios = build_claim_promotion_scenarios(_objects())
    summary = summarize_claim_promotion_benchmark(scenarios)
    overall = summary[summary["scope"] == "all_scenarios"].set_index("method")

    assert scenarios["scenario_id"].nunique() == 6 * 4 * 5
    assert len(scenarios) == 6 * 4 * 5 * 4
    assert overall.loc["claim_state_compiler", "false_promotion_rate"] == 0
    assert overall.loc["claim_state_compiler", "exact_permission_rate"] == 1
    assert overall.loc["state_blind_frozen_baseline", "false_promotion_rate"] > 0
    assert overall.loc["decision_only_baseline", "replication_sensitivity"] == 0
    assert overall.loc["external_only_baseline", "replication_false_positive_rate"] > 0


def test_report_discloses_contract_oracle_limit():
    scenarios = build_claim_promotion_scenarios(_objects())
    summary = summarize_claim_promotion_benchmark(scenarios)
    report = render_claim_promotion_benchmark_report(scenarios, summary)

    assert "contract stress test, not an empirical ground-truth benchmark" in report
    assert "zero-error result is expected" in report


def test_benchmark_requires_unique_well_formed_objects():
    with pytest.raises(ValueError, match="missing columns"):
        build_claim_promotion_scenarios(pd.DataFrame({"unit_id": ["u1"]}))
    duplicated = pd.concat([_objects(), _objects()], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate unit_id"):
        build_claim_promotion_scenarios(duplicated)
