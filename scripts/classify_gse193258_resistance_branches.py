#!/usr/bin/env python3
"""Apply the frozen GSE249721 branch classifier to GSE193258."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.prospective_resistance_branching import (
    classify_gse193258_branches,
    predict_branch_vulnerabilities,
    render_prospective_audit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-genes", required=True)
    parser.add_argument("--expression", required=True)
    parser.add_argument("--assignments-out", required=True)
    parser.add_argument("--trajectories-out", required=True)
    parser.add_argument("--vulnerabilities-out", required=True)
    parser.add_argument("--audit-out", required=True)
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=193258)
    args = parser.parse_args()
    genes = pd.read_csv(args.branch_genes, sep="\t")
    expression = pd.read_csv(args.expression, sep="\t", index_col=0)
    assignments, trajectories = classify_gse193258_branches(
        genes, expression, permutations=args.permutations, seed=args.seed
    )
    vulnerabilities = predict_branch_vulnerabilities(assignments)
    for path, frame in (
        (args.assignments_out, assignments),
        (args.trajectories_out, trajectories),
        (args.vulnerabilities_out, vulnerabilities),
    ):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
        print(f"Wrote {path}")
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_prospective_audit(assignments, vulnerabilities), encoding="utf-8"
    )
    print(f"Wrote {args.audit_out}")


if __name__ == "__main__":
    main()
