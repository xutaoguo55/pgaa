"""Bioinformatics-first method-upgrade plan for PGAA."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_method_upgrade_matrix() -> pd.DataFrame:
    """Define the upgrades needed to make PGAA credible for Bioinformatics."""
    rows = [
        {
            "upgrade_id": "bioinfo_01_problem_reframing",
            "category": "positioning",
            "priority": 1,
            "current_gap": "PGAA can look like another perturbation ranking method.",
            "upgrade": "Reframe the method as a claim-state compiler that controls unsupported promotion from scores to biological claims.",
            "reviewer_value": "creates a distinct methodological object beyond differential-expression or target-recovery ranking",
            "required_artifact": "docs/BIOINFORMATICS_METHOD_POSITIONING.md",
            "pass_condition": "title, abstract, and first Results paragraph state claim-state compilation before any ATM biology",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_02_claim_promotion_metric",
            "category": "benchmark",
            "priority": 2,
            "current_gap": "Existing benchmarks can be interpreted as implementation-contract checks rather than empirical method comparisons.",
            "upgrade": "Promote false-promotion rate, exact-permission rate, under-promotion rate, and replication false-positive rate as formal reporting metrics.",
            "reviewer_value": "gives Bioinformatics reviewers quantitative endpoints that match the stated novelty",
            "required_artifact": "docs/CLAIM_PROMOTION_ERROR_BENCHMARK.md",
            "pass_condition": "main benchmark table compares compiler, frozen score reporting, decision-only, and external-only baselines",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_03_empirical_anchor",
            "category": "benchmark",
            "priority": 3,
            "current_gap": "Contract fidelity alone does not prove biological utility.",
            "upgrade": "Separate contract-stress tests from empirical anchors: Norman, Adamson, Replogle, and EGFR-resistance branch-vulnerability examples.",
            "reviewer_value": "prevents circular validation while preserving evidence for real-data usefulness",
            "required_artifact": "DATASET_MANIFEST.tsv",
            "pass_condition": "every empirical claim maps to a real source-data row and a claim ceiling",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_04_comparator_fairness",
            "category": "benchmark",
            "priority": 4,
            "current_gap": "Reviewers may ask whether PGAA outperforms SCEPTRE, CPT, Welch, or mean-shift on a conventional endpoint.",
            "upgrade": "Make comparator fairness explicit: conventional recovery metrics are reported, but the primary endpoint is claim-state correctness.",
            "reviewer_value": "preempts the criticism that the paper changes the target only after weak standard benchmark results",
            "required_artifact": "evidence/bioinformatics_comparator_contract.tsv",
            "pass_condition": "each comparator has input, endpoint, allowed interpretation, and limitation fields",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_05_ablation_stack",
            "category": "ablation",
            "priority": 5,
            "current_gap": "The compiler can appear rule-based unless the value of each evidence gate is shown.",
            "upgrade": "Add ablations removing stability, external evidence, source provenance, and branch-vulnerability promotion gates.",
            "reviewer_value": "shows which gates prevent which false-claim failure modes",
            "required_artifact": "evidence/bioinformatics_method_ablation_plan.tsv",
            "pass_condition": "each ablation has expected failure mode and manuscript consequence",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_06_branch_vulnerability_use_case",
            "category": "biological_demonstration",
            "priority": 6,
            "current_gap": "ATM could be read as an overextended pharmacology claim.",
            "upgrade": "Use ATM as a bounded demonstration of branch-specific vulnerability hypothesis compilation, not as a validated drug claim.",
            "reviewer_value": "adds biological interest without triggering translational overclaiming",
            "required_artifact": "docs/BRANCH_VULNERABILITY_PROMOTION_GATE.md",
            "pass_condition": "ATM is primary demonstration; HDAC remains secondary; definitive pharmacology is blocked",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_07_software_contract",
            "category": "software",
            "priority": 7,
            "current_gap": "Bioinformatics requires credible availability and reproducibility for method papers.",
            "upgrade": "Expose one-command scripts, CLI smoke tests, source-data manifest, and full pytest status as the software contract.",
            "reviewer_value": "reduces desk risk for reproducibility and software availability concerns",
            "required_artifact": "README.md",
            "pass_condition": "README lists key commands and tests pass from a clean checkout with documented external-data boundaries",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_08_manuscript_figure_order",
            "category": "presentation",
            "priority": 8,
            "current_gap": "Current story can feel like many rescued directions rather than one method paper.",
            "upgrade": "Reorder figures around method logic: compiler, claim-promotion benchmark, empirical anchors, branch-vulnerability case, reproducibility package.",
            "reviewer_value": "makes the paper legible as a Bioinformatics Original Paper",
            "required_artifact": "evidence/bioinformatics_figure_plan.tsv",
            "pass_condition": "every figure has a primary method claim and a non-overclaim boundary",
            "status": "available",
        },
        {
            "upgrade_id": "bioinfo_09_target_specificity_scorecard",
            "category": "presentation",
            "priority": 9,
            "current_gap": "The branch-specific ATM story has a target-specificity audit but no named figure slot in the method narrative.",
            "upgrade": "Render the GSE193258 target-specificity audit as a dedicated lead-target scorecard figure and carry it as a support figure in the submission package.",
            "reviewer_value": "makes the ATM specificity claim visually legible instead of leaving it buried in tables and prose",
            "required_artifact": "figures_png/gse193258_target_specificity_map.png",
            "pass_condition": "the support figure appears in the submission position and mirrors the audit conclusion without overstating validation",
            "status": "available",
        },
    ]
    return pd.DataFrame(rows)


def build_comparator_contract() -> pd.DataFrame:
    """Define fair comparator roles for a Bioinformatics-style methods paper."""
    rows = [
        {
            "comparator": "PGAA_claim_state_compiler",
            "comparison_role": "primary_method",
            "input": "PGAA outputs plus decision, stability, external, source, and promotion-gate metadata",
            "primary_endpoint": "claim-promotion correctness and bounded biological-use-case support",
            "allowed_interpretation": "reduces unsupported claim promotion while retaining actionable hypotheses",
            "limitation": "contract correctness is not biological truth without empirical anchors",
        },
        {
            "comparator": "state_blind_frozen_reporting",
            "comparison_role": "negative_reporting_baseline",
            "input": "observed permission rank held fixed after evidence-state mutation",
            "primary_endpoint": "false-promotion rate under evidence-gate mutation",
            "allowed_interpretation": "models a common reporting failure where claims do not update after evidence changes",
            "limitation": "not a published algorithm and should be labeled as a reporting baseline",
        },
        {
            "comparator": "decision_only_reporting",
            "comparison_role": "partial_gate_baseline",
            "input": "internal decision state only",
            "primary_endpoint": "under-promotion and replication sensitivity",
            "allowed_interpretation": "tests the cost of ignoring external evidence gates",
            "limitation": "conservative behavior can look safe while missing eligible replication claims",
        },
        {
            "comparator": "external_only_reporting",
            "comparison_role": "partial_gate_baseline",
            "input": "external concordance without internal or stability checks",
            "primary_endpoint": "replication false-positive rate",
            "allowed_interpretation": "tests the danger of promoting from external concordance alone",
            "limitation": "not a full expression-ranking method",
        },
        {
            "comparator": "SCEPTRE_or_CPT",
            "comparison_role": "conventional_method_baseline",
            "input": "single-cell perturbation expression and target/control labels where applicable",
            "primary_endpoint": "known-target recovery or ranking concordance",
            "allowed_interpretation": "contextualizes PGAA against established perturbation-analysis methods on conventional endpoints",
            "limitation": "does not directly solve claim-state promotion unless wrapped in the same compiler contract",
        },
        {
            "comparator": "Welch_or_mean_shift",
            "comparison_role": "simple_statistical_baseline",
            "input": "matched target/control expression matrices",
            "primary_endpoint": "known-target recovery, rank overlap, and claim-state after compiler wrapping",
            "allowed_interpretation": "tests whether PGAA adds value over simple distributional or mean-difference summaries",
            "limitation": "strong simple baselines should be retained, not hidden, because they define the honest method ceiling",
        },
    ]
    return pd.DataFrame(rows)


def build_ablation_plan() -> pd.DataFrame:
    """Define Bioinformatics-facing ablations."""
    rows = [
        {
            "ablation_id": "remove_stability_gate",
            "removed_component": "stability evidence",
            "expected_failure": "unstable internal units can be promoted as reproducible",
            "primary_metric": "increase in false promotion or reduction in exact permission",
            "manuscript_consequence": "justifies keeping leave-one-method and cross-dataset stability as formal gates",
        },
        {
            "ablation_id": "remove_external_gate",
            "removed_component": "external evidence state",
            "expected_failure": "same-context replication claims cannot be distinguished from internal-only support",
            "primary_metric": "replication sensitivity collapse or under-promotion",
            "manuscript_consequence": "shows why internal signal is not enough for replication language",
        },
        {
            "ablation_id": "remove_source_gate",
            "removed_component": "source-data provenance",
            "expected_failure": "figure-level or missing-source evidence can be promoted beyond traceable numerical support",
            "primary_metric": "source-ceiling violations",
            "manuscript_consequence": "supports the GSE335846 source-table boundary",
        },
        {
            "ablation_id": "remove_branch_promotion_gate",
            "removed_component": "branch-vulnerability promotion gate",
            "expected_failure": "ATM and HDAC can be promoted to the same claim level despite unequal evidence",
            "primary_metric": "candidate hierarchy violation",
            "manuscript_consequence": "preserves ATM as primary and HDAC as secondary",
        },
        {
            "ablation_id": "score_only_reporting",
            "removed_component": "claim-state compiler",
            "expected_failure": "ranked outputs become manuscript claims without evidence-state permissions",
            "primary_metric": "false-promotion rate",
            "manuscript_consequence": "establishes the central Bioinformatics novelty",
        },
    ]
    return pd.DataFrame(rows)


def build_figure_plan() -> pd.DataFrame:
    """Define a Bioinformatics-first figure order."""
    rows = [
        {
            "figure": "Figure 1",
            "title": "PGAA as a claim-state compiler",
            "primary_method_claim": "scores, stability, external evidence, source provenance, and promotion gates are compiled into bounded claim states",
            "required_source": "evidence/main_figure_source_data.tsv",
            "boundary": "workflow figure only; no biological validation claim",
        },
        {
            "figure": "Figure 2",
            "title": "False-promotion benchmark and ablation stack",
            "primary_method_claim": "the compiler reduces unsupported claim promotion compared with incomplete reporting baselines",
            "required_source": "docs/CLAIM_PROMOTION_ERROR_BENCHMARK.md;evidence/bioinformatics_method_ablation_plan.tsv",
            "boundary": "contract benchmark; not empirical proof of biological truth",
        },
        {
            "figure": "Figure 3",
            "title": "Empirical perturbation transcriptomics anchors",
            "primary_method_claim": "claim-state outputs remain traceable across Norman, Adamson, Replogle, and simple/computational baselines",
            "required_source": "DATASET_MANIFEST.tsv;evidence/result_claim_states.tsv",
            "boundary": "known-target recovery and reproducibility evidence, not universal method superiority",
        },
        {
            "figure": "Figure 4",
            "title": "EGFR-resistance branch-vulnerability demonstration",
            "primary_method_claim": "a frozen resistance branch compiles to an ATM vulnerability hypothesis across matched and dynamic systems",
            "required_source": "evidence/branch_vulnerability_promotion_gates.tsv;evidence/atm_hdac_branch_vulnerability_map.tsv",
            "boundary": "preclinical hypothesis; not clinical or definitive pharmacology",
        },
        {
            "figure": "Figure 5",
            "title": "Reproducibility and source-data audit",
            "primary_method_claim": "every promoted claim is backed by executable scripts, source-data rows, and explicit blocked-evidence states",
            "required_source": "DATASET_MANIFEST.tsv;evidence/gse335846_source_data_numeric_audit.tsv",
            "boundary": "documents reproducibility state; does not erase external-data limitations",
        },
        {
            "figure": "Supplementary Figure S4",
            "title": "GSE193258 target-class specificity scorecard",
            "primary_method_claim": "ATM is the cleanest positive target-class signal in the matched screen while ALK and HDAC remain runner-up positive tier candidates",
            "required_source": "docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md;figures_png/gse193258_target_specificity_map.png",
            "boundary": "lead-target specificity evidence; not independent validation or clinical pharmacology",
        },
    ]
    return pd.DataFrame(rows)


def render_positioning_doc(
    upgrades: pd.DataFrame,
    comparators: pd.DataFrame,
    ablations: pd.DataFrame,
    figures: pd.DataFrame,
) -> str:
    """Render the Bioinformatics-first method-positioning document."""
    required = upgrades[upgrades["status"].isin(["new_required", "planned"])]
    upgrade_rows = "\n".join(
        f"| {row.priority} | {row.upgrade_id} | {row.category} | {row.upgrade} | {row.pass_condition} | {row.status} |"
        for row in upgrades.sort_values("priority").itertuples()
    )
    comparator_rows = "\n".join(
        f"| {row.comparator} | {row.comparison_role} | {row.primary_endpoint} | {row.allowed_interpretation} | {row.limitation} |"
        for row in comparators.itertuples()
    )
    ablation_rows = "\n".join(
        f"| {row.ablation_id} | {row.removed_component} | {row.expected_failure} | {row.primary_metric} |"
        for row in ablations.itertuples()
    )
    figure_rows = "\n".join(
        f"| {row.figure} | {row.title} | {row.primary_method_claim} | {row.boundary} |"
        for row in figures.itertuples()
    )
    required_rows = "\n".join(
        f"- {row.upgrade_id}: {row.required_artifact}"
        for row in required.sort_values("priority").itertuples()
    )
    if not required_rows:
        required_rows = "None"
    return f"""# Bioinformatics-First Method Positioning

## Objective Verdict

Bioinformatics is a credible first target only if PGAA is presented as a computational method for claim-state compilation, not as another differential-expression or perturbation-ranking score. The methodological claim is that PGAA converts heterogeneous perturbation and resistance transcriptomic evidence into auditable claim states while minimizing unsupported claim promotion.

## Required Upgrade Matrix

| Priority | Upgrade | Category | Method change | Pass condition | Status |
|---:|---|---|---|---|---|
{upgrade_rows}

## Comparator Contract

| Comparator | Role | Primary endpoint | Allowed interpretation | Limitation |
|---|---|---|---|---|
{comparator_rows}

## Ablation Stack

| Ablation | Removed component | Expected failure | Primary metric |
|---|---|---|---|
{ablation_rows}

## Bioinformatics Figure Order

| Figure | Title | Primary method claim | Boundary |
|---|---|---|---|
{figure_rows}

## Immediate Gaps To Close

{required_rows}

## Submission Position

Target article type: Original Paper.

Lead sentence direction: Current perturbation-transcriptomic workflows often report ranked genes or associations, but manuscript claims require a separate, auditable evidence-state layer. PGAA fills this gap by compiling score, stability, external replication, source provenance, and promotion gates into claim states that preserve both positive hypotheses and evidence ceilings.

External pitch: see `docs/BIOINFORMATICS_SUBMISSION_POSITION.md` for the submission-facing version of the same story.
"""


def render_submission_position_doc(
    upgrades: pd.DataFrame,
    comparators: pd.DataFrame,
    ablations: pd.DataFrame,
    figures: pd.DataFrame,
) -> str:
    """Render a submission-facing Bioinformatics position note."""
    available = upgrades[upgrades["status"].isin(["available", "planned"])]
    method_rows = "\n".join(
        f"- {row.upgrade_id}: {row.upgrade}"
        for row in available.sort_values("priority").itertuples()
    )
    comparator_rows = "\n".join(
        f"- {row.comparator}: {row.primary_endpoint}"
        for row in comparators.itertuples()
    )
    ablation_rows = "\n".join(
        f"- {row.ablation_id}: {row.expected_failure}"
        for row in ablations.itertuples()
    )
    figure_rows = "\n".join(
        f"- {row.figure}: {row.title}"
        for row in figures.itertuples()
    )
    package_rows = [
        "- `docs/SUBMISSION_PACKAGE_INDEX.md`",
        "- `docs/AUTHOR_DATA_REQUEST_GSE335846.md`",
        "- `docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md`",
        "- `docs/PUBLICATION_GAP_AUDIT.md`",
    ]
    if any(str(row.figure).startswith("Supplementary Figure") for row in figures.itertuples()):
        package_rows.append("- `figures_png/gse193258_target_specificity_map.png`")
        package_rows.append("- `docs/GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md`")
    return f"""# Bioinformatics Submission Position

## Target

Article type: Original Paper.

Lead pitch: PGAA is a claim-state compiler for perturbation transcriptomics. It transforms score, stability, external replication, source provenance, and promotion gates into auditable claim states so manuscript claims stay bounded without discarding positive biological hypotheses.

## What Makes It A Bioinformatics Paper

{method_rows}

## Comparator Contract

{comparator_rows}

## Ablation Logic

{ablation_rows}

## Figure Spine

{figure_rows}

## Current Submission Package

{chr(10).join(package_rows)}

## Claim Ceiling

Do claim: PGAA compiles auditable claim states and produces a bounded branch-vulnerability demonstration.

Do not claim: ATM pharmacology is definitively validated, source-level dynamic response tables have been recovered, or the manuscript is ready for direct submission.
"""


def write_bioinformatics_upgrade_package(
    evidence_dir: Path,
    docs_dir: Path,
) -> dict[str, Path]:
    """Write Bioinformatics-first method-upgrade artifacts."""
    upgrades = build_method_upgrade_matrix()
    comparators = build_comparator_contract()
    ablations = build_ablation_plan()
    figures = build_figure_plan()

    evidence_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "upgrade_matrix": evidence_dir / "bioinformatics_method_upgrade_matrix.tsv",
        "comparator_contract": evidence_dir / "bioinformatics_comparator_contract.tsv",
        "ablation_plan": evidence_dir / "bioinformatics_method_ablation_plan.tsv",
        "figure_plan": evidence_dir / "bioinformatics_figure_plan.tsv",
        "positioning_doc": docs_dir / "BIOINFORMATICS_METHOD_POSITIONING.md",
        "submission_position_doc": docs_dir / "BIOINFORMATICS_SUBMISSION_POSITION.md",
    }
    upgrades.to_csv(paths["upgrade_matrix"], sep="\t", index=False)
    comparators.to_csv(paths["comparator_contract"], sep="\t", index=False)
    ablations.to_csv(paths["ablation_plan"], sep="\t", index=False)
    figures.to_csv(paths["figure_plan"], sep="\t", index=False)
    paths["positioning_doc"].write_text(
        render_positioning_doc(upgrades, comparators, ablations, figures),
        encoding="utf-8",
    )
    paths["submission_position_doc"].write_text(
        render_submission_position_doc(upgrades, comparators, ablations, figures),
        encoding="utf-8",
    )
    return paths
