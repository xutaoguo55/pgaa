from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

from pgaa.core.cross_platform_dual_gate import (
    PlatformSpec,
    _load_expression,
    adapt_platform_observations,
    build_platform_unit_contract,
    evaluate_platform_leave_one_out,
    evaluate_stability_threshold_sensitivity,
    render_threshold_sensitivity_report,
    render_platform_robustness_report,
    summarize_platform_dual_gate,
    synthesize_cross_platform_gates,
    summarize_platform_state_uncertainty,
)


def test_norman_adapter_and_contract_are_result_blind():
    obs = pd.DataFrame(
        {
            "perturbation": ["control"] * 16 + ["A"] * 8 + ["B"] * 8,
            "nperts": [0] * 16 + [1] * 16,
            "gemgroup": (["1", "2"] * 8) + (["1", "2"] * 8),
        },
        index=[f"c{i}" for i in range(32)],
    )
    spec = PlatformSpec("d", "p", Path("x"), "norman2019", "gemgroup", None, "log1p_1e4", "batch")
    contract, split, adapted = build_platform_unit_contract(
        obs, spec, max_units=2, max_cells_per_group=4, min_cells_per_group=2
    )

    assert set(contract["analysis_unit"]) == {"A", "B"}
    assert contract["n_per_group"].eq(4).all()
    assert set(split.values()) == {"discovery", "validation"}
    assert adapted.loc[adapted["perturbation"].eq("control"), "is_control"].all()
    nadig = adapt_platform_observations(obs, "nadig2024")
    assert nadig["is_eligible_perturbation"].sum() == 16


def test_adapters_preserve_control_strata_and_drug_units():
    datlinger = pd.DataFrame(
        {
            "perturbation": ["control", "guide"],
            "perturbation_2": ["stimulated", "stimulated"],
            "target": [pd.NA, "NFKB1"],
        }
    )
    adapted_d = adapt_platform_observations(datlinger, "datlinger2017")
    assert adapted_d.loc[1, "analysis_unit"] == "NFKB1|stimulated"
    assert adapted_d.loc[0, "control_stratum"] == "stimulated"

    sciplex = pd.DataFrame(
        {"perturbation": ["control", "Drug"], "dose": [1.0, 0.1], "control": [1, 0]}
    )
    adapted_s = adapt_platform_observations(sciplex, "sciplex3")
    assert adapted_s.loc[1, "analysis_unit"] == "Drug|dose=0.1"
    assert adapted_s.loc[1, "excluded_feature"] == ""


def test_declarative_single_gene_adapter_and_result_blind_cell_filter():
    obs = pd.DataFrame(
        {
            "perturbation": [pd.NA] * 16 + ["A"] * 8 + ["B"] * 8,
            "nperts": [0] * 16 + [1] * 16,
            "batch": (["1", "2"] * 8) + (["1", "2"] * 8),
            "celltype": ["GMP"] * 32,
        },
        index=[f"c{i}" for i in range(32)],
    )
    adapted = adapt_platform_observations(obs, "single_gene_nperts")
    assert adapted.loc[adapted["nperts"].eq(0), "is_control"].all()
    assert set(adapted.loc[adapted["nperts"].eq(1), "excluded_feature"]) == {"A", "B"}

    spec = PlatformSpec(
        "d",
        "p",
        Path("x"),
        "single_gene_nperts",
        "batch",
        None,
        "log1p_1e4",
        "recorded_batch",
        (("celltype", "GMP"),),
    )
    contract, _, filtered = build_platform_unit_contract(
        obs, spec, max_units=2, max_cells_per_group=4, min_cells_per_group=2
    )
    assert set(contract["analysis_unit"]) == {"A", "B"}
    assert filtered["celltype"].eq("GMP").all()


def test_generic_condition_adapter_builds_contextual_units():
    rows = []
    for replicate in ("r1", "r2"):
        for time in ("6h", "24h"):
            rows.extend(
                {"treatment": "control", "time": time, "replicate": replicate}
                for _ in range(40)
            )
            rows.extend(
                {"treatment": "drug_a", "time": time, "replicate": replicate}
                for _ in range(20)
            )
    obs = pd.DataFrame(rows, index=[f"cell_{i}" for i in range(len(rows))])
    spec = PlatformSpec(
        dataset_id="contextual",
        platform="Contextual drug",
        path=Path("unused.h5ad"),
        adapter="generic_condition",
        batch_column="replicate",
        matrix_layer=None,
        normalization="log1p_1e4",
        split_strength="biological_replicate_holdout_1_vs_1",
        analysis_unit_columns=("treatment", "time"),
        control_stratum_columns=("time",),
        control_column="treatment",
        control_values=("control",),
    )
    contract, _, adapted = build_platform_unit_contract(
        obs, spec, max_units=8, max_cells_per_group=20, min_cells_per_group=20
    )
    assert set(contract["analysis_unit"]) == {"drug_a|6h", "drug_a|24h"}
    assert set(adapted.loc[adapted["is_control"], "control_stratum"]) == {
        "6h",
        "24h",
    }


def test_value_set_filter_is_applied_before_split_assignment():
    rows = []
    for replicate in ("r1", "r2", "pooled"):
        rows.extend(
            {"perturbation": "control", "nperts": 0, "batch": replicate}
            for _ in range(8)
        )
        rows.extend(
            {"perturbation": "A", "nperts": 1, "batch": replicate}
            for _ in range(4)
        )
    obs = pd.DataFrame(rows)
    spec = PlatformSpec(
        "d",
        "p",
        Path("x"),
        "single_gene_nperts",
        "batch",
        None,
        "log1p_1e4",
        "recorded_batch",
        obs_value_sets=(("batch", ("r1", "r2")),),
    )
    contract, split, filtered = build_platform_unit_contract(
        obs, spec, max_units=1, max_cells_per_group=4, min_cells_per_group=2
    )
    assert set(split) == {"r1", "r2"}
    assert set(filtered["batch"]) == {"r1", "r2"}
    assert len(contract) == 1


def test_load_expression_supports_backed_dense_double_subset(tmp_path):
    path = tmp_path / "dense.h5ad"
    matrix = np.arange(60, dtype=np.float32).reshape(10, 6)
    ad.AnnData(
        matrix,
        obs=pd.DataFrame({"ncounts": matrix.sum(axis=1)}),
    ).write_h5ad(path)
    backed = ad.read_h5ad(path, backed="r")
    try:
        spec = PlatformSpec(
            "dense", "dense", path, "nadig2024", "batch", None, "precomputed_log", "batch"
        )
        observed = _load_expression(
            backed, np.array([1, 4, 7]), np.array([0, 2, 5]), spec
        )
    finally:
        backed.file.close()
    np.testing.assert_array_equal(observed, matrix[[1, 4, 7]][:, [0, 2, 5]])


def test_platform_summary_and_cross_platform_recurrence():
    rows = []
    for dataset in ("d1", "d2"):
        for unit in tuple(f"u{i}" for i in range(1, 9)):
            for method in ("pgaa_w", "absolute_mean_shift"):
                for repeat in range(2):
                    observed = 0.8 if method == "pgaa_w" else 0.6
                    pseudo = (
                        (0.79 if int(unit[1:]) % 2 else 0.81)
                        if method == "pgaa_w"
                        else 0.2
                    )
                    rows.append(
                        {
                            "dataset_id": dataset,
                            "platform": dataset,
                            "split_strength": "batch",
                            "analysis_unit": unit,
                            "method": method,
                            "repeat": repeat,
                            "observed_top_k_overlap_fraction": observed,
                            "pseudo_top_k_overlap_fraction": pseudo,
                            "specificity_margin": observed - pseudo,
                        }
                    )
    _, _, gates = summarize_platform_dual_gate(pd.DataFrame(rows))
    synthesis = synthesize_cross_platform_gates(gates).set_index("method")

    assert synthesis.loc["pgaa_w", "n_stable_but_not_specific"] == 2
    assert synthesis.loc["pgaa_w", "cross_platform_interpretation"] == "recurrent_stability_specificity_decoupling"
    assert synthesis.loc["absolute_mean_shift", "n_stable_and_specific"] == 2

    sensitivity = evaluate_stability_threshold_sensitivity(
        gates, thresholds=(0.20, 0.70, 0.90)
    )
    w = sensitivity[sensitivity["method"].eq("pgaa_w")].set_index("stability_threshold")
    assert w.loc[0.20, "n_stable_but_not_specific"] == 2
    assert w.loc[0.90, "n_stable_but_not_specific"] == 0
    report = render_threshold_sensitivity_report(sensitivity)
    assert "not preregistered" in report
    assert "0.90" in report

    leave_one_out = evaluate_platform_leave_one_out(gates)
    w_loo = leave_one_out[leave_one_out["method"].eq("pgaa_w")]
    assert not w_loo["recurrence_survives_omission"].any()
    uncertainty = summarize_platform_state_uncertainty(gates)
    w_stable_only = uncertainty[
        uncertainty["method"].eq("pgaa_w")
        & uncertainty["platform_event"].eq("stable_but_not_specific")
    ].iloc[0]
    assert w_stable_only["n_event"] == 2
    assert w_stable_only["exact_ci_low"] < 0.5 < w_stable_only["exact_ci_high"]
    robustness_report = render_platform_robustness_report(leave_one_out, uncertainty)
    assert "describe the sampled platforms" in robustness_report
    assert "four sampled platforms" not in robustness_report
    assert "platform-sensitive evidence" in robustness_report
