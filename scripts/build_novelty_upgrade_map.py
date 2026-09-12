#!/usr/bin/env python3
"""Build the PGAA novelty upgrade map and report."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.novelty_upgrade_map import (  # noqa: E402
    build_novelty_upgrade_map,
    render_novelty_upgrade_report,
    summarize_novelty_upgrade_map,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a 100+ point novelty upgrade map for the PGAA recharter."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "evidence/novelty_upgrade_map.tsv",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=ROOT / "evidence/novelty_upgrade_summary.tsv",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=ROOT / "docs/NOVELTY_UPGRADE_MAP.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    upgrades = build_novelty_upgrade_map()
    summary = summarize_novelty_upgrade_map(upgrades)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    upgrades.to_csv(args.out, sep="\t", index=False)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.write_text(
        render_novelty_upgrade_report(upgrades, summary), encoding="utf-8"
    )

    print(f"Wrote {args.out} ({len(upgrades)} rows)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
