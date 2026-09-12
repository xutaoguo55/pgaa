#!/usr/bin/env python3
"""Build an execution contract for external PGAA claim-state reruns."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_claim_state_contract import (  # noqa: E402
    build_external_claim_state_contract,
    render_external_claim_state_contract_report,
    summarize_external_claim_state_contract,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the per-target execution contract for external PGAA reruns."
    )
    parser.add_argument(
        "--readiness",
        type=Path,
        default=ROOT / "evidence/external_rerun_readiness_replogle_k562_gwps.tsv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "external_rerun/replogle_k562_gwps",
    )
    parser.add_argument("--group-column", default="group")
    parser.add_argument("--perturbed-value", default="perturbed")
    parser.add_argument("--control-value", default="control")
    parser.add_argument("--n-perms", type=int, default=2000)
    parser.add_argument("--n-bins", type=int, default=20)
    parser.add_argument("--contract-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    contract = build_external_claim_state_contract(
        pd.read_csv(args.readiness, sep="\t"),
        args.output_dir,
        group_column=args.group_column,
        perturbed_value=args.perturbed_value,
        control_value=args.control_value,
        n_perms=args.n_perms,
        n_bins=args.n_bins,
    )
    summary = summarize_external_claim_state_contract(contract)

    args.contract_out.parent.mkdir(parents=True, exist_ok=True)
    contract.to_csv(args.contract_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_claim_state_contract_report(contract, summary), encoding="utf-8"
    )
    print(f"Wrote {args.contract_out} ({len(contract)} target contracts)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
