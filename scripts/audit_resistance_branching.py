#!/usr/bin/env python3
"""Discover DTC resistance branches and validate them in held-out DTEC samples."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.resistance_branching import (
    build_branch_effects,
    rank_dtc_branch_genes,
    render_branch_audit,
    validate_dtec_branch,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression", required=True)
    parser.add_argument("--effects-out", required=True)
    parser.add_argument("--genes-out", required=True)
    parser.add_argument("--validation-out", required=True)
    parser.add_argument("--summary-out", required=True)
    parser.add_argument("--audit-out", required=True)
    parser.add_argument("--permutations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260720)
    args = parser.parse_args()
    raw = pd.read_csv(args.expression, sep="\t", index_col=0)
    effects = build_branch_effects(raw)
    genes = rank_dtc_branch_genes(effects, raw)
    validation, summary = validate_dtec_branch(
        genes, permutations=args.permutations, seed=args.seed
    )
    for path, frame in (
        (args.effects_out, effects.reset_index(names="gene_id")),
        (args.genes_out, genes),
        (args.validation_out, validation),
        (args.summary_out, summary),
    ):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
        print(f"Wrote {path}")
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_branch_audit(validation, summary), encoding="utf-8"
    )
    print(f"Wrote {args.audit_out}")


if __name__ == "__main__":
    main()
