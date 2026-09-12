#!/usr/bin/env python3
"""Build multi-level decoys and stratified public-evidence enrichment."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.multilevel_decoy import (  # noqa: E402
    build_multilevel_decoys,
    compare_multilevel_decoy_enrichment,
    render_multilevel_decoy_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--existing-decoys", type=Path, required=True)
    parser.add_argument("--ligand-evidence", type=Path, required=True)
    parser.add_argument("--tcell-evidence", type=Path, required=True)
    parser.add_argument("--decoys-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--audit-out", type=Path)
    args = parser.parse_args()

    candidates = pd.read_csv(args.candidates, sep="\t")
    decoys = build_multilevel_decoys(
        candidates, pd.read_csv(args.existing_decoys, sep="\t")
    )
    summary = compare_multilevel_decoy_enrichment(
        candidates,
        decoys,
        pd.read_csv(args.ligand_evidence, sep="\t"),
        pd.read_csv(args.tcell_evidence, sep="\t"),
    )
    args.decoys_out.parent.mkdir(parents=True, exist_ok=True)
    decoys.to_csv(args.decoys_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    if args.audit_out:
        args.audit_out.parent.mkdir(parents=True, exist_ok=True)
        args.audit_out.write_text(render_multilevel_decoy_audit(summary), encoding="utf-8")
    print(f"Wrote {args.decoys_out} ({len(decoys)} decoys)")
    print(f"Wrote {args.summary_out} ({len(summary)} groups)")
    if args.audit_out:
        print(f"Wrote {args.audit_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
