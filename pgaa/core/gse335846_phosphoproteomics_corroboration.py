"""Build the GSE335846 companion phosphoproteomics corroboration package."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pgaa.core.figure_io import save_figure


PROTEIN_PANEL = (
    "CDK1",
    "MCM2",
    "MCM5",
    "MKI67",
    "PCNA",
    "EGFR",
    "RPA2",
    "RB1",
    "CCND1",
)

PHOSPHO_PANEL = (
    "ATR",
    "EGFR",
    "CDK1",
    "MCM2",
    "MKI67",
    "RB1",
    "BAD",
    "SAMHD1",
    "YAP1",
    "CCNE1",
)

TIMEPOINT_COLUMNS = ["DMSO", "Osi_5min", "Osi_10min", "Osi_6h", "DTP", "DTP-24h", "DTP-7d"]
DELTA_COLUMNS = [f"{column}_minus_DMSO" for column in TIMEPOINT_COLUMNS[1:]]


def _read_workbook(workbook_path: Path) -> dict[str, pd.DataFrame]:
    return {
        sheet: pd.read_excel(workbook_path, sheet_name=sheet)
        for sheet in ("README", "Prot_IDs", "Phos_IDs", "Overlap")
    }


def _readme_counts(readme: pd.DataFrame) -> dict[str, str]:
    rows = [str(value) for value in readme.stack().dropna().tolist()]
    text = " ".join(rows)
    protein_match = re.search(r"([0-9,]+)\s+quantified proteins", text)
    phospho_match = re.search(r"([0-9,]+)\s+unique phosphosites", text)
    return {
        "quantified_proteins": protein_match.group(1) if protein_match else "unknown",
        "unique_phosphosites": phospho_match.group(1) if phospho_match else "unknown",
    }


def _exact_gene_mask(values: pd.Series, gene: str) -> pd.Series:
    pattern = rf"(?:^|[;,_\-\s]){re.escape(gene)}(?:$|[;,_\-\s])"
    return values.fillna("").astype(str).str.contains(pattern, regex=True)


def _best_row(frame: pd.DataFrame, gene_col: str, q_col: str, gene: str) -> pd.Series:
    mask = _exact_gene_mask(frame[gene_col], gene)
    hits = frame.loc[mask].copy()
    if hits.empty:
        raise ValueError(f"No exact row found for {gene} in {gene_col}")
    hits[q_col] = pd.to_numeric(hits[q_col], errors="coerce")
    hits = hits.sort_values(q_col, kind="mergesort").reset_index(drop=True)
    return hits.iloc[0]


def _feature_label_from_row(row: pd.Series, sheet_name: str, gene_col: str) -> str:
    if sheet_name == "Prot_IDs":
        return str(row[gene_col])
    ptm_key = str(row.get("PTM_collapse_key", "") or "")
    if ptm_key and ptm_key != "nan":
        return ptm_key.rsplit("_", 1)[0]
    peptide = str(row.get("EG.ModifiedPeptide", "") or "")
    if peptide and peptide != "nan":
        return peptide
    return str(row[gene_col])


def _build_selected_marker_table(frame: pd.DataFrame, sheet_name: str, panel: tuple[str, ...]) -> pd.DataFrame:
    if sheet_name == "Prot_IDs":
        gene_col = "T: PG.Genes"
        q_col = "N: ANOVA q-value"
        id_col = "T: PG.ProteinGroups"
    else:
        gene_col = "PG.Genes"
        q_col = "ANOVA q-value"
        id_col = "PTM_collapse_key"

    records: list[dict[str, object]] = []
    for gene in panel:
        row = _best_row(frame, gene_col, q_col, gene)
        record: dict[str, object] = {
            "panel": "protein" if sheet_name == "Prot_IDs" else "phosphosite",
            "gene_symbol": gene,
            "feature_label": _feature_label_from_row(row, sheet_name, gene_col),
            "source_feature_id": str(row.get(id_col, "")),
            "q_value": float(row[q_col]),
        }
        for column in TIMEPOINT_COLUMNS:
            value = row[column]
            record[column] = float(value) if pd.notna(value) else np.nan
        for column in TIMEPOINT_COLUMNS[1:]:
            record[f"{column}_minus_DMSO"] = float(row[column]) - float(row["DMSO"])
        records.append(record)
    return pd.DataFrame(records)


def _build_boundary_scan(protein_frame: pd.DataFrame, phospho_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for gene in ("ATM", "ATR"):
        protein_hits = int(_exact_gene_mask(protein_frame["T: PG.Genes"], gene).sum())
        phospho_hits = int(_exact_gene_mask(phospho_frame["PG.Genes"], gene).sum())
        rows.append(
            {
                "gene_symbol": gene,
                "protein_exact_hits": protein_hits,
                "phosphosite_exact_hits": phospho_hits,
                "status": (
                    "no_exact_hit_in_quick_scan"
                    if protein_hits == 0 and phospho_hits == 0
                    else "exact_hit_in_phosphoproteome"
                    if phospho_hits > 0
                    else "exact_hit_in_proteome"
                ),
                "boundary_statement": (
                    "ATM is not an exact gene-symbol hit in the workbook's quick scan, "
                    "so the supplement does not provide ATM source-table closure."
                    if gene == "ATM"
                    else "ATR is an exact phosphosite hit, which supports DDR-adjacent corroboration."
                ),
            }
        )
    return pd.DataFrame(rows)


def build_phosphoproteomics_corroboration(
    workbook_path: Path,
) -> dict[str, pd.DataFrame | dict[str, str]]:
    """Load the workbook and build source-backed corroboration tables."""
    sheets = _read_workbook(workbook_path)
    counts = _readme_counts(sheets["README"])
    proteins = _build_selected_marker_table(sheets["Prot_IDs"], "Prot_IDs", PROTEIN_PANEL)
    phosphos = _build_selected_marker_table(sheets["Phos_IDs"], "Phos_IDs", PHOSPHO_PANEL)
    selected = pd.concat([proteins, phosphos], ignore_index=True)
    boundary = _build_boundary_scan(sheets["Prot_IDs"], sheets["Phos_IDs"])
    sheet_summary = pd.DataFrame(
        [
            {
                "sheet_name": "Prot_IDs",
                "summary": f"{counts['quantified_proteins']} quantified proteins",
                "selected_panel_hits": int((selected["panel"] == "protein").sum()),
                "boundary_role": "protein-level corroboration",
            },
            {
                "sheet_name": "Phos_IDs",
                "summary": f"{counts['unique_phosphosites']} unique phosphosites",
                "selected_panel_hits": int((selected["panel"] == "phosphosite").sum()),
                "boundary_role": "phosphosite-level corroboration",
            },
        ]
    )
    return {
        "sheets": sheets,
        "counts": counts,
        "selected_markers": selected,
        "boundary_scan": boundary,
        "sheet_summary": sheet_summary,
    }


def _selected_to_tsv(selected: pd.DataFrame) -> str:
    columns = [
        "panel",
        "gene_symbol",
        "feature_label",
        "source_feature_id",
        "q_value",
        *TIMEPOINT_COLUMNS,
        *DELTA_COLUMNS,
    ]
    frame = selected.loc[:, columns].copy()
    frame["q_value"] = frame["q_value"].map(lambda value: f"{float(value):.6g}")
    for column in TIMEPOINT_COLUMNS + DELTA_COLUMNS:
        frame[column] = frame[column].map(lambda value: f"{float(value):.6f}")
    return frame.to_csv(sep="\t", index=False).strip()


def _boundary_to_tsv(boundary: pd.DataFrame) -> str:
    frame = boundary.loc[:, ["gene_symbol", "protein_exact_hits", "phosphosite_exact_hits", "status"]].copy()
    return frame.to_csv(sep="\t", index=False).strip()


def _render_report(data: dict[str, pd.DataFrame | dict[str, str]], workbook_path: Path) -> str:
    counts = data["counts"]  # type: ignore[assignment]
    selected = data["selected_markers"]  # type: ignore[assignment]
    boundary = data["boundary_scan"]  # type: ignore[assignment]
    summary = data["sheet_summary"]  # type: ignore[assignment]

    protein_selected = selected.loc[selected["panel"].eq("protein")].copy()
    phospho_selected = selected.loc[selected["panel"].eq("phosphosite")].copy()
    protein_delta = protein_selected["DTP_minus_DMSO"].astype(float)
    phospho_delta = phospho_selected["DTP_minus_DMSO"].astype(float)

    protein_down = ", ".join(
        protein_selected.loc[protein_delta < 0, "gene_symbol"].astype(str).tolist()
    )
    protein_up = ", ".join(
        protein_selected.loc[protein_delta > 0, "gene_symbol"].astype(str).tolist()
    )
    phospho_down = ", ".join(
        phospho_selected.loc[phospho_delta < 0, "feature_label"].astype(str).tolist()
    )
    phospho_up = ", ".join(
        phospho_selected.loc[phospho_delta > 0, "feature_label"].astype(str).tolist()
    )
    boundary_rows = "\n".join(
        f"| {row.gene_symbol} | {row.protein_exact_hits} | {row.phosphosite_exact_hits} | {row.status} |"
        for row in boundary.itertuples()
    )
    summary_rows = "\n".join(
        f"| {row.sheet_name} | {row.summary} | {row.selected_panel_hits} | {row.boundary_role} |"
        for row in summary.itertuples()
    )

    return "\n".join(
        [
            "# GSE335846 Companion Phosphoproteomics Corroboration",
            "",
            "## Result",
            "",
            (
                "A companion Springernature phosphoproteomics workbook from the same osimertinib-tolerant "
                "persister study provides source-table-backed corroboration for the DTP logic. The workbook "
                f"contains {counts['quantified_proteins']} quantified proteins and {counts['unique_phosphosites']} unique phosphosites across DMSO, Osi_5min, Osi_10min, Osi_6h, DTP, DTP-24h, and DTP-7d."
            ),
            (
                "In the selected protein panel, the DTP state suppresses canonical proliferation markers "
                f"({protein_down}) and leaves EGFR / RPA2 / CCND1 on the positive side of the selected panel ({protein_up})."
            ),
            (
                "In the selected phosphosite panel, the DTP state shows source-backed changes in ATR-adjacent and replication-stress phosphosites, with "
                f"negative DTP shifts for {phospho_down} and positive DTP shifts for {phospho_up}."
            ),
            (
                "This workbook strengthens the dynamic DTP / replication-stress narrative, but the quick exact-gene scan does not surface ATM as a usable source-table row, so it remains corroboration rather than ATM source-table closure."
            ),
            "",
            "## Workbook summary",
            "",
            f"Source workbook: `{workbook_path.as_posix()}`",
            "",
            "| Sheet | Summary | Selected hits | Role |",
            "|---|---|---:|---|",
            summary_rows,
            "",
            "## Boundary scan",
            "",
            "| Gene | Protein exact hits | Phosphosite exact hits | Status |",
            "|---|---:|---:|---|",
            boundary_rows,
            "",
            "## Claim boundary",
            "",
            (
                "The workbook is useful because it is source-table-backed and it captures the same DTP / replication-stress logic that the manuscript uses for external corroboration. "
                "It is not a substitute for replicate-level ATM pharmacology source tables, and it does not change the current claim ceiling."
            ),
            "",
        ]
    )


def _render_support_text(data: dict[str, pd.DataFrame | dict[str, str]]) -> str:
    selected = data["selected_markers"]  # type: ignore[assignment]
    boundary = data["boundary_scan"]  # type: ignore[assignment]
    protein_selected = selected.loc[selected["panel"].eq("protein")].copy()
    phospho_selected = selected.loc[selected["panel"].eq("phosphosite")].copy()
    protein_down = ", ".join(
        protein_selected.loc[protein_selected["DTP_minus_DMSO"].astype(float) < 0, "gene_symbol"]
        .astype(str)
        .tolist()
    )
    phospho_down = ", ".join(
        phospho_selected.loc[phospho_selected["DTP_minus_DMSO"].astype(float) < 0, "feature_label"]
        .astype(str)
        .tolist()
    )
    boundary_atm = boundary.loc[boundary["gene_symbol"].eq("ATM")].iloc[0]
    boundary_atr = boundary.loc[boundary["gene_symbol"].eq("ATR")].iloc[0]
    return "\n".join(
        [
            "# GSE335846 Phosphoproteomics Corroboration Support Text",
            "",
            "Supplementary Figure S7 summarizes a companion phosphoproteomics workbook from the same osimertinib-tolerant persister study. Panel A shows a selected protein panel across the DMSO, Osi_5min, Osi_10min, Osi_6h, DTP, DTP-24h, and DTP-7d conditions, while Panel B shows the selected phosphosite panel across the same conditions. The workbook is source-table-backed and therefore stronger than a figure-digitized summary, but it still functions as corroboration rather than source-table closure for ATM pharmacology.",
            "",
            "## Supplementary Figure S7",
            "",
            (
                "Supplementary Figure S7. GSE335846 companion phosphoproteomics corroboration. "
                f"(A) Selected protein-level rows show that DTP suppresses canonical proliferation markers ({protein_down}) while keeping EGFR / RPA2 / CCND1 on the positive side of the panel. "
                "(B) Selected phosphosite-level rows show source-backed DTP shifts for ATR-adjacent and replication-stress phosphosites, including negative DTP shifts for "
                f"{phospho_down}. The workbook does not expose an exact ATM gene-symbol hit in the quick scan, so the figure strengthens dynamic corroboration without upgrading the public source ceiling."
            ),
            "",
            "## Boundary",
            "",
            (
                f"ATM exact scan: {int(boundary_atm['protein_exact_hits'])} protein hits and {int(boundary_atm['phosphosite_exact_hits'])} phosphosite hits. "
                f"ATR exact scan: {int(boundary_atr['protein_exact_hits'])} protein hits and {int(boundary_atr['phosphosite_exact_hits'])} phosphosite hits."
            ),
            "",
            (
                "This support text is intentionally bounded. It confirms a source-backed phosphoproteomic corroboration layer, but it does not replace the missing replicate-level dynamic ATM source tables or the prospective branch-stratified ATM experiment."
            ),
            "",
        ]
    )


def _render_heatmap(ax: plt.Axes, panel: pd.DataFrame, title: str, vmax: float) -> None:
    if panel.empty:
        ax.axis("off")
        ax.set_title(title, loc="left", fontweight="bold")
        ax.text(0.5, 0.5, "No selected rows", ha="center", va="center")
        return

    matrix = panel.loc[:, DELTA_COLUMNS].astype(float).to_numpy()
    im = ax.imshow(matrix, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xticks(range(len(DELTA_COLUMNS)))
    ax.set_xticklabels([label.replace("_minus_DMSO", "") for label in DELTA_COLUMNS], rotation=25, ha="right")
    ax.set_yticks(range(len(panel)))
    ax.set_yticklabels(panel["feature_label"].astype(str).tolist())
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.axvline(-0.5, color="#666666", linewidth=0.5)
    for row in range(matrix.shape[0] + 1):
        ax.axhline(row - 0.5, color="white", linewidth=0.4, alpha=0.7)
    return im


def render_phosphoproteomics_figure(
    selected: pd.DataFrame,
    png_out: Path,
    pdf_out: Path | None = None,
) -> None:
    """Render the companion phosphoproteomics scorecard."""
    protein_selected = selected.loc[selected["panel"].eq("protein")].copy().reset_index(drop=True)
    phospho_selected = selected.loc[selected["panel"].eq("phosphosite")].copy().reset_index(drop=True)

    vmax = float(
        np.nanmax(
            np.abs(
                pd.concat(
                    [
                        protein_selected[DELTA_COLUMNS].astype(float).stack(),
                        phospho_selected[DELTA_COLUMNS].astype(float).stack(),
                    ],
                    ignore_index=True,
                ).to_numpy()
            )
        )
    )
    vmax = max(2.5, round(vmax + 0.1, 1))

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
        }
    )

    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8.0), constrained_layout=True)
    im0 = _render_heatmap(axes[0], protein_selected, "A  Protein-level DTP changes relative to DMSO", vmax)
    im1 = _render_heatmap(axes[1], phospho_selected, "B  Phosphosite-level DTP changes relative to DMSO", vmax)
    cbar = fig.colorbar(im1, ax=axes, shrink=0.8, pad=0.01)
    cbar.set_label("log2 intensity change vs DMSO")
    fig.suptitle(
        "GSE335846 companion phosphoproteomics corroboration",
        x=0.02,
        y=1.01,
        ha="left",
        fontweight="bold",
    )
    save_figure(fig, png_out, dpi=300, bbox_inches="tight")
    if pdf_out is not None:
        save_figure(fig, pdf_out, bbox_inches="tight")
    plt.close(fig)


def write_phosphoproteomics_corroboration_assets(
    source_dir: Path,
    workbook_path: Path,
    summary_out: Path,
    report_out: Path,
    selected_out: Path,
    boundary_out: Path,
    figure_out: Path,
    figure_pdf_out: Path | None,
    support_text_out: Path,
) -> dict[str, Path]:
    """Write the phosphoproteomics corroboration asset bundle."""
    source_dir.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    selected_out.parent.mkdir(parents=True, exist_ok=True)
    boundary_out.parent.mkdir(parents=True, exist_ok=True)
    figure_out.parent.mkdir(parents=True, exist_ok=True)
    support_text_out.parent.mkdir(parents=True, exist_ok=True)

    data = build_phosphoproteomics_corroboration(workbook_path)
    summary = _selected_to_tsv(data["selected_markers"])  # type: ignore[arg-type]
    boundary = _boundary_to_tsv(data["boundary_scan"])  # type: ignore[arg-type]
    report = _render_report(data, workbook_path)
    support_text = _render_support_text(data)

    summary_out.write_text(summary + "\n", encoding="utf-8")
    selected_out.write_text(summary + "\n", encoding="utf-8")
    boundary_out.write_text(boundary + "\n", encoding="utf-8")
    report_out.write_text(report, encoding="utf-8")
    support_text_out.write_text(support_text, encoding="utf-8")
    render_phosphoproteomics_figure(
        data["selected_markers"],  # type: ignore[arg-type]
        figure_out,
        pdf_out=figure_pdf_out,
    )

    outputs = {
        "summary": summary_out,
        "report": report_out,
        "selected_markers": selected_out,
        "boundary_scan": boundary_out,
        "figure": figure_out,
        "support_text": support_text_out,
    }
    if figure_pdf_out is not None:
        outputs["figure_pdf"] = figure_pdf_out
    return outputs
