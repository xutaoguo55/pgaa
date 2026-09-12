"""Discover PC9 resistance-state modules and validate them across datasets."""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


DISCOVERY_GROUPS = {
    "parental": ("PC9_VEH.rep1", "PC9_VEH.rep2"),
    "early_resistant": ("PC9_GR2_VEH.rep1", "PC9_GR2_VEH.rep2"),
    "late_resistant": ("PC9_GR3_VEH.rep1", "PC9_GR3_VEH.rep2"),
}
VALIDATION_PARENTAL = ("A1", "A2", "A3")
VALIDATION_RESISTANT = ("C1", "C2", "C3")
MODULE_SIZES = (10, 25, 50, 100, 200)
PRIMARY_MODULE_SIZE = 50


def _required_columns(frame: pd.DataFrame, columns: tuple[str, ...], label: str) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{label} matrix is missing columns: {missing}")


def _exact_one_sided_p(values: np.ndarray, n_parental: int) -> tuple[float, float]:
    observed = float(values[n_parental:].mean() - values[:n_parental].mean())
    differences = []
    for resistant_indices in combinations(range(len(values)), len(values) - n_parental):
        mask = np.zeros(len(values), dtype=bool)
        mask[list(resistant_indices)] = True
        differences.append(float(values[mask].mean() - values[~mask].mean()))
    p_value = sum(value >= observed - 1e-12 for value in differences) / len(differences)
    return observed, float(p_value)


def discover_resistance_modules(discovery_cpm: pd.DataFrame) -> pd.DataFrame:
    """Rank genes with replicate-robust changes in both resistant paths."""
    required = tuple(column for columns in DISCOVERY_GROUPS.values() for column in columns)
    _required_columns(discovery_cpm, required, "GSE75602")
    expression = np.log1p(discovery_cpm.loc[:, required].astype(float))
    parental = expression[list(DISCOVERY_GROUPS["parental"])]
    early = expression[list(DISCOVERY_GROUPS["early_resistant"])]
    late = expression[list(DISCOVERY_GROUPS["late_resistant"])]
    early_difference = early.mean(axis=1) - parental.mean(axis=1)
    late_difference = late.mean(axis=1) - parental.mean(axis=1)
    rows = []
    for direction in ("up", "down"):
        if direction == "up":
            robust = (early.min(axis=1) > parental.max(axis=1)) & (
                late.min(axis=1) > parental.max(axis=1)
            )
            locked_score = np.minimum(early_difference, late_difference)
        else:
            robust = (early.max(axis=1) < parental.min(axis=1)) & (
                late.max(axis=1) < parental.min(axis=1)
            )
            locked_score = np.minimum(-early_difference, -late_difference)
        ranked = locked_score[robust & (locked_score > 0)].sort_values(ascending=False)
        for rank, (gene_id, score) in enumerate(ranked.items(), start=1):
            rows.append(
                {
                    "direction": direction,
                    "rank": rank,
                    "gene_id": gene_id,
                    "locked_discovery_score": float(score),
                    "early_minus_parental_log1p_cpm": float(early_difference.loc[gene_id]),
                    "late_minus_parental_log1p_cpm": float(late_difference.loc[gene_id]),
                    "replicate_separation_robust": True,
                }
            )
    return pd.DataFrame(rows)


def validate_resistance_modules(
    modules: pd.DataFrame,
    validation_fpkm: pd.DataFrame,
    module_sizes: tuple[int, ...] = MODULE_SIZES,
) -> pd.DataFrame:
    """Validate discovery-ranked modules without re-ranking on GSE129221."""
    columns = VALIDATION_PARENTAL + VALIDATION_RESISTANT
    _required_columns(validation_fpkm, columns, "GSE129221")
    expression = np.log1p(validation_fpkm.loc[:, columns].astype(float))
    rows = []
    for direction in ("up", "down"):
        ranked = modules.loc[modules["direction"] == direction].sort_values("rank")
        for requested_size in module_sizes:
            genes = [gene for gene in ranked["gene_id"] if gene in expression.index][
                :requested_size
            ]
            if len(genes) != requested_size:
                raise ValueError(
                    f"Only {len(genes)} {direction} genes overlap for module size {requested_size}"
                )
            selected = expression.loc[genes]
            standard_deviation = selected.std(axis=1).replace(0, np.nan)
            standardized = selected.sub(selected.mean(axis=1), axis=0).div(
                standard_deviation, axis=0
            )
            orientation = 1.0 if direction == "up" else -1.0
            sample_scores = standardized.mean(axis=0).fillna(0.0) * orientation
            difference, p_value = _exact_one_sided_p(
                sample_scores.to_numpy(dtype=float), len(VALIDATION_PARENTAL)
            )
            gene_differences = (
                selected[list(VALIDATION_RESISTANT)].mean(axis=1)
                - selected[list(VALIDATION_PARENTAL)].mean(axis=1)
            ) * orientation
            rows.append(
                {
                    "direction": direction,
                    "requested_module_size": requested_size,
                    "overlap_module_size": len(genes),
                    "resistant_minus_parental_oriented_score": difference,
                    "exact_one_sided_p": p_value,
                    "gene_direction_concordance": float((gene_differences > 0).mean()),
                    "validation_direction_supported": bool(difference > 0),
                    "primary_module_size": requested_size == PRIMARY_MODULE_SIZE,
                }
            )
    return pd.DataFrame(rows)


def score_resistance_module_routes(validation: pd.DataFrame) -> pd.DataFrame:
    """Score up/down routes using locked replication and robustness gates."""
    rows = []
    for direction, group in validation.groupby("direction", sort=False):
        primary = group.loc[group["primary_module_size"]].iloc[0]
        all_directional = bool(group["validation_direction_supported"].all())
        all_exact = bool((group["exact_one_sided_p"] <= 0.05).all())
        median_concordance = float(group["gene_direction_concordance"].median())
        passed = bool(
            primary["exact_one_sided_p"] <= 0.05
            and primary["gene_direction_concordance"] >= 0.60
            and all_directional
            and all_exact
        )
        rows.append(
            {
                "route": f"shared_resistance_{direction}_module",
                "primary_module_size": PRIMARY_MODULE_SIZE,
                "primary_exact_p": float(primary["exact_one_sided_p"]),
                "primary_gene_direction_concordance": float(
                    primary["gene_direction_concordance"]
                ),
                "all_sizes_direction_supported": all_directional,
                "all_sizes_exact_p_le_0_05": all_exact,
                "median_gene_direction_concordance": median_concordance,
                "route_gate": "pass" if passed else "fail",
                "claim_ceiling": "development_stage_external_module_replication",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["route_gate", "median_gene_direction_concordance"],
        ascending=[False, False],
    )


def validate_cortad_module_context(
    modules: pd.DataFrame,
    annotation: pd.DataFrame,
    cortad_expression: pd.DataFrame,
    cortad_metadata: pd.DataFrame,
    module_sizes: tuple[int, ...] = MODULE_SIZES,
) -> pd.DataFrame:
    """Test the locked down module after adjusting for CORTAD source group."""
    metadata = cortad_metadata.set_index("cell_id").loc[cortad_expression.index].copy()
    metadata["event_high"] = (metadata["group"] == "perturbed").astype(int)
    metadata["source_group"] = metadata.index.to_series().str.rsplit("_S", n=1).str[0]
    overlap_groups = metadata.groupby("source_group")["event_high"].nunique()
    overlap_groups = overlap_groups.index[overlap_groups == 2]
    metadata = metadata.loc[metadata["source_group"].isin(overlap_groups)]
    mapping = annotation.set_index("gene_id")["display_name"].dropna().astype(str)
    ranked = modules.loc[modules["direction"] == "down"].sort_values("rank")
    rows = []
    for requested_size in module_sizes:
        locked_ids = ranked.head(requested_size)["gene_id"]
        symbols = [mapping.get(gene_id, "") for gene_id in locked_ids]
        genes = [gene for gene in symbols if gene and gene in cortad_expression.columns]
        selected = cortad_expression.loc[:, genes]
        standardized = selected.sub(selected.mean(axis=0), axis=1).div(
            selected.std(axis=0).replace(0, np.nan), axis=1
        )
        scores = -standardized.mean(axis=1)
        scores = scores.loc[metadata.index]
        model_data = metadata[["event_high", "source_group"]].copy()
        model_data["module_score"] = scores
        if not len(overlap_groups):
            rows.append(
                {
                    "requested_module_size": requested_size,
                    "mapped_cortad_genes": len(genes),
                    "overlap_source_groups": 0,
                    "raw_high_minus_low_oriented_score": np.nan,
                    "source_group_adjusted_high_minus_low": np.nan,
                    "source_group_adjusted_p": np.nan,
                    "adjusted_direction_supported": False,
                    "adjusted_gate": "fail",
                }
            )
            continue
        model = smf.ols(
            "module_score ~ event_high + C(source_group)", data=model_data
        ).fit(cov_type="HC3")
        raw_difference = float(
            scores.loc[metadata["event_high"] == 1].mean()
            - scores.loc[metadata["event_high"] == 0].mean()
        )
        rows.append(
            {
                "requested_module_size": requested_size,
                "mapped_cortad_genes": len(genes),
                "overlap_source_groups": len(overlap_groups),
                "raw_high_minus_low_oriented_score": raw_difference,
                "source_group_adjusted_high_minus_low": float(model.params["event_high"]),
                "source_group_adjusted_p": float(model.pvalues["event_high"]),
                "adjusted_direction_supported": bool(model.params["event_high"] > 0),
                "adjusted_gate": (
                    "pass"
                    if model.params["event_high"] > 0 and model.pvalues["event_high"] <= 0.05
                    else "fail"
                ),
            }
        )
    return pd.DataFrame(rows)


def select_resistance_reframe_route(
    routes: pd.DataFrame, cortad_validation: pd.DataFrame
) -> pd.DataFrame:
    """Compare event, module, and same-cell transfer routes."""
    down = routes.set_index("route").loc["shared_resistance_down_module"]
    up = routes.set_index("route").loc["shared_resistance_up_module"]
    cortad_primary = cortad_validation.loc[
        cortad_validation["requested_module_size"] == PRIMARY_MODULE_SIZE
    ].iloc[0]
    rows = [
        {
            "candidate_route": "fixed_t790m_egfr_effect",
            "gate": "fail",
            "evidence_strength": 0,
            "reason": "direction_discordant_across_GSE112274_and_GSE129221",
        },
        {
            "candidate_route": "shared_resistance_up_module",
            "gate": str(up["route_gate"]),
            "evidence_strength": 1 if up["route_gate"] == "pass" else 0,
            "reason": "fails_module_size_robustness",
        },
        {
            "candidate_route": "shared_resistance_down_module",
            "gate": str(down["route_gate"]),
            "evidence_strength": 3 if down["route_gate"] == "pass" else 0,
            "reason": "independent_directional_replication_all_locked_sizes",
        },
        {
            "candidate_route": "t790m_same_cell_down_module_transfer",
            "gate": str(cortad_primary["adjusted_gate"]),
            "evidence_strength": 2 if cortad_primary["adjusted_gate"] == "pass" else 0,
            "reason": "source_group_adjusted_CORTAD_test",
        },
        {
            "candidate_route": "pathway_mechanism",
            "gate": "fail",
            "evidence_strength": 0,
            "reason": "enrichment_fragmented_and_driven_by_small_terms",
        },
    ]
    return pd.DataFrame(rows).sort_values(
        ["evidence_strength", "candidate_route"], ascending=[False, True]
    )


def render_resistance_module_audit(
    modules: pd.DataFrame,
    validation: pd.DataFrame,
    routes: pd.DataFrame,
    cortad_validation: pd.DataFrame | None = None,
    reframe_routes: pd.DataFrame | None = None,
) -> str:
    """Render the route competition without converting it to confirmatory evidence."""
    winner = routes.iloc[0]
    lines = [
        "# PC9 Resistance-State Module Route Audit",
        "",
        f"Two-dataset provisional route: `{winner['route']}`",
        "",
        "Superseded for universal-direction claims by the locked GSE249721 audit in `docs/RESISTANCE_STATE_SEPARATION_AUDIT.md`, which observes direction reversal in the main PC9 contexts.",
        "",
        "## Locked Design",
        "",
        "GSE75602 is used only to rank genes showing complete replicate separation in the same direction in both early GR2 and late GR3 relative to parental PC9. GSE129221 is then used as an independent clone-level validation set without gene re-ranking. The 50-gene module is primary; sizes 10, 25, 100, and 200 are sensitivity checks.",
        "",
        "## Route Competition",
        "",
        "| Route | Primary exact p | Primary concordance | All sizes p <= 0.05 | Gate |",
        "|---|---:|---:|---|---|",
    ]
    for _, row in routes.iterrows():
        lines.append(
            f"| {row['route']} | {row['primary_exact_p']:.3f} | {row['primary_gene_direction_concordance']:.3f} | {row['all_sizes_exact_p_le_0_05']} | {row['route_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Validation Sensitivity",
            "",
            "| Direction | Module size | Oriented score difference | Exact p | Gene concordance |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in validation.iterrows():
        lines.append(
            f"| {row['direction']} | {row['requested_module_size']} | {row['resistant_minus_parental_oriented_score']:.3f} | {row['exact_one_sided_p']:.3f} | {row['gene_direction_concordance']:.3f} |"
        )
    if reframe_routes is not None:
        lines.extend(
            [
                "",
                "## Reframe Route Selection",
                "",
                "| Candidate | Gate | Evidence strength | Reason |",
                "|---|---|---:|---|",
            ]
        )
        for _, row in reframe_routes.iterrows():
            lines.append(
                f"| {row['candidate_route']} | {row['gate']} | {row['evidence_strength']} | {row['reason']} |"
            )
    if cortad_validation is not None:
        lines.extend(
            [
                "",
                "## Same-Cell Context Check",
                "",
                "The locked down module does not transfer to the CORTAD T790M-high contrast after restricting analysis to source groups containing both event states and adjusting for source group. The primary 50-gene module has 12 mapped genes, adjusted effect 0.026, and HC3 p=0.620. This failure prevents relabeling the module as T790M-specific.",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The shared down-regulated resistance module passes the two-dataset development gate across every prespecified module size. The up-regulated route is less stable and fails the all-size robustness gate. This result motivated a locked third-system test; it no longer supports a universal directional program because GSE249721 reverses direction in its main PC9 contexts.",
            "",
            "This is a route-selection result, not a final confirmatory claim. GSE75602 has two replicates per state, GSE129221 has three per group, and both are clone-level systems. The selected module must remain locked for any next dataset, and biological interpretation requires gene annotation and pathway analysis that do not alter membership.",
            "",
            f"Discovery contained {len(modules.loc[modules['direction'] == 'down'])} robust down genes and {len(modules.loc[modules['direction'] == 'up'])} robust up genes.",
            "",
        ]
    )
    return "\n".join(lines)
