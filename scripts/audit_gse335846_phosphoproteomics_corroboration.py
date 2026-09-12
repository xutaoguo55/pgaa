#!/usr/bin/env python3
"""Build the GSE335846 companion phosphoproteomics corroboration package."""
from __future__ import annotations

import argparse
from pathlib import Path

from pgaa.core.gse335846_phosphoproteomics_corroboration import (
    write_phosphoproteomics_corroboration_assets,
)


ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render the GSE335846 companion phosphoproteomics corroboration package."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm"),
        help="Directory containing the archived DTP source artifacts.",
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm/source_ev1.xlsx"),
        help="Path to the archived Springernature phosphoproteomics workbook.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=Path("evidence/gse335846_phosphoproteomics_corroboration.tsv"),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md"),
    )
    parser.add_argument(
        "--selected-out",
        type=Path,
        default=Path("evidence/gse335846_phosphoproteomics_selected_markers.tsv"),
    )
    parser.add_argument(
        "--boundary-out",
        type=Path,
        default=Path("evidence/gse335846_phosphoproteomics_boundary_scan.tsv"),
    )
    parser.add_argument(
        "--figure-out",
        type=Path,
        default=Path("figures_png/gse335846_phosphoproteomics_corroboration_scorecard.png"),
    )
    parser.add_argument(
        "--figure-pdf-out",
        type=Path,
        default=Path("figures_png/gse335846_phosphoproteomics_corroboration_scorecard.pdf"),
    )
    parser.add_argument(
        "--support-text-out",
        type=Path,
        default=Path("docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION_SUPPORT_TEXT.md"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    workbook = args.workbook if args.workbook.is_absolute() else ROOT / args.workbook
    summary_out = args.summary_out if args.summary_out.is_absolute() else ROOT / args.summary_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    selected_out = args.selected_out if args.selected_out.is_absolute() else ROOT / args.selected_out
    boundary_out = args.boundary_out if args.boundary_out.is_absolute() else ROOT / args.boundary_out
    figure_out = args.figure_out if args.figure_out.is_absolute() else ROOT / args.figure_out
    figure_pdf_out = (
        args.figure_pdf_out if args.figure_pdf_out.is_absolute() else ROOT / args.figure_pdf_out
    )
    support_text_out = (
        args.support_text_out
        if args.support_text_out.is_absolute()
        else ROOT / args.support_text_out
    )
    paths = write_phosphoproteomics_corroboration_assets(
        source_dir=source_dir,
        workbook_path=workbook,
        summary_out=summary_out,
        report_out=report_out,
        selected_out=selected_out,
        boundary_out=boundary_out,
        figure_out=figure_out,
        figure_pdf_out=figure_pdf_out,
        support_text_out=support_text_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

