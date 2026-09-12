#!/usr/bin/env python3
"""Audit candidate public datasets for external PGAA validation."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_dataset_candidates import (  # noqa: E402
    audit_external_dataset_candidates,
    render_external_dataset_candidate_report,
    summarize_external_dataset_candidates,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify public dataset candidates before external PGAA validation."
    )
    parser.add_argument(
        "--opportunities",
        type=Path,
        default=ROOT / "evidence/external_validation_opportunities.tsv",
    )
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        default=ROOT / "evidence/external_dataset_candidate_manifest.tsv",
    )
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audit = audit_external_dataset_candidates(
        pd.read_csv(args.opportunities, sep="\t"),
        pd.read_csv(args.candidate_manifest, sep="\t"),
    )
    summary = summarize_external_dataset_candidates(audit)

    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.audit_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_dataset_candidate_report(audit, summary), encoding="utf-8"
    )
    print(f"Wrote {args.audit_out} ({len(audit)} target-candidate pairs)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
