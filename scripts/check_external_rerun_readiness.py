#!/usr/bin/env python3
"""Check readiness for an external single-cell PGAA rerun."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_rerun_readiness import (  # noqa: E402
    build_external_rerun_readiness,
    render_external_rerun_readiness_report,
    summarize_external_rerun_readiness,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight an external single-cell h5ad before PGAA/comparator rerun."
    )
    parser.add_argument(
        "--import-plan",
        type=Path,
        default=ROOT / "evidence/external_singlecell_import_plan_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=ROOT / "evidence/external_target_coverage_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--candidate-dataset-id",
        default="replogle_2022_k562_gwps",
    )
    parser.add_argument(
        "--singlecell-h5ad",
        required=True,
        type=Path,
        help="Local path to the matching external single-cell h5ad.",
    )
    parser.add_argument("--include-all-priority-targets", action="store_true")
    parser.add_argument("--readiness-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    readiness = build_external_rerun_readiness(
        pd.read_csv(args.import_plan, sep="\t"),
        pd.read_csv(args.coverage, sep="\t"),
        args.singlecell_h5ad,
        candidate_dataset_id=args.candidate_dataset_id,
        require_tier1_only=not args.include_all_priority_targets,
    )
    summary = summarize_external_rerun_readiness(readiness)

    args.readiness_out.parent.mkdir(parents=True, exist_ok=True)
    readiness.to_csv(args.readiness_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_rerun_readiness_report(readiness, summary), encoding="utf-8"
    )
    status = readiness.iloc[0]["singlecell_gate_status"]
    print(f"Wrote {args.readiness_out} (status={status})")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
