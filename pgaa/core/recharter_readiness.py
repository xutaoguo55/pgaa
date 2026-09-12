"""Go/no-go readiness audit for the PGAA top-journal recharter."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pgaa.core.immune_evidence import scan_placeholder_artifacts


@dataclass(frozen=True)
class ReadinessCheck:
    check_id: str
    artifact: str
    requirement: str
    required_columns: tuple[str, ...] = ()
    min_rows: int = 1


READINESS_CHECKS = (
    ReadinessCheck(
        "real_event_contexts",
        "evidence/event_sequence_contexts.tsv",
        "Real altered sequence contexts exist for event-to-peptide compilation.",
        (
            "source_event_id",
            "altered_sequence_context",
            "event_index",
            "hla_allele",
            "hla_class",
            "pgaa_rank",
        ),
    ),
    ReadinessCheck(
        "real_candidate_peptides",
        "evidence/candidate_event_peptides.tsv",
        "Compiled non-smoke event-peptide-HLA candidates exist.",
        (
            "candidate_id",
            "source_event_id",
            "peptide_sequence",
            "event_position_in_peptide",
            "hla_allele",
            "pgaa_rank",
        ),
    ),
    ReadinessCheck(
        "real_ligand_evidence",
        "evidence/public_ligand_evidence.tsv",
        "Public ligand/immunopeptidome evidence query output exists.",
        ("peptide_sequence",),
    ),
    ReadinessCheck(
        "real_tcell_evidence",
        "evidence/public_tcell_evidence.tsv",
        "Public T-cell evidence query output exists.",
        ("peptide_sequence",),
    ),
    ReadinessCheck(
        "real_decoys",
        "evidence/decoy_peptides.tsv",
        "Matched decoy peptide table exists.",
        ("peptide_sequence",),
    ),
    ReadinessCheck(
        "real_tier_table",
        "evidence/immune_evidence_tiers.tsv",
        "Real immune-evidence tier table exists.",
        (
            "candidate_id",
            "presentation_category",
            "tcell_category",
            "integrated_tier",
            "allowed_claim",
        ),
    ),
    ReadinessCheck(
        "real_claim_audit",
        "docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md",
        "Claim audit exists for real candidate evidence.",
    ),
    ReadinessCheck(
        "real_panel_summary",
        "evidence/followup_panel_summary.tsv",
        "Decision-impact panel summary exists for real tiers.",
        ("comparison_method", "jaccard_with_full_ladder"),
    ),
    ReadinessCheck(
        "real_threshold_summary",
        "evidence/threshold_robustness_summary.tsv",
        "Threshold robustness summary exists for real tiers.",
        ("threshold_scenario", "default_AB_lost"),
    ),
)


def _audit_one(root: Path, check: ReadinessCheck) -> dict[str, object]:
    path = root / check.artifact
    if not path.exists():
        return {
            "check_id": check.check_id,
            "artifact": check.artifact,
            "status": "missing",
            "row_count": 0,
            "requirement": check.requirement,
            "detail": "artifact is missing",
        }

    if path.suffix.lower() in {".tsv", ".csv"}:
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        table = pd.read_csv(path, sep=sep)
        missing_columns = [column for column in check.required_columns if column not in table.columns]
        placeholder_hits = scan_placeholder_artifacts(table, check.check_id)
        if missing_columns:
            status = "incomplete"
            detail = f"missing columns: {missing_columns}"
        elif len(table) < check.min_rows:
            status = "incomplete"
            detail = f"row count {len(table)} is below required {check.min_rows}"
        elif placeholder_hits:
            status = "smoke_or_template"
            detail = "; ".join(placeholder_hits[:5])
        else:
            status = "ready"
            detail = "artifact exists, required columns present, no smoke/template tokens detected"
        return {
            "check_id": check.check_id,
            "artifact": check.artifact,
            "status": status,
            "row_count": int(len(table)),
            "requirement": check.requirement,
            "detail": detail,
        }

    text = path.read_text(encoding="utf-8")
    upper = text.upper()
    hits = [pattern for pattern in ("SMOKE", "PEPTIDEX", "REPLACE_WITH", "EXAMPLE_") if pattern in upper]
    status = "smoke_or_template" if hits else "ready"
    detail = f"placeholder tokens detected: {hits}" if hits else "artifact exists"
    return {
        "check_id": check.check_id,
        "artifact": check.artifact,
        "status": status,
        "row_count": 1,
        "requirement": check.requirement,
        "detail": detail,
    }


def audit_recharter_readiness(root: Path) -> pd.DataFrame:
    """Audit whether real non-smoke recharter evidence is ready."""
    rows = [_audit_one(root, check) for check in READINESS_CHECKS]
    return pd.DataFrame(rows)


def readiness_verdict(audit: pd.DataFrame) -> str:
    """Return a conservative manuscript-readiness verdict."""
    statuses = set(audit["status"])
    if statuses == {"ready"}:
        return "READY_FOR_RECHARTER_MANUSCRIPT_DRAFT"
    if "ready" in statuses:
        return "PARTIAL_INFRASTRUCTURE_READY_REAL_EVIDENCE_INCOMPLETE"
    return "NOT_READY_REAL_EVIDENCE_MISSING"


def render_readiness_markdown(audit: pd.DataFrame) -> str:
    """Render a reviewer-facing go/no-go audit report."""
    verdict = readiness_verdict(audit)
    lines = [
        "# PGAA Recharter Readiness Audit",
        "",
        f"Verdict: `{verdict}`",
        "",
        "| Check | Status | Artifact | Detail |",
        "|---|---|---|---|",
    ]
    for _, row in audit.iterrows():
        detail = str(row["detail"]).replace("|", "/")
        lines.append(
            f"| {row['check_id']} | {row['status']} | `{row['artifact']}` | {detail} |"
        )
    blockers = audit[audit["status"] != "ready"]
    lines.extend(
        [
            "",
            "## Blocking Interpretation",
            "",
        ]
    )
    if blockers.empty:
        lines.append("All required real artifacts are present and free of smoke/template tokens.")
    else:
        lines.append(
            "The rechartered top-journal manuscript is not ready while any row above is "
            "`missing`, `incomplete`, or `smoke_or_template`."
        )
    lines.extend(
        [
            "",
            "This audit checks artifact readiness only. It does not prove biological validity, "
            "wet-lab validation, or journal acceptance.",
            "",
        ]
    )
    return "\n".join(lines)
