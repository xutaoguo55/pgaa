#!/usr/bin/env python3
"""Build the GSE193258 target-specificity audit package."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.gse193258_drug_screen_source_audit import (  # noqa: E402
    build_gse193258_drug_screen_source_audit,
)
from pgaa.core.gse193258_target_specificity_audit import (  # noqa: E402
    write_gse193258_target_specificity_audit_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE193258 target-specificity audit and report."
    )
    parser.add_argument(
        "--drug-associations",
        type=Path,
        default=ROOT / "evidence/gse193258_branch_drug_associations.tsv",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=ROOT / "data/external/GSE193258",
        help="Directory containing the archived GSE193258 screen package.",
    )
    parser.add_argument("--evidence-out", type=Path, default=ROOT / "evidence/gse193258_target_specificity.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir
    if not source_dir.is_absolute():
        source_dir = ROOT / source_dir
    _, _, target_context = build_gse193258_drug_screen_source_audit(source_dir)
    paths = write_gse193258_target_specificity_audit_package(
        drug_associations=pd.read_csv(args.drug_associations, sep="\t"),
        evidence_out=args.evidence_out,
        report_out=args.report_out,
        target_context=target_context,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
