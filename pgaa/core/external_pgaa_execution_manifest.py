"""Build an auditable PGAA execution manifest for external reruns."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_CONTRACT_COLUMNS = {
    "candidate_dataset_id",
    "target_gene",
    "contract_status",
    "pgaa_s1_out",
    "pgaa_s2_out",
    "external_claim_state_out",
    "pgaa_command",
}

REQUIRED_EXTRACTION_COLUMNS = {
    "candidate_dataset_id",
    "target_gene",
    "extraction_status",
    "expression_csv",
    "metadata_csv",
    "n_perturbed_cells",
    "n_control_cells",
    "n_genes",
}


def _exists(value: object) -> bool:
    text = str(value)
    return bool(text) and Path(text).exists()


def _first_present(row: pd.Series, names: list[str]) -> object:
    for name in names:
        if name in row and pd.notna(row[name]):
            return row[name]
    return ""


def build_external_pgaa_execution_manifest(
    contract: pd.DataFrame,
    extraction: pd.DataFrame,
) -> pd.DataFrame:
    """Compile per-target PGAA execution readiness and output presence.

    This manifest does not run PGAA. It records whether the predeclared input
    files, PGAA outputs, and external claim-state outputs exist for each target.
    """
    missing_contract = sorted(REQUIRED_CONTRACT_COLUMNS - set(contract.columns))
    if missing_contract:
        raise ValueError(f"contract table is missing columns: {missing_contract}")
    missing_extraction = sorted(REQUIRED_EXTRACTION_COLUMNS - set(extraction.columns))
    if missing_extraction:
        raise ValueError(f"extraction table is missing columns: {missing_extraction}")

    merged = contract.merge(
        extraction,
        on=["candidate_dataset_id", "target_gene"],
        how="left",
        suffixes=("_contract", "_extraction"),
    )

    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        expression_csv = _first_present(
            row, ["expression_csv_extraction", "expression_csv", "expression_csv_contract"]
        )
        metadata_csv = _first_present(
            row, ["metadata_csv_extraction", "metadata_csv", "metadata_csv_contract"]
        )
        has_expression = _exists(expression_csv)
        has_metadata = _exists(metadata_csv)
        has_s1 = _exists(row["pgaa_s1_out"])
        has_s2 = _exists(row["pgaa_s2_out"])
        has_claim_state = _exists(row["external_claim_state_out"])

        contract_status = str(_first_present(row, ["contract_status_contract", "contract_status"]))
        extraction_status = str(row.get("extraction_status", "missing_extraction_row"))
        pgaa_command = str(row.get("pgaa_command", ""))
        if contract_status != "ready_for_pgaa_input_extraction":
            execution_status = "blocked_by_contract_status"
            next_action = "Resolve the external claim-state contract before PGAA execution."
        elif extraction_status != "extracted_pgaa_cli_inputs":
            execution_status = "blocked_by_input_extraction_status"
            next_action = "Extract audited expression and metadata CSVs before PGAA execution."
        elif not (has_expression and has_metadata):
            execution_status = "blocked_missing_pgaa_inputs"
            next_action = "Regenerate or restore the audited expression and metadata CSV files."
        elif not pgaa_command:
            execution_status = "blocked_missing_pgaa_command"
            next_action = "Rebuild the external claim-state contract to include the PGAA CLI command."
        elif has_s1 and has_s2 and has_claim_state:
            execution_status = "external_claim_state_present"
            next_action = "Compare this external claim state with the internal responder-state unit."
        elif has_s1 and has_s2:
            execution_status = "pgaa_outputs_present_waiting_claim_state_compilation"
            next_action = "Compile the PGAA outputs into the predeclared external claim-state audit."
        else:
            execution_status = "ready_for_pgaa_cli_execution"
            next_action = "Run the predeclared PGAA CLI command for this target."

        rows.append(
            {
                "candidate_dataset_id": row["candidate_dataset_id"],
                "target_gene": row["target_gene"],
                "contract_status": contract_status,
                "extraction_status": extraction_status,
                "execution_status": execution_status,
                "n_perturbed_cells": int(row.get("n_perturbed_cells", 0) or 0),
                "n_control_cells": int(row.get("n_control_cells", 0) or 0),
                "n_genes": int(row.get("n_genes", 0) or 0),
                "expression_csv": str(expression_csv),
                "metadata_csv": str(metadata_csv),
                "pgaa_s1_out": str(row["pgaa_s1_out"]),
                "pgaa_s2_out": str(row["pgaa_s2_out"]),
                "external_claim_state_out": str(row["external_claim_state_out"]),
                "has_expression_csv": bool(has_expression),
                "has_metadata_csv": bool(has_metadata),
                "has_pgaa_s1_out": bool(has_s1),
                "has_pgaa_s2_out": bool(has_s2),
                "has_external_claim_state_out": bool(has_claim_state),
                "pgaa_command": pgaa_command if execution_status == "ready_for_pgaa_cli_execution" else "",
                "claim_use": "execution_manifest_not_replication",
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows)


def summarize_external_pgaa_execution_manifest(manifest: pd.DataFrame) -> pd.DataFrame:
    """Summarize external PGAA execution manifest state."""
    required = {"contract_status", "extraction_status", "execution_status", "claim_use"}
    missing = sorted(required - set(manifest.columns))
    if missing:
        raise ValueError(f"execution manifest is missing columns: {missing}")
    return (
        manifest.groupby(
            ["contract_status", "extraction_status", "execution_status", "claim_use"],
            dropna=False,
        )
        .size()
        .reset_index(name="n_targets")
        .sort_values(["contract_status", "extraction_status", "execution_status"])
        .reset_index(drop=True)
    )


def render_external_pgaa_execution_manifest_report(
    manifest: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a conservative external PGAA execution manifest report."""
    lines = [
        "# PGAA External Execution Manifest",
        "",
        "This report audits whether external PGAA rerun inputs and outputs exist. It is not replication evidence; replication claims require compiled external claim-state outputs and agreement with predeclared internal responder-state units.",
        "",
        "## Summary",
        "",
        "| Contract status | Extraction status | Execution status | Allowed use | Targets |",
        "|---|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['contract_status']} | {row['extraction_status']} | "
            f"{row['execution_status']} | {row['claim_use']} | {row['n_targets']} |"
        )

    lines.extend(
        [
            "",
            "## Target Manifest",
            "",
            "| Target | Execution status | Inputs present | PGAA outputs present | Claim-state present |",
            "|---|---|---|---|---|",
        ]
    )
    for _, row in manifest.iterrows():
        inputs_present = bool(row["has_expression_csv"]) and bool(row["has_metadata_csv"])
        pgaa_present = bool(row["has_pgaa_s1_out"]) and bool(row["has_pgaa_s2_out"])
        lines.append(
            f"| {row['target_gene']} | {row['execution_status']} | {inputs_present} | "
            f"{pgaa_present} | {row['has_external_claim_state_out']} |"
        )

    ready = manifest[manifest["pgaa_command"].astype(str) != ""]
    if not ready.empty:
        lines.extend(["", "## Ready PGAA Commands", ""])
        for _, row in ready.iterrows():
            lines.extend([f"### {row['target_gene']}", "", "```bash", row["pgaa_command"], "```", ""])

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "A `ready_for_pgaa_cli_execution` row means the audited input files and command exist. It does not mean PGAA has been run, and it does not support external replication until both PGAA outputs and the external claim-state audit exist.",
        ]
    )
    return "\n".join(lines) + "\n"
