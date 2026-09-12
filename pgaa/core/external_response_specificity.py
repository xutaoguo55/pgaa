"""Matched control-vs-control stress test for response-ranking stability."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

from pgaa.core.external_response_replication import (
    METHODS,
    _replication_metrics,
    _score_methods,
    deterministic_batch_split,
)


def _ordered_indices(indices: np.ndarray, cell_ids: pd.Index, seed: str) -> np.ndarray:
    return np.asarray(
        sorted(
            indices,
            key=lambda index: hashlib.sha256(
                f"{seed}\0{cell_ids[index]}".encode("utf-8", errors="replace")
            ).hexdigest(),
        ),
        dtype=int,
    )


def benchmark_response_specificity(
    contract: pd.DataFrame,
    top_k: int = 100,
    n_bins: int = 20,
    n_repeats: int = 5,
    split_seed: str = "pgaa-response-replication-v1",
    pseudo_seed: str = "pgaa-response-specificity-v1",
    min_target_cells_per_split: int = 10,
) -> pd.DataFrame:
    """Compare observed response stability with matched pseudo-perturbation stability."""
    if n_repeats < 1:
        raise ValueError("n_repeats must be positive")
    split_map = deterministic_batch_split(
        pd.Series([str(batch) for batch in range(1, 49)]), split_seed
    )
    rows: list[dict[str, object]] = []
    for _, contract_row in contract.iterrows():
        target = str(contract_row["target_gene"])
        try:
            expression = pd.read_csv(Path(str(contract_row["expression_csv"])), index_col=0)
            metadata = pd.read_csv(
                Path(str(contract_row["metadata_csv"])),
                dtype={"cell_id": str, "source_batch": str},
            ).set_index("cell_id")
            metadata = metadata.loc[expression.index.astype(str)]
            split = metadata["source_batch"].map(split_map)
            if split.isna().any():
                raise ValueError("metadata contains a batch outside 1..48")
            genes_all = expression.columns.astype(str).tolist()
            if target not in genes_all:
                raise ValueError("target gene is absent from expression")
            keep = np.asarray([gene != target for gene in genes_all])
            genes = [gene for gene in genes_all if gene != target]
            X = expression.to_numpy(dtype=float)
            cell_ids = metadata.index

            for repeat in range(n_repeats):
                observed_scores: dict[str, dict[str, np.ndarray]] = {}
                pseudo_scores: dict[str, dict[str, np.ndarray]] = {}
                split_sizes: dict[str, int] = {}
                for split_name in ("discovery", "validation"):
                    target_idx = np.flatnonzero(
                        (split == split_name).to_numpy()
                        & metadata["group"].astype(str).eq("perturbed").to_numpy()
                    )
                    control_idx = np.flatnonzero(
                        (split == split_name).to_numpy()
                        & metadata["group"].astype(str).eq("control").to_numpy()
                    )
                    n_target = len(target_idx)
                    if n_target < min_target_cells_per_split:
                        raise ValueError(f"{split_name} has only {n_target} target cells")
                    if len(control_idx) < 2 * n_target:
                        raise ValueError(
                            f"{split_name} needs {2 * n_target} matched controls but has {len(control_idx)}"
                        )
                    ordered = _ordered_indices(
                        control_idx,
                        cell_ids,
                        f"{pseudo_seed}:repeat={repeat}:split={split_name}",
                    )
                    pseudo_target = ordered[:n_target]
                    matched_control = ordered[n_target : 2 * n_target]
                    split_sizes[split_name] = n_target
                    observed_scores[split_name] = {
                        method: score[keep]
                        for method, score in _score_methods(
                            X, genes_all, target, target_idx, matched_control, n_bins
                        ).items()
                    }
                    pseudo_scores[split_name] = {
                        method: score[keep]
                        for method, score in _score_methods(
                            X, genes_all, target, pseudo_target, matched_control, n_bins
                        ).items()
                    }

                for method in METHODS:
                    observed = _replication_metrics(
                        observed_scores["discovery"][method],
                        observed_scores["validation"][method],
                        genes,
                        top_k,
                    )
                    pseudo = _replication_metrics(
                        pseudo_scores["discovery"][method],
                        pseudo_scores["validation"][method],
                        genes,
                        top_k,
                    )
                    rows.append(
                        {
                            "target_gene": target,
                            "method": method,
                            "repeat": repeat,
                            "status": "complete",
                            "n_discovery_per_group": split_sizes["discovery"],
                            "n_validation_per_group": split_sizes["validation"],
                            "observed_top_k_overlap_fraction": observed["top_k_overlap_fraction"],
                            "pseudo_top_k_overlap_fraction": pseudo["top_k_overlap_fraction"],
                            "specificity_margin": observed["top_k_overlap_fraction"]
                            - pseudo["top_k_overlap_fraction"],
                            "observed_all_gene_spearman_rho": observed["all_gene_spearman_rho"],
                            "pseudo_all_gene_spearman_rho": pseudo["all_gene_spearman_rho"],
                            "analysis_role": "post_result_matched_control_specificity_stress_test",
                            "failure_reason": "",
                        }
                    )
        except Exception as exc:
            for repeat in range(n_repeats):
                for method in METHODS:
                    rows.append(
                        {
                            "target_gene": target,
                            "method": method,
                            "repeat": repeat,
                            "status": "failed",
                            "analysis_role": "post_result_matched_control_specificity_stress_test",
                            "failure_reason": f"{type(exc).__name__}: {exc}",
                        }
                    )
    return pd.DataFrame(rows)


def summarize_response_specificity(
    results: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate repeats within targets, then test target-level specificity margins."""
    complete = results[results["status"] == "complete"]
    target_level = (
        complete.groupby(["target_gene", "method"], as_index=False)
        .agg(
            median_observed_top_k_overlap_fraction=(
                "observed_top_k_overlap_fraction",
                "median",
            ),
            median_pseudo_top_k_overlap_fraction=("pseudo_top_k_overlap_fraction", "median"),
            median_specificity_margin=("specificity_margin", "median"),
            median_observed_all_gene_spearman_rho=("observed_all_gene_spearman_rho", "median"),
            median_pseudo_all_gene_spearman_rho=("pseudo_all_gene_spearman_rho", "median"),
            n_repeats=("repeat", "nunique"),
        )
    )
    rows: list[dict[str, object]] = []
    for method in METHODS:
        current = target_level[target_level["method"] == method]
        try:
            p_value = float(
                wilcoxon(current["median_specificity_margin"], alternative="greater").pvalue
            )
        except ValueError:
            p_value = 1.0
        rows.append(
            {
                "method": method,
                "n_complete_targets": current["target_gene"].nunique(),
                "median_observed_top_k_overlap_fraction": current[
                    "median_observed_top_k_overlap_fraction"
                ].median(),
                "median_pseudo_top_k_overlap_fraction": current[
                    "median_pseudo_top_k_overlap_fraction"
                ].median(),
                "median_specificity_margin": current["median_specificity_margin"].median(),
                "n_targets_positive_margin": int((current["median_specificity_margin"] > 0).sum()),
                "wilcoxon_one_sided_p": p_value,
            }
        )
    summary = pd.DataFrame(rows)
    summary["holm_adjusted_p"] = multipletests(
        summary["wilcoxon_one_sided_p"], method="holm"
    )[1]
    return target_level, summary


def render_response_specificity_report(
    target_level: pd.DataFrame, summary: pd.DataFrame
) -> str:
    lines = [
        "# Matched Control Specificity Stress Test",
        "",
        "This post-result sensitivity analysis tests whether cross-batch ranking stability exceeds a control-vs-control pseudo-perturbation background. Within each batch half and repeat, the observed comparison and pseudo comparison use equal group sizes and share the same matched-control group.",
        "",
        "| Method | Complete targets | Observed overlap | Pseudo overlap | Specificity margin | Positive targets | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['method']}` | {int(row['n_complete_targets'])} | "
            f"{row['median_observed_top_k_overlap_fraction']:.3f} | "
            f"{row['median_pseudo_top_k_overlap_fraction']:.3f} | "
            f"{row['median_specificity_margin']:.3f} | "
            f"{int(row['n_targets_positive_margin'])} | {row['holm_adjusted_p']:.4g} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "A positive margin supports response-specific stability beyond gene-wise variability and abundance that can make null rankings reproducible. This diagnostic was specified after inspecting the primary split result, uses one experiment, and is sensitivity evidence rather than independent confirmation.",
            "",
        ]
    )
    return "\n".join(lines)
