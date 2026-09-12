"""Journal-style manuscript draft for the PGAA recharter."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.cross_platform_dual_gate import (
    evaluate_platform_leave_one_out,
    synthesize_cross_platform_gates,
)
from pgaa.core.recharter_manuscript_draft import (
    _format_context_list,
    build_recharter_manuscript_payload,
)


REQUIRED_NOVELTY_COLUMNS = {
    "upgrade_id",
    "pillar_id",
    "pillar_name",
    "priority_tier",
}

REQUIRED_FORMAL_AUDIT_COLUMNS = {
    "invariant_id",
    "status",
    "n_checked",
    "n_violations",
}

REQUIRED_PROMOTION_BENCHMARK_COLUMNS = {
    "method",
    "scope",
    "n_scenarios",
    "false_promotion_rate",
    "under_promotion_rate",
    "exact_permission_rate",
    "replication_false_positive_rate",
    "replication_sensitivity",
}

def render_recharter_journal_style_draft(payload: dict[str, object]) -> str:
    """Render a more journal-like draft while preserving claim boundaries."""
    claim_counts = payload["claim_counts"]
    matrix_counts = payload["matrix_counts"]
    missing = payload["missing_readiness_artifacts"]
    blocked_evidence = list(missing)
    # The event-evidence readiness audit and the prospective v3 expression
    # cohort are separate gates. Keep the latter visible in the manuscript
    # even when the former is complete.
    v3_plan_path = Path(__file__).resolve().parents[2] / "evidence" / (
        "expansion_v3_ready_panel_execution_plan.tsv"
    )
    if v3_plan_path.is_file():
        v3_plan = pd.read_csv(v3_plan_path, sep="\t")
        if "source_available" in v3_plan.columns:
            unavailable = int((~v3_plan["source_available"].astype(bool)).sum())
            if unavailable:
                blocked_evidence.append(
                    {
                        "check_id": "v3_external_source_availability",
                        "artifact": str(v3_plan_path.relative_to(v3_plan_path.parents[1])),
                        "detail": (
                            f"{unavailable}/{len(v3_plan)} frozen v3 sources are unavailable; "
                            "prospective cross-platform scoring remains unexecuted"
                        ),
                    }
                )
    real_event_ready = len(missing) == 0
    supported_contexts = _format_context_list(payload["supported_contexts"])
    provisional_contexts = _format_context_list(payload["provisional_contexts"])
    stable_contexts = _format_context_list(payload["stable_contexts"])
    sensitive_contexts = _format_context_list(payload["sensitive_contexts"])
    n_external_concordant = payload["n_external_concordant_units"]
    n_external_blocked = payload["n_external_blocked_units"]
    n_external_discordant = payload["n_external_discordant_units"]
    n_external_unresolved = payload["n_external_unresolved_units"]
    has_external_layer = (
        n_external_concordant
        + n_external_blocked
        + n_external_discordant
        + n_external_unresolved
        > 0
    )
    n_novelty_upgrades = int(payload.get("n_novelty_upgrades", 0))
    n_tier1_upgrades = int(payload.get("n_tier1_novelty_upgrades", 0))
    novelty_provenance = (
        f"The framing spine is tracked in `evidence/novelty_upgrade_map.tsv` "
        f"({n_novelty_upgrades} upgrade points; {n_tier1_upgrades} tier-1 thesis points)."
        if n_novelty_upgrades
        else ""
    )
    n_invariants = int(payload.get("n_formal_invariants", 0))
    n_invariants_passed = int(payload.get("n_formal_invariants_passed", 0))
    n_invariant_violations = int(payload.get("n_formal_invariant_violations", 0))
    n_promotion_scenarios = int(payload.get("n_promotion_scenarios", 0))
    compiler_false_promotion = float(payload.get("compiler_false_promotion_rate", 0.0))
    frozen_false_promotion = float(payload.get("frozen_false_promotion_rate", 0.0))
    external_false_promotion = float(payload.get("external_false_promotion_rate", 0.0))
    decision_replication_sensitivity = float(
        payload.get("decision_replication_sensitivity", 0.0)
    )
    n_generality_targets = int(payload.get("n_generality_targets", 0))
    n_generality_complete = int(payload.get("n_generality_complete", 0))
    n_generality_w_top10 = int(payload.get("n_generality_w_top10", 0))
    n_generality_h_top10 = int(payload.get("n_generality_h_top10", 0))
    n_mean_shift_top10 = int(payload.get("n_mean_shift_top10", 0))
    n_welch_top10 = int(payload.get("n_welch_top10", 0))
    has_response_replication = bool(payload.get("has_response_replication", False))
    if has_response_replication:
        w_overlap = float(payload["response_w_overlap"])
        h_overlap = float(payload["response_h_overlap"])
        mean_overlap = float(payload["response_mean_overlap"])
        w_pseudo_overlap = float(payload["response_w_pseudo_overlap"])
        w_specificity_margin = float(payload["response_w_specificity_margin"])
        w_specificity_holm_p = float(payload["response_w_specificity_holm_p"])
        h_specificity_margin = float(payload["response_h_specificity_margin"])
        h_specificity_holm_p = float(payload["response_h_specificity_holm_p"])
        response_abstract_sentence = (
            f"In a held-out-batch non-target response benchmark, PGAA-W showed {w_overlap:.1%} "
            f"top-100 overlap versus {mean_overlap:.1%} for mean shift, but matched "
            f"control-versus-control overlap was {w_pseudo_overlap:.1%}; its {w_specificity_margin:.1%} "
            f"specificity margin was not significant after Holm correction (p={w_specificity_holm_p:.3f}). "
            f"PGAA-H had only {h_overlap:.1%} absolute overlap despite a {h_specificity_margin:.1%} "
            f"specificity margin (Holm p={h_specificity_holm_p:.3g}). "
        )
        response_results = (
            "### A pseudo-perturbation gate separates reproducibility from response specificity\n\n"
            "We next excluded each directly perturbed gene and compared discovery-versus-validation "
            "top-100 response rankings across a locked 24/24 batch split. PGAA-W initially appeared "
            f"strongest, with median overlap {w_overlap:.3f}, compared with {mean_overlap:.3f} for "
            f"absolute mean shift; PGAA-H overlap was {h_overlap:.3f}. This apparent PGAA-W advantage "
            "did not survive a matched control-versus-control stress test. Across five deterministic "
            f"equal-size repeats, the PGAA-W pseudo overlap was {w_pseudo_overlap:.3f}, leaving a median "
            f"specificity margin of {w_specificity_margin:.3f} (Holm p={w_specificity_holm_p:.4g}). "
            "The high Wasserstein overlap therefore largely reflects reproducible gene-wise distributional "
            "properties rather than demonstrated perturbation-specific response. PGAA-H showed a statistically "
            f"positive but small margin ({h_specificity_margin:.3f}; Holm p={h_specificity_holm_p:.4g}) against "
            f"a low absolute overlap of {h_overlap:.3f}, which is insufficient for a useful stability claim. "
            "Under the resulting stability-specificity dual gate, absolute mean shift was the only method to "
            "pass both gates; PGAA-W was stable but not response-specific, whereas PGAA-H and Welch were "
            "specificity-positive but insufficiently stable.\n\n"
            "Evidence source: `evidence/replogle_essential_response_replication.tsv` and "
            "`evidence/replogle_essential_response_specificity_summary.tsv`; compiled decision states: "
            "`evidence/response_stability_specificity_dual_gate.tsv`.\n\n"
            "Claim boundary: this post-result stress test is within one experiment. It rejects a PGAA-W "
            "response-specific superiority interpretation and does not establish biological correctness."
        )
        response_methods_sentence = (
            "Held-out response stability and specificity. Source batches 1-48 were deterministically "
            "divided into 24 discovery and 24 validation batches. The perturbed target gene was excluded, "
            "and top-100 overlap, Jaccard index, all-gene Spearman correlation, and hypergeometric overlap "
            "were computed for PGAA-W, PGAA-H, absolute mean shift, and absolute Welch t. A post-result "
            "specificity stress test then repeated each comparison five times with equal-size pseudo-target "
            "and matched-control groups drawn only from controls. Repeat-level results were aggregated within "
            "target before one-sided Wilcoxon testing and Holm correction."
        )
    else:
        response_abstract_sentence = ""
        response_results = ""
        response_methods_sentence = ""
    if payload.get("has_cross_platform_dual_gate", False):
        n_cross_platforms = int(payload["n_cross_platforms"])
        recurrent_methods = list(payload["cross_platform_recurrent_methods"])
        robust_methods = list(payload["cross_platform_threshold_robust_methods"])
        recurrence_limits = list(payload["cross_platform_recurrence_limits"])
        loo_robust_methods = list(payload["cross_platform_leave_one_out_robust_methods"])
        recurrent_text = ", ".join(f"`{method}`" for method in recurrent_methods) or "none"
        robust_text = ", ".join(f"`{method}`" for method in robust_methods) or "none"
        recurrence_limit_text = ", ".join(recurrence_limits) or "none"
        loo_robust_text = ", ".join(f"`{method}`" for method in loo_robust_methods) or "none"
        loo_abstract_clause = (
            f"methods surviving every leave-one-platform-out deletion were {loo_robust_text}"
            if loo_robust_methods
            else "no method survived every leave-one-platform-out deletion"
        )
        loo_results_clause = (
            f"Methods retaining recurrence after every platform deletion: {loo_robust_text}."
            if loo_robust_methods
            else "No method retained recurrence after every platform deletion."
        )
        state_text = "; ".join(payload["cross_platform_state_descriptions"])
        cross_platform_abstract_sentence = (
            f"Across {n_cross_platforms} independent perturbation datasets, the same dual-gate "
            f"design identified recurrent stability-specificity decoupling for {recurrent_text}; "
            f"the tested stability-floor limit of recurrence was {recurrence_limit_text}, and "
            f"{loo_abstract_clause}. "
        )
        cross_platform_results = (
            "### The dual gate exposes recurrent cross-platform decoupling\n\n"
            "We applied one result-blind contract to independent CRISPRi, CRISPRa, conventional "
            "CRISPR and multiplexed drug perturbation datasets. Perturbation units were selected "
            "by available cell count, while equal group size, five deterministic repeats, top-100 "
            "ranking, pseudo-target controls and Holm correction were shared. At the nominal 0.20 "
            f"stability floor, the observed states were: {state_text}. Recurrent stable-but-not-specific "
            f"behavior occurred for {recurrent_text}. Across stability floors 0.10-0.30, methods "
            f"retaining that recurrence at every threshold were {robust_text}.\n\n"
            f"{loo_results_clause} Accordingly, the nominal "
            "recurrence is treated as platform-sensitive rather than platform-robust.\n\n"
            "Evidence source: `evidence/cross_platform_dual_gate_states.tsv`, "
            "`evidence/cross_platform_dual_gate_synthesis.tsv` and "
            "`evidence/cross_platform_dual_gate_threshold_sensitivity.tsv`; deletion and interval "
            "audit: `evidence/cross_platform_dual_gate_leave_one_out.tsv` and "
            "`evidence/cross_platform_dual_gate_platform_uncertainty.tsv`.\n\n"
            "Claim boundary: this is a cross-platform empirical recurrence in the sampled systems, "
            "not proof of a universal law. The stability floor was not preregistered, platform splits "
            "differ in strength, and specificity here is statistical rather than biological validation."
        )
        cross_platform_methods_sentence = (
            "Cross-platform dual-gate benchmark. Dataset-specific adapters defined perturbation, "
            "control and replicate metadata only. The statistical contract then selected up to 16 "
            "count-ranked units per dataset, capped equal groups at 70 cells, excluded direct targets "
            "for gene perturbations, evaluated 5,000 features, and compared observed with pseudo-target "
            "top-100 overlap across five deterministic repeats. Target-level median specificity margins "
            "were tested by one-sided Wilcoxon tests with within-dataset Holm correction. Stability "
            "floors from 0.10 to 0.30 were reported because 0.20 was a post-result decision threshold."
        )
    else:
        cross_platform_abstract_sentence = ""
        cross_platform_results = ""
        cross_platform_methods_sentence = ""
    if n_generality_targets:
        generality_abstract_sentence = (
            f"A locked 16-target Replogle essential-gene panel completed {n_generality_complete}/"
            f"{n_generality_targets} runs; PGAA-W and PGAA-H placed the perturbed target in the "
            f"top decile for {n_generality_w_top10}/{n_generality_targets} and "
            f"{n_generality_h_top10}/{n_generality_targets} targets, respectively. Simple "
            f"mean-shift and Welch baselines also reached {n_mean_shift_top10}/"
            f"{n_generality_targets} and {n_welch_top10}/{n_generality_targets}, preventing "
            "a target-recovery superiority claim. "
        )
        generality_results = (
            "### A locked cross-target panel separates execution generality from superiority\n\n"
            f"We selected 16 targets from 1,164 eligible perturbations using expression-blind "
            "cell-count strata and retained every locked target in the denominator. All "
            f"{n_generality_complete}/{n_generality_targets} runs completed. PGAA-W placed the "
            f"perturbed gene in the top decile for {n_generality_w_top10}/"
            f"{n_generality_targets} targets and PGAA-H did so for {n_generality_h_top10}/"
            f"{n_generality_targets}. However, post-pilot absolute mean-shift and Welch "
            f"baselines reached the same threshold for {n_mean_shift_top10}/"
            f"{n_generality_targets} and {n_welch_top10}/{n_generality_targets} targets. The "
            "panel therefore supports cross-target execution generality and transparent "
            "failure accounting, but direct target recovery does not distinguish PGAA from "
            "simple conventional summaries.\n\n"
            "Evidence source: `evidence/replogle_essential_generality_results.tsv` and "
            "`evidence/replogle_essential_generality_baseline_comparison.tsv`.\n\n"
            "Claim boundary: this is one K562 experiment, not independent biological "
            "replication, and the exploratory baselines do not support method superiority."
        )
        generality_methods_sentence = (
            "Cross-target generality audit. Targets were selected from metadata alone using "
            "four target-cell abundance strata and deterministic hashing. All target cells, "
            "a shared deterministic 1,000-control subsample, and all measured genes entered "
            "PGAA-W and PGAA-H. The locked denominator included failures. Primary recovery "
            "endpoints were target permutation p values and target rank percentiles; absolute "
            "mean shift and absolute Welch statistics were explicitly post-pilot exploratory "
            "baselines."
        )
    else:
        generality_abstract_sentence = ""
        generality_results = ""
        generality_methods_sentence = ""
    if n_invariants:
        formal_abstract_sentence = (
            f"An executable formal audit tested {n_invariants} compiler invariants; "
            f"{n_invariants_passed} passed with {n_invariant_violations} observed violations, "
            "including counterfactual checks against illegal claim promotion. "
        )
        formal_results = (
            "### Executable invariants make evidence-to-claim translation falsifiable\n\n"
            f"We represented the compiler as a finite permission system linking row-level "
            f"claim states, responder decisions, omission stability, and typed external "
            f"evidence. The audit evaluated {n_invariants} invariants and recorded "
            f"{n_invariants_passed} passes with {n_invariant_violations} violations. Tested "
            "conditions included deterministic action-to-state mapping, preservation of "
            "failure rows during aggregation, witness requirements for supported and "
            "provisional units, stability-label consistency, external-concordance "
            "preconditions, and rejection of five counterfactual illegal promotions. The "
            "compiler can therefore fail explicitly when evidence and permission diverge.\n\n"
            "Evidence source: `evidence/claim_state_invariant_audit.tsv`, "
            "`evidence/claim_transition_rules.tsv`, and "
            "`docs/CLAIM_STATE_COMPILER_FORMALIZATION.md`.\n\n"
            "Claim boundary: passing software invariants establishes internal contract "
            "consistency, not empirical correctness or biological validation."
        )
        formal_methods_sentence = (
            "Formal permission system. The compiler defines finite vocabularies for row "
            "claims, responder decisions, stability states, and external states. A unit "
            "receives bounded computational same-context replication permission if and only "
            "if it is internally supported, leave-one-method stable, and externally "
            "concordant. Blocked, unresolved, discordant, provisional, and unstable inputs "
            "cannot emit replication permission, and no computational state can emit "
            "biological-validation permission. These constraints are evaluated as executable "
            "invariants and counterfactual transition tests."
        )
    else:
        formal_abstract_sentence = ""
        formal_results = ""
        formal_methods_sentence = ""
    if n_promotion_scenarios:
        promotion_abstract_sentence = (
            f"Across {n_promotion_scenarios} exhaustive finite-state scenarios, the compiler "
            f"had a {compiler_false_promotion:.1%} contract-defined false-promotion rate, "
            f"compared with {frozen_false_promotion:.1%} for a state-blind frozen-output "
            f"baseline and {external_false_promotion:.1%} for an external-only gate. "
        )
        promotion_results = (
            "### Exhaustive state mutation quantifies unsupported claim promotion\n\n"
            f"We exhaustively enumerated {n_promotion_scenarios} decision-by-stability-by-"
            "external-state scenarios over the observed units and compared four reporting "
            "strategies against the predeclared permission contract. The claim-state compiler "
            f"produced a {compiler_false_promotion:.1%} false-promotion rate. A state-blind "
            f"frozen-output baseline produced {frozen_false_promotion:.1%} false promotions, "
            "whereas an external-only baseline that ignored internal support and stability "
            f"produced {external_false_promotion:.1%}. A decision-only baseline avoided false "
            f"promotion but had {decision_replication_sensitivity:.1%} replication sensitivity, "
            "showing that indiscriminate claim suppression is not equivalent to faithful "
            "permission compilation.\n\n"
            "Evidence source: `evidence/claim_promotion_benchmark_summary.tsv` and "
            "`docs/CLAIM_PROMOTION_ERROR_BENCHMARK.md`.\n\n"
            "Claim boundary: the oracle is the declared compiler contract. This stress test "
            "verifies contract fidelity under evidence-state mutation; it is not independent "
            "biological ground truth or evidence that the contract is empirically optimal."
        )
        promotion_methods_sentence = (
            "Claim-promotion stress test. For each observed decision unit, we enumerated the "
            "complete finite product of six decision states, four stability states, and five "
            "external states. False promotion was defined as a predicted permission rank "
            "above the predeclared contract ceiling; under-promotion was the converse. We "
            "also measured exact permission agreement, replication false-positive rate among "
            "ineligible states, and replication sensitivity among eligible states. The "
            "state-blind comparator freezes the observed permission as a favorable proxy for "
            "reporting that does not update after evidence changes; it is not presented as a "
            "universal raw-score threshold."
        )
    else:
        promotion_abstract_sentence = ""
        promotion_results = ""
        promotion_methods_sentence = ""
    if has_external_layer:
        external_abstract_sentence = (
            f"External Replogle K562 GWPS integration identifies "
            f"{n_external_concordant} bounded computational same-context concordant units, "
            f"with {n_external_blocked} external-blocked, {n_external_discordant} discordant, "
            f"and {n_external_unresolved} unresolved units. "
        )
        stability_result_sentence = (
            f"The integrated external layer records {n_external_concordant} "
            "external_same_context_concordant units and keeps the remaining "
            f"{n_external_blocked} external_same_context_blocked units internal-only. "
            "This allows bounded computational replication language for concordant rows "
            "without converting them into biological validation."
        )
        stability_boundary = (
            "Claim boundary: external_same_context_concordant rows support only bounded "
            "computational same-context replication; external_same_context_blocked rows "
            "remain internal-only."
        )
        discussion_external_sentence = (
            "The new external layer reduces the earlier externality gap, but it does not "
            "remove the claim ceiling. Replogle K562 GWPS provides concordant same-context "
            "computational claim states for the stable supported Adamson units, while "
            "blocked rows remain visible rather than silently promoted. The strongest local "
            "PC9 drug-perturbation candidates still do not close the third-system gap: "
            "Aissa2021 is blocked by a single-batch metadata contract error, and Chang2021 "
            "is below the minimum selected-unit gate."
        )
        methods_external_sentence = (
            "External responder-state integration. Replogle K562 GWPS PGAA-W and PGAA-H "
            "outputs were compiled into target-level external claim states and joined to "
            "the internal responder-state stability table. Concordant rows were assigned "
            "external_same_context_concordant and a bounded computational replication "
            "ceiling; missing or unexecuted external claim states remained "
            "external_same_context_blocked."
        )
    else:
        external_abstract_sentence = ""
        stability_result_sentence = (
            "The same table records `no_cross_dataset_same_context` for all units, which "
            "is central to the current claim ceiling. The analysis can show method "
            "dependence and bounded stability, but it cannot present same-context "
            "cross-dataset support without additional evidence."
        )
        stability_boundary = (
            "Claim boundary: same-context cross-dataset replication is absent in the current evidence package."
        )
        discussion_external_sentence = (
            "Without same-context external evidence, the responder-state units should not "
            "be framed as cross-dataset replicated."
        )
        methods_external_sentence = (
            "Stability audit. Each responder-state unit was recalculated under leave-one-method "
            "omission and annotated for same-context cross-dataset availability. Units are "
            "classified as stable, method-sensitive, or PGAA-support dependent before any "
            "biological claim is written."
        )

    if real_event_ready:
        draft_status = (
            "This journal-style draft is generated from the current evidence chain and is "
            "not yet a submission-ready manuscript. The real-event readiness audit passes, "
            "so the draft includes a bounded public domain-transfer event-peptide benchmark; "
            "wet-lab presentation, synthetic-peptide, and T-cell validation claims remain blocked."
        )
        draft_status = (
            draft_status
            + " Recommended route: `stable_resistance_state_bifurcation`; the claim-state "
            "compiler stays as the governance layer, not the mainline biological route."
        )
        immune_heading = "### Public real-event evidence activates a bounded domain-transfer benchmark"
        immune_result = (
            "The event-peptide extension now contains real altered-sequence contexts, candidate "
            "peptides, public ligand and T-cell evidence, matched decoys, tier assignments, panel "
            "comparisons, and threshold-robustness outputs. These artifacts establish an auditable "
            "public-data domain-transfer benchmark, not a direct link between PGAA-ranked perturbation "
            "outputs and antigen evidence. Candidates separate from composition-shuffled and "
            "cross-event controls but not from same-context non-event windows. This mixed decoy "
            "sensitivity blocks a global enrichment claim and is retained as a central limitation. "
            "A same-cell GSE112274 pilot now connects EGFR T790M allele fraction with expression. "
            "PGAA-W detects an EGFR distributional association (2,000-permutation p=0.0005), whereas "
            "PGAA-H does not rank EGFR among its leading scores. This observational result is neither "
            "causal replication nor evidence of antigen presentation or T-cell recognition. An "
            "independent GSE129221 clone-level stress test does not reproduce a directionally "
            "invariant association: EGFR is lower in T790M-high CORTAD-seq cells but 1.31-fold "
            "higher in T790M-positive PC9GR replicates, with exact Wasserstein p=0.10. The compiler "
            "therefore retains this as a failed or unresolved cross-system state. A GSE75602 "
            "evolutionary stress test shows that early GR2 and late GR3 T790M-positive states both "
            "exceed parental EGFR expression, whereas late GR3 falls below the drug-tolerant "
            "precursor and early GR2. With two replicates per state and a minimum one-sided exact "
            "p=0.167, this supports comparator- and path-dependent modulation but does not rescue "
            "cross-system replication. A locked shift from the single marker to a distributed state "
            "program yields a positive external result: the GSE75602-derived 50-gene down-regulated "
            "resistance module transfers to GSE129221 with exact p=0.05 and 62% gene-direction "
            "concordance, with the same direction across all prespecified 10- to 200-gene modules. "
            "The up-regulated route is not size-robust, and source-group-adjusted CORTAD-seq transfer "
            "fails; the positive result is therefore a resistance-state program, not a T790M-specific "
            "mechanism."
        )
        immune_discussion = (
            "A real public event source now activates the peptide-evidence compiler as a bounded "
            "domain-transfer benchmark. Matched event-expression data are now connected in one "
            "observational pilot; an independent clone-level stress test is directionally discordant, "
            "and the stage-resolved evolution series indicates comparator-dependent modulation rather "
            "than a fixed T790M effect. A distributed down-regulated resistance-state module does "
            "transfer across the two clone-level systems, establishing a bounded positive result while "
            "T790M-specific replication and new wet-lab validation remain absent. The next decisive "
            "upgrade is a third independent PC9 evolution system tested with the module frozen."
        )
    else:
        draft_status = (
            "This journal-style draft is generated from the current evidence chain and is "
            "not yet a submission-ready manuscript. The readiness audit still blocks "
            "event-peptide, immune-presentation, synthetic-peptide, and T-cell function "
            "claims; the draft therefore positions PGAA as a claim-controlled benchmark "
            "compiler rather than as an immune-discovery workflow."
        )
        immune_heading = "### The event-peptide immune route remains a blocked extension"
        immune_result = (
            "The repository contains infrastructure for an event-peptide immune-evidence "
            "extension, but real event contexts and downstream evidence artifacts remain missing. "
            "This blocked state prevents gene-level perturbation outputs from being converted into "
            "molecular event claims by prose."
        )
        immune_discussion = (
            "Without real altered-sequence events, the immune extension remains infrastructure. "
            "The next decisive upgrade is a real event source that activates the peptide-evidence compiler."
        )

    lines = [
        "# PGAA Recharter Journal-Style Draft",
        "",
        "## Draft Status",
        "",
        draft_status,
        "",
        "## Title",
        "",
        (
            f"{payload['recommended_route_name']}: claim-state control in single-cell "
            "perturbation analysis"
        ),
        "",
        "## Abstract Draft",
        "",
        (
            "Single-cell perturbation analyses produce heterogeneous evidence, but standard "
            "benchmarking usually compresses that evidence into ranks or aggregate performance "
            "scores. This creates evidentiary inflation when descriptive shifts, restricted "
            "results, calibration failures, and method-sensitive findings are reported as if "
            "they licensed the same claim. Claim-state compilation controls evidentiary "
            "inflation by acting as a claim-controlled benchmark compiler rather than a "
            "score-only ranker. We reframe PGAA as a claim-state compiler that "
            "maps perturbation evidence to typed interpretation states and explicit claim "
            "ceilings. The current implementation converts "
            f"{payload['n_claim_rows']} benchmark and guardrail rows into explicit claim "
            f"states: {claim_counts.get('comparative_support', 0)} comparative-support, "
            f"{claim_counts.get('descriptive_only', 0)} descriptive-only, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows. "
            f"These rows define {payload['n_responder_units']} context-level responder-state "
            f"units, of which {payload['n_supported_units']} are supported and "
            f"{payload['n_provisional_units']} are provisional under the present evidence. "
            f"Leave-one-method analysis identifies {payload['n_stable_units']} stable units "
            f"and {payload['n_sensitive_units']} method-sensitive or PGAA-dependent units, "
            "thereby testing stability of the allowed interpretation rather than score "
            "stability alone. "
            f"{external_abstract_sentence}"
            f"{formal_abstract_sentence}"
            f"{promotion_abstract_sentence}"
            f"{generality_abstract_sentence}"
            f"{response_abstract_sentence}"
            f"{cross_platform_abstract_sentence}"
            "The resulting method object preserves support, restrictions, failures, typed "
            "replication states, and claim ceilings in one auditable representation. The "
            "contribution is not a new biological claim, but computational control over how "
            "evidence is translated into one."
        ),
        "",
        "## Introduction Draft",
        "",
        (
            "Perturbation-response methods are usually evaluated by whether they recover "
            "known targets or rank plausible genes highly. That convention is useful for "
            "benchmarking, but it does not solve a more basic reporting problem: methods "
            "produce outputs with different evidentiary meanings. Some rows support a "
            "bounded comparison, some describe a pattern without a decisive comparator, "
            "some expose a calibration limit, and some should be treated as failures for "
            "primary interpretation. Collapsing these states into a single ranking makes "
            "a method look cleaner than it is and makes manuscript claims difficult to audit."
        ),
        "",
        (
            "The rechartered PGAA analysis treats this translation problem as the method "
            "object. PGAA's distribution-aware scores enter a compiler that assigns each "
            "benchmark row to an allowed claim state, aggregates compatible rows into "
            "responder-state decision units, and types their replication status as concordant, "
            "discordant, unresolved, or blocked. The benchmark question therefore changes "
            "from whether one statistic wins to whether every result carries a defensible, "
            "stable, and auditable claim."
        ),
        "",
        "## Results Draft",
        "",
        "### A claim-state compiler turns heterogeneous evidence into typed manuscript decisions",
        "",
        (
            "We treated every benchmark and guardrail row as a typed evidence object with "
            "a source metric, an admissible interpretation, and an explicit claim ceiling. "
            "Compilation produced "
            f"{claim_counts.get('comparative_support', 0)} comparative-support rows, "
            f"{claim_counts.get('descriptive_only', 0)} descriptive-only rows, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support rows, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use rows, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows. "
            "Rather than maximizing the apparent positive fraction, the compiler preserves "
            "restricted and failed rows as first-class outputs. Because the claim ceiling "
            "travels with the originating evidence row into figures and prose, a descriptive "
            "shift cannot silently become comparative support and a computationally concordant "
            "state cannot silently become biological validation. This evidence-to-claim "
            "translation, rather than rank production alone, defines the rechartered method."
        ),
        "",
        "Evidence source: `evidence/result_claim_states.tsv`.",
        "",
        "Claim boundary: descriptive, restricted, calibration, and failure-or-guardrail rows cannot support a broad method-superiority claim.",
        "",
        formal_results,
        "" if formal_results else "",
        promotion_results,
        "" if promotion_results else "",
        generality_results,
        "" if generality_results else "",
        response_results,
        "" if response_results else "",
        cross_platform_results,
        "" if cross_platform_results else "",
        "### Responder-state units turn row-level scores into decision objects",
        "",
        (
            "Decision-benchmark rows are then collapsed by biological or perturbation context "
            f"into {payload['n_responder_units']} responder-state units. Supported units occur "
            f"in {supported_contexts}; provisional units occur in {provisional_contexts}. "
            f"Primary metric values span {payload['min_primary_metric']:.3f} to "
            f"{payload['max_primary_metric']:.3f}. This aggregation makes the manuscript "
            "unit match the decision unit: a context can be supported, provisional, or "
            "restricted depending on how many methods support it and how much failure "
            "evidence travels with it."
        ),
        "",
        "Evidence source: `evidence/responder_state_units.tsv`.",
        "",
        "Claim boundary: provisional units are responder-state hypotheses, not replicated responder states.",
        "",
        "### Stability gates identify which units depend on method choice",
        "",
        (
            "We next asked whether each responder-state unit survives leave-one-method "
            f"omission. Stable units occur in {stable_contexts}; method-sensitive or "
            f"PGAA-dependent units occur in {sensitive_contexts}. {stability_result_sentence}"
        ),
        "",
        "Evidence source: `evidence/responder_state_stability_summary.tsv` and `evidence/external_responder_state_stability_summary.tsv`.",
        "",
        stability_boundary,
        "",
        "### A source-driven figure makes the claim-control object inspectable",
        "",
        (
            "The main figure is built from a 27-row source table that combines claim-state "
            "counts, responder-state units, internal stability, and typed external states. "
            "It functions as an executable decision object rather than a workflow schematic: "
            "each visual mark traces to a generated evidence row, and each row carries the "
            "interpretive ceiling used by the manuscript."
        ),
        "",
        "Evidence source: `evidence/main_figure_source_data.tsv` and `figures_png/figure1_recharter_decision_object.png`.",
        "",
        "Claim boundary: Figure 1 is a benchmark and claim-control figure, not evidence of wet-lab validation or immune presentation.",
        "",
        immune_heading,
        "",
        immune_result,
        "",
        "Evidence source: `docs/RECHARTER_READINESS_AUDIT.md`, "
        "`docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md`, and "
        "`evidence/threshold_robustness_summary.tsv`.",
        "",
        "Claim boundary: do not claim event-peptide presentation, synthetic-peptide wet-lab confirmation, or T-cell function.",
        "",
        "## Discussion Draft",
        "",
        (
            "The rechartered method addresses a general failure mode in computational biology: "
            "evidence types are often heterogeneous when generated but homogeneous when narrated. "
            "By compiling scores, restrictions, failures, stability results, and external states "
            "into typed claim objects, PGAA makes evidentiary inflation measurable and testable. "
            "This shifts the contribution from another perturbation score to a computational "
            "governance layer for evidence-to-claim translation."
        ),
        "",
        (
            f"The limitation is also explicit. {discussion_external_sentence} "
            "The locked generality panel further shows that "
            "strong direct target recovery is shared by simple baselines, so it cannot be "
            "used as a PGAA superiority argument. The held-out response analysis adds a more "
            "general warning: reproducible rankings can arise from stable null distributional "
            f"properties unless a matched pseudo-perturbation gate is applied. {immune_discussion}"
        ),
        "",
        "## Methods Draft",
        "",
        (
            "Failure-mode and claim-state compilation. Calibration, parameter-sensitivity, "
            "Norman, and Adamson benchmark outputs were first converted into failure-mode "
            "states and then into manuscript-facing claim states. Each row retains its source, "
            "metric, allowed interpretation, and figure-panel assignment."
        ),
        "",
        (
            "Responder-state aggregation. Decision-benchmark rows were grouped by context. "
            "For each context, the compiler records the primary method, primary metric, "
            "supporting methods, descriptive methods, failure/guardrail methods, and allowed "
            "manuscript use."
        ),
        "",
        methods_external_sentence,
        "",
        formal_methods_sentence,
        "" if formal_methods_sentence else "",
        promotion_methods_sentence,
        "" if promotion_methods_sentence else "",
        generality_methods_sentence,
        "" if generality_methods_sentence else "",
        response_methods_sentence,
        "" if response_methods_sentence else "",
        cross_platform_methods_sentence,
        "" if cross_platform_methods_sentence else "",
        (
            "Figure, text, and claim audit. Figure 1, this draft, and the claim-safety report "
            "are generated from source tables and readiness audits. The manuscript audit scans "
            "required evidence references, blocked-evidence disclosure, boundary language, and "
            "unsupported phrases before style revision."
        ),
        "",
        "## Current Worklist State",
        "",
        novelty_provenance,
        "" if novelty_provenance else "",
        f"Benchmark matrix rows: {payload['n_benchmark_rows']}.",
        "",
        "| Status | Rows |",
        "|---|---:|",
    ]
    for status, count in sorted(matrix_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(
        [
            "",
            "## Still-Blocked Evidence",
            "",
            "| Missing item | Artifact | Detail |",
            "|---|---|---|",
        ]
    )
    for row in blocked_evidence:
        lines.append(f"| {row['check_id']} | `{row['artifact']}` | {row['detail']} |")
    lines.extend(
        [
            "",
            "## Forbidden Phrases For This Draft",
            "",
            "- validated antigen",
            "- immunogenic peptide validated by T cells",
            "- same-context replicated responder state",
            "- experimentally confirmed presentation",
            "- synthetic peptide validation",
            "- validated T-cell function",
            "",
        ]
    )
    return "\n".join(lines)


def build_and_render_recharter_journal_style_draft(
    route_scores: pd.DataFrame,
    benchmark_matrix: pd.DataFrame,
    figure_sources: pd.DataFrame,
    readiness_audit: pd.DataFrame,
    claim_states: pd.DataFrame,
    responder_units: pd.DataFrame,
    stability_summary: pd.DataFrame,
    external_stability_summary: pd.DataFrame | None = None,
    novelty_upgrades: pd.DataFrame | None = None,
    formal_invariant_audit: pd.DataFrame | None = None,
    promotion_benchmark_summary: pd.DataFrame | None = None,
    generality_summary: pd.DataFrame | None = None,
    generality_baseline_summary: pd.DataFrame | None = None,
    response_replication_summary: pd.DataFrame | None = None,
    response_specificity_summary: pd.DataFrame | None = None,
    cross_platform_gates: pd.DataFrame | None = None,
    cross_platform_sensitivity: pd.DataFrame | None = None,
) -> str:
    """Build and render the journal-style claim-bounded manuscript draft."""
    payload = build_recharter_manuscript_payload(
        route_scores,
        benchmark_matrix,
        figure_sources,
        readiness_audit,
        claim_states,
        responder_units,
        stability_summary,
        external_stability_summary,
    )
    if novelty_upgrades is not None:
        missing = sorted(REQUIRED_NOVELTY_COLUMNS - set(novelty_upgrades.columns))
        if missing:
            raise ValueError(f"novelty upgrade map is missing columns: {missing}")
        payload["n_novelty_upgrades"] = int(len(novelty_upgrades))
        payload["n_tier1_novelty_upgrades"] = int(
            (novelty_upgrades["priority_tier"] == "tier1_core_thesis").sum()
        )
    if formal_invariant_audit is not None:
        missing = sorted(REQUIRED_FORMAL_AUDIT_COLUMNS - set(formal_invariant_audit.columns))
        if missing:
            raise ValueError(f"formal invariant audit is missing columns: {missing}")
        payload["n_formal_invariants"] = int(len(formal_invariant_audit))
        payload["n_formal_invariants_passed"] = int(
            (formal_invariant_audit["status"] == "pass").sum()
        )
        payload["n_formal_invariant_violations"] = int(
            pd.to_numeric(formal_invariant_audit["n_violations"], errors="coerce")
            .fillna(0)
            .sum()
        )
    if promotion_benchmark_summary is not None:
        missing = sorted(
            REQUIRED_PROMOTION_BENCHMARK_COLUMNS
            - set(promotion_benchmark_summary.columns)
        )
        if missing:
            raise ValueError(f"promotion benchmark summary is missing columns: {missing}")
        overall = promotion_benchmark_summary[
            promotion_benchmark_summary["scope"] == "all_scenarios"
        ].set_index("method")
        required_methods = {
            "claim_state_compiler",
            "state_blind_frozen_baseline",
            "decision_only_baseline",
            "external_only_baseline",
        }
        missing_methods = sorted(required_methods - set(overall.index))
        if missing_methods:
            raise ValueError(
                f"promotion benchmark summary is missing methods: {missing_methods}"
            )
        payload["n_promotion_scenarios"] = int(
            overall.loc["claim_state_compiler", "n_scenarios"]
        )
        payload["compiler_false_promotion_rate"] = float(
            overall.loc["claim_state_compiler", "false_promotion_rate"]
        )
        payload["frozen_false_promotion_rate"] = float(
            overall.loc["state_blind_frozen_baseline", "false_promotion_rate"]
        )
        payload["external_false_promotion_rate"] = float(
            overall.loc["external_only_baseline", "false_promotion_rate"]
        )
        payload["decision_replication_sensitivity"] = float(
            overall.loc["decision_only_baseline", "replication_sensitivity"]
        )
    if generality_summary is not None:
        indexed = generality_summary.set_index("metric")
        payload["n_generality_targets"] = int(indexed.loc["execution_complete", "n_locked_targets"])
        payload["n_generality_complete"] = int(indexed.loc["execution_complete", "n_success"])
        payload["n_generality_w_top10"] = int(indexed.loc["pgaa_w_top10pct", "n_success"])
        payload["n_generality_h_top10"] = int(indexed.loc["pgaa_h_top10pct", "n_success"])
    if generality_baseline_summary is not None:
        indexed = generality_baseline_summary.set_index("metric")
        payload["n_mean_shift_top10"] = int(indexed.loc["absolute_mean_shift_top10pct", "n_targets"])
        payload["n_welch_top10"] = int(indexed.loc["welch_abs_t_top10pct", "n_targets"])
    if response_replication_summary is not None and response_specificity_summary is not None:
        replication = response_replication_summary.set_index("method")
        specificity = response_specificity_summary.set_index("method")
        required_methods = {"pgaa_w", "pgaa_h", "absolute_mean_shift", "welch_abs_t"}
        missing_methods = sorted(
            required_methods - set(replication.index) | required_methods - set(specificity.index)
        )
        if missing_methods:
            raise ValueError(f"response summaries are missing methods: {missing_methods}")
        payload["has_response_replication"] = True
        payload["response_w_overlap"] = float(
            replication.loc["pgaa_w", "median_top_k_overlap_fraction"]
        )
        payload["response_h_overlap"] = float(
            replication.loc["pgaa_h", "median_top_k_overlap_fraction"]
        )
        payload["response_mean_overlap"] = float(
            replication.loc["absolute_mean_shift", "median_top_k_overlap_fraction"]
        )
        payload["response_w_pseudo_overlap"] = float(
            specificity.loc["pgaa_w", "median_pseudo_top_k_overlap_fraction"]
        )
        payload["response_w_specificity_margin"] = float(
            specificity.loc["pgaa_w", "median_specificity_margin"]
        )
        payload["response_w_specificity_holm_p"] = float(
            specificity.loc["pgaa_w", "holm_adjusted_p"]
        )
        payload["response_h_specificity_margin"] = float(
            specificity.loc["pgaa_h", "median_specificity_margin"]
        )
        payload["response_h_specificity_holm_p"] = float(
            specificity.loc["pgaa_h", "holm_adjusted_p"]
        )
    if cross_platform_gates is not None and cross_platform_sensitivity is not None:
        required_gate_columns = {
            "dataset_id",
            "method",
            "dual_gate_state",
        }
        required_sensitivity_columns = {
            "method",
            "stability_threshold",
            "cross_platform_interpretation",
        }
        missing_gates = sorted(required_gate_columns - set(cross_platform_gates.columns))
        missing_sensitivity = sorted(
            required_sensitivity_columns - set(cross_platform_sensitivity.columns)
        )
        if missing_gates or missing_sensitivity:
            raise ValueError(
                "cross-platform evidence is missing columns: "
                f"gates={missing_gates}, sensitivity={missing_sensitivity}"
            )
        synthesis = synthesize_cross_platform_gates(cross_platform_gates)
        payload["has_cross_platform_dual_gate"] = True
        payload["n_cross_platforms"] = int(
            cross_platform_gates["dataset_id"].nunique()
        )
        payload["cross_platform_recurrent_methods"] = synthesis.loc[
            synthesis["cross_platform_interpretation"].eq(
                "recurrent_stability_specificity_decoupling"
            ),
            "method",
        ].astype(str).tolist()
        threshold_counts = cross_platform_sensitivity.groupby("method")[
            "stability_threshold"
        ].nunique()
        recurrent_counts = cross_platform_sensitivity[
            cross_platform_sensitivity["cross_platform_interpretation"].eq(
                "recurrent_stability_specificity_decoupling"
            )
        ].groupby("method")["stability_threshold"].nunique()
        payload["cross_platform_threshold_robust_methods"] = sorted(
            method for method in threshold_counts.index
            if recurrent_counts.get(method, 0) == threshold_counts[method]
        )
        recurrence_limits = []
        for method in payload["cross_platform_recurrent_methods"]:
            current = cross_platform_sensitivity[
                cross_platform_sensitivity["method"].eq(method)
                & cross_platform_sensitivity["cross_platform_interpretation"].eq(
                    "recurrent_stability_specificity_decoupling"
                )
            ]
            if not current.empty:
                recurrence_limits.append(
                    f"`{method}` through {current['stability_threshold'].max():.2f}"
                )
        payload["cross_platform_recurrence_limits"] = recurrence_limits
        leave_one_out = evaluate_platform_leave_one_out(cross_platform_gates)
        payload["cross_platform_leave_one_out_robust_methods"] = sorted(
            method
            for method, current in leave_one_out.groupby("method")
            if current["recurrence_survives_omission"].all()
        )
        payload["cross_platform_state_descriptions"] = [
            f"{dataset}: "
            + ", ".join(
                f"{row.method}={row.dual_gate_state}"
                for row in current.sort_values("method").itertuples()
            )
            for dataset, current in cross_platform_gates.groupby("dataset_id", sort=True)
        ]
    return render_recharter_journal_style_draft(payload)
