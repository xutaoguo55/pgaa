#!/usr/bin/env python3
"""Draft the PGAA recharter manuscript skeleton from generated evidence."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_manuscript_skeleton import (  # noqa: E402
    build_and_render_recharter_manuscript_skeleton,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft a claim-bounded manuscript skeleton for the PGAA recharter."
    )
    parser.add_argument(
        "--route-scores",
        type=Path,
        default=ROOT / "evidence/recharter_route_scores.tsv",
    )
    parser.add_argument(
        "--benchmark-matrix",
        type=Path,
        default=ROOT / "evidence/top_journal_benchmark_matrix_template.tsv",
    )
    parser.add_argument(
        "--figure-sources",
        type=Path,
        default=ROOT / "evidence/main_figure_source_data.tsv",
    )
    parser.add_argument(
        "--readiness-audit",
        type=Path,
        default=ROOT / "evidence/recharter_readiness_audit.tsv",
    )
    parser.add_argument(
        "--novelty-upgrades",
        type=Path,
        default=ROOT / "evidence/novelty_upgrade_map.tsv",
    )
    parser.add_argument("--out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    route_scores = pd.read_csv(args.route_scores, sep="\t")
    benchmark_matrix = pd.read_csv(args.benchmark_matrix, sep="\t")
    figure_sources = pd.read_csv(args.figure_sources, sep="\t")
    readiness_audit = pd.read_csv(args.readiness_audit, sep="\t")
    novelty_upgrades = (
        pd.read_csv(args.novelty_upgrades, sep="\t")
        if args.novelty_upgrades.exists()
        else None
    )
    text = build_and_render_recharter_manuscript_skeleton(
        route_scores, benchmark_matrix, figure_sources, readiness_audit, novelty_upgrades
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
