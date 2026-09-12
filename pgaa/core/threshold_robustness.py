"""Threshold and rule-sensitivity checks for immune-evidence tiers."""
from __future__ import annotations

import pandas as pd

from pgaa.core.immune_evidence import allowed_claim, integrated_tier, missing_flags
from pgaa.core.panel_design import compare_followup_panels


SCENARIOS = ("default", "strict_exact_only", "decoy_guarded")


def _numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def apply_threshold_scenario(tiers: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Apply a conservative evidence rule scenario and recompute tiers."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown threshold scenario: {scenario}")
    required = {
        "candidate_id",
        "presentation_category",
        "binding_prediction_category",
        "synthesis_category",
        "tcell_category",
        "integrated_tier",
    }
    missing = sorted(required - set(tiers.columns))
    if missing:
        raise ValueError(f"tier table is missing required columns: {missing}")

    adjusted = tiers.copy()
    adjusted["threshold_scenario"] = scenario
    adjusted["threshold_rule_notes"] = "none"

    if scenario == "strict_exact_only":
        overlap_mask = adjusted["presentation_category"].eq("presented-overlap")
        region_mask = adjusted["tcell_category"].eq("tcell-recognized-region")
        adjusted.loc[overlap_mask, "presentation_category"] = "binding-only"
        adjusted.loc[overlap_mask, "presentation_best_match_type"] = "none"
        adjusted.loc[overlap_mask, "presentation_source_count"] = 0
        adjusted.loc[region_mask, "tcell_category"] = "immune-context-support"
        adjusted.loc[region_mask, "tcell_source_count"] = 0
        adjusted.loc[overlap_mask | region_mask, "threshold_rule_notes"] = (
            "overlap_or_region_evidence_downgraded"
        )

    if scenario == "decoy_guarded":
        candidate_rate = _numeric(adjusted.get("candidate_match_rate", pd.Series([0.0] * len(adjusted))))
        decoy_rate = _numeric(adjusted.get("decoy_match_rate", pd.Series([0.0] * len(adjusted))))
        weak_background = decoy_rate >= candidate_rate
        evidence_mask = adjusted["presentation_category"].isin(
            {"presented-same-event", "presented-overlap"}
        ) | adjusted["tcell_category"].isin(
            {"tcell-recognized-exact-peptide", "tcell-recognized-region"}
        )
        downgrade = weak_background & evidence_mask
        adjusted.loc[downgrade, "presentation_category"] = "binding-only"
        adjusted.loc[downgrade, "presentation_best_match_type"] = "none"
        adjusted.loc[downgrade, "presentation_source_count"] = 0
        adjusted.loc[downgrade, "tcell_category"] = "no_tcell_evidence"
        adjusted.loc[downgrade, "tcell_source_count"] = 0
        adjusted.loc[downgrade, "threshold_rule_notes"] = (
            "public_evidence_not_above_decoy_background"
        )

    recalculated = []
    for _, row in adjusted.iterrows():
        presentation = str(row["presentation_category"])
        binding = str(row["binding_prediction_category"])
        synthesis = str(row["synthesis_category"])
        tcell = str(row["tcell_category"])
        tier = integrated_tier(presentation, binding, synthesis, tcell)
        recalculated.append(
            {
                "integrated_tier": tier,
                "allowed_claim": allowed_claim(tier, presentation, tcell),
                "missing_evidence_flags": missing_flags(
                    presentation, binding, synthesis, tcell
                ),
            }
        )
    recalculated_df = pd.DataFrame(recalculated, index=adjusted.index)
    for column in recalculated_df.columns:
        adjusted[column] = recalculated_df[column]
    return adjusted


def compare_threshold_robustness(
    tiers: pd.DataFrame,
    top_n: int = 20,
    scenarios: tuple[str, ...] = SCENARIOS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return scenario-adjusted tiers and summary stability metrics."""
    adjusted_tables = [apply_threshold_scenario(tiers, scenario) for scenario in scenarios]
    adjusted = pd.concat(adjusted_tables, ignore_index=True)
    default = adjusted[adjusted["threshold_scenario"] == "default"].set_index("candidate_id")
    default_ab = set(default[default["integrated_tier"].isin({"A", "B"})].index)

    summary_rows: list[dict[str, object]] = []
    for scenario in scenarios:
        scenario_table = adjusted[adjusted["threshold_scenario"] == scenario]
        scenario_ab = set(
            scenario_table[scenario_table["integrated_tier"].isin({"A", "B"})][
                "candidate_id"
            ]
        )
        tier_counts = scenario_table["integrated_tier"].value_counts().sort_index().to_dict()
        _, panel_summary = compare_followup_panels(
            scenario_table.drop(columns=["threshold_scenario"]),
            top_n=min(top_n, len(scenario_table)),
        )
        full_panel = panel_summary.set_index("comparison_method").loc["full_ladder"]
        summary_rows.append(
            {
                "threshold_scenario": scenario,
                "candidate_count": len(scenario_table),
                "tier_A_count": int(tier_counts.get("A", 0)),
                "tier_B_count": int(tier_counts.get("B", 0)),
                "tier_C_count": int(tier_counts.get("C", 0)),
                "tier_D_count": int(tier_counts.get("D", 0)),
                "default_AB_retained": len(default_ab & scenario_ab),
                "default_AB_lost": len(default_ab - scenario_ab),
                "scenario_AB_new": len(scenario_ab - default_ab),
                "full_ladder_panel_tier_A_count": int(full_panel["tier_A_count"]),
                "full_ladder_panel_tier_B_count": int(full_panel["tier_B_count"]),
            }
        )
    return adjusted, pd.DataFrame(summary_rows)
