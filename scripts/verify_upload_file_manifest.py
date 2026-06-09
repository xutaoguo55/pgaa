#!/usr/bin/env python3
"""Validate the Bioinformatics upload-file manifest."""
from __future__ import annotations

import csv
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "UPLOAD_FILE_MANIFEST.tsv"
ZIP_PATH = ROOT / "PGAA_supplementary_code.zip"

FORBIDDEN_UPLOAD_TERMS = [
    "figure_workflow",
    "CURRENT_BIOINFORMATICS_REVIEW",
    "SIMULATED_BIOINFORMATICS_REVIEW",
    "POST_REVISION_BIOINFORMATICS_REVIEW",
    "REFERENCE_AUDIT",
    "SUBMISSION_READINESS_AUDIT",
    "SUBMISSION_CHECKLIST",
    "mmd_psm",
]

REQUIRED_UPLOAD_FILES = {
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_BIOINFORMATICS.md",
    "PORTAL_INPUTS.md",
    "figures_png/figure_1.png",
    "figures_png/figure_2.png",
    "figures_png/figure_elane_histogram.png",
    "figures_png/figure_3.png",
    "figures_png/figure_4.png",
    "figures_png/figure_adamson_benchmark.png",
    "figures_png/figure_5.png",
    "figures_png/figure_s2_calibration_qq.png",
    "figures_png/figure_s2_bhlhe40.png",
    "figures_png/figure_pgaa_workflow.png",
}


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

    for rel, row in by_file.items():
        path = ROOT / rel
        if row["upload"] in {"yes", "in_zip"} and not path.exists():
            errors.append(f"Manifested required file is missing: {rel}")
        if row["upload"] == "yes" and any(term in rel for term in FORBIDDEN_UPLOAD_TERMS):
            errors.append(f"Forbidden internal/deprecated file marked for upload: {rel}")

    for rel in sorted(REQUIRED_UPLOAD_FILES):
        row = by_file.get(rel)
        if row is None:
            errors.append(f"Required upload file missing from manifest: {rel}")
        elif row["upload"] != "yes":
            errors.append(f"Required upload file not marked upload=yes: {rel}")

    deprecated = by_file.get("figures_png/figure_workflow.png")
    if deprecated is None or deprecated["upload"] != "no":
        errors.append("Deprecated figures_png/figure_workflow.png must be marked upload=no")

    if not ZIP_PATH.exists():
        errors.append("Missing PGAA_supplementary_code.zip")
    else:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            names = zf.namelist()
        for term in FORBIDDEN_UPLOAD_TERMS:
            hits = [name for name in names if term in name]
            if hits:
                errors.append(f"Supplementary software zip contains forbidden entry: {hits[0]}")

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
