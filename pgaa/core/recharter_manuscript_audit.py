"""Claim-safety audit for the PGAA recharter manuscript draft."""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


REQUIRED_READINESS_COLUMNS = {"check_id", "artifact", "status", "detail"}

REQUIRED_SECTIONS = (
    "## Draft Status",
    "## Title",
    "## Abstract Draft",
    "## Introduction Draft",
    "## Results Draft",
    "## Discussion Draft",
    "## Methods Draft",
    "## Still-Blocked Evidence",
    "## Forbidden Phrases For This Draft",
)

REQUIRED_REFERENCES = (
    "evidence/result_claim_states.tsv",
    "evidence/responder_state_units.tsv",
    "evidence/responder_state_stability_summary.tsv",
    "evidence/external_responder_state_stability_summary.tsv",
    "evidence/main_figure_source_data.tsv",
    "figures_png/figure1_recharter_decision_object.png",
    "docs/RECHARTER_READINESS_AUDIT.md",
)

REQUIRED_BOUNDARY_PHRASES = (
    "not yet a submission-ready manuscript",
    "Claim boundary",
)

FORBIDDEN_UNSUPPORTED_PHRASES = (
    "validated antigen",
    "immunogenic peptide validated by T cells",
    "same-context replicated responder state",
    "experimentally confirmed presentation",
    "synthetic peptide validation",
    "validated T-cell function",
)


@dataclass(frozen=True)
class ManuscriptAuditResult:
    audit: pd.DataFrame
    verdict: str


def _validate_readiness(readiness_audit: pd.DataFrame) -> None:
    missing = REQUIRED_READINESS_COLUMNS.difference(readiness_audit.columns)
    if missing:
        raise ValueError(f"readiness audit is missing columns: {sorted(missing)}")


def _without_forbidden_phrase_section(text: str) -> str:
    marker = "## Forbidden Phrases For This Draft"
    if marker not in text:
        return text
    before, _sep, _after = text.partition(marker)
    return before


def _row(check_id: str, status: str, severity: str, detail: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": status,
        "severity": severity,
        "detail": detail,
    }


def audit_recharter_manuscript_draft(
    draft_text: str,
    readiness_audit: pd.DataFrame,
) -> ManuscriptAuditResult:
    """Audit whether the manuscript draft preserves required claim boundaries."""
    _validate_readiness(readiness_audit)
    rows: list[dict[str, str]] = []

    for section in REQUIRED_SECTIONS:
        rows.append(
            _row(
                f"section:{section.removeprefix('## ').lower().replace(' ', '_')}",
                "pass" if section in draft_text else "fail",
                "error",
                f"required section {'present' if section in draft_text else 'missing'}: {section}",
            )
        )

    for reference in REQUIRED_REFERENCES:
        rows.append(
            _row(
                f"reference:{reference}",
                "pass" if reference in draft_text else "fail",
                "error",
                f"required evidence reference {'present' if reference in draft_text else 'missing'}: {reference}",
            )
        )

    for phrase in REQUIRED_BOUNDARY_PHRASES:
        rows.append(
            _row(
                f"boundary:{phrase}",
                "pass" if phrase in draft_text else "fail",
                "error",
                f"required claim-boundary phrase {'present' if phrase in draft_text else 'missing'}: {phrase}",
            )
        )

    same_context_boundary_ok = (
        "no_cross_dataset_same_context" in draft_text
        or (
            "external_same_context" in draft_text
            and "bounded computational" in draft_text
        )
    )
    rows.append(
        _row(
            "boundary:same_context_replication_ceiling",
            "pass" if same_context_boundary_ok else "fail",
            "error",
            (
                "same-context replication ceiling is explicit"
                if same_context_boundary_ok
                else "same-context replication ceiling is missing"
            ),
        )
    )

    body_text = _without_forbidden_phrase_section(draft_text)
    body_lower = body_text.lower()
    for phrase in FORBIDDEN_UNSUPPORTED_PHRASES:
        pattern = re.escape(phrase.lower()).replace("\\ ", r"\s+")
        unsupported_hits = len(re.findall(pattern, body_lower))
        rows.append(
            _row(
                f"unsupported_phrase:{phrase}",
                "pass" if unsupported_hits == 0 else "fail",
                "error",
                (
                    "unsupported phrase absent outside forbidden-phrase list"
                    if unsupported_hits == 0
                    else f"unsupported phrase appears {unsupported_hits} time(s) outside forbidden-phrase list"
                ),
            )
        )

    readiness_blockers = readiness_audit[readiness_audit["status"].astype(str) != "ready"]
    has_blockers = not readiness_blockers.empty
    blocker_statuses = sorted(readiness_blockers["status"].astype(str).unique())
    if has_blockers:
        consistency_ok = (
            "not yet a submission-ready manuscript" in draft_text
            and "## Still-Blocked Evidence" in draft_text
            and "readiness audit still" in draft_text
        )
        detail = (
            "readiness blockers are acknowledged in draft"
            if consistency_ok
            else f"readiness blockers are not adequately acknowledged: {blocker_statuses}"
        )
        rows.append(
            _row(
                "readiness_consistency:blocked",
                "pass" if consistency_ok else "fail",
                "error",
                detail,
            )
        )
    else:
        rows.append(
            _row(
                "readiness_consistency:ready",
                "pass",
                "info",
                "readiness audit reports all required artifacts ready",
            )
        )

    audit = pd.DataFrame(rows)
    if (audit["status"] == "fail").any():
        verdict = "CLAIM_AUDIT_FAIL"
    elif has_blockers:
        verdict = "CLAIM_SAFE_WITH_BLOCKERS"
    else:
        verdict = "CLAIM_SAFE_READY_FOR_STYLE_REVISION"
    return ManuscriptAuditResult(audit=audit, verdict=verdict)


def render_recharter_manuscript_audit(result: ManuscriptAuditResult) -> str:
    """Render a reviewer-facing manuscript claim-safety audit report."""
    audit = result.audit
    counts = audit["status"].value_counts().to_dict()
    lines = [
        "# PGAA Recharter Manuscript Draft Claim Audit",
        "",
        f"Verdict: `{result.verdict}`",
        "",
        "| Status | Rows |",
        "|---|---:|",
    ]
    for status in ("pass", "fail", "warning"):
        lines.append(f"| {status} | {int(counts.get(status, 0))} |")
    lines.extend(
        [
            "",
            "## Audit Rows",
            "",
            "| Check | Status | Severity | Detail |",
            "|---|---|---|---|",
        ]
    )
    for _, row in audit.iterrows():
        detail = str(row["detail"]).replace("|", "/")
        lines.append(
            f"| `{row['check_id']}` | {row['status']} | {row['severity']} | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if result.verdict == "CLAIM_AUDIT_FAIL":
        lines.append(
            "The draft is not claim-safe. Resolve failed rows before journal-style rewriting."
        )
    elif result.verdict == "CLAIM_SAFE_WITH_BLOCKERS":
        lines.append(
            "The draft preserves current claim boundaries, but it remains blocked for "
            "submission-readiness by missing real event/immune validation evidence."
        )
    else:
        lines.append(
            "The draft is claim-safe against the current audit and can proceed to style revision."
        )
    lines.append("")
    return "\n".join(lines)
