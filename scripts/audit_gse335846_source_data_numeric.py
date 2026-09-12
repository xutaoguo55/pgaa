#!/usr/bin/env python3
"""Rebuild the GSE335846 source-data numerical audit."""
from __future__ import annotations

import argparse
from pathlib import Path

from pgaa.core.atm_hdac_upgrade_package import (
    annotate_local_artifacts,
    build_author_request_rows,
    build_source_data_audit,
    render_source_data_audit,
)

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE335846 source-data numerical audit."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("sources/gse335846_dynamic_atm"),
        help="Directory containing the archived GSE335846 source artifacts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Repository root used to resolve relative artifact paths.",
    )
    parser.add_argument(
        "--evidence-out",
        type=Path,
        default=Path("evidence/gse335846_source_data_numeric_audit.tsv"),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("docs/GSE335846_SOURCE_DATA_NUMERIC_AUDIT.md"),
    )
    return parser


def build_source_data_numeric_audit_package(
    source_dir: Path,
    output_dir: Path,
    evidence_out: Path,
    report_out: Path,
) -> dict[str, Path]:
    audit = build_source_data_audit(source_dir)
    annotate_local_artifacts(audit, output_dir)
    requests = build_author_request_rows()

    evidence_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(evidence_out, sep="\t", index=False)
    report_out.write_text(render_source_data_audit(audit, requests), encoding="utf-8")
    return {"evidence": evidence_out, "report": report_out}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_dir = args.source_dir if args.source_dir.is_absolute() else ROOT / args.source_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    evidence_out = args.evidence_out if args.evidence_out.is_absolute() else ROOT / args.evidence_out
    report_out = args.report_out if args.report_out.is_absolute() else ROOT / args.report_out
    paths = build_source_data_numeric_audit_package(
        source_dir=source_dir,
        output_dir=output_dir,
        evidence_out=evidence_out,
        report_out=report_out,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
