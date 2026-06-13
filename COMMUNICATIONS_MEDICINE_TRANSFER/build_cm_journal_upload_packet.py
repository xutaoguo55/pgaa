#!/usr/bin/env python3
"""Build the clean Communications Medicine journal-upload packet.

This packet is intentionally narrower than the author-facing transfer packet:
it excludes internal audits, readiness notes, and portal-helper text files.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "UPLOAD_PACKET_COMMUNICATIONS_MEDICINE"
CLEAN = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_MEDICINE"
ZIP = ROOT / "PGAA_COMMUNICATIONS_MEDICINE_JOURNAL_UPLOAD.zip"

REQUIRED_FILES = [
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_MEDICINE.md",
]

FORBIDDEN_TERMS = [
    "AUDIT",
    "READINESS",
    "REQUIREMENTS",
    "PORTAL_INPUTS",
    "CHECKLIST",
    "REVIEW",
    "INTERNAL",
]


def fail(message: str) -> None:
    raise SystemExit(f"CM JOURNAL UPLOAD BUILD FAILED: {message}")


def build() -> Path:
    if not SOURCE.exists():
        fail(f"source packet missing: {SOURCE}")
    if CLEAN.exists():
        shutil.rmtree(CLEAN)
    CLEAN.mkdir(parents=True)

    for name in REQUIRED_FILES:
        src = SOURCE / name
        if not src.exists() or src.stat().st_size == 0:
            fail(f"missing required source file: {name}")
        shutil.copy2(src, CLEAN / name)

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(CLEAN.iterdir()):
            if path.is_file():
                zf.write(path, path.relative_to(CLEAN.parent))
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
    return len(zip_names), total_size


def main() -> None:
    zpath = build()
    n_files, total_size = validate(zpath)
    print(f"Wrote {CLEAN}")
    print(f"Wrote {zpath}")
    print(f"Journal-upload files: {n_files}")
    print(f"Compressed size: {zpath.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Uncompressed size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
