#!/usr/bin/env python3
"""Audit whether existing PGAA source tables can support event-peptide compilation."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.event_source_audit import (
    audit_event_sources,
    render_event_source_audit_markdown,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Classify candidate source tables as event-ready, gene-level-only, "
            "peptide-only, unsupported, or missing."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--markdown-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = pd.read_csv(args.manifest, sep="\t")
    audit = audit_event_sources(manifest, args.root)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.audit_out, sep="\t", index=False)
    args.markdown_out.write_text(render_event_source_audit_markdown(audit), encoding="utf-8")
    event_ready = int((audit["status"] == "event_ready").sum())
    print(f"Wrote {args.audit_out} ({len(audit)} sources; {event_ready} event-ready)")
    print(f"Wrote {args.markdown_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
