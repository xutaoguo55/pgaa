#!/usr/bin/env python3
"""Check target coverage in an external h5ad candidate dataset."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import scanpy as sc

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_target_coverage import (  # noqa: E402
    build_external_target_coverage,
    render_external_target_coverage_report,
    summarize_external_target_coverage,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify target coverage and control metadata in an external h5ad file."
    )
    parser.add_argument(
        "--candidate-audit",
        type=Path,
        default=ROOT / "evidence/external_dataset_candidate_audit.tsv",
    )
    parser.add_argument("--candidate-dataset-id", required=True)
    parser.add_argument("--h5ad", required=True, type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--coverage-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    adata = sc.read_h5ad(args.h5ad, backed="r")
    coverage = build_external_target_coverage(
        pd.read_csv(args.candidate_audit, sep="\t"),
        adata.obs.copy(),
        args.candidate_dataset_id,
        args.h5ad.name,
        args.source_url,
    )
    summary = summarize_external_target_coverage(coverage)

    args.coverage_out.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(args.coverage_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_target_coverage_report(coverage, summary), encoding="utf-8"
    )
    print(f"Wrote {args.coverage_out} ({len(coverage)} targets)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
