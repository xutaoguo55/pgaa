"""Audit whether source tables can support event-peptide compilation."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.event_peptide_compiler import REQUIRED_EVENT_COLUMNS
from pgaa.core.immune_evidence import scan_placeholder_artifacts


GENE_LEVEL_COLUMNS = {
    "gene",
    "target",
    "target_gene",
    "perturbation",
    "pgaa_rank",
    "s1_wasserstein",
    "W_observed",
    "S2",
    "p_value",
    "fdr",
}


def classify_source_table(table: pd.DataFrame, source_id: str) -> tuple[str, str]:
    """Classify whether a table has enough fields for event-peptide compilation."""
    columns = set(table.columns)
    missing_event_columns = sorted(REQUIRED_EVENT_COLUMNS - columns)
    placeholder_hits = scan_placeholder_artifacts(table, source_id)
    if not missing_event_columns and not placeholder_hits:
        return "event_ready", "required event columns present and no smoke/template tokens detected"
    if not missing_event_columns and placeholder_hits:
        return "event_template_or_smoke", "; ".join(placeholder_hits[:5])
    if "peptide_sequence" in columns:
        return (
            "peptide_only_without_complete_event",
            f"peptide rows exist but event compiler columns are missing: {missing_event_columns}",
        )
    if columns & GENE_LEVEL_COLUMNS:
        present = sorted(columns & GENE_LEVEL_COLUMNS)
        return (
            "gene_level_only",
            f"gene-level PGAA/expression columns present ({present}); missing event columns: "
            f"{missing_event_columns}",
        )
    return "unsupported_schema", f"missing event columns: {missing_event_columns}"


def audit_event_sources(manifest: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Audit candidate source files listed in a manifest.

    The manifest must contain `source_id` and `path`. Optional columns are
    preserved in the output for traceability.
    """
    required_manifest_columns = {"source_id", "path"}
    missing = sorted(required_manifest_columns - set(manifest.columns))
    if missing:
        raise ValueError(f"source manifest is missing required columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, item in manifest.iterrows():
        source_id = str(item["source_id"])
        relative_path = str(item["path"])
        path = root / relative_path
        row: dict[str, object] = {
            "source_id": source_id,
            "path": relative_path,
            "exists": path.exists(),
            "row_count": 0,
            "column_count": 0,
            "status": "missing",
            "detail": "source file is missing",
        }
        for column in manifest.columns:
            if column not in row:
                row[column] = item[column]

        if path.exists():
            sep = "\t" if path.suffix.lower() == ".tsv" else ","
            table = pd.read_csv(path, sep=sep, nrows=5000)
            status, detail = classify_source_table(table, source_id)
            row.update(
                {
                    "row_count": int(len(table)),
                    "column_count": int(len(table.columns)),
                    "status": status,
                    "detail": detail,
                    "columns": ";".join(map(str, table.columns)),
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def render_event_source_audit_markdown(audit: pd.DataFrame) -> str:
    """Render a concise audit report for source-level feasibility."""
    event_ready = audit[audit["status"] == "event_ready"]
    gene_only = audit[audit["status"] == "gene_level_only"]
    lines = [
        "# PGAA Event-Source Audit",
        "",
        f"Event-ready source tables: {len(event_ready)}",
        f"Gene-level-only source tables: {len(gene_only)}",
        "",
        "| Source | Status | Rows inspected | Detail |",
        "|---|---|---:|---|",
    ]
    for _, row in audit.iterrows():
        detail = str(row["detail"]).replace("|", "/")
        lines.append(
            f"| `{row['source_id']}` | {row['status']} | {row['row_count']} | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if event_ready.empty:
        lines.append(
            "No inspected source table currently supports real event-peptide compilation. "
            "Gene-level PGAA outputs must not be converted into altered peptide events unless "
            "a real mutation, splice junction, fusion, editing, or other sequence-changing "
            "event table is added."
        )
    else:
        lines.append(
            "At least one inspected source table has the required event compiler columns. "
            "Run `scripts/compile_event_peptides.py` on those rows after manual source review."
        )
    lines.append("")
    return "\n".join(lines)
