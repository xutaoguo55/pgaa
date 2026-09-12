"""Auditable matched event-expression import for CORTAD-seq data."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


T790M_VARIANT_ID = "chr_7_55249071_rs121434569_C_T"


def _gene_symbol(feature_id: str) -> str:
    parts = str(feature_id).rsplit("__", 1)
    return parts[-1].strip() if len(parts) == 2 and parts[-1].strip() else str(feature_id)


def prepare_gse112274_event_expression(
    expression: pd.DataFrame,
    mutation_af: pd.DataFrame,
    mutation_dp: pd.DataFrame,
    variant_id: str = T790M_VARIANT_ID,
    high_af: float = 0.10,
    low_af: float = 0.01,
    min_depth: int = 100,
    min_detected_cells: int = 10,
    n_variable_genes: int = 5000,
    target_gene: str = "EGFR",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create compact PGAA inputs from same-cell mutation and expression matrices."""
    if variant_id not in mutation_af.index or variant_id not in mutation_dp.index:
        raise ValueError(f"variant is absent from mutation matrices: {variant_id}")
    expression_cells = set(expression.columns.astype(str))
    if expression_cells != set(mutation_af.columns.astype(str)) or expression_cells != set(
        mutation_dp.columns.astype(str)
    ):
        raise ValueError("expression, mutation AF, and mutation DP cell columns must match")
    mutation_af = mutation_af.loc[:, expression.columns]
    mutation_dp = mutation_dp.loc[:, expression.columns]
    if high_af <= low_af:
        raise ValueError("high_af must be greater than low_af")

    af = mutation_af.loc[variant_id].astype(float)
    depth = mutation_dp.loc[variant_id].astype(float)
    state = pd.Series("excluded_transition", index=expression.columns, dtype=object)
    state.loc[(af >= high_af) & (depth >= min_depth)] = "event_high"
    state.loc[(af <= low_af) & (depth >= min_depth)] = "event_low"
    state.loc[depth < min_depth] = "excluded_low_depth"
    selected_cells = state.isin(["event_high", "event_low"])

    symbols = pd.Index([_gene_symbol(value) for value in expression.index])
    if symbols.duplicated().any():
        expression = expression.groupby(symbols, sort=False).sum()
    else:
        expression = expression.copy()
        expression.index = symbols
    if target_gene not in expression.index:
        raise ValueError(f"target gene is absent from expression matrix: {target_gene}")

    selected_raw = expression.loc[:, selected_cells]
    detected = selected_raw.gt(0).sum(axis=1) >= min_detected_cells
    transformed = np.log1p(selected_raw.loc[detected])
    variable = transformed.var(axis=1, ddof=1).sort_values(ascending=False)
    selected_genes = list(variable.head(n_variable_genes).index)
    if target_gene not in selected_genes:
        selected_genes = selected_genes[:-1] + [target_gene]
    selected_genes = list(dict.fromkeys(selected_genes))
    cli_expression = transformed.loc[selected_genes].T

    source_group = pd.Index(expression.columns).to_series(index=expression.columns).str.replace(
        r"_[0-9]+$", "", regex=True
    )
    metadata = pd.DataFrame(
        {
            "cell_id": expression.columns,
            "group": state.map({"event_high": "perturbed", "event_low": "control"}),
            "event_state": state,
            "t790m_af": af,
            "t790m_depth": depth,
            "source_cell_group": source_group,
            "library_size_fpkm": expression.sum(axis=0),
        }
    )
    cli_metadata = metadata.loc[selected_cells].reset_index(drop=True)

    summary = pd.DataFrame(
        [
            {
                "dataset_id": "GSE112274_CORTAD_seq_PC9",
                "event_id": variant_id,
                "event_label": "EGFR_T790M",
                "n_cells_total": int(len(state)),
                "n_event_high": int((state == "event_high").sum()),
                "n_event_low": int((state == "event_low").sum()),
                "n_excluded_transition": int((state == "excluded_transition").sum()),
                "n_excluded_low_depth": int((state == "excluded_low_depth").sum()),
                "n_genes_input": int(expression.shape[0]),
                "n_genes_cli": int(cli_expression.shape[1]),
                "high_af_threshold": high_af,
                "low_af_threshold": low_af,
                "min_depth": min_depth,
                "expression_transform": "log1p_FPKM",
                "feature_selection": (
                    f"detected_in_at_least_{min_detected_cells}_selected_cells;"
                    f"top_{n_variable_genes}_variance;force_include_{target_gene}"
                ),
                "claim_state": "matched_event_expression_association_input_not_causal_replication",
            }
        ]
    )
    return cli_expression, cli_metadata, summary


def import_gse112274_event_expression(
    expression_path: Path,
    mutation_af_path: Path,
    mutation_dp_path: Path,
    expression_out: Path,
    metadata_out: Path,
    summary_out: Path,
    **kwargs,
) -> pd.DataFrame:
    """Read public matrices and write compact, CLI-compatible artifacts."""
    expression = pd.read_csv(expression_path, index_col=0)
    mutation_af = pd.read_csv(mutation_af_path, index_col=0)
    mutation_dp = pd.read_csv(mutation_dp_path, index_col=0)
    cli_expression, metadata, summary = prepare_gse112274_event_expression(
        expression, mutation_af, mutation_dp, **kwargs
    )
    for path in (expression_out, metadata_out, summary_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    cli_expression.to_csv(expression_out)
    metadata.to_csv(metadata_out, index=False)
    summary.to_csv(summary_out, sep="\t", index=False)
    return summary


def render_gse112274_audit(summary: pd.DataFrame) -> str:
    """Render the evidence boundary for the matched event-expression pilot."""
    row = summary.iloc[0]
    return "\n".join(
        [
            "# GSE112274 Matched Event-Expression Audit",
            "",
            "Verdict: `READY_MATCHED_EVENT_EXPRESSION_ASSOCIATION_PILOT`",
            "",
            "## Imported Evidence",
            "",
            f"- Same-cell PC-9 expression and EGFR T790M allele fractions: {row['n_cells_total']} cells.",
            f"- Locked comparison: {row['n_event_high']} event-high versus {row['n_event_low']} event-low cells.",
            f"- Excluded before analysis: {row['n_excluded_transition']} transition and {row['n_excluded_low_depth']} low-depth cells.",
            f"- CLI matrix: {row['n_genes_cli']} genes after `{row['expression_transform']}` and the recorded variance filter.",
            "",
            "## Claim Boundary",
            "",
            "This is a matched event-expression association test from observational same-cell data. "
            "It is not a perturbation experiment, causal replication, antigen-presentation assay, "
            "or T-cell validation. HLA and peptide evidence must remain separate annotations.",
            "",
            "The manuscript mainline remains the claim-state compiler. This pilot may test whether "
            "the compiler can ingest a real event-linked expression state without promoting an "
            "immune claim.",
            "",
        ]
    )
