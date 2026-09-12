#!/usr/bin/env python3
"""Draft claim-bounded manuscript sections for the PGAA recharter."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_manuscript_draft import (  # noqa: E402
    build_and_render_recharter_manuscript_draft,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft claim-bounded manuscript sections for the PGAA recharter."
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
        "--claim-states",
        type=Path,
        default=ROOT / "evidence/result_claim_states.tsv",
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
        "--external-stability-summary",
        type=Path,
        default=ROOT / "evidence/external_responder_state_stability_summary.tsv",
    )
    parser.add_argument("--out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    external_stability_summary = (
        pd.read_csv(args.external_stability_summary, sep="\t")
        if args.external_stability_summary.exists()
        else None
    )
    text = build_and_render_recharter_manuscript_draft(
        pd.read_csv(args.route_scores, sep="\t"),
        pd.read_csv(args.benchmark_matrix, sep="\t"),
        pd.read_csv(args.figure_sources, sep="\t"),
        pd.read_csv(args.readiness_audit, sep="\t"),
        pd.read_csv(args.claim_states, sep="\t"),
        pd.read_csv(args.responder_units, sep="\t"),
        pd.read_csv(args.stability_summary, sep="\t"),
        external_stability_summary,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
