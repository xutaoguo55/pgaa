"""Build figure-ready source tables from PGAA result-claim states."""
from __future__ import annotations

import pandas as pd


REQUIRED_CLAIM_COLUMNS = {
    "claim_id",
    "figure_panel",
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

PANEL_LABELS = {
    "decision_benchmark": ("Figure 1", "Benchmark decision states"),
    "calibration_guardrail": ("Figure 2", "Calibration guardrails"),
    "parameter_guardrail": ("Figure 2", "Parameter sensitivity guardrails"),
    "response_specificity_guardrail": (
        "Figure 2",
        "Held-out stability versus pseudo-perturbation specificity",
    ),
    "manual_review": ("Supplementary Figure", "Manual-review rows"),
}

CLAIM_ORDER = {
    "comparative_support": 1,
    "calibration_support": 2,
    "descriptive_only": 3,
    "restricted_use": 4,
    "failure_or_guardrail": 5,
    "manual_review_required": 6,
}

SEVERITY_ORDER = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "very_high": 4,
    "critical": 5,
    "manual": 6,
}


def _panel_metadata(panel: object) -> tuple[str, str]:
    return PANEL_LABELS.get(str(panel), ("Supplementary Figure", "Unassigned claim states"))


def _numeric_or_empty(value: object) -> object:
    if pd.isna(value):
        return ""
    return value


def build_claim_panel_sources(claims: pd.DataFrame) -> pd.DataFrame:
    """Return a source-data table ready to drive claim-state figure panels."""
    missing = sorted(REQUIRED_CLAIM_COLUMNS - set(claims.columns))
    if missing:
        raise ValueError(f"claim table is missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in claims.iterrows():
        figure_id, panel_title = _panel_metadata(row["figure_panel"])
        claim_state = str(row["result_claim_state"])
        severity = str(row["severity"])
        rows.append(
            {
                "figure_id": figure_id,
                "panel_key": row["figure_panel"],
                "panel_title": panel_title,
                "claim_id": row["claim_id"],
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "method": row["method"],
                "metric": row["metric"],
                "metric_value": _numeric_or_empty(row["metric_value"]),
                "secondary_metric_value": _numeric_or_empty(row["secondary_metric_value"]),
                "result_claim_state": claim_state,
                "claim_state_order": CLAIM_ORDER.get(claim_state, 99),
                "severity": severity,
                "severity_order": SEVERITY_ORDER.get(severity, 99),
                "manuscript_allowed_claim": row["manuscript_allowed_claim"],
                "technical_interpretation": row["technical_interpretation"],
                "source_table": row["source_table"],
            }
        )

    panel_sources = pd.DataFrame(rows)
    return panel_sources.sort_values(
        ["figure_id", "panel_key", "claim_state_order", "severity_order", "context", "method"]
    ).reset_index(drop=True)


def summarize_claim_panels(panel_sources: pd.DataFrame) -> pd.DataFrame:
    """Summarize figure panels by claim state and severity."""
    required = {"figure_id", "panel_key", "result_claim_state", "severity"}
    missing = sorted(required - set(panel_sources.columns))
    if missing:
        raise ValueError(f"panel source table is missing columns: {missing}")
    return (
        panel_sources.groupby(
            ["figure_id", "panel_key", "result_claim_state", "severity"], dropna=False
        )
        .size()
        .reset_index(name="n_rows")
        .sort_values(["figure_id", "panel_key", "result_claim_state", "severity"])
    )


def render_claim_panel_report(panel_sources: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render a concise report describing the generated figure source tables."""
    figure_counts = (
        panel_sources.groupby(["figure_id", "panel_key"], dropna=False)
        .size()
        .reset_index(name="n_rows")
        .sort_values(["figure_id", "panel_key"])
    )
    lines = [
        "# PGAA Claim-Panel Source Report",
        "",
        f"Panel source rows: {len(panel_sources)}",
        "",
        "## Figure Inputs",
        "",
        "| Figure | Panel | Rows |",
        "|---|---|---:|",
    ]
    for _, row in figure_counts.iterrows():
        lines.append(f"| {row['figure_id']} | {row['panel_key']} | {row['n_rows']} |")

    lines.extend(
        [
            "",
            "## Claim-State and Severity Summary",
            "",
            "| Figure | Panel | Claim state | Severity | Rows |",
            "|---|---|---|---|---:|",
        ]
    )
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['figure_id']} | {row['panel_key']} | "
            f"{row['result_claim_state']} | {row['severity']} | {row['n_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "Use this table as source data for a claim-state figure. Positive benchmark claims "
            "should be drawn only from `comparative_support` rows. Guardrail and failure rows "
            "should remain visible as method behavior, not hidden exclusions.",
            "",
        ]
    )
    return "\n".join(lines)
