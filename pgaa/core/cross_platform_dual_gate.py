"""Cross-platform response stability and pseudo-perturbation specificity benchmark."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

from pgaa.core.external_response_replication import (
    METHODS,
    _replication_metrics,
    _score_methods,
    deterministic_batch_split,
)


@dataclass(frozen=True)
class PlatformSpec:
    dataset_id: str
    platform: str
    path: Path
    adapter: str
    batch_column: str
    matrix_layer: str | None
    normalization: str
    split_strength: str
    obs_filters: tuple[tuple[str, str], ...] = ()
    obs_value_sets: tuple[tuple[str, tuple[str, ...]], ...] = ()
    analysis_unit_columns: tuple[str, ...] = ()
    control_stratum_columns: tuple[str, ...] = ()
    control_column: str = "perturbation"
    control_values: tuple[str, ...] = ("control",)
    excluded_feature_column: str | None = None


def _hash_order(indices: np.ndarray, cell_ids: pd.Index, seed: str) -> np.ndarray:
    return np.asarray(
        sorted(
            indices,
            key=lambda i: hashlib.sha256(
                f"{seed}\0{cell_ids[i]}".encode("utf-8", errors="replace")
            ).hexdigest(),
        ),
        dtype=int,
    )


def _join_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    if not columns:
        return pd.Series("all", index=frame.index, dtype="string")
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"metadata is missing columns: {missing}")
    values = frame.loc[:, list(columns)].astype("string").fillna("missing")
    return values.agg("|".join, axis=1)


def adapt_platform_observations(
    obs: pd.DataFrame, adapter: str, spec: PlatformSpec | None = None
) -> pd.DataFrame:
    """Create a common perturbation-unit and matched-control schema."""
    out = obs.copy()
    if adapter in {"norman2019", "nadig2024"}:
        required = {"perturbation", "nperts"}
        missing = sorted(required - set(out.columns))
        if missing:
            raise ValueError(f"single-gene metadata is missing columns: {missing}")
        out["analysis_unit"] = out["perturbation"].astype(str)
        out["control_stratum"] = "all"
        out["excluded_feature"] = out["analysis_unit"]
        out["is_control"] = out["perturbation"].astype(str).eq("control")
        out["is_eligible_perturbation"] = (
            pd.to_numeric(out["nperts"], errors="coerce").eq(1) & ~out["is_control"]
        )
    elif adapter == "single_gene_nperts":
        required = {"perturbation", "nperts"}
        missing = sorted(required - set(out.columns))
        if missing:
            raise ValueError(f"single-gene metadata is missing columns: {missing}")
        nperts = pd.to_numeric(out["nperts"], errors="coerce")
        perturbation = out["perturbation"].astype("string")
        out["analysis_unit"] = perturbation.fillna("control").astype(str)
        out["control_stratum"] = "all"
        out["excluded_feature"] = perturbation.fillna("").astype(str)
        out["is_control"] = nperts.eq(0)
        out["is_eligible_perturbation"] = nperts.eq(1) & perturbation.notna()
    elif adapter == "datlinger2017":
        required = {"perturbation", "perturbation_2", "target"}
        missing = sorted(required - set(out.columns))
        if missing:
            raise ValueError(f"Datlinger metadata is missing columns: {missing}")
        target = out["target"].astype("string")
        stimulation = out["perturbation_2"].astype(str)
        out["analysis_unit"] = target.fillna("control") + "|" + stimulation
        out["control_stratum"] = stimulation
        out["excluded_feature"] = target.fillna("")
        out["is_control"] = out["perturbation"].astype(str).eq("control")
        out["is_eligible_perturbation"] = target.notna() & ~out["is_control"]
    elif adapter == "sciplex3":
        required = {"perturbation", "dose", "control"}
        missing = sorted(required - set(out.columns))
        if missing:
            raise ValueError(f"SciPlex metadata is missing columns: {missing}")
        out["analysis_unit"] = (
            out["perturbation"].astype(str) + "|dose=" + out["dose"].astype(str)
        )
        out["control_stratum"] = "all"
        out["excluded_feature"] = ""
        out["is_control"] = pd.to_numeric(out["control"], errors="coerce").eq(1)
        out["is_eligible_perturbation"] = ~out["is_control"]
    elif adapter == "generic_condition":
        if spec is None:
            raise ValueError("generic_condition adapter requires a platform spec")
        required = {
            spec.control_column,
            *spec.analysis_unit_columns,
            *spec.control_stratum_columns,
        }
        if spec.excluded_feature_column:
            required.add(spec.excluded_feature_column)
        missing = sorted(required - set(out.columns))
        if missing:
            raise ValueError(f"generic condition metadata is missing columns: {missing}")
        control_values = {str(value) for value in spec.control_values}
        control = out[spec.control_column].astype("string").isin(control_values)
        out["analysis_unit"] = _join_columns(out, spec.analysis_unit_columns)
        out["control_stratum"] = _join_columns(out, spec.control_stratum_columns)
        if spec.excluded_feature_column:
            out["excluded_feature"] = (
                out[spec.excluded_feature_column].astype("string").fillna("")
            )
        else:
            out["excluded_feature"] = ""
        out["is_control"] = control
        out["is_eligible_perturbation"] = ~control
    else:
        raise ValueError(f"unknown platform adapter: {adapter}")
    return out


def build_platform_unit_contract(
    obs: pd.DataFrame,
    spec: PlatformSpec,
    *,
    max_units: int = 16,
    max_cells_per_group: int = 70,
    min_cells_per_group: int = 20,
    split_seed: str = "pgaa-cross-platform-dual-gate-v1",
) -> tuple[pd.DataFrame, dict[str, str], pd.DataFrame]:
    """Select count-ranked units without inspecting expression results."""
    if spec.batch_column not in obs.columns:
        raise ValueError(f"metadata is missing batch column: {spec.batch_column}")
    if max_units < 1 or max_cells_per_group < min_cells_per_group:
        raise ValueError("invalid unit or cell-count limits")
    filtered = obs.copy()
    for column, expected in spec.obs_filters:
        if column not in filtered.columns:
            raise ValueError(f"metadata is missing filter column: {column}")
        filtered = filtered[filtered[column].astype(str).eq(expected)].copy()
    for column, allowed in spec.obs_value_sets:
        if column not in filtered.columns:
            raise ValueError(f"metadata is missing value-set filter column: {column}")
        filtered = filtered[filtered[column].astype(str).isin(set(allowed))].copy()
    if filtered.empty:
        raise ValueError("metadata filters removed every cell")
    adapted = adapt_platform_observations(filtered, spec.adapter, spec)
    split_map = deterministic_batch_split(
        adapted[spec.batch_column].astype(str), f"{split_seed}:{spec.dataset_id}"
    )
    adapted["analysis_split"] = adapted[spec.batch_column].astype(str).map(split_map)

    rows: list[dict[str, object]] = []
    eligible_units = sorted(
        adapted.loc[adapted["is_eligible_perturbation"], "analysis_unit"].unique()
    )
    for unit in eligible_units:
        unit_rows = adapted[adapted["analysis_unit"].eq(unit)]
        stratum = str(unit_rows["control_stratum"].iloc[0])
        excluded = str(unit_rows["excluded_feature"].iloc[0])
        counts: dict[str, int] = {}
        control_counts: dict[str, int] = {}
        for split in ("discovery", "validation"):
            counts[split] = int(unit_rows["analysis_split"].eq(split).sum())
            control_counts[split] = int(
                (
                    adapted["is_control"]
                    & adapted["control_stratum"].astype(str).eq(stratum)
                    & adapted["analysis_split"].eq(split)
                ).sum()
            )
        n_per_group = min(
            max_cells_per_group,
            counts["discovery"],
            counts["validation"],
            control_counts["discovery"] // 2,
            control_counts["validation"] // 2,
        )
        rows.append(
            {
                "dataset_id": spec.dataset_id,
                "platform": spec.platform,
                "analysis_unit": unit,
                "control_stratum": stratum,
                "excluded_feature": excluded,
                "n_discovery_perturbed_available": counts["discovery"],
                "n_validation_perturbed_available": counts["validation"],
                "n_discovery_controls_available": control_counts["discovery"],
                "n_validation_controls_available": control_counts["validation"],
                "n_per_group": n_per_group,
                "eligible": n_per_group >= min_cells_per_group,
                "selection_basis": "descending_minimum_equal_group_size_then_unit_id",
                "split_strength": spec.split_strength,
                "source_h5ad": str(spec.path),
            }
        )
    all_units = pd.DataFrame(rows)
    selected = (
        all_units[all_units["eligible"]]
        .sort_values(["n_per_group", "analysis_unit"], ascending=[False, True])
        .head(max_units)
        .copy()
        .reset_index(drop=True)
    )
    selected["selected_rank"] = np.arange(1, len(selected) + 1)
    return selected, split_map, adapted


def _select_gene_indices(
    adata: ad.AnnData, required_features: set[str], max_features: int
) -> np.ndarray:
    var = adata.var
    if "highly_variable_5000" in var.columns and var["highly_variable_5000"].fillna(False).any():
        ranked = np.flatnonzero(var["highly_variable_5000"].fillna(False).to_numpy(bool))
    elif "ncells" in var.columns:
        ranked = np.argsort(-pd.to_numeric(var["ncells"], errors="coerce").fillna(0).to_numpy())
    elif "n_cells" in var.columns:
        ranked = np.argsort(-pd.to_numeric(var["n_cells"], errors="coerce").fillna(0).to_numpy())
    else:
        ranked = np.arange(adata.n_vars)
    ranked = list(map(int, ranked[:max_features]))
    name_to_index = {str(name): i for i, name in enumerate(adata.var_names)}
    required = [name_to_index[name] for name in sorted(required_features) if name in name_to_index]
    selected = required + [i for i in ranked if i not in set(required)]
    return np.asarray(selected[:max_features], dtype=int)


def _load_expression(
    adata: ad.AnnData,
    row_indices: np.ndarray,
    gene_indices: np.ndarray,
    spec: PlatformSpec,
) -> np.ndarray:
    source = adata.layers[spec.matrix_layer] if spec.matrix_layer else adata.X
    try:
        view = adata[row_indices, gene_indices]
        matrix = view.layers[spec.matrix_layer] if spec.matrix_layer else view.X
    except TypeError as exc:
        if "one indexing vector" not in str(exc):
            raise
        # Backed dense HDF5 datasets permit only one fancy axis per read.
        matrix = np.asarray(source[row_indices, :])[:, gene_indices]
    if sparse.issparse(matrix):
        matrix = matrix.toarray()
    X = np.asarray(matrix, dtype=np.float32)
    if spec.normalization == "log1p_1e4":
        if "ncounts" in adata.obs.columns:
            totals = pd.to_numeric(adata.obs.iloc[row_indices]["ncounts"], errors="coerce").to_numpy()
        else:
            totals = X.sum(axis=1)
        scale = np.divide(1e4, totals, out=np.zeros_like(totals, dtype=float), where=totals > 0)
        X = np.log1p(X * scale[:, None]).astype(np.float32)
    elif spec.normalization != "precomputed_log":
        raise ValueError(f"unknown normalization: {spec.normalization}")
    return X


def benchmark_platform_dual_gate(
    spec: PlatformSpec,
    *,
    max_units: int = 16,
    max_cells_per_group: int = 70,
    min_cells_per_group: int = 20,
    max_features: int = 5000,
    top_k: int = 100,
    n_bins: int = 20,
    n_repeats: int = 5,
    split_seed: str = "pgaa-cross-platform-dual-gate-v1",
    sampling_seed: str = "pgaa-cross-platform-matched-controls-v1",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run a common matched observed-versus-pseudo benchmark on one platform."""
    adata = ad.read_h5ad(spec.path)
    contract, split_map, obs = build_platform_unit_contract(
        adata.obs,
        spec,
        max_units=max_units,
        max_cells_per_group=max_cells_per_group,
        min_cells_per_group=min_cells_per_group,
        split_seed=split_seed,
    )
    if contract.empty:
        raise ValueError("no perturbation unit passed the cell-count gate")
    required = set(contract["excluded_feature"].astype(str)) - {""}
    gene_indices = _select_gene_indices(adata, required, max_features)
    genes_all = adata.var_names[gene_indices].astype(str).tolist()
    cell_ids = obs.index
    result_rows: list[dict[str, object]] = []

    for _, unit_row in contract.iterrows():
        unit = str(unit_row["analysis_unit"])
        stratum = str(unit_row["control_stratum"])
        excluded = str(unit_row["excluded_feature"])
        n = int(unit_row["n_per_group"])
        samples: dict[tuple[int, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        used: set[int] = set()
        for repeat in range(n_repeats):
            for split in ("discovery", "validation"):
                target_pool = np.flatnonzero(
                    obs["analysis_unit"].eq(unit).to_numpy()
                    & obs["analysis_split"].eq(split).to_numpy()
                )
                control_pool = np.flatnonzero(
                    obs["is_control"].to_numpy()
                    & obs["control_stratum"].astype(str).eq(stratum).to_numpy()
                    & obs["analysis_split"].eq(split).to_numpy()
                )
                target_idx = _hash_order(
                    target_pool,
                    cell_ids,
                    f"{sampling_seed}:{spec.dataset_id}:{unit}:{repeat}:{split}:target",
                )[:n]
                ordered_controls = _hash_order(
                    control_pool,
                    cell_ids,
                    f"{sampling_seed}:{spec.dataset_id}:{unit}:{repeat}:{split}:control",
                )
                pseudo_idx = ordered_controls[:n]
                matched_idx = ordered_controls[n : 2 * n]
                if min(len(target_idx), len(pseudo_idx), len(matched_idx)) < n:
                    raise ValueError(f"insufficient sampled cells for {unit} {split}")
                samples[(repeat, split)] = (target_idx, pseudo_idx, matched_idx)
                used.update(map(int, target_idx))
                used.update(map(int, pseudo_idx))
                used.update(map(int, matched_idx))

        global_rows = np.asarray(sorted(used), dtype=int)
        X = _load_expression(adata, global_rows, gene_indices, spec)
        global_to_local = {global_i: local_i for local_i, global_i in enumerate(global_rows)}
        keep = np.asarray([gene != excluded for gene in genes_all], dtype=bool)
        genes = [gene for gene in genes_all if gene != excluded]
        score_target = excluded if excluded in genes_all else genes_all[0]

        for repeat in range(n_repeats):
            observed_scores: dict[str, dict[str, np.ndarray]] = {}
            pseudo_scores: dict[str, dict[str, np.ndarray]] = {}
            for split in ("discovery", "validation"):
                target_idx, pseudo_idx, matched_idx = samples[(repeat, split)]
                local_target = np.asarray([global_to_local[int(i)] for i in target_idx])
                local_pseudo = np.asarray([global_to_local[int(i)] for i in pseudo_idx])
                local_matched = np.asarray([global_to_local[int(i)] for i in matched_idx])
                observed_scores[split] = {
                    method: score[keep]
                    for method, score in _score_methods(
                        X, genes_all, score_target, local_target, local_matched, n_bins
                    ).items()
                }
                pseudo_scores[split] = {
                    method: score[keep]
                    for method, score in _score_methods(
                        X, genes_all, score_target, local_pseudo, local_matched, n_bins
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
                result_rows.append(
                    {
                        "dataset_id": spec.dataset_id,
                        "platform": spec.platform,
                        "split_strength": spec.split_strength,
                        "analysis_unit": unit,
                        "excluded_feature": excluded,
                        "repeat": repeat,
                        "method": method,
                        "n_per_group": n,
                        "n_evaluated_features": len(genes),
                        "observed_top_k_overlap_fraction": observed[
                            "top_k_overlap_fraction"
                        ],
                        "pseudo_top_k_overlap_fraction": pseudo[
                            "top_k_overlap_fraction"
                        ],
                        "specificity_margin": observed["top_k_overlap_fraction"]
                        - pseudo["top_k_overlap_fraction"],
                        "observed_all_feature_spearman": observed[
                            "all_gene_spearman_rho"
                        ],
                        "pseudo_all_feature_spearman": pseudo["all_gene_spearman_rho"],
                        "split_seed": split_seed,
                        "sampling_seed": sampling_seed,
                    }
                )
    return contract, pd.DataFrame(result_rows)


def summarize_platform_dual_gate(
    results: pd.DataFrame,
    *,
    stability_threshold: float = 0.20,
    alpha: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Summarize repeats, test target-level margins, and compile gate states."""
    target = (
        results.groupby(
            ["dataset_id", "platform", "split_strength", "analysis_unit", "method"],
            as_index=False,
        )
        .agg(
            median_observed_overlap=("observed_top_k_overlap_fraction", "median"),
            median_pseudo_overlap=("pseudo_top_k_overlap_fraction", "median"),
            median_specificity_margin=("specificity_margin", "median"),
            n_repeats=("repeat", "nunique"),
        )
    )
    method_rows: list[dict[str, object]] = []
    for (dataset_id, platform, strength, method), current in target.groupby(
        ["dataset_id", "platform", "split_strength", "method"], sort=True
    ):
        margins = current["median_specificity_margin"].to_numpy(float)
        try:
            p_value = float(wilcoxon(margins, alternative="greater").pvalue)
        except ValueError:
            p_value = 1.0
        method_rows.append(
            {
                "dataset_id": dataset_id,
                "platform": platform,
                "split_strength": strength,
                "method": method,
                "n_units": current["analysis_unit"].nunique(),
                "median_observed_overlap": current["median_observed_overlap"].median(),
                "median_pseudo_overlap": current["median_pseudo_overlap"].median(),
                "median_specificity_margin": np.median(margins),
                "n_units_positive_margin": int((margins > 0).sum()),
                "wilcoxon_one_sided_p": p_value,
            }
        )
    method_summary = pd.DataFrame(method_rows)
    method_summary["holm_adjusted_p"] = np.nan
    for dataset_id, idx in method_summary.groupby("dataset_id").groups.items():
        method_summary.loc[idx, "holm_adjusted_p"] = multipletests(
            method_summary.loc[idx, "wilcoxon_one_sided_p"], method="holm"
        )[1]

    gates = method_summary.copy()
    gates["stability_threshold"] = stability_threshold
    gates["specificity_alpha"] = alpha
    gates["stability_gate_pass"] = gates["median_observed_overlap"] >= stability_threshold
    gates["specificity_gate_pass"] = (
        (gates["median_specificity_margin"] > 0) & (gates["holm_adjusted_p"] <= alpha)
    )
    gates["dual_gate_state"] = np.select(
        [
            gates["stability_gate_pass"] & gates["specificity_gate_pass"],
            gates["stability_gate_pass"] & ~gates["specificity_gate_pass"],
            ~gates["stability_gate_pass"] & gates["specificity_gate_pass"],
        ],
        ["stable_and_specific", "stable_but_not_specific", "specific_but_not_stable"],
        default="neither_stable_nor_specific",
    )
    return target, method_summary, gates


def synthesize_cross_platform_gates(gates: pd.DataFrame) -> pd.DataFrame:
    """Count recurrence of each method-level state across independent platforms."""
    rows: list[dict[str, object]] = []
    for method, current in gates.groupby("method", sort=True):
        states = current["dual_gate_state"]
        n_stable_not_specific = int(states.eq("stable_but_not_specific").sum())
        n_stable_specific = int(states.eq("stable_and_specific").sum())
        rows.append(
            {
                "method": method,
                "n_platforms": current["dataset_id"].nunique(),
                "n_stability_pass": int(current["stability_gate_pass"].sum()),
                "n_specificity_pass": int(current["specificity_gate_pass"].sum()),
                "n_stable_and_specific": n_stable_specific,
                "n_stable_but_not_specific": n_stable_not_specific,
                "n_specific_but_not_stable": int(states.eq("specific_but_not_stable").sum()),
                "n_neither": int(states.eq("neither_stable_nor_specific").sum()),
                "cross_platform_interpretation": (
                    "recurrent_stability_specificity_decoupling"
                    if n_stable_not_specific >= 2
                    else "no_recurrent_decoupling_demonstrated"
                ),
            }
        )
    return pd.DataFrame(rows)


def evaluate_stability_threshold_sensitivity(
    gates: pd.DataFrame,
    *,
    thresholds: tuple[float, ...] = (0.10, 0.15, 0.20, 0.25, 0.30),
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Recompute cross-platform states across declared stability thresholds."""
    required = {
        "dataset_id",
        "method",
        "median_observed_overlap",
        "median_specificity_margin",
        "holm_adjusted_p",
    }
    missing = sorted(required - set(gates.columns))
    if missing:
        raise ValueError(f"gate table is missing columns: {missing}")
    rows: list[pd.DataFrame] = []
    for threshold in thresholds:
        current = gates.copy()
        current["stability_threshold"] = float(threshold)
        current["specificity_alpha"] = float(alpha)
        current["stability_gate_pass"] = (
            current["median_observed_overlap"] >= threshold
        )
        current["specificity_gate_pass"] = (
            (current["median_specificity_margin"] > 0)
            & (current["holm_adjusted_p"] <= alpha)
        )
        current["dual_gate_state"] = np.select(
            [
                current["stability_gate_pass"] & current["specificity_gate_pass"],
                current["stability_gate_pass"] & ~current["specificity_gate_pass"],
                ~current["stability_gate_pass"] & current["specificity_gate_pass"],
            ],
            ["stable_and_specific", "stable_but_not_specific", "specific_but_not_stable"],
            default="neither_stable_nor_specific",
        )
        synthesis = synthesize_cross_platform_gates(current)
        synthesis.insert(1, "stability_threshold", float(threshold))
        synthesis.insert(2, "specificity_alpha", float(alpha))
        rows.append(synthesis)
    return pd.concat(rows, ignore_index=True)


def evaluate_platform_leave_one_out(gates: pd.DataFrame) -> pd.DataFrame:
    """Test whether recurrence survives deletion of each contributing platform."""
    dataset_ids = sorted(gates["dataset_id"].astype(str).unique())
    rows: list[pd.DataFrame] = []
    for omitted in dataset_ids:
        current = gates[~gates["dataset_id"].astype(str).eq(omitted)]
        synthesis = synthesize_cross_platform_gates(current)
        synthesis.insert(1, "omitted_dataset_id", omitted)
        synthesis.insert(2, "n_remaining_platforms", current["dataset_id"].nunique())
        rows.append(synthesis)
    result = pd.concat(rows, ignore_index=True)
    result["recurrence_survives_omission"] = result[
        "cross_platform_interpretation"
    ].eq("recurrent_stability_specificity_decoupling")
    return result


def summarize_platform_state_uncertainty(
    gates: pd.DataFrame,
    *,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Attach exact binomial intervals to descriptive platform-state proportions."""
    event_columns = {
        "stability_pass": "stability_gate_pass",
        "specificity_pass": "specificity_gate_pass",
        "stable_but_not_specific": "dual_gate_state",
    }
    rows: list[dict[str, object]] = []
    for method, current in gates.groupby("method", sort=True):
        n = int(current["dataset_id"].nunique())
        for event, column in event_columns.items():
            if event == "stable_but_not_specific":
                k = int(current[column].eq(event).sum())
            else:
                k = int(current[column].astype(bool).sum())
            low, high = proportion_confint(k, n, alpha=alpha, method="beta")
            rows.append(
                {
                    "method": method,
                    "platform_event": event,
                    "n_platforms": n,
                    "n_event": k,
                    "proportion": k / n,
                    "exact_ci_low": float(low),
                    "exact_ci_high": float(high),
                    "confidence_level": 1 - alpha,
                }
            )
    return pd.DataFrame(rows)


def render_platform_robustness_report(
    leave_one_out: pd.DataFrame,
    uncertainty: pd.DataFrame,
) -> str:
    """Render influence and small-platform-count uncertainty together."""
    lines = [
        "# Cross-platform Dual-gate Robustness Audit",
        "",
        "Leave-one-platform-out analysis re-applies the locked recurrence rule after "
        "removing each dataset. Exact binomial intervals describe the sampled "
        "platforms; they are not population estimates under guaranteed exchangeability.",
        "",
        "## Leave-one-platform-out",
        "",
        "| Method | Omitted dataset | Remaining | Stable only | Recurrence survives |",
        "|---|---|---:|---:|---|",
    ]
    for _, row in leave_one_out.sort_values(["method", "omitted_dataset_id"]).iterrows():
        lines.append(
            f"| `{row['method']}` | {row['omitted_dataset_id']} | "
            f"{int(row['n_remaining_platforms'])} | "
            f"{int(row['n_stable_but_not_specific'])} | "
            f"{str(bool(row['recurrence_survives_omission'])).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Platform-state uncertainty",
            "",
            "| Method | Event | Count | Proportion | Exact 95% CI |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for _, row in uncertainty.sort_values(["method", "platform_event"]).iterrows():
        lines.append(
            f"| `{row['method']}` | {row['platform_event']} | "
            f"{int(row['n_event'])}/{int(row['n_platforms'])} | {row['proportion']:.3f} | "
            f"[{row['exact_ci_low']:.3f}, {row['exact_ci_high']:.3f}] |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A nominal recurrence that fails after deletion of a contributing platform is "
            "classified as platform-sensitive evidence. It remains a replicated observation, "
            "but does not warrant a platform-robust or universal claim.",
            "",
        ]
    )
    return "\n".join(lines)


def render_threshold_sensitivity_report(sensitivity: pd.DataFrame) -> str:
    """Render threshold robustness without presenting the threshold as preregistered."""
    lines = [
        "# Cross-platform Dual-gate Threshold Sensitivity",
        "",
        "The stability floor was not preregistered. The full declared range below therefore "
        "shows whether the cross-platform interpretation depends on the nominal 0.20 choice. "
        "Specificity remains defined by a positive median margin and Holm-adjusted p <= 0.05.",
        "",
        "| Method | Stability floor | Platforms | Both | Stable only | Specific only | Neither | Interpretation |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in sensitivity.sort_values(["method", "stability_threshold"]).iterrows():
        lines.append(
            f"| `{row['method']}` | {row['stability_threshold']:.2f} | "
            f"{int(row['n_platforms'])} | {int(row['n_stable_and_specific'])} | "
            f"{int(row['n_stable_but_not_specific'])} | "
            f"{int(row['n_specific_but_not_stable'])} | {int(row['n_neither'])} | "
            f"{row['cross_platform_interpretation']} |"
        )
    robust = (
        sensitivity.groupby("method")["cross_platform_interpretation"]
        .apply(lambda values: values.eq("recurrent_stability_specificity_decoupling").all())
    )
    robust_methods = ", ".join(f"`{method}`" for method in robust[robust].index) or "none"
    lines.extend(
        [
            "",
            "## Robustness Readout",
            "",
            f"Methods retaining recurrent decoupling at every tested stability floor: {robust_methods}.",
            "",
            "This analysis tests threshold dependence only. It does not make the sampled "
            "platforms representative of all perturbation technologies or biological systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_cross_platform_report(
    contracts: pd.DataFrame,
    gates: pd.DataFrame,
    synthesis: pd.DataFrame,
) -> str:
    """Render an evidence-bounded cross-platform report."""
    lines = [
        "# Cross-platform Stability-Specificity Dual Gate",
        "",
        "The same count-ranked unit selection, equal-group sampling, top-100 ranking, "
        "five-repeat pseudo-perturbation design, and multiplicity correction were applied "
        "without dataset-specific result tuning.",
        "",
        "## Platform Gate States",
        "",
        "| Dataset | Split | Method | Units | Observed | Pseudo | Margin | Holm p | State |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in gates.sort_values(["dataset_id", "method"]).iterrows():
        lines.append(
            f"| {row['dataset_id']} | {row['split_strength']} | `{row['method']}` | "
            f"{int(row['n_units'])} | {row['median_observed_overlap']:.3f} | "
            f"{row['median_pseudo_overlap']:.3f} | {row['median_specificity_margin']:.3f} | "
            f"{row['holm_adjusted_p']:.4g} | {row['dual_gate_state']} |"
        )
    lines.extend(
        [
            "",
            "## Cross-platform Recurrence",
            "",
            "| Method | Platforms | Stability pass | Specificity pass | Both | Stable only | Interpretation |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in synthesis.iterrows():
        lines.append(
            f"| `{row['method']}` | {int(row['n_platforms'])} | {int(row['n_stability_pass'])} | "
            f"{int(row['n_specificity_pass'])} | {int(row['n_stable_and_specific'])} | "
            f"{int(row['n_stable_but_not_specific'])} | {row['cross_platform_interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Recurrence on multiple independent platforms supports a cross-platform empirical "
            "regularity, not a universal theorem. The 0.20 stability floor remains a post-result "
            "decision threshold, and results close to either gate require sensitivity analysis. "
            "Platform split strength is retained because biological-replicate or batch holdout is "
            "stronger than an arbitrary cell split.",
            "",
            "Source hashes and USB paths: `evidence/cross_platform_source_manifest.tsv`.",
            "",
            f"Newly selected perturbation units: {len(contracts)}; the locked Replogle "
            "reference contributes 16 additional units.",
            "",
        ]
    )
    return "\n".join(lines)
