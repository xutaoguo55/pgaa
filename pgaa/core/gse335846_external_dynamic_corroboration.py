"""Build the GSE335846 external dynamic corroboration audit."""
from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from pgaa.core.atm_hdac_upgrade_package import build_source_data_audit

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure


CORROBORATION_SPECS = (
    {
        "evidence_layer": "pc9_dynamic_dtp_replication",
        "line_refs": "40-47; 416-425; 1434-1442",
        "support_statement": (
            "PC9 keeps cycling under osimertinib, the DTP state is unexpectedly dynamic, "
            "and the time-course readouts document repeated EdU positivity and regrowth."
        ),
        "manuscript_role": "Independent dynamic corroboration",
        "required_phrases": (
            "extensive DNA replication occurs",
            "DTP state is highly mutagenic",
            "EdU positive cells",
            "Quantification of PC9 cell confluence over 0, 7, 14, and 28 days",
            "Quantification of time to regrowth (to 100% confluence)",
        ),
    },
    {
        "evidence_layer": "atm_sensitivity",
        "line_refs": "653-677; 1434-1442",
        "support_statement": (
            "Low-dose ATM inhibition with AZD1390 reduces cell number, replication, "
            "and return-to-growth behavior in the PC9 DTP system."
        ),
        "manuscript_role": "Reinforces the ATM lead",
        "required_phrases": (
            "ATM (AZD1390)",
            "AZD1390 and ceralasertib inhibitors reducing cell number",
            "DNA damage responses are critical for survival in the DTP state",
            "Quantification of PC9 cell confluence over 0, 7, 14, and 28 days",
        ),
    },
    {
        "evidence_layer": "atr_sensitivity",
        "line_refs": "638-677; 1568-1570",
        "support_statement": (
            "Low-dose ATR inhibition with ceralasertib reduces DTP survival and "
            "shows the same DDR logic is not ATM-only."
        ),
        "manuscript_role": "Shows the DDR logic extends beyond ATM",
        "required_phrases": (
            "ATR (ceralasertib)",
            "Ceralasertib (ATR inhibitor)",
            "AZD1390 and ceralasertib inhibitors reducing cell number",
            "DNA damage responses are critical for survival in the DTP state",
        ),
    },
    {
        "evidence_layer": "hcc4006_bridge",
        "line_refs": "124-129; 433-433; 657-657; 1476-1477; 1577-1580",
        "support_statement": (
            "The same dynamic DTP logic is reproduced in HCC4006, which makes the "
            "preprint useful as a second EGFR-mutant bridge."
        ),
        "manuscript_role": "Secondary generalization bridge",
        "required_phrases": (
            "HCC4006",
            "was reproduced in HCC4006 cells",
            "Assays were performed in PC9 and HCC4006 cells",
            "Quantification of the proportion of HCC4006 cells positive for EdU",
            "Quantification of time to regrowth (to 100% confluence) of HCC4006 cells",
        ),
    },
)


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _find_phrase_line(lines: list[str], phrase: str) -> int:
    needle = phrase.lower()
    for index, line in enumerate(lines, start=1):
        if needle in line.lower():
            return index
    raise ValueError(f"Missing required phrase in preprint text: {phrase}")


def _validate_span(lines: list[str], line_refs: str, phrases: tuple[str, ...]) -> str:
    spans: list[tuple[int, int]] = []
    for raw_span in line_refs.split(";"):
        start_str, end_str = raw_span.strip().split("-")
        spans.append((int(start_str), int(end_str)))
    for phrase in phrases:
        line_no = _find_phrase_line(lines, phrase)
        if not any(start <= line_no <= end for start, end in spans):
            raise ValueError(
                f"Phrase {phrase!r} was found on line {line_no}, outside the declared span {line_refs}"
            )
    return line_refs


def build_external_dynamic_corroboration_summary(preprint_path: Path) -> pd.DataFrame:
    """Summarize the independent dynamic corroboration with line-anchored evidence."""
    lines = _read_lines(preprint_path)
    rows: list[dict[str, str]] = []
    for spec in CORROBORATION_SPECS:
        rows.append(
            {
                "evidence_layer": spec["evidence_layer"],
                "line_refs": _validate_span(lines, spec["line_refs"], spec["required_phrases"]),
                "support_statement": spec["support_statement"],
                "manuscript_role": spec["manuscript_role"],
                "claim_boundary": "corroboration_only_not_source_table_upgrade",
            }
        )

    return pd.DataFrame(rows)


def _render_source_ceiling_snapshot(source_audit: pd.DataFrame) -> str:
    snapshot = source_audit.loc[
        source_audit["source_id"].isin(
            ["gse335846_geo_family", "gse335848_superseries", "biorxiv_preprint_v1"]
        ),
        [
            "source_id",
            "source_numerical_status",
            "usable_for_current_analysis",
            "missing_for_upgrade",
        ],
    ].copy()
    if snapshot.empty:
        return "No source audit rows were available."
    return snapshot.to_csv(sep="\t", index=False).strip()


def render_external_dynamic_corroboration(
    summary: pd.DataFrame,
    source_audit: pd.DataFrame,
) -> str:
    """Render the manuscript-facing corroboration audit."""
    rows = "\n".join(
        f"| {row.evidence_layer} | {row.line_refs} | {row.support_statement} | {row.manuscript_role} | {row.claim_boundary} |"
        for row in summary.itertuples()
    )
    source_audit_snapshot = _render_source_ceiling_snapshot(source_audit)
    return "\n".join(
        [
            "# GSE335846 External Dynamic Corroboration",
            "",
            "## Result",
            "",
            "An independent 2026 PC9 osimertinib-DTP preprint supports the same dynamic resistance logic used in the manuscript: the DTP state is not static, PC9 cells continue to cycle under osimertinib, and low-dose ATM inhibition and low-dose ATR inhibition both reduce DTP survival and return-to-growth behavior. The same paper also reports the related phenotype in HCC4006, which makes it a useful independent corroboration layer.",
            "The preprint's data-availability statement points to GEO accession GSE335848, but the publicly accessible accession viewer does not provide supplementary data files, so replicate-level drug-response source tables remain unavailable in the public record.",
            "",
            "## Evidence anchors",
            "",
            "| Evidence layer | Preprint line refs | Support statement | Manuscript role | Claim boundary |",
            "|---|---|---|---|---|",
            rows,
            "",
            "## Source ceiling snapshot",
            "",
            "The corroboration layer does not upgrade the public source ceiling. The current source audit still distinguishes RNA-seq source-table availability from the missing replicate-level dynamic drug-response tables.",
            "",
            source_audit_snapshot,
            "",
            "## Boundary",
            "",
            "This preprint is not a substitute for replicate-level source numerical tables. It strengthens the dynamic ATM branch logic, but it remains below the source-table ceiling and therefore cannot close the submission-grade gap on its own.",
            "",
        ]
    )


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def render_external_dynamic_corroboration_figure(
    timecourse: pd.DataFrame,
    branch_scores: pd.DataFrame,
    marker_summary: pd.DataFrame,
    png_out: Path,
    pdf_out: Path | None = None,
) -> None:
    """Render a publication-style scorecard for the fifth-system corroboration."""
    _require_columns(
        timecourse,
        {
            "day",
            "replication_branch_strength",
            "osimertinib_confluence",
            "atm_combo_confluence",
            "atm_added_benefit",
        },
        "timecourse",
    )
    _require_columns(
        branch_scores,
        {"sample", "day", "cycle_phase", "source_branch_contrast"},
        "branch_scores",
    )
    _require_columns(
        marker_summary,
        {"feature_symbol", "day0_mean", "day28_mean", "delta_day28_minus_day0"},
        "marker_summary",
    )

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8.5,
            "figure.dpi": 300,
        }
    )

    phase_colors = {"G1": "#009E73", "S": "#56B4E9", "G2": "#CC79A7"}
    phase_offsets = {"G1": -0.18, "S": 0.0, "G2": 0.18}
    phase_markers = {"G1": "o", "S": "^", "G2": "s"}

    fig = plt.figure(figsize=(13.8, 8.6))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], wspace=0.36, hspace=0.34)
    ax_a = fig.add_subplot(grid[0, :])
    ax_b = fig.add_subplot(grid[1, 0])
    ax_c = fig.add_subplot(grid[1, 1])
    ax_c.tick_params(axis="y", labelsize=8.2)

    timecourse = timecourse.sort_values("day").reset_index(drop=True)
    x = timecourse["day"].astype(float).to_numpy()
    branch = timecourse["replication_branch_strength"].astype(float).to_numpy()
    benefit = timecourse["atm_added_benefit"].astype(float).to_numpy()
    ax_a.plot(
        x,
        branch,
        color="#0072B2",
        marker="o",
        linewidth=2.0,
        markersize=6,
        label="Replication-branch strength",
    )
    ax_a.set_xlabel("Day")
    ax_a.set_ylabel("Replication-branch strength", color="#0072B2")
    ax_a.tick_params(axis="y", colors="#0072B2")
    ax_a.set_xticks(x)
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.grid(axis="y", alpha=0.2, linewidth=0.8)
    ax_a.set_title(
        "a  Dynamic gradient from figure-digitized DTP readouts",
        loc="left",
        fontweight="bold",
        pad=8,
    )

    ax_a2 = ax_a.twinx()
    ax_a2.plot(
        x,
        benefit,
        color="#D55E00",
        marker="s",
        linewidth=2.0,
        markersize=6,
        linestyle="--",
        label="ATM added benefit",
    )
    ax_a2.set_ylabel("ATM added benefit", color="#D55E00")
    ax_a2.tick_params(axis="y", colors="#D55E00")
    ax_a2.spines["top"].set_visible(False)
    ax_a2.set_ylim(0, max(36.0, float(np.max(benefit)) * 1.12))

    assoc = timecourse.attrs.get("association")
    if not assoc:
        assoc = {}
    rho = assoc.get("spearman_rho", np.nan)
    pval = assoc.get("one_sided_exact_permutation_p", np.nan)
    n_timepoints = assoc.get("n_timepoints", len(timecourse))
    ax_a.text(
        0.98,
        0.05,
        f"Spearman rho = {float(rho):.3f}; exact p = {float(pval):.4f}; n = {int(n_timepoints)}",
        transform=ax_a.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD"},
    )
    ax_a.legend(
        handles=[
            Line2D([0], [0], color="#0072B2", marker="o", linewidth=2.0, label="Replication-branch strength"),
            Line2D([0], [0], color="#D55E00", marker="s", linestyle="--", linewidth=2.0, label="ATM added benefit"),
        ],
        frameon=False,
        loc="upper left",
    )

    branch_scores = branch_scores.sort_values(["day", "cycle_phase", "sample"]).reset_index(drop=True)
    day_means = branch_scores.groupby("day", as_index=False)["source_branch_contrast"].mean()
    for phase, color in phase_colors.items():
        sub = branch_scores[branch_scores["cycle_phase"].eq(phase)]
        if sub.empty:
            continue
        xs = sub["day"].astype(float).to_numpy() + phase_offsets[phase]
        ax_b.scatter(
            xs,
            sub["source_branch_contrast"].astype(float).to_numpy(),
            s=42,
            color=color,
            edgecolor="black",
            linewidth=0.5,
            marker=phase_markers[phase],
            label=f"{phase} samples",
            alpha=0.95,
        )
    ax_b.plot(
        day_means["day"].astype(float).to_numpy(),
        day_means["source_branch_contrast"].astype(float).to_numpy(),
        color="#222222",
        linewidth=1.7,
        marker="D",
        markersize=5,
        label="Day mean",
    )
    ax_b.axhline(0, color="#888888", linewidth=0.9, linestyle="--")
    ax_b.set_title(
        "b  RNA-seq source-axis projection",
        loc="left",
        fontweight="bold",
        pad=8,
    )
    ax_b.set_xlabel("Day")
    ax_b.set_ylabel("Source-axis contrast (PC9 - HCC4006)")
    ax_b.set_xticks(sorted(branch_scores["day"].unique()))
    ax_b.grid(axis="y", alpha=0.2, linewidth=0.8)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)
    ax_b.legend(frameon=False, loc="best")
    day0_mean = float(day_means.loc[day_means["day"].eq(0), "source_branch_contrast"].iloc[0])
    day28_mean = float(day_means.loc[day_means["day"].eq(28), "source_branch_contrast"].iloc[0])
    ax_b.text(
        0.02,
        0.95,
        f"Day 0 mean = {day0_mean:.3f}\nDay 28 mean = {day28_mean:.3f}",
        transform=ax_b.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD"},
    )

    marker_summary = marker_summary.sort_values("delta_day28_minus_day0", ascending=True).reset_index(drop=True)
    y_positions = np.arange(len(marker_summary))
    colors = np.where(
        marker_summary["delta_day28_minus_day0"].astype(float).to_numpy() >= 0,
        "#2F6DB3",
        "#D55E00",
    )
    ax_c.barh(
        y_positions,
        marker_summary["delta_day28_minus_day0"].astype(float).to_numpy(),
        color=colors,
        edgecolor="#222222",
        linewidth=0.5,
    )
    ax_c.axvline(0, color="#888888", linewidth=0.9)
    ax_c.set_yticks(
        y_positions,
        [
            f"{row.feature_symbol} (n={int(row.probe_count)})"
            for row in marker_summary.itertuples()
        ],
    )
    ax_c.set_xlabel("Day 28 minus Day 0 mean expression")
    ax_c.set_title(
        "c  Source-table marker shifts",
        loc="left",
        fontweight="bold",
        pad=8,
    )
    ax_c.grid(axis="x", alpha=0.2, linewidth=0.8)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)
    ax_c.spines["left"].set_visible(False)
    ax_c.tick_params(axis="y", length=0)
    for idx, row in enumerate(marker_summary.itertuples()):
        value = float(row.delta_day28_minus_day0)
        ax_c.text(
            value + (0.06 if value >= 0 else -0.06),
            idx,
            f"{value:+.3f}",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8.2,
        )

    fig.suptitle(
        "GSE335846 dynamic corroboration scorecard",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Rank-level dynamic DTP readouts remain figure-digitized; the RNA-seq branch-axis projection is source-table backed.",
        ha="center",
        va="bottom",
        fontsize=8.2,
        color="#444444",
    )
    save_figure(fig, png_out, dpi=300, bbox_inches="tight")
    if pdf_out is not None:
        save_figure(fig, pdf_out, bbox_inches="tight")
    plt.close(fig)


def render_external_dynamic_corroboration_support_text(
    timecourse: pd.DataFrame,
    branch_scores: pd.DataFrame,
    marker_summary: pd.DataFrame,
    association: pd.DataFrame | dict[str, float],
) -> str:
    """Render the support text for the corroboration figure."""
    if isinstance(association, pd.DataFrame):
        assoc = association.iloc[0].to_dict()
    else:
        assoc = dict(association)
    branch_scores = branch_scores.copy()
    branch_scores["day"] = branch_scores["day"].astype(int)
    source_summary = (
        branch_scores.groupby("day", as_index=False)
        .agg(
            samples=("sample", "count"),
            mean_source_axis_contrast=("source_branch_contrast", "mean"),
            min_source_axis_contrast=("source_branch_contrast", "min"),
            max_source_axis_contrast=("source_branch_contrast", "max"),
        )
        .sort_values("day")
    )
    marker_summary = marker_summary.sort_values("delta_day28_minus_day0", ascending=False)
    top_up = marker_summary.head(3)
    top_down = marker_summary.tail(3).sort_values("delta_day28_minus_day0")
    timecourse = timecourse.sort_values("day").reset_index(drop=True)
    dynamic_rows = "\n".join(
        f"| {int(row.day)} | {row.replication_branch_strength:.3f} | {row.atm_added_benefit:.1f} | {row.osimertinib_confluence:.1f} | {row.atm_combo_confluence:.1f} |"
        for row in timecourse.itertuples()
    )
    source_rows = "\n".join(
        f"| {int(row.day)} | {int(row.samples)} | {row.mean_source_axis_contrast:.3f} | {row.min_source_axis_contrast:.3f} | {row.max_source_axis_contrast:.3f} |"
        for row in source_summary.itertuples()
    )
    marker_rows = "\n".join(
        f"| {row.feature_symbol} | {row.day0_mean:.3f} | {row.day28_mean:.3f} | {row.delta_day28_minus_day0:+.3f} |"
        for row in marker_summary.itertuples()
    )
    return f"""# GSE335846 External Dynamic Corroboration Support Text

Supplementary Figure S5 summarizes the fifth-system evidence in three bounded panels. Panel A keeps the dynamic DTP time-course at figure-digitized rank level, while Panels B and C show the source-table-backed RNA-seq branch-axis projection and the associated marker shifts. The linked preprint's data-availability statement points to GEO accession GSE335848, but the accession viewer does not expose supplementary data files, so the dynamic drug-response source tables are still not public.

## Supplementary Figure S5

Supplementary Figure S5. GSE335846 dynamic corroboration scorecard. (A) The linked preprint reports a monotonic increase in replication-branch strength from day 0 to day 28 and a larger ATM added benefit at the late DTP time point. (B) The public GSE335846 RNA-seq source table projects onto the frozen branch axis without re-ranking genes; the sample-level source-axis contrast shifts from a negative day-0 mean toward a less negative day-28 mean. (C) The same source table shows concordant marker shifts, including positive ATM and EGFR movement and negative proliferation/replication markers such as MKI67, MCM2, MCM5, PCNA, RAD51, RPA2, and CDK1. The figure therefore strengthens dynamic corroboration while preserving the public source ceiling.

## Evidence Summary

### Dynamic Time Course

| Day | Replication-branch strength | ATM added benefit | Osimertinib confluence | +AZD1390 confluence |
|---:|---:|---:|---:|---:|
{dynamic_rows}

Spearman rho = {float(assoc.get("spearman_rho", np.nan)):.3f}; one-sided exact permutation p = {float(assoc.get("one_sided_exact_permutation_p", np.nan)):.4f}; n = {int(float(assoc.get("n_timepoints", len(timecourse))))} time points.

### Source-Axis Projection

| Day | Samples | Mean source-axis contrast | Min | Max |
|---:|---:|---:|---:|---:|
{source_rows}

### Marker Shifts

| Feature | Day 0 mean | Day 28 mean | Delta (28 - 0) |
|---|---:|---:|---:|
{marker_rows}

Representative upward-shifted markers: {", ".join(top_up["feature_symbol"].astype(str).tolist())}.
Representative downward-shifted markers: {", ".join(top_down["feature_symbol"].astype(str).tolist())}.

## Boundary

This figure is a corroboration layer, not a source-table-level pharmacology result. The dynamic branch-strength and ATM-benefit values remain figure-digitized; only the RNA-seq branch-axis projection and marker shifts are source-table backed. The figure is therefore useful for reviewer-facing explanation, but it does not close the replicate-level source-table gap on its own.
"""


def write_external_dynamic_corroboration_assets(
    source_dir: Path,
    preprint_path: Path,
    summary_out: Path,
    report_out: Path,
    timecourse_path: Path,
    branch_scores_path: Path,
    marker_summary_path: Path,
    association_path: Path,
    figure_out: Path,
    figure_pdf_out: Path | None,
    support_text_out: Path,
) -> dict[str, Path]:
    """Write the corroboration audit, support figure, and support text."""
    source_audit = build_source_data_audit(source_dir)
    summary = build_external_dynamic_corroboration_summary(preprint_path)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_out, sep="\t", index=False)
    report_out.write_text(
        render_external_dynamic_corroboration(summary, source_audit),
        encoding="utf-8",
    )

    timecourse = pd.read_csv(timecourse_path, sep="\t")
    branch_scores = pd.read_csv(branch_scores_path, sep="\t")
    marker_summary = pd.read_csv(marker_summary_path, sep="\t")
    association = pd.read_csv(association_path, sep="\t")
    timecourse.attrs["association"] = association.iloc[0].to_dict()
    render_external_dynamic_corroboration_figure(
        timecourse=timecourse,
        branch_scores=branch_scores,
        marker_summary=marker_summary,
        png_out=figure_out,
        pdf_out=figure_pdf_out,
    )
    support_text_out.parent.mkdir(parents=True, exist_ok=True)
    support_text_out.write_text(
        render_external_dynamic_corroboration_support_text(
            timecourse=timecourse,
            branch_scores=branch_scores,
            marker_summary=marker_summary,
            association=association,
        ),
        encoding="utf-8",
    )
    return {
        "summary": summary_out,
        "report": report_out,
        "figure": figure_out,
        "figure_pdf": figure_pdf_out if figure_pdf_out is not None else figure_out.with_suffix(".pdf"),
        "support_text": support_text_out,
    }


def write_external_dynamic_corroboration_package(
    source_dir: Path,
    preprint_path: Path,
    summary_out: Path,
    report_out: Path,
) -> dict[str, Path]:
    """Write the corroboration summary table and audit markdown."""
    source_audit = build_source_data_audit(source_dir)
    summary = build_external_dynamic_corroboration_summary(preprint_path)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_out, sep="\t", index=False)
    report_out.write_text(
        render_external_dynamic_corroboration(summary, source_audit),
        encoding="utf-8",
    )
    return {"summary": summary_out, "report": report_out}
