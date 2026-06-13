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

REQUIRED_PACKET_FILES = {
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
    "PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md",
    "CM_REQUIREMENTS_AUDIT.md",
    "CM_SUBMISSION_READINESS_AUDIT.md",
}

FORBIDDEN_MANUSCRIPT_PATTERNS = [
    "Bioinformatics",
    "No new biological discoveries",
    "Motivation:",
    "Availability and implementation:",
]

REQUIRED_MANUSCRIPT_REGEXES = [
    r"disease-relevant",
    r"translational",
    r"marker[- ]recovery[\s\S]{0,80}causal validation",
    r"Data availability",
    r"Code availability",
    r"Competing interests",
    r"public repository[\s\S]{0,160}archive identifiers[\s\S]{0,120}before\s+(?:final\s+)?submission",
    r"Figure 1:[\s\S]{0,120}clinically oriented single-cell perturbation mapping",
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

    portal = (PACKET / "PORTAL_INPUTS_COMMUNICATIONS_MEDICINE.md").read_text()
    expected_placeholder = "[insert final archive DOI or persistent URL]"
    if expected_placeholder not in portal:
        fail("expected archive placeholder missing from portal inputs; update verifier after DOI insertion")
    if "OPT OUT of publication of reviewer reports" not in portal:
        fail("transparent peer review preference is not set in portal inputs")

    cover = (PACKET / "COVER_LETTER_COMMUNICATIONS_MEDICINE.md").read_text()
    if "OPT OUT of publication of the reviewer reports" not in cover:
        fail("transparent peer review preference is not stated in the cover letter")

    print("CM TRANSFER CHECK PASSED")
    print(f"Packet files: {len(REQUIRED_PACKET_FILES)}")
    print(f"Manuscript pages: {pdf_pages(manuscript)}")
    print(f"Supplement pages: {pdf_pages(supplement)}")
    print("Remaining expected blocker: public repository/archive DOI placeholder")


if __name__ == "__main__":
    main()
