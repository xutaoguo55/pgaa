#!/usr/bin/env python3
"""Extract PGAA CLI input CSVs from an external h5ad rerun contract."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_pgaa_input_extraction import (  # noqa: E402
    extract_external_pgaa_inputs,
    render_external_pgaa_input_extraction_report,
    summarize_external_pgaa_input_extraction,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract target/control PGAA CLI inputs from an external single-cell h5ad."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "evidence/external_claim_state_contract_replogle_k562_gwps.tsv",
    )
    parser.add_argument("--label-column", default=None)
    parser.add_argument("--group-column", default="group")
    parser.add_argument("--perturbed-value", default="perturbed")
    parser.add_argument("--control-value", default="control")
    parser.add_argument("--no-write-files", action="store_true")
    parser.add_argument("--max-control-cells", type=int, default=None)
    parser.add_argument("--control-sampling-seed", default="pgaa-control-v1")
    parser.add_argument("--exact-label-matching", action="store_true")
    parser.add_argument(
        "--metadata-column",
        action="append",
        default=[],
        help="Source obs column to retain in metadata; repeat for multiple columns.",
    )
    parser.add_argument("--extraction-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    extraction = extract_external_pgaa_inputs(
        pd.read_csv(args.contract, sep="\t"),
        label_column=args.label_column,
        group_column=args.group_column,
        perturbed_value=args.perturbed_value,
        control_value=args.control_value,
        write_files=not args.no_write_files,
        max_control_cells=args.max_control_cells,
        control_sampling_seed=args.control_sampling_seed,
        exact_label_matching=args.exact_label_matching,
        metadata_columns=args.metadata_column,
    )
    summary = summarize_external_pgaa_input_extraction(extraction)

    args.extraction_out.parent.mkdir(parents=True, exist_ok=True)
    extraction.to_csv(args.extraction_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_pgaa_input_extraction_report(extraction, summary),
        encoding="utf-8",
    )
    print(f"Wrote {args.extraction_out} ({len(extraction)} targets)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
