#!/usr/bin/env python3
"""Verify dataset accession and reproduction metadata for the PGAA package."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "DATASET_MANIFEST.tsv"
# The files that define what this package cites. Four of the five paths listed here
# before 2026-09-13 (communications_ai_computing/ and communications_medicine/)
# do not exist, and accessions_in_text() skipped missing files silently, so the gate
# was checking README.md alone while reporting that it checked the manuscripts --
# which is why GSE103350, GSE150949, and GSE335848 were cited but unlisted. A
# declared source that is missing is now an error, not a silent loss of coverage.
TEXT_SOURCES = [
    ROOT / "MANUSCRIPT.md",
    ROOT / "SUPPLEMENTARY.md",
    ROOT / "README.md",
    ROOT / "docs" / "SUBMISSION_PACKAGE_INDEX.md",
    ROOT / "docs" / "PC9_THIRD_SYSTEM_BLOCKER_AUDIT.md",
    ROOT / "docs" / "PUBLICATION_GAP_AUDIT.md",
]
REQUIRED_COLUMNS = [
    "dataset_id",
    "display_name",
    "accession_or_source",
    "public_landing_page",
    "data_type",
    "analysis_role",
    "evidence_level",
    "cells_used",
    "primary_manuscript_items",
    "raw_data_status",
    "included_source_files",
    "rebuild_commands",
    "limitations",
]
NA_ALLOWED_COLUMNS = {"included_source_files", "rebuild_commands"}
EXPECTED_ACCESSIONS = {
    "GSE133344",
    "GSE90546",
    "GSE111014",
    "GSE167363",
    "GSE159117",
    "GSE116222",
    # Added 2026-09-13: all three were cited by the manuscript or supplementary text
    # while being absent from the manifest, so the text scan is now backed by an
    # explicit list that survives a change to TEXT_SOURCES.
    "GSE103350",
    "GSE150949",
    "GSE335848",
}


def accessions_in_text() -> set[str]:
    found: set[str] = set()
    for path in TEXT_SOURCES:
        if path.exists():
            found.update(re.findall(r"GSE\d+", path.read_text(errors="replace")))
    return found


def check_manifest() -> list[str]:
    errors: list[str] = []
    for path in TEXT_SOURCES:
        if not path.exists():
            errors.append(
                f"Declared text source is missing: {path.relative_to(ROOT)}"
            )
    if not MANIFEST.exists():
        return errors + ["Missing DATASET_MANIFEST.tsv"]
    df = pd.read_csv(MANIFEST, sep="\t").fillna("")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"DATASET_MANIFEST.tsv missing columns: {missing_cols}")
        return errors

    if df["dataset_id"].duplicated().any():
        dup = sorted(df.loc[df["dataset_id"].duplicated(), "dataset_id"].unique())
        errors.append(f"Duplicate dataset_id entries: {dup}")

    manifest_accessions = set(df["accession_or_source"])
    for acc in sorted(EXPECTED_ACCESSIONS | accessions_in_text()):
        if acc not in manifest_accessions:
            errors.append(f"Accession {acc} is referenced but missing from manifest")

    if "10x Genomics PBMC 3k demo" not in manifest_accessions:
        errors.append("10x Genomics PBMC 3k demo source is missing from manifest")

    for _, row in df.iterrows():
        dataset_id = row["dataset_id"]
        for col in REQUIRED_COLUMNS:
            # "NA" is the sentinel for a field that legitimately has nothing to list;
            # pandas reads it as NaN, so it arrives here as "". The included-files loop
            # below already skips a literal "NA", which is only reachable once the
            # emptiness check stops rejecting the row first.
            if not str(row[col]).strip() and col not in NA_ALLOWED_COLUMNS:
                errors.append(f"{dataset_id} has empty required field: {col}")
        if not str(row["public_landing_page"]).startswith("https://"):
            errors.append(f"{dataset_id} landing page is not an https URL")
        for rel in str(row["included_source_files"]).split(";"):
            rel = rel.strip()
            if rel and rel != "NA" and not (ROOT / rel).exists():
                errors.append(f"{dataset_id} lists missing source file: {rel}")
        limitation = str(row["limitations"])
        if (
            "Observational" in row["evidence_level"]
            and "not a perturbation" not in limitation
            and "not an experimental intervention" not in limitation
        ):
            errors.append(f"{dataset_id} observational limitation is not explicit")

    return errors


def main() -> None:
    errors = check_manifest()
    if errors:
        print("DATASET MANIFEST CHECK FAILED")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)
    print("DATASET MANIFEST CHECK PASSED")


if __name__ == "__main__":
    main()
