#!/usr/bin/env python3
"""Build the GSE150949 PC9 evolution audit package."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.gse150949_pc9_evolution_audit import (  # noqa: E402
    write_gse150949_pc9_evolution_assets,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the GSE150949 PC9 evolution audit package."
    )
    parser.add_argument(
        "--state-modules",
        type=Path,
        default=Path("evidence/gse75602_resistance_state_modules.tsv"),
        help="Frozen down-module state table used for the route definition.",
    )
    parser.add_argument(
        "--annotation",
        type=Path,
        default=Path("evidence/gse75602_resistance_down_module_ensembl_annotation.tsv"),
        help="Gene annotation table for the frozen route.",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/gse150949/GSE150949_metaData_with_lineage.txt.gz"),
        help="Lineage-aware metadata table for GSE150949.",
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("data/gse150949/GSE150949_pc9_count_matrix.csv.gz"),
        help="Gene-by-cell count matrix for GSE150949.",
    )
    parser.add_argument(
        "--figure-out",
        type=Path,
        default=Path("figures_png/gse150949_pc9_evolution_scorecard.png"),
    )
    parser.add_argument(
        "--figure-pdf-out",
        type=Path,
        default=Path("figures_png/gse150949_pc9_evolution_scorecard.pdf"),
    )
    parser.add_argument(
        "--audit-out",
        type=Path,
        default=Path("docs/GSE150949_PC9_EVOLUTION_AUDIT.md"),
    )
    parser.add_argument(
        "--support-text-out",
        type=Path,
        default=Path("docs/GSE150949_PC9_EVOLUTION_SUPPORT_TEXT.md"),
    )
    parser.add_argument(
        "--coverage-out",
        type=Path,
        default=Path("evidence/gse150949_pc9_module_coverage.tsv"),
    )
    parser.add_argument(
        "--route-scores-out",
        type=Path,
        default=Path("evidence/gse150949_pc9_route_scores.tsv"),
    )
    parser.add_argument(
        "--sample-summary-out",
        type=Path,
        default=Path("evidence/gse150949_pc9_sample_summary.tsv"),
    )
    parser.add_argument(
        "--group-summary-out",
        type=Path,
        default=Path("evidence/gse150949_pc9_group_summary.tsv"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else ROOT / path

    paths = write_gse150949_pc9_evolution_assets(
        state_modules_path=resolve(args.state_modules),
        annotation_path=resolve(args.annotation),
        metadata_path=resolve(args.metadata),
        matrix_path=resolve(args.matrix),
        figure_out=resolve(args.figure_out),
        figure_pdf_out=resolve(args.figure_pdf_out),
        audit_out=resolve(args.audit_out),
        support_text_out=resolve(args.support_text_out),
        coverage_out=resolve(args.coverage_out),
        route_scores_out=resolve(args.route_scores_out),
        sample_summary_out=resolve(args.sample_summary_out),
        group_summary_out=resolve(args.group_summary_out),
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
