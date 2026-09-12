import pandas as pd

from pgaa.core.recharter_manuscript_audit import (
    audit_recharter_manuscript_draft,
    render_recharter_manuscript_audit,
)


def _readiness(status: str = "missing") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "check_id": "real_event_contexts",
                "artifact": "evidence/event_sequence_contexts.tsv",
                "status": status,
                "detail": "artifact is missing" if status != "ready" else "artifact exists",
            }
        ]
    )


def _safe_draft() -> str:
    return "\n".join(
        [
            "# PGAA Recharter Manuscript Draft",
            "",
            "## Draft Status",
            "This is not yet a submission-ready manuscript because the readiness audit still blocks immune claims.",
            "## Title",
            "A failure-preserving benchmark engine",
            "## Abstract Draft",
            "Claim boundary language is preserved.",
            "## Introduction Draft",
            "Evidence is compiled conservatively.",
            "## Results Draft",
            "Evidence source: `evidence/result_claim_states.tsv`.",
            "Evidence source: `evidence/responder_state_units.tsv`.",
            "Evidence source: `evidence/responder_state_stability_summary.tsv`.",
            "Evidence source: `evidence/external_responder_state_stability_summary.tsv`.",
            "Evidence source: `evidence/main_figure_source_data.tsv`.",
            "Evidence source: `figures_png/figure1_recharter_decision_object.png`.",
            "Evidence source: `docs/RECHARTER_READINESS_AUDIT.md`.",
            "All stability rows are `no_cross_dataset_same_context`.",
            "## Discussion Draft",
            "The current claim ceiling remains explicit.",
            "## Methods Draft",
            "Tables are generated from source artifacts.",
            "## Still-Blocked Evidence",
            "Missing real immune artifacts remain blocked.",
            "## Forbidden Phrases For This Draft",
            "- validated antigen",
            "- immunogenic peptide validated by T cells",
            "- same-context replicated responder state",
            "- experimentally confirmed presentation",
            "- synthetic peptide validation",
            "- validated T-cell function",
        ]
    )


def test_recharter_manuscript_audit_accepts_claim_safe_blocked_draft():
    result = audit_recharter_manuscript_draft(_safe_draft(), _readiness())

    assert result.verdict == "CLAIM_SAFE_WITH_BLOCKERS"
    assert set(result.audit["status"]) == {"pass"}
    assert "CLAIM_SAFE_WITH_BLOCKERS" in render_recharter_manuscript_audit(result)


def test_recharter_manuscript_audit_fails_unsupported_phrase_in_body():
    draft = _safe_draft().replace(
        "Claim boundary language is preserved.",
        "This workflow identifies a validated antigen.",
    )

    result = audit_recharter_manuscript_draft(draft, _readiness())

    assert result.verdict == "CLAIM_AUDIT_FAIL"
    failed = result.audit[result.audit["status"] == "fail"]
    assert any("unsupported_phrase:validated antigen" == row for row in failed["check_id"])


def test_recharter_manuscript_audit_fails_missing_required_section():
    draft = _safe_draft().replace("## Still-Blocked Evidence", "## Blockers")

    result = audit_recharter_manuscript_draft(draft, _readiness())

    assert result.verdict == "CLAIM_AUDIT_FAIL"
    assert any("section:still-blocked_evidence" in row for row in result.audit["check_id"])
