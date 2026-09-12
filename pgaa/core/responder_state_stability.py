"""Stability checks for PGAA responder-state decision units."""
from __future__ import annotations

import pandas as pd

from pgaa.core.responder_state_units import build_responder_state_units


REQUIRED_UNIT_COLUMNS = {
    "unit_id",
    "evidence_type",
    "context",
    "decision_state",
    "supporting_methods",
    "descriptive_methods",
    "failure_or_guardrail_methods",
}

REQUIRED_PANEL_COLUMNS = {
    "panel_key",
    "evidence_type",
    "context",
    "method",
    "result_claim_state",
}


def _split_methods(value: object) -> set[str]:
    if pd.isna(value) or str(value).strip() == "":
        return set()
    return {part for part in str(value).split(";") if part}


def _is_pgaa_method(method: object) -> bool:
    return "PGAA" in str(method).upper()


def _method_role(method: object, unit: pd.Series) -> str:
    method_text = str(method)
    if method_text in _split_methods(unit.get("supporting_methods")):
        return "supporting"
    if method_text in _split_methods(unit.get("descriptive_methods")):
        return "descriptive"
    if method_text in _split_methods(unit.get("failure_or_guardrail_methods")):
        return "failure_or_guardrail"
    return "unclassified"


def _cross_dataset_status(units: pd.DataFrame, context: object) -> str:
    matches = units[units["context"] == context]
    if matches["evidence_type"].nunique(dropna=True) > 1:
        states = set(matches["decision_state"].astype(str))
        if len(states) == 1:
            return "replicated_same_state"
        return "replicated_state_discordant"
    return "no_cross_dataset_same_context"


def build_leave_one_method_stability(
    panel_sources: pd.DataFrame, units: pd.DataFrame
) -> pd.DataFrame:
    """Recompute responder-state units after omitting one method at a time."""
    missing_units = sorted(REQUIRED_UNIT_COLUMNS - set(units.columns))
    if missing_units:
        raise ValueError(f"responder-state table is missing columns: {missing_units}")
    missing_panel = sorted(REQUIRED_PANEL_COLUMNS - set(panel_sources.columns))
    if missing_panel:
        raise ValueError(f"panel source table is missing columns: {missing_panel}")

    decision_rows = panel_sources[panel_sources["panel_key"] == "decision_benchmark"].copy()
    rows: list[dict[str, object]] = []
    unit_index = units.set_index("unit_id", drop=False)
    for unit_id, unit in unit_index.iterrows():
        unit_rows = decision_rows[
            (decision_rows["evidence_type"] == unit["evidence_type"])
            & (decision_rows["context"] == unit["context"])
        ]
        for method in sorted(unit_rows["method"].dropna().astype(str).unique()):
            reduced = unit_rows[unit_rows["method"].astype(str) != method]
            if reduced.empty:
                perturbed_state = "no_evidence_after_omission"
                perturbed_primary_method = ""
            else:
                perturbed_units = build_responder_state_units(reduced)
                if perturbed_units.empty:
                    perturbed_state = "no_decision_after_omission"
                    perturbed_primary_method = ""
                else:
                    perturbed_state = str(perturbed_units.iloc[0]["decision_state"])
                    perturbed_primary_method = str(perturbed_units.iloc[0]["primary_method"])

            baseline_state = str(unit["decision_state"])
            rows.append(
                {
                    "unit_id": unit_id,
                    "evidence_type": unit["evidence_type"],
                    "context": unit["context"],
                    "omitted_method": method,
                    "omitted_method_role": _method_role(method, unit),
                    "omitted_method_is_pgaa": _is_pgaa_method(method),
                    "baseline_decision_state": baseline_state,
                    "perturbed_decision_state": perturbed_state,
                    "state_preserved": baseline_state == perturbed_state,
                    "perturbed_primary_method": perturbed_primary_method,
                    "cross_dataset_status": _cross_dataset_status(units, unit["context"]),
                }
            )
    return pd.DataFrame(rows)


def summarize_responder_state_stability(
    stability_rows: pd.DataFrame, units: pd.DataFrame
) -> pd.DataFrame:
    """Summarize leave-one-method and cross-dataset stability per responder-state unit."""
    required = {
        "unit_id",
        "omitted_method_role",
        "omitted_method_is_pgaa",
        "baseline_decision_state",
        "state_preserved",
        "cross_dataset_status",
    }
    missing = sorted(required - set(stability_rows.columns))
    if missing:
        raise ValueError(f"stability table is missing columns: {missing}")
    missing_units = sorted({"unit_id", "decision_state"} - set(units.columns))
    if missing_units:
        raise ValueError(f"responder-state table is missing columns: {missing_units}")

    rows: list[dict[str, object]] = []
    for unit_id, group in stability_rows.groupby("unit_id", dropna=False):
        baseline_state = str(group["baseline_decision_state"].iloc[0])
        n_checks = int(len(group))
        n_preserved = int(group["state_preserved"].sum())
        n_changed = n_checks - n_preserved
        pgaa_rows = group[group["omitted_method_is_pgaa"]]
        pgaa_changed = int((~pgaa_rows["state_preserved"]).sum()) if not pgaa_rows.empty else 0
        supporting_rows = group[group["omitted_method_role"] == "supporting"]
        supporting_changed = (
            int((~supporting_rows["state_preserved"]).sum()) if not supporting_rows.empty else 0
        )
        if n_changed == 0:
            stability_class = "leave_one_method_stable"
        elif pgaa_changed > 0 and baseline_state == "supported_responder_state":
            stability_class = "pgaa_support_dependent"
        elif supporting_changed > 0:
            stability_class = "support_method_dependent"
        else:
            stability_class = "method_sensitive"

        rows.append(
            {
                "unit_id": unit_id,
                "baseline_decision_state": baseline_state,
                "n_leave_one_checks": n_checks,
                "n_state_preserved": n_preserved,
                "n_state_changed": n_changed,
                "n_pgaa_omission_changed": pgaa_changed,
                "n_supporting_omission_changed": supporting_changed,
                "stability_class": stability_class,
                "cross_dataset_status": str(group["cross_dataset_status"].iloc[0]),
            }
        )

    summary = pd.DataFrame(rows)
    unit_meta = units[["unit_id", "evidence_type", "context", "primary_method"]].copy()
    return unit_meta.merge(summary, on="unit_id", how="left").sort_values(
        ["stability_class", "evidence_type", "context"]
    )


def render_responder_state_stability_report(
    unit_summary: pd.DataFrame, stability_rows: pd.DataFrame
) -> str:
    """Render a manuscript-facing stability report."""
    class_counts = (
        unit_summary.groupby(["stability_class", "cross_dataset_status"], dropna=False)
        .size()
        .reset_index(name="n_units")
        .sort_values(["stability_class", "cross_dataset_status"])
    )
    lines = [
        "# PGAA Responder-State Stability Report",
        "",
        f"Responder-state units audited: {len(unit_summary)}",
        f"Leave-one-method checks: {len(stability_rows)}",
        "",
        "## Stability Classes",
        "",
        "| Stability class | Cross-dataset status | Units |",
        "|---|---|---:|",
    ]
    for _, row in class_counts.iterrows():
        lines.append(
            f"| {row['stability_class']} | {row['cross_dataset_status']} | {row['n_units']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "`leave_one_method_stable` units can be shown as more robust examples. "
            "`pgaa_support_dependent` and `support_method_dependent` units should be framed "
            "as method-sensitive and must keep their omitted-method diagnostics visible. "
            "`no_cross_dataset_same_context` means the current repository does not yet prove "
            "same-context replication across datasets.",
            "",
        ]
    )
    return "\n".join(lines)
