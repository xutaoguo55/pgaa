#!/usr/bin/env python3
"""Validate the Communications Medicine upload-file manifest."""
from __future__ import annotations

import csv
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "UPLOAD_FILE_MANIFEST.tsv"
CLEAN_ZIP = ROOT / "COMMUNICATIONS_MEDICINE_TRANSFER" / "PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip"
SUPP_CODE = (
    ROOT
    / "COMMUNICATIONS_MEDICINE_TRANSFER"
    / "JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE"
    / "PGAA_supplementary_code.zip"
)

REQUIRED_UPLOAD_FILES = {
    "COMMUNICATIONS_MEDICINE_TRANSFER/JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE/MANUSCRIPT.pdf",
    "COMMUNICATIONS_MEDICINE_TRANSFER/JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE/SUPPLEMENTARY.pdf",
    "COMMUNICATIONS_MEDICINE_TRANSFER/JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE/PGAA_supplementary_code.zip",
    "COMMUNICATIONS_MEDICINE_TRANSFER/JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE/COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
    "COMMUNICATIONS_MEDICINE_TRANSFER/PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip",
}

FORBIDDEN_ANYWHERE = [
    "COVER_LETTER_BIOINFORMATICS",
    "CURRENT_BIOINFORMATICS_REVIEW",
    "SIMULATED_BIOINFORMATICS_REVIEW",
    "POST_REVISION_BIOINFORMATICS_REVIEW",
    "REFERENCE_AUDIT_BIOINFORMATICS",
    "SUBMISSION_READINESS_AUDIT",
    "SUBMISSION_CHECKLIST",
    "figure_workflow",
    "Figure 6:",
    "Figure 7:",
]


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        raise SystemExit("Missing UPLOAD_FILE_MANIFEST.tsv")
    with MANIFEST.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required_columns = {"file", "role", "upload", "action", "notes"}
        if set(reader.fieldnames or []) != required_columns:
            raise SystemExit("UPLOAD_FILE_MANIFEST.tsv has unexpected columns")
        return list(reader)


def main() -> None:
    rows = read_manifest()
    errors: list[str] = []
    by_file = {row["file"]: row for row in rows}

    if len(by_file) != len(rows):
        errors.append("UPLOAD_FILE_MANIFEST.tsv contains duplicate file rows")

    manifest_text = MANIFEST.read_text(errors="replace")
    for term in FORBIDDEN_ANYWHERE:
        if term in manifest_text:
            errors.append(f"Manifest contains stale/internal term: {term}")

    for rel, row in by_file.items():
        path = ROOT / rel
        if row["upload"] in {"yes", "in_zip", "in_pdf"} and not path.exists():
            errors.append(f"Manifested file is missing: {rel}")
        if row["upload"] == "yes" and "AUDIT" in rel.upper():
            errors.append(f"Internal audit file marked upload=yes: {rel}")

    for rel in sorted(REQUIRED_UPLOAD_FILES):
        row = by_file.get(rel)
        if row is None:
            errors.append(f"Required CM upload file missing from manifest: {rel}")
        elif row["upload"] != "yes":
            errors.append(f"Required CM upload file not marked upload=yes: {rel}")

    if not CLEAN_ZIP.exists():
        errors.append("Missing PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip")
    else:
        with zipfile.ZipFile(CLEAN_ZIP) as zf:
            names = {Path(name).name for name in zf.namelist() if not name.endswith("/")}
        expected = {
            "MANUSCRIPT.pdf",
            "SUPPLEMENTARY.pdf",
            "PGAA_supplementary_code.zip",
            "COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
        }
        if names != expected:
            errors.append(f"Clean journal upload zip has unexpected files: {sorted(names)}")

    if not SUPP_CODE.exists():
        errors.append("Missing clean supplementary software archive")
    else:
        with zipfile.ZipFile(SUPP_CODE) as zf:
            names = zf.namelist()
        for term in [
            "COVER_LETTER_BIOINFORMATICS",
            "verify_cm_transfer_ready.py",
            "build_cm_journal_upload_packet.py",
            "build_cm_supplementary_zip.py",
        ]:
            hits = [name for name in names if term in name]
            if hits:
                errors.append(f"Supplementary software zip contains internal/stale entry: {hits[0]}")

    if errors:
        print("UPLOAD FILE MANIFEST CHECK FAILED")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    yes_count = sum(1 for row in rows if row["upload"] == "yes")
    print("UPLOAD FILE MANIFEST CHECK PASSED")
    print(f"Manifest rows: {len(rows)}; upload=yes files: {yes_count}")


if __name__ == "__main__":
    main()
