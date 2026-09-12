#!/usr/bin/env python3
"""Build the fifth-system dynamic ATM validation artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.dynamic_atm_validation import (
    evaluate_dynamic_atm_gradient,
    project_source_branch_axis,
    render_dynamic_atm_audit,
    summarize_source_branch_axis_projection,
    score_day28_branch_induction,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-genes", required=True)
    parser.add_argument("--expression", required=True)
    parser.add_argument("--timecourse", required=True)
    parser.add_argument("--phase-out", required=True)
    parser.add_argument("--association-out", required=True)
    parser.add_argument("--projection-summary-out")
    parser.add_argument("--audit-out", required=True)
    args = parser.parse_args()

    ranked = pd.read_csv(args.branch_genes, sep="\t")
    raw = pd.read_csv(args.expression, sep="\t", low_memory=False)
    expression = (
        raw.loc[raw["Type"].eq("gene")]
        .groupby("Feature")
        .mean(numeric_only=True)
    )
    timecourse = pd.read_csv(args.timecourse, sep="\t")
    phase_scores = score_day28_branch_induction(ranked, expression)
    association = evaluate_dynamic_atm_gradient(timecourse)
    association_frame = pd.DataFrame([association])
    projection = project_source_branch_axis(ranked, expression)
    projection_summary = summarize_source_branch_axis_projection(projection)

    for path, frame in (
        (args.phase_out, phase_scores),
        (args.association_out, association_frame),
    ):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
    if args.projection_summary_out:
        Path(args.projection_summary_out).parent.mkdir(parents=True, exist_ok=True)
        projection_summary.to_csv(
            args.projection_summary_out, sep="\t", index=False
        )
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_dynamic_atm_audit(
            phase_scores,
            timecourse,
            association,
            projection_summary,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
