#!/usr/bin/env python3
"""Focused consistency checks for the PGAA manuscript package."""
from pathlib import Path
import zipfile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = [
    "figure_workflow",
    "Supplementary Note S7",
    "will be deposited upon acceptance",
    "Good, 2013",
    "rank 1661",
    "1661/2012",
    "p = 0.84",
    "0.8406",
    "0.8405797101449275",
    "0.432",
    "29-fold",
    "ELANE rank 586",
]

TEXT_FILES = [
    ROOT / "MANUSCRIPT.md",
    ROOT / "SUPPLEMENTARY.md",
    ROOT / "build_pdf.py",
    ROOT / "scripts" / "figure_norman_nbins20.py",
    ROOT / "scripts" / "table_sceptre_vs_pgaa.py",
    ROOT / "scripts" / "generate_paper_tables.py",
    ROOT / "scripts" / "tables_paper.md",
    ROOT / "scripts" / "prt_s2_nbins20_summary.csv",
    ROOT / "scripts" / "prt_s2_summary.csv",
    ROOT / "scripts" / "prt_s2_calibrated_summary.csv",
    ROOT / "scripts" / "table1_datasets_summary.csv",
    ROOT / "scripts" / "run_toy_example.py",
    ROOT / "scripts" / "build_submission_zip.py",
    ROOT / "pgaa" / "cli.py",
    ROOT / "pyproject.toml",
    ROOT / "CITATION.cff",
    ROOT / "codemeta.json",
    ROOT / "RELEASE_ARCHIVE_CHECKLIST.md",
    ROOT / "DATASET_MANIFEST.tsv",
    ROOT / "figure_source_data" / "FIGURE_PROMPTS.md",
    ROOT / "scripts" / "verify_dataset_manifest.py",
    ROOT / "scripts" / "verify_bioinformatics_upload_ready.py",
    ROOT / "scripts" / "finalize_archive_metadata.py",
]

ALLOW_FORBIDDEN_BY_FILE = {
    ROOT / "scripts" / "build_submission_zip.py": {
        "figure_workflow",
    },
}

ZIP_FORBIDDEN_TERMS = [
    "figure_workflow",
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
]


def check_forbidden() -> list[str]:
    errors = []
    for path in TEXT_FILES:
        if not path.exists():
            errors.append(f"Missing expected file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(errors="replace")
        allowed_terms = ALLOW_FORBIDDEN_BY_FILE.get(path, set())
        for term in FORBIDDEN:
            if term in allowed_terms:
                continue
            if term in text:
                errors.append(f"{path.relative_to(ROOT)} contains forbidden term: {term}")
    return errors


def check_norman_numbers() -> list[str]:
    errors = []
    s1 = pd.read_csv(ROOT / "scripts" / "norman2019_prt_s1_full.csv")
    p = s1["p_value_perm"].fillna(1.0).astype(float)
    genes = list(s1["gene"])
    elane_idx = genes.index("ELANE")
    elane_rank = int((p < p.iloc[elane_idx]).sum()) + 1
    elane_p = round(float(p.iloc[elane_idx]), 4)

    table = pd.read_csv(ROOT / "scripts" / "table_sceptre_vs_pgaa.csv")
    s1_row = table[table["method"].str.contains("Wasserstein", regex=False)].iloc[0]
    if int(s1_row["elane_rank"]) != elane_rank:
        errors.append(
            f"S1 ELANE rank mismatch: table={int(s1_row['elane_rank'])}, csv={elane_rank}"
        )
    if round(float(s1_row["elane_p"]), 4) != elane_p:
        errors.append(
            f"S1 ELANE p mismatch: table={float(s1_row['elane_p'])}, csv={elane_p}"
        )

    manuscript = (ROOT / "MANUSCRIPT.md").read_text()
    if "1452/2012" not in manuscript or "$p = 0.223$" not in manuscript:
        errors.append("MANUSCRIPT.md does not contain the current S1 ELANE result")
    if "rank 57" not in manuscript and "position 57" not in manuscript:
        errors.append("MANUSCRIPT.md does not contain the current S2 ELANE rank")

    source = pd.read_csv(ROOT / "figure_source_data" / "fig3_elane_ranks.csv")
    src_s1 = source[source["Method"] == "Wasserstein"].iloc[0]
    if int(src_s1["ELANE_rank"]) != 1452:
        errors.append("figure_source_data/fig3_elane_ranks.csv has stale S1 ELANE rank")
    if round(float(src_s1["ELANE_p"]), 4) != 0.2234:
        errors.append("figure_source_data/fig3_elane_ranks.csv has stale S1 ELANE p-value")
    if int(src_s1["n_sig"]) != 1083:
        errors.append("figure_source_data/fig3_elane_ranks.csv has stale S1 n_sig")
    return errors


def check_adamson_ci() -> list[str]:
    errors = []
    ci = ROOT / "scripts" / "adamson2016_method_summary_ci.csv"
    if not ci.exists() or ci.stat().st_size == 0:
        errors.append("Missing Adamson method CI summary: scripts/adamson2016_method_summary_ci.csv")
        return errors
    df = pd.read_csv(ci)
    expected_methods = {
        "S1 Wasserstein",
        "S2 persistence",
        "Wilcoxon rank-sum",
        "t-test",
        "MAST",
    }
    if set(df["method"]) != expected_methods:
        errors.append("Adamson method CI summary has unexpected method rows")
    if not (df["n_perturbations"] == 5).all():
        errors.append("Adamson method CI summary should use five perturbations")
    return errors


def check_assets() -> list[str]:
    errors = []
    required = [
        "figures_png/figure_1.png",
        "figures_png/figure_2.png",
        "figures_png/figure_3.png",
        "figures_png/figure_4.png",
        "figures_png/figure_adamson_benchmark.png",
        "figures_png/figure_5.png",
        "figures_png/figure_elane_histogram.png",
        "figures_png/figure_s2_calibration_qq.png",
        "figures_png/figure_s2_bhlhe40.png",
        "figures_png/figure_pgaa_workflow.png",
    ]
    for rel in required:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"Missing or empty asset: {rel}")

    supp_text = (ROOT / "SUPPLEMENTARY.md").read_text(errors="replace")
    for rel in [
        "figures_png/figure_s2_calibration_qq.png",
        "figures_png/figure_s2_bhlhe40.png",
        "figures_png/figure_pgaa_workflow.png",
    ]:
        if rel not in supp_text:
            errors.append(f"SUPPLEMENTARY.md does not include supplementary figure asset: {rel}")
    return errors


def check_toy_example_documented() -> list[str]:
    errors = []
    toy = ROOT / "scripts" / "run_toy_example.py"
    readme = ROOT / "README.md"
    if not toy.exists() or toy.stat().st_size == 0:
        errors.append("Missing runnable toy example: scripts/run_toy_example.py")
    text = readme.read_text(errors="replace") if readme.exists() else ""
    if "python3 scripts/run_toy_example.py" not in text:
        errors.append("README.md does not document the runnable toy example")
    return errors


def check_cli_documented() -> list[str]:
    errors = []
    cli = ROOT / "pgaa" / "cli.py"
    readme = ROOT / "README.md"
    pyproject = ROOT / "pyproject.toml"
    if not cli.exists() or cli.stat().st_size == 0:
        errors.append("Missing CSV command-line runner: pgaa/cli.py")
    readme_text = readme.read_text(errors="replace") if readme.exists() else ""
    if "python3 -m pgaa.cli" not in readme_text:
        errors.append("README.md does not document the CSV command-line runner")
    pyproject_text = pyproject.read_text(errors="replace") if pyproject.exists() else ""
    if 'pgaa-run = "pgaa.cli:main"' not in pyproject_text:
        errors.append("pyproject.toml does not expose the pgaa-run console script")
    if "Predictive Gene Activation Analysis" in pyproject_text:
        errors.append("pyproject.toml still contains the old package description")
    return errors


def check_zip_builder() -> list[str]:
    errors = []
    builder = ROOT / "scripts" / "build_submission_zip.py"
    readme = ROOT / "README.md"
    if not builder.exists() or builder.stat().st_size == 0:
        errors.append("Missing clean zip builder: scripts/build_submission_zip.py")
        return errors
    text = readme.read_text(errors="replace") if readme.exists() else ""
    if "python3 scripts/build_submission_zip.py" not in text:
        errors.append("README.md does not document the clean zip builder")
    builder_text = builder.read_text(errors="replace")
    for term in ZIP_FORBIDDEN_TERMS:
        if term not in builder_text:
            errors.append(f"Clean zip builder does not explicitly forbid: {term}")

    zpath = ROOT / "PGAA_supplementary_code.zip"
    if zpath.exists():
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
        for term in ZIP_FORBIDDEN_TERMS:
            hits = [name for name in names if term in name]
            if hits:
                errors.append(f"Clean zip contains forbidden term {term}: {hits[0]}")
    return errors


def check_release_metadata() -> list[str]:
    errors = []
    required_files = [
        ROOT / "CITATION.cff",
        ROOT / "codemeta.json",
        ROOT / "RELEASE_ARCHIVE_CHECKLIST.md",
        ROOT / "UPLOAD_FILE_MANIFEST.tsv",
    ]
    for path in required_files:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"Missing release metadata file: {path.relative_to(ROOT)}")
    citation = (ROOT / "CITATION.cff").read_text(errors="replace")
    codemeta = (ROOT / "codemeta.json").read_text(errors="replace")
    for text, rel in [(citation, "CITATION.cff"), (codemeta, "codemeta.json")]:
        if "https://github.com/xutaoguo55/pgaa" not in text:
            errors.append(f"{rel} does not contain the canonical repository URL")
        if "0.1.0" not in text:
            errors.append(f"{rel} does not contain package version 0.1.0")
    readme = (ROOT / "README.md").read_text(errors="replace")
    if "CITATION.cff" not in readme or "codemeta.json" not in readme:
        errors.append("README.md does not mention release metadata files")
    return errors


def check_dataset_manifest() -> list[str]:
    errors = []
    manifest = ROOT / "DATASET_MANIFEST.tsv"
    verifier = ROOT / "scripts" / "verify_dataset_manifest.py"
    readme = ROOT / "README.md"
    if not manifest.exists() or manifest.stat().st_size == 0:
        errors.append("Missing dataset manifest: DATASET_MANIFEST.tsv")
    if not verifier.exists() or verifier.stat().st_size == 0:
        errors.append("Missing dataset manifest verifier: scripts/verify_dataset_manifest.py")
    readme_text = readme.read_text(errors="replace") if readme.exists() else ""
    if "DATASET_MANIFEST.tsv" not in readme_text:
        errors.append("README.md does not mention DATASET_MANIFEST.tsv")
    return errors


def check_upload_manifest_documented() -> list[str]:
    errors = []
    manifest = ROOT / "UPLOAD_FILE_MANIFEST.tsv"
    verifier = ROOT / "scripts" / "verify_upload_file_manifest.py"
    builder = ROOT / "scripts" / "build_bioinformatics_upload_packet.py"
    readme_text = (ROOT / "README.md").read_text(errors="replace")
    checklist_text = (ROOT / "SUBMISSION_CHECKLIST.md").read_text(errors="replace")
    if not manifest.exists() or manifest.stat().st_size == 0:
        errors.append("Missing upload-file manifest: UPLOAD_FILE_MANIFEST.tsv")
    if not verifier.exists() or verifier.stat().st_size == 0:
        errors.append("Missing upload-file manifest verifier: scripts/verify_upload_file_manifest.py")
    if not builder.exists() or builder.stat().st_size == 0:
        errors.append("Missing Bioinformatics upload-packet builder: scripts/build_bioinformatics_upload_packet.py")
    for text, rel in [(readme_text, "README.md"), (checklist_text, "SUBMISSION_CHECKLIST.md")]:
        if "UPLOAD_FILE_MANIFEST.tsv" not in text:
            errors.append(f"{rel} does not mention UPLOAD_FILE_MANIFEST.tsv")
        if "python3 scripts/verify_upload_file_manifest.py" not in text:
            errors.append(f"{rel} does not document the upload-file manifest verifier")
        if "python3 scripts/build_bioinformatics_upload_packet.py" not in text:
            errors.append(f"{rel} does not document the Bioinformatics upload-packet builder")
    return errors


def check_upload_gate_documented() -> list[str]:
    errors = []
    gate = ROOT / "scripts" / "verify_bioinformatics_upload_ready.py"
    finalizer = ROOT / "scripts" / "finalize_archive_metadata.py"
    if not gate.exists() or gate.stat().st_size == 0:
        errors.append("Missing final upload gate: scripts/verify_bioinformatics_upload_ready.py")
    if not finalizer.exists() or finalizer.stat().st_size == 0:
        errors.append("Missing archive metadata finalizer: scripts/finalize_archive_metadata.py")
    readme_text = (ROOT / "README.md").read_text(errors="replace")
    checklist_text = (ROOT / "RELEASE_ARCHIVE_CHECKLIST.md").read_text(errors="replace")
    if "python3 scripts/verify_bioinformatics_upload_ready.py" not in readme_text:
        errors.append("README.md does not document the Bioinformatics upload gate")
    if "python3 scripts/verify_bioinformatics_upload_ready.py" not in checklist_text:
        errors.append("RELEASE_ARCHIVE_CHECKLIST.md does not document the upload gate")
    gate_text = gate.read_text(errors="replace")
    required_gate_terms = [
        "COVER_LETTER_BIOINFORMATICS.md",
        "[insert archive DOI or persistent URL]",
        "[Author names]",
        "[Affiliations]",
        "[Contact email]",
    ]
    for term in required_gate_terms:
        if term not in gate_text:
            errors.append(f"Bioinformatics upload gate does not cover: {term}")
    finalizer_text = finalizer.read_text(errors="replace")
    required_finalizer_terms = [
        "COVER_LETTER_BIOINFORMATICS.md",
        "[insert archive DOI or persistent URL]",
        "[archive DOI or persistent URL]",
        "[repository URL]",
        "citation_identifier",
        "validate_url",
    ]
    for term in required_finalizer_terms:
        if term not in finalizer_text:
            errors.append(f"Archive metadata finalizer does not cover: {term}")
    return errors


def check_status_documents_current() -> list[str]:
    errors = []
    stale_terms = [
        "181 entries",
        "183 entries",
        "184 entries",
        "8.9 MB compressed",
        "Supplementary Tables S1-S11",
    ]
    paths = [
        ROOT / "SUBMISSION_READINESS_AUDIT.md",
        ROOT / "SUBMISSION_CHECKLIST.md",
        ROOT / "CURRENT_BIOINFORMATICS_REVIEW_2026-06-09.md",
    ]
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        for term in stale_terms:
            if term in text:
                errors.append(f"{path.relative_to(ROOT)} contains stale zip status: {term}")
    return errors


def main() -> None:
    errors = []
    errors.extend(check_forbidden())
    errors.extend(check_norman_numbers())
    errors.extend(check_adamson_ci())
    errors.extend(check_assets())
    errors.extend(check_toy_example_documented())
    errors.extend(check_cli_documented())
    errors.extend(check_zip_builder())
    errors.extend(check_release_metadata())
    errors.extend(check_dataset_manifest())
    errors.extend(check_upload_manifest_documented())
    errors.extend(check_upload_gate_documented())
    errors.extend(check_status_documents_current())

    if errors:
        print("CONSISTENCY CHECK FAILED")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    print("CONSISTENCY CHECK PASSED")
    print("Norman S1/S2 values, forbidden terms, and required figure assets are in sync.")


if __name__ == "__main__":
    main()
