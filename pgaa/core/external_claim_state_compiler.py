"""Compile external PGAA outputs into conservative claim-state rows."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_MANIFEST_COLUMNS = {
    "candidate_dataset_id",
    "target_gene",
    "execution_status",
    "pgaa_s1_out",
    "pgaa_s2_out",
    "external_claim_state_out",
}

REQUIRED_INTERNAL_UNIT_COLUMNS = {
    "unit_id",
    "evidence_type",
    "context",
    "decision_state",
    "primary_method",
    "supporting_methods",
}


def _target_from_context(context: object) -> str:
    return str(context).split("_", 1)[0]


def _rank_row(path: Path, target: str, score_columns: list[str]) -> dict[str, object]:
    if not path.exists():
        return {
            "status": "missing_output",
            "rank": np.nan,
            "score": np.nan,
            "p_value": np.nan,
            "n_genes": 0,
        }
    table = pd.read_csv(path)
    if "gene" not in table.columns:
        return {
            "status": "missing_gene_column",
            "rank": np.nan,
            "score": np.nan,
            "p_value": np.nan,
            "n_genes": len(table),
        }
    score_column = next((column for column in score_columns if column in table.columns), None)
    if score_column is None:
        return {
            "status": "missing_score_column",
            "rank": np.nan,
            "score": np.nan,
            "p_value": np.nan,
            "n_genes": len(table),
        }
    ranked = table.copy()
    ranked["_score"] = pd.to_numeric(ranked[score_column], errors="coerce")
    ranked = ranked.sort_values("_score", ascending=False, na_position="last").reset_index(drop=True)
    matches = ranked[ranked["gene"].astype(str) == target]
    if matches.empty:
        return {
            "status": "target_gene_absent_from_output",
            "rank": np.nan,
            "score": np.nan,
            "p_value": np.nan,
            "n_genes": len(ranked),
        }
    index = int(matches.index[0])
    p_value = np.nan
    for p_col in ["p_value_perm", "p_value", "pval", "padj"]:
        if p_col in ranked.columns:
            p_value = pd.to_numeric(pd.Series([ranked.loc[index, p_col]]), errors="coerce").iloc[0]
            break
    return {
        "status": "target_gene_ranked",
        "rank": index + 1,
        "score": ranked.loc[index, "_score"],
        "p_value": p_value,
        "n_genes": len(ranked),
    }


def _support_status(
    s1: dict[str, object],
    s2: dict[str, object],
    top_n: int,
    alpha: float,
) -> tuple[str, str]:
    s1_rank = pd.to_numeric(pd.Series([s1["rank"]]), errors="coerce").iloc[0]
    s2_rank = pd.to_numeric(pd.Series([s2["rank"]]), errors="coerce").iloc[0]
    s1_p = pd.to_numeric(pd.Series([s1["p_value"]]), errors="coerce").iloc[0]
    s2_p = pd.to_numeric(pd.Series([s2["p_value"]]), errors="coerce").iloc[0]
    s1_support = pd.notna(s1_p) and float(s1_p) <= alpha
    if pd.notna(s1_rank) and int(s1_rank) <= top_n:
        s1_support = True
    s2_support = pd.notna(s2_p) and float(s2_p) <= alpha
    if pd.notna(s2_rank) and int(s2_rank) <= top_n:
        s2_support = True

    if s1["status"] != "target_gene_ranked" and s2["status"] != "target_gene_ranked":
        return (
            "external_claim_state_unresolved",
            "Target gene could not be ranked in either PGAA output.",
        )
    if s1_support and s2_support:
        return (
            "external_pgaa_w_h_support_observed",
            f"Target meets support rule in both PGAA-W and PGAA-H at alpha={alpha} or top_n={top_n}.",
        )
    if s1_support or s2_support:
        return (
            "external_single_pgaa_mode_support_observed",
            f"Target meets support rule in one PGAA mode at alpha={alpha} or top_n={top_n}.",
        )
    return (
        "external_support_not_observed",
        f"Target is ranked but does not meet alpha={alpha} or top_n={top_n} support rules.",
    )


def _internal_match(units: pd.DataFrame, target: str) -> pd.Series | None:
    matches = units[units["context"].map(_target_from_context) == target]
    if matches.empty:
        return None
    adamson = matches[matches["evidence_type"].astype(str).str.contains("adamson", case=False)]
    if not adamson.empty:
        return adamson.iloc[0]
    return matches.iloc[0]


def compile_external_claim_states(
    manifest: pd.DataFrame,
    internal_units: pd.DataFrame,
    top_n: int = 100,
    alpha: float = 0.05,
    write_files: bool = True,
) -> pd.DataFrame:
    """Compile external PGAA output files into per-target claim-state rows."""
    missing_manifest = sorted(REQUIRED_MANIFEST_COLUMNS - set(manifest.columns))
    if missing_manifest:
        raise ValueError(f"execution manifest is missing columns: {missing_manifest}")
    missing_units = sorted(REQUIRED_INTERNAL_UNIT_COLUMNS - set(internal_units.columns))
    if missing_units:
        raise ValueError(f"internal responder-state table is missing columns: {missing_units}")

    rows: list[dict[str, object]] = []
    for _, row in manifest.iterrows():
        target = str(row["target_gene"])
        execution_status = str(row["execution_status"])
        internal = _internal_match(internal_units, target)
        if internal is None:
            internal_unit_id = ""
            internal_decision_state = "missing_internal_responder_state_unit"
            internal_supported = False
        else:
            internal_unit_id = str(internal["unit_id"])
            internal_decision_state = str(internal["decision_state"])
            internal_supported = internal_decision_state == "supported_responder_state"

        if execution_status not in {
            "pgaa_outputs_present_waiting_claim_state_compilation",
            "external_claim_state_present",
        }:
            claim_state = "blocked_by_external_execution_status"
            concordance_state = "not_assessable"
            rationale = "External PGAA outputs are not ready for claim-state compilation."
            s1 = {"status": "not_read", "rank": np.nan, "score": np.nan, "p_value": np.nan, "n_genes": 0}
            s2 = {"status": "not_read", "rank": np.nan, "score": np.nan, "p_value": np.nan, "n_genes": 0}
        elif internal is None:
            claim_state = "blocked_missing_internal_unit"
            concordance_state = "not_assessable"
            rationale = "No predeclared internal responder-state unit matched this external target."
            s1 = _rank_row(Path(str(row["pgaa_s1_out"])), target, ["W_std_observed", "W_observed", "z_score"])
            s2 = _rank_row(Path(str(row["pgaa_s2_out"])), target, ["S2"])
        else:
            s1 = _rank_row(Path(str(row["pgaa_s1_out"])), target, ["W_std_observed", "W_observed", "z_score"])
            s2 = _rank_row(Path(str(row["pgaa_s2_out"])), target, ["S2"])
            claim_state, rationale = _support_status(s1, s2, top_n=top_n, alpha=alpha)
            external_supported = claim_state in {
                "external_pgaa_w_h_support_observed",
                "external_single_pgaa_mode_support_observed",
            }
            if internal_supported and external_supported:
                concordance_state = "external_concordant_with_internal_supported_unit"
            elif internal_supported and claim_state == "external_support_not_observed":
                concordance_state = "external_discordant_with_internal_supported_unit"
            elif internal_supported:
                concordance_state = "external_unresolved_for_internal_supported_unit"
            elif external_supported:
                concordance_state = "external_support_without_internal_supported_unit"
            else:
                concordance_state = "not_assessable"

        out_path = Path(str(row["external_claim_state_out"]))
        compiled_row = {
            "candidate_dataset_id": row["candidate_dataset_id"],
            "target_gene": target,
            "internal_unit_id": internal_unit_id,
            "internal_decision_state": internal_decision_state,
            "execution_status": execution_status,
            "external_claim_state": claim_state,
            "concordance_state": concordance_state,
            "pgaa_w_status": s1["status"],
            "pgaa_w_rank": s1["rank"],
            "pgaa_w_score": s1["score"],
            "pgaa_w_p_value": s1["p_value"],
            "pgaa_h_status": s2["status"],
            "pgaa_h_rank": s2["rank"],
            "pgaa_h_score": s2["score"],
            "pgaa_h_p_value": s2["p_value"],
            "n_genes_pgaa_w": s1["n_genes"],
            "n_genes_pgaa_h": s2["n_genes"],
            "support_rule_top_n": int(top_n),
            "support_rule_alpha": float(alpha),
            "external_claim_state_out": str(out_path),
            "claim_use": "external_claim_state_not_wet_lab_validation",
            "rationale": rationale,
        }
        if write_files and execution_status == "pgaa_outputs_present_waiting_claim_state_compilation":
            out_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame([compiled_row]).to_csv(out_path, sep="\t", index=False)
        rows.append(compiled_row)
    return pd.DataFrame(rows)


def summarize_external_claim_states(claim_states: pd.DataFrame) -> pd.DataFrame:
    """Summarize compiled external claim-state rows."""
    required = {"external_claim_state", "concordance_state", "claim_use"}
    missing = sorted(required - set(claim_states.columns))
    if missing:
        raise ValueError(f"external claim-state table is missing columns: {missing}")
    return (
        claim_states.groupby(["external_claim_state", "concordance_state", "claim_use"], dropna=False)
        .size()
        .reset_index(name="n_targets")
        .sort_values(["external_claim_state", "concordance_state"])
        .reset_index(drop=True)
    )


def render_external_claim_state_report(claim_states: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render a conservative external claim-state compiler report."""
    lines = [
        "# PGAA External Claim-State Compiler Report",
        "",
        "This report compiles external PGAA-W/PGAA-H outputs into target-level claim states. It is not wet-lab validation, immune-presentation evidence, synthetic-peptide validation, or T-cell functional validation.",
        "",
        "## Summary",
        "",
        "| External claim state | Concordance state | Allowed use | Targets |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['external_claim_state']} | {row['concordance_state']} | "
            f"{row['claim_use']} | {row['n_targets']} |"
        )

    lines.extend(
        [
            "",
            "## Target Claim States",
            "",
            "| Target | Internal unit | External claim state | Concordance | PGAA-W rank | PGAA-H rank |",
            "|---|---|---|---|---:|---:|",
        ]
    )
    for _, row in claim_states.iterrows():
        lines.append(
            f"| {row['target_gene']} | {row['internal_unit_id']} | "
            f"{row['external_claim_state']} | {row['concordance_state']} | "
            f"{row['pgaa_w_rank']} | {row['pgaa_h_rank']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "A concordant external claim-state row can support only a computational same-context replication statement after the predeclared PGAA outputs exist. It still cannot support immune-presentation, synthetic-peptide, or T-cell-function claims.",
        ]
    )
    return "\n".join(lines) + "\n"
