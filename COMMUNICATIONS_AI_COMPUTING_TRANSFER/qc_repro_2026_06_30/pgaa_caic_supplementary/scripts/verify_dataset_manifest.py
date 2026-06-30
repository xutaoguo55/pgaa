#!/usr/bin/env python3
"""Verify dataset accession and reproduction metadata for the PGAA package."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "DATASET_MANIFEST.tsv"
TEXT_SOURCES = [
    ROOT / "communications_ai_computing" / "MANUSCRIPT_CAIC.md",
    ROOT / "communications_ai_computing" / "SUPPLEMENTARY_CAIC.md",
    ROOT / "communications_medicine" / "MANUSCRIPT_CM.md",
    ROOT / "communications_medicine" / "SUPPLEMENTARY_CM.md",
    ROOT / "README.md",
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
EXPECTED_ACCESSIONS = {
    "GSE133344",
    "GSE90546",
    "GSE111014",
    "GSE167363",
    "GSE159117",
    "GSE116222",
}


def accessions_in_text() -> set[str]:
    found: set[str] = set()
    for path in TEXT_SOURCES:
        if path.exists():
            found.update(re.findall(r"GSE\d+", path.read_text(errors="replace")))
    return found


def check_manifest() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.exists():
        return ["Missing DATASET_MANIFEST.tsv"]
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
            if not str(row[col]).strip():
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
