#!/usr/bin/env python3
"""Build unified main-figure source data for the PGAA recharter."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.main_figure_sources import (  # noqa: E402
    build_main_figure_sources,
    render_main_figure_source_report,
    summarize_main_figure_sources,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile claim, responder-state, and stability artifacts into main-figure source data."
    )
    parser.add_argument(
        "--claim-summary",
        type=Path,
        default=ROOT / "evidence/claim_panel_summary.tsv",
    )
    parser.add_argument(
        "--responder-units",
        type=Path,
        default=ROOT / "evidence/responder_state_units.tsv",
    )
    parser.add_argument(
        "--stability-summary",
        type=Path,
        default=ROOT / "evidence/responder_state_stability_summary.tsv",
    )
    parser.add_argument(
        "--integrated-stability",
        type=Path,
        default=ROOT / "evidence/external_responder_state_stability_integrated.tsv",
    )
    parser.add_argument("--figure-source-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    claim_summary = pd.read_csv(args.claim_summary, sep="\t")
    responder_units = pd.read_csv(args.responder_units, sep="\t")
    stability_summary = pd.read_csv(args.stability_summary, sep="\t")
    integrated_stability = (
        pd.read_csv(args.integrated_stability, sep="\t")
        if args.integrated_stability.exists()
        else None
    )
    figure_sources = build_main_figure_sources(
        claim_summary, responder_units, stability_summary, integrated_stability
    )
    summary = summarize_main_figure_sources(figure_sources)

    args.figure_source_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    figure_sources.to_csv(args.figure_source_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(
        render_main_figure_source_report(figure_sources, summary), encoding="utf-8"
    )

    print(f"Wrote {args.figure_source_out} ({len(figure_sources)} rows)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
