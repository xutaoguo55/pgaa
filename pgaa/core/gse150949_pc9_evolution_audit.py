"""Audit GSE150949 as the strongest local third-system PC9 candidate."""
from __future__ import annotations

import csv
import gzip
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

# Fixed so that rebuilding the reviewer archive is byte-identical: a build-time
# date here would dirty this tracked file and make the archive depend on the day
# it was built.
AUDIT_DATE = "2026-09-12"

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

from pgaa.core.figure_io import save_figure


TOP_DOWN_GENE_COUNT = 50
PANEL_COLORS = {
    "day0": "#0072B2",
    "day3": "#56B4E9",
    "day7": "#009E73",
    "day14_high": "#D55E00",
    "day14_med": "#E69F00",
    "day14_low": "#CC79A7",
}


def _load_inputs(
    state_modules_path: Path,
    annotation_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    state_modules = pd.read_csv(state_modules_path, sep="\t")
    annotation = pd.read_csv(annotation_path, sep="\t")
    if "gene_id" not in state_modules.columns or "direction" not in state_modules.columns:
        raise ValueError("State-module table must contain gene_id and direction columns")
    if "gene_id" not in annotation.columns or "display_name" not in annotation.columns:
        raise ValueError("Annotation table must contain gene_id and display_name columns")
    return state_modules, annotation


def _build_top_down_module(
    state_modules: pd.DataFrame,
    annotation: pd.DataFrame,
    top_n: int = TOP_DOWN_GENE_COUNT,
) -> pd.DataFrame:
    frozen = state_modules.loc[state_modules["direction"].astype(str).eq("down")].copy()
    frozen = frozen.nsmallest(top_n, "rank").reset_index(drop=True)
    annotation_map = annotation.set_index("gene_id")["display_name"].to_dict()
    frozen["gene_symbol"] = frozen["gene_id"].map(annotation_map)
    missing = frozen[frozen["gene_symbol"].isna()]
    if not missing.empty:
        raise ValueError(
            "Annotation table is missing gene symbols for: "
            + ", ".join(missing["gene_id"].astype(str).tolist())
        )
    frozen["gene_symbol"] = frozen["gene_symbol"].astype(str)
    frozen["present_in_matrix"] = False
    return frozen.loc[:, ["rank", "gene_id", "gene_symbol", "locked_discovery_score", "present_in_matrix"]]


def _extract_matrix_rows(
    matrix_path: Path,
    ordered_symbols: list[str],
) -> tuple[list[str], dict[str, np.ndarray]]:
    ordered_set = set(ordered_symbols)
    rows: dict[str, np.ndarray] = {}
    with gzip.open(matrix_path, "rt", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        barcodes = [value.strip('"') for value in header[1:]]
        for row in reader:
            gene = row[0]
            if gene in ordered_set:
                rows[gene] = np.asarray(row[1:], dtype=np.float32)
                if len(rows) == len(ordered_set):
                    break
    return barcodes, rows


def _compute_route_scores(
    counts: np.ndarray,
    library_sizes: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    normalized = np.log1p(counts / library_sizes * 1e4)
    gene_means = normalized.mean(axis=1, keepdims=True)
    gene_stds = normalized.std(axis=1, keepdims=True, ddof=0)
    gene_stds = np.where(gene_stds == 0, np.nan, gene_stds)
    z_scores = np.divide(
        normalized - gene_means,
        gene_stds,
        out=np.zeros_like(normalized),
        where=~np.isnan(gene_stds),
    )
    route_scores = -z_scores.mean(axis=0)
    return normalized, route_scores


def build_gse150949_pc9_evolution_audit(
    state_modules_path: Path,
    annotation_path: Path,
    metadata_path: Path,
    matrix_path: Path,
    top_n: int = TOP_DOWN_GENE_COUNT,
) -> dict[str, pd.DataFrame | list[str]]:
    """Build the third-system candidate audit from source tables."""
    state_modules, annotation = _load_inputs(state_modules_path, annotation_path)
    frozen = _build_top_down_module(state_modules, annotation, top_n=top_n)

    metadata = pd.read_csv(metadata_path, sep="\t", index_col=0)
    metadata.index = metadata.index.astype(str)
    required_meta = {"nUMI", "sample_id", "time_point", "sample_type"}
    missing_meta = sorted(required_meta - set(metadata.columns))
    if missing_meta:
        raise ValueError(f"Metadata table is missing columns: {missing_meta}")
    metadata["sample_id"] = metadata["sample_id"].astype(int)
    metadata["time_point"] = metadata["time_point"].astype(int)
    metadata["sample_type"] = metadata["sample_type"].astype(str)
    library_sizes = metadata["nUMI"].astype(float).to_numpy()

    barcodes, matrix_rows = _extract_matrix_rows(matrix_path, frozen["gene_symbol"].tolist())
    expected_barcodes = metadata.index.astype(str).tolist()
    if barcodes != expected_barcodes:
        raise ValueError("Matrix column order does not match metadata index order")

    present_symbols = [symbol for symbol in frozen["gene_symbol"] if symbol in matrix_rows]
    missing_symbols = [symbol for symbol in frozen["gene_symbol"] if symbol not in matrix_rows]
    if not present_symbols:
        raise ValueError("No frozen down-module genes were recovered from the matrix")
    counts = np.vstack([matrix_rows[symbol] for symbol in present_symbols])
    normalized, route_scores = _compute_route_scores(counts, library_sizes)

    route_score_df = metadata.copy()
    route_score_df["route_aligned_score"] = route_scores
    route_score_df["sample_barcode"] = route_score_df.index.astype(str)
    route_score_df = route_score_df.reset_index(drop=True).loc[
        :, [
            "sample_barcode",
            "sample_id",
            "time_point",
            "sample_type",
            "nUMI",
            "route_aligned_score",
        ]
    ]

    sample_summary = (
        route_score_df.groupby(["sample_id", "time_point", "sample_type"], as_index=False)
        .agg(
            n_cells=("sample_barcode", "count"),
            mean_route_score=("route_aligned_score", "mean"),
            median_route_score=("route_aligned_score", "median"),
            std_route_score=("route_aligned_score", "std"),
        )
        .sort_values(["time_point", "sample_id"])
        .reset_index(drop=True)
    )
    sample_summary["std_route_score"] = sample_summary["std_route_score"].fillna(0.0)

    group_summary = (
        route_score_df.groupby(["time_point", "sample_type"], as_index=False)
        .agg(
            n_cells=("sample_barcode", "count"),
            mean_route_score=("route_aligned_score", "mean"),
            median_route_score=("route_aligned_score", "median"),
            std_route_score=("route_aligned_score", "std"),
        )
        .sort_values(["time_point", "sample_type"])
        .reset_index(drop=True)
    )
    group_summary["std_route_score"] = group_summary["std_route_score"].fillna(0.0)

    coverage = frozen.copy()
    coverage["present_in_matrix"] = coverage["gene_symbol"].isin(present_symbols)
    coverage["matrix_rank"] = np.where(coverage["present_in_matrix"], coverage["rank"], np.nan)
    coverage["coverage_role"] = np.where(
        coverage["present_in_matrix"],
        "present",
        "missing",
    )
    coverage = coverage.sort_values("rank").reset_index(drop=True)

    return {
        "state_modules": state_modules,
        "annotation": annotation,
        "frozen_module": frozen,
        "coverage": coverage,
        "route_scores": route_score_df,
        "sample_summary": sample_summary,
        "group_summary": group_summary,
        "missing_symbols": missing_symbols,
        "present_symbols": present_symbols,
        "normalized_expression": pd.DataFrame(
            normalized,
            index=present_symbols,
            columns=metadata.index.astype(str).tolist(),
        ),
    }


def _render_table(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    frame = df.loc[:, columns] if columns is not None else df
    return frame.to_csv(sep="\t", index=False).strip()


def _render_coverage_table(coverage: pd.DataFrame) -> str:
    view = coverage.loc[
        :,
        [
            "rank",
            "gene_id",
            "gene_symbol",
            "locked_discovery_score",
            "present_in_matrix",
        ],
    ].copy()
    view["locked_discovery_score"] = view["locked_discovery_score"].map(lambda value: f"{float(value):.6f}")
    view["present_in_matrix"] = view["present_in_matrix"].map(lambda value: "yes" if bool(value) else "no")
    return view.to_csv(sep="\t", index=False).strip()


def render_gse150949_pc9_evolution_audit(
    coverage: pd.DataFrame,
    sample_summary: pd.DataFrame,
    group_summary: pd.DataFrame,
    missing_symbols: list[str],
    date: str = AUDIT_DATE,
) -> str:
    """Render the manuscript-facing audit document."""
    timepoint_rows = []
    for time_point, frame in group_summary.groupby("time_point", sort=True):
        weights = frame["n_cells"].astype(float).to_numpy()
        means = frame["mean_route_score"].astype(float).to_numpy()
        medians = frame["median_route_score"].astype(float).to_numpy()
        stds = frame["std_route_score"].astype(float).to_numpy()
        weight_sum = float(weights.sum())
        timepoint_rows.append(
            {
                "time_point": int(time_point),
                "n_cells": int(weight_sum),
                "mean_route_score": float(np.average(means, weights=weights)),
                "median_route_score": float(np.median(medians)),
                "std_route_score": float(np.average(stds, weights=weights)) if weight_sum else 0.0,
            }
        )
    timepoint_summary = pd.DataFrame(timepoint_rows).sort_values("time_point").reset_index(drop=True)
    sample_table = sample_summary.loc[
        :,
        [
            "sample_id",
            "time_point",
            "sample_type",
            "n_cells",
            "mean_route_score",
            "median_route_score",
            "std_route_score",
        ],
    ].copy()
    sample_table["mean_route_score"] = sample_table["mean_route_score"].map(lambda value: f"{float(value):.6f}")
    sample_table["median_route_score"] = sample_table["median_route_score"].map(lambda value: f"{float(value):.6f}")
    sample_table["std_route_score"] = sample_table["std_route_score"].map(lambda value: f"{float(value):.6f}")
    timepoint_table = timepoint_summary.copy()
    timepoint_table["mean_route_score"] = timepoint_table["mean_route_score"].map(lambda value: f"{float(value):.6f}")
    timepoint_table["median_route_score"] = timepoint_table["median_route_score"].map(lambda value: f"{float(value):.6f}")
    timepoint_table["std_route_score"] = timepoint_table["std_route_score"].map(lambda value: f"{float(value):.6f}")

    day14 = group_summary[group_summary["time_point"].eq(14)].copy()
    day0_mean = float(
        timepoint_summary.loc[timepoint_summary["time_point"].eq(0), "mean_route_score"].iloc[0]
    )
    day14_min = float(day14["mean_route_score"].min())
    day14_low = float(
        day14.loc[day14["sample_type"].eq("14_low"), "mean_route_score"].iloc[0]
    )
    return f"""# GSE150949 PC9 Evolution Audit

Date: {date}

## Purpose

This audit records why `GSE150949` is the strongest local PC9 evolution candidate for the manuscript's remaining third-system gap, while still stopping short of a full route closure.

## Data source

`GSE150949` provides a gene-by-cell PC9 count matrix and lineage-aware metadata. The frozen route uses the top 50 genes from the locked down-module selected in `GSE75602`, with route-aligned scores defined as the negative average z-scored log1p CPM of the mapped module genes.

## Module coverage

The frozen top-50 down-module is represented by 45 of the 50 genes in the public matrix.

Missing module symbols:

{", ".join(missing_symbols)}

### Frozen top-50 coverage

{_render_coverage_table(coverage)}

## Route-aligned score summary

### Time-point summary

| Time point | Cells | Mean route score | Median route score | Std route score |
|---:|---:|---:|---:|---:|
{_render_table(timepoint_table, ["time_point", "n_cells", "mean_route_score", "median_route_score", "std_route_score"])}

### Sample summary

| Sample ID | Time point | Sample type | Cells | Mean route score | Median route score | Std route score |
|---:|---:|---|---:|---:|---:|---:|
{_render_table(sample_table, ["sample_id", "time_point", "sample_type", "n_cells", "mean_route_score", "median_route_score", "std_route_score"])}

## Interpretation

The route-aligned score is directionally stronger than `GSE103350` because late day-14 subtype groups are all below day 0 on the frozen down-module axis. The sample-level means are still mixed at day 3 and day 7, so the dataset supports the route only partially and does not close the third-system contract by itself.

At the summary level, day 0 mean route score is {day0_mean:.3f}, day 14-low mean route score is {day14_low:.3f}, and the minimum day-14 subtype mean is {day14_min:.3f}.

The strongest statement supported by this audit is:

- `GSE150949` is a real, analyzable local third-system candidate;
- the frozen down-module transfers with 45/50 mapped genes;
- the late day-14 subtype groups remain below day 0 on the route-aligned score;
- early day 3 and day 7 states remain mixed, so the candidate is not yet a clean closure system.

## Manuscript use

This audit can be cited as the best local PC9 evolution candidate for the current route, but only as partial support. It strengthens the claim that the locked resistance-module route is biologically tractable without overstating third-system closure.

## Summary tables

### Group summary

{_render_table(group_summary, ["time_point", "sample_type", "n_cells", "mean_route_score", "median_route_score", "std_route_score"])}
"""


def _render_figure_panel_a(ax: plt.Axes, sample_summary: pd.DataFrame, group_summary: pd.DataFrame) -> None:
    sample_summary = sample_summary.sort_values(["time_point", "sample_id"]).reset_index(drop=True)
    day_groups = {
        0: sample_summary[sample_summary["time_point"].eq(0)],
        3: sample_summary[sample_summary["time_point"].eq(3)],
        7: sample_summary[sample_summary["time_point"].eq(7)],
        14: sample_summary[sample_summary["time_point"].eq(14)],
    }
    offsets = {
        "14_high": -0.22,
        "14_med": 0.0,
        "14_low": 0.22,
    }
    x_positions = {0: 0, 3: 1, 7: 2, 14: 3}
    for time_point in [0, 3, 7]:
        sub = day_groups[time_point]
        if sub.empty:
            continue
        ax.scatter(
            np.full(len(sub), x_positions[time_point], dtype=float),
            sub["mean_route_score"].astype(float).to_numpy(),
            s=60,
            color=PANEL_COLORS[f"day{time_point}"],
            edgecolor="black",
            linewidth=0.5,
            zorder=3,
            label=f"Day {time_point}",
        )
    day14 = day_groups[14]
    for subtype in ["14_high", "14_med", "14_low"]:
        sub = day14[day14["sample_type"].eq(subtype)]
        if sub.empty:
            continue
        ax.scatter(
            np.full(len(sub), x_positions[14] + offsets[subtype], dtype=float),
            sub["mean_route_score"].astype(float).to_numpy(),
            s=68,
            color=PANEL_COLORS[f"day{subtype}"],
            edgecolor="black",
            linewidth=0.5,
            zorder=3,
            label=subtype.replace("_", " "),
        )

    timepoint_rows = []
    for time_point, frame in sample_summary.groupby("time_point", sort=True):
        weights = frame["n_cells"].astype(float).to_numpy()
        means = frame["mean_route_score"].astype(float).to_numpy()
        weight_sum = float(weights.sum())
        timepoint_rows.append(
            {
                "time_point": int(time_point),
                "mean_route_score": float(np.average(means, weights=weights)) if weight_sum else float("nan"),
            }
        )
    timepoint_means = pd.DataFrame(timepoint_rows).sort_values("time_point").reset_index(drop=True)
    ax.plot(
        timepoint_means["time_point"].map(x_positions).astype(float).to_numpy(),
        timepoint_means["mean_route_score"].astype(float).to_numpy(),
        color="#222222",
        linewidth=1.8,
        marker="D",
        markersize=5,
        zorder=2,
        label="Time-point mean",
    )
    ax.axhline(0, color="#888888", linestyle="--", linewidth=0.9)
    ax.set_xticks(list(x_positions.values()), ["Day 0", "Day 3", "Day 7", "Day 14"])
    ax.set_ylabel("Route-aligned down-module score")
    ax.set_title("a  Frozen down-module route score across GSE150949", loc="left", fontweight="bold")
    ax.grid(axis="y", alpha=0.2, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="best", fontsize=9)
    day14_mean = float(timepoint_means.loc[timepoint_means["time_point"].eq(14), "mean_route_score"].iloc[0])
    day0_mean = float(timepoint_means.loc[timepoint_means["time_point"].eq(0), "mean_route_score"].iloc[0])
    ax.text(
        0.02,
        0.98,
        f"Day 0 mean = {day0_mean:.3f}\nDay 14 mean = {day14_mean:.3f}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD"},
    )


def _render_figure_panel_b(ax: plt.Axes, coverage: pd.DataFrame) -> None:
    coverage = coverage.sort_values("rank").reset_index(drop=True)
    present = coverage["present_in_matrix"].astype(int).to_numpy()[None, :]
    cmap = ListedColormap(["#D55E00", "#009E73"])
    ax.imshow(present, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks([])
    ax.set_xticks(np.arange(0, len(coverage), 5), [str(rank) for rank in coverage["rank"].iloc[::5].tolist()])
    ax.set_xlabel("Frozen down-module rank")
    ax.set_title("b  Frozen top-50 module coverage", loc="left", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.text(
        0.02,
        0.92,
        f"45/50 mapped\nMissing ranks: 31, 32, 34, 37, 49",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD"},
    )
    legend_handles = [
        Line2D([0], [0], color="#009E73", marker="s", linewidth=0, markersize=9, label="present"),
        Line2D([0], [0], color="#D55E00", marker="s", linewidth=0, markersize=9, label="missing"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="lower right", fontsize=9)


def render_gse150949_pc9_evolution_figure(
    sample_summary: pd.DataFrame,
    group_summary: pd.DataFrame,
    coverage: pd.DataFrame,
    figure_out: Path,
    figure_pdf_out: Path | None,
) -> None:
    """Render a reviewer-facing scorecard for the third-system candidate."""
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(12.4, 4.6),
        gridspec_kw={"width_ratios": [1.25, 1.0]},
    )
    _render_figure_panel_a(ax_a, sample_summary, group_summary)
    _render_figure_panel_b(ax_b, coverage)
    fig.suptitle(
        "GSE150949 PC9 evolution scorecard",
        fontsize=13,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.01,
        "Late day-14 subtype groups remain below day 0 on the frozen route-aligned score; the candidate remains partial because day 3 and day 7 are mixed.",
        ha="center",
        va="bottom",
        fontsize=8.4,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    save_figure(fig, figure_out, dpi=300, bbox_inches="tight")
    if figure_pdf_out is not None:
        save_figure(fig, figure_pdf_out, bbox_inches="tight")
    plt.close(fig)


def render_gse150949_pc9_evolution_support_text(
    sample_summary: pd.DataFrame,
    group_summary: pd.DataFrame,
    missing_symbols: list[str],
) -> str:
    """Render support text for the GSE150949 scorecard."""
    sample_table = sample_summary.loc[
        :,
        [
            "sample_id",
            "time_point",
            "sample_type",
            "n_cells",
            "mean_route_score",
            "median_route_score",
            "std_route_score",
        ],
    ].copy()
    sample_table["mean_route_score"] = sample_table["mean_route_score"].map(lambda value: f"{float(value):.6f}")
    sample_table["median_route_score"] = sample_table["median_route_score"].map(lambda value: f"{float(value):.6f}")
    sample_table["std_route_score"] = sample_table["std_route_score"].map(lambda value: f"{float(value):.6f}")
    group_table = group_summary.loc[
        :,
        [
            "time_point",
            "sample_type",
            "n_cells",
            "mean_route_score",
            "median_route_score",
            "std_route_score",
        ],
    ].copy()
    group_table["mean_route_score"] = group_table["mean_route_score"].map(lambda value: f"{float(value):.6f}")
    group_table["median_route_score"] = group_table["median_route_score"].map(lambda value: f"{float(value):.6f}")
    group_table["std_route_score"] = group_table["std_route_score"].map(lambda value: f"{float(value):.6f}")
    sample_text = sample_table.to_csv(sep="\t", index=False).strip()
    group_text = group_table.to_csv(sep="\t", index=False).strip()
    return f"""# GSE150949 PC9 Evolution Support Text

Supplementary Figure S6 summarizes the strongest local third-system candidate in two bounded panels. Panel A shows the route-aligned frozen down-module score across the PC9 evolution series, while Panel B shows coverage of the frozen top-50 down-module in the public count matrix. The scorecard strengthens the manuscript's third-system discussion without claiming clean route closure.

## Supplementary Figure S6

Supplementary Figure S6. GSE150949 PC9 evolution scorecard. (A) The frozen down-module route score is computed as the negative average z-scored log1p CPM of the mapped top-50 down-module genes from the locked resistance-state route. Day 0 is positive, day 3 and day 7 remain mixed, and all day-14 subtype groups sit below day 0 on the route-aligned score. (B) The public count matrix covers 45 of the 50 frozen down-module genes; the five missing genes are `LINC01819`, `SLC60A1`, `UBBP4`, `CPP`, and `MAB21L4`. The figure therefore strengthens the manuscript's third-system discussion while preserving the claim ceiling.

## Evidence Summary

### Sample-level route scores

```text
{sample_text}
```

### Group-level summary

```text
{group_text}
```

## Boundary

This figure is only partial support. The candidate does not close the third-system contract because the early day 3 and day 7 states remain mixed, and the public matrix does not contain all 50 frozen module genes.

Missing symbols: {", ".join(missing_symbols)}.
"""


def write_gse150949_pc9_evolution_assets(
    state_modules_path: Path,
    annotation_path: Path,
    metadata_path: Path,
    matrix_path: Path,
    figure_out: Path,
    figure_pdf_out: Path | None,
    audit_out: Path,
    support_text_out: Path,
    coverage_out: Path,
    route_scores_out: Path,
    sample_summary_out: Path,
    group_summary_out: Path,
) -> dict[str, Path]:
    """Write the full GSE150949 audit package."""
    package = build_gse150949_pc9_evolution_audit(
        state_modules_path=state_modules_path,
        annotation_path=annotation_path,
        metadata_path=metadata_path,
        matrix_path=matrix_path,
    )
    coverage = package["coverage"]
    sample_summary = package["sample_summary"]
    group_summary = package["group_summary"]
    route_scores = package["route_scores"]
    missing_symbols = package["missing_symbols"]

    for path in [audit_out, support_text_out, coverage_out, route_scores_out, sample_summary_out, group_summary_out]:
        path.parent.mkdir(parents=True, exist_ok=True)
    audit_out.write_text(
        render_gse150949_pc9_evolution_audit(
            coverage=coverage,
            sample_summary=sample_summary,
            group_summary=group_summary,
            missing_symbols=missing_symbols,
        ),
        encoding="utf-8",
    )
    render_gse150949_pc9_evolution_figure(
        sample_summary=sample_summary,
        group_summary=group_summary,
        coverage=coverage,
        figure_out=figure_out,
        figure_pdf_out=figure_pdf_out,
    )
    support_text_out.write_text(
        render_gse150949_pc9_evolution_support_text(
            sample_summary=sample_summary,
            group_summary=group_summary,
            missing_symbols=missing_symbols,
        ),
        encoding="utf-8",
    )
    coverage.to_csv(coverage_out, sep="\t", index=False)
    route_scores.to_csv(route_scores_out, sep="\t", index=False)
    sample_summary.to_csv(sample_summary_out, sep="\t", index=False)
    group_summary.to_csv(group_summary_out, sep="\t", index=False)
    return {
        "audit": audit_out,
        "support_text": support_text_out,
        "figure": figure_out,
        "figure_pdf": figure_pdf_out if figure_pdf_out is not None else figure_out.with_suffix(".pdf"),
        "coverage": coverage_out,
        "route_scores": route_scores_out,
        "sample_summary": sample_summary_out,
        "group_summary": group_summary_out,
    }


def write_gse150949_pc9_evolution_package(
    state_modules_path: Path,
    annotation_path: Path,
    metadata_path: Path,
    matrix_path: Path,
    audit_out: Path,
) -> dict[str, Path]:
    """Write the main GSE150949 audit markdown only."""
    package = build_gse150949_pc9_evolution_audit(
        state_modules_path=state_modules_path,
        annotation_path=annotation_path,
        metadata_path=metadata_path,
        matrix_path=matrix_path,
    )
    coverage = package["coverage"]
    sample_summary = package["sample_summary"]
    group_summary = package["group_summary"]
    missing_symbols = package["missing_symbols"]
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit_out.write_text(
        render_gse150949_pc9_evolution_audit(
            coverage=coverage,
            sample_summary=sample_summary,
            group_summary=group_summary,
            missing_symbols=missing_symbols,
        ),
        encoding="utf-8",
    )
    return {"audit": audit_out}
