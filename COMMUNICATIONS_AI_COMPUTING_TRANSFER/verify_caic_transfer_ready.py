#!/usr/bin/env python3
"""Check the Communications AI & Computing transfer packet."""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING"
ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_TRANSFER_PACKET.zip"
CLEAN_PACKET = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
CLEAN_ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip"
FINAL_UPLOAD = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"

REQUIRED_PACKET_FILES = {
    "MANUSCRIPT.docx",
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
    "PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf",
}

REQUIRED_CLEAN_UPLOAD_FILES = {
    "MANUSCRIPT.docx",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
}

CURRENT_FILE_MAP = {
    ROOT / "MANUSCRIPT_CAIC.docx": "MANUSCRIPT.docx",
    ROOT / "MANUSCRIPT_CAIC.pdf": "MANUSCRIPT.pdf",
    ROOT / "SUPPLEMENTARY_CAIC.pdf": "SUPPLEMENTARY.pdf",
    ROOT / "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf": "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
}

FORBIDDEN_UPLOAD_TERMS = [
    "AUDIT",
    "READINESS",
    "REQUIREMENTS",
    "PORTAL_INPUTS",
    "REVIEW",
    "INTERNAL",
]

FORBIDDEN_MANUSCRIPT_PATTERNS = [
    "Bioinformatics",
    "Communications Medicine because",
    "submitted to Communications Medicine",
    "desk rejection",
    "declined without external peer review",
    "bedside diagnosis",
    "treatment recommendation",
    "clinical biomarker claim",
    "No new biological discoveries",
    "Motivation:",
    "Availability and implementation:",
]

REQUIRED_MANUSCRIPT_REGEXES = [
    r"distribution-aware computational framework",
    r"computational ranking layer",
    r"single-cell perturbation data",
    r"marker[- ]recovery stress (tests|checks)",
    r"rather than causal interpretation",
    r"Data availability",
    r"Code availability",
    r"Competing interests",
    r"public\s+code-only repository",
    r"https://github\.com/xutaoguo55/pgaa",
    r"10\.5281/zenodo\.20681141",
    r"swh:1:snp:\s*5b1b2cc9ce32298968e00f69e1af5ff8aed8889f",
    r"Figure 1:[\s\S]{0,220}distribution-aware single-cell perturbation ranking",
]


def fail(msg: str) -> None:
    print(f"CAIC TRANSFER CHECK FAILED: {msg}")
    sys.exit(1)


def pdf_pages(path: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(path)], text=True)
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    if not match:
        fail(f"could not read page count for {path}")
    return int(match.group(1))


def pdf_text(path: Path) -> str:
    return subprocess.check_output(["pdftotext", str(path), "-"], text=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_upload_dir(path: Path, required: set[str], label: str, forbid_internal_names: bool = True) -> None:
    missing = sorted(name for name in required if not (path / name).exists())
    if missing:
        fail(f"{label} missing files: {', '.join(missing)}")
    extras = sorted(p.name for p in path.iterdir() if p.is_file() and p.name not in required)
    if extras:
        fail(f"{label} has unexpected files: {', '.join(extras)}")
    if forbid_internal_names:
        bad = [
            p.name
            for p in path.iterdir()
            if p.is_file() and any(term in p.name.upper() for term in FORBIDDEN_UPLOAD_TERMS)
        ]
        if bad:
            fail(f"{label} contains internal filenames: {', '.join(bad)}")


def main() -> None:
    check_upload_dir(PACKET, REQUIRED_PACKET_FILES, "author-facing packet", forbid_internal_names=False)
    check_upload_dir(CLEAN_PACKET, REQUIRED_CLEAN_UPLOAD_FILES, "clean journal upload packet")

    if not ZIP.exists():
        fail("missing PGAA_COMMUNICATIONS_AI_COMPUTING_TRANSFER_PACKET.zip")
    if not CLEAN_ZIP.exists():
        fail("missing PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip")

    required_by_base = {
        PACKET: REQUIRED_PACKET_FILES,
        CLEAN_PACKET: REQUIRED_CLEAN_UPLOAD_FILES,
        FINAL_UPLOAD: REQUIRED_CLEAN_UPLOAD_FILES,
    }
    for current, packet_name in CURRENT_FILE_MAP.items():
        for base in [PACKET, CLEAN_PACKET, FINAL_UPLOAD]:
            if packet_name not in required_by_base[base]:
                continue
            candidate = base / packet_name
            if not candidate.exists():
                fail(f"missing synced upload file: {candidate}")
            if sha256(current) != sha256(candidate):
                fail(f"stale upload file: {candidate} does not match {current.name}")

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
        zip_entries = [name for name in zf.namelist() if not name.endswith("/")]
        zip_names = {Path(name).name for name in zip_entries}
    missing_in_zip = sorted(REQUIRED_PACKET_FILES - zip_names)
    if missing_in_zip:
        fail(f"packet zip missing files: {', '.join(missing_in_zip)}")
    bad_zip = [
        name
        for name in zip_entries
        if Path(name).name != "PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md"
        and any(term in name.upper() for term in FORBIDDEN_UPLOAD_TERMS)
    ]
    if bad_zip:
        fail(f"packet zip contains internal entries: {', '.join(bad_zip)}")

    with zipfile.ZipFile(CLEAN_ZIP) as zf:
        clean_entries = [name for name in zf.namelist() if not name.endswith("/")]
        clean_names = {Path(name).name for name in clean_entries}
    if clean_names != REQUIRED_CLEAN_UPLOAD_FILES:
        fail(f"clean zip has unexpected files: {sorted(clean_names)}")
    bad_clean_zip = [
        name
        for name in clean_entries
        if any(term in name.upper() for term in FORBIDDEN_UPLOAD_TERMS)
    ]
    if bad_clean_zip:
        fail(f"clean journal upload zip contains internal entries: {', '.join(bad_clean_zip)}")

    code_zip = PACKET / "PGAA_supplementary_code.zip"
    with zipfile.ZipFile(code_zip) as zf:
        code_names = set(zf.namelist())
    required_code_entries = {
        "pgaa_caic_supplementary/communications_ai_computing/MANUSCRIPT_CAIC.pdf",
        "pgaa_caic_supplementary/communications_ai_computing/SUPPLEMENTARY_CAIC.pdf",
        "pgaa_caic_supplementary/communications_ai_computing/scripts_generate_caic_norman_figure.py",
        "pgaa_caic_supplementary/.zenodo.json",
        "pgaa_caic_supplementary/CITATION.cff",
        "pgaa_caic_supplementary/codemeta.json",
        "pgaa_caic_supplementary/pgaa/cli.py",
    }
    missing_code_entries = sorted(required_code_entries - code_names)
    if missing_code_entries:
        fail(f"supplementary code zip missing CAIC entries: {', '.join(missing_code_entries)}")
    forbidden_code_terms = [
        "BIOINFORMATICS_UPLOAD_PACKET",
        "COMMUNICATIONS_MEDICINE_TRANSFER",
        "CURRENT_BIOINFORMATICS_REVIEW",
        "SIMULATED_BIOINFORMATICS_REVIEW",
        "POST_REVISION_BIOINFORMATICS_REVIEW",
        "RELEASE_ARCHIVE_CHECKLIST.md",
        "build_submission_zip.py",
        "FIGURE_PROMPTS.md",
    ]
    bad_code_entries = sorted(
        name for name in code_names if any(term in name for term in forbidden_code_terms)
    )
    if bad_code_entries:
        fail(f"supplementary code zip contains internal entries: {', '.join(bad_code_entries[:10])}")

    portal = (PACKET / "PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md").read_text()
    for required in [
        "Communications AI & Computing",
        "https://github.com/xutaoguo55/pgaa/releases/tag/v0.1.0-code",
        "https://doi.org/10.5281/zenodo.20681141",
        "swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f",
        "OPT IN to Transparent Peer Review",
    ]:
        if required not in portal:
            fail(f"portal required text missing: {required}")

    cover_text = pdf_text(PACKET / "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf")
    for required in [
        "Communications AI & Computing",
        "computational framework",
        "opt in to Transparent Peer Review",
    ]:
        if required not in cover_text:
            fail(f"cover letter required text missing: {required}")

    print("CAIC TRANSFER CHECK PASSED")
    print(f"Packet files: {len(REQUIRED_PACKET_FILES)}")
    print(f"Clean journal-upload files: {len(REQUIRED_CLEAN_UPLOAD_FILES)}")
    print(f"Manuscript pages: {pdf_pages(manuscript)}")
    print(f"Supplement pages: {pdf_pages(supplement)}")
    print("Public code-only repository, Zenodo DOI, and Software Heritage SWHID are present")


if __name__ == "__main__":
    main()
