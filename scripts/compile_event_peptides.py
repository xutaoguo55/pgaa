#!/usr/bin/env python3
"""Compile event sequence contexts into peptide-HLA candidates and decoys."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.event_peptide_compiler import EventCompilerConfig, compile_event_peptides
from pgaa.core.immune_evidence import scan_placeholder_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create event-containing peptide-HLA candidate units from altered "
            "amino-acid sequence contexts. This script refuses smoke/template "
            "tokens unless --allow-smoke is set."
        )
    )
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--candidates-out", required=True, type=Path)
    parser.add_argument("--decoys-out", required=True, type=Path)
    parser.add_argument("--max-decoys-per-candidate", type=int, default=1)
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
    events = pd.read_csv(args.events, sep="\t")
    if not args.allow_smoke:
        placeholder_hits = scan_placeholder_artifacts(events, "events")
        if placeholder_hits:
            joined = "\n  - ".join(placeholder_hits)
            raise ValueError(
                "Smoke/template tokens detected. Use --allow-smoke only for "
                f"examples, never for manuscript analyses:\n  - {joined}"
            )

    candidates, decoys = compile_event_peptides(
        events,
        EventCompilerConfig(max_decoys_per_candidate=args.max_decoys_per_candidate),
    )
    if not args.allow_smoke:
        placeholder_hits = []
        placeholder_hits.extend(scan_placeholder_artifacts(candidates, "candidates"))
        placeholder_hits.extend(scan_placeholder_artifacts(decoys, "decoys"))
        if placeholder_hits:
            joined = "\n  - ".join(placeholder_hits)
            raise ValueError(
                "Smoke/template tokens were emitted. Review event identifiers before "
                f"manuscript use:\n  - {joined}"
            )

    _write_tsv(args.candidates_out, candidates)
    _write_tsv(args.decoys_out, decoys)
    print(f"Wrote {args.candidates_out} ({len(candidates)} candidates)")
    print(f"Wrote {args.decoys_out} ({len(decoys)} decoys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
