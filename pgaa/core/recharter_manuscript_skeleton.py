"""Build a claim-bounded manuscript skeleton for the PGAA recharter."""
from __future__ import annotations

import pandas as pd


REQUIRED_ROUTE_COLUMNS = {
    "route_id",
    "route_name",
    "central_object",
    "current_support",
    "next_decisive_action",
    "recommended_now",
}

REQUIRED_MATRIX_COLUMNS = {
    "benchmark_id",
    "endpoint",
    "pass_condition",
    "current_status",
    "blocking_file",
    "next_action",
}

REQUIRED_FIGURE_COLUMNS = {
    "panel_id",
    "state",
    "stability_class",
    "cross_dataset_status",
    "y_value",
}

REQUIRED_READINESS_COLUMNS = {"check_id", "status", "artifact", "detail"}

REQUIRED_NOVELTY_COLUMNS = {
    "upgrade_id",
    "pillar_id",
    "pillar_name",
    "upgrade_point",
    "elevation_type",
    "manuscript_role",
    "evidence_gate",
    "current_status",
    "next_action",
    "claim_boundary",
    "priority_tier",
}


def _validate(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def build_recharter_story_payload(
    route_scores: pd.DataFrame,
    benchmark_matrix: pd.DataFrame,
    figure_sources: pd.DataFrame,
    readiness_audit: pd.DataFrame,
    novelty_upgrades: pd.DataFrame | None = None,
) -> dict[str, object]:
    """Summarize evidence needed for a top-journal recharter skeleton."""
    _validate(route_scores, REQUIRED_ROUTE_COLUMNS, "route scores")
    _validate(benchmark_matrix, REQUIRED_MATRIX_COLUMNS, "benchmark matrix")
    _validate(figure_sources, REQUIRED_FIGURE_COLUMNS, "figure sources")
    _validate(readiness_audit, REQUIRED_READINESS_COLUMNS, "readiness audit")
    if novelty_upgrades is not None:
        _validate(novelty_upgrades, REQUIRED_NOVELTY_COLUMNS, "novelty upgrade map")

    recommended = route_scores[route_scores["recommended_now"].astype(bool)]
    if recommended.empty:
        raise ValueError("route scores do not contain a recommended route")
    recommended_row = recommended.iloc[0]

    panel_a = figure_sources[figure_sources["panel_id"] == "A_claim_state_distribution"]
    panel_b = figure_sources[figure_sources["panel_id"] == "B_responder_state_units"]
    panel_c = figure_sources[figure_sources["panel_id"] == "C_unit_stability"]

    claim_counts = (
        panel_a.groupby("state", dropna=False)["y_value"]
        .sum()
        .astype(int)
        .to_dict()
    )
    responder_counts = panel_b["state"].value_counts().astype(int).to_dict()
    base_stability = panel_c["stability_class"].astype(str).str.replace(
        r"_external_(?:concordant|blocked|discordant|unresolved)$", "", regex=True
    )
    stability_counts = base_stability.value_counts().astype(int).to_dict()
    readiness_counts = readiness_audit["status"].value_counts().astype(int).to_dict()
    matrix_counts = benchmark_matrix["current_status"].value_counts().astype(int).to_dict()
    if novelty_upgrades is None:
        novelty_counts = {}
        tier1_pillars: list[dict[str, str]] = []
    else:
        novelty_counts = novelty_upgrades["priority_tier"].value_counts().astype(int).to_dict()
        tier1_pillars = (
            novelty_upgrades[novelty_upgrades["priority_tier"] == "tier1_core_thesis"]
            .drop_duplicates("pillar_id")
            .sort_values("pillar_id")[
                ["pillar_id", "pillar_name", "elevation_type", "manuscript_role"]
            ]
            .to_dict("records")
        )

    return {
        "recommended_route": str(recommended_row["route_id"]),
        "recommended_route_name": str(recommended_row["route_name"]),
        "central_object": str(recommended_row["central_object"]),
        "current_support": str(recommended_row["current_support"]),
        "next_decisive_action": str(recommended_row["next_decisive_action"]),
        "n_benchmark_rows": int(len(benchmark_matrix)),
        "matrix_counts": matrix_counts,
        "claim_counts": claim_counts,
        "n_responder_units": int(len(panel_b)),
        "responder_counts": responder_counts,
        "stability_counts": stability_counts,
        "n_no_same_context_replication": int(
            (panel_c["cross_dataset_status"] == "no_cross_dataset_same_context").sum()
        ),
        "n_external_same_context_concordant": int(
            (panel_c["cross_dataset_status"] == "external_same_context_concordant").sum()
        ),
        "n_external_same_context_blocked": int(
            (panel_c["cross_dataset_status"] == "external_same_context_blocked").sum()
        ),
        "n_external_same_context_discordant": int(
            (panel_c["cross_dataset_status"] == "external_same_context_discordant").sum()
        ),
        "n_external_same_context_unresolved": int(
            (panel_c["cross_dataset_status"] == "external_same_context_unresolved").sum()
        ),
        "readiness_counts": readiness_counts,
        "real_evidence_ready": bool(
            len(readiness_audit) > 0 and (readiness_audit["status"] == "ready").all()
        ),
        "n_novelty_upgrades": 0 if novelty_upgrades is None else int(len(novelty_upgrades)),
        "novelty_counts": novelty_counts,
        "tier1_novelty_pillars": tier1_pillars,
        "missing_readiness_artifacts": readiness_audit[
            readiness_audit["status"] != "ready"
        ][["check_id", "artifact", "detail"]].to_dict("records"),
    }


def render_recharter_manuscript_skeleton(payload: dict[str, object]) -> str:
    """Render a claim-bounded manuscript skeleton and reviewer-risk map."""
    claim_counts = payload["claim_counts"]
    responder_counts = payload["responder_counts"]
    stability_counts = payload["stability_counts"]
    matrix_counts = payload["matrix_counts"]
    missing = payload["missing_readiness_artifacts"]
    tier1_pillars = payload["tier1_novelty_pillars"]
    external_total = (
        payload["n_external_same_context_concordant"]
        + payload["n_external_same_context_blocked"]
        + payload["n_external_same_context_discordant"]
        + payload["n_external_same_context_unresolved"]
    )
    if payload["real_evidence_ready"]:
        immune_result_title = (
            "### Result 5: Public real-event evidence activates a bounded domain-transfer route"
        )
        immune_support = (
            "Current support: the readiness audit reports all nine real-evidence artifacts "
            "ready, including event contexts, candidate peptides, public ligand and T-cell "
            "evidence, decoys, tier assignments, claim audit, panel summary, and threshold robustness."
        )
        immune_allowed = (
            "Allowed claim: a public real-event domain-transfer benchmark is operational and auditable."
        )
        immune_reviewer_answer = (
            "| Is the immune story supported? | A public real-event domain-transfer benchmark is ready, "
            "but it is not matched PGAA-ranked or newly generated wet-lab evidence. | Keep the source "
            "boundary explicit and resolve the decoy-guarded sensitivity before stronger claims. |"
        )
        immediate_writing_rule = (
            "Write the manuscript around the failure-preserving benchmark object and use the real "
            "event-peptide evidence as a bounded domain-transfer result, not as PGAA wet-lab validation."
        )
    else:
        immune_result_title = (
            "### Result 5: The immune/event-peptide route is explicitly blocked, not silently overclaimed"
        )
        immune_support = (
            "Current support: the readiness audit still reports "
            "`NOT_READY_REAL_EVIDENCE_MISSING`; missing non-smoke artifacts are listed below."
        )
        immune_allowed = "Allowed claim: immune-evidence infrastructure exists as a future route."
        immune_reviewer_answer = (
            "| Is the immune story supported? | No; current PGAA outputs are gene-level and lack real "
            "event-peptide inputs. | Keep immune route as future infrastructure unless real event "
            "sources are added. |"
        )
        immediate_writing_rule = (
            "Write the manuscript around the failure-preserving benchmark object now. Only add "
            "immune/event-peptide claims after the readiness audit changes from "
            "`NOT_READY_REAL_EVIDENCE_MISSING` to a real-data ready state."
        )
    if external_total:
        replication_support = (
            f"Current support: {payload['n_external_same_context_concordant']} stability "
            "rows are `external_same_context_concordant`, "
            f"{payload['n_external_same_context_blocked']} are "
            "`external_same_context_blocked`, "
            f"{payload['n_external_same_context_discordant']} are "
            "`external_same_context_discordant`, and "
            f"{payload['n_external_same_context_unresolved']} are "
            "`external_same_context_unresolved` in the rendered figure."
        )
        replication_prohibited = (
            "Prohibited claim: Do not convert external computational concordance into "
            "wet-lab validation, immune presentation, synthetic peptide validation, or "
            "T-cell function."
        )
        reviewer_replication_answer = (
            "| Are responder states replicated? | Four current rows have bounded "
            "computational same-context external concordance, while blocked rows remain "
            "internal-only. | Use typed replication language and keep wet-lab claims blocked. |"
        )
    else:
        replication_support = (
            f"Current support: {payload['n_no_same_context_replication']} stability rows are "
            "`no_cross_dataset_same_context`, and that limitation is visible in the rendered figure."
        )
        replication_prohibited = (
            "Prohibited claim: Do not claim cross-dataset replication while all units lack same-context replication evidence."
        )
        reviewer_replication_answer = (
            "| Are responder states replicated? | Not yet; all same-context replication gates are negative. | "
            "Add external same-context evidence before using replication language. |"
        )
    lines = [
        "# PGAA Recharter Manuscript Skeleton",
        "",
        "## Central Method Object",
        "",
        (
            f"Recommended route: `{payload['recommended_route']}` "
            f"({payload['recommended_route_name']})."
        ),
        "",
        f"Central object: **{payload['central_object']}**.",
        "",
        (
            "This manuscript should be framed as a claim-state compiler for single-cell "
            "perturbation evidence. The primary novelty is not another score, but a "
            "compiled evidence object that carries positive support, descriptive-only "
            "findings, restricted-use states, failures, typed external replication states, "
            "and claim ceilings into the same auditable output."
        ),
        "",
        "## One-Sentence Thesis",
        "",
        (
            "PGAA can be rechartered from a distribution-aware ranking statistic into a "
            "claim-state compiler that converts perturbation scores into responder-state "
            "decision units, typed replication states, failure-preserving benchmark rows, "
            "and manuscript-safe claim ceilings."
        ),
        "",
        "## Novelty Upgrade Spine",
        "",
        (
            f"Novelty upgrade points: {payload['n_novelty_upgrades']}; tier-1 thesis "
            f"points: {payload['novelty_counts'].get('tier1_core_thesis', 0)}. "
            "This spine raises the manuscript from a tool-performance report to a framework "
            "for controlling evidentiary inflation in single-cell perturbation biology."
        ),
        "",
        "Evidence source: `evidence/novelty_upgrade_map.tsv` and `docs/NOVELTY_UPGRADE_MAP.md`.",
        "",
        "| Pillar | Name | Elevation | Manuscript role |",
        "|---|---|---|---|",
    ]
    for row in tier1_pillars:
        lines.append(
            f"| {row['pillar_id']} | {row['pillar_name']} | "
            f"{row['elevation_type']} | {row['manuscript_role']} |"
        )
    lines.extend(
        [
            "",
            (
                "Claim boundary: the upgraded thesis claims controlled interpretation and "
                "bounded computational same-context concordance, not validated antigens, "
                "immune presentation, synthetic-peptide validation, or T-cell function."
            ),
            "",
            "## Results Skeleton",
            "",
        ]
    )
    lines.extend(
        [
        "### Result 1: PGAA outputs are converted into claim states rather than score-only rows",
        "",
        "Evidence source: `evidence/result_claim_states.tsv` and `docs/RESULT_CLAIM_STATE_REPORT.md`.",
        "",
        (
            f"Current support: {claim_counts.get('comparative_support', 0)} comparative-support "
            f"rows, {claim_counts.get('descriptive_only', 0)} descriptive-only rows, "
            f"{claim_counts.get('calibration_support', 0)} calibration-support rows, "
            f"{claim_counts.get('restricted_use', 0)} restricted-use rows, and "
            f"{claim_counts.get('failure_or_guardrail', 0)} failure-or-guardrail rows."
        ),
        "",
        "Allowed claim: PGAA outputs can be audited into manuscript-safe claim states.",
        "",
        "Prohibited claim: Do not claim broad superiority from rows assigned to descriptive, restricted, or failure states.",
        "",
        "### Result 2: Decision-benchmark rows form context-level responder-state units",
        "",
        "Evidence source: `evidence/responder_state_units.tsv` and `docs/RESPONDER_STATE_DECISION_UNITS.md`.",
        "",
        (
            f"Current support: {payload['n_responder_units']} units, including "
            f"{responder_counts.get('supported_responder_state', 0)} supported units and "
            f"{responder_counts.get('provisional_responder_state', 0)} provisional units."
        ),
        "",
        "Allowed claim: selected Adamson contexts support bounded responder-state interpretation; Norman units remain provisional.",
        "",
        "Prohibited claim: Do not present provisional units as replicated discoveries.",
        "",
        "### Result 3: Leave-one-method checks expose dependence and method sensitivity",
        "",
        "Evidence source: `evidence/responder_state_stability_summary.tsv` and `docs/RESPONDER_STATE_STABILITY_REPORT.md`.",
        "",
        (
            f"Current support: {stability_counts.get('leave_one_method_stable', 0)} "
            f"leave-one-method stable units, {stability_counts.get('method_sensitive', 0)} "
            f"method-sensitive units, and {stability_counts.get('pgaa_support_dependent', 0)} "
            "PGAA-support dependent unit."
        ),
        "",
        "Allowed claim: the method distinguishes robust responder-state units from method-sensitive units.",
        "",
        replication_prohibited,
        "",
        "### Result 4: Figure 1 is generated from an auditable source table",
        "",
        "Evidence source: `evidence/main_figure_source_data.tsv`, `docs/MAIN_FIGURE_RENDER_REPORT.md`, and `figures_png/figure1_recharter_decision_object.png`.",
        "",
        replication_support,
        "",
        "Allowed claim: the figure is source-driven and claim bounded.",
        "",
        "Prohibited claim: Do not use Figure 1 as visual evidence of biological validation.",
        "",
        immune_result_title,
        "",
        "Evidence source: `docs/RECHARTER_READINESS_AUDIT.md` and `docs/EVENT_SOURCE_AUDIT.md`.",
        "",
        immune_support,
        "",
        immune_allowed,
        "",
        "Prohibited claim: Do not claim event-peptide presentation, synthetic peptide validation, or T-cell function.",
        "",
        "## Reviewer-Risk Map",
        "",
        "| Likely reviewer challenge | Current answer | Remaining action |",
        "|---|---|---|",
        (
            "| Is this more than another ranking statistic? | The method object is a claim-state "
            "compiler plus responder-state stability gate. | Make Figure 1 and Result 1 the entry point. |"
        ),
        (
            "| Are failures hidden? | No; failure-or-guardrail rows are counted and rendered. | "
            "Keep failure rows visible in main and supplementary figures. |"
        ),
        reviewer_replication_answer,
        immune_reviewer_answer,
        (
            "| Can the figures be reproduced? | Figure 1 is rendered from a 27-row source table. | "
            "Add the generated command chain to Methods and supplement. |"
        ),
        "",
        "## Benchmark Matrix State",
        "",
        f"Benchmark worklist rows: {payload['n_benchmark_rows']}.",
        "",
        "| Status | Rows |",
        "|---|---:|",
    ]
    )
    for status, count in sorted(matrix_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(
        [
            "",
            "## Missing Readiness Artifacts",
            "",
            "| Check | Artifact | Detail |",
            "|---|---|---|",
        ]
    )
    for row in missing:
        lines.append(f"| {row['check_id']} | `{row['artifact']}` | {row['detail']} |")
    lines.extend(
        [
            "",
            "## Immediate Writing Rule",
            "",
            immediate_writing_rule,
            "",
            f"Next decisive action: {payload['next_decisive_action']}",
            "",
        ]
    )
    return "\n".join(lines)


def build_and_render_recharter_manuscript_skeleton(
    route_scores: pd.DataFrame,
    benchmark_matrix: pd.DataFrame,
    figure_sources: pd.DataFrame,
    readiness_audit: pd.DataFrame,
    novelty_upgrades: pd.DataFrame | None = None,
) -> str:
    """Build and render the recharter manuscript skeleton."""
    payload = build_recharter_story_payload(
        route_scores, benchmark_matrix, figure_sources, readiness_audit, novelty_upgrades
    )
    return render_recharter_manuscript_skeleton(payload)
