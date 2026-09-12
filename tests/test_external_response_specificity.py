import numpy as np
import pandas as pd

from pgaa.core.external_response_specificity import (
    benchmark_response_specificity,
    render_response_specificity_report,
    summarize_response_specificity,
)


def test_matched_control_specificity_runs_and_summarizes(tmp_path):
    rng = np.random.default_rng(11)
    genes = ["TARGET", "RESPONSE", "G2", "G3", "G4"]
    values = []
    metadata = []
    ids = []
    for batch in range(1, 49):
        for group, n_cells in (("perturbed", 1), ("control", 4)):
            for cell in range(n_cells):
                cell_id = f"b{batch}_{group}_{cell}"
                row = rng.normal(0, 0.2, len(genes))
                if group == "perturbed":
                    row[0] += 3
                    row[1] += 2
                ids.append(cell_id)
                values.append(row)
                metadata.append(
                    {"cell_id": cell_id, "group": group, "source_batch": str(batch)}
                )
    expression_path = tmp_path / "expression.csv"
    metadata_path = tmp_path / "metadata.csv"
    pd.DataFrame(values, index=ids, columns=genes).to_csv(expression_path)
    pd.DataFrame(metadata).to_csv(metadata_path, index=False)
    contract = pd.DataFrame(
        [{"target_gene": "TARGET", "expression_csv": expression_path, "metadata_csv": metadata_path}]
    )

    results = benchmark_response_specificity(
        contract, top_k=2, n_bins=5, n_repeats=2, min_target_cells_per_split=10
    )
    target_level, summary = summarize_response_specificity(results)
    report = render_response_specificity_report(target_level, summary)

    assert len(results) == 8
    assert results["status"].eq("complete").all()
    assert len(target_level) == 4
    assert len(summary) == 4
    assert "post-result sensitivity" in report
