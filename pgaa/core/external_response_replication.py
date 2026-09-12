"""Held-out-batch replication benchmark for non-target response rankings."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import hypergeom, spearmanr, wilcoxon
from statsmodels.stats.multitest import multipletests

from pgaa.core.prt import wasserstein_1d_by_column
from pgaa.core.prt_s2 import s2_test


METHODS = ("pgaa_w", "pgaa_h", "absolute_mean_shift", "welch_abs_t")


def deterministic_batch_split(
    batches: pd.Series, seed: str = "pgaa-response-replication-v1"
) -> dict[str, str]:
    """Assign unique batches to balanced discovery and validation halves."""
    unique = sorted(set(batches.astype(str)))
    if len(unique) < 2:
        raise ValueError("at least two batches are required for held-out replication")
    ordered = sorted(
        unique,
        key=lambda batch: hashlib.sha256(
            f"{seed}\0{batch}".encode("utf-8", errors="replace")
        ).hexdigest(),
    )
    midpoint = len(ordered) // 2
    return {
        batch: ("discovery" if index < midpoint else "validation")
        for index, batch in enumerate(ordered)
    }


def _score_methods(
    X: np.ndarray,
    genes: list[str],
    target: str,
    perturbed_idx: np.ndarray,
    control_idx: np.ndarray,
    n_bins: int,
) -> dict[str, np.ndarray]:
    target_x = X[perturbed_idx]
    control_x = X[control_idx]
    delta = target_x.mean(axis=0) - control_x.mean(axis=0)
    variance = (
        target_x.var(axis=0, ddof=1) / len(target_x)
        + control_x.var(axis=0, ddof=1) / len(control_x)
    )
    welch = np.divide(
        np.abs(delta),
        np.sqrt(variance),
        out=np.zeros_like(delta, dtype=float),
        where=np.isfinite(variance) & (variance > 0),
    )
    h = s2_test(
        X,
        genes,
        target,
        perturbed_idx,
        control_idx,
        n_bins=n_bins,
        verbose=False,
    ).set_index("gene")["S2"].reindex(genes).to_numpy(dtype=float)
    return {
        "pgaa_w": wasserstein_1d_by_column(target_x, control_x),
        "pgaa_h": h,
        "absolute_mean_shift": np.abs(delta),
        "welch_abs_t": welch,
    }


def _replication_metrics(
    discovery: np.ndarray,
    validation: np.ndarray,
    genes: list[str],
    top_k: int,
) -> dict[str, float | int]:
    universe = len(genes)
    k = min(top_k, universe)
    order_d = np.lexsort((np.asarray(genes, dtype=str), -discovery))
    order_v = np.lexsort((np.asarray(genes, dtype=str), -validation))
    top_d = set(order_d[:k])
    top_v = set(order_v[:k])
    overlap = len(top_d & top_v)
    validation_rank = np.empty(universe, dtype=int)
    validation_rank[order_v] = np.arange(1, universe + 1)
    rho = spearmanr(discovery, validation).statistic
    return {
        "n_evaluated_genes": universe,
        "top_k": k,
        "top_k_overlap": overlap,
        "top_k_overlap_fraction": overlap / k,
        "top_k_jaccard": overlap / len(top_d | top_v),
        "hypergeom_p": float(hypergeom.sf(overlap - 1, universe, k, k)),
        "all_gene_spearman_rho": float(rho) if np.isfinite(rho) else np.nan,
        "median_validation_percentile_of_discovery_top_k": float(
            np.median(validation_rank[list(top_d)] / universe)
        ),
    }


def benchmark_response_replication(
    contract: pd.DataFrame,
    top_k: int = 100,
    n_bins: int = 20,
    split_seed: str = "pgaa-response-replication-v1",
    min_cells_per_group_per_split: int = 10,
    batch_universe: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Benchmark cross-batch replication for every locked target and method."""
    required = {"target_gene", "expression_csv", "metadata_csv"}
    missing = sorted(required - set(contract.columns))
    if missing:
        raise ValueError(f"contract is missing columns: {missing}")
    if top_k < 1:
        raise ValueError("top_k must be positive")
    locked_split_map = (
        deterministic_batch_split(pd.Series(list(batch_universe), dtype=str), split_seed)
        if batch_universe is not None
        else None
    )

    rows: list[dict[str, object]] = []
    for _, contract_row in contract.iterrows():
        target = str(contract_row["target_gene"])
        base = {
            "target_gene": target,
            "split_seed": split_seed,
            "analysis_role": "within_experiment_held_out_batch_replication",
        }
        try:
            expression = pd.read_csv(Path(str(contract_row["expression_csv"])), index_col=0)
            metadata = pd.read_csv(
                Path(str(contract_row["metadata_csv"])), dtype={"cell_id": str, "source_batch": str}
            ).set_index("cell_id")
            if "source_batch" not in metadata.columns:
                raise ValueError("metadata is missing source_batch")
            metadata = metadata.loc[expression.index.astype(str)]
            split_map = locked_split_map or deterministic_batch_split(
                metadata["source_batch"], split_seed
            )
            unknown_batches = sorted(set(metadata["source_batch"].astype(str)) - set(split_map))
            if unknown_batches:
                raise ValueError(f"metadata contains batches outside locked universe: {unknown_batches}")
            split = metadata["source_batch"].map(split_map)
            genes_all = expression.columns.astype(str).tolist()
            if target not in genes_all:
                raise ValueError("target gene is absent from expression")
            keep = np.asarray([gene != target for gene in genes_all])
            genes = [gene for gene in genes_all if gene != target]
            X = expression.to_numpy(dtype=float)
            split_scores: dict[str, dict[str, np.ndarray]] = {}
            split_counts: dict[str, tuple[int, int]] = {}
            for split_name in ("discovery", "validation"):
                perturbed = np.flatnonzero(
                    (split == split_name).to_numpy()
                    & metadata["group"].astype(str).eq("perturbed").to_numpy()
                )
                control = np.flatnonzero(
                    (split == split_name).to_numpy()
                    & metadata["group"].astype(str).eq("control").to_numpy()
                )
                split_counts[split_name] = (len(perturbed), len(control))
                if min(len(perturbed), len(control)) < min_cells_per_group_per_split:
                    raise ValueError(
                        f"{split_name} has {len(perturbed)} perturbed and {len(control)} controls"
                    )
                split_scores[split_name] = {
                    method: score[keep]
                    for method, score in _score_methods(
                        X, genes_all, target, perturbed, control, n_bins
                    ).items()
                }

            for method in METHODS:
                metrics = _replication_metrics(
                    split_scores["discovery"][method],
                    split_scores["validation"][method],
                    genes,
                    top_k,
                )
                rows.append(
                    {
                        **base,
                        "method": method,
                        "status": "complete",
                        "n_discovery_batches": sum(v == "discovery" for v in split_map.values()),
                        "n_validation_batches": sum(v == "validation" for v in split_map.values()),
                        "n_discovery_perturbed": split_counts["discovery"][0],
                        "n_discovery_control": split_counts["discovery"][1],
                        "n_validation_perturbed": split_counts["validation"][0],
                        "n_validation_control": split_counts["validation"][1],
                        **metrics,
                        "failure_reason": "",
                    }
                )
        except Exception as exc:
            for method in METHODS:
                rows.append(
                    {
                        **base,
                        "method": method,
                        "status": "failed",
                        "n_discovery_batches": np.nan,
                        "n_validation_batches": np.nan,
                        "n_discovery_perturbed": np.nan,
                        "n_discovery_control": np.nan,
                        "n_validation_perturbed": np.nan,
                        "n_validation_control": np.nan,
                        "n_evaluated_genes": np.nan,
                        "top_k": min(top_k, 0),
                        "top_k_overlap": np.nan,
                        "top_k_overlap_fraction": np.nan,
                        "top_k_jaccard": np.nan,
                        "hypergeom_p": np.nan,
                        "all_gene_spearman_rho": np.nan,
                        "median_validation_percentile_of_discovery_top_k": np.nan,
                        "failure_reason": f"{type(exc).__name__}: {exc}",
                    }
                )

    result = pd.DataFrame(rows)
    result["hypergeom_q_bh"] = np.nan
    for method in METHODS:
        complete = result["status"].eq("complete") & result["method"].eq(method)
        if complete.any():
            result.loc[complete, "hypergeom_q_bh"] = multipletests(
                result.loc[complete, "hypergeom_p"].astype(float), method="fdr_bh"
            )[1]
    return result


def summarize_response_replication(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize methods and paired PGAA-vs-baseline overlap comparisons."""
    locked_targets = results["target_gene"].nunique()
    rows: list[dict[str, object]] = []
    for method in METHODS:
        current = results[(results["method"] == method) & (results["status"] == "complete")]
        rows.append(
            {
                "method": method,
                "n_complete_targets": current["target_gene"].nunique(),
                "n_locked_targets": locked_targets,
                "median_top_k_overlap_fraction": current["top_k_overlap_fraction"].median(),
                "median_top_k_jaccard": current["top_k_jaccard"].median(),
                "median_all_gene_spearman_rho": current["all_gene_spearman_rho"].median(),
                "n_hypergeom_fdr_le_0_05": int((current["hypergeom_q_bh"] <= 0.05).sum()),
            }
        )
    return pd.DataFrame(rows)


def paired_response_replication_comparisons(results: pd.DataFrame) -> pd.DataFrame:
    """Run four predeclared paired overlap comparisons with Holm correction."""
    complete = results[results["status"] == "complete"].pivot(
        index="target_gene", columns="method", values="top_k_overlap_fraction"
    ).reindex(columns=list(METHODS))
    rows: list[dict[str, object]] = []
    for pgaa_method in ("pgaa_w", "pgaa_h"):
        for baseline in ("absolute_mean_shift", "welch_abs_t"):
            paired = complete[[pgaa_method, baseline]].dropna()
            delta = paired[pgaa_method] - paired[baseline]
            try:
                p_value = float(wilcoxon(delta, alternative="greater").pvalue)
            except ValueError:
                p_value = 1.0
            rows.append(
                {
                    "pgaa_method": pgaa_method,
                    "baseline_method": baseline,
                    "n_paired_targets": len(paired),
                    "median_overlap_fraction_difference": delta.median(),
                    "wilcoxon_one_sided_p": p_value,
                }
            )
    comparison = pd.DataFrame(rows)
    comparison["holm_adjusted_p"] = multipletests(
        comparison["wilcoxon_one_sided_p"], method="holm"
    )[1]
    return comparison


def render_response_replication_report(
    results: pd.DataFrame, summary: pd.DataFrame, comparisons: pd.DataFrame
) -> str:
    """Render a claim-bounded report for the held-out-batch benchmark."""
    lines = [
        "# Replogle Essential Held-out-batch Response Replication",
        "",
        "This locked benchmark asks whether non-target response-gene rankings replicate across a deterministic discovery/validation split of experimental batches. The directly perturbed gene is excluded. It measures within-experiment reproducibility, not independent biological replication or biological correctness.",
        "",
        "## Method Summary",
        "",
        "| Method | Complete / locked | Median top-k overlap | Median Jaccard | Median Spearman | FDR-significant targets |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['method']}` | {int(row['n_complete_targets'])}/{int(row['n_locked_targets'])} | "
            f"{row['median_top_k_overlap_fraction']:.3f} | {row['median_top_k_jaccard']:.3f} | "
            f"{row['median_all_gene_spearman_rho']:.3f} | {int(row['n_hypergeom_fdr_le_0_05'])} |"
        )
    lines.extend(
        [
            "",
            "## Predeclared Paired Comparisons",
            "",
            "| PGAA method | Baseline | Paired targets | Median difference | One-sided Wilcoxon p | Holm p |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in comparisons.iterrows():
        lines.append(
            f"| `{row['pgaa_method']}` | `{row['baseline_method']}` | {int(row['n_paired_targets'])} | "
            f"{row['median_overlap_fraction_difference']:.3f} | {row['wilcoxon_one_sided_p']:.4g} | "
            f"{row['holm_adjusted_p']:.4g} |"
        )
    failures = results[results["status"] != "complete"]
    lines.extend(
        [
            "",
            "## Failure Accounting",
            "",
            f"{failures['target_gene'].nunique()} of {results['target_gene'].nunique()} locked targets failed at least one method. Failures remain in the locked denominator.",
            "",
            "## Interpretation Boundary",
            "",
            "Greater held-out overlap would support incremental ranking stability, but would not establish that the recovered genes are true biological effectors. A tie or loss against simple summaries is evidence against a PGAA-specific stability advantage in this experiment.",
            "",
        ]
    )
    return "\n".join(lines)
