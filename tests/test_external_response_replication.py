import numpy as np
import pandas as pd

from pgaa.core.external_response_replication import (
    benchmark_response_replication,
    deterministic_batch_split,
    paired_response_replication_comparisons,
    render_response_replication_report,
    summarize_response_replication,
)


def test_deterministic_batch_split_is_balanced_and_stable():
    batches = pd.Series([str(i) for i in range(1, 9)] * 2)
    first = deterministic_batch_split(batches)
    second = deterministic_batch_split(batches)

    assert first == second
    assert list(first.values()).count("discovery") == 4
    assert list(first.values()).count("validation") == 4


def test_response_replication_excludes_target_and_keeps_locked_denominator(tmp_path):
    rng = np.random.default_rng(7)
    genes = ["TARGET", "RESPONSE", "G2", "G3", "G4", "G5"]
    expression_rows = []
    metadata_rows = []
    cell_ids = []
    for batch in range(1, 5):
        for group in ("perturbed", "control"):
            for cell in range(12):
                cell_id = f"b{batch}_{group}_{cell}"
                values = rng.normal(0, 0.2, len(genes))
                if group == "perturbed":
                    values[0] += 3.0
                    values[1] += 2.0
                cell_ids.append(cell_id)
                expression_rows.append(values)
                metadata_rows.append(
                    {"cell_id": cell_id, "group": group, "source_batch": str(batch)}
                )
    expression_path = tmp_path / "expression.csv"
    metadata_path = tmp_path / "metadata.csv"
    pd.DataFrame(expression_rows, index=cell_ids, columns=genes).to_csv(expression_path)
    pd.DataFrame(metadata_rows).to_csv(metadata_path, index=False)
    contract = pd.DataFrame(
        [{"target_gene": "TARGET", "expression_csv": expression_path, "metadata_csv": metadata_path}]
    )

    results = benchmark_response_replication(
        contract, top_k=2, n_bins=5, min_cells_per_group_per_split=10
    )
    summary = summarize_response_replication(results)
    comparisons = paired_response_replication_comparisons(results)
    report = render_response_replication_report(results, summary, comparisons)

    assert len(results) == 4
    assert results["status"].eq("complete").all()
    assert results["n_evaluated_genes"].eq(5).all()
    assert results["top_k"].eq(2).all()
    assert summary["n_locked_targets"].eq(1).all()
    assert len(comparisons) == 4
    assert "not independent biological replication" in report


def test_response_replication_records_missing_batch_as_failure(tmp_path):
    expression_path = tmp_path / "expression.csv"
    metadata_path = tmp_path / "metadata.csv"
    pd.DataFrame([[1, 2], [2, 3]], index=["a", "b"], columns=["TARGET", "G1"]).to_csv(expression_path)
    pd.DataFrame({"cell_id": ["a", "b"], "group": ["perturbed", "control"]}).to_csv(metadata_path, index=False)
    contract = pd.DataFrame(
        [{"target_gene": "TARGET", "expression_csv": expression_path, "metadata_csv": metadata_path}]
    )

    results = benchmark_response_replication(contract, top_k=1)

    assert len(results) == 4
    assert results["status"].eq("failed").all()
    assert results["failure_reason"].str.contains("source_batch").all()

    summary = summarize_response_replication(results)
    comparisons = paired_response_replication_comparisons(results)
    assert summary["n_complete_targets"].eq(0).all()
    assert comparisons["n_paired_targets"].eq(0).all()
