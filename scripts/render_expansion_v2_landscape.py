#!/usr/bin/env python3
"""Render the frozen expansion-v2 primary result and full state landscape."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def _markdown(frame: pd.DataFrame) -> str:
    values = frame.fillna("").astype(str)
    header = "| " + " | ".join(values.columns) + " |"
    divider = "| " + " | ".join(["---"] * len(values.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in values.itertuples(index=False, name=None)]
    return "\n".join([header, divider, *rows])


def main() -> int:
    states = pd.read_csv(EVIDENCE / "expansion_v2_dual_gate_states.tsv", sep="\t")
    primary = pd.read_csv(EVIDENCE / "expansion_v2_confirmatory_claim_state.tsv", sep="\t").iloc[0]
    landscape = pd.read_csv(EVIDENCE / "expansion_v2_state_landscape.tsv", sep="\t")
    secondary = pd.read_csv(EVIDENCE / "expansion_v2_joint_portability_secondary.tsv", sep="\t").iloc[0]

    pgaa = states[states["method"].eq("pgaa_w")][
        [
            "dataset_id",
            "median_observed_overlap",
            "median_pseudo_overlap",
            "median_specificity_margin",
            "holm_adjusted_p",
            "dual_gate_state",
        ]
    ].sort_values("dataset_id")
    for column in [
        "median_observed_overlap",
        "median_pseudo_overlap",
        "median_specificity_margin",
        "holm_adjusted_p",
    ]:
        pgaa[column] = pgaa[column].map(lambda value: f"{value:.4g}")

    counts = landscape.pivot(index="method", columns="dual_gate_state", values="state_count")
    counts = counts.reindex(
        columns=[
            "stable_and_specific",
            "stable_but_not_specific",
            "specific_but_not_stable",
            "neither_stable_nor_specific",
        ],
        fill_value=0,
    ).reset_index()

    lines = [
        "# Expansion v2 State Landscape",
        "",
        "## Frozen primary result",
        "",
        (
            f"The frozen primary event (`pgaa_w` stable-but-not-specific) occurred in "
            f"{int(primary['n_stable_but_not_specific'])}/{int(primary['n_confirmatory_platforms'])} "
            f"platforms. The machine claim state is `{primary['confirmatory_claim_state']}`. "
            "The pre-specified recurrence claim is therefore not supported."
        ),
        "",
        "## Complete four-state landscape",
        "",
        (
            f"PGAA-W was stable-and-specific in {int(secondary['state_count'])}/"
            f"{int(secondary['n_confirmatory_platforms'])} platforms "
            f"(exact 95% CI {secondary['clopper_pearson_95_low']:.3f}-"
            f"{secondary['clopper_pearson_95_high']:.3f}), spanning "
            f"{int(secondary['mechanism_classes'])} perturbation-mechanism classes and "
            f"{int(secondary['cell_context_classes'])} cell-context classes. The minimum "
            f"leave-one-study-out count was {int(secondary['minimum_leave_one_study_out_count'])}."
        ),
        "",
        _markdown(counts),
        "",
        "This is a secondary summary of the pre-specified four-state output. Applying the frozen cross-context recurrence thresholds symmetrically to stable-and-specific states was decided after outcomes and is typed as `post_outcome_symmetric_rule_application`; it does not replace the frozen primary estimand.",
        "",
        "## PGAA-W platform states",
        "",
        _markdown(pgaa),
        "",
        "## Interpretation",
        "",
        "The ten-platform expansion does not support a general stability-specificity decoupling law. Instead, it reveals conditional joint portability: when PGAA-W passed the stability gate in this cohort, it also passed the pseudo-perturbation specificity gate (6/6 stable platforms). The remaining systems occupied one specific-but-not-stable state and three neither-state positions.",
        "",
        "The result supports a method-by-context state landscape, not universal PGAA-W superiority. Absolute mean shift was stable-and-specific in 4/10 platforms, Welch in 2/10, and PGAA-H in 0/10; paired platform counts are too small to license a broad superiority claim.",
    ]
    output = ROOT / "docs/EXPANSION_V2_STATE_LANDSCAPE.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
