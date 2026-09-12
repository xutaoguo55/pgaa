#!/usr/bin/env python3
"""Rank PGAA recharter routes by feasibility and top-journal upside."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_route_selection import render_route_report, score_routes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score candidate PGAA recharter routes from a TSV option matrix."
    )
    parser.add_argument(
        "--routes",
        type=Path,
        default=ROOT / "evidence/recharter_route_options.tsv",
    )
    parser.add_argument("--scored-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    routes = pd.read_csv(args.routes, sep="\t")
    scored = score_routes(routes)
    args.scored_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.scored_out, sep="\t", index=False)
    args.report_out.write_text(render_route_report(scored), encoding="utf-8")
    recommended = scored[scored["recommended_now"]].iloc[0]
    print(f"Wrote {args.scored_out} ({len(scored)} routes)")
    print(f"Wrote {args.report_out}")
    print(f"Recommended route now: {recommended['route_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
