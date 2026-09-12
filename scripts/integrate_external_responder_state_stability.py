#!/usr/bin/env python3
"""Integrate external claim states with responder-state stability."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_responder_state_stability import (  # noqa: E402
    integrate_external_responder_state_stability,
    render_external_responder_state_stability_report,
    summarize_external_responder_state_stability,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Integrate external claim-state rows with internal responder-state stability."
    )
    parser.add_argument(
        "--internal-stability",
        type=Path,
        default=ROOT / "evidence/responder_state_stability_summary.tsv",
    )
    parser.add_argument(
        "--external-claim-states",
        type=Path,
        default=ROOT / "evidence/external_claim_states_replogle_k562_gwps.tsv",
    )
    parser.add_argument("--integrated-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    integrated = integrate_external_responder_state_stability(
        pd.read_csv(args.internal_stability, sep="\t"),
        pd.read_csv(args.external_claim_states, sep="\t"),
    )
    summary = summarize_external_responder_state_stability(integrated)

    args.integrated_out.parent.mkdir(parents=True, exist_ok=True)
    integrated.to_csv(args.integrated_out, sep="\t", index=False)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_external_responder_state_stability_report(integrated, summary),
        encoding="utf-8",
    )
    print(f"Wrote {args.integrated_out} ({len(integrated)} units)")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
