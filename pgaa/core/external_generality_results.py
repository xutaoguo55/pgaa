"""Compile locked cross-target PGAA outputs without dropping failures."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def _target_result(path: Path, target: str, score_column: str) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size == 0:
        return {"status": "missing", "rank": pd.NA, "percentile": pd.NA, "score": pd.NA}
    try:
        result = pd.read_csv(path)
    except Exception as exc:
        return {
            "status": f"unreadable:{type(exc).__name__}",
            "rank": pd.NA,
            "percentile": pd.NA,
            "score": pd.NA,
        }
    required = {"gene", score_column}
    if not required.issubset(result.columns) or target not in set(result["gene"].astype(str)):
        return {"status": "invalid_or_target_missing", "rank": pd.NA, "percentile": pd.NA, "score": pd.NA}
    ordered = result.sort_values(score_column, ascending=False, kind="mergesort").reset_index(drop=True)
    position = int(ordered.index[ordered["gene"].astype(str) == target][0])
    row = ordered.iloc[position]
    return {
        "status": "complete",
        "rank": position + 1,
        "percentile": (position + 1) / len(ordered),
        "score": float(row[score_column]),
        "p_value": row.get("p_value_perm", pd.NA),
        "n_genes": len(ordered),
    }


def compile_generality_results(contract: pd.DataFrame) -> pd.DataFrame:
    """Compile every locked target; missing or invalid outputs remain failures."""
    required = {"target_gene", "pgaa_s1_out", "pgaa_s2_out", "denominator_rule"}
    missing = sorted(required - set(contract.columns))
    if missing:
        raise ValueError(f"Contract is missing columns: {', '.join(missing)}")
    rows: list[dict[str, object]] = []
    for _, contract_row in contract.iterrows():
        target = str(contract_row["target_gene"])
        w = _target_result(Path(str(contract_row["pgaa_s1_out"])), target, "W_observed")
        h = _target_result(Path(str(contract_row["pgaa_s2_out"])), target, "S2")
        complete = w["status"] == "complete" and h["status"] == "complete"
        w_percentile = w.get("percentile", pd.NA)
        h_percentile = h.get("percentile", pd.NA)
        w_p = w.get("p_value", pd.NA)
        w_top10 = bool(complete and float(w_percentile) <= 0.10)
        h_top10 = bool(complete and float(h_percentile) <= 0.10)
        rows.append(
            {
                "target_gene": target,
                "execution_status": "complete" if complete else "failed_or_incomplete",
                "pgaa_w_status": w["status"],
                "pgaa_w_rank": w.get("rank", pd.NA),
                "pgaa_w_percentile": w_percentile,
                "pgaa_w_score": w.get("score", pd.NA),
                "pgaa_w_p_value": w_p,
                "pgaa_w_significant_0_05": bool(complete and pd.notna(w_p) and float(w_p) <= 0.05),
                "pgaa_w_top10pct": w_top10,
                "pgaa_h_status": h["status"],
                "pgaa_h_rank": h.get("rank", pd.NA),
                "pgaa_h_percentile": h_percentile,
                "pgaa_h_score": h.get("score", pd.NA),
                "pgaa_h_top10pct": h_top10,
                "joint_top10pct": w_top10 and h_top10,
                "denominator_rule": contract_row["denominator_rule"],
                "claim_use": "cross_target_generality_only_not_same_target_replication",
            }
        )
    return pd.DataFrame(rows)


def summarize_generality_results(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize locked-denominator completion and target-recovery endpoints."""
    n = len(results)
    metrics = [
        ("execution_complete", results["execution_status"].eq("complete")),
        ("pgaa_w_significant_0_05", results["pgaa_w_significant_0_05"].astype(bool)),
        ("pgaa_w_top10pct", results["pgaa_w_top10pct"].astype(bool)),
        ("pgaa_h_top10pct", results["pgaa_h_top10pct"].astype(bool)),
        ("joint_top10pct", results["joint_top10pct"].astype(bool)),
    ]
    return pd.DataFrame(
        {
            "metric": [name for name, _ in metrics],
            "n_success": [int(mask.sum()) for _, mask in metrics],
            "n_locked_targets": n,
            "fraction": [float(mask.sum() / n) if n else 0.0 for _, mask in metrics],
        }
    )


def render_generality_results_report(results: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render result-blind endpoints with the correct evidence boundary."""
    values = summary.set_index("metric")
    lines = [
        "# Replogle Essential Cross-target Generality Results",
        "",
        "The denominator is the complete locked 16-target panel, including execution failures. The endpoints were fixed after the one-target pipeline pilot and before executing the remaining targets: PGAA-W target permutation p <= 0.05, PGAA-W target top 10%, PGAA-H target top 10%, and joint top-10% recovery.",
        "",
        "| Endpoint | Success / locked | Fraction |",
        "|---|---:|---:|",
    ]
    for metric, row in values.iterrows():
        lines.append(
            f"| `{metric}` | {int(row['n_success'])}/{int(row['n_locked_targets'])} | {float(row['fraction']):.1%} |"
        )
    lines.extend(
        [
            "",
            "| Target | Status | W rank | W percentile | W p | H rank | H percentile | Joint top 10% |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in results.iterrows():
        def number(value: object, fmt: str) -> str:
            return "NA" if pd.isna(value) else format(float(value), fmt)

        lines.append(
            f"| `{row['target_gene']}` | {row['execution_status']} | {number(row['pgaa_w_rank'], '.0f')} | "
            f"{number(row['pgaa_w_percentile'], '.3f')} | {number(row['pgaa_w_p_value'], '.4g')} | "
            f"{number(row['pgaa_h_rank'], '.0f')} | {number(row['pgaa_h_percentile'], '.3f')} | "
            f"{bool(row['joint_top10pct'])} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "These endpoints quantify target recovery across a locked panel within one K562 essential-gene Perturb-seq experiment. Targets share an experiment and a fixed control subsample, so target rows are not independent biological replicates. Results do not establish same-target cross-dataset replication, immune presentation, synthetic-peptide validation, or T-cell function.",
            "",
        ]
    )
    return "\n".join(lines)
