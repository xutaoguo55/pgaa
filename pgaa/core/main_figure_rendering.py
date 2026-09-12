"""Render the source-driven PGAA recharter Figure 1."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from pgaa.core.figure_io import save_figure


REQUIRED_FIGURE_COLUMNS = {
    "figure_id",
    "panel_id",
    "source_kind",
    "context",
    "state",
    "stability_class",
    "cross_dataset_status",
    "x_group",
    "y_value",
    "secondary_value",
    "label",
    "n_methods",
    "n_comparative_support",
    "n_descriptive_only",
    "n_failure_or_guardrail",
}

PANEL_IDS = {
    "A_claim_state_distribution",
    "B_responder_state_units",
    "C_unit_stability",
}

STATE_COLORS = {
    "comparative_support": "#1f7a4d",
    "calibration_support": "#4d908e",
    "restricted_use": "#c77d13",
    "descriptive_only": "#6c757d",
    "failure_or_guardrail": "#b23a48",
    "supported_responder_state": "#1f7a4d",
    "provisional_responder_state": "#c77d13",
}

STABILITY_COLORS = {
    "leave_one_method_stable": "#1f7a4d",
    "method_sensitive": "#c77d13",
    "pgaa_support_dependent": "#b23a48",
}

PANEL_LABELS = {
    "calibration_guardrail": "Calibration\nchecks",
    "decision_benchmark": "Decision\nbenchmarks",
    "parameter_guardrail": "Parameter\nchecks",
}


def _stability_color(value: object) -> str:
    text = str(value)
    for stability_class, color in STABILITY_COLORS.items():
        if text == stability_class or text.startswith(f"{stability_class}_"):
            return color
    return "#6c757d"


def _validate(frame: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_FIGURE_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"main-figure source table is missing columns: {missing}")
    observed_panels = set(frame["panel_id"].dropna().astype(str))
    missing_panels = sorted(PANEL_IDS - observed_panels)
    if missing_panels:
        raise ValueError(f"main-figure source table is missing panels: {missing_panels}")


def build_figure1_payload(figure_sources: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split and lightly normalize source rows for Figure 1 rendering."""
    _validate(figure_sources)
    payload = {
        "panel_a": figure_sources[
            figure_sources["panel_id"] == "A_claim_state_distribution"
        ].copy(),
        "panel_b": figure_sources[
            figure_sources["panel_id"] == "B_responder_state_units"
        ].copy(),
        "panel_c": figure_sources[figure_sources["panel_id"] == "C_unit_stability"].copy(),
    }
    for frame in payload.values():
        frame["y_value"] = pd.to_numeric(frame["y_value"], errors="coerce").fillna(0.0)
        frame["secondary_value"] = pd.to_numeric(
            frame["secondary_value"], errors="coerce"
        ).fillna(0.0)
    return payload


def _plot_panel_a(ax: plt.Axes, data: pd.DataFrame) -> None:
    grouped = (
        data.groupby(["x_group", "state"], dropna=False)["y_value"]
        .sum()
        .unstack(fill_value=0.0)
    )
    x_groups = ["decision_benchmark", "calibration_guardrail", "parameter_guardrail"]
    states = [
        "comparative_support",
        "calibration_support",
        "restricted_use",
        "descriptive_only",
        "failure_or_guardrail",
    ]
    bottom = [0.0] * len(x_groups)
    x_positions = range(len(x_groups))
    for state in states:
        values = [float(grouped.loc[group, state]) if state in grouped.columns and group in grouped.index else 0.0 for group in x_groups]
        ax.bar(
            x_positions,
            values,
            bottom=bottom,
            color=STATE_COLORS[state],
            edgecolor="white",
            linewidth=0.8,
            label=state.replace("_", " "),
        )
        bottom = [left + value for left, value in zip(bottom, values)]
    ax.set_title("A. Claim-state distribution", loc="left", fontweight="bold")
    ax.set_xticks(list(x_positions), [PANEL_LABELS[group] for group in x_groups])
    ax.set_ylabel("Source rows")
    ax.set_ylim(0, max(bottom) * 1.18)
    for idx, total in enumerate(bottom):
        ax.text(idx, total + 0.45, str(int(total)), ha="center", va="bottom", fontsize=8)
    ax.legend(
        ncol=1,
        frameon=False,
        fontsize=7.5,
        loc="upper right",
    )


def _plot_panel_b(ax: plt.Axes, data: pd.DataFrame) -> None:
    data = data.sort_values(["state", "y_value", "context"], ascending=[True, False, True])
    y_positions = list(range(len(data)))
    colors = [STATE_COLORS.get(str(state), "#6c757d") for state in data["state"]]
    ax.barh(
        y_positions,
        data["y_value"],
        color=colors,
        edgecolor="#222222",
        linewidth=0.6,
    )
    for pos, (_, row) in zip(y_positions, data.iterrows()):
        ax.text(
            row["y_value"] + 0.01,
            pos,
            f"{row['primary_method']} | {row['stability_class'].replace('_', ' ')}",
            va="center",
            fontsize=6.5,
        )
    ax.set_title("B. Responder-state decision units", loc="left", fontweight="bold")
    ax.set_yticks(y_positions, data["context"])
    ax.set_xlabel("Primary ranking metric")
    ax.set_xlim(0, max(1.35, float(data["y_value"].max()) + 0.45))
    ax.invert_yaxis()


def _plot_panel_c(ax: plt.Axes, data: pd.DataFrame) -> None:
    data = data.sort_values(["stability_class", "context"])
    y_positions = list(range(len(data)))
    preserved = data["y_value"].astype(float)
    changed = data["secondary_value"].astype(float)
    colors = [_stability_color(value) for value in data["stability_class"]]
    ax.barh(
        y_positions,
        preserved,
        color=colors,
        edgecolor="#222222",
        linewidth=0.6,
        label="state preserved",
    )
    ax.barh(
        y_positions,
        changed,
        left=preserved,
        color="#d9dde2",
        edgecolor="#222222",
        linewidth=0.6,
        label="state changed",
    )
    for pos, (_, row) in zip(y_positions, data.iterrows()):
        total = float(row["y_value"]) + float(row["secondary_value"])
        ax.text(
            total + 0.06,
            pos,
            row["cross_dataset_status"].replace("_", " "),
            va="center",
            fontsize=7,
            color="#444444",
        )
    ax.set_title("C. Stability and replication gate", loc="left", fontweight="bold")
    ax.set_yticks(y_positions, data["context"])
    ax.set_xlabel("Leave-one-method checks")
    ax.set_xlim(0, max(7.2, float((preserved + changed).max()) + 2.2))
    ax.invert_yaxis()
    ax.legend(
        frameon=False,
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
    )


def render_figure1(
    figure_sources: pd.DataFrame,
    png_out: str | Path,
    pdf_out: str | Path | None = None,
) -> dict[str, object]:
    """Render Figure 1 from the unified source-data table."""
    payload = build_figure1_payload(figure_sources)
    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10.2, 13.2),
        gridspec_kw={"height_ratios": [1.0, 1.35, 1.35]},
        constrained_layout=False,
    )
    fig.suptitle(
        "PGAA recharter: claim-controlled responder-state evidence",
        fontsize=15,
        fontweight="bold",
        y=0.997,
    )
    _plot_panel_a(axes[0], payload["panel_a"])
    _plot_panel_b(axes[1], payload["panel_b"])
    _plot_panel_c(axes[2], payload["panel_c"])
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", color="#e7e7e7", linewidth=0.8)
        ax.set_axisbelow(True)
    fig.tight_layout(rect=(0.02, 0.035, 0.99, 0.955), h_pad=2.8)

    png_path = Path(png_out)
    save_figure(fig, png_path, dpi=300, bbox_inches="tight")

    pdf_path: Path | None = None
    if pdf_out is not None:
        pdf_path = Path(pdf_out)
        save_figure(fig, pdf_path, bbox_inches="tight")
    plt.close(fig)

    return {
        "png": str(png_path),
        "pdf": str(pdf_path) if pdf_path is not None else "",
        "n_source_rows": int(len(figure_sources)),
        "n_panels": 3,
        "n_no_same_context_replication": int(
            (
                payload["panel_c"]["cross_dataset_status"]
                == "no_cross_dataset_same_context"
            ).sum()
        ),
        "n_external_same_context_concordant": int(
            (
                payload["panel_c"]["cross_dataset_status"]
                == "external_same_context_concordant"
            ).sum()
        ),
        "n_external_same_context_blocked": int(
            (
                payload["panel_c"]["cross_dataset_status"]
                == "external_same_context_blocked"
            ).sum()
        ),
        "n_external_same_context_discordant": int(
            (
                payload["panel_c"]["cross_dataset_status"]
                == "external_same_context_discordant"
            ).sum()
        ),
        "n_external_same_context_unresolved": int(
            (
                payload["panel_c"]["cross_dataset_status"]
                == "external_same_context_unresolved"
            ).sum()
        ),
    }


def render_figure1_report(metadata: dict[str, object], figure_sources: pd.DataFrame) -> str:
    """Render a markdown report for the generated Figure 1 draft."""
    payload = build_figure1_payload(figure_sources)
    external_total = sum(
        int(metadata.get(key, 0))
        for key in (
            "n_external_same_context_concordant",
            "n_external_same_context_blocked",
            "n_external_same_context_discordant",
            "n_external_same_context_unresolved",
        )
    )
    if external_total:
        boundary = (
            "The figure is source-driven and keeps external same-context claim-state status "
            "visible. "
            f"{metadata['n_external_same_context_concordant']} rows are "
            "external_same_context_concordant, "
            f"{metadata['n_external_same_context_blocked']} are "
            "external_same_context_blocked, "
            f"{metadata['n_external_same_context_discordant']} are "
            "external_same_context_discordant, and "
            f"{metadata['n_external_same_context_unresolved']} are "
            "external_same_context_unresolved. Concordant rows support only bounded "
            "computational replication; no row supports wet-lab or immune validation."
        )
    else:
        boundary = (
            "The figure is source-driven and keeps same-context replication status visible. "
            f"{metadata['n_no_same_context_replication']} stability rows are still "
            "`no_cross_dataset_same_context`; do not claim replicated responder states "
            "unless external same-context evidence is added."
        )
    lines = [
        "# PGAA Figure 1 Render Report",
        "",
        f"PNG: `{metadata['png']}`",
        f"PDF: `{metadata['pdf']}`",
        f"Source rows: {metadata['n_source_rows']}",
        f"Panels rendered: {metadata['n_panels']}",
        "",
        "## Panel Source Counts",
        "",
        "| Panel | Rows |",
        "|---|---:|",
        f"| A. Claim-state distribution | {len(payload['panel_a'])} |",
        f"| B. Responder-state decision units | {len(payload['panel_b'])} |",
        f"| C. Stability and replication gate | {len(payload['panel_c'])} |",
        "",
        "## Claim Boundary",
        "",
        boundary,
        "",
    ]
    return "\n".join(lines)
