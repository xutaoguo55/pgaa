#!/usr/bin/env python3
"""Build PGAA failure-mode audit artifacts from existing benchmark tables."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.failure_mode_audit import (
    build_failure_mode_audit,
    render_failure_mode_report,
    summarize_failure_mode_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert PGAA calibration and sensitivity outputs into failure-mode audits."
    )
    parser.add_argument(
        "--calibration",
        type=Path,
        default=ROOT / "scripts/table2_s2_calibration.csv",
    )
    parser.add_argument(
        "--sensitivity",
        type=Path,
        default=ROOT / "scripts/sensitivity_s2_bins.csv",
    )
    parser.add_argument(
        "--norman-summary",
        type=Path,
        default=ROOT / "scripts/norman_multi_perturbation_summary.csv",
    )
    parser.add_argument(
        "--adamson-full",
        type=Path,
        default=ROOT / "scripts/adamson2016_full_results.csv",
    )
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    calibration = pd.read_csv(args.calibration)
    sensitivity = pd.read_csv(args.sensitivity)
    norman = pd.read_csv(args.norman_summary)
    adamson_full = pd.read_csv(args.adamson_full)
    audit = build_failure_mode_audit(calibration, sensitivity, norman, adamson_full)
    summary = summarize_failure_mode_audit(audit)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.audit_out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(render_failure_mode_report(audit, summary), encoding="utf-8")
    print(f"Wrote {args.audit_out} ({len(audit)} rows)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
