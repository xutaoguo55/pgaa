#!/usr/bin/env python3
"""Check leave-one-method stability of PGAA responder-state units."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.responder_state_stability import (  # noqa: E402
    build_leave_one_method_stability,
    render_responder_state_stability_report,
    summarize_responder_state_stability,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit responder-state units with leave-one-method stability checks."
    )
    parser.add_argument(
        "--panel-source",
        type=Path,
        default=ROOT / "evidence/claim_panel_source_data.tsv",
    )
    parser.add_argument(
        "--units",
        type=Path,
        default=ROOT / "evidence/responder_state_units.tsv",
    )
    parser.add_argument("--detail-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    panel_sources = pd.read_csv(args.panel_source, sep="\t")
    units = pd.read_csv(args.units, sep="\t")
    detail = build_leave_one_method_stability(panel_sources, units)
    summary = summarize_responder_state_stability(detail, units)

    args.detail_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.detail_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(
        render_responder_state_stability_report(summary, detail), encoding="utf-8"
    )

    print(f"Wrote {args.detail_out} ({len(detail)} checks)")
    print(f"Wrote {args.summary_out} ({len(summary)} units)")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
