import pandas as pd

from pgaa.core.multilevel_decoy import (
    build_multilevel_decoys,
    compare_multilevel_decoy_enrichment,
    multilevel_decoy_verdict,
    render_multilevel_decoy_audit,
)


def _candidates():
    return pd.DataFrame(
        [
            {"candidate_id": "c1", "source_event_id": "e1", "source_gene": "G1", "peptide_sequence": "SLYNTVATL", "peptide_length": 9, "hla_allele": "HLA-A*02:01", "hla_class": "I"},
            {"candidate_id": "c2", "source_event_id": "e2", "source_gene": "G2", "peptide_sequence": "GILGFVFTL", "peptide_length": 9, "hla_allele": "HLA-A*02:01", "hla_class": "I"},
        ]
    )


def test_multilevel_decoys_preserve_matching_constraints():
    decoys = build_multilevel_decoys(_candidates())
    assert set(decoys["decoy_type"]) == {
        "composition_matched_shuffle",
        "cross_event_length_class_matched",
    }
    assert set(decoys["peptide_length"]) == {9}
    assert len(decoys) == 4


def test_enrichment_is_stratified_by_decoy_type():
    candidates = _candidates()
    decoys = build_multilevel_decoys(candidates)
    ligand = pd.DataFrame([{"peptide_sequence": "SLYNTVATL", "hla_allele": "HLA-A*02:01"}])
    tcell = pd.DataFrame(columns=["peptide_sequence", "hla_allele"])
    summary = compare_multilevel_decoy_enrichment(candidates, decoys, ligand, tcell)
    assert set(summary["group"]) == {
        "candidate",
        "composition_matched_shuffle",
        "cross_event_length_class_matched",
    }
    assert summary.set_index("group").loc["candidate", "match_rate"] == 0.5
    assert "decoy_gate" in summary.columns


def test_mixed_decoy_results_block_global_enrichment_claim():
    summary = pd.DataFrame(
        [
            {"group": "candidate", "hit_count": 10, "total_count": 10, "match_rate": 1.0, "decoy_gate": "reference_candidate_group", "fisher_p_value": 1.0},
            {"group": "easy", "hit_count": 0, "total_count": 10, "match_rate": 0.0, "decoy_gate": "passed_candidate_above_decoy", "fisher_p_value": 0.001},
            {"group": "hard", "hit_count": 10, "total_count": 10, "match_rate": 1.0, "decoy_gate": "failed_candidate_not_above_decoy", "fisher_p_value": 1.0},
        ]
    )

    assert multilevel_decoy_verdict(summary) == "MIXED_DECOY_SENSITIVITY_NO_GLOBAL_ENRICHMENT_CLAIM"
    assert "blocks a global enrichment claim" in render_multilevel_decoy_audit(summary)
