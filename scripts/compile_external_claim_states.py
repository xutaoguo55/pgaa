#!/usr/bin/env python3
"""Compile external PGAA outputs into external claim-state rows."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_claim_state_compiler import (  # noqa: E402
    compile_external_claim_states,
    render_external_claim_state_report,
    summarize_external_claim_states,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile external PGAA-W/PGAA-H outputs into conservative claim states."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "evidence/external_pgaa_execution_manifest_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--internal-units",
        type=Path,
        default=ROOT / "evidence/responder_state_units.tsv",
    )
    parser.add_argument("--top-n", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--no-write-per-target", action="store_true")
    parser.add_argument("--claim-states-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    claim_states = compile_external_claim_states(
        pd.read_csv(args.manifest, sep="\t"),
        pd.read_csv(args.internal_units, sep="\t"),
        top_n=args.top_n,
        alpha=args.alpha,
        write_files=not args.no_write_per_target,
    )
    summary = summarize_external_claim_states(claim_states)

    args.claim_states_out.parent.mkdir(parents=True, exist_ok=True)
    claim_states.to_csv(args.claim_states_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_claim_state_report(claim_states, summary),
        encoding="utf-8",
    )
    print(f"Wrote {args.claim_states_out} ({len(claim_states)} targets)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
