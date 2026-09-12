#!/usr/bin/env python3
"""Plan safe import of external single-cell h5ad files for PGAA reruns."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_singlecell_import_plan import (  # noqa: E402
    build_external_singlecell_import_plan,
    render_external_singlecell_import_plan_report,
    summarize_external_singlecell_import_plan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan single-cell matrix import after external target coverage is verified."
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=ROOT / "evidence/external_target_coverage_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--file-manifest",
        type=Path,
        default=ROOT / "evidence/external_singlecell_file_manifest.tsv",
    )
    parser.add_argument("--scratch-dir", type=Path, default=Path("/tmp/pgaa_replogle"))
    parser.add_argument("--safety-multiplier", type=float, default=1.25)
    parser.add_argument("--plan-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_external_singlecell_import_plan(
        pd.read_csv(args.coverage, sep="\t"),
        pd.read_csv(args.file_manifest, sep="\t"),
        args.scratch_dir,
        args.safety_multiplier,
    )
    summary = summarize_external_singlecell_import_plan(plan)

    args.plan_out.parent.mkdir(parents=True, exist_ok=True)
    plan.to_csv(args.plan_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_singlecell_import_plan_report(plan, summary), encoding="utf-8"
    )
    print(f"Wrote {args.plan_out} ({len(plan)} files)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
