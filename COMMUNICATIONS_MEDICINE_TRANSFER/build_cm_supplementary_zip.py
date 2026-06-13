#!/usr/bin/env python3
"""Build the Communications Medicine supplementary software archive."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


CM_ROOT = Path(__file__).resolve().parent
ROOT = CM_ROOT.parent
OUT = CM_ROOT / "UPLOAD_PACKET_COMMUNICATIONS_MEDICINE" / "PGAA_supplementary_code.zip"
STAGE_NAME = "pgaa_cm_supplementary"

ROOT_FILES = [
    "README.md",
    "LICENSE",
    "DATASET_MANIFEST.tsv",
    "CITATION.cff",
    "codemeta.json",
    ".zenodo.json",
    "pyproject.toml",
    "requirements.txt",
    "environment.yml",
    "Dockerfile",
]

CM_FILES = [
    "MANUSCRIPT_CM.md",
    "MANUSCRIPT_CM.pdf",
    "SUPPLEMENTARY_CM.md",
    "SUPPLEMENTARY_CM.pdf",
    "build_cm_pdf.py",
    "scripts_generate_cm_entry_figure.py",
    "scripts_generate_cm_norman_figure.py",
]

ROOT_DIRS = ["pgaa", "pgaa_r", "figure_source_data", "figures_png", "tests"]
SCRIPT_SUFFIXES = {".py", ".R", ".csv", ".md", ".txt", ".sh"}
FORBIDDEN_SUBSTRINGS = [
    "BIOINFORMATICS_UPLOAD_PACKET",
    "Bioinformatics",
    "BIOINFORMATICS",
    "bioinformatics",
    "MANUSCRIPT.docx",
    "MANUSCRIPT.html",
    "MANUSCRIPT.pdf",
    "MANUSCRIPT.tex",
    "MANUSCRIPT.md",
    "SUPPLEMENTARY.html",
    "SUPPLEMENTARY.pdf",
    "SUPPLEMENTARY.tex",
    "SUPPLEMENTARY.md",
    "RELEASE_ARCHIVE_CHECKLIST.md",
    "build_submission_zip.py",
    "finalize_archive_metadata.py",
    "COVER_LETTER",
    "PORTAL_INPUTS",
    "SUBMISSION_READINESS_AUDIT",
    "SUBMISSION_CHECKLIST",
    "CURRENT_BIOINFORMATICS_REVIEW",
    "SIMULATED_BIOINFORMATICS_REVIEW",
    "POST_REVISION_BIOINFORMATICS_REVIEW",
    "PROJECT_REVIEW",
    "REVIEWER_RESPONSE",
    "REFERENCE_AUDIT",
    "FIGURE_PROMPTS.md",
    "verify_manuscript_consistency.py",
    "verify_upload_file_manifest.py",
    "figure_workflow",
    "workflow_schematic",
    "mmd_psm",
    "virtual_KO_method",
    "OE_paper",
    "SCEPTRE_Drug",
    "__pycache__",
    ".pytest_cache",
    "_test_output.txt",
    ".log",
]


def allowed(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(term in rel for term in FORBIDDEN_SUBSTRINGS):
        return False
    if path.name == ".DS_Store" or path.suffix == ".pyc":
        return False
    return True


def copy_tree(src: Path, dest: Path, suffixes: set[str] | None = None) -> None:
    for path in src.rglob("*"):
        if not path.is_file() or not allowed(path):
            continue
        if suffixes is not None and path.suffix not in suffixes:
            continue
        rel = path.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def build() -> Path:
    stage_parent = Path(tempfile.mkdtemp(prefix="pgaa_cm_zip_"))
    try:
        stage = stage_parent / STAGE_NAME
        stage.mkdir(parents=True)

        for rel in ROOT_FILES:
            src = ROOT / rel
            if src.exists() and allowed(src):
                shutil.copy2(src, stage / rel)

        manuscript_dir = stage / "communications_medicine"
        manuscript_dir.mkdir(parents=True, exist_ok=True)
        for rel in CM_FILES:
            src = CM_ROOT / rel
            if src.exists():
                shutil.copy2(src, manuscript_dir / rel)

        for rel in ROOT_DIRS:
            src = ROOT / rel
            if src.exists():
                copy_tree(src, stage / rel)

        copy_tree(ROOT / "scripts", stage / "scripts", suffixes=SCRIPT_SUFFIXES)

        OUT.parent.mkdir(parents=True, exist_ok=True)
        if OUT.exists():
            OUT.unlink()
        with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(stage_parent))
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)
    return OUT


def validate(zpath: Path) -> tuple[int, int]:
    required = [
        f"{STAGE_NAME}/pgaa/cli.py",
        f"{STAGE_NAME}/scripts/run_toy_example.py",
        f"{STAGE_NAME}/DATASET_MANIFEST.tsv",
        f"{STAGE_NAME}/LICENSE",
        f"{STAGE_NAME}/CITATION.cff",
        f"{STAGE_NAME}/codemeta.json",
        f"{STAGE_NAME}/.zenodo.json",
        f"{STAGE_NAME}/communications_medicine/MANUSCRIPT_CM.pdf",
        f"{STAGE_NAME}/communications_medicine/SUPPLEMENTARY_CM.pdf",
        f"{STAGE_NAME}/communications_medicine/scripts_generate_cm_norman_figure.py",
        f"{STAGE_NAME}/figures_png/figure_pgaa_workflow.png",
    ]
    forbidden_suffixes = [
        f"{STAGE_NAME}/MANUSCRIPT.pdf",
        f"{STAGE_NAME}/MANUSCRIPT.md",
        f"{STAGE_NAME}/SUPPLEMENTARY.pdf",
        f"{STAGE_NAME}/SUPPLEMENTARY.md",
    ]
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        forbidden = [
            name
            for name in names
            if any(term in name for term in FORBIDDEN_SUBSTRINGS)
            or name in forbidden_suffixes
        ]
        missing = [name for name in required if name not in names]
        if forbidden or missing:
            for name in forbidden[:30]:
                print(f"Forbidden zip entry: {name}")
            for name in missing:
                print(f"Missing required zip entry: {name}")
            raise SystemExit(1)
        total_size = sum(info.file_size for info in zf.infolist())
        return len(names), total_size


def main() -> None:
    zpath = build()
    n_entries, total_size = validate(zpath)
    print(f"Wrote {zpath}")
    print(f"Zip entries: {n_entries}")
    print(f"Compressed size: {zpath.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Uncompressed size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
