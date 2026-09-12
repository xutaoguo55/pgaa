#!/usr/bin/env python3
"""Audit whether the PGAA recharter has real non-smoke evidence artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_readiness import (
    audit_recharter_readiness,
    readiness_verdict,
    render_readiness_markdown,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a go/no-go readiness audit for the PGAA top-journal recharter."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--markdown-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audit = audit_recharter_readiness(args.root)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.audit_out, sep="\t", index=False)
    args.markdown_out.write_text(render_readiness_markdown(audit), encoding="utf-8")
    print(f"Wrote {args.audit_out} ({len(audit)} checks)")
    print(f"Wrote {args.markdown_out}")
    print(f"Verdict: {readiness_verdict(audit)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
