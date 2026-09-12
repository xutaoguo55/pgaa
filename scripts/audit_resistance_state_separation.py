#!/usr/bin/env python3
"""Run the locked module against GSE249721 treatment contexts."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.resistance_state_separation import (
    audit_gse249721_separation,
    render_separation_audit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules", required=True)
    parser.add_argument("--expression", required=True)
    parser.add_argument("--contexts-out", required=True)
    parser.add_argument("--summary-out", required=True)
    parser.add_argument("--audit-out", required=True)
    parser.add_argument("--decoys", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=249721)
    args = parser.parse_args()
    modules = pd.read_csv(args.modules, sep="\t")
    expression = pd.read_csv(args.expression, sep="\t", index_col=0)
    contexts, summary = audit_gse249721_separation(
        modules, expression, decoy_count=args.decoys, seed=args.seed
    )
    for path, frame in ((args.contexts_out, contexts), (args.summary_out, summary)):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
        print(f"Wrote {path}")
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_separation_audit(contexts, summary), encoding="utf-8"
    )
    print(f"Wrote {args.audit_out}")


if __name__ == "__main__":
    main()
