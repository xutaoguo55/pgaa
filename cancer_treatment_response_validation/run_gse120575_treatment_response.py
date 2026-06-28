#!/usr/bin/env python3
"""GSE120575 melanoma checkpoint-immunotherapy response validation.

This script performs a bounded, patient-outcome-facing validation for PGAA:
baseline/pre-treatment single cells are grouped by clinical response
(Responder vs Non-responder), and genes are ranked by a 99-point Wasserstein
quantile-grid statistic. The analysis is deliberately framed as treatment-
response marker prioritization, not causal discovery or a predictive model.
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

META = RAW / "GSE120575_patient_ID_single_cells.txt.gz"
EXPR = RAW / "GSE120575_Sade_Feldman_melanoma_single_cells_TPM_GEO.txt.gz"

RESPONSE_MARKERS = {
    # Memory / progenitor-like T-cell states and immune activation markers
    # reported or commonly used in checkpoint-response melanoma scRNA-seq.
    "TCF7",
    "CCR7",
    "SELL",
    "LTB",
    "IL7R",
    "LEF1",
    "CD27",
    "CD28",
    "BCL2",
    # Dysfunction/exhaustion/cytotoxic response-state markers.
    "ENTPD1",
    "HAVCR2",
    "PDCD1",
    "LAG3",
    "TIGIT",
    "CXCL13",
    "IFNG",
    "GZMB",
    "PRF1",
    "NKG7",
    "GNLY",
    "GZMK",
    "CCL3",
    "CCL4",
    "CD38",
    "WARS",
}


def read_geo_metadata() -> pd.DataFrame:
    with gzip.open(META, "rt", errors="ignore", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = None
        for row in reader:
            if row and row[0] == "Sample name":
                header = row
                break
        if header is None:
            raise RuntimeError("Could not find GEO sample metadata header")
        rows = []
        for row in reader:
            if not row or not row[0].startswith("Sample "):
                continue
            row = row + [""] * (len(header) - len(row))
            rows.append(dict(zip(header, row)))
    df = pd.DataFrame(rows)
    df = df.rename(
        columns={
            "title": "cell_id",
            "characteristics: patinet ID (Pre=baseline; Post= on treatment)": "patient_time",
            "characteristics: response": "response",
            "characteristics: therapy": "therapy",
        }
    )
    df["timepoint"] = np.where(df["patient_time"].str.startswith("Pre_"), "Pre", "Post")
    df["patient_id"] = df["patient_time"].str.replace(r"^(Pre|Post)_", "", regex=True)
    return df[["cell_id", "patient_time", "patient_id", "timepoint", "response", "therapy"]]


def load_expression_header() -> tuple[list[str], list[str]]:
    with gzip.open(EXPR, "rt", errors="ignore") as f:
        cells = f.readline().rstrip("\n").split("\t")[1:]
        patient_time = f.readline().rstrip("\n").split("\t")[1:]
    return cells, patient_time


def pgaa_wasserstein(x1: np.ndarray, x0: np.ndarray) -> float:
    grid = np.arange(1, 100, dtype=float) / 100.0
    q1 = np.quantile(x1, grid)
    q0 = np.quantile(x0, grid)
    return float(np.mean(np.abs(q1 - q0)))


def analyze_subset(label: str, meta: pd.DataFrame, cells: list[str]) -> pd.DataFrame:
    cell_to_meta = meta.set_index("cell_id")
    selected = []
    responses = []
    patient_ids = []
    therapies = []
    for i, cell in enumerate(cells):
        if cell not in cell_to_meta.index:
            continue
        row = cell_to_meta.loc[cell]
        if label == "baseline" and row["timepoint"] != "Pre":
            continue
        if row["response"] not in {"Responder", "Non-responder"}:
            continue
        selected.append(i)
        responses.append(row["response"])
        patient_ids.append(row["patient_id"])
        therapies.append(row["therapy"])

    selected = np.array(selected, dtype=int)
    responses = np.array(responses)
    mask_r = responses == "Responder"
    mask_n = responses == "Non-responder"
    if mask_r.sum() < 50 or mask_n.sum() < 50:
        raise RuntimeError(f"Subset {label} has too few cells")

    summary = {
        "subset": label,
        "n_cells": int(len(selected)),
        "n_responder_cells": int(mask_r.sum()),
        "n_nonresponder_cells": int(mask_n.sum()),
        "n_patients": int(len(set(patient_ids))),
        "n_responder_patients": int(len({p for p, r in zip(patient_ids, responses) if r == "Responder"})),
        "n_nonresponder_patients": int(len({p for p, r in zip(patient_ids, responses) if r == "Non-responder"})),
        "therapies": ";".join(sorted(set(therapies))),
    }

    rows = []
    with gzip.open(EXPR, "rt", errors="ignore") as f:
        next(f)
        next(f)
        for line_no, line in enumerate(f, start=1):
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) != 2:
                continue
            gene = parts[0].strip()
            if not gene:
                continue
            values = np.fromstring(parts[1], sep="\t", dtype=np.float32)
            if values.shape[0] < len(cells):
                continue
            v = values[selected]
            expressed = int((v > 0).sum())
            if expressed < max(20, int(0.005 * len(v))):
                continue
            xr = v[mask_r]
            xn = v[mask_n]
            s1 = pgaa_wasserstein(xr, xn)
            mean_r = float(np.mean(xr))
            mean_n = float(np.mean(xn))
            tt = ttest_ind(xr, xn, equal_var=False, nan_policy="omit")
            rows.append(
                {
                    "gene": gene,
                    "s1_wasserstein": s1,
                    "mean_responder": mean_r,
                    "mean_nonresponder": mean_n,
                    "signed_mean_diff": mean_r - mean_n,
                    "abs_mean_diff": abs(mean_r - mean_n),
                    "t_abs": abs(float(tt.statistic)) if np.isfinite(tt.statistic) else np.nan,
                    "t_pvalue": float(tt.pvalue) if np.isfinite(tt.pvalue) else np.nan,
                    "expressed_cells": expressed,
                    "is_response_marker": gene in RESPONSE_MARKERS,
                }
            )

    out = pd.DataFrame(rows)
    out = out.dropna(subset=["s1_wasserstein"])
    for col in ["s1_wasserstein", "abs_mean_diff", "t_abs"]:
        out[f"rank_{col}"] = out[col].rank(ascending=False, method="min").astype(int)
    out["subset"] = label

    y = out["is_response_marker"].astype(int).to_numpy()
    metrics = dict(summary)
    metrics["n_genes_tested"] = int(out.shape[0])
    metrics["n_marker_genes_present"] = int(y.sum())
    metrics["random_auprc_baseline"] = float(y.mean())
    for col in ["s1_wasserstein", "abs_mean_diff", "t_abs"]:
        scores = out[col].fillna(out[col].min()).to_numpy()
        metrics[f"{col}_auroc"] = float(roc_auc_score(y, scores)) if y.sum() > 1 else np.nan
        metrics[f"{col}_auprc"] = float(average_precision_score(y, scores)) if y.sum() > 1 else np.nan
        for k in [50, 100, 250, 500]:
            top = out.nlargest(k, col)
            obs = int(top["is_response_marker"].sum())
            exp = k * y.mean()
            metrics[f"{col}_top{k}_markers"] = obs
            metrics[f"{col}_top{k}_enrichment"] = float(obs / exp) if exp > 0 else np.nan

    out.to_csv(RESULTS / f"gse120575_{label}_gene_scores.csv", index=False)
    pd.DataFrame([metrics]).to_csv(RESULTS / f"gse120575_{label}_summary.csv", index=False)
    return out


def plot_results(baseline: pd.DataFrame, allcells: pd.DataFrame) -> None:
    marker_ranks = []
    for label, df in [("Baseline", baseline), ("All cells", allcells)]:
        present = df[df["is_response_marker"]].copy()
        present["analysis"] = label
        marker_ranks.append(present)
    markers = pd.concat(marker_ranks, ignore_index=True)
    markers.to_csv(RESULTS / "gse120575_response_marker_ranks.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.2), dpi=300)
    for ax, (label, df) in zip(axes, [("Baseline", baseline), ("All cells", allcells)]):
        top = df.nsmallest(20, "rank_s1_wasserstein").copy()
        colors = ["#0072B2" if x else "#BDBDBD" for x in top["is_response_marker"]]
        ax.barh(np.arange(len(top)), top["s1_wasserstein"], color=colors)
        ax.set_yticks(np.arange(len(top)))
        ax.set_yticklabels(top["gene"], fontsize=6)
        ax.invert_yaxis()
        ax.set_xlabel("S1 Wasserstein", fontsize=8)
        ax.set_title(label, fontsize=9, weight="bold")
        ax.tick_params(axis="x", labelsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "gse120575_top_s1_genes.png", bbox_inches="tight")
    fig.savefig(FIGURES / "gse120575_top_s1_genes.pdf", bbox_inches="tight")
    plt.close(fig)

    top_markers = markers.nsmallest(20, "rank_s1_wasserstein")
    fig, ax = plt.subplots(figsize=(5.4, 3.4), dpi=300)
    for label, grp in top_markers.groupby("analysis"):
        ax.scatter(grp["rank_s1_wasserstein"], grp["gene"], label=label, s=24)
    ax.set_xscale("log")
    ax.set_xlabel("S1 rank among tested genes", fontsize=8)
    ax.set_ylabel("")
    ax.tick_params(labelsize=7)
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "gse120575_response_marker_ranks.png", bbox_inches="tight")
    fig.savefig(FIGURES / "gse120575_response_marker_ranks.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    meta = read_geo_metadata()
    cells, patient_time = load_expression_header()
    meta.to_csv(RESULTS / "gse120575_cell_metadata_parsed.csv", index=False)

    expr_meta = pd.DataFrame({"cell_id": cells, "expr_patient_time": patient_time})
    expr_meta.to_csv(RESULTS / "gse120575_expression_header_metadata.csv", index=False)
    merged = expr_meta.merge(meta, on="cell_id", how="left")
    if merged["response"].isna().any():
        raise RuntimeError("Expression header and GEO metadata are not fully aligned")

    baseline = analyze_subset("baseline", meta, cells)
    allcells = analyze_subset("all_cells", meta, cells)
    plot_results(baseline, allcells)


if __name__ == "__main__":
    main()
