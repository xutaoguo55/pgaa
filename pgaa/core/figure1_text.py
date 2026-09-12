"""Draft claim-bounded Figure 1 caption and Results text."""
from __future__ import annotations

import pandas as pd

from pgaa.core.main_figure_rendering import REQUIRED_FIGURE_COLUMNS


def _validate(frame: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_FIGURE_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"main-figure source table is missing columns: {missing}")


def _base_stability_class(value: object) -> str:
    """Strip an external-state suffix while retaining the internal stability class."""
    text = str(value)
    for suffix in (
        "_external_concordant",
        "_external_blocked",
        "_external_discordant",
        "_external_unresolved",
    ):
        if text.endswith(suffix):
            return text[: -len(suffix)]
    return text


def summarize_figure1_text_inputs(figure_sources: pd.DataFrame) -> dict[str, object]:
    """Summarize the source table into manuscript-safe text inputs."""
    _validate(figure_sources)
    panel_a = figure_sources[figure_sources["panel_id"] == "A_claim_state_distribution"]
    panel_b = figure_sources[figure_sources["panel_id"] == "B_responder_state_units"]
    panel_c = figure_sources[figure_sources["panel_id"] == "C_unit_stability"]

    claim_counts = (
        panel_a.groupby("state", dropna=False)["y_value"]
        .sum()
        .astype(int)
        .to_dict()
    )
    responder_counts = panel_b["state"].value_counts().astype(int).to_dict()
    stability_counts = (
        panel_c["stability_class"]
        .map(_base_stability_class)
        .value_counts()
        .astype(int)
        .to_dict()
    )
    no_replication = int(
        (panel_c["cross_dataset_status"] == "no_cross_dataset_same_context").sum()
    )
    return {
        "n_source_rows": int(len(figure_sources)),
        "n_claim_rows": int(len(panel_a)),
        "n_responder_units": int(len(panel_b)),
        "n_stability_rows": int(len(panel_c)),
        "claim_counts": claim_counts,
        "responder_counts": responder_counts,
        "stability_counts": stability_counts,
        "n_no_same_context_replication": no_replication,
        "n_external_same_context_concordant": int(
            (panel_c["cross_dataset_status"] == "external_same_context_concordant").sum()
        ),
        "n_external_same_context_blocked": int(
            (panel_c["cross_dataset_status"] == "external_same_context_blocked").sum()
        ),
        "n_external_same_context_discordant": int(
            (panel_c["cross_dataset_status"] == "external_same_context_discordant").sum()
        ),
        "n_external_same_context_unresolved": int(
            (panel_c["cross_dataset_status"] == "external_same_context_unresolved").sum()
        ),
    }


def render_figure1_caption_and_results(figure_sources: pd.DataFrame) -> str:
    """Render a conservative caption and Results draft from Figure 1 sources."""
    summary = summarize_figure1_text_inputs(figure_sources)
    claim_counts = summary["claim_counts"]
    responder_counts = summary["responder_counts"]
    stability_counts = summary["stability_counts"]
    external_total = sum(
        int(summary[key])
        for key in (
            "n_external_same_context_concordant",
            "n_external_same_context_blocked",
            "n_external_same_context_discordant",
            "n_external_same_context_unresolved",
        )
    )
    if external_total:
        boundary_text = (
            "This text is bounded to the generated Figure 1 source table. External "
            "same-context concordance denotes computational agreement in a matched "
            "perturbation setting; it does not establish biological validation, immune "
            "presentation, peptide validation, or T-cell function."
        )
        replication_caption = (
            f"The typed external gate classifies "
            f"{summary['n_external_same_context_concordant']} units as concordant, "
            f"{summary['n_external_same_context_blocked']} as blocked, "
            f"{summary['n_external_same_context_discordant']} as discordant, and "
            f"{summary['n_external_same_context_unresolved']} as unresolved. Concordant "
            "units support bounded computational same-context replication only."
        )
        replication_results = (
            f"The external gate then assigned {summary['n_external_same_context_concordant']} "
            "units to `external_same_context_concordant` and "
            f"{summary['n_external_same_context_blocked']} to "
            "`external_same_context_blocked`, with "
            f"{summary['n_external_same_context_discordant']} discordant and "
            f"{summary['n_external_same_context_unresolved']} unresolved units. This typed "
            "state distinguishes computational concordance from unavailable or conflicting "
            "evidence without promoting any unit to biological validation."
        )
    else:
        boundary_text = (
            "This text is bounded to the generated Figure 1 source table. It does not "
            "claim same-context cross-dataset replication, immune presentation, peptide "
            "validation, or T-cell function."
        )
        replication_caption = (
            "All units currently lack same-context cross-dataset replication evidence."
        )
        replication_results = (
            "Because all stability rows are currently marked "
            "`no_cross_dataset_same_context`, these results should be presented as "
            "claim-controlled benchmark evidence, not as replicated responder-state "
            "discoveries."
        )

    lines = [
        "# Figure 1 Caption and Results Draft",
        "",
        "## Claim Boundary",
        "",
        boundary_text,
        "",
        "## Figure Caption Draft",
        "",
        (
            "Figure 1. A claim-state compiler controls evidentiary inflation in "
            "single-cell perturbation benchmarking. (A) Benchmark and guardrail rows "
            "are compiled into typed manuscript claim states, including "
            f"{claim_counts.get('comparative_support', 0)} comparative-support rows, "
            f"{claim_counts.get('descriptive_only', 0)} descriptive-only rows, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support rows, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use rows, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows. "
            "(B) Row-level evidence is aggregated into context-level responder-state "
            f"decision units, including {responder_counts.get('supported_responder_state', 0)} "
            "supported units and "
            f"{responder_counts.get('provisional_responder_state', 0)} provisional "
            "units. (C) Leave-one-method stability and same-context replication gate "
            f"for the {summary['n_stability_rows']} responder-state units. "
            f"{stability_counts.get('leave_one_method_stable', 0)} units are "
            "leave-one-method stable, "
            f"{stability_counts.get('method_sensitive', 0)} are method-sensitive, "
            f"and {stability_counts.get('pgaa_support_dependent', 0)} is "
            f"PGAA-support dependent. {replication_caption}"
        ),
        "",
        "## Results Paragraph Draft",
        "",
        (
            "We implemented PGAA as a claim-state compiler that maps heterogeneous "
            "benchmark evidence to typed manuscript decisions rather than leaving each "
            "score open to post hoc interpretation. The generated "
            f"Figure 1 source table contains {summary['n_source_rows']} rows spanning "
            f"{summary['n_claim_rows']} claim-state summaries, "
            f"{summary['n_responder_units']} responder-state decision units, and "
            f"{summary['n_stability_rows']} stability summaries. This conversion makes "
            "positive, descriptive, restricted, and failed benchmark outcomes visible "
            "in the same object. Each row therefore retains an explicit interpretation "
            "ceiling, preventing restricted or failed evidence from being promoted during "
            "manuscript assembly. At the decision-unit level, the current evidence supports "
            f"{responder_counts.get('supported_responder_state', 0)} bounded Adamson "
            "responder-state claims and leaves "
            f"{responder_counts.get('provisional_responder_state', 0)} Norman units as "
            "provisional descriptive findings. Leave-one-method checks identify "
            f"{stability_counts.get('leave_one_method_stable', 0)} stable units, "
            f"{stability_counts.get('method_sensitive', 0)} method-sensitive units, "
            f"and {stability_counts.get('pgaa_support_dependent', 0)} PGAA-support "
            f"dependent unit. {replication_results}"
        ),
        "",
    ]
    return "\n".join(lines)
