#!/usr/bin/env python3
"""Build the external PGAA execution manifest from contract and extraction gates."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_pgaa_execution_manifest import (  # noqa: E402
    build_external_pgaa_execution_manifest,
    render_external_pgaa_execution_manifest_report,
    summarize_external_pgaa_execution_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an audit manifest for external PGAA CLI execution and outputs."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "evidence/external_claim_state_contract_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--extraction",
        type=Path,
        default=ROOT / "evidence/external_pgaa_input_extraction_replogle_k562_gwps.tsv",
    )
    parser.add_argument("--manifest-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = build_external_pgaa_execution_manifest(
        pd.read_csv(args.contract, sep="\t"),
        pd.read_csv(args.extraction, sep="\t"),
    )
    summary = summarize_external_pgaa_execution_manifest(manifest)

    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.manifest_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_pgaa_execution_manifest_report(manifest, summary),
        encoding="utf-8",
    )
    print(f"Wrote {args.manifest_out} ({len(manifest)} targets)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
