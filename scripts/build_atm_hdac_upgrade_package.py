#!/usr/bin/env python3
"""Build the ATM/HDAC branch-vulnerability upgrade package."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.atm_hdac_upgrade_package import write_upgrade_package  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write source-data audit, experiment design, and ATM/HDAC upgrade docs."
    )
    parser.add_argument(
        "--drug-associations",
        type=Path,
        default=ROOT / "evidence/gse193258_branch_drug_associations.tsv",
    )
    parser.add_argument(
        "--dynamic-association",
        type=Path,
        default=ROOT / "evidence/gse335846_dynamic_atm_association.tsv",
    )
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "evidence")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm"),
        help="Directory containing archived GSE335846/GSE335848 public-source artifacts.",
    )
    parser.add_argument(
        "--gse193258-source-dir",
        type=Path,
        default=Path("data/external/GSE193258"),
        help="Directory containing the archived GSE193258 screen package.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir
    if not source_dir.is_absolute():
        source_dir = ROOT / source_dir
    gse193258_source_dir = args.gse193258_source_dir
    if not gse193258_source_dir.is_absolute():
        gse193258_source_dir = ROOT / gse193258_source_dir
    paths = write_upgrade_package(
        output_dir=args.output_dir,
        evidence_dir=args.evidence_dir,
        docs_dir=args.docs_dir,
        drug_associations=pd.read_csv(args.drug_associations, sep="\t"),
        dynamic_association=pd.read_csv(args.dynamic_association, sep="\t"),
        source_dir=source_dir,
        gse193258_source_dir=gse193258_source_dir,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
