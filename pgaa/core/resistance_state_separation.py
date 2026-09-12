"""Audit a locked resistance module across heterogeneous treatment contexts."""
from __future__ import annotations

import numpy as np
import pandas as pd


PRIMARY_MODULE_SIZE = 50
DEFAULT_DECOYS = 2000
DEFAULT_SEED = 249721
GSE249721_CONTEXTS = {
    "PC9_DTC": (
        tuple(f"PC9_CT_24h_{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"PC9_Erlo_DTC_{index}.genes.results" for index in (1, 2, 3)),
    ),
    "PC9_DTEC": (
        tuple(f"PC9_CT_24h_{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"PC9_Erlo_DTEC_{index}.genes.results" for index in (1, 2, 3)),
    ),
    "PC9_3_DTEC": (
        ("PC9-3_NT1_1.genes.results", "PC9-3_NT1_2.genes.results"),
        tuple(
            f"PC9-3_DTEC_{replicate}_75_jours.genes.results"
            for replicate in ("A", "B", "D", "E")
        ),
    ),
    "H4006_DTC": (
        tuple(f"H4006_CT_24h_{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"H4006_Erlo_DTC_{index}.genes.results" for index in (1, 2, 3)),
    ),
    "H4006_DTEC": (
        tuple(f"H4006_CT_24h_{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"H4006_Erlo_DTEC_{index}.genes.results" for index in (1, 2, 3)),
    ),
    "H3255_21d": (
        tuple(f"H3255_NT{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"H3255_Erlo_21j_{index}.genes.results" for index in (1, 2, 3)),
    ),
    "HCC827_11d": (
        tuple(f"HCC827Untreated{index}.genes.results" for index in (1, 2, 3)),
        tuple(f"HCC827Osimertinib11d{index}.genes.results" for index in (1, 2, 3)),
    ),
}


def prepare_gse249721(expression: pd.DataFrame) -> pd.DataFrame:
    """Convert composite row labels to stable Ensembl identifiers."""
    prepared = np.log1p(expression.astype(float))
    prepared.index = prepared.index.to_series().str.split("_").str[0]
    return prepared.groupby(level=0).mean()


def locked_down_genes(modules: pd.DataFrame) -> list[str]:
    """Return the prespecified 50-gene discovery module."""
    genes = (
        modules.loc[modules["direction"] == "down"]
        .sort_values("rank")
        .head(PRIMARY_MODULE_SIZE)["gene_id"]
        .astype(str)
        .str.split(".")
        .str[0]
        .tolist()
    )
    if len(genes) != PRIMARY_MODULE_SIZE:
        raise ValueError("The locked 50-gene down module is incomplete")
    return genes


def _context_gene_effects(
    expression: pd.DataFrame, control: tuple[str, ...], resistant: tuple[str, ...]
) -> pd.Series:
    columns = control + resistant
    missing = sorted(set(columns) - set(expression.columns))
    if missing:
        raise ValueError(f"GSE249721 matrix is missing columns: {missing}")
    selected = expression.loc[:, columns]
    standardized = selected.sub(selected.mean(axis=1), axis=0).div(
        selected.std(axis=1).replace(0, np.nan), axis=0
    )
    return standardized.loc[:, resistant].mean(axis=1) - standardized.loc[:, control].mean(axis=1)


def _matched_decoys(
    expression: pd.DataFrame,
    genes: list[str],
    decoy_count: int,
    seed: int,
) -> np.ndarray:
    feature_bins = pd.DataFrame(
        {
            "mean": pd.qcut(expression.mean(axis=1).rank(method="first"), 10, labels=False),
            "sd": pd.qcut(expression.std(axis=1).rank(method="first"), 10, labels=False),
        }
    )
    module = set(genes)
    pools = []
    for gene in genes:
        target = feature_bins.loc[gene]
        distance = (feature_bins["mean"] - target["mean"]).abs() + (
            feature_bins["sd"] - target["sd"]
        ).abs()
        minimum_distance = distance.loc[~feature_bins.index.isin(module)].min()
        pool = feature_bins.index[
            (distance == minimum_distance) & ~feature_bins.index.isin(module)
        ].to_numpy()
        pools.append(pool)
    generator = np.random.default_rng(seed)
    return np.asarray(
        [[generator.choice(pool) for pool in pools] for _ in range(decoy_count)]
    )


def audit_gse249721_separation(
    modules: pd.DataFrame,
    raw_expression: pd.DataFrame,
    decoy_count: int = DEFAULT_DECOYS,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Test directional transfer and sign-invariant panel separation."""
    expression = prepare_gse249721(raw_expression)
    locked = locked_down_genes(modules)
    genes = [gene for gene in locked if gene in expression.index]
    if len(genes) < 40:
        raise ValueError(f"Only {len(genes)} locked genes overlap GSE249721")
    decoys = _matched_decoys(expression, genes, decoy_count, seed)
    effects = pd.concat(
        {
            context: _context_gene_effects(expression, control, resistant)
            for context, (control, resistant) in GSE249721_CONTEXTS.items()
        },
        axis=1,
    )
    rows = []
    null_by_context = {}
    for context in effects.columns:
        module_effect = float(effects.loc[genes, context].mean())
        null = np.abs(
            effects.loc[decoys.ravel(), context]
            .to_numpy()
            .reshape(decoys.shape)
            .mean(axis=1)
        )
        null_by_context[context] = null
        p_value = (1 + int((null >= abs(module_effect) - 1e-12).sum())) / (
            decoy_count + 1
        )
        rows.append(
            {
                "context": context,
                "overlap_genes": len(genes),
                "resistant_minus_control_score": module_effect,
                "discovery_direction_supported": module_effect < 0,
                "absolute_separation": abs(module_effect),
                "matched_decoy_p": p_value,
                "context_gate": "pass" if p_value <= 0.05 else "fail",
            }
        )
    context_results = pd.DataFrame(rows)
    observed = float(context_results["absolute_separation"].mean())
    null_panel = np.column_stack(list(null_by_context.values())).mean(axis=1)
    panel_p = (1 + int((null_panel >= observed - 1e-12).sum())) / (decoy_count + 1)
    direction_count = int(context_results["discovery_direction_supported"].sum())
    significant_count = int((context_results["matched_decoy_p"] <= 0.05).sum())
    summary = pd.DataFrame(
        [
            {
                "route": "context_adaptive_resistance_state_separation",
                "contexts": len(context_results),
                "overlap_genes": len(genes),
                "direction_supported_contexts": direction_count,
                "matched_significant_contexts": significant_count,
                "mean_absolute_separation": observed,
                "panel_matched_decoy_p": panel_p,
                "universal_direction_gate": "pass" if direction_count == len(context_results) else "fail",
                "exploratory_panel_gate": "pass" if panel_p <= 0.05 else "fail",
                "claim_ceiling": "development_stage_sign_invariant_panel_association",
            }
        ]
    )
    return context_results, summary


def render_separation_audit(contexts: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render a failure-preserving interpretation of the third-system audit."""
    result = summary.iloc[0]
    lines = [
        "# Context-Adaptive Resistance-State Separation Audit",
        "",
        "## Verdict",
        "",
        "The third system falsifies universal directional transfer but supports an exploratory sign-invariant panel association after mean-variance-matched decoy control.",
        "",
        f"- Universal direction gate: `{result['universal_direction_gate']}` ({result['direction_supported_contexts']}/{result['contexts']} contexts).",
        f"- Exploratory panel gate: `{result['exploratory_panel_gate']}` (matched-decoy p={result['panel_matched_decoy_p']:.4f}).",
        f"- Individually significant contexts: {result['matched_significant_contexts']}/{result['contexts']}.",
        "",
        "## Context Results",
        "",
        "| Context | Signed effect | Absolute separation | Matched p | Direction retained | Gate |",
        "|---|---:|---:|---:|---|---|",
    ]
    for _, row in contexts.iterrows():
        lines.append(
            f"| {row['context']} | {row['resistant_minus_control_score']:.3f} | {row['absolute_separation']:.3f} | {row['matched_decoy_p']:.4f} | {row['discovery_direction_supported']} | {row['context_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The sign-invariant endpoint was selected after observing directional heterogeneity, so it is developmental rather than confirmatory. It cannot rescue a universal down-regulation claim. The next independent dataset must freeze the 50-gene membership, absolute-separation statistic, expression matching, random seed, and aggregate panel test before inspection.",
            "",
        ]
    )
    return "\n".join(lines)
