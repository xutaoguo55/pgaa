#!/usr/bin/env python3
"""Draft journal-style claim-bounded manuscript sections for the PGAA recharter."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_journal_style_draft import (  # noqa: E402
    build_and_render_recharter_journal_style_draft,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Draft journal-style claim-bounded manuscript sections for PGAA."
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
    parser.add_argument(
        "--novelty-upgrades",
        type=Path,
        default=ROOT / "evidence/novelty_upgrade_map.tsv",
    )
    parser.add_argument(
        "--formal-invariant-audit",
        type=Path,
        default=ROOT / "evidence/claim_state_invariant_audit.tsv",
    )
    parser.add_argument(
        "--promotion-benchmark-summary",
        type=Path,
        default=ROOT / "evidence/claim_promotion_benchmark_summary.tsv",
    )
    parser.add_argument(
        "--generality-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_generality_results_summary.tsv",
    )
    parser.add_argument(
        "--generality-baseline-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_generality_baseline_summary.tsv",
    )
    parser.add_argument(
        "--response-replication-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_response_replication_summary.tsv",
    )
    parser.add_argument(
        "--response-specificity-summary",
        type=Path,
        default=ROOT / "evidence/replogle_essential_response_specificity_summary.tsv",
    )
    parser.add_argument(
        "--cross-platform-gates",
        type=Path,
        default=ROOT / "evidence/cross_platform_dual_gate_states.tsv",
    )
    parser.add_argument(
        "--cross-platform-sensitivity",
        type=Path,
        default=ROOT / "evidence/cross_platform_dual_gate_threshold_sensitivity.tsv",
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
    novelty_upgrades = (
        pd.read_csv(args.novelty_upgrades, sep="\t")
        if args.novelty_upgrades.exists()
        else None
    )
    formal_invariant_audit = (
        pd.read_csv(args.formal_invariant_audit, sep="\t")
        if args.formal_invariant_audit.exists()
        else None
    )
    promotion_benchmark_summary = (
        pd.read_csv(args.promotion_benchmark_summary, sep="\t")
        if args.promotion_benchmark_summary.exists()
        else None
    )
    generality_summary = (
        pd.read_csv(args.generality_summary, sep="\t")
        if args.generality_summary.exists()
        else None
    )
    generality_baseline_summary = (
        pd.read_csv(args.generality_baseline_summary, sep="\t")
        if args.generality_baseline_summary.exists()
        else None
    )
    response_replication_summary = (
        pd.read_csv(args.response_replication_summary, sep="\t")
        if args.response_replication_summary.exists()
        else None
    )
    response_specificity_summary = (
        pd.read_csv(args.response_specificity_summary, sep="\t")
        if args.response_specificity_summary.exists()
        else None
    )
    cross_platform_gates = (
        pd.read_csv(args.cross_platform_gates, sep="\t")
        if args.cross_platform_gates.exists()
        else None
    )
    cross_platform_sensitivity = (
        pd.read_csv(args.cross_platform_sensitivity, sep="\t")
        if args.cross_platform_sensitivity.exists()
        else None
    )
    text = build_and_render_recharter_journal_style_draft(
        pd.read_csv(args.route_scores, sep="\t"),
        pd.read_csv(args.benchmark_matrix, sep="\t"),
        pd.read_csv(args.figure_sources, sep="\t"),
        pd.read_csv(args.readiness_audit, sep="\t"),
        pd.read_csv(args.claim_states, sep="\t"),
        pd.read_csv(args.responder_units, sep="\t"),
        pd.read_csv(args.stability_summary, sep="\t"),
        external_stability_summary,
        novelty_upgrades,
        formal_invariant_audit,
        promotion_benchmark_summary,
        generality_summary,
        generality_baseline_summary,
        response_replication_summary,
        response_specificity_summary,
        cross_platform_gates,
        cross_platform_sensitivity,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
