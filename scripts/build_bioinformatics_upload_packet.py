#!/usr/bin/env python3
"""Build an author-facing Bioinformatics upload packet from the manifest."""
from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "UPLOAD_FILE_MANIFEST.tsv"
OUT_DIR = ROOT / "BIOINFORMATICS_UPLOAD_PACKET"

FORBIDDEN_TERMS = [
    "figure_workflow",
    "CURRENT_BIOINFORMATICS_REVIEW",
    "SIMULATED_BIOINFORMATICS_REVIEW",
    "POST_REVISION_BIOINFORMATICS_REVIEW",
    "REFERENCE_AUDIT",
    "SUBMISSION_READINESS_AUDIT",
    "SUBMISSION_CHECKLIST",
    "mmd_psm",
]


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate_packet() -> None:
    errors: list[str] = []
    for path in OUT_DIR.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(OUT_DIR).as_posix()
        if any(term in rel for term in FORBIDDEN_TERMS):
            errors.append(f"Forbidden packet file: {rel}")
    if errors:
        for err in errors:
            print(err)
        raise SystemExit(1)


def main() -> None:
    rows = read_manifest()
    upload_rows = [row for row in rows if row["upload"] == "yes"]
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    copied = 0
    for row in upload_rows:
        rel = row["file"]
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f"Manifested upload file is missing: {rel}")
        if any(term in rel for term in FORBIDDEN_TERMS):
            raise SystemExit(f"Forbidden file is marked upload=yes: {rel}")
        dest = OUT_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied += 1

    validate_packet()
    print(f"Wrote {OUT_DIR}")
    print(f"Upload files copied: {copied}")


if __name__ == "__main__":
    main()
