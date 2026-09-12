"""Execution contract for external PGAA/comparator claim-state reruns."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_READINESS_COLUMNS = {
    "candidate_dataset_id",
    "singlecell_h5ad",
    "target_control_gate",
    "required_targets",
    "singlecell_gate_status",
    "claim_use",
}


def _target_list(value: object) -> list[str]:
    return [item for item in str(value).split(";") if item]


def build_external_claim_state_contract(
    readiness: pd.DataFrame,
    output_dir: str | Path,
    group_column: str = "group",
    perturbed_value: str = "perturbed",
    control_value: str = "control",
    n_perms: int = 2000,
    n_bins: int = 20,
    target_only_permutation_p: bool = True,
) -> pd.DataFrame:
    """Build the per-target contract for an external claim-state rerun.

    This table intentionally remains useful when the h5ad is missing: it records
    the blocked state and the exact files/commands that become required after
    the readiness gate reaches ready_for_external_claim_state_rerun.
    """
    missing = sorted(REQUIRED_READINESS_COLUMNS - set(readiness.columns))
    if missing:
        raise ValueError(f"readiness table is missing columns: {missing}")
    if readiness.empty:
        raise ValueError("readiness table is empty")

    row = readiness.iloc[0]
    dataset_id = str(row["candidate_dataset_id"])
    h5ad = str(row["singlecell_h5ad"])
    gate_status = str(row["singlecell_gate_status"])
    target_control_gate = str(row["target_control_gate"])
    output_path = Path(output_dir)
    targets = _target_list(row["required_targets"])
    if not targets:
        targets = ["UNRESOLVED_TARGETS"]

    rows: list[dict[str, object]] = []
    for target in targets:
        prefix = output_path / dataset_id / target / target
        expression_csv = output_path / dataset_id / target / "expression.csv"
        metadata_csv = output_path / dataset_id / target / "metadata.csv"
        s1_out = prefix.with_suffix(".s1.csv")
        s2_out = prefix.with_suffix(".s2.csv")
        claim_state_out = output_path / dataset_id / target / "external_claim_state.tsv"

        if gate_status != "ready_for_external_claim_state_rerun":
            contract_status = "blocked_by_readiness_gate"
            next_action = (
                "Resolve the external rerun readiness gate before preparing PGAA/comparator inputs."
            )
            command = ""
        elif target_control_gate != "passed":
            contract_status = "blocked_by_target_control_gate"
            next_action = "Resolve target/control metadata before external PGAA/comparator rerun."
            command = ""
        else:
            contract_status = "ready_for_pgaa_input_extraction"
            next_action = (
                "Extract target/control expression and metadata from the h5ad, run PGAA-W/PGAA-H, "
                "then compile this target into the external claim-state audit."
            )
            command = (
                "python3 -m pgaa.cli "
                f"--expression {expression_csv} "
                f"--metadata {metadata_csv} "
                f"--target {target} "
                f"--out-prefix {prefix} "
                f"--group-column {group_column} "
                f"--perturbed-value {perturbed_value} "
                f"--control-value {control_value} "
                f"--n-perms {n_perms} "
                f"--n-bins {n_bins}"
            )
            if target_only_permutation_p:
                command = f"{command} --target-only-permutation-p"

        rows.append(
            {
                "candidate_dataset_id": dataset_id,
                "target_gene": target,
                "singlecell_h5ad": h5ad,
                "readiness_gate_status": gate_status,
                "target_control_gate": target_control_gate,
                "contract_status": contract_status,
                "expression_csv": str(expression_csv),
                "metadata_csv": str(metadata_csv),
                "pgaa_s1_out": str(s1_out),
                "pgaa_s2_out": str(s2_out),
                "external_claim_state_out": str(claim_state_out),
                "pgaa_command": command,
                "claim_use": "execution_contract_not_replication",
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows)


def summarize_external_claim_state_contract(contract: pd.DataFrame) -> pd.DataFrame:
    """Summarize external rerun contract status."""
    required = {"readiness_gate_status", "contract_status", "claim_use"}
    missing = sorted(required - set(contract.columns))
    if missing:
        raise ValueError(f"contract table is missing columns: {missing}")
    return (
        contract.groupby(["readiness_gate_status", "contract_status", "claim_use"], dropna=False)
        .size()
        .reset_index(name="n_targets")
        .sort_values(["readiness_gate_status", "contract_status"])
        .reset_index(drop=True)
    )


def render_external_claim_state_contract_report(
    contract: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a conservative external rerun contract report."""
    lines = [
        "# PGAA External Claim-State Rerun Contract",
        "",
        "This report defines the executable contract for an external PGAA/comparator claim-state rerun. It is not replication evidence; it becomes evidence only after the commands are run and the external claim-state audit is produced.",
        "",
        "## Summary",
        "",
        "| Readiness gate | Contract status | Allowed use | Targets |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['readiness_gate_status']} | {row['contract_status']} | "
            f"{row['claim_use']} | {row['n_targets']} |"
        )

    lines.extend(
        [
            "",
            "## Target Contract",
            "",
            "| Target | Status | PGAA-W output | PGAA-H output | Claim-state output |",
            "|---|---|---|---|---|",
        ]
    )
    for _, row in contract.iterrows():
        lines.append(
            f"| {row['target_gene']} | {row['contract_status']} | "
            f"{row['pgaa_s1_out']} | {row['pgaa_s2_out']} | {row['external_claim_state_out']} |"
        )

    ready = contract[contract["pgaa_command"].astype(str) != ""]
    if not ready.empty:
        lines.extend(["", "## PGAA Commands", ""])
        for _, row in ready.iterrows():
            lines.extend([f"### {row['target_gene']}", "", "```bash", row["pgaa_command"], "```", ""])

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "A `ready_for_pgaa_input_extraction` row only authorizes input extraction and PGAA/comparator rerun. It does not authorize a manuscript replication claim until the external claim-state output exists and agrees with the predeclared internal responder-state unit.",
            "",
            "The external rerun command keeps full-gene observed PGAA-W and PGAA-H ranks, while restricting PGAA-W permutation p-value estimation to the perturbation target gene used by the claim-state rule.",
        ]
    )
    return "\n".join(lines) + "\n"
