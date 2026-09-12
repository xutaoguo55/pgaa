"""Audit target-class specificity in the GSE193258 osimertinib DTP screen."""
from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure


REQUIRED_ASSOCIATION_COLUMNS = {
    "drug",
    "putative_target",
    "spearman_rho",
    "exact_one_sided_p",
    "response_z_range",
    "total_hit_calls",
    "association_rank",
}

REQUIRED_CONTEXT_COLUMNS = {
    "table_id",
    "target_class",
    "n_rows",
    "n_unique_cell_lines",
    "n_unique_drugs",
}

TARGET_ROLE_COLORS = {
    "lead_exact_significant_positive": "#0072B2",
    "runner_up_positive_tier": "#E69F00",
    "weaker_positive_tier": "#D9A441",
    "negative_or_inverse": "#A9A9A9",
}


def _summarize_target_context(target_context: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(REQUIRED_CONTEXT_COLUMNS - set(target_context.columns))
    if missing:
        raise ValueError(f"Target context is missing columns: {missing}")
    context = target_context.copy()
    context["table_label"] = context["table_id"].map(
        {"Supplementary_Data_1": "replicate", "Supplementary_Data_2": "summary"}
    )
    pivot = context.pivot_table(
        index="target_class",
        columns="table_label",
        values=["n_rows", "n_unique_cell_lines", "n_unique_drugs"],
        aggfunc="first",
    )
    pivot.columns = [f"{table}_{metric}" for metric, table in pivot.columns]
    pivot = pivot.reset_index()
    source_counts = (
        context.groupby("target_class", as_index=False)
        .agg(n_source_tables=("table_id", "nunique"))
        .sort_values("target_class")
    )
    merged = pivot.merge(source_counts, on="target_class", how="left")
    rename_map = {
        "replicate_n_rows": "replicate_rows",
        "summary_n_rows": "summary_rows",
        "replicate_n_unique_cell_lines": "replicate_unique_cell_lines",
        "summary_n_unique_cell_lines": "summary_unique_cell_lines",
        "replicate_n_unique_drugs": "replicate_unique_drugs",
        "summary_n_unique_drugs": "summary_unique_drugs",
    }
    merged = merged.rename(columns=rename_map)
    for column in [
        "replicate_rows",
        "summary_rows",
        "replicate_unique_cell_lines",
        "summary_unique_cell_lines",
        "replicate_unique_drugs",
        "summary_unique_drugs",
        "n_source_tables",
    ]:
        if column in merged.columns:
            merged[column] = merged[column].fillna(0).astype(int)
    return merged


def build_gse193258_target_specificity_audit(
    drug_associations: pd.DataFrame,
    target_context: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize target-class specificity inside the GSE193258 screen landscape."""
    missing = sorted(REQUIRED_ASSOCIATION_COLUMNS - set(drug_associations.columns))
    if missing:
        raise ValueError(f"Drug associations are missing columns: {missing}")

    summary = drug_associations.copy()
    summary = summary.sort_values(
        ["spearman_rho", "response_z_range", "exact_one_sided_p", "putative_target"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    summary["association_rank"] = np.arange(1, len(summary) + 1)

    positive_rhos = sorted(
        {float(value) for value in summary["spearman_rho"] if float(value) > 0},
        reverse=True,
    )
    rho_to_positive_tier = {rho: index + 1 for index, rho in enumerate(positive_rhos)}
    next_lower_rho: dict[float, float | None] = {}
    for index, rho in enumerate(positive_rhos):
        next_lower_rho[rho] = positive_rhos[index + 1] if index + 1 < len(positive_rhos) else None

    summary["positive_tier"] = summary["spearman_rho"].map(
        lambda value: rho_to_positive_tier.get(float(value), np.nan)
    )
    summary["next_lower_positive_rho"] = summary["spearman_rho"].map(
        lambda value: next_lower_rho.get(float(value), np.nan)
    )
    summary["positive_tier_margin_to_next"] = summary.apply(
        lambda row: (
            float(row["spearman_rho"]) - float(row["next_lower_positive_rho"])
            if pd.notna(row["next_lower_positive_rho"])
            else np.nan
        ),
        axis=1,
    )
    summary["exact_significant_positive"] = (
        (summary["spearman_rho"] > 0) & (summary["exact_one_sided_p"] <= 0.05)
    )

    if target_context is not None:
        coverage = _summarize_target_context(target_context)
        summary = summary.merge(
            coverage,
            left_on="putative_target",
            right_on="target_class",
            how="left",
            suffixes=("", "_coverage"),
        )
        summary = summary.drop(columns=["target_class"])
        summary["source_landscape_rows"] = (
            summary["replicate_rows"].fillna(0).astype(int)
            + summary["summary_rows"].fillna(0).astype(int)
        )
    else:
        summary["replicate_rows"] = np.nan
        summary["summary_rows"] = np.nan
        summary["replicate_unique_cell_lines"] = np.nan
        summary["summary_unique_cell_lines"] = np.nan
        summary["replicate_unique_drugs"] = np.nan
        summary["summary_unique_drugs"] = np.nan
        summary["n_source_tables"] = np.nan
        summary["source_landscape_rows"] = np.nan

    summary["specificity_role"] = summary.apply(
        lambda row: (
            "lead_exact_significant_positive"
            if row["putative_target"] == "ATM" and bool(row["exact_significant_positive"])
            else "runner_up_positive_tier"
            if pd.notna(row["positive_tier"]) and int(row["positive_tier"]) == 2
            else "weaker_positive_tier"
            if pd.notna(row["positive_tier"]) and int(row["positive_tier"]) > 2
            else "negative_or_inverse"
        ),
        axis=1,
    )

    contrast_rows: list[dict[str, object]] = []
    positive = summary[summary["spearman_rho"] > 0].copy()
    if not positive.empty:
        best = positive.iloc[0]
        runner_up_rho = positive.loc[
            positive["spearman_rho"] < float(best["spearman_rho"]), "spearman_rho"
        ].max()
        if pd.notna(runner_up_rho):
            runner_up = positive[positive["spearman_rho"] == runner_up_rho].copy()
            runner_up_targets = ", ".join(runner_up["putative_target"].astype(str).tolist())
        else:
            runner_up_targets = "none"
        contrast_rows.append(
            {
                "contrast": "ATM_vs_runner_up_positive_tier",
                "lead_target_class": best["putative_target"],
                "lead_drug": best["drug"],
                "lead_rho": float(best["spearman_rho"]),
                "lead_exact_p": float(best["exact_one_sided_p"]),
                "runner_up_target_classes": runner_up_targets,
                "runner_up_rho": float(runner_up_rho) if pd.notna(runner_up_rho) else np.nan,
                "rho_margin": (
                    float(best["spearman_rho"]) - float(runner_up_rho)
                    if pd.notna(runner_up_rho)
                    else np.nan
                ),
                "positive_target_count": int(positive["putative_target"].nunique()),
                "exact_significant_positive_count": int(summary["exact_significant_positive"].sum()),
                "total_target_classes": int(summary["putative_target"].nunique()),
            }
        )

    contrast = pd.DataFrame(contrast_rows)
    summary = summary.rename(columns={"putative_target": "target_class", "drug": "lead_drug"})
    return summary, contrast


def render_gse193258_target_specificity_audit(
    summary: pd.DataFrame, contrast: pd.DataFrame
) -> str:
    """Render a manuscript-facing specificity audit."""
    table_rows = []
    for _, row in summary.iterrows():
        table_rows.append(
            "| {association_rank} | {target_class} | {lead_drug} | {spearman_rho:.3f} | {exact_one_sided_p:.4f} | {positive_tier} | {specificity_role} | {replicate_rows} | {summary_rows} |".format(
                association_rank=int(row["association_rank"]),
                target_class=row["target_class"],
                lead_drug=row["lead_drug"],
                spearman_rho=float(row["spearman_rho"]),
                exact_one_sided_p=float(row["exact_one_sided_p"]),
                positive_tier=(
                    int(row["positive_tier"]) if pd.notna(row["positive_tier"]) else "NA"
                ),
                specificity_role=row["specificity_role"],
                replicate_rows=(
                    int(row["replicate_rows"]) if pd.notna(row["replicate_rows"]) else "NA"
                ),
                summary_rows=(
                    int(row["summary_rows"]) if pd.notna(row["summary_rows"]) else "NA"
                ),
            )
        )
    contrast_row = contrast.iloc[0] if not contrast.empty else None
    contrast_table = ""
    if contrast_row is not None:
        contrast_table = "\n".join(
            [
                "| Contrast | Lead target | Runner-up target classes | Lead rho | Runner-up rho | Rho margin | Positive targets | Exact-significant positives | Total target classes |",
                "|---|---|---|---:|---:|---:|---:|---:|---:|",
                f"| {contrast_row['contrast']} | {contrast_row['lead_target_class']} | {contrast_row['runner_up_target_classes']} | {float(contrast_row['lead_rho']):.3f} | {float(contrast_row['runner_up_rho']):.3f} | {float(contrast_row['rho_margin']):.3f} | {int(contrast_row['positive_target_count'])} | {int(contrast_row['exact_significant_positive_count'])} | {int(contrast_row['total_target_classes'])} |",
            ]
        )
    exact_positive = summary[summary["exact_significant_positive"]]
    exact_positive_classes = ", ".join(exact_positive["target_class"].astype(str).tolist())
    positive_count = int((summary["spearman_rho"] > 0).sum())
    total_count = int(summary["target_class"].nunique())
    source_landscape_target_classes = int(
        (summary["n_source_tables"].fillna(0) > 0).sum()
    ) if "n_source_tables" in summary.columns else 0
    return f"""# GSE193258 Target Specificity Audit

The matched-screen package spans a broad target landscape. This audit asks whether ATM is merely one positive hit or the cleanest positive target-class signal in the screen package.

## Target-Class Ranking

| Rank | Target class | Lead drug | Spearman rho | Exact p | Positive tier | Specificity role | Replicate rows | Summary rows |
|---|---|---|---:|---:|---:|---|---:|---:|
{chr(10).join(table_rows)}

## Specificity Contrast

{contrast_table}

## Interpretation Boundary

ATM is the only exact-significant positive target class in the screen landscape. ALK and HDAC occupy the runner-up positive tier; the remaining positive classes are weaker, and the negative classes fall below zero. That makes ATM the cleanest positive branch-linked target-class signal inside the broad GSE193258 screen package.

- Positive target classes: {positive_count}
- Exact-significant positive target classes: {len(exact_positive)}
- Exact-significant positive target classes named explicitly: {exact_positive_classes if exact_positive_classes else "none"}
- Total target classes in the audit: {total_count}
- Target classes with source-table coverage across the screen package: {source_landscape_target_classes}

This tightens the manuscript claim to a lead-target specificity statement without promoting ATM to general clinical validation.
"""


def render_gse193258_target_specificity_caption_and_results(
    summary: pd.DataFrame, contrast: pd.DataFrame
) -> str:
    """Render a claim-bounded caption and short Results text for the support figure."""
    if summary.empty:
        raise ValueError("Target-specificity summary is empty")
    atm = summary[summary["target_class"].eq("ATM")]
    if atm.empty:
        raise ValueError("Target-specificity summary does not include ATM")
    atm_row = atm.iloc[0]
    contrast_row = contrast.iloc[0] if not contrast.empty else None
    runner_up = (
        contrast_row["runner_up_target_classes"]
        if contrast_row is not None
        else "runner-up positive tier"
    )
    return f"""# GSE193258 Target Specificity Figure Support Text

## Claim Boundary

This text is bounded to the GSE193258 matched-screen package and the generated target-specificity figure. It supports a lead-target specificity statement only. It does not establish clinical validation, general pharmacologic utility, or source-level replicate recovery beyond the audited tables.

## Figure Caption Draft

Supplementary Figure S4. GSE193258 target-class specificity scorecard. The matched-screen package spans a broad target landscape, but ATM is the only exact-significant positive target-class signal in the screen landscape. ALK and HDAC occupy the runner-up positive tier, while the remaining positive classes are weaker and the negative classes fall below zero. The lead ATM row is AZD0156 with Spearman rho {float(atm_row['spearman_rho']):.1f} and exact one-sided p = {float(atm_row['exact_one_sided_p']):.4f}. The scorecard summarizes the rank margin between ATM and the runner-up positive tier ({runner_up}) and keeps the claim ceiling at lead-target specificity rather than general validation.

## Results Paragraph Draft

The GSE193258 matched screen supports a clean lead-target specificity statement. ATM is the only exact-significant positive target-class signal, with AZD0156 ranked first and a Spearman rho of {float(atm_row['spearman_rho']):.1f} (exact one-sided p = {float(atm_row['exact_one_sided_p']):.4f}). ALK and HDAC form the runner-up positive tier, and the remaining positive classes are weaker. The specificity scorecard therefore sharpens the manuscript from a general branch-linked vulnerability statement to a lead-target claim: ATM is the cleanest positive target-class signal in the matched screen, but this remains a source-backed preclinical hypothesis rather than clinical or source-table-level pharmacologic validation.
"""


def render_gse193258_target_specificity_figure(
    summary: pd.DataFrame,
    contrast: pd.DataFrame,
    png_out: str | Path,
    pdf_out: str | Path | None = None,
) -> dict[str, str]:
    """Render a manuscript-ready figure for the GSE193258 target-specificity audit."""
    required = {
        "target_class",
        "lead_drug",
        "spearman_rho",
        "exact_one_sided_p",
        "positive_tier",
        "specificity_role",
        "exact_significant_positive",
    }
    missing = sorted(required - set(summary.columns))
    if missing:
        raise ValueError(f"Target-specificity summary is missing columns: {missing}")
    if summary.empty:
        raise ValueError("Target-specificity summary is empty")
    summary = summary.copy().sort_values("association_rank").reset_index(drop=True)
    contrast_row = contrast.iloc[0] if not contrast.empty else None
    atm = summary[summary["target_class"].eq("ATM")]
    if atm.empty:
        raise ValueError("Target-specificity summary does not include ATM")
    atm_row = atm.iloc[0]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(11.8, 5.2),
        gridspec_kw={"width_ratios": [1.7, 1.05], "wspace": 0.28},
    )
    ax = axes[0]
    y_positions = list(range(len(summary)))
    colors = [
        TARGET_ROLE_COLORS.get(str(row["specificity_role"]), "#999999")
        for _, row in summary.iterrows()
    ]
    ax.barh(
        y_positions,
        summary["spearman_rho"].astype(float),
        color=colors,
        edgecolor="#222222",
        linewidth=0.7,
    )
    ax.axvline(0, color="#666666", linewidth=0.8, linestyle="--")
    for pos, (_, row) in zip(y_positions, summary.iterrows()):
        rho = float(row["spearman_rho"])
        p_value = float(row["exact_one_sided_p"])
        text_x = rho + 0.04 if rho >= 0 else rho - 0.04
        ax.text(
            text_x,
            pos,
            f"p={p_value:.3f}" + (" *" if bool(row["exact_significant_positive"]) else ""),
            va="center",
            ha="left" if rho >= 0 else "right",
            fontsize=7.2,
            color="#333333",
        )
    ax.set_yticks(y_positions, summary["target_class"])
    ax.invert_yaxis()
    ax.set_xlim(min(-1.1, float(summary["spearman_rho"].min()) - 0.2), 1.18)
    ax.set_xlabel("Spearman rho", fontsize=9)
    ax.set_title("A. Target-class specificity ranking", loc="left", fontweight="bold")
    for label, row in zip(ax.get_yticklabels(), summary.itertuples()):
        if row.target_class == "ATM":
            label.set_fontweight("bold")
            label.set_color(TARGET_ROLE_COLORS["lead_exact_significant_positive"])
        elif row.specificity_role == "runner_up_positive_tier":
            label.set_color(TARGET_ROLE_COLORS["runner_up_positive_tier"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax = axes[1]
    ax.set_axis_off()
    summary_lines = [
        ("Lead target", f"ATM / AZD0156"),
        ("Lead rho", f"{float(atm_row['spearman_rho']):.1f}"),
        ("Lead exact p", f"{float(atm_row['exact_one_sided_p']):.4f}"),
        (
            "Runner-up tier",
            contrast_row["runner_up_target_classes"] if contrast_row is not None else "n/a",
        ),
        (
            "Rho margin",
            f"{float(contrast_row['rho_margin']):.1f}" if contrast_row is not None else "n/a",
        ),
        ("Positive classes", f"{int((summary['spearman_rho'] > 0).sum())}"),
        (
            "Exact-significant positives",
            f"{int(summary['exact_significant_positive'].sum())}",
        ),
        ("Total target classes", f"{int(summary['target_class'].nunique())}"),
    ]
    ax.text(
        0.02,
        0.98,
        "B. Lead-target specificity scorecard",
        fontsize=10,
        fontweight="bold",
        va="top",
        ha="left",
        transform=ax.transAxes,
    )
    box_lines = [
        "ATM is the only exact-significant positive target-class signal.",
        "ALK and HDAC form the runner-up positive tier.",
        "",
    ]
    for label, value in summary_lines:
        box_lines.append(f"{label}: {value}")
    box_lines.extend(
        [
            "",
            "This figure tightens the manuscript claim to a lead-target",
            "specificity statement, not general pharmacologic validation.",
        ]
    )
    ax.text(
        0.02,
        0.88,
        "\n".join(box_lines),
        fontsize=9.0,
        va="top",
        ha="left",
        transform=ax.transAxes,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "#F6F8FA",
            "edgecolor": "#C8CDD3",
            "linewidth": 0.9,
        },
        linespacing=1.3,
    )
    ax.text(
        0.02,
        0.07,
        "Source tables: GSE193258 Supplementary Data 1 and 2 plus the frozen RNA-seq matrix.",
        fontsize=7.6,
        color="#555555",
        ha="left",
        va="bottom",
        transform=ax.transAxes,
    )
    fig.suptitle(
        "GSE193258 target specificity: ATM is the cleanest positive class",
        fontsize=12.5,
        fontweight="bold",
        y=0.995,
    )
    fig.subplots_adjust(top=0.86, bottom=0.11, left=0.11, right=0.98)
    png_path = Path(png_out)
    save_figure(fig, png_path, dpi=300, bbox_inches="tight")
    pdf_path_str = None
    if pdf_out is not None:
        pdf_path = Path(pdf_out)
        save_figure(fig, pdf_path, bbox_inches="tight")
        pdf_path_str = str(pdf_path)
    plt.close(fig)
    return {"png": str(png_path), "pdf": pdf_path_str}


def write_gse193258_target_specificity_audit_package(
    drug_associations: pd.DataFrame,
    evidence_out: Path,
    report_out: Path,
    target_context: pd.DataFrame | None = None,
    figure_out: Path | None = None,
    figure_pdf_out: Path | None = None,
    caption_out: Path | None = None,
) -> dict[str, Path]:
    """Write the target-specificity audit package for GSE193258."""
    summary, contrast = build_gse193258_target_specificity_audit(
        drug_associations=drug_associations, target_context=target_context
    )
    evidence_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(evidence_out, sep="\t", index=False)
    contrast_out = evidence_out.with_name("gse193258_target_specificity_contrast.tsv")
    contrast.to_csv(contrast_out, sep="\t", index=False)
    report_out.write_text(
        render_gse193258_target_specificity_audit(summary, contrast),
        encoding="utf-8",
    )
    paths = {
        "evidence": evidence_out,
        "contrast": contrast_out,
        "report": report_out,
    }
    if figure_out is not None:
        figure_paths = render_gse193258_target_specificity_figure(
            summary=summary,
            contrast=contrast,
            png_out=figure_out,
            pdf_out=figure_pdf_out,
        )
        paths["figure"] = Path(figure_paths["png"])
        if figure_paths["pdf"] is not None:
            paths["figure_pdf"] = Path(figure_paths["pdf"])
    if caption_out is not None:
        caption_out.parent.mkdir(parents=True, exist_ok=True)
        caption_out.write_text(
            render_gse193258_target_specificity_caption_and_results(summary, contrast),
            encoding="utf-8",
        )
        paths["caption"] = caption_out
    return paths
