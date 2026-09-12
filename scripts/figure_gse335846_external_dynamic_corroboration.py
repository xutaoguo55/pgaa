#!/usr/bin/env python3
"""Build the GSE335846 external dynamic corroboration scorecard."""
from __future__ import annotations

import argparse
from pathlib import Path

from pgaa.core.gse335846_external_dynamic_corroboration import (
    write_external_dynamic_corroboration_assets,
)

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render the GSE335846 external dynamic corroboration figure and support text."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm"),
        help="Directory containing the archived GSE335846 source artifacts.",
    )
    parser.add_argument(
        "--preprint",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm/preprint_733326.txt"),
        help="Path to the archived preprint text.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=Path("evidence/gse335846_external_dynamic_corroboration.tsv"),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION.md"),
    )
    parser.add_argument(
        "--timecourse",
        type=Path,
        default=Path("evidence/gse335846_dynamic_atm_timecourse.tsv"),
    )
    parser.add_argument(
        "--branch-scores",
        type=Path,
        default=Path("evidence/gse335846_rna_seq_branch_axis_scores.tsv"),
    )
    parser.add_argument(
        "--marker-summary",
        type=Path,
        default=Path("evidence/gse335846_rna_seq_branch_axis_source_summary.tsv"),
    )
    parser.add_argument(
        "--association",
        type=Path,
        default=Path("evidence/gse335846_dynamic_atm_association.tsv"),
    )
    parser.add_argument(
        "--figure-out",
        type=Path,
        default=Path("figures_png/gse335846_dynamic_corroboration_scorecard.png"),
    )
    parser.add_argument(
        "--figure-pdf-out",
        type=Path,
        default=Path("figures_png/gse335846_dynamic_corroboration_scorecard.pdf"),
    )
    parser.add_argument(
        "--support-text-out",
        type=Path,
        default=Path("docs/GSE335846_EXTERNAL_DYNAMIC_CORROBORATION_SUPPORT_TEXT.md"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    preprint = args.preprint if args.preprint.is_absolute() else ROOT / args.preprint
    summary_out = args.summary_out if args.summary_out.is_absolute() else ROOT / args.summary_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    timecourse = args.timecourse if args.timecourse.is_absolute() else ROOT / args.timecourse
    branch_scores = (
        args.branch_scores if args.branch_scores.is_absolute() else ROOT / args.branch_scores
    )
    marker_summary = (
        args.marker_summary if args.marker_summary.is_absolute() else ROOT / args.marker_summary
    )
    association = args.association if args.association.is_absolute() else ROOT / args.association
    figure_out = args.figure_out if args.figure_out.is_absolute() else ROOT / args.figure_out
    figure_pdf_out = (
        args.figure_pdf_out if args.figure_pdf_out.is_absolute() else ROOT / args.figure_pdf_out
    )
    support_text_out = (
        args.support_text_out
        if args.support_text_out.is_absolute()
        else ROOT / args.support_text_out
    )
    paths = write_external_dynamic_corroboration_assets(
        source_dir=source_dir,
        preprint_path=preprint,
        summary_out=summary_out,
        report_out=report_out,
        timecourse_path=timecourse,
        branch_scores_path=branch_scores,
        marker_summary_path=marker_summary,
        association_path=association,
        figure_out=figure_out,
        figure_pdf_out=figure_pdf_out,
        support_text_out=support_text_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
