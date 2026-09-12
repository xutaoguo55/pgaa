import pandas as pd
import pytest

from pgaa.core.external_responder_state_stability import (
    integrate_external_responder_state_stability,
    render_external_responder_state_stability_report,
    summarize_external_responder_state_stability,
)


def _internal_stability() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson_decision_benchmark::BHLHE40_pDS258",
                "evidence_type": "adamson_decision_benchmark",
                "context": "BHLHE40_pDS258",
                "baseline_decision_state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 5,
                "n_state_preserved": 5,
                "n_state_changed": 0,
            },
            {
                "unit_id": "adamson_decision_benchmark::CREB1_pDS269",
                "evidence_type": "adamson_decision_benchmark",
                "context": "CREB1_pDS269",
                "baseline_decision_state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "n_leave_one_checks": 5,
                "n_state_preserved": 5,
                "n_state_changed": 0,
            },
        ]
    )


def _external_claims(concordance: str, claim_state: str = "external_pgaa_w_h_support_observed"):
    return pd.DataFrame(
        [
            {
                "target_gene": "BHLHE40",
                "internal_unit_id": "adamson_decision_benchmark::BHLHE40_pDS258",
                "external_claim_state": claim_state,
                "concordance_state": concordance,
                "claim_use": "external_claim_state_not_wet_lab_validation",
            }
        ]
    )


def test_external_responder_state_stability_concordant_upgrade():
    integrated = integrate_external_responder_state_stability(
        _internal_stability(),
        _external_claims("external_concordant_with_internal_supported_unit"),
    ).set_index("unit_id")

    row = integrated.loc["adamson_decision_benchmark::BHLHE40_pDS258"]
    assert row["integrated_cross_dataset_status"] == "external_same_context_concordant"
    assert row["claim_ceiling"] == "bounded_computational_same_context_replication_allowed"

    missing = integrated.loc["adamson_decision_benchmark::CREB1_pDS269"]
    assert missing["external_claim_state"] == "missing_external_claim_state"
    assert missing["integrated_cross_dataset_status"] == "external_same_context_blocked"


def test_external_responder_state_stability_discordant_blocks_replication():
    integrated = integrate_external_responder_state_stability(
        _internal_stability(),
        _external_claims(
            "external_discordant_with_internal_supported_unit",
            claim_state="external_support_not_observed",
        ),
    )

    row = integrated[integrated["external_target_gene"] == "BHLHE40"].iloc[0]
    assert row["integrated_cross_dataset_status"] == "external_same_context_discordant"
    assert row["claim_ceiling"] == "replication_claim_blocked_by_external_discordance"


def test_external_concordance_cannot_upgrade_an_internally_unstable_unit():
    internal = _internal_stability()
    internal.loc[
        internal["context"] == "BHLHE40_pDS258", "stability_class"
    ] = "method_sensitive"
    internal.loc[internal["context"] == "BHLHE40_pDS258", "n_state_preserved"] = 4
    internal.loc[internal["context"] == "BHLHE40_pDS258", "n_state_changed"] = 1

    integrated = integrate_external_responder_state_stability(
        internal,
        _external_claims("external_concordant_with_internal_supported_unit"),
    ).set_index("unit_id")

    row = integrated.loc["adamson_decision_benchmark::BHLHE40_pDS258"]
    assert row["integrated_cross_dataset_status"] == "external_same_context_unresolved"
    assert row["claim_ceiling"] == "replication_claim_blocked_by_unresolved_external_state"
    assert "internally unstable" in row["next_action"]


def test_external_responder_state_stability_blocked_state():
    integrated = integrate_external_responder_state_stability(
        _internal_stability(),
        _external_claims(
            "not_assessable",
            claim_state="blocked_by_external_execution_status",
        ),
    )
    summary = summarize_external_responder_state_stability(integrated)
    report = render_external_responder_state_stability_report(integrated, summary)

    assert set(integrated["integrated_cross_dataset_status"]) == {"external_same_context_blocked"}
    assert int(summary["n_units"].sum()) == 2
    assert "cannot support immune presentation" in report
    assert "computational replication language" in report


def test_external_responder_state_stability_requires_schema():
    with pytest.raises(ValueError, match="internal stability table is missing columns"):
        integrate_external_responder_state_stability(pd.DataFrame(), _external_claims("not_assessable"))
