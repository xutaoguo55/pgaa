#!/usr/bin/env python3
"""Build the Communications AI & Computing supplementary software archive."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


CAIC_ROOT = Path(__file__).resolve().parent
ROOT = CAIC_ROOT.parent
OUT = CAIC_ROOT / "UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING" / "PGAA_supplementary_code.zip"
STAGE_NAME = "pgaa_caic_supplementary"

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

CAIC_FILES = [
    "MANUSCRIPT_CAIC.md",
    "MANUSCRIPT_CAIC.pdf",
    "SUPPLEMENTARY_CAIC.md",
    "SUPPLEMENTARY_CAIC.pdf",
    "build_caic_supplementary_pdf.py",
    "build_caic_pdf.py",
    "scripts_generate_caic_entry_figure.py",
    "scripts_generate_caic_norman_figure.py",
]

CAIC_FIGURES = [
    "figure_caic_entry.png",
    "figure_adamson_benchmark.png",
    "figure_norman_main_caic.png",
    "figure_3.png",
    "figure_1.png",
    "figure_5.png",
    "figure_elane_histogram.png",
    "figure_s2_calibration_qq.png",
    "figure_s2_bhlhe40.png",
    "figure_pgaa_workflow.png",
]

ROOT_DIRS = ["pgaa", "pgaa_r", "figure_source_data", "figures_png", "tests"]
SCRIPT_SUFFIXES = {".py", ".R", ".csv", ".md", ".txt", ".sh"}
FORBIDDEN_SCRIPT_CONTENT = [
    "/Users/guoxutao",
    "COMMUNICATIONS_MEDICINE_TRANSFER",
    "BIOINFORMATICS",
    "Bioinformatics",
    "bioinformatics",
    "desk reject",
    "desk rejection",
    "declined without external peer review",
    "internal review",
]
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
    "generate_paper_tables.py",
    "table2_s2_calibration.csv",
    "table3_decision_rule.csv",
    "tables_paper.md",
    "figure_workflow",
    "workflow_schematic",
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
        if suffixes is not None and path.suffix in {".py", ".R", ".md", ".txt", ".sh"}:
            text = path.read_text(errors="replace")
            if any(term in text for term in FORBIDDEN_SCRIPT_CONTENT):
                continue
        rel = path.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def build() -> Path:
    stage_parent = Path(tempfile.mkdtemp(prefix="pgaa_caic_zip_"))
    try:
        stage = stage_parent / STAGE_NAME
        stage.mkdir(parents=True)

        for rel in ROOT_FILES:
            src = ROOT / rel
            if src.exists() and allowed(src):
                shutil.copy2(src, stage / rel)

        manuscript_dir = stage / "communications_ai_computing"
        manuscript_dir.mkdir(parents=True, exist_ok=True)
        for rel in CAIC_FILES:
            src = CAIC_ROOT / rel
            if src.exists():
                shutil.copy2(src, manuscript_dir / rel)

        for rel in ROOT_DIRS:
            src = ROOT / rel
            if src.exists():
                copy_tree(src, stage / rel)

        for rel in CAIC_FIGURES:
            src = CAIC_ROOT / "figures_png" / rel
            if src.exists():
                out = stage / "figures_png" / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, out)

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
        f"{STAGE_NAME}/communications_ai_computing/MANUSCRIPT_CAIC.pdf",
        f"{STAGE_NAME}/communications_ai_computing/SUPPLEMENTARY_CAIC.pdf",
        f"{STAGE_NAME}/communications_ai_computing/scripts_generate_caic_norman_figure.py",
        f"{STAGE_NAME}/figures_png/figure_caic_entry.png",
        f"{STAGE_NAME}/figures_png/figure_adamson_benchmark.png",
        f"{STAGE_NAME}/figures_png/figure_norman_main_caic.png",
        f"{STAGE_NAME}/figures_png/figure_pgaa_workflow.png",
        f"{STAGE_NAME}/pgaa/core/mmd_psm.py",
        f"{STAGE_NAME}/scripts/table1_datasets_summary.csv",
        f"{STAGE_NAME}/scripts/rebuild_adamson_full_results.py",
        f"{STAGE_NAME}/scripts/table_sceptre_vs_pgaa.py",
        f"{STAGE_NAME}/scripts/figure_simulation.py",
        f"{STAGE_NAME}/scripts/benchmark_mmd_psm.py",
        f"{STAGE_NAME}/scripts/mmd_psm_summary.csv",
        f"{STAGE_NAME}/scripts/benchmark_norman_multi_perturbation.py",
        f"{STAGE_NAME}/scripts/norman_multi_perturbation_summary.csv",
        f"{STAGE_NAME}/scripts/norman_multi_perturbation_gene_scores.csv",
        f"{STAGE_NAME}/scripts/norman_multi_perturbation_panel_audit.csv",
        f"{STAGE_NAME}/scripts/norman_multi_perturbation_metadata.csv",
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
