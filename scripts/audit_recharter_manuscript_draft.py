#!/usr/bin/env python3
"""Audit claim safety of the PGAA recharter manuscript draft."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.recharter_manuscript_audit import (  # noqa: E402
    audit_recharter_manuscript_draft,
    render_recharter_manuscript_audit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit claim safety of the PGAA recharter manuscript draft."
    )
    parser.add_argument(
        "--draft",
        type=Path,
        default=ROOT / "docs/RECHARTER_MANUSCRIPT_DRAFT.md",
    )
    parser.add_argument(
        "--readiness-audit",
        type=Path,
        default=ROOT / "evidence/recharter_readiness_audit.tsv",
    )
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--report-out", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = audit_recharter_manuscript_draft(
        args.draft.read_text(encoding="utf-8"),
        pd.read_csv(args.readiness_audit, sep="\t"),
    )

    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    result.audit.to_csv(args.audit_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(render_recharter_manuscript_audit(result), encoding="utf-8")
    print(f"Verdict: {result.verdict}")
    print(f"Wrote {args.audit_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
