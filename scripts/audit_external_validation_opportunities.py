#!/usr/bin/env python3
"""Build an external same-context validation worklist for PGAA responder-state units."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_validation_opportunities import (  # noqa: E402
    build_external_validation_opportunities,
    render_external_validation_report,
    summarize_external_validation_opportunities,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an external same-context validation worklist for PGAA."
    )
    parser.add_argument(
        "--units",
        type=Path,
        default=ROOT / "evidence/responder_state_units.tsv",
    )
    parser.add_argument(
        "--stability-summary",
        type=Path,
        default=ROOT / "evidence/responder_state_stability_summary.tsv",
    )
    parser.add_argument(
        "--dataset-manifest",
        type=Path,
        default=ROOT / "DATASET_MANIFEST.tsv",
    )
    parser.add_argument("--opportunities-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    opportunities = build_external_validation_opportunities(
        pd.read_csv(args.units, sep="\t"),
        pd.read_csv(args.stability_summary, sep="\t"),
        pd.read_csv(args.dataset_manifest, sep="\t"),
    )
    summary = summarize_external_validation_opportunities(opportunities)

    args.opportunities_out.parent.mkdir(parents=True, exist_ok=True)
    opportunities.to_csv(args.opportunities_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_validation_report(opportunities, summary), encoding="utf-8"
    )
    print(f"Wrote {args.opportunities_out} ({len(opportunities)} units)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
