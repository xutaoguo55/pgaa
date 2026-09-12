import pandas as pd
import pytest

from pgaa.core.threshold_robustness import (
    apply_threshold_scenario,
    compare_threshold_robustness,
)


def _tier_table():
    return pd.DataFrame(
        [
            {
                "candidate_id": "exact_stable",
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "presentation_category": "presented-same-event",
                "presentation_source_count": 1,
                "presentation_best_match_type": "exact_peptide_or_junction",
                "binding_prediction_category": "not_assessed",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "tcell-recognized-exact-peptide",
                "tcell_source_count": 1,
                "candidate_match_rate": 0.8,
                "decoy_match_rate": 0.2,
                "integrated_tier": "A",
                "allowed_claim": "placeholder",
                "missing_evidence_flags": "none",
            },
            {
                "candidate_id": "overlap_sensitive",
                "peptide_sequence": "GILGFVFTL",
                "hla_allele": "HLA-A*02:01",
                "presentation_category": "presented-overlap",
                "presentation_source_count": 1,
                "presentation_best_match_type": "overlap_or_event_region",
                "binding_prediction_category": "not_assessed",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "no_tcell_evidence",
                "tcell_source_count": 0,
                "candidate_match_rate": 0.8,
                "decoy_match_rate": 0.2,
                "integrated_tier": "B",
                "allowed_claim": "placeholder",
                "missing_evidence_flags": "none",
            },
            {
                "candidate_id": "decoy_sensitive",
                "peptide_sequence": "LLFGYPVYV",
                "hla_allele": "HLA-A*02:01",
                "presentation_category": "presented-same-event",
                "presentation_source_count": 1,
                "presentation_best_match_type": "exact_peptide_or_junction",
                "binding_prediction_category": "not_assessed",
                "synthesis_category": "synthesis-ready",
                "tcell_category": "tcell-recognized-exact-peptide",
                "tcell_source_count": 1,
                "candidate_match_rate": 0.5,
                "decoy_match_rate": 0.5,
                "integrated_tier": "A",
                "allowed_claim": "placeholder",
                "missing_evidence_flags": "none",
            },
        ]
    )


def test_strict_exact_only_downgrades_overlap_evidence():
    adjusted = apply_threshold_scenario(_tier_table(), "strict_exact_only").set_index(
        "candidate_id"
    )

    assert adjusted.loc["exact_stable", "integrated_tier"] == "A"
    assert adjusted.loc["overlap_sensitive", "presentation_category"] == "binding-only"
    assert adjusted.loc["overlap_sensitive", "integrated_tier"] == "D"


def test_decoy_guarded_downgrades_public_evidence_not_above_decoys():
    adjusted = apply_threshold_scenario(_tier_table(), "decoy_guarded").set_index(
        "candidate_id"
    )

    assert adjusted.loc["exact_stable", "integrated_tier"] == "A"
    assert adjusted.loc["decoy_sensitive", "presentation_category"] == "binding-only"
    assert adjusted.loc["decoy_sensitive", "tcell_category"] == "no_tcell_evidence"
    assert adjusted.loc["decoy_sensitive", "integrated_tier"] == "D"


def test_compare_threshold_robustness_reports_default_ab_losses():
    _, summary = compare_threshold_robustness(_tier_table(), top_n=2)
    indexed = summary.set_index("threshold_scenario")

    assert indexed.loc["default", "tier_A_count"] == 2
    assert indexed.loc["strict_exact_only", "default_AB_lost"] == 1
    assert indexed.loc["decoy_guarded", "default_AB_lost"] == 1


def test_apply_threshold_scenario_rejects_unknown_scenario():
    with pytest.raises(ValueError, match="unknown threshold scenario"):
        apply_threshold_scenario(_tier_table(), "not_a_scenario")
