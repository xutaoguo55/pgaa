#!/usr/bin/env python3
"""Build CAIC checklist documents as DOCX and PDF."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SOFFICE = Path("/Users/guoxutao/.codex/skills/docx/scripts/office/soffice.py")

CHECKLISTS = [
    "MACHINE_LEARNING_CHECKLIST_COMMUNICATIONS_AI_COMPUTING",
    "SOFTWARE_SUBMISSION_CHECKLIST_COMMUNICATIONS_AI_COMPUTING",
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def build_one(stem: str) -> None:
    md = ROOT / f"{stem}.md"
    docx = ROOT / f"{stem}.docx"
    pdf = ROOT / f"{stem}.pdf"
    if not md.exists():
        raise FileNotFoundError(md)

    run([
        "pandoc",
        str(md),
        "-o",
        str(docx),
        "--from",
        "markdown",
        "--standalone",
    ])
    run([
        sys.executable,
        str(SOFFICE),
        "--headless",
        "--convert-to",
        "pdf",
        str(docx),
        "--outdir",
        str(ROOT),
    ])
    if not docx.exists() or docx.stat().st_size == 0:
        raise RuntimeError(f"failed to build {docx.name}")
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"failed to build {pdf.name}")
    print(f"Wrote {docx}")
    print(f"Wrote {pdf}")


def main() -> int:
    for stem in CHECKLISTS:
        build_one(stem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
