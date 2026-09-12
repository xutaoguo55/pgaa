#!/usr/bin/env python3
"""Build responder-state decision units from PGAA claim-panel source data."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.responder_state_units import (  # noqa: E402
    build_responder_state_units,
    render_responder_state_report,
    summarize_responder_state_units,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile claim-panel rows into responder-state decision units."
    )
    parser.add_argument(
        "--panel-source",
        type=Path,
        default=ROOT / "evidence/claim_panel_source_data.tsv",
    )
    parser.add_argument("--units-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    panel_sources = pd.read_csv(args.panel_source, sep="\t")
    units = build_responder_state_units(panel_sources)
    summary = summarize_responder_state_units(units)

    args.units_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    units.to_csv(args.units_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(render_responder_state_report(units, summary), encoding="utf-8")

    print(f"Wrote {args.units_out} ({len(units)} units)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
