from pathlib import Path

import pandas as pd

from pgaa.core.dynamic_atm_validation import (
    evaluate_dynamic_atm_gradient,
    project_source_branch_axis,
    render_dynamic_atm_audit,
    summarize_source_branch_axis_projection,
)


def test_dynamic_atm_gradient_is_monotonic_and_exact() -> None:
    timecourse = pd.DataFrame(
        {
            "replication_branch_strength": [0.0, 0.33, 0.48, 0.64],
            "atm_added_benefit": [0.0, 7.0, 8.0, 32.0],
        }
    )
    result = evaluate_dynamic_atm_gradient(timecourse)
    assert result["spearman_rho"] == 1.0
    assert result["one_sided_exact_permutation_p"] == 1 / 24
    assert result["n_timepoints"] == 4


def test_dynamic_atm_audit_includes_source_axis_projection() -> None:
    phase_scores = pd.DataFrame(
        {
            "cell_cycle_phase": ["G1"],
            "day28_branch_induction": [2.028],
            "day0_replicates": [2],
            "day28_replicates": [2],
        }
    )
    timecourse = pd.DataFrame(
        {
            "day": [0, 7, 14, 28],
            "replication_branch_strength": [0.0, 0.33, 0.48, 0.64],
            "osimertinib_confluence": [72.0, 42.0, 32.0, 55.0],
            "atm_combo_confluence": [72.0, 35.0, 24.0, 23.0],
            "atm_added_benefit": [0.0, 7.0, 8.0, 32.0],
        }
    )
    audit = render_dynamic_atm_audit(
        phase_scores,
        timecourse,
        {
            "spearman_rho": 1.0,
            "one_sided_exact_permutation_p": 1 / 24,
            "n_timepoints": 4,
        },
    )

    assert "Source-Axis Projection" in audit
    assert "gse335846_rna_seq_branch_axis_scores.tsv" in audit


def test_source_axis_projection_summary_is_time_associated() -> None:
    root = Path(__file__).resolve().parents[1]
    ranked = pd.read_csv(
        root / "evidence/gse249721_resistance_branch_genes.tsv",
        sep="\t",
    )
    expression = pd.read_csv(
        root / "data/external/GSE335846/GSE335846_RNA-seq_for_GEO.txt.gz",
        sep="\t",
        compression="gzip",
        low_memory=False,
    ).loc[lambda frame: frame["Type"].eq("gene")].groupby("Feature").mean(numeric_only=True)

    projection = project_source_branch_axis(ranked, expression)
    summary = summarize_source_branch_axis_projection(projection)

    assert projection.shape[0] == 9
    assert summary["spearman_rho_day_vs_contrast"].iat[0] == 0.8660254037844386
    assert summary["spearman_pvalue_day_vs_contrast"].iat[0] == 0.002535996080258108
