#!/usr/bin/env python3
"""Build the GSE335846 external dynamic corroboration audit."""
from __future__ import annotations

import argparse
from pathlib import Path

from pgaa.core.gse335846_external_dynamic_corroboration import (
    write_external_dynamic_corroboration_package,
)

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE335846 external dynamic corroboration audit."
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    preprint = args.preprint if args.preprint.is_absolute() else ROOT / args.preprint
    summary_out = args.summary_out if args.summary_out.is_absolute() else ROOT / args.summary_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    paths = write_external_dynamic_corroboration_package(
        source_dir=source_dir,
        preprint_path=preprint,
        summary_out=summary_out,
        report_out=report_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
