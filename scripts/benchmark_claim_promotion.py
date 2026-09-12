#!/usr/bin/env python3
"""Run the finite-state claim-promotion contract stress test."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.claim_promotion_benchmark import (  # noqa: E402
    build_claim_promotion_scenarios,
    render_claim_promotion_benchmark_report,
    summarize_claim_promotion_benchmark,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark unsupported claim promotion under exhaustive state mutation.")
    parser.add_argument("--objects", type=Path, default=ROOT / "evidence/formal_decision_objects.tsv")
    parser.add_argument("--scenarios-out", type=Path, default=ROOT / "evidence/claim_promotion_benchmark_scenarios.tsv")
    parser.add_argument("--summary-out", type=Path, default=ROOT / "evidence/claim_promotion_benchmark_summary.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/CLAIM_PROMOTION_ERROR_BENCHMARK.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    objects = pd.read_csv(args.objects, sep="\t")
    scenarios = build_claim_promotion_scenarios(objects)
    summary = summarize_claim_promotion_benchmark(scenarios)
    for path, frame in ((args.scenarios_out, scenarios), (args.summary_out, summary)):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_claim_promotion_benchmark_report(scenarios, summary), encoding="utf-8"
    )
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
