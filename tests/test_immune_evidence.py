import pandas as pd

from pgaa.core.immune_evidence import (
    annotate_public_evidence,
    build_immune_evidence_ladder,
    longest_hydrophobic_run,
    render_claim_audit_markdown,
    scan_placeholder_artifacts,
    summarize_immune_evidence,
    synthesis_category,
)


def test_synthesis_category_flags_length_and_hydrophobic_risk():
    category, flags = synthesis_category("AAAAAAAAAAAA", "I")
    assert category == "synthesis-risk"
    assert "hla_i_length_outside_8_11" in flags
    assert "long_hydrophobic_run" in flags


def test_synthesis_category_accepts_clean_hla_i_peptide():
    category, flags = synthesis_category("SLYNTVATL", "I")
    assert category == "synthesis-ready"
    assert flags == []
    assert longest_hydrophobic_run("AAVVVKLL") == 5


def test_build_immune_evidence_ladder_assigns_tiers_and_claims():
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "tier_a",
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "presentation_exact_count": 2,
                "binding_affinity_nm": 30,
                "tcell_exact_count": 1,
            },
            {
                "candidate_id": "tier_b",
                "peptide_sequence": "GILGFVFTL",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "presentation_overlap_count": 3,
                "binding_affinity_nm": 120,
                "tcell_exact_count": 0,
            },
            {
                "candidate_id": "tier_c",
                "peptide_sequence": "LLFGYPVYV",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "binding_percentile_rank": 1.0,
                "immune_context_score": 0.8,
            },
            {
                "candidate_id": "tier_d",
                "peptide_sequence": "AAAAAAAAAAAA",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "binding_percentile_rank": 0.1,
            },
        ]
    )

    tiers = build_immune_evidence_ladder(candidates).set_index("candidate_id")

    assert tiers.loc["tier_a", "integrated_tier"] == "A"
    assert tiers.loc["tier_a", "presentation_category"] == "presented-same-event"
    assert "no new wet-lab" in tiers.loc["tier_a", "allowed_claim"]
    assert tiers.loc["tier_b", "integrated_tier"] == "B"
    assert tiers.loc["tier_c", "integrated_tier"] == "C"
    assert tiers.loc["tier_c", "missing_evidence_flags"] == (
        "no_public_ligand;no_peptide_specific_tcell_function"
    )
    assert tiers.loc["tier_d", "integrated_tier"] == "D"
    assert "synthesis-risk" in tiers.loc["tier_d", "missing_evidence_flags"]


def test_annotate_public_evidence_counts_exact_overlap_and_decoys():
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "exact",
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
            },
            {
                "candidate_id": "overlap",
                "peptide_sequence": "GILGFVFTL",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
            },
        ]
    )
    ligand = pd.DataFrame(
        [
            {
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "source_id": "ligand_exact",
            },
            {
                "peptide_sequence": "XXGILGFVFTLXX",
                "hla_allele": "HLA-A*02",
                "source_id": "ligand_overlap",
            },
        ]
    )
    tcell = pd.DataFrame(
        [
            {
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "source_id": "tcell_exact",
            }
        ]
    )
    decoys = pd.DataFrame(
        [
            {"peptide_sequence": "AAAAAAAAA", "hla_allele": "HLA-A*02:01"},
            {"peptide_sequence": "GILGFVFTL", "hla_allele": "HLA-A*02:01"},
        ]
    )

    annotated = annotate_public_evidence(candidates, ligand, tcell, decoys)
    indexed = annotated.set_index("candidate_id")

    assert indexed.loc["exact", "presentation_exact_count"] == 1
    assert indexed.loc["exact", "tcell_exact_count"] == 1
    assert indexed.loc["overlap", "presentation_overlap_count"] == 1
    assert indexed.loc["exact", "candidate_match_rate"] == 1.0
    assert indexed.loc["overlap", "decoy_match_rate"] == 0.5

    tiers = build_immune_evidence_ladder(annotated).set_index("candidate_id")
    assert tiers.loc["exact", "integrated_tier"] == "A"
    assert tiers.loc["overlap", "integrated_tier"] == "B"


def test_claim_audit_summarizes_tiers_without_validation_overclaim():
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "tier_a",
                "peptide_sequence": "SLYNTVATL",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "presentation_exact_count": 1,
                "tcell_exact_count": 1,
            },
            {
                "candidate_id": "tier_d",
                "peptide_sequence": "AAAAAAAAAAAA",
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
            },
        ]
    )
    tiers = build_immune_evidence_ladder(candidates)

    summary = summarize_immune_evidence(tiers)
    report = render_claim_audit_markdown(tiers)

    assert summary["total_candidates"] == 2
    assert summary["tier_counts"] == {"A": 1, "D": 1}
    assert summary["exact_presentation_count"] == 1
    assert "public-data-supported prioritization" in summary["headline_claim"]
    assert "validated antigen" in report
    assert "does not provide new wet-lab" in report


def test_claim_audit_prioritizes_failed_decoy_gate_over_tier_a():
    tiers = pd.DataFrame(
        [
            {
                "candidate_id": "tier_a_with_weak_background_control",
                "presentation_category": "presented-same-event",
                "tcell_category": "tcell-recognized-exact-peptide",
                "integrated_tier": "A",
                "candidate_match_rate": 1.0,
                "decoy_match_rate": 1.0,
                "missing_evidence_flags": "none",
            }
        ]
    )

    summary = summarize_immune_evidence(tiers)
    report = render_claim_audit_markdown(tiers)

    assert summary["decoy_guard_status"] == "failed_candidate_not_above_decoy"
    assert "enrichment is not supported" in summary["headline_claim"]
    assert "failed_candidate_not_above_decoy" in report


def test_placeholder_scan_flags_smoke_and_template_tokens():
    table = pd.DataFrame(
        [
            {
                "candidate_id": "SMOKE_exact",
                "peptide_sequence": "PEPTIDEX",
                "notes": "REPLACE_WITH_REAL_SOURCE",
            }
        ]
    )

    hits = scan_placeholder_artifacts(table, "candidates")

    assert any("SMOKE" in hit for hit in hits)
    assert any("PEPTIDEX" in hit for hit in hits)
    assert any("REPLACE_WITH" in hit for hit in hits)
