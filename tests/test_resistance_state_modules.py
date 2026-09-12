import numpy as np
import pandas as pd

from pgaa.core.resistance_state_modules import (
    DISCOVERY_GROUPS,
    discover_resistance_modules,
    score_resistance_module_routes,
    select_resistance_reframe_route,
    validate_cortad_module_context,
    validate_resistance_modules,
)


def test_down_module_passes_independent_route_gate() -> None:
    genes = [f"ENSG{i:011d}" for i in range(480)]
    columns = [column for group in DISCOVERY_GROUPS.values() for column in group]
    discovery = pd.DataFrame(index=genes, columns=columns, dtype=float)
    for index, gene in enumerate(genes):
        base = 100.0 + index
        if index < 240:
            discovery.loc[gene] = [base, base + 1, base - 20, base - 19, base - 30, base - 29]
        else:
            discovery.loc[gene] = [base, base + 1, base + 20, base + 21, base + 30, base + 31]
    validation = pd.DataFrame(index=genes, columns=["A1", "A2", "A3", "C1", "C2", "C3"])
    for index, gene in enumerate(genes):
        base = 20.0 + index
        if index < 240:
            validation.loc[gene] = [base, base + 1, base + 2, base - 8, base - 7, base - 6]
        else:
            validation.loc[gene] = [base, base + 1, base + 2, base + 8, base + 9, base + 10]
    modules = discover_resistance_modules(discovery)
    results = validate_resistance_modules(modules, validation)
    routes = score_resistance_module_routes(results)
    down = routes.set_index("route").loc["shared_resistance_down_module"]
    assert down["route_gate"] == "pass"
    assert down["primary_exact_p"] == 0.05
    assert down["all_sizes_exact_p_le_0_05"]


def test_cortad_adjustment_can_reject_confounded_raw_difference() -> None:
    modules = pd.DataFrame(
        {
            "direction": ["down"] * 200,
            "rank": range(1, 201),
            "gene_id": [f"ENSG{i:011d}" for i in range(200)],
        }
    )
    annotation = pd.DataFrame(
        {
            "gene_id": modules["gene_id"],
            "display_name": [f"G{i}" for i in range(200)],
        }
    )
    cells = [f"group_a_S{i}" for i in range(20)] + [f"group_b_S{i}" for i in range(20)]
    expression = pd.DataFrame(
        np.tile(np.r_[np.repeat(2.0, 20), np.repeat(5.0, 20)][:, None], (1, 200)),
        index=cells,
        columns=annotation["display_name"],
    )
    metadata = pd.DataFrame(
        {
            "cell_id": cells,
            "group": ["perturbed"] * 20 + ["control"] * 20,
        }
    )
    cortad = validate_cortad_module_context(modules, annotation, expression, metadata)
    assert (cortad["adjusted_gate"] == "fail").all()
    routes = pd.DataFrame(
        {
            "route": ["shared_resistance_down_module", "shared_resistance_up_module"],
            "route_gate": ["pass", "fail"],
        }
    )
    selected = select_resistance_reframe_route(routes, cortad)
    assert selected.iloc[0]["candidate_route"] == "shared_resistance_down_module"
