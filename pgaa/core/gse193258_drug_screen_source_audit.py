"""Audit the source tables behind the GSE193258 osimertinib DTP drug screen."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


REQUIRED_REPLICATE_COLUMNS = {
    "Cell line",
    "Drug",
    "Dose (nM)",
    "Putative Target",
    "Screen format",
    "AUC osi. DTP control",
    "AUC osi. DTP combo",
    "AUC DMSO",
    "AUC monotherapy",
}

REQUIRED_SUMMARY_COLUMNS = {
    "Cell line",
    "Drug ID",
    "Putative target",
    "Screen format",
    "Avg. AUC DTP",
    "Avg. AUC DTP Combination",
    "Avg. AUC DMSO",
    "Avg. AUC monotherapy",
    "Combination activity",
    "Monotherapy activity",
    "Label",
    "Screen hit status",
}

MATCHED_BRANCH_LINES = {"PC9", "HCC827", "H1975", "HCC2935"}
REPLICATE_SOURCE_FILE = "41698_2022_337_MOESM2_ESM.xlsx"
SUMMARY_SOURCE_FILE = "41698_2022_337_MOESM3_ESM.xlsx"
RNASEQ_SOURCE_FILE = "GSE193258_RNAseq_log2TPM_abundance.tsv.gz"


def _sha256_or_na(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _coverage_label(values: set[str]) -> str:
    return ", ".join(sorted(values)) if values else "none"


def build_gse193258_target_context(
    replicate: pd.DataFrame, summary: pd.DataFrame
) -> pd.DataFrame:
    """Summarize the target-class breadth of the GSE193258 screen package."""
    rows = []
    for table_id, frame, target_col in [
        ("Supplementary_Data_1", replicate, "Putative Target"),
        ("Supplementary_Data_2", summary, "Putative target"),
    ]:
        counts = frame[target_col].astype(str).value_counts()
        for rank, (target_class, n_rows) in enumerate(counts.items(), start=1):
            subset = frame[frame[target_col].astype(str) == target_class]
            rows.append(
                {
                    "table_id": table_id,
                    "target_class": target_class,
                    "n_rows": int(n_rows),
                    "rank_within_table": int(rank),
                    "n_unique_cell_lines": int(subset["Cell line"].nunique()),
                    "n_unique_drugs": int(
                        subset["Drug"].nunique()
                        if "Drug" in subset.columns
                        else subset["Drug ID"].nunique()
                    ),
                    "highlight": target_class in {"ATM", "HDAC"},
                }
            )
    return pd.DataFrame(rows)


def build_gse193258_drug_screen_source_audit(
    source_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Summarize the public source tables for the GSE193258 screen package."""
    replicate_xlsx = source_dir / REPLICATE_SOURCE_FILE
    summary_xlsx = source_dir / SUMMARY_SOURCE_FILE
    rnaseq_tsv = source_dir / RNASEQ_SOURCE_FILE
    replicate = pd.read_excel(replicate_xlsx, header=2)
    summary = pd.read_excel(summary_xlsx, header=2)
    rnaseq = pd.read_csv(rnaseq_tsv, sep="\t", index_col=0)

    missing_replicate = sorted(REQUIRED_REPLICATE_COLUMNS - set(replicate.columns))
    if missing_replicate:
        raise ValueError(f"Replicate table is missing columns: {missing_replicate}")
    missing_summary = sorted(REQUIRED_SUMMARY_COLUMNS - set(summary.columns))
    if missing_summary:
        raise ValueError(f"Summary table is missing columns: {missing_summary}")

    rep_cell_lines = set(replicate["Cell line"].astype(str))
    sum_cell_lines = set(summary["Cell line"].astype(str))
    matched_from_replicate = rep_cell_lines & MATCHED_BRANCH_LINES
    matched_from_summary = sum_cell_lines & MATCHED_BRANCH_LINES
    screen_only = sorted((rep_cell_lines | sum_cell_lines) - MATCHED_BRANCH_LINES)

    summary_rows = [
        {
            "table_id": "Supplementary_Data_1",
            "source_file": replicate_xlsx.name,
            "sheet_name": "Table S3",
            "role": "replicate_level_source",
            "local_artifact": _display_path(replicate_xlsx, source_dir.parent),
            "local_artifact_status": "present" if replicate_xlsx.exists() else "missing",
            "local_sha256": _sha256_or_na(replicate_xlsx),
            "n_rows": int(len(replicate)),
            "n_columns": int(replicate.shape[1]),
            "unique_cell_lines": int(replicate["Cell line"].nunique()),
            "unique_drugs": int(replicate["Drug"].nunique()),
            "screen_formats": _coverage_label(
                set(replicate["Screen format"].astype(str).str.lower())
            ),
            "matched_branch_lines": _coverage_label(matched_from_replicate),
            "screen_only_lines": _coverage_label(set(screen_only)),
            "atm_rows": int((replicate["Drug"] == "AZD0156").sum()),
            "hdac_rows": int(
                replicate["Drug"]
                .astype(str)
                .str.contains("HDAC|Quisinostat", case=False, regex=True)
                .sum()
            ),
            "source_ceiling": "replicate_rows_exist_but_branch_calibration_is_sample_size_limited",
        },
        {
            "table_id": "Supplementary_Data_2",
            "source_file": summary_xlsx.name,
            "sheet_name": "Supplementary_Table_S4",
            "role": "summary_level_source",
            "local_artifact": _display_path(summary_xlsx, source_dir.parent),
            "local_artifact_status": "present" if summary_xlsx.exists() else "missing",
            "local_sha256": _sha256_or_na(summary_xlsx),
            "n_rows": int(len(summary)),
            "n_columns": int(summary.shape[1]),
            "unique_cell_lines": int(summary["Cell line"].nunique()),
            "unique_drugs": int(summary["Drug ID"].nunique()),
            "screen_formats": _coverage_label(
                set(summary["Screen format"].astype(str).str.lower())
            ),
            "matched_branch_lines": _coverage_label(matched_from_summary),
            "screen_only_lines": _coverage_label(set(screen_only)),
            "atm_rows": int((summary["Drug ID"] == "AZD0156").sum()),
            "hdac_rows": int(
                summary["Drug ID"]
                .astype(str)
                .str.contains("HDAC|Quisinostat", case=False, regex=True)
                .sum()
            ),
            "source_ceiling": "summary_table_exists_but_four_matched_models_remain_the_branch-link_limit",
        },
        {
            "table_id": "GSE193258_RNAseq",
            "source_file": RNASEQ_SOURCE_FILE,
            "sheet_name": "n/a",
            "role": "frozen_branch_assignment_source",
            "local_artifact": _display_path(rnaseq_tsv, source_dir.parent),
            "local_artifact_status": "present" if rnaseq_tsv.exists() else "missing",
            "local_sha256": _sha256_or_na(rnaseq_tsv),
            "n_rows": int(rnaseq.shape[0]),
            "n_columns": int(rnaseq.shape[1]),
            "unique_cell_lines": 4,
            "unique_drugs": 0,
            "screen_formats": "n/a",
            "matched_branch_lines": _coverage_label(MATCHED_BRANCH_LINES),
            "screen_only_lines": "n/a",
            "atm_rows": 0,
            "hdac_rows": 0,
            "source_ceiling": "expression_source_for_frozen_assignment",
        },
    ]

    target_context = build_gse193258_target_context(replicate, summary)

    detail_rows = []
    for table_id, frame, drug_col in [
        ("Supplementary_Data_1", replicate, "Drug"),
        ("Supplementary_Data_2", summary, "Drug ID"),
    ]:
        for drug in ("AZD0156", "Quisinostat"):
            subset = frame[frame[drug_col].astype(str) == drug]
            for cell_line in sorted(subset["Cell line"].astype(str).unique()):
                detail_rows.append(
                    {
                        "table_id": table_id,
                        "drug_id": drug,
                        "cell_line": cell_line,
                        "n_rows": int((subset["Cell line"].astype(str) == cell_line).sum()),
                    }
                )

    audit = pd.DataFrame(summary_rows)
    detail = pd.DataFrame(detail_rows)
    return audit, detail, target_context


def render_gse193258_drug_screen_source_audit(
    audit: pd.DataFrame, detail: pd.DataFrame, target_context: pd.DataFrame
) -> str:
    """Render a manuscript-facing source audit for the GSE193258 screen package."""
    replicate = audit[audit["table_id"] == "Supplementary_Data_1"].iloc[0]
    summary = audit[audit["table_id"] == "Supplementary_Data_2"].iloc[0]
    rnaseq = audit[audit["table_id"] == "GSE193258_RNAseq"].iloc[0]
    target_rows = []
    for table_id in ["Supplementary_Data_1", "Supplementary_Data_2"]:
        table = target_context[target_context["table_id"] == table_id].sort_values(
            ["rank_within_table", "target_class"]
        )
        top = table.head(10)
        target_rows.append(f"### {table_id}")
        target_rows.append("")
        target_rows.append("| Rank | Target class | Rows | Cell lines | Drugs | Highlight |")
        target_rows.append("|---|---|---:|---:|---:|---|")
        for _, row in top.iterrows():
            target_rows.append(
                f"| {int(row['rank_within_table'])} | {row['target_class']} | {int(row['n_rows'])} | {int(row['n_unique_cell_lines'])} | {int(row['n_unique_drugs'])} | {'yes' if bool(row['highlight']) else 'no'} |"
            )
        highlight = table[table["highlight"]]
        if not highlight.empty:
            highlight_rows = ", ".join(
                f"{row.target_class} (rank {int(row.rank_within_table)}, rows {int(row.n_rows)})"
                for row in highlight.itertuples()
            )
        else:
            highlight_rows = "none"
        target_rows.extend(
            [
                "",
                f"- Highlight targets in this table: {highlight_rows}",
                "",
            ]
        )
    lines = [
        "# GSE193258 Drug-Screen Source Audit",
        "",
        "The public GSE193258 screen package is source-table-backed. Supplementary Data 1 provides replicate-level AUC values, Supplementary Data 2 provides averaged screen values plus hit calls, and the frozen expression matrix is also present locally for branch assignment. The current branch calibration is still sample-size limited because only four cell lines overlap with the frozen branch assignments, but the screen itself is not a black box.",
        "",
        "## Source Tables",
        "",
        "| Table | Role | Artifact | Status | Rows | Columns | Cell lines | Drugs | Screen formats | Matched branch lines | Screen-only lines |",
        "|---|---|---|---|---:|---:|---:|---:|---|---|---|",
        f"| {replicate['table_id']} | {replicate['role']} | {replicate['local_artifact']} | {replicate['local_artifact_status']} | {replicate['n_rows']} | {replicate['n_columns']} | {replicate['unique_cell_lines']} | {replicate['unique_drugs']} | {replicate['screen_formats']} | {replicate['matched_branch_lines']} | {replicate['screen_only_lines']} |",
        f"| {summary['table_id']} | {summary['role']} | {summary['local_artifact']} | {summary['local_artifact_status']} | {summary['n_rows']} | {summary['n_columns']} | {summary['unique_cell_lines']} | {summary['unique_drugs']} | {summary['screen_formats']} | {summary['matched_branch_lines']} | {summary['screen_only_lines']} |",
        f"| {rnaseq['table_id']} | {rnaseq['role']} | {rnaseq['local_artifact']} | {rnaseq['local_artifact_status']} | {rnaseq['n_rows']} | {rnaseq['n_columns']} | {rnaseq['unique_cell_lines']} | {rnaseq['unique_drugs']} | {rnaseq['screen_formats']} | {rnaseq['matched_branch_lines']} | {rnaseq['screen_only_lines']} |",
        "",
        "## Target Breadth",
        "",
        "The GSE193258 screen spans a broad target landscape rather than a single-target assay. ATM and HDAC are highlighted because they are the branch-linked candidates used in the manuscript, but they sit inside a panel that includes many other target classes.",
        "",
        *target_rows,
        "## Source-Coverage Notes",
        "",
        f"- Replicate table coverage includes ATM rows ({replicate['atm_rows']}) and HDAC-related rows ({replicate['hdac_rows']}).",
        f"- Summary table coverage includes ATM rows ({summary['atm_rows']}) and HDAC-related rows ({summary['hdac_rows']}).",
        "- The frozen RNA-seq matrix is also present locally and is the source basis for the prospective branch assignment layer.",
        "- The matched branch calibration still uses only PC9, HCC827, H1975, and HCC2935 because the frozen branch scores are available only for those four transcriptome-matched models.",
        "- The screen-only cell lines are HCC2279, HCC4006, and II-18; they are part of the public screen source package but remain outside the frozen branch calibration contract.",
        "",
        "## Detail Check",
        "",
        "| Table | Drug | Cell line | Rows |",
        "|---|---|---|---:|",
    ]
    if detail.empty:
        lines.append("| none | none | none | 0 |")
    else:
        for _, row in detail.iterrows():
            lines.append(
                f"| {row['table_id']} | {row['drug_id']} | {row['cell_line']} | {row['n_rows']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This source audit does not change the branch-vulnerability ceiling. It does make the calibration traceable: the GSE193258 drug-screen result is sourced from explicit supplementary tables and a local RNA-seq matrix, not inferred from the manuscript figure alone. The remaining limitation is the four-model branch matching, not the absence of public source tables.",
            "",
        ]
    )
    return "\n".join(lines)


def write_gse193258_drug_screen_source_audit_package(
    source_dir: Path, evidence_out: Path, report_out: Path
) -> dict[str, Path]:
    """Write the source audit package for the GSE193258 screen data."""
    audit, detail, target_context = build_gse193258_drug_screen_source_audit(source_dir)
    evidence_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(evidence_out, sep="\t", index=False)
    report_out.write_text(
        render_gse193258_drug_screen_source_audit(audit, detail, target_context),
        encoding="utf-8",
    )
    target_context_out = evidence_out.with_name("gse193258_drug_screen_target_context.tsv")
    target_context.to_csv(target_context_out, sep="\t", index=False)
    return {"evidence": evidence_out, "target_context": target_context_out, "report": report_out}
