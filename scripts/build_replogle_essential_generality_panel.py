#!/usr/bin/env python3
"""Build the locked Replogle essential cross-target generality panel."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.data_root import data_root  # noqa: E402
from pgaa.core.external_generality_panel import (  # noqa: E402
    build_generality_panel_from_h5ad,
    render_generality_panel_report,
)


DEFAULT_H5AD = data_root(
    "claude code大电脑备份data/data/data/"
    "replogle_2022_k562_essential.h5ad"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h5ad", type=Path, default=DEFAULT_H5AD)
    parser.add_argument("--objects", type=Path, default=ROOT / "evidence/formal_decision_objects.tsv")
    parser.add_argument("--candidates-out", type=Path, default=ROOT / "evidence/replogle_essential_generality_readiness.tsv")
    parser.add_argument("--panel-out", type=Path, default=ROOT / "evidence/replogle_essential_generality_panel.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/REPLOGLE_ESSENTIAL_GENERALITY_PANEL.md")
    parser.add_argument("--min-target-cells", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    objects = pd.read_csv(args.objects, sep="\t")
    excluded = {str(context).split("_")[0] for context in objects["context"]}
    candidates, panel, shape = build_generality_panel_from_h5ad(
        args.h5ad, excluded, min_target_cells=args.min_target_cells
    )
    for output in (args.candidates_out, args.panel_out, args.report_out):
        output.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(args.candidates_out, sep="\t", index=False)
    panel.to_csv(args.panel_out, sep="\t", index=False)
    args.report_out.write_text(
        render_generality_panel_report(
            panel, candidates, args.h5ad, shape, excluded, args.min_target_cells
        ),
        encoding="utf-8",
    )
    print(f"Wrote locked panel with {len(panel)} targets to {args.panel_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
