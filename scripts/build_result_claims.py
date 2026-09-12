#!/usr/bin/env python3
"""Build manuscript-facing result-claim states from the PGAA failure audit."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.result_claims import (  # noqa: E402
    build_response_specificity_claim_table,
    build_result_claim_table,
    build_stability_specificity_dual_gate,
    render_result_claim_report,
    render_stability_specificity_dual_gate_report,
    summarize_result_claims,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile failure-mode audit rows into manuscript-facing claim states."
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=ROOT / "evidence/failure_mode_audit.tsv",
    )
    parser.add_argument(
        "--response-specificity-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_response_specificity_summary.tsv",
    )
    parser.add_argument(
        "--response-replication-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_response_replication_summary.tsv",
    )
    parser.add_argument(
        "--dual-gate-out",
        type=Path,
        default=ROOT / "evidence/response_stability_specificity_dual_gate.tsv",
    )
    parser.add_argument(
        "--dual-gate-report-out",
        type=Path,
        default=ROOT / "docs/RESPONSE_STABILITY_SPECIFICITY_DUAL_GATE.md",
    )
    parser.add_argument("--claims-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audit = pd.read_csv(args.audit, sep="\t")
    claims = build_result_claim_table(audit)
    if args.response_specificity_summary.exists():
        response_claims = build_response_specificity_claim_table(
            pd.read_csv(args.response_specificity_summary, sep="\t")
        )
        claims = pd.concat([claims, response_claims], ignore_index=True)
    summary = summarize_result_claims(claims)

    args.claims_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    claims.to_csv(args.claims_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(render_result_claim_report(claims, summary), encoding="utf-8")

    if args.response_replication_summary.exists() and args.response_specificity_summary.exists():
        dual_gate = build_stability_specificity_dual_gate(
            pd.read_csv(args.response_replication_summary, sep="\t"),
            pd.read_csv(args.response_specificity_summary, sep="\t"),
        )
        args.dual_gate_out.parent.mkdir(parents=True, exist_ok=True)
        args.dual_gate_report_out.parent.mkdir(parents=True, exist_ok=True)
        dual_gate.to_csv(args.dual_gate_out, sep="\t", index=False)
        args.dual_gate_report_out.write_text(
            render_stability_specificity_dual_gate_report(dual_gate), encoding="utf-8"
        )

    print(f"Wrote {args.claims_out} ({len(claims)} rows)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    if args.response_replication_summary.exists() and args.response_specificity_summary.exists():
        print(f"Wrote {args.dual_gate_out}")
        print(f"Wrote {args.dual_gate_report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
