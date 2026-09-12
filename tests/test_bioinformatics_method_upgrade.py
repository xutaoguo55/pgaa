from pgaa.core.bioinformatics_method_upgrade import (
    build_ablation_plan,
    build_comparator_contract,
    build_figure_plan,
    build_method_upgrade_matrix,
    render_positioning_doc,
    render_submission_position_doc,
)


def test_bioinformatics_upgrade_reframes_method_not_pharmacology() -> None:
    upgrades = build_method_upgrade_matrix()
    first = upgrades.sort_values("priority").iloc[0]

    assert first["upgrade_id"] == "bioinfo_01_problem_reframing"
    assert "claim-state compiler" in first["upgrade"]
    assert "ATM" not in first["pass_condition"].split("before")[0]


def test_comparator_contract_includes_conventional_and_claim_baselines() -> None:
    contract = build_comparator_contract()

    assert "SCEPTRE_or_CPT" in set(contract["comparator"])
    assert "Welch_or_mean_shift" in set(contract["comparator"])
    assert "state_blind_frozen_reporting" in set(contract["comparator"])
    assert any(contract["primary_endpoint"].str.contains("false-promotion"))


def test_ablation_plan_targets_claim_failure_modes() -> None:
    ablations = build_ablation_plan()

    assert "remove_branch_promotion_gate" in set(ablations["ablation_id"])
    assert any(ablations["expected_failure"].str.contains("ATM and HDAC"))
    assert "score_only_reporting" in set(ablations["ablation_id"])


def test_figure_plan_keeps_atm_as_late_use_case() -> None:
    figures = build_figure_plan()
    atm_figure = figures[figures["title"].str.contains("EGFR-resistance")].iloc[0]
    specificity = figures[
        figures["title"].str.contains("target-class specificity scorecard")
    ].iloc[0]

    assert atm_figure["figure"] == "Figure 4"
    assert "preclinical hypothesis" in atm_figure["boundary"]
    assert figures.iloc[0]["title"] == "PGAA as a claim-state compiler"
    assert specificity["figure"] == "Supplementary Figure S4"
    assert "runner-up positive tier" in specificity["primary_method_claim"]


def test_positioning_doc_declares_original_paper_and_gaps() -> None:
    doc = render_positioning_doc(
        build_method_upgrade_matrix(),
        build_comparator_contract(),
        build_ablation_plan(),
        build_figure_plan(),
    )

    assert "Target article type: Original Paper." in doc
    assert "not as another differential-expression" in doc
    assert "Immediate Gaps To Close" in doc
    assert "None" in doc


def test_updated_bioinformatics_components_are_available() -> None:
    upgrades = build_method_upgrade_matrix()

    status_map = dict(zip(upgrades["upgrade_id"], upgrades["status"]))
    assert status_map["bioinfo_01_problem_reframing"] == "available"
    assert status_map["bioinfo_04_comparator_fairness"] == "available"
    assert status_map["bioinfo_05_ablation_stack"] == "available"
    assert status_map["bioinfo_08_manuscript_figure_order"] == "available"
    assert status_map["bioinfo_09_target_specificity_scorecard"] == "available"


def test_submission_position_doc_reflects_the_current_package() -> None:
    doc = render_submission_position_doc(
        build_method_upgrade_matrix(),
        build_comparator_contract(),
        build_ablation_plan(),
        build_figure_plan(),
    )

    assert "Bioinformatics Submission Position" in doc
    assert "docs/SUBMISSION_PACKAGE_INDEX.md" in doc
    assert "Do not claim: ATM pharmacology is definitively validated" in doc
    assert "Supplementary Figure S4" in doc
    assert "gse193258_target_specificity_map.png" in doc
