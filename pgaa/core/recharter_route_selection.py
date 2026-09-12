"""Rank feasible recharter routes for the PGAA methods paper."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_ROUTE_COLUMNS = [
    "route_id",
    "route_name",
    "central_object",
    "evidence_fit",
    "novelty_potential",
    "implementation_burden",
    "fatal_blocker_count",
    "claim_risk",
    "current_support",
    "next_decisive_action",
]


@dataclass(frozen=True)
class RouteWeights:
    evidence_fit: float = 0.35
    novelty_potential: float = 0.30
    implementation_burden: float = 0.15
    fatal_blocker_count: float = 0.15
    claim_risk: float = 0.05


def validate_route_matrix(routes: pd.DataFrame) -> list[str]:
    """Return validation errors for a route-option matrix."""
    errors: list[str] = []
    missing = [column for column in REQUIRED_ROUTE_COLUMNS if column not in routes.columns]
    if missing:
        return [f"missing columns: {missing}"]
    if routes.empty:
        return ["route matrix is empty"]

    seen: set[str] = set()
    for idx, row in routes.iterrows():
        route_id = str(row["route_id"]).strip()
        if not route_id:
            errors.append(f"row {idx}: empty route_id")
        elif route_id in seen:
            errors.append(f"{route_id}: duplicate route_id")
        seen.add(route_id)

        for column in REQUIRED_ROUTE_COLUMNS:
            if pd.isna(row[column]) or str(row[column]).strip() == "":
                errors.append(f"{route_id or idx}: empty {column}")

        for column in [
            "evidence_fit",
            "novelty_potential",
            "implementation_burden",
            "fatal_blocker_count",
            "claim_risk",
        ]:
            try:
                value = float(row[column])
            except (TypeError, ValueError):
                errors.append(f"{route_id}: nonnumeric {column}")
                continue
            if column == "fatal_blocker_count":
                if value < 0:
                    errors.append(f"{route_id}: fatal_blocker_count must be >= 0")
            elif value < 0 or value > 5:
                errors.append(f"{route_id}: {column} must be between 0 and 5")
    return errors


def score_routes(routes: pd.DataFrame, weights: RouteWeights | None = None) -> pd.DataFrame:
    """Score routes by current feasibility and top-journal upside."""
    weights = weights or RouteWeights()
    errors = validate_route_matrix(routes)
    if errors:
        raise ValueError("; ".join(errors))

    scored = routes.copy()
    for column in [
        "evidence_fit",
        "novelty_potential",
        "implementation_burden",
        "fatal_blocker_count",
        "claim_risk",
    ]:
        scored[column] = pd.to_numeric(scored[column])

    scored["route_score"] = (
        weights.evidence_fit * scored["evidence_fit"]
        + weights.novelty_potential * scored["novelty_potential"]
        - weights.implementation_burden * scored["implementation_burden"]
        - weights.fatal_blocker_count * scored["fatal_blocker_count"]
        - weights.claim_risk * scored["claim_risk"]
    ).round(3)
    scored["recommended_now"] = False
    best_index = scored.sort_values(
        ["route_score", "fatal_blocker_count", "evidence_fit"],
        ascending=[False, True, False],
    ).index[0]
    scored.loc[best_index, "recommended_now"] = True
    return scored.sort_values("route_score", ascending=False).reset_index(drop=True)


def render_route_report(scored: pd.DataFrame) -> str:
    """Render a recharter route decision report."""
    recommended = scored[scored["recommended_now"]].iloc[0]
    lines = [
        "# PGAA Recharter Route Decision",
        "",
        f"Recommended route now: `{recommended['route_id']}`",
    ]
    if "readiness_state" in scored.columns:
        states = sorted(set(scored["readiness_state"].dropna().astype(str)))
        if states:
            lines.extend(["", f"Real-evidence transition: `{', '.join(states)}`"])
    lines.extend([
        "",
        "| Rank | Route | Score | Evidence fit | Novelty | Fatal blockers | Claim risk |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ])
    for rank, (_, row) in enumerate(scored.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['route_id']}` | {row['route_score']} | "
            f"{row['evidence_fit']} | {row['novelty_potential']} | "
            f"{row['fatal_blocker_count']} | {row['claim_risk']} |"
        )
    lines.extend(
        [
            "",
            "## Recommended Interpretation",
            "",
            f"**{recommended['route_name']}** is the best route to advance immediately because "
            f"its central object is `{recommended['central_object']}` and its current support is: "
            f"{recommended['current_support']}",
            "",
            f"Next decisive action: {recommended['next_decisive_action']}",
            "",
            "## Route Details",
            "",
        ]
    )
    for _, row in scored.iterrows():
        lines.extend(
            [
                f"### {row['route_id']}",
                "",
                f"- Route name: {row['route_name']}",
                f"- Central object: {row['central_object']}",
                f"- Current support: {row['current_support']}",
                f"- Next decisive action: {row['next_decisive_action']}",
                "",
            ]
        )
    return "\n".join(lines)
