import pandas as pd
import pytest

from pgaa.core.figure1_text import (
    render_figure1_caption_and_results,
    summarize_figure1_text_inputs,
)


def _sources() -> pd.DataFrame:
    rows = []
    base = {
        "figure_id": "Figure 1",
        "source_kind": "",
        "context": "",
        "stability_class": "",
        "cross_dataset_status": "",
        "secondary_value": "",
        "label": "",
        "n_methods": "",
        "n_comparative_support": "",
        "n_descriptive_only": "",
        "n_failure_or_guardrail": "",
    }
    for state, value in [
        ("comparative_support", 2),
        ("descriptive_only", 1),
        ("failure_or_guardrail", 3),
    ]:
        rows.append(
            {
                **base,
                "panel_id": "A_claim_state_distribution",
                "state": state,
                "x_group": "decision_benchmark",
                "y_value": value,
            }
        )
    for state, context, stability, preserved, changed in [
        ("supported_responder_state", "A", "leave_one_method_stable", 5, 0),
        ("provisional_responder_state", "B", "method_sensitive", 3, 1),
    ]:
        rows.append(
            {
                **base,
                "panel_id": "B_responder_state_units",
                "state": state,
                "context": context,
                "stability_class": stability,
                "cross_dataset_status": "no_cross_dataset_same_context",
                "x_group": "adamson_decision_benchmark",
                "y_value": 0.8,
                "secondary_value": 0.1,
            }
        )
        rows.append(
            {
                **base,
                "panel_id": "C_unit_stability",
                "state": state,
                "context": context,
                "stability_class": stability,
                "cross_dataset_status": "no_cross_dataset_same_context",
                "x_group": stability,
                "y_value": preserved,
                "secondary_value": changed,
            }
        )
    return pd.DataFrame(rows)


def test_figure1_text_summary_counts_inputs():
    summary = summarize_figure1_text_inputs(_sources())

    assert summary["n_source_rows"] == 7
    assert summary["claim_counts"]["comparative_support"] == 2
    assert summary["responder_counts"]["supported_responder_state"] == 1
    assert summary["stability_counts"]["method_sensitive"] == 1
    assert summary["n_no_same_context_replication"] == 2


def test_figure1_text_is_claim_bounded():
    text = render_figure1_caption_and_results(_sources())

    assert "does not claim same-context cross-dataset replication" in text
    assert "not as replicated responder-state discoveries" in text
    assert "immune presentation" in text


def test_figure1_text_reports_typed_external_states_and_base_stability():
    sources = _sources()
    panel_c = sources["panel_id"] == "C_unit_stability"
    indices = sources.index[panel_c].tolist()
    sources.loc[indices[0], "stability_class"] = (
        "leave_one_method_stable_external_concordant"
    )
    sources.loc[indices[0], "cross_dataset_status"] = (
        "external_same_context_concordant"
    )
    sources.loc[indices[1], "stability_class"] = "method_sensitive_external_blocked"
    sources.loc[indices[1], "cross_dataset_status"] = "external_same_context_blocked"

    summary = summarize_figure1_text_inputs(sources)
    text = render_figure1_caption_and_results(sources)

    assert summary["stability_counts"]["leave_one_method_stable"] == 1
    assert summary["stability_counts"]["method_sensitive"] == 1
    assert summary["n_external_same_context_concordant"] == 1
    assert summary["n_external_same_context_blocked"] == 1
    assert "typed external gate classifies 1 units as concordant, 1 as blocked" in text
    assert "bounded computational same-context replication only" in text
    assert "does not establish biological validation" in text


def test_figure1_text_requires_schema():
    with pytest.raises(ValueError, match="main-figure source table is missing columns"):
        summarize_figure1_text_inputs(pd.DataFrame({"x": [1]}))
