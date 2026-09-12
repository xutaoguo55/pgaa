"""Predeclare a deterministic cross-target generality panel from h5ad metadata."""
from __future__ import annotations

import hashlib
from pathlib import Path

import anndata as ad
import pandas as pd


def _stable_order(gene: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}\0{gene}".encode()).hexdigest()


def build_generality_panel(
    obs: pd.DataFrame,
    var_names: pd.Index,
    excluded_targets: set[str],
    *,
    target_column: str = "gene",
    control_label: str = "non-targeting",
    batch_column: str = "batch",
    min_target_cells: int = 100,
    n_strata: int = 4,
    per_stratum: int = 4,
    selection_seed: str = "pgaa-generality-v1",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build a result-blind panel stratified only by target-cell abundance."""
    required = {target_column, batch_column}
    missing = sorted(required - set(obs.columns))
    if missing:
        raise ValueError(f"Missing observation columns: {', '.join(missing)}")
    if min_target_cells < 1 or n_strata < 1 or per_stratum < 1:
        raise ValueError("Panel thresholds and sizes must be positive")

    labels = obs[target_column].astype(str)
    batches = obs[batch_column].astype(str)
    control_mask = labels == control_label
    n_controls = int(control_mask.sum())
    if not n_controls:
        raise ValueError(f"Control label {control_label!r} was not found")

    non_control = obs.loc[~control_mask, [target_column, batch_column]].copy()
    non_control[target_column] = non_control[target_column].astype(str)
    non_control[batch_column] = non_control[batch_column].astype(str)
    counts = non_control.groupby(target_column, observed=True).size().rename("n_target_cells")
    batch_counts = (
        non_control.groupby(target_column, observed=True)[batch_column]
        .nunique()
        .rename("n_target_batches")
    )
    candidates = pd.concat([counts, batch_counts], axis=1).reset_index()
    candidates = candidates.rename(columns={target_column: "target_gene"})
    measured = set(map(str, var_names))
    candidates["target_gene_measured"] = candidates["target_gene"].isin(measured)
    candidates["excluded_current_target"] = candidates["target_gene"].isin(excluded_targets)
    candidates["eligible"] = (
        candidates["target_gene_measured"]
        & ~candidates["excluded_current_target"]
        & (candidates["n_target_cells"] >= min_target_cells)
    )
    candidates["selection_stratum"] = "ineligible"
    candidates["selection_order_sha256"] = candidates["target_gene"].map(
        lambda gene: _stable_order(gene, selection_seed)
    )
    candidates["selected"] = False

    eligible = candidates.loc[candidates["eligible"]].copy()
    required_n = n_strata * per_stratum
    if len(eligible) < required_n:
        raise ValueError(f"Only {len(eligible)} eligible targets; {required_n} required")

    # Rank first so ties in cell counts are assigned deterministically.
    abundance_rank = eligible.sort_values(
        ["n_target_cells", "target_gene"], kind="mergesort"
    ).reset_index().index
    eligible = eligible.sort_values(["n_target_cells", "target_gene"], kind="mergesort").copy()
    eligible["selection_stratum"] = pd.qcut(
        abundance_rank, q=n_strata, labels=[f"Q{i + 1}" for i in range(n_strata)]
    ).astype(str)
    chosen: list[int] = []
    for stratum in [f"Q{i + 1}" for i in range(n_strata)]:
        subset = eligible.loc[eligible["selection_stratum"] == stratum]
        chosen.extend(
            subset.sort_values("selection_order_sha256", kind="mergesort")
            .head(per_stratum)
            .index.tolist()
        )
    eligible.loc[chosen, "selected"] = True
    candidates.loc[eligible.index, ["selection_stratum", "selected"]] = eligible[
        ["selection_stratum", "selected"]
    ]

    candidates["n_control_cells"] = n_controls
    candidates["n_control_batches"] = int(batches.loc[control_mask].nunique())
    candidates["allowed_claim_role"] = "cross_target_generality_only_not_same_target_replication"
    panel = candidates.loc[candidates["selected"]].sort_values(
        ["selection_stratum", "target_gene"], kind="mergesort"
    )
    return candidates.reset_index(drop=True), panel.reset_index(drop=True)


def build_generality_panel_from_h5ad(
    path: Path, excluded_targets: set[str], **kwargs: object
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[int, int]]:
    """Read h5ad metadata in backed mode and leave the source file unchanged."""
    adata = ad.read_h5ad(Path(path), backed="r")
    try:
        candidates, panel = build_generality_panel(
            adata.obs, adata.var_names, excluded_targets, **kwargs
        )
        shape = (adata.n_obs, adata.n_vars)
    finally:
        adata.file.close()
    return candidates, panel, shape


def render_generality_panel_report(
    panel: pd.DataFrame,
    candidates: pd.DataFrame,
    source_path: Path,
    shape: tuple[int, int],
    excluded_targets: set[str],
    min_target_cells: int,
) -> str:
    """Render the predeclared panel and its claim boundary."""
    eligible = candidates[candidates["eligible"]]
    lines = [
        "# Replogle Essential Cross-target Generality Panel",
        "",
        "This panel was selected from metadata only in backed, read-only mode. No expression result or PGAA score was used for target selection, and the source h5ad was not copied, modified, or deleted.",
        "",
        f"- Source: `{source_path}`",
        f"- Shape: {shape[0]} cells x {shape[1]} features",
        f"- Excluded current targets: {', '.join(sorted(excluded_targets))}",
        f"- Eligibility: target gene measured and at least {min_target_cells} target cells",
        f"- Eligible targets: {len(eligible)}; locked panel: {len(panel)}",
        "- Selection: four abundance strata; four targets per stratum; deterministic SHA-256 ordering with seed `pgaa-generality-v1`",
        "",
        "| Stratum | Target | Target cells | Target batches | Control cells | Control batches |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in panel.iterrows():
        lines.append(
            f"| `{row['selection_stratum']}` | `{row['target_gene']}` | {int(row['n_target_cells'])} | "
            f"{int(row['n_target_batches'])} | {int(row['n_control_cells'])} | {int(row['n_control_batches'])} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This panel can test cross-target computational generality within the Replogle K562 essential-gene experiment. It is not a second biological source, does not replicate the existing responder states for the current targets, and cannot support wet-lab, immunopeptidomic, synthetic-peptide, or T-cell functional claims.",
            "",
            "Panel membership is locked before expression extraction. Targets must remain in the denominator after execution failures; failed targets may not be silently replaced.",
            "",
        ]
    )
    return "\n".join(lines)


def build_generality_execution_contract(
    panel: pd.DataFrame,
    source_h5ad: Path,
    output_dir: Path,
    *,
    n_perms: int = 2000,
    n_bins: int = 20,
) -> pd.DataFrame:
    """Create an executable PGAA contract without implying replication."""
    required = {"target_gene", "selected", "allowed_claim_role"}
    missing = sorted(required - set(panel.columns))
    if missing:
        raise ValueError(f"Panel is missing columns: {', '.join(missing)}")
    selected = panel[panel["selected"].astype(bool)]
    rows: list[dict[str, object]] = []
    for _, row in selected.iterrows():
        target = str(row["target_gene"])
        target_dir = Path(output_dir) / target
        prefix = target_dir / target
        expression = target_dir / "expression.csv"
        metadata = target_dir / "metadata.csv"
        command = (
            "python3 -m pgaa.cli "
            f"--expression {expression} --metadata {metadata} --target {target} "
            f"--out-prefix {prefix} --group-column group --perturbed-value perturbed "
            f"--control-value control --n-perms {n_perms} --n-bins {n_bins} "
            "--target-only-permutation-p"
        )
        rows.append(
            {
                "candidate_dataset_id": "replogle_2022_k562_essential_generality",
                "target_gene": target,
                "singlecell_h5ad": str(source_h5ad),
                "contract_status": "ready_for_pgaa_input_extraction",
                "expression_csv": str(expression),
                "metadata_csv": str(metadata),
                "pgaa_s1_out": str(prefix.with_suffix(".s1.csv")),
                "pgaa_s2_out": str(prefix.with_suffix(".s2.csv")),
                "pgaa_command": command,
                "allowed_claim_role": row["allowed_claim_role"],
                "claim_use": "cross_target_generality_execution_not_replication",
                "denominator_rule": f"all_{len(selected)}_locked_targets_including_failures",
            }
        )
    return pd.DataFrame(rows)
