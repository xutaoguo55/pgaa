#!/usr/bin/env python3
"""Render PGAA recharter Figure 1 from generated source data."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.main_figure_rendering import (  # noqa: E402
    render_figure1,
    render_figure1_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render Figure 1 from evidence/main_figure_source_data.tsv."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "evidence/main_figure_source_data.tsv",
    )
    parser.add_argument("--png-out", required=True, type=Path)
    parser.add_argument("--pdf-out", type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    figure_sources = pd.read_csv(args.source, sep="\t")
    metadata = render_figure1(figure_sources, args.png_out, args.pdf_out)

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_figure1_report(metadata, figure_sources), encoding="utf-8"
    )

    print(f"Wrote {metadata['png']}")
    if metadata["pdf"]:
        print(f"Wrote {metadata['pdf']}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
