import numpy as np
import pandas as pd

from pgaa.core.resistance_state_separation import (
    GSE249721_CONTEXTS,
    audit_gse249721_separation,
)


def test_separation_preserves_direction_failure() -> None:
    module_genes = [f"ENSG{index:011d}" for index in range(50)]
    background = [f"ENSG{index:011d}" for index in range(50, 550)]
    modules = pd.DataFrame(
        {"direction": "down", "rank": range(1, 51), "gene_id": module_genes}
    )
    columns = sorted(
        {
            column
            for groups in GSE249721_CONTEXTS.values()
            for group in groups
            for column in group
        }
    )
    generator = np.random.default_rng(7)
    values = generator.normal(10, 0.2, size=(550, len(columns)))
    expression = pd.DataFrame(
        values,
        index=[f"{gene}_G{index}" for index, gene in enumerate(module_genes + background)],
        columns=columns,
    )
    for context_index, (_, (control, resistant)) in enumerate(GSE249721_CONTEXTS.items()):
        direction = 1 if context_index == 0 else -1
        expression.loc[expression.index[:50], resistant] += direction * 4
    contexts, summary = audit_gse249721_separation(
        modules, expression, decoy_count=99, seed=11
    )
    assert len(contexts) == len(GSE249721_CONTEXTS)
    assert summary.iloc[0]["universal_direction_gate"] == "fail"
    assert summary.iloc[0]["exploratory_panel_gate"] == "pass"
    assert contexts.iloc[0]["discovery_direction_supported"] == False
