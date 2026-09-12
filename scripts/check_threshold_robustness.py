#!/usr/bin/env python3
"""Run threshold robustness checks for immune-evidence tier tables."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.immune_evidence import scan_placeholder_artifacts
from pgaa.core.threshold_robustness import compare_threshold_robustness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Stress-test immune-evidence tiers under stricter exact-match and "
            "decoy-background rules."
        )
    )
    parser.add_argument("--tiers", required=True, type=Path)
    parser.add_argument("--adjusted-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument(
        "--allow-smoke",
        action="store_true",
        help="Allow template/smoke/example tokens in input and output.",
    )
    return parser


def _write_tsv(path: Path, table: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, sep="\t", index=False)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tiers = pd.read_csv(args.tiers, sep="\t")
    if not args.allow_smoke:
        placeholder_hits = scan_placeholder_artifacts(tiers, "tiers")
        if placeholder_hits:
            joined = "\n  - ".join(placeholder_hits)
            raise ValueError(
                "Smoke/template tokens detected. Use --allow-smoke only for "
                f"examples, never for manuscript analyses:\n  - {joined}"
            )
    adjusted, summary = compare_threshold_robustness(tiers, top_n=args.top_n)
    _write_tsv(args.adjusted_out, adjusted)
    _write_tsv(args.summary_out, summary)
    print(f"Wrote {args.adjusted_out} ({len(adjusted)} scenario rows)")
    print(f"Wrote {args.summary_out} ({len(summary)} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
