from pathlib import Path

import pandas as pd

from pgaa.core.recharter_readiness import (
    READINESS_CHECKS,
    audit_recharter_readiness,
    readiness_verdict,
    render_readiness_markdown,
)


def _write_table(root: Path, artifact: str, columns: tuple[str, ...], prefix: str) -> None:
    path = root / artifact
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {}
    for idx, column in enumerate(columns):
        if column == "peptide_sequence":
            row[column] = "SLYNTVATL"
        elif column == "event_index":
            row[column] = 8
        elif column == "event_position_in_peptide":
            row[column] = 4
        elif column == "pgaa_rank":
            row[column] = 1
        elif column == "jaccard_with_full_ladder":
            row[column] = 1.0
        elif column == "default_AB_lost":
            row[column] = 0
        else:
            row[column] = f"{prefix}_{idx}"
    pd.DataFrame([row]).to_csv(path, sep="\t", index=False)


def _write_ready_artifacts(root: Path) -> None:
    for check in READINESS_CHECKS:
        path = root / check.artifact
        if check.required_columns:
            _write_table(root, check.artifact, check.required_columns, check.check_id)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Real claim audit\n\nNo prohibited validation claims.\n", encoding="utf-8")


def test_readiness_audit_marks_missing_real_artifacts_as_not_ready(tmp_path):
    audit = audit_recharter_readiness(tmp_path)

    assert set(audit["status"]) == {"missing"}
    assert readiness_verdict(audit) == "NOT_READY_REAL_EVIDENCE_MISSING"


def test_readiness_audit_accepts_complete_non_smoke_artifacts(tmp_path):
    _write_ready_artifacts(tmp_path)

    audit = audit_recharter_readiness(tmp_path)

    assert set(audit["status"]) == {"ready"}
    assert readiness_verdict(audit) == "READY_FOR_RECHARTER_MANUSCRIPT_DRAFT"
    assert "READY_FOR_RECHARTER_MANUSCRIPT_DRAFT" in render_readiness_markdown(audit)


def test_readiness_audit_rejects_smoke_or_template_rows(tmp_path):
    _write_ready_artifacts(tmp_path)
    candidate_path = tmp_path / "evidence/candidate_event_peptides.tsv"
    candidates = pd.read_csv(candidate_path, sep="\t")
    candidates.loc[0, "candidate_id"] = "SMOKE_candidate"
    candidates.to_csv(candidate_path, sep="\t", index=False)

    audit = audit_recharter_readiness(tmp_path)
    indexed = audit.set_index("check_id")

    assert indexed.loc["real_candidate_peptides", "status"] == "smoke_or_template"
    assert readiness_verdict(audit) == "PARTIAL_INFRASTRUCTURE_READY_REAL_EVIDENCE_INCOMPLETE"


def test_readiness_audit_rejects_incomplete_tables(tmp_path):
    _write_ready_artifacts(tmp_path)
    ligand_path = tmp_path / "evidence/public_ligand_evidence.tsv"
    pd.DataFrame([{"source_id": "real_source"}]).to_csv(ligand_path, sep="\t", index=False)

    audit = audit_recharter_readiness(tmp_path)
    indexed = audit.set_index("check_id")

    assert indexed.loc["real_ligand_evidence", "status"] == "incomplete"
    assert "missing columns" in indexed.loc["real_ligand_evidence", "detail"]
