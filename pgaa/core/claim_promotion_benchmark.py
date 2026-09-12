"""Contract stress tests for unsupported claim promotion."""
from __future__ import annotations

from itertools import product

import pandas as pd

from pgaa.core.claim_state_formalization import (
    DECISION_STATES,
    EXTERNAL_STATES,
    STABILITY_STATES,
    compile_unit_claim_ceiling,
)


REQUIRED_OBJECT_COLUMNS = {
    "unit_id",
    "decision_state",
    "stability_class",
    "external_state",
    "permission_rank",
}

METHODS = (
    "claim_state_compiler",
    "state_blind_frozen_baseline",
    "decision_only_baseline",
    "external_only_baseline",
)


def _validate_objects(objects: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_OBJECT_COLUMNS - set(objects.columns))
    if missing:
        raise ValueError(f"formal decision objects are missing columns: {missing}")
    if objects["unit_id"].duplicated().any():
        raise ValueError("formal decision objects contain duplicate unit_id values")


def _decision_only_rank(decision_state: str) -> int:
    return int(
        compile_unit_claim_ceiling(
            decision_state,
            "method_sensitive",
            "external_same_context_blocked",
        )["permission_rank"]
    )


def _predict_rank(
    method: str,
    baseline_rank: int,
    decision_state: str,
    stability_class: str,
    external_state: str,
) -> int:
    if method == "claim_state_compiler":
        return int(
            compile_unit_claim_ceiling(
                decision_state, stability_class, external_state
            )["permission_rank"]
        )
    if method == "state_blind_frozen_baseline":
        return baseline_rank
    internal_rank = _decision_only_rank(decision_state)
    if method == "decision_only_baseline":
        return internal_rank
    if method == "external_only_baseline":
        return 3 if external_state == "external_same_context_concordant" else internal_rank
    raise ValueError(f"unknown benchmark method: {method}")


def build_claim_promotion_scenarios(objects: pd.DataFrame) -> pd.DataFrame:
    """Enumerate the complete finite state space for every observed decision unit."""
    _validate_objects(objects)
    decisions = sorted(DECISION_STATES)
    stabilities = sorted(STABILITY_STATES)
    external_states = sorted(EXTERNAL_STATES)
    rows: list[dict[str, object]] = []
    for _, observed in objects.iterrows():
        observed_tuple = (
            str(observed["decision_state"]),
            str(observed["stability_class"]),
            str(observed["external_state"]),
        )
        baseline_rank = int(observed["permission_rank"])
        for decision, stability, external in product(
            decisions, stabilities, external_states
        ):
            candidate = (decision, stability, external)
            changed = [
                name
                for name, old, new in zip(
                    ("decision", "stability", "external"), observed_tuple, candidate
                )
                if old != new
            ]
            mutation_scope = {
                0: "observed_state",
                1: "single_factor_mutation",
            }.get(len(changed), "multi_factor_mutation")
            oracle = compile_unit_claim_ceiling(decision, stability, external)
            scenario_id = "::".join(
                [str(observed["unit_id"]), decision, stability, external]
            )
            for method in METHODS:
                predicted_rank = _predict_rank(
                    method,
                    baseline_rank,
                    decision,
                    stability,
                    external,
                )
                oracle_rank = int(oracle["permission_rank"])
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "unit_id": observed["unit_id"],
                        "mutation_scope": mutation_scope,
                        "mutated_layers": ";".join(changed) if changed else "none",
                        "decision_state": decision,
                        "stability_class": stability,
                        "external_state": external,
                        "method": method,
                        "observed_permission_rank": baseline_rank,
                        "oracle_permission_rank": oracle_rank,
                        "predicted_permission_rank": predicted_rank,
                        "false_promotion": predicted_rank > oracle_rank,
                        "under_promotion": predicted_rank < oracle_rank,
                        "exact_permission": predicted_rank == oracle_rank,
                        "replication_false_positive": predicted_rank >= 3
                        and oracle_rank < 3,
                        "replication_true_positive": predicted_rank >= 3
                        and oracle_rank >= 3,
                        "replication_eligible": oracle_rank >= 3,
                    }
                )
    return pd.DataFrame(rows)


def summarize_claim_promotion_benchmark(scenarios: pd.DataFrame) -> pd.DataFrame:
    """Summarize permission errors for each method and mutation scope."""
    required = {
        "scenario_id",
        "mutation_scope",
        "method",
        "false_promotion",
        "under_promotion",
        "exact_permission",
        "replication_false_positive",
        "replication_true_positive",
        "replication_eligible",
    }
    missing = sorted(required - set(scenarios.columns))
    if missing:
        raise ValueError(f"claim-promotion scenarios are missing columns: {missing}")
    rows: list[dict[str, object]] = []
    scopes = ["all_scenarios", "observed_state", "single_factor_mutation", "multi_factor_mutation"]
    for method in METHODS:
        method_rows = scenarios[scenarios["method"] == method]
        for scope in scopes:
            group = (
                method_rows
                if scope == "all_scenarios"
                else method_rows[method_rows["mutation_scope"] == scope]
            )
            n = len(group)
            noneligible = group[~group["replication_eligible"].astype(bool)]
            eligible = group[group["replication_eligible"].astype(bool)]
            rows.append(
                {
                    "method": method,
                    "scope": scope,
                    "n_scenarios": n,
                    "n_false_promotions": int(group["false_promotion"].sum()),
                    "false_promotion_rate": float(group["false_promotion"].mean()) if n else 0.0,
                    "n_under_promotions": int(group["under_promotion"].sum()),
                    "under_promotion_rate": float(group["under_promotion"].mean()) if n else 0.0,
                    "exact_permission_rate": float(group["exact_permission"].mean()) if n else 0.0,
                    "replication_false_positive_rate": (
                        float(noneligible["replication_false_positive"].mean())
                        if len(noneligible)
                        else float("nan")
                    ),
                    "replication_sensitivity": (
                        float(eligible["replication_true_positive"].mean())
                        if len(eligible)
                        else float("nan")
                    ),
                    "n_replication_ineligible": len(noneligible),
                    "n_replication_eligible": len(eligible),
                }
            )
    return pd.DataFrame(rows)


def render_claim_promotion_benchmark_report(
    scenarios: pd.DataFrame, summary: pd.DataFrame
) -> str:
    """Render an honest report of the finite-state contract stress test."""
    overall = summary[summary["scope"] == "all_scenarios"].set_index("method")
    n_units = scenarios["unit_id"].nunique()
    n_states = scenarios["scenario_id"].nunique()
    lines = [
        "# Claim-Promotion Error Benchmark",
        "",
        "## Scope",
        "",
        f"The benchmark exhaustively evaluates {n_states} finite-state scenarios across {n_units} observed decision units. Each scenario changes zero, one, or multiple evidence gates while holding the originating unit identity fixed.",
        "",
        "This is a contract stress test, not an empirical ground-truth benchmark. The oracle is the predeclared permission contract. It tests whether a reporting strategy obeys that contract when evidence states change; it does not establish that the contract is biologically correct.",
        "",
        "## Overall Results",
        "",
        "| Method | Scenarios | False promotion | Replication false positive | Under-promotion | Exact permission | Replication sensitivity |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in METHODS:
        row = overall.loc[method]
        lines.append(
            f"| `{method}` | {int(row['n_scenarios'])} | {row['false_promotion_rate']:.1%} | "
            f"{row['replication_false_positive_rate']:.1%} | {row['under_promotion_rate']:.1%} | "
            f"{row['exact_permission_rate']:.1%} | {row['replication_sensitivity']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## Comparator Definitions",
            "",
            "- `claim_state_compiler`: recomputes permission from decision, stability, and external state.",
            "- `state_blind_frozen_baseline`: preserves the observed permission rank when evidence-gate metadata change. It is a deliberately favorable frozen-output proxy for reporting that does not update claims when evidence gates change, not a universal raw-score threshold.",
            "- `decision_only_baseline`: uses the internal decision state but cannot grant replication permission.",
            "- `external_only_baseline`: grants replication permission from external concordance without checking internal support or stability.",
            "",
            "## Interpretation",
            "",
            "A false promotion occurs when a method emits a permission rank above the contract ceiling. Under-promotion records the converse, so a conservative method cannot appear optimal merely by blocking every claim. Replication sensitivity is measured only among contract-eligible states; replication false-positive rate is measured only among ineligible states.",
            "",
            "The compiler's zero-error result is expected because this experiment verifies implementation fidelity to the declared contract. Evidence of empirical superiority requires independent annotations, additional datasets, or prospective reviewer/author decisions that were not used to define the oracle.",
            "",
        ]
    )
    return "\n".join(lines)
