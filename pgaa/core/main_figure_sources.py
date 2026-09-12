"""Compile PGAA recharter artifacts into main-figure source data."""
from __future__ import annotations

import pandas as pd


REQUIRED_CLAIM_SUMMARY_COLUMNS = {
    "figure_id",
    "panel_key",
    "result_claim_state",
    "severity",
    "n_rows",
}

REQUIRED_UNIT_COLUMNS = {
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
    "allowed_manuscript_use",
}

REQUIRED_STABILITY_COLUMNS = {
    "unit_id",
    "stability_class",
    "cross_dataset_status",
    "n_leave_one_checks",
    "n_state_preserved",
    "n_state_changed",
    "n_pgaa_omission_changed",
}

REQUIRED_INTEGRATED_STABILITY_COLUMNS = {
    "unit_id",
    "integrated_stability_class",
    "integrated_cross_dataset_status",
    "claim_ceiling",
}

PANEL_ORDER = {
    "A_claim_state_distribution": 1,
    "B_responder_state_units": 2,
    "C_unit_stability": 3,
}


def _validate(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def build_main_figure_sources(
    claim_summary: pd.DataFrame,
    responder_units: pd.DataFrame,
    stability_summary: pd.DataFrame,
    integrated_stability: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build a unified source table for the rechartered main figure."""
    _validate(claim_summary, REQUIRED_CLAIM_SUMMARY_COLUMNS, "claim summary")
    _validate(responder_units, REQUIRED_UNIT_COLUMNS, "responder-state table")
    _validate(stability_summary, REQUIRED_STABILITY_COLUMNS, "stability summary")
    if integrated_stability is not None:
        _validate(
            integrated_stability,
            REQUIRED_INTEGRATED_STABILITY_COLUMNS,
            "integrated stability table",
        )
        integrated_index = integrated_stability.set_index("unit_id", drop=False)
    else:
        integrated_index = None

    rows: list[dict[str, object]] = []
    for _, row in claim_summary.iterrows():
        rows.append(
            {
                "figure_id": "Figure 1",
                "panel_id": "A_claim_state_distribution",
                "panel_title": "Claim-state and guardrail distribution",
                "source_kind": "claim_summary",
                "item_id": f"{row['panel_key']}::{row['result_claim_state']}::{row['severity']}",
                "evidence_type": "",
                "context": "",
                "primary_method": "",
                "state": row["result_claim_state"],
                "stability_class": "",
                "cross_dataset_status": "",
                "x_group": row["panel_key"],
                "y_value": row["n_rows"],
                "secondary_value": "",
                "n_methods": "",
                "n_pgaa_methods": "",
                "n_comparative_support": "",
                "n_descriptive_only": "",
                "n_failure_or_guardrail": "",
                "label": f"{row['result_claim_state']} ({row['severity']})",
                "allowed_manuscript_use": "",
            }
        )

    stability_index = stability_summary.set_index("unit_id", drop=False)
    for _, row in responder_units.iterrows():
        stability = stability_index.loc[row["unit_id"]]
        if integrated_index is not None and row["unit_id"] in integrated_index.index:
            integrated = integrated_index.loc[row["unit_id"]]
            if isinstance(integrated, pd.DataFrame):
                integrated = integrated.iloc[0]
            stability_class = integrated["integrated_stability_class"]
            cross_dataset_status = integrated["integrated_cross_dataset_status"]
            allowed_use = f"{row['allowed_manuscript_use']} | {integrated['claim_ceiling']}"
        else:
            stability_class = stability["stability_class"]
            cross_dataset_status = stability["cross_dataset_status"]
            allowed_use = row["allowed_manuscript_use"]
        rows.append(
            {
                "figure_id": "Figure 1",
                "panel_id": "B_responder_state_units",
                "panel_title": "Responder-state decision units",
                "source_kind": "responder_state_unit",
                "item_id": row["unit_id"],
                "evidence_type": row["evidence_type"],
                "context": row["context"],
                "primary_method": row["primary_method"],
                "state": row["decision_state"],
                "stability_class": stability_class,
                "cross_dataset_status": cross_dataset_status,
                "x_group": row["evidence_type"],
                "y_value": row["primary_metric_value"],
                "secondary_value": row["primary_secondary_metric_value"],
                "n_methods": row["n_methods"],
                "n_pgaa_methods": row["n_pgaa_methods"],
                "n_comparative_support": row["n_comparative_support"],
                "n_descriptive_only": row["n_descriptive_only"],
                "n_failure_or_guardrail": row["n_failure_or_guardrail"],
                "label": f"{row['context']} / {row['decision_state']}",
                "allowed_manuscript_use": allowed_use,
            }
        )

    unit_index = responder_units.set_index("unit_id", drop=False)
    for _, row in stability_summary.iterrows():
        unit = unit_index.loc[row["unit_id"]]
        if integrated_index is not None and row["unit_id"] in integrated_index.index:
            integrated = integrated_index.loc[row["unit_id"]]
            if isinstance(integrated, pd.DataFrame):
                integrated = integrated.iloc[0]
            stability_class = integrated["integrated_stability_class"]
            cross_dataset_status = integrated["integrated_cross_dataset_status"]
            allowed_use = f"{unit['allowed_manuscript_use']} | {integrated['claim_ceiling']}"
        else:
            stability_class = row["stability_class"]
            cross_dataset_status = row["cross_dataset_status"]
            allowed_use = unit["allowed_manuscript_use"]
        rows.append(
            {
                "figure_id": "Figure 1",
                "panel_id": "C_unit_stability",
                "panel_title": "Leave-one-method and replication status",
                "source_kind": "stability_summary",
                "item_id": row["unit_id"],
                "evidence_type": unit["evidence_type"],
                "context": unit["context"],
                "primary_method": unit["primary_method"],
                "state": unit["decision_state"],
                "stability_class": stability_class,
                "cross_dataset_status": cross_dataset_status,
                "x_group": stability_class,
                "y_value": row["n_state_preserved"],
                "secondary_value": row["n_state_changed"],
                "n_methods": unit["n_methods"],
                "n_pgaa_methods": unit["n_pgaa_methods"],
                "n_comparative_support": unit["n_comparative_support"],
                "n_descriptive_only": unit["n_descriptive_only"],
                "n_failure_or_guardrail": unit["n_failure_or_guardrail"],
                "label": (
                    f"{unit['context']}: {row['n_state_preserved']}/"
                    f"{row['n_leave_one_checks']} preserved"
                ),
                "allowed_manuscript_use": allowed_use,
            }
        )

    figure_sources = pd.DataFrame(rows)
    figure_sources["_panel_order"] = figure_sources["panel_id"].map(PANEL_ORDER).fillna(99)
    return figure_sources.sort_values(
        ["_panel_order", "source_kind", "x_group", "state", "context"]
    ).drop(columns=["_panel_order"]).reset_index(drop=True)


def summarize_main_figure_sources(figure_sources: pd.DataFrame) -> pd.DataFrame:
    """Summarize the generated main-figure source table."""
    required = {"figure_id", "panel_id", "source_kind"}
    _validate(figure_sources, required, "main-figure source table")
    return (
        figure_sources.groupby(["figure_id", "panel_id", "source_kind"], dropna=False)
        .size()
        .reset_index(name="n_rows")
        .sort_values(["figure_id", "panel_id", "source_kind"])
    )


def render_main_figure_source_report(
    figure_sources: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render a report describing the main-figure source-data contract."""
    stability_rows = figure_sources[figure_sources["panel_id"] == "C_unit_stability"]
    no_replication = int(
        (stability_rows["cross_dataset_status"] == "no_cross_dataset_same_context").sum()
    )
    external_concordant = int(
        (stability_rows["cross_dataset_status"] == "external_same_context_concordant").sum()
    )
    external_blocked = int(
        (stability_rows["cross_dataset_status"] == "external_same_context_blocked").sum()
    )
    external_discordant = int(
        (stability_rows["cross_dataset_status"] == "external_same_context_discordant").sum()
    )
    external_unresolved = int(
        (stability_rows["cross_dataset_status"] == "external_same_context_unresolved").sum()
    )
    if external_concordant + external_blocked + external_discordant + external_unresolved:
        replication_sentence = (
            f"Panel C includes an external same-context evidence layer: "
            f"{external_concordant} stability rows are external_same_context_concordant, "
            f"{external_blocked} are external_same_context_blocked, "
            f"{external_discordant} are external_same_context_discordant, and "
            f"{external_unresolved} are external_same_context_unresolved. Concordant rows "
            "support only bounded computational replication language; blocked, discordant, "
            "or unresolved rows must not be promoted."
        )
    else:
        replication_sentence = (
            f"Same-context cross-dataset replication is absent for {no_replication} "
            "stability rows; do not claim replicated responder states unless an external "
            "same-context evidence layer is added."
        )
    lines = [
        "# PGAA Main-Figure Source Report",
        "",
        f"Main-figure source rows: {len(figure_sources)}",
        "",
        "## Panel Inputs",
        "",
        "| Figure | Panel | Source kind | Rows |",
        "|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['figure_id']} | {row['panel_id']} | {row['source_kind']} | {row['n_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "Panel A shows claim-state and guardrail counts. Panel B shows context-level "
            "responder-state units. Panel C shows leave-one-method stability and same-context "
            "cross-dataset status.",
            "",
            replication_sentence,
            "",
        ]
    )
    return "\n".join(lines)
