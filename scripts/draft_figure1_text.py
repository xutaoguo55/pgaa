#!/usr/bin/env python3
"""Draft claim-bounded Figure 1 caption and Results text."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.figure1_text import render_figure1_caption_and_results  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate claim-bounded Figure 1 caption and Results text."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "evidence/main_figure_source_data.tsv",
    )
    parser.add_argument("--text-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    figure_sources = pd.read_csv(args.source, sep="\t")
    args.text_out.parent.mkdir(parents=True, exist_ok=True)
    args.text_out.write_text(
        render_figure1_caption_and_results(figure_sources), encoding="utf-8"
    )
    print(f"Wrote {args.text_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
