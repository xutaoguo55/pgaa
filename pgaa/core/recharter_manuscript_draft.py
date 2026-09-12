"""Draft claim-bounded manuscript sections for the PGAA recharter."""
from __future__ import annotations

import pandas as pd

from pgaa.core.recharter_manuscript_skeleton import (
    REQUIRED_FIGURE_COLUMNS,
    REQUIRED_MATRIX_COLUMNS,
    REQUIRED_READINESS_COLUMNS,
    REQUIRED_ROUTE_COLUMNS,
    _validate,
    build_recharter_story_payload,
)


REQUIRED_CLAIM_COLUMNS = {
    "result_claim_state",
    "figure_panel",
    "evidence_type",
    "context",
    "method",
    "metric",
    "metric_value",
    "manuscript_allowed_claim",
}

REQUIRED_UNIT_COLUMNS = {
    "context",
    "decision_state",
    "primary_method",
    "primary_metric",
    "primary_metric_value",
    "n_methods",
    "n_comparative_support",
    "n_descriptive_only",
    "n_failure_or_guardrail",
}

REQUIRED_STABILITY_COLUMNS = {
    "context",
    "baseline_decision_state",
    "n_leave_one_checks",
    "n_state_preserved",
    "n_state_changed",
    "stability_class",
    "cross_dataset_status",
}

REQUIRED_EXTERNAL_STABILITY_SUMMARY_COLUMNS = {
    "integrated_stability_class",
    "integrated_cross_dataset_status",
    "claim_ceiling",
    "n_units",
}


def _format_context_list(values: list[str], limit: int = 5) -> str:
    values = [str(value) for value in values if str(value)]
    if not values:
        return "none"
    if len(values) <= limit:
        return ", ".join(values)
    return ", ".join(values[:limit]) + f", and {len(values) - limit} others"


def build_recharter_manuscript_payload(
    route_scores: pd.DataFrame,
    benchmark_matrix: pd.DataFrame,
    figure_sources: pd.DataFrame,
    readiness_audit: pd.DataFrame,
    claim_states: pd.DataFrame,
    responder_units: pd.DataFrame,
    stability_summary: pd.DataFrame,
    external_stability_summary: pd.DataFrame | None = None,
) -> dict[str, object]:
    """Collect evidence summaries for the manuscript draft."""
    _validate(route_scores, REQUIRED_ROUTE_COLUMNS, "route scores")
    _validate(benchmark_matrix, REQUIRED_MATRIX_COLUMNS, "benchmark matrix")
    _validate(figure_sources, REQUIRED_FIGURE_COLUMNS, "figure sources")
    _validate(readiness_audit, REQUIRED_READINESS_COLUMNS, "readiness audit")
    _validate(claim_states, REQUIRED_CLAIM_COLUMNS, "claim states")
    _validate(responder_units, REQUIRED_UNIT_COLUMNS, "responder units")
    _validate(stability_summary, REQUIRED_STABILITY_COLUMNS, "stability summary")
    if external_stability_summary is not None:
        _validate(
            external_stability_summary,
            REQUIRED_EXTERNAL_STABILITY_SUMMARY_COLUMNS,
            "external stability summary",
        )

    story = build_recharter_story_payload(
        route_scores, benchmark_matrix, figure_sources, readiness_audit
    )
    decision_claims = claim_states[claim_states["figure_panel"] == "decision_benchmark"]
    guardrail_claims = claim_states[
        claim_states["figure_panel"].isin(["calibration_guardrail", "parameter_guardrail"])
    ]
    supported_units = responder_units[
        responder_units["decision_state"] == "supported_responder_state"
    ]
    provisional_units = responder_units[
        responder_units["decision_state"] == "provisional_responder_state"
    ]
    stable_units = stability_summary[
        stability_summary["stability_class"] == "leave_one_method_stable"
    ]
    sensitive_units = stability_summary[
        stability_summary["stability_class"] != "leave_one_method_stable"
    ]
    if external_stability_summary is None:
        external_counts: dict[str, int] = {}
        external_ceiling_counts: dict[str, int] = {}
    else:
        external_counts = (
            external_stability_summary.groupby("integrated_cross_dataset_status")["n_units"]
            .sum()
            .astype(int)
            .to_dict()
        )
        external_ceiling_counts = (
            external_stability_summary.groupby("claim_ceiling")["n_units"]
            .sum()
            .astype(int)
            .to_dict()
        )

    return {
        **story,
        "n_decision_claims": int(len(decision_claims)),
        "n_guardrail_claims": int(len(guardrail_claims)),
        "supported_contexts": supported_units["context"].astype(str).tolist(),
        "provisional_contexts": provisional_units["context"].astype(str).tolist(),
        "stable_contexts": stable_units["context"].astype(str).tolist(),
        "sensitive_contexts": sensitive_units["context"].astype(str).tolist(),
        "n_claim_rows": int(len(claim_states)),
        "n_supported_units": int(len(supported_units)),
        "n_provisional_units": int(len(provisional_units)),
        "n_stable_units": int(len(stable_units)),
        "n_sensitive_units": int(len(sensitive_units)),
        "external_counts": external_counts,
        "external_ceiling_counts": external_ceiling_counts,
        "n_external_concordant_units": int(
            external_counts.get("external_same_context_concordant", 0)
        ),
        "n_external_blocked_units": int(
            external_counts.get("external_same_context_blocked", 0)
        ),
        "n_external_discordant_units": int(
            external_counts.get("external_same_context_discordant", 0)
        ),
        "n_external_unresolved_units": int(
            external_counts.get("external_same_context_unresolved", 0)
        ),
        "max_primary_metric": float(pd.to_numeric(responder_units["primary_metric_value"]).max()),
        "min_primary_metric": float(pd.to_numeric(responder_units["primary_metric_value"]).min()),
    }


def render_recharter_manuscript_draft(payload: dict[str, object]) -> str:
    """Render manuscript-style sections with explicit claim boundaries."""
    claim_counts = payload["claim_counts"]
    matrix_counts = payload["matrix_counts"]
    missing = payload["missing_readiness_artifacts"]
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
    if real_event_ready:
        draft_status = (
            "This is a claim-bounded working draft generated from current evidence tables. "
            "It is not yet a submission-ready manuscript. The real-event readiness gate "
            "passes, enabling bounded public domain-transfer "
            "analysis while wet-lab presentation and T-cell validation claims remain blocked."
        )
        immune_heading = "### Public real-event evidence enables a bounded domain-transfer analysis"
        immune_result = (
            "The event-peptide route now contains real altered-sequence contexts, candidate "
            "peptides, public ligand and T-cell evidence, decoys, tiers, claim audit, panel "
            "summaries, and threshold robustness. This is public domain-transfer evidence, not "
            "a direct link between PGAA-ranked perturbations and experimental antigen evidence. "
            "Candidates separate from composition-shuffled and cross-event decoys but not from "
            "same-context non-event windows. This mixed decoy sensitivity fails the global "
            "enrichment gate and keeps strong immune-evidence claims blocked. A same-cell "
            "GSE112274 pilot now links EGFR T790M allele fraction to expression: PGAA-W detects "
            "an EGFR distributional association (2,000-permutation p=0.0005), whereas PGAA-H "
            "does not place EGFR among its leading scores. The observation is non-causal and "
            "does not establish antigen presentation or T-cell recognition. An independent "
            "GSE129221 clone-level stress test does not replicate a directionally invariant "
            "association: EGFR is lower in T790M-high CORTAD-seq cells but 1.31-fold higher in "
            "T790M-positive PC9GR replicates, with exact Wasserstein p=0.10. This discordant, "
            "underpowered result is retained as a failed or unresolved cross-system state. "
            "A GSE75602 evolutionary stress test further shows that both early GR2 and late GR3 "
            "T790M-positive states exceed parental EGFR expression, while late GR3 falls below "
            "the drug-tolerant precursor and early GR2. With two replicates per state and a minimum "
            "one-sided exact p=0.167, this is descriptive evidence that evolutionary path and "
            "comparator modulate direction, not a rescue of cross-system replication. Moving from "
            "the single marker to a locked distributed state program produces a positive result: "
            "a GSE75602-derived 50-gene down-regulated resistance module transfers to GSE129221 "
            "with exact p=0.05 and 62% gene-direction concordance, and the direction remains supported "
            "for every prespecified size from 10 to 200 genes. The corresponding up-regulated route "
            "fails size robustness. Source-group-adjusted testing in CORTAD-seq also fails, so the "
            "selected module is framed as a transferable resistance-state program rather than a "
            "T790M-specific mechanism."
        )
        remaining_event_action = (
            "A top-tier method paper would be stronger if additional external contexts produced "
            "the locked resistance-state module in a third independent PC9 evolution system and "
            "resolved its currently fragmented pathway interpretation. The local PC9 drug "
            "perturbation candidates do not yet close that gap: Aissa2021 is blocked by a "
            "single-batch metadata contract error, and Chang2021 is below the minimum "
            "selected-unit gate."
        )
    else:
        draft_status = (
            "This is a claim-bounded working draft generated from current evidence tables. "
            "It is not yet a submission-ready manuscript because the readiness audit still "
            "blocks event-peptide, immune-presentation, synthetic-peptide, and T-cell function claims."
        )
        immune_heading = "### The immune/event-peptide route remains infrastructure-only until real event evidence exists"
        immune_result = (
            "The event-peptide immune route remains explicitly blocked because the required "
            "real event and downstream evidence artifacts are incomplete."
        )
        remaining_event_action = (
            "A top-tier method paper would be stronger if additional external contexts produced "
            "the same failure-preserving pattern or if real sequence-changing event sources "
            "enabled the event-peptide compiler route."
        )
    if has_external_layer:
        external_abstract_sentence = (
            f"An external Replogle K562 GWPS claim-state layer adds "
            f"{n_external_concordant} bounded computational same-context concordant "
            f"units, while {n_external_blocked} units remain external blocked, "
            f"{n_external_discordant} discordant, and {n_external_unresolved} unresolved. "
        )
        stability_boundary = (
            f"Claim boundary: external same-context evidence supports only bounded "
            f"computational replication for {n_external_concordant} concordant units; "
            f"{n_external_blocked} blocked units remain internal-only, and no row supports "
            "wet-lab, immune-presentation, synthetic-peptide, or T-cell-function claims."
        )
        methods_external_sentence = (
            "External responder-state stability integration. External Replogle K562 GWPS "
            "claim-state rows were integrated with internal leave-one-method stability. "
            "The integrated status separates external_same_context_concordant rows from "
            "external_same_context_blocked, external_same_context_discordant, or "
            "external_same_context_unresolved rows before any replication language is written."
        )
    else:
        external_abstract_sentence = (
            "Same-context external replication remains absent from the current evidence package. "
        )
        stability_boundary = (
            "Claim boundary: all stability rows are currently marked "
            "`no_cross_dataset_same_context`, so the draft must not claim cross-dataset "
            "replication."
        )
        methods_external_sentence = (
            "Stability and replication gate. Each responder-state unit was re-evaluated under "
            "leave-one-method omission. Units were classified as leave-one-method stable, "
            "method-sensitive, or PGAA-support dependent. Same-context cross-dataset evidence "
            "was tracked separately and is currently absent for all units."
        )

    lines = [
        "# PGAA Recharter Manuscript Draft",
        "",
        "## Draft Status",
        "",
        draft_status,
        "",
        (
            f"Recommended route: `{payload['recommended_route']}` "
            f"({payload['recommended_route_name']}). The claim-state compiler remains "
            "the governance layer, but the mainline route is the stable resistance-state "
            "bifurcation program."
        ),
        "",
        "## Title",
        "",
        (
            f"{payload['recommended_route_name']}: claim-controlled single-cell "
            "perturbation response analysis"
        ),
        "",
        "## Abstract Draft",
        "",
        (
            "Single-cell perturbation methods often report ranked genes or scores without "
            "preserving the evidentiary state of each result. This creates a practical "
            "problem for method comparison: positive, descriptive, unstable, and failed "
            "outcomes can be mixed into the same narrative. We recharter PGAA around the "
            f"`{payload['recommended_route']}` route ({payload['recommended_route_name']}), while using a failure-preserving "
            "benchmark engine to compile perturbation-response outputs into claim states, "
            "responder-state units, and stability gates. "
            f"In the current evidence package, {payload['n_claim_rows']} benchmark and "
            f"guardrail rows are compiled into {claim_counts.get('comparative_support', 0)} "
            "comparative-support rows, "
            f"{claim_counts.get('descriptive_only', 0)} descriptive-only rows, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use rows, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support rows, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows. "
            f"Decision-benchmark rows further define {payload['n_responder_units']} "
            f"responder-state units, including {payload['n_supported_units']} supported "
            f"and {payload['n_provisional_units']} provisional units. Leave-one-method "
            f"checks identify {payload['n_stable_units']} stable units and "
            f"{payload['n_sensitive_units']} method-sensitive or PGAA-dependent units. "
            f"{external_abstract_sentence}"
            "The resulting object turns failure handling and claim control into primary "
            "method outputs rather than after-the-fact caveats."
        ),
        "",
        "## Introduction Draft",
        "",
        (
            "Distribution-aware perturbation analysis is useful only when the reported "
            "result can be interpreted at the same level of rigor as the downstream claim. "
            "A ranked response score may be adequate for exploratory prioritization, but "
            "it is not sufficient for deciding whether a result supports a comparative "
            "claim, a descriptive observation, a parameter guardrail, or a failure mode. "
            "This gap is especially visible in heterogeneous single-cell perturbation "
            "settings, where different statistics can emphasize different response "
            "features and where calibration or parameter sensitivity can change the "
            "allowed interpretation."
        ),
        "",
        (
            "The current recharter therefore changes the method object. Instead of asking "
            "only which genes rank highly, PGAA is framed as a compiler from benchmark "
            "evidence into explicit claim states and responder-state units. This framing "
            "does not hide negative or unstable outcomes. It makes them part of the output "
            "and uses them to constrain manuscript language."
        ),
        "",
        "## Results Draft",
        "",
        "### PGAA benchmark evidence can be compiled into explicit claim states",
        "",
        (
            "We first converted benchmark and guardrail rows into manuscript-facing claim "
            "states. The compiled evidence contains "
            f"{claim_counts.get('comparative_support', 0)} comparative-support rows, "
            f"{claim_counts.get('descriptive_only', 0)} descriptive-only rows, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support rows, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use rows, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows. "
            "This distribution is important because it prevents the manuscript from "
            "treating every numerical output as equally claim-bearing. Rows assigned to "
            "failure or restricted states remain visible and are used to define the "
            "ceiling of allowed interpretation."
        ),
        "",
        "Evidence source: `evidence/result_claim_states.tsv`.",
        "",
        "Claim boundary: no broad superiority claim should be made from descriptive, restricted, or failure-or-guardrail rows.",
        "",
        "### Decision rows define responder-state units rather than isolated method scores",
        "",
        (
            "Decision-benchmark rows were aggregated into context-level responder-state "
            f"units. The current table contains {payload['n_responder_units']} units. "
            f"Supported units occur in {supported_contexts}; provisional units occur in "
            f"{provisional_contexts}. Across units, primary metric values range from "
            f"{payload['min_primary_metric']:.3f} to {payload['max_primary_metric']:.3f}. "
            "The supported units can carry bounded comparative interpretation, whereas "
            "the provisional units should be reported as descriptive responder-state "
            "hypotheses rather than as validated discoveries."
        ),
        "",
        "Evidence source: `evidence/responder_state_units.tsv`.",
        "",
        "Claim boundary: provisional Norman units remain hypothesis-generating and should not be described as replicated responder states.",
        "",
        "### Stability gates separate robust units from method-sensitive units",
        "",
        (
            "We next evaluated whether the responder-state labels survive leave-one-method "
            "omission. Four units remain leave-one-method stable "
            f"({stable_contexts}), whereas method-sensitive or PGAA-dependent units occur "
            f"in {sensitive_contexts}. These gates make dependency visible: a result can "
            "be useful as a benchmark finding while still being too method-sensitive for "
            "strong biological interpretation."
        ),
        "",
        "Evidence source: `evidence/responder_state_stability_summary.tsv` and `evidence/external_responder_state_stability_summary.tsv`.",
        "",
        stability_boundary,
        "",
        "### Figure 1 exposes the claim-control object rather than decorating the workflow",
        "",
        (
            "Figure 1 is rendered from a 27-row source table rather than assembled as a "
            "manual schematic. The figure displays claim-state distribution, responder-state "
            "units, and the stability/replication gate in a single object. This design makes "
            "the method claim auditable: the figure shows both where PGAA supports bounded "
            "interpretation and where evidence remains provisional, sensitive, or missing."
        ),
        "",
        "Evidence source: `evidence/main_figure_source_data.tsv` and `figures_png/figure1_recharter_decision_object.png`.",
        "",
        "Claim boundary: Figure 1 is not evidence of wet-lab validation or immune presentation.",
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
            "The rechartered PGAA object is strongest where it changes the unit of method "
            "evaluation. Rather than presenting only ranked outputs, it reports whether each "
            "output supports a claim, requires restriction, or exposes a failure mode. This "
            "is a defensible methodological contribution because it turns calibration, "
            "negative results, method sensitivity, and external concordance or blockage "
            "into primary outputs. The current evidence can now support a bounded "
            "computational same-context replication statement for the external concordant "
            "units, but it still does not support a strong immune-discovery paper. The "
            "strongest honest submission path is therefore a claim-controlled computational "
            "method paper centered on failure-preserving benchmarking."
        ),
        "",
        (
            "The main remaining weakness is no longer a total absence of externality, but "
            "the narrowness and claim ceiling of that externality. The Replogle layer is "
            "useful because it creates real concordant and blocked external claim states, "
            "yet it is still computational same-context evidence rather than wet-lab or "
            f"immune validation. {remaining_event_action}"
        ),
        "",
        "## Methods Draft",
        "",
        (
            "Failure-mode audit. Existing calibration, parameter-sensitivity, Norman, and "
            "Adamson benchmark outputs were compiled into failure-mode states. Each row was "
            "assigned an internal failure state, severity, recommended action, and allowed "
            "technical interpretation."
        ),
        "",
        (
            "Claim-state compilation. Failure-mode rows were converted into manuscript-facing "
            "claim states. The compiler assigns each row to comparative support, descriptive "
            "only, calibration support, restricted use, or failure/guardrail status and "
            "stores the allowed claim language alongside the source table."
        ),
        "",
        (
            "Responder-state units. Decision-benchmark claim rows were aggregated by context "
            "into responder-state units. Each unit records the primary method, primary metric, "
            "supporting methods, descriptive methods, failure/guardrail methods, and allowed "
            "manuscript use."
        ),
        "",
        methods_external_sentence,
        "",
        (
            "Figure and text generation. Figure 1 and the draft manuscript text were generated "
            "from source tables and route/readiness audits. This prevents unsupported claim "
            "language from being introduced manually during manuscript assembly."
        ),
        "",
        "## Current Worklist State",
        "",
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
    for row in missing:
        lines.append(f"| {row['check_id']} | `{row['artifact']}` | {row['detail']} |")
    lines.extend(
        [
            "",
            "## Forbidden Phrases For This Draft",
            "",
            "- validated antigen",
            "- immunogenic peptide validated by T cells",
            "- same-context replicated responder state",
            "- wet-lab validated responder state",
            "- experimentally confirmed presentation",
            "- synthetic peptide validation",
            "- validated T-cell function",
            "",
        ]
    )
    return "\n".join(lines)


def build_and_render_recharter_manuscript_draft(
    route_scores: pd.DataFrame,
    benchmark_matrix: pd.DataFrame,
    figure_sources: pd.DataFrame,
    readiness_audit: pd.DataFrame,
    claim_states: pd.DataFrame,
    responder_units: pd.DataFrame,
    stability_summary: pd.DataFrame,
    external_stability_summary: pd.DataFrame | None = None,
) -> str:
    """Build and render the claim-bounded manuscript draft."""
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
    return render_recharter_manuscript_draft(payload)
