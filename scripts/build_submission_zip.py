#!/usr/bin/env python3
"""Build the clean PGAA supplementary software archive."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from pgaa.core.gse335846_external_dynamic_corroboration import (
    write_external_dynamic_corroboration_assets,
)
from pgaa.core.gse335846_phosphoproteomics_corroboration import (
    write_phosphoproteomics_corroboration_assets,
)
from pgaa.core.gse150949_pc9_evolution_audit import (
    write_gse150949_pc9_evolution_assets,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "PGAA_supplementary_code.zip"
STAGE_NAME = "pgaa_supplementary"

ROOT_FILES = [
    "MANUSCRIPT.md",
    "MANUSCRIPT.pdf",
    "SUPPLEMENTARY.md",
    "SUPPLEMENTARY.pdf",
    "docs/SUBMISSION_PACKAGE_INDEX.md",
    "docs/PUBLICATION_GAP_AUDIT.md",
    "docs/DATA_ROOT_PROVENANCE.md",
    "docs/AUTHOR_DATA_REQUEST_GSE335846.md",
    "docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md",
    "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md",
    "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md",
    "evidence/gse335846_source_data_numeric_audit.tsv",
    "evidence/gse335846_external_dynamic_corroboration.tsv",
    "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md",
    "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md",
    "evidence/gse335846_phosphoproteomics_corroboration.tsv",
    "evidence/gse335846_phosphoproteomics_selected_markers.tsv",
    "evidence/gse335846_phosphoproteomics_boundary_scan.tsv",
    "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png",
    "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf",
    "docs/GSE150949_PC9_EVOLUTION_AUDIT.md",
    "docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md",
    "evidence/gse150949_pc9_module_coverage.tsv",
    "evidence/gse150949_pc9_route_scores.tsv",
    "evidence/gse150949_pc9_sample_summary.tsv",
    "evidence/gse150949_pc9_group_summary.tsv",
    "docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md",
    "docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md",
    "docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md",
    "README.md",
    "LICENSE",
    "DATASET_MANIFEST.tsv",
    "CITATION.cff",
    "codemeta.json",
    "RELEASE_ARCHIVE_CHECKLIST.md",
    "build_pdf.py",
    "pyproject.toml",
    "requirements.txt",
    "environment.yml",
    "Dockerfile",
    "UPLOAD_FILE_MANIFEST.tsv",
]

ROOT_DIRS = ["pgaa", "pgaa_r", "figure_source_data", "figures_png", "tests"]
SCRIPT_SUFFIXES = {".py", ".R", ".csv", ".md", ".txt", ".sh"}
FORBIDDEN_SUBSTRINGS = [
    "figure_workflow",
    "workflow_schematic",
    "CURRENT_BIOINFORMATICS_REVIEW",
    "SIMULATED_BIOINFORMATICS_REVIEW",
    "POST_REVISION_BIOINFORMATICS_REVIEW",
    "PROJECT_REVIEW",
    "REVIEWER_RESPONSE",
    "REFERENCE_AUDIT",
    "SUBMISSION_READINESS_AUDIT",
    "SUBMISSION_CHECKLIST",
    "COVER_LETTER",
    "mmd_psm",
    "virtual_KO_method",
    "OE_paper",
    "SCEPTRE_Drug",
    "__pycache__",
    ".pytest_cache",
    "_test_output.txt",
    ".log",
]


def _refresh_gse335846_corroboration_assets() -> None:
    write_external_dynamic_corroboration_assets(
        source_dir=ROOT / "sources/gse335846_dynamic_atm",
        preprint_path=ROOT / "sources/gse335846_dynamic_atm/preprint_733326.txt",
        summary_out=ROOT / "evidence/gse335846_external_dynamic_corroboration.tsv",
        report_out=ROOT / "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md",
        timecourse_path=ROOT / "evidence/gse335846_dynamic_atm_timecourse.tsv",
        branch_scores_path=ROOT / "evidence/gse335846_rna_seq_branch_axis_scores.tsv",
        marker_summary_path=ROOT / "evidence/gse335846_rna_seq_branch_axis_source_summary.tsv",
        association_path=ROOT / "evidence/gse335846_dynamic_atm_association.tsv",
        figure_out=ROOT / "figures_png/gse335846_dynamic_corroboration_scorecard.png",
        figure_pdf_out=ROOT / "figures_png/gse335846_dynamic_corroboration_scorecard.pdf",
        support_text_out=ROOT / "docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md",
    )


def _refresh_gse335846_phosphoproteomics_assets() -> None:
    write_phosphoproteomics_corroboration_assets(
        source_dir=ROOT / "sources/gse335846_dynamic_atm",
        workbook_path=ROOT / "sources/gse335846_dynamic_atm/source_ev1.xlsx",
        summary_out=ROOT / "evidence/gse335846_phosphoproteomics_corroboration.tsv",
        report_out=ROOT / "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md",
        selected_out=ROOT / "evidence/gse335846_phosphoproteomics_selected_markers.tsv",
        boundary_out=ROOT / "evidence/gse335846_phosphoproteomics_boundary_scan.tsv",
        figure_out=ROOT / "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png",
        figure_pdf_out=ROOT / "figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf",
        support_text_out=ROOT / "docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md",
    )


def _refresh_gse150949_pc9_assets() -> None:
    write_gse150949_pc9_evolution_assets(
        state_modules_path=ROOT / "evidence/gse75602_resistance_state_modules.tsv",
        annotation_path=ROOT / "evidence/gse75602_resistance_down_module_ensembl_annotation.tsv",
        metadata_path=ROOT / "data/gse150949/GSE150949_metaData_with_lineage.txt.gz",
        matrix_path=ROOT / "data/gse150949/GSE150949_pc9_count_matrix.csv.gz",
        figure_out=ROOT / "figures_png/gse150949_pc9_evolution_scorecard.png",
        figure_pdf_out=ROOT / "figures_png/gse150949_pc9_evolution_scorecard.pdf",
        audit_out=ROOT / "docs/GSE150949_PC9_EVOLUTION_AUDIT.md",
        support_text_out=ROOT / "docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md",
        coverage_out=ROOT / "evidence/gse150949_pc9_module_coverage.tsv",
        route_scores_out=ROOT / "evidence/gse150949_pc9_route_scores.tsv",
        sample_summary_out=ROOT / "evidence/gse150949_pc9_sample_summary.tsv",
        group_summary_out=ROOT / "evidence/gse150949_pc9_group_summary.tsv",
    )


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
    _refresh_gse335846_corroboration_assets()
    _refresh_gse335846_phosphoproteomics_assets()
    _refresh_gse150949_pc9_assets()
    stage_parent = Path(tempfile.mkdtemp(prefix="pgaa_submission_zip_"))
    try:
        stage = stage_parent / STAGE_NAME
        stage.mkdir(parents=True)

        for rel in ROOT_FILES:
            src = ROOT / rel
            if src.exists() and allowed(src):
                dest = stage / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

        for rel in ROOT_DIRS:
            src = ROOT / rel
            if src.exists():
                copy_tree(src, stage / rel)

        copy_tree(ROOT / "scripts", stage / "scripts", suffixes=SCRIPT_SUFFIXES)

        if OUT.exists():
            OUT.unlink()
        with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(stage.rglob("*")):
                if not path.is_file():
                    continue
                # Three generators rewrite their assets into the workspace on every
                # build, so those entries carry the build's mtime and the archive
                # differs byte-wise between otherwise identical runs. Pin the
                # timestamp to the zip epoch so a rebuild is reproducible.
                rel = path.relative_to(stage_parent).as_posix()
                info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zf.writestr(info, path.read_bytes())
    finally:
        shutil.rmtree(stage_parent, ignore_errors=True)
    return OUT


def validate(zpath: Path) -> tuple[int, int]:
    required = [
        f"{STAGE_NAME}/pgaa/cli.py",
        f"{STAGE_NAME}/scripts/run_toy_example.py",
        f"{STAGE_NAME}/scripts/build_submission_zip.py",
        f"{STAGE_NAME}/scripts/verify_dataset_manifest.py",
        f"{STAGE_NAME}/scripts/verify_bioinformatics_upload_ready.py",
        f"{STAGE_NAME}/scripts/finalize_archive_metadata.py",
        f"{STAGE_NAME}/DATASET_MANIFEST.tsv",
        f"{STAGE_NAME}/docs/SUBMISSION_PACKAGE_INDEX.md",
        f"{STAGE_NAME}/docs/PUBLICATION_GAP_AUDIT.md",
        f"{STAGE_NAME}/docs/AUTHOR_DATA_REQUEST_GSE335846.md",
        f"{STAGE_NAME}/docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md",
        f"{STAGE_NAME}/docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md",
        f"{STAGE_NAME}/docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md",
        f"{STAGE_NAME}/evidence/gse335846_source_data_numeric_audit.tsv",
        f"{STAGE_NAME}/evidence/gse335846_external_dynamic_corroboration.tsv",
        f"{STAGE_NAME}/docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md",
        f"{STAGE_NAME}/docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md",
        f"{STAGE_NAME}/evidence/gse335846_phosphoproteomics_corroboration.tsv",
        f"{STAGE_NAME}/evidence/gse335846_phosphoproteomics_selected_markers.tsv",
        f"{STAGE_NAME}/evidence/gse335846_phosphoproteomics_boundary_scan.tsv",
        f"{STAGE_NAME}/figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png",
        f"{STAGE_NAME}/figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf",
        f"{STAGE_NAME}/docs/GSE150949_PC9_EVOLUTION_AUDIT.md",
        f"{STAGE_NAME}/docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md",
        f"{STAGE_NAME}/evidence/gse150949_pc9_module_coverage.tsv",
        f"{STAGE_NAME}/evidence/gse150949_pc9_route_scores.tsv",
        f"{STAGE_NAME}/evidence/gse150949_pc9_sample_summary.tsv",
        f"{STAGE_NAME}/evidence/gse150949_pc9_group_summary.tsv",
        f"{STAGE_NAME}/docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md",
        f"{STAGE_NAME}/docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md",
        f"{STAGE_NAME}/docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md",
        f"{STAGE_NAME}/LICENSE",
        f"{STAGE_NAME}/CITATION.cff",
        f"{STAGE_NAME}/codemeta.json",
        f"{STAGE_NAME}/RELEASE_ARCHIVE_CHECKLIST.md",
        f"{STAGE_NAME}/figures_png/figure_pgaa_workflow.png",
        f"{STAGE_NAME}/figures_png/gse335846_dynamic_corroboration_scorecard.png",
        f"{STAGE_NAME}/figures_png/gse335846_dynamic_corroboration_scorecard.pdf",
        f"{STAGE_NAME}/MANUSCRIPT.pdf",
        f"{STAGE_NAME}/SUPPLEMENTARY.pdf",
        f"{STAGE_NAME}/figures_png/gse150949_pc9_evolution_scorecard.png",
        f"{STAGE_NAME}/figures_png/gse150949_pc9_evolution_scorecard.pdf",
    ]
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        forbidden = [
            name for name in names if any(term in name for term in FORBIDDEN_SUBSTRINGS)
        ]
        missing = [name for name in required if name not in names]
        if forbidden or missing:
            for name in forbidden[:20]:
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
