#!/usr/bin/env python3
"""Build figure-ready source data from PGAA result-claim states."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.claim_panel_sources import (  # noqa: E402
    build_claim_panel_sources,
    render_claim_panel_report,
    summarize_claim_panels,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile result-claim states into figure-ready panel source data."
    )
    parser.add_argument(
        "--claims",
        type=Path,
        default=ROOT / "evidence/result_claim_states.tsv",
    )
    parser.add_argument("--panel-source-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    claims = pd.read_csv(args.claims, sep="\t")
    panel_sources = build_claim_panel_sources(claims)
    summary = summarize_claim_panels(panel_sources)

    args.panel_source_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    panel_sources.to_csv(args.panel_source_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(
        render_claim_panel_report(panel_sources, summary), encoding="utf-8"
    )

    print(f"Wrote {args.panel_source_out} ({len(panel_sources)} rows)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
