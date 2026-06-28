#!/usr/bin/env python3
"""Build the clean Communications AI & Computing journal-upload packet.

This packet is intentionally narrower than the author-facing transfer packet:
it excludes internal audits, readiness notes, and portal-helper text files.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING"
CLEAN = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
FINAL = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip"
TRANSFER_ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_TRANSFER_PACKET.zip"

REQUIRED_FILES = [
    "MANUSCRIPT.docx",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
]

CURRENT_FILE_MAP = {
    "MANUSCRIPT_CAIC.docx": "MANUSCRIPT.docx",
    "MANUSCRIPT_CAIC.pdf": "MANUSCRIPT.pdf",
    "SUPPLEMENTARY_CAIC.pdf": "SUPPLEMENTARY.pdf",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md": "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.md",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx": "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.docx",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf": "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
    "PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md": "PORTAL_INPUTS_COMMUNICATIONS_AI_COMPUTING.md",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md": "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx": "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx",
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf": "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md": "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.md",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx": "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.docx",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf": "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING.pdf",
}

FORBIDDEN_TERMS = [
    "AUDIT",
    "READINESS",
    "REQUIREMENTS",
    "PORTAL_INPUTS",
    "REVIEW",
    "INTERNAL",
]


def fail(message: str) -> None:
    raise SystemExit(f"CAIC JOURNAL UPLOAD BUILD FAILED: {message}")


def build() -> Path:
    if not SOURCE.exists():
        fail(f"source packet missing: {SOURCE}")
    for current_name, packet_name in CURRENT_FILE_MAP.items():
        current = ROOT / current_name
        if not current.exists() or current.stat().st_size == 0:
            fail(f"missing current source file: {current_name}")
        shutil.copy2(current, SOURCE / packet_name)

    if CLEAN.exists():
        shutil.rmtree(CLEAN)
    CLEAN.mkdir(parents=True)
    if FINAL.exists():
        shutil.rmtree(FINAL)
    FINAL.mkdir(parents=True)

    for name in REQUIRED_FILES:
        src = SOURCE / name
        if not src.exists() or src.stat().st_size == 0:
            fail(f"missing required source file: {name}")
        shutil.copy2(src, CLEAN / name)
        shutil.copy2(src, FINAL / name)

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(CLEAN.iterdir()):
            if path.is_file():
                zf.write(path, path.relative_to(CLEAN.parent))

    if TRANSFER_ZIP.exists():
        TRANSFER_ZIP.unlink()
    with zipfile.ZipFile(TRANSFER_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SOURCE.iterdir()):
            if path.is_file():
                zf.write(path, path.relative_to(SOURCE.parent))
    return ZIP


def validate(zpath: Path) -> tuple[int, int]:
    names = sorted(path.name for path in CLEAN.iterdir() if path.is_file())
    if names != sorted(REQUIRED_FILES):
        fail(f"unexpected clean packet files: {names}")

    bad_names = [name for name in names if any(term in name.upper() for term in FORBIDDEN_TERMS)]
    if bad_names:
        fail(f"clean packet contains internal filenames: {bad_names}")

    with zipfile.ZipFile(zpath) as zf:
        zip_names = sorted(Path(name).name for name in zf.namelist() if not name.endswith("/"))
        if zip_names != sorted(REQUIRED_FILES):
            fail(f"journal upload zip has unexpected files: {zip_names}")
        bad_zip = [
            name
            for name in zf.namelist()
            if any(term in name.upper() for term in FORBIDDEN_TERMS)
        ]
        if bad_zip:
            fail(f"journal upload zip contains internal entries: {bad_zip}")
        total_size = sum(info.file_size for info in zf.infolist())

    with zipfile.ZipFile(TRANSFER_ZIP) as zf:
        transfer_names = sorted(Path(name).name for name in zf.namelist() if not name.endswith("/"))
        missing_transfer = sorted(set(CURRENT_FILE_MAP.values()) - set(transfer_names))
        if missing_transfer:
            fail(f"transfer packet zip missing files: {missing_transfer}")
    return len(zip_names), total_size


def main() -> None:
    zpath = build()
    n_files, total_size = validate(zpath)
    print(f"Wrote {CLEAN}")
    print(f"Wrote {FINAL}")
    print(f"Wrote {zpath}")
    print(f"Wrote {TRANSFER_ZIP}")
    print(f"Journal-upload files: {n_files}")
    print(f"Compressed size: {zpath.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Uncompressed size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
