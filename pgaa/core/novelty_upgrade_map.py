"""Build a high-level novelty upgrade map for the PGAA recharter."""
from __future__ import annotations

from collections import Counter

import pandas as pd


REQUIRED_COLUMNS = {
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


PILLARS: tuple[dict[str, object], ...] = (
    {
        "pillar_id": "P01",
        "pillar_name": "Claim-state compiler",
        "elevation_type": "from score output to evidence-to-claim translation",
        "manuscript_role": "central framing",
        "evidence_gate": "result_claim_states plus manuscript audit",
        "claim_boundary": "claim language must be compiled from source evidence rows",
        "points": (
            "Define PGAA as an evidence-to-claim compiler rather than a ranking statistic.",
            "Treat each benchmark row as a typed claim object with allowed manuscript language.",
            "Attach claim ceilings directly to source rows instead of Discussion caveats.",
            "Make descriptive, restricted, and failure rows first-class method outputs.",
            "Separate numerical strength from evidentiary permission.",
            "Expose the transformation from metric value to manuscript claim state.",
            "Convert reviewer objections into explicit compiler checks.",
            "Let unsupported language fail a claim audit before submission.",
            "Make the manuscript text a rendered artifact of evidence states.",
            "Use claim compilation as the main novelty rather than an auxiliary QC layer.",
        ),
    },
    {
        "pillar_id": "P02",
        "pillar_name": "Failure-preserving benchmark engine",
        "elevation_type": "from winner-take-all benchmark to failure-aware benchmark governance",
        "manuscript_role": "methods contribution",
        "evidence_gate": "failure_mode_audit and claim_panel_summary",
        "claim_boundary": "failure and guardrail rows cannot be promoted to support claims",
        "points": (
            "Preserve failed, blocked, and restricted rows in the primary benchmark object.",
            "Report calibration failures as results rather than hiding them in limitations.",
            "Use parameter sensitivity as a claim limiter.",
            "Make negative controls part of the main evidence architecture.",
            "Score methods by whether they preserve the right claim ceiling.",
            "Represent benchmark failure modes as an interpretable taxonomy.",
            "Create a route where failure is informative rather than embarrassing.",
            "Turn missing evidence into an auditable state.",
            "Separate benchmark usefulness from biological validation.",
            "Define top-journal novelty around evidentiary discipline, not only accuracy.",
        ),
    },
    {
        "pillar_id": "P03",
        "pillar_name": "Responder-state decision units",
        "elevation_type": "from gene hit to context-level decision object",
        "manuscript_role": "results unit definition",
        "evidence_gate": "responder_state_units and stability summary",
        "claim_boundary": "provisional units remain hypotheses until support and stability gates pass",
        "points": (
            "Promote each perturbation context to a responder-state unit.",
            "Represent target, context, primary method, and support profile together.",
            "Store comparative support, descriptive support, and failure burden per unit.",
            "Use the unit, not the gene, as the manuscript claim object.",
            "Distinguish supported responder states from provisional responder-state hypotheses.",
            "Attach primary and secondary metrics to the same decision unit.",
            "Expose PGAA dependence at the unit level.",
            "Make method omission a property of each responder-state unit.",
            "Let responder units bridge internal benchmarks and external validation.",
            "Use unit-level tables as the source for figure and prose generation.",
        ),
    },
    {
        "pillar_id": "P04",
        "pillar_name": "Typed replication state",
        "elevation_type": "from binary replication to concordant, discordant, unresolved, or blocked state",
        "manuscript_role": "external validation framing",
        "evidence_gate": "external_claim_states and external_responder_state_stability",
        "claim_boundary": "external concordance supports only bounded computational same-context replication",
        "points": (
            "Replace yes/no replication with typed external claim states.",
            "Separate concordant, discordant, unresolved, and blocked external outcomes.",
            "Treat blocked external evidence as an explicit state rather than missing prose.",
            "Compile target-level external PGAA-W and PGAA-H outputs into claim states.",
            "Join external claim states back to internal responder-state units.",
            "Use external discordance as failure-preserving evidence rather than an exclusion.",
            "Make same-context replication computational unless wet-lab evidence exists.",
            "Track whether replication language is allowed, blocked, or unresolved.",
            "Show external status directly in Figure 1 Panel C.",
            "Use typed replication to avoid overclaiming from partial external support.",
        ),
    },
    {
        "pillar_id": "P05",
        "pillar_name": "Computational-wet-lab firewall",
        "elevation_type": "from missing wet-lab validation to explicit cross-layer claim control",
        "manuscript_role": "claim safety boundary",
        "evidence_gate": "readiness audit and immune evidence ladder",
        "claim_boundary": "no immune presentation, synthetic peptide, or T-cell function claim without direct evidence",
        "points": (
            "Encode wet-lab absence as a formal claim ceiling.",
            "Block antigen language unless event and ligand evidence exist.",
            "Block T-cell function language unless functional evidence exists.",
            "Keep immune route infrastructure separate from current PGAA claims.",
            "Use the firewall to turn a weakness into methodological honesty.",
            "Prevent gene-level perturbation support from becoming peptide-level assertion.",
            "Define evidence layers for sequence event, ligand presentation, and T-cell function.",
            "Require each layer to have its own source table before prose can use it.",
            "Make immune-readiness blockers reviewer-visible.",
            "Position PGAA as a tool that prevents evidentiary inflation.",
        ),
    },
    {
        "pillar_id": "P06",
        "pillar_name": "Dual-mode PGAA evidence",
        "elevation_type": "from one statistic to distribution-shift and shape-state complementarity",
        "manuscript_role": "method mechanics",
        "evidence_gate": "PGAA-W and PGAA-H target-level support states",
        "claim_boundary": "single-mode support is weaker than dual-mode support",
        "points": (
            "Separate Wasserstein distributional displacement from histogram-shape evidence.",
            "Use PGAA-W and PGAA-H as complementary evidence modes.",
            "Define dual-mode support as a stronger computational state.",
            "Retain single-mode support as bounded but weaker evidence.",
            "Interpret mode discordance as biologically or technically informative.",
            "Report mode-specific ranks and p-values instead of collapsing support.",
            "Use target-only permutation p-values only for the predeclared claim-state rule.",
            "Preserve full-gene observed ranks for interpretability.",
            "Make the two PGAA modes part of the external claim-state compiler.",
            "Avoid calling PGAA-H or PGAA-W alone a validated biological mechanism.",
        ),
    },
    {
        "pillar_id": "P07",
        "pillar_name": "Executable manuscript boundary",
        "elevation_type": "from written claims to tested manuscript invariants",
        "manuscript_role": "submission hardening",
        "evidence_gate": "manuscript audit tests and generated drafts",
        "claim_boundary": "drafts fail if required evidence references or boundaries disappear",
        "points": (
            "Generate manuscript sections from evidence payloads.",
            "Audit required evidence references in each draft.",
            "Audit forbidden unsupported phrases outside the forbidden-phrase list.",
            "Test that same-context replication boundaries are explicit.",
            "Keep blocked evidence visible in the manuscript body.",
            "Make figure captions source-driven rather than decorative.",
            "Use tests to prevent accidental claim inflation during style revision.",
            "Treat manuscript readiness as a machine-checkable contract.",
            "Keep journal-style prose aligned with evidence tables.",
            "Use executable boundaries as reviewer-facing transparency.",
        ),
    },
    {
        "pillar_id": "P08",
        "pillar_name": "Decision-object figure system",
        "elevation_type": "from workflow schematic to auditable decision object",
        "manuscript_role": "main figure strategy",
        "evidence_gate": "main_figure_source_data and render report",
        "claim_boundary": "figure panels cannot imply wet-lab validation",
        "points": (
            "Make Figure 1 a claim-control object rather than a pipeline illustration.",
            "Panel A shows claim-state and guardrail distribution.",
            "Panel B shows responder-state decision units.",
            "Panel C shows internal stability and external typed replication status.",
            "Use source rows for every plotted element.",
            "Show external blocked states rather than omitting them.",
            "Show external concordance without implying wet-lab validation.",
            "Keep method-sensitive units visible in the main figure.",
            "Render figure reports that state allowed interpretation.",
            "Use the figure as a compact reviewer audit surface.",
        ),
    },
    {
        "pillar_id": "P09",
        "pillar_name": "Claim-state stability theory",
        "elevation_type": "from stable score to stable allowed interpretation",
        "manuscript_role": "conceptual contribution",
        "evidence_gate": "leave-one-method and external integration summaries",
        "claim_boundary": "a stable score is insufficient unless the allowed claim is stable",
        "points": (
            "Define stability over claim states rather than raw scores only.",
            "Track whether leave-one-method omission changes the decision state.",
            "Separate method-sensitive from PGAA-support-dependent units.",
            "Join stability class to external claim-state status.",
            "Make claim transitions inspectable across methods.",
            "Treat stability loss as an interpretive result.",
            "Distinguish internal stability from external concordance.",
            "Use claim-state stability as a general benchmark criterion.",
            "Elevate reproducibility from repeated ranks to repeated allowed claims.",
            "Use stability theory to justify the rechartered method object.",
        ),
    },
    {
        "pillar_id": "P10",
        "pillar_name": "Generalizable claim-aware computational biology",
        "elevation_type": "from PGAA-specific rescue to reusable methodological class",
        "manuscript_role": "discussion and positioning",
        "evidence_gate": "route decision and benchmark matrix",
        "claim_boundary": "generalization is conceptual until each domain has its own evidence gates",
        "points": (
            "Position PGAA as one implementation of claim-aware computational biology.",
            "Map the framework to perturb-seq benchmarking.",
            "Map the framework to drug-response ranking.",
            "Map the framework to CRISPR screen interpretation.",
            "Map the framework to single-cell atlas comparison.",
            "Map the framework to biomarker prioritization.",
            "Reserve immunology applications for event-backed evidence layers.",
            "Define domain transfer as reuse of compiler semantics, not reuse of claims.",
            "Use the benchmark matrix to show which transfers are ready or blocked.",
            "Make broader applicability a framework claim rather than an empirical overclaim.",
        ),
    },
    {
        "pillar_id": "P11",
        "pillar_name": "Reviewer-facing governance",
        "elevation_type": "from defensive limitations to predeclared governance",
        "manuscript_role": "editorial risk reduction",
        "evidence_gate": "readiness audit, route selector, and benchmark matrix",
        "claim_boundary": "route claims must match readiness state",
        "points": (
            "Turn desk-reject risks into named governance gates.",
            "Use route selection to justify the computational methods framing.",
            "Keep top-journal ambition tied to evidence contracts.",
            "Record why immune-discovery framing remains blocked.",
            "Record why stable resistance-state bifurcation is the current route, with failure-preserving benchmark governance as the support layer.",
            "Expose next decisive actions instead of hiding work remaining.",
            "Use journal-style drafts only after claim audit passes.",
            "Make reviewer skepticism part of the design target.",
            "Preserve blocked rows so reviewers can see restraint.",
            "Use governance language to raise perceived maturity of the method.",
        ),
    },
    {
        "pillar_id": "P12",
        "pillar_name": "Epistemic inflation control",
        "elevation_type": "from better analysis to control of evidentiary inflation",
        "manuscript_role": "highest-level thesis",
        "evidence_gate": "all claim, figure, audit, and external status artifacts",
        "claim_boundary": "the paper claims controlled interpretation, not unbounded discovery",
        "points": (
            "Frame the problem as evidentiary inflation in single-cell perturbation reports.",
            "Argue that rankings alone cannot control downstream claims.",
            "Show that PGAA prevents computational support from becoming biological assertion.",
            "Use blocked and failed states to reduce false narrative certainty.",
            "Make the method's value a reduction in unsupported claim promotion.",
            "Connect claim ceilings to reproducibility and reviewability.",
            "Treat transparency as an operational method property.",
            "Make the paper about responsible computational inference.",
            "Use the external Replogle layer as proof that claim ceilings can update without overclaiming.",
            "Present PGAA as infrastructure for claim-safe perturbation biology.",
        ),
    },
)


def build_novelty_upgrade_map() -> pd.DataFrame:
    """Return a 100+ point map of large-scale novelty upgrades."""
    rows: list[dict[str, object]] = []
    for pillar_index, pillar in enumerate(PILLARS, start=1):
        for point_index, point in enumerate(pillar["points"], start=1):
            priority_tier = "tier1_core_thesis" if pillar_index in {1, 2, 3, 4, 12} else "tier2_supporting_frame"
            if pillar_index in {5, 7, 8, 9}:
                priority_tier = "tier1_core_thesis" if point_index <= 5 else "tier2_supporting_frame"
            rows.append(
                {
                    "upgrade_id": f"{pillar['pillar_id']}.{point_index:02d}",
                    "pillar_id": pillar["pillar_id"],
                    "pillar_name": pillar["pillar_name"],
                    "upgrade_point": point,
                    "elevation_type": pillar["elevation_type"],
                    "manuscript_role": pillar["manuscript_role"],
                    "evidence_gate": pillar["evidence_gate"],
                    "current_status": _status_for_pillar(str(pillar["pillar_id"])),
                    "next_action": _next_action_for_pillar(str(pillar["pillar_id"])),
                    "claim_boundary": pillar["claim_boundary"],
                    "priority_tier": priority_tier,
                }
            )
    frame = pd.DataFrame(rows)
    _validate(frame)
    return frame


def summarize_novelty_upgrade_map(upgrades: pd.DataFrame) -> pd.DataFrame:
    """Summarize the novelty map by pillar and priority tier."""
    _validate(upgrades)
    return (
        upgrades.groupby(
            [
                "pillar_id",
                "pillar_name",
                "elevation_type",
                "manuscript_role",
                "current_status",
                "priority_tier",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_upgrade_points")
        .sort_values(["priority_tier", "pillar_id"])
        .reset_index(drop=True)
    )


def render_novelty_upgrade_report(upgrades: pd.DataFrame, summary: pd.DataFrame) -> str:
    """Render a manuscript-strategy report from the novelty upgrade map."""
    _validate(upgrades)
    required_summary = {
        "pillar_id",
        "pillar_name",
        "elevation_type",
        "manuscript_role",
        "current_status",
        "priority_tier",
        "n_upgrade_points",
    }
    missing = sorted(required_summary - set(summary.columns))
    if missing:
        raise ValueError(f"novelty summary is missing columns: {missing}")

    tier_counts = Counter(upgrades["priority_tier"].astype(str))
    lines = [
        "# PGAA Novelty Upgrade Map",
        "",
        (
            "This map converts broad brainstorming into executable manuscript strategy. "
            "Each upgrade point is tied to a manuscript role, evidence gate, next action, "
            "and claim boundary so that the recharter raises the conceptual level without "
            "creating unsupported biological claims."
        ),
        "",
        f"Upgrade points: {len(upgrades)}",
        f"Tier-1 thesis points: {tier_counts.get('tier1_core_thesis', 0)}",
        f"Tier-2 supporting-frame points: {tier_counts.get('tier2_supporting_frame', 0)}",
        "",
        "## Core Thesis",
        "",
        (
            "PGAA should be positioned as a claim-state compiler for single-cell "
            "perturbation evidence: it converts scores into responder-state units, typed "
            "replication states, failure-preserving benchmark rows, and manuscript-safe "
            "claim ceilings."
        ),
        "",
        "## Pillar Summary",
        "",
        "| Pillar | Name | Role | Status | Tier | Points |",
        "|---|---|---|---|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['pillar_id']} | {row['pillar_name']} | {row['manuscript_role']} | "
            f"{row['current_status']} | {row['priority_tier']} | {row['n_upgrade_points']} |"
        )

    lines.extend(
        [
            "",
            "## Tier-1 Upgrade Points",
            "",
            "| Upgrade | Pillar | Point | Evidence gate | Claim boundary |",
            "|---|---|---|---|---|",
        ]
    )
    tier1 = upgrades[upgrades["priority_tier"] == "tier1_core_thesis"]
    for _, row in tier1.iterrows():
        lines.append(
            f"| {row['upgrade_id']} | {row['pillar_name']} | {row['upgrade_point']} | "
            f"{row['evidence_gate']} | {row['claim_boundary']} |"
        )

    lines.extend(
        [
            "",
            "## Immediate Recharter Moves",
            "",
            "1. Rewrite the title, abstract, and first Results section around claim-state compilation rather than PGAA as another ranking statistic.",
            "2. Make typed replication a named contribution: concordant, discordant, unresolved, and blocked are all valid external states.",
            "3. Keep the immune/wet-lab firewall prominent: computational concordance updates only the computational claim ceiling.",
            "4. Turn Figure 1 into the primary decision object and route every panel through source data.",
            "5. Add a compact theory paragraph: reproducibility should be assessed over allowed claims, not only over scores.",
            "",
            "## Non-Negotiable Boundary",
            "",
            (
                "The upgraded framing must not claim validated antigens, immune presentation, "
                "synthetic-peptide validation, or T-cell function. The current external "
                "Replogle layer supports bounded computational same-context concordance only."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _status_for_pillar(pillar_id: str) -> str:
    if pillar_id in {"P01", "P04", "P08", "P09", "P12"}:
        return "implemented_in_executable_recharter_chain"
    if pillar_id in {"P02", "P03", "P07"}:
        return "partially_implemented_in_current_recharter"
    if pillar_id == "P05":
        return "implemented_as_claim_boundary_but_not_as_main_thesis"
    return "strategy_defined_needs_manuscript_integration"


def _next_action_for_pillar(pillar_id: str) -> str:
    actions = {
        "P01": "Validate claim ceilings through additional external datasets and prospective source-row stress tests.",
        "P02": "Make failure-preserving benchmark governance a named Methods subsection.",
        "P03": "Use responder-state units as the canonical unit in Results and Figure 1.",
        "P04": "Add real or synthetic discordant and unresolved external cases to stress every typed replication branch.",
        "P05": "Keep wet-lab and immune claims blocked unless direct event, ligand, and T-cell evidence exists.",
        "P06": "Clarify single-mode versus dual-mode PGAA support in the external claim-state paragraph.",
        "P07": "Describe the manuscript audit as an executable claim-boundary layer.",
        "P08": "Add the formal transition contract as the next source-driven decision figure.",
        "P09": "Extend permission-stability analysis to additional external datasets and empirical row-level perturbations.",
        "P10": "Limit generalization to reusable compiler semantics unless new domain gates are built.",
        "P11": "Use route and readiness artifacts as reviewer-facing governance evidence.",
        "P12": "Estimate unsupported claim promotion under additional external datasets and prospective reporting decisions.",
    }
    return actions[pillar_id]


def _validate(frame: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"novelty upgrade map is missing columns: {missing}")
    if len(frame) < 100:
        raise ValueError("novelty upgrade map must contain at least 100 upgrade points")
