import pandas as pd
import pytest

from pgaa.core.panel_design import add_panel_scores, compare_followup_panels, select_panel


def _tier_table():
    return pd.DataFrame(
        [
            {
                "candidate_id": "high_pgaa_weak_evidence",
                "pgaa_rank": 1,
                "integrated_tier": "D",
                "presentation_category": "binding-only",
                "binding_prediction_category": "predicted_binding",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "no_tcell_evidence",
            },
            {
                "candidate_id": "tier_a_public_support",
                "pgaa_rank": 5,
                "integrated_tier": "A",
                "presentation_category": "presented-same-event",
                "binding_prediction_category": "not_assessed",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "tcell-recognized-exact-peptide",
            },
            {
                "candidate_id": "binding_only_candidate",
                "pgaa_rank": 2,
                "integrated_tier": "C",
                "presentation_category": "binding-only",
                "binding_prediction_category": "strong_predicted_binding",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "immune-context-support",
            },
        ]
    )


def test_add_panel_scores_prioritizes_full_ladder_evidence():
    scored = add_panel_scores(_tier_table()).set_index("candidate_id")

    assert (
        scored.loc["tier_a_public_support", "full_ladder_panel_score"]
        > scored.loc["high_pgaa_weak_evidence", "full_ladder_panel_score"]
    )


def test_compare_followup_panels_quantifies_decision_difference():
    panel, summary = compare_followup_panels(_tier_table(), top_n=1)
    full_top = panel[panel["selection_method"] == "full_ladder"].iloc[0]
    pgaa_top = panel[panel["selection_method"] == "pgaa_rank"].iloc[0]
    pgaa_summary = summary.set_index("comparison_method").loc["pgaa_rank"]

    assert full_top["candidate_id"] == "tier_a_public_support"
    assert pgaa_top["candidate_id"] == "high_pgaa_weak_evidence"
    assert pgaa_summary["jaccard_with_full_ladder"] == 0.0
    assert pgaa_summary["missed_by_method_vs_full_ladder"] == 1


def test_select_panel_rejects_missing_score_column():
    with pytest.raises(ValueError, match="missing score column"):
        select_panel(_tier_table(), "not_a_score", top_n=1)


def test_compare_followup_panels_rejects_nonpositive_top_n():
    with pytest.raises(ValueError, match="top_n must be positive"):
        compare_followup_panels(_tier_table(), top_n=0)
