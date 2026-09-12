"""Decision-level follow-up panel comparison for immune-evidence candidates."""
from __future__ import annotations

import pandas as pd


TIER_WEIGHT = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 0.0}
BINDING_WEIGHT = {
    "strong_predicted_binding": 2.0,
    "predicted_binding": 1.0,
    "weak_or_no_predicted_binding": -1.0,
    "not_assessed": 0.0,
}
PRESENTATION_WEIGHT = {
    "presented-same-event": 2.0,
    "presented-overlap": 1.0,
    "binding-only": 0.0,
}
TCELL_WEIGHT = {
    "tcell-recognized-exact-peptide": 2.0,
    "tcell-recognized-region": 1.0,
    "immune-context-support": 0.5,
    "no_tcell_evidence": 0.0,
}


def _numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _rank_component(table: pd.DataFrame) -> pd.Series:
    if "pgaa_rank" in table.columns:
        rank = _numeric(table["pgaa_rank"], default=float("nan"))
        if rank.notna().any():
            max_rank = rank.max()
            return (max_rank - rank + 1).fillna(0.0) / max(max_rank, 1.0)
    if "pgaa_score" in table.columns:
        score = _numeric(table["pgaa_score"])
        spread = score.max() - score.min()
        if spread > 0:
            return (score - score.min()) / spread
        return pd.Series([1.0] * len(table), index=table.index)
    return pd.Series([0.0] * len(table), index=table.index)


def add_panel_scores(tiers: pd.DataFrame) -> pd.DataFrame:
    """Add baseline and full-ladder ranking scores to an immune tier table."""
    required = {"candidate_id", "integrated_tier"}
    missing = sorted(required - set(tiers.columns))
    if missing:
        raise ValueError(f"tier table is missing required columns: {missing}")

    scored = tiers.copy()
    scored["pgaa_rank_score"] = _rank_component(scored)
    scored["binding_panel_score"] = scored.get(
        "binding_prediction_category", pd.Series(["not_assessed"] * len(scored))
    ).map(BINDING_WEIGHT).fillna(0.0)
    scored["ligand_panel_score"] = scored.get(
        "presentation_category", pd.Series(["binding-only"] * len(scored))
    ).map(PRESENTATION_WEIGHT).fillna(0.0)
    scored["tcell_panel_score"] = scored.get(
        "tcell_category", pd.Series(["no_tcell_evidence"] * len(scored))
    ).map(TCELL_WEIGHT).fillna(0.0)
    scored["tier_panel_score"] = scored["integrated_tier"].map(TIER_WEIGHT).fillna(0.0)
    scored["synthesis_penalty"] = (
        scored.get("synthesis_category", pd.Series([""] * len(scored)))
        .eq("synthesis-risk")
        .astype(float)
        * 3.0
    )
    scored["full_ladder_panel_score"] = (
        scored["tier_panel_score"]
        + scored["ligand_panel_score"]
        + scored["tcell_panel_score"]
        + scored["binding_panel_score"]
        + scored["pgaa_rank_score"]
        - scored["synthesis_penalty"]
    )
    return scored


def select_panel(scored: pd.DataFrame, score_column: str, top_n: int) -> pd.DataFrame:
    """Select the top-N candidate panel for a score column."""
    if score_column not in scored.columns:
        raise ValueError(f"missing score column: {score_column}")
    sort_columns = [score_column]
    ascending = [False]
    if "pgaa_rank" in scored.columns:
        sort_columns.append("pgaa_rank")
        ascending.append(True)
    sort_columns.append("candidate_id")
    ascending.append(True)
    return scored.sort_values(sort_columns, ascending=ascending).head(top_n).copy()


def compare_followup_panels(
    tiers: pd.DataFrame,
    top_n: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare full-ladder panel selection against simple baselines."""
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    scored = add_panel_scores(tiers)
    methods = {
        "full_ladder": "full_ladder_panel_score",
        "pgaa_rank": "pgaa_rank_score",
        "binding_only": "binding_panel_score",
        "ligand_only": "ligand_panel_score",
    }

    panel_rows: list[pd.DataFrame] = []
    selected: dict[str, set[str]] = {}
    for method, score_column in methods.items():
        panel = select_panel(scored, score_column, top_n)
        panel.insert(0, "selection_method", method)
        panel.insert(1, "selection_rank", range(1, len(panel) + 1))
        panel_rows.append(panel)
        selected[method] = set(panel["candidate_id"])

    full = selected["full_ladder"]
    summary_rows: list[dict[str, object]] = []
    for method, candidate_ids in selected.items():
        intersection = full & candidate_ids
        union = full | candidate_ids
        panel = pd.concat(panel_rows)
        method_panel = panel[panel["selection_method"] == method]
        tier_counts = (
            method_panel["integrated_tier"].value_counts().sort_index().to_dict()
            if "integrated_tier" in method_panel.columns
            else {}
        )
        summary_rows.append(
            {
                "comparison_method": method,
                "top_n": top_n,
                "selected_count": len(candidate_ids),
                "overlap_with_full_ladder": len(intersection),
                "new_vs_full_ladder": len(candidate_ids - full),
                "missed_by_method_vs_full_ladder": len(full - candidate_ids),
                "jaccard_with_full_ladder": len(intersection) / len(union) if union else 1.0,
                "tier_A_count": int(tier_counts.get("A", 0)),
                "tier_B_count": int(tier_counts.get("B", 0)),
                "tier_C_count": int(tier_counts.get("C", 0)),
                "tier_D_count": int(tier_counts.get("D", 0)),
            }
        )

    return pd.concat(panel_rows, ignore_index=True), pd.DataFrame(summary_rows)
