import pandas as pd
import pytest

from pgaa.core.external_dataset_candidates import (
    audit_external_dataset_candidates,
    render_external_dataset_candidate_report,
    summarize_external_dataset_candidates,
)


def _opportunities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "unit_id": "adamson::BHLHE40_pDS258",
                "target_gene": "BHLHE40",
                "evidence_type": "adamson_decision_benchmark",
                "validation_priority": "tier1_replication_candidate",
                "preferred_external_modality": "independent K562 CRISPRi screen",
            },
            {
                "unit_id": "adamson::SPI1_pDS255",
                "target_gene": "SPI1",
                "evidence_type": "adamson_decision_benchmark",
                "validation_priority": "tier2_dependency_stress_test",
                "preferred_external_modality": "independent K562 CRISPRi screen",
            },
            {
                "unit_id": "norman::CEBPE",
                "target_gene": "CEBPE",
                "evidence_type": "norman_decision_benchmark",
                "validation_priority": "tier3_provisional_state_test",
                "preferred_external_modality": "independent K562 CRISPRa screen",
            },
        ]
    )


def _candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_dataset_id": "replogle_2022_k562_gwps",
                "source_name": "Replogle K562 genome-wide",
                "accession_or_url": "https://example.org/replogle",
                "cell_context": "K562",
                "perturbation_modality": "CRISPRi Perturb-seq",
                "candidate_scope": "genome_scale_single_cell_candidate",
                "data_access_status": "download_page_identified_metadata_check_required",
                "target_coverage_status": "unverified",
                "raw_single_cell_status": "raw_or_processed_single_cell_available",
                "source_note": "metadata check required",
            },
            {
                "candidate_dataset_id": "processed_signatures",
                "source_name": "Processed signatures",
                "accession_or_url": "manual",
                "cell_context": "mixed_or_unspecified",
                "perturbation_modality": "mixed_or_unspecified",
                "candidate_scope": "processed_signature_or_index_only",
                "data_access_status": "summary_or_index_only",
                "target_coverage_status": "unverified",
                "raw_single_cell_status": "not_raw_single_cell",
                "source_note": "not rerunnable",
            },
        ]
    )


def test_genome_wide_k562_crispri_candidate_requires_metadata_check():
    audit = audit_external_dataset_candidates(_opportunities(), _candidates())
    replogle = audit[
        (audit["target_gene"] == "BHLHE40")
        & (audit["candidate_dataset_id"] == "replogle_2022_k562_gwps")
    ].iloc[0]

    assert replogle["same_context_class"] == "same_context_candidate_metadata_required"
    assert replogle["claim_use"] == "candidate_for_metadata_verification_not_replication"
    assert "metadata" in replogle["required_next_check"]


def test_processed_signature_source_is_not_pgaa_rerunnable():
    audit = audit_external_dataset_candidates(_opportunities(), _candidates())
    processed = audit[audit["candidate_dataset_id"] == "processed_signatures"].iloc[0]

    assert processed["same_context_class"] == "processed_signature_or_index_only"
    assert processed["pgaa_rerun_feasibility"] == "not_pgaa_rerunnable"
    assert processed["claim_use"] == "source_discovery_only_not_replication"


def test_candidate_report_states_not_replication_evidence():
    audit = audit_external_dataset_candidates(_opportunities(), _candidates())
    summary = summarize_external_dataset_candidates(audit)
    report = render_external_dataset_candidate_report(audit, summary)

    assert int(summary["n_target_candidate_pairs"].sum()) == 4
    assert "not replication evidence" in report
    assert "Target-Verified Import Candidates" in report
    assert "metadata verification and import" in report


def test_candidate_manifest_schema_is_required():
    candidates = _candidates().drop(columns=["raw_single_cell_status"])
    with pytest.raises(ValueError, match="candidate manifest is missing columns"):
        audit_external_dataset_candidates(_opportunities(), candidates)
