#!/usr/bin/env python3
"""Check the Communications Medicine transfer packet."""
from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "UPLOAD_PACKET_COMMUNICATIONS_MEDICINE"
ZIP = ROOT / "PGAA_COMMUNICATIONS_MEDICINE_TRANSFER_PACKET.zip"
CLEAN_PACKET = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE"
CLEAN_ZIP = ROOT / "PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip"

REQUIRED_PACKET_FILES = {
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
    "PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md",
    "CM_REQUIREMENTS_AUDIT.md",
    "CM_SUBMISSION_READINESS_AUDIT.md",
}

REQUIRED_CLEAN_UPLOAD_FILES = {
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
}

FORBIDDEN_CLEAN_UPLOAD_TERMS = [
    "AUDIT",
    "READINESS",
    "REQUIREMENTS",
    "PORTAL_INPUTS",
    "CHECKLIST",
    "REVIEW",
    "INTERNAL",
]

FORBIDDEN_MANUSCRIPT_PATTERNS = [
    "Bioinformatics",
    "No new biological discoveries",
    "Motivation:",
    "Availability and implementation:",
]

REQUIRED_MANUSCRIPT_REGEXES = [
    r"disease-relevant",
    r"translational",
    r"marker[- ](?:recovery|prioritization)[\s\S]{0,120}causal validation",
    r"Data availability",
    r"Code availability",
    r"Competing interests",
    r"public\s+code-only repository",
    r"https://github\.com/xutaoguo55/pgaa",
    r"10\.5281/zenodo\.20681141",
    r"swh:1:snp:\s*5b1b2cc9ce32298968e00f69e1af5ff8aed8889f",
    r"Figure 1:[\s\S]{0,160}clinically oriented single-cell perturbation mapping",
]


def fail(msg: str) -> None:
    print(f"CM TRANSFER CHECK FAILED: {msg}")
    sys.exit(1)


def pdf_pages(path: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(path)], text=True)
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    if not match:
        fail(f"could not read page count for {path}")
    return int(match.group(1))


def pdf_text(path: Path) -> str:
    return subprocess.check_output(["pdftotext", str(path), "-"], text=True)


def main() -> None:
    missing = sorted(name for name in REQUIRED_PACKET_FILES if not (PACKET / name).exists())
    if missing:
        fail(f"missing packet files: {', '.join(missing)}")

    if not ZIP.exists():
        fail("missing PGAA_COMMUNICATIONS_MEDICINE_TRANSFER_PACKET.zip")
    if not CLEAN_ZIP.exists():
        fail("missing PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip")

    manuscript = PACKET / "MANUSCRIPT.pdf"
    supplement = PACKET / "SUPPLEMENTARY.pdf"
    if pdf_pages(manuscript) < 5:
        fail("manuscript PDF is unexpectedly short")
    if pdf_pages(supplement) < 3:
        fail("supplementary PDF is unexpectedly short")

    text = pdf_text(manuscript)
    for pattern in FORBIDDEN_MANUSCRIPT_PATTERNS:
        if pattern in text:
            fail(f"forbidden manuscript pattern remains: {pattern}")
    for pattern in REQUIRED_MANUSCRIPT_REGEXES:
        if not re.search(pattern, text):
            fail(f"required manuscript pattern missing: {pattern}")

    with zipfile.ZipFile(ZIP) as zf:
        names = {Path(name).name for name in zf.namelist()}
    missing_in_zip = sorted(name for name in REQUIRED_PACKET_FILES if name not in names)
    if missing_in_zip:
        fail(f"packet zip missing files: {', '.join(missing_in_zip)}")

    clean_missing = sorted(name for name in REQUIRED_CLEAN_UPLOAD_FILES if not (CLEAN_PACKET / name).exists())
    if clean_missing:
        fail(f"clean journal upload packet missing files: {', '.join(clean_missing)}")
    clean_extra = sorted(path.name for path in CLEAN_PACKET.iterdir() if path.is_file() and path.name not in REQUIRED_CLEAN_UPLOAD_FILES)
    if clean_extra:
        fail(f"clean journal upload packet has unexpected files: {', '.join(clean_extra)}")
    clean_bad_names = [
        path.name
        for path in CLEAN_PACKET.iterdir()
        if path.is_file() and any(term in path.name.upper() for term in FORBIDDEN_CLEAN_UPLOAD_TERMS)
    ]
    if clean_bad_names:
        fail(f"clean journal upload packet contains internal filenames: {', '.join(clean_bad_names)}")
    with zipfile.ZipFile(CLEAN_ZIP) as zf:
        clean_zip_names = {Path(name).name for name in zf.namelist() if not name.endswith("/")}
        clean_zip_entries = [name for name in zf.namelist() if not name.endswith("/")]
    missing_clean_zip = sorted(REQUIRED_CLEAN_UPLOAD_FILES - clean_zip_names)
    if missing_clean_zip:
        fail(f"clean journal upload zip missing files: {', '.join(missing_clean_zip)}")
    extra_clean_zip = sorted(clean_zip_names - REQUIRED_CLEAN_UPLOAD_FILES)
    if extra_clean_zip:
        fail(f"clean journal upload zip has unexpected files: {', '.join(extra_clean_zip)}")
    bad_clean_zip = [
        name
        for name in clean_zip_entries
        if any(term in name.upper() for term in FORBIDDEN_CLEAN_UPLOAD_TERMS)
    ]
    if bad_clean_zip:
        fail(f"clean journal upload zip contains internal entries: {', '.join(bad_clean_zip)}")

    code_zip = PACKET / "PGAA_supplementary_code.zip"
    with zipfile.ZipFile(code_zip) as zf:
        code_names = set(zf.namelist())
    required_code_entries = {
        "pgaa_cm_supplementary/communications_medicine/MANUSCRIPT_CM.pdf",
        "pgaa_cm_supplementary/communications_medicine/SUPPLEMENTARY_CM.pdf",
        "pgaa_cm_supplementary/communications_medicine/scripts_generate_cm_norman_figure.py",
        "pgaa_cm_supplementary/.zenodo.json",
        "pgaa_cm_supplementary/CITATION.cff",
        "pgaa_cm_supplementary/codemeta.json",
        "pgaa_cm_supplementary/pgaa/cli.py",
    }
    missing_code_entries = sorted(required_code_entries - code_names)
    if missing_code_entries:
        fail(f"supplementary code zip missing CM entries: {', '.join(missing_code_entries)}")
    forbidden_code_entries = {
        "pgaa_cm_supplementary/MANUSCRIPT.md",
        "pgaa_cm_supplementary/MANUSCRIPT.pdf",
        "pgaa_cm_supplementary/SUPPLEMENTARY.md",
        "pgaa_cm_supplementary/SUPPLEMENTARY.pdf",
    }
    present_forbidden = sorted(forbidden_code_entries & code_names)
    if present_forbidden:
        fail(f"supplementary code zip contains older manuscript entries: {', '.join(present_forbidden)}")
    bioinformatics_named = sorted(name for name in code_names if "bioinformatics" in name.lower())
    if bioinformatics_named:
        fail(f"supplementary code zip contains Bioinformatics-specific entries: {', '.join(bioinformatics_named[:10])}")
    internal_release_entries = sorted(
        name
        for name in code_names
        if any(
            term in name
            for term in [
                "RELEASE_ARCHIVE_CHECKLIST.md",
                "build_submission_zip.py",
                "finalize_archive_metadata.py",
                "COMMUNICATIONS_MEDICINE_TRANSFER",
            ]
        )
    )
    if internal_release_entries:
        fail(f"supplementary code zip contains internal release entries: {', '.join(internal_release_entries[:10])}")

    portal = (PACKET / "PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md").read_text()
    if "https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code" not in portal:
        fail("final GitHub release URL missing from portal inputs")
    if "https://doi.org/10.5281/zenodo.20681141" not in portal:
        fail("final Zenodo DOI missing from portal inputs")
    if "swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f" not in portal:
        fail("final Software Heritage SWHID missing from portal inputs")
    if "OPT OUT of publication of reviewer reports" not in portal:
        fail("transparent peer review preference is not set in portal inputs")

    print("CM TRANSFER CHECK PASSED")
    print(f"Packet files: {len(REQUIRED_PACKET_FILES)}")
    print(f"Clean journal-upload files: {len(REQUIRED_CLEAN_UPLOAD_FILES)}")
    print(f"Manuscript pages: {pdf_pages(manuscript)}")
    print(f"Supplement pages: {pdf_pages(supplement)}")
    print("Public code-only repository, Zenodo DOI, and Software Heritage SWHID are present")


if __name__ == "__main__":
    main()
