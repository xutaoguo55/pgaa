#!/usr/bin/env python3
"""Build the GSE75602 resistance-module biology audit."""
from __future__ import annotations

import argparse
from pathlib import Path

from pgaa.core.gse75602_resistance_module_biology import (
    write_module_biology_audit_package,
)

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE75602 resistance-module biology audit."
    )
    parser.add_argument(
        "--annotation",
        type=Path,
        required=True,
        help="Path to gse75602_resistance_down_module_ensembl_annotation.tsv",
    )
    parser.add_argument(
        "--pathway-enrichment",
        type=Path,
        required=True,
        help="Path to gse75602_resistance_down_module_pathway_enrichment.tsv",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        required=True,
        help="Output path for gse75602_resistance_down_module_biology_summary.tsv",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        required=True,
        help="Output path for GSE75602_RESISTANCE_MODULE_BIOLOGY_AUDIT.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    annotation = args.annotation if args.annotation.is_absolute() else ROOT / args.annotation
    pathway_enrichment = (
        args.pathway_enrichment
        if args.pathway_enrichment.is_absolute()
        else ROOT / args.pathway_enrichment
    )
    summary_out = args.summary_out if args.summary_out.is_absolute() else ROOT / args.summary_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    paths = write_module_biology_audit_package(
        annotation_path=annotation,
        pathway_enrichment_path=pathway_enrichment,
        summary_out=summary_out,
        report_out=report_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
