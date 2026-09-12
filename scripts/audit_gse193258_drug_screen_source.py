#!/usr/bin/env python3
"""Build the GSE193258 drug-screen source audit."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.gse193258_drug_screen_source_audit import (  # noqa: E402
    write_gse193258_drug_screen_source_audit_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE193258 drug-screen source audit."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("data/external/GSE193258"),
        help="Directory containing the archived GSE193258 source artifacts.",
    )
    parser.add_argument(
        "--evidence-out",
        type=Path,
        default=Path("evidence/gse193258_drug_screen_source_audit.tsv"),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    evidence_out = args.evidence_out if args.evidence_out.is_absolute() else ROOT / args.evidence_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    paths = write_gse193258_drug_screen_source_audit_package(
        source_dir=source_dir,
        evidence_out=evidence_out,
        report_out=report_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
