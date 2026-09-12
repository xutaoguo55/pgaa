"""Compile PGAA claim-panel rows into responder-state decision units."""
from __future__ import annotations

import pandas as pd


REQUIRED_PANEL_COLUMNS = {
    "claim_id",
    "panel_key",
    "evidence_type",
    "context",
    "method",
    "metric",
    "metric_value",
    "secondary_metric_value",
    "result_claim_state",
    "severity",
    "manuscript_allowed_claim",
    "technical_interpretation",
    "source_table",
}

CLAIM_PRIORITY = {
    "comparative_support": 1,
    "calibration_support": 2,
    "descriptive_only": 3,
    "restricted_use": 4,
    "failure_or_guardrail": 5,
    "manual_review_required": 6,
}

SEVERITY_PRIORITY = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "very_high": 4,
    "critical": 5,
    "manual": 6,
}


def _is_pgaa_method(method: object) -> bool:
    return "PGAA" in str(method).upper()


def _join_unique(values: pd.Series) -> str:
    clean = [str(value) for value in values if pd.notna(value) and str(value).strip()]
    return ";".join(dict.fromkeys(clean))


def _decision_state(group: pd.DataFrame) -> tuple[str, str]:
    n_comparative = int((group["result_claim_state"] == "comparative_support").sum())
    n_descriptive = int((group["result_claim_state"] == "descriptive_only").sum())
    n_failures = int((group["result_claim_state"] == "failure_or_guardrail").sum())
    n_pgaa_comparative = int(
        (
            (group["result_claim_state"] == "comparative_support")
            & group["method"].map(_is_pgaa_method)
        ).sum()
    )
    n_pgaa_descriptive = int(
        ((group["result_claim_state"] == "descriptive_only") & group["method"].map(_is_pgaa_method)).sum()
    )

    if n_pgaa_comparative > 0:
        return (
            "supported_responder_state",
            "PGAA has at least one bounded comparative-support row for this context.",
        )
    if n_comparative > 0:
        return (
            "comparator_supported_state",
            "A non-PGAA comparator has comparative support; PGAA should not claim primary support.",
        )
    if n_pgaa_descriptive > 0:
        return (
            "provisional_responder_state",
            "PGAA evidence is descriptive only; use as a hypothesis-generating responder state.",
        )
    if n_descriptive > 0:
        return (
            "descriptive_comparator_state",
            "Only descriptive comparator evidence is present for this context.",
        )
    if n_failures > 0:
        return (
            "failed_or_limited_state",
            "Available benchmark rows are failure, weak-evidence, or guardrail rows.",
        )
    return (
        "manual_review_state",
        "No supported decision class was available; manual review is required.",
    )


def _primary_row(group: pd.DataFrame) -> pd.Series:
    ranked = group.copy()
    ranked["_claim_priority"] = ranked["result_claim_state"].map(CLAIM_PRIORITY).fillna(99)
    ranked["_severity_priority"] = ranked["severity"].map(SEVERITY_PRIORITY).fillna(99)
    ranked["_pgaa_priority"] = ranked["method"].map(lambda value: 0 if _is_pgaa_method(value) else 1)
    ranked["_metric_sort"] = pd.to_numeric(ranked["metric_value"], errors="coerce").fillna(-1)
    ranked["_secondary_sort"] = pd.to_numeric(
        ranked["secondary_metric_value"], errors="coerce"
    ).fillna(-1)
    ranked = ranked.sort_values(
        [
            "_claim_priority",
            "_pgaa_priority",
            "_severity_priority",
            "_secondary_sort",
            "_metric_sort",
            "method",
        ],
        ascending=[True, True, True, False, False, True],
    )
    return ranked.iloc[0]


def build_responder_state_units(panel_sources: pd.DataFrame) -> pd.DataFrame:
    """Aggregate decision-benchmark rows into target-level responder-state units."""
    missing = sorted(REQUIRED_PANEL_COLUMNS - set(panel_sources.columns))
    if missing:
        raise ValueError(f"panel source table is missing columns: {missing}")

    decision_rows = panel_sources[panel_sources["panel_key"] == "decision_benchmark"].copy()
    if decision_rows.empty:
        return pd.DataFrame(
            columns=[
                "unit_id",
                "evidence_type",
                "context",
                "decision_state",
                "primary_method",
                "primary_metric",
                "primary_metric_value",
                "primary_secondary_metric_value",
                "n_methods",
                "n_pgaa_methods",
                "n_comparative_support",
                "n_descriptive_only",
                "n_failure_or_guardrail",
                "supporting_methods",
                "descriptive_methods",
                "failure_or_guardrail_methods",
                "allowed_manuscript_use",
                "technical_rationale",
                "source_tables",
            ]
        )

    rows: list[dict[str, object]] = []
    for (evidence_type, context), group in decision_rows.groupby(
        ["evidence_type", "context"], dropna=False
    ):
        primary = _primary_row(group)
        decision_state, technical_rationale = _decision_state(group)
        supporting = group[group["result_claim_state"] == "comparative_support"]
        descriptive = group[group["result_claim_state"] == "descriptive_only"]
        failures = group[group["result_claim_state"] == "failure_or_guardrail"]
        rows.append(
            {
                "unit_id": f"{evidence_type}::{context}",
                "evidence_type": evidence_type,
                "context": context,
                "decision_state": decision_state,
                "primary_method": primary["method"],
                "primary_metric": primary["metric"],
                "primary_metric_value": primary["metric_value"],
                "primary_secondary_metric_value": primary["secondary_metric_value"],
                "n_methods": int(group["method"].nunique(dropna=True)),
                "n_pgaa_methods": int(group["method"].map(_is_pgaa_method).sum()),
                "n_comparative_support": int(len(supporting)),
                "n_descriptive_only": int(len(descriptive)),
                "n_failure_or_guardrail": int(len(failures)),
                "supporting_methods": _join_unique(supporting["method"]),
                "descriptive_methods": _join_unique(descriptive["method"]),
                "failure_or_guardrail_methods": _join_unique(failures["method"]),
                "allowed_manuscript_use": primary["manuscript_allowed_claim"],
                "technical_rationale": technical_rationale,
                "source_tables": _join_unique(group["source_table"]),
            }
        )

    units = pd.DataFrame(rows)
    units["_state_order"] = units["decision_state"].map(
        {
            "supported_responder_state": 1,
            "comparator_supported_state": 2,
            "provisional_responder_state": 3,
            "descriptive_comparator_state": 4,
            "failed_or_limited_state": 5,
            "manual_review_state": 6,
        }
    )
    units = units.sort_values(["_state_order", "evidence_type", "context"]).drop(
        columns=["_state_order"]
    )
    return units.reset_index(drop=True)


def summarize_responder_state_units(units: pd.DataFrame) -> pd.DataFrame:
    """Summarize responder-state decision units for figure captions."""
    required = {"evidence_type", "decision_state"}
    missing = sorted(required - set(units.columns))
    if missing:
        raise ValueError(f"responder-state table is missing columns: {missing}")
    return (
        units.groupby(["evidence_type", "decision_state"], dropna=False)
        .size()
        .reset_index(name="n_units")
        .sort_values(["evidence_type", "decision_state"])
    )


def render_responder_state_report(units: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render a report for the responder-state decision-unit layer."""
    lines = [
        "# PGAA Responder-State Decision Unit Report",
        "",
        f"Responder-state units: {len(units)}",
        "",
        "## Unit Summary",
        "",
        "| Evidence type | Decision state | Units |",
        "|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(f"| {row['evidence_type']} | {row['decision_state']} | {row['n_units']} |")
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "`supported_responder_state` units can be used as bounded positive examples. "
            "`provisional_responder_state` units should be framed as hypothesis-generating. "
            "`failed_or_limited_state` units are retained as explicit benchmark failures or "
            "comparator limits. This keeps the method centered on auditable decision states "
            "rather than unqualified ranked gene lists.",
            "",
        ]
    )
    return "\n".join(lines)
