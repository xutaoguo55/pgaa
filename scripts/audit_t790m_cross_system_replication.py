#!/usr/bin/env python3
"""Audit EGFR T790M-expression replication across two public systems."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.t790m_cross_system_replication import (  # noqa: E402
    audit_t790m_cross_system_replication,
    render_t790m_cross_system_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cortad-expression", type=Path, required=True)
    parser.add_argument("--cortad-metadata", type=Path, required=True)
    parser.add_argument("--replication-fpkm", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--audit-out", type=Path, required=True)
    args = parser.parse_args()
    summary = audit_t790m_cross_system_replication(
        pd.read_csv(args.cortad_expression, index_col=0),
        pd.read_csv(args.cortad_metadata),
        pd.read_csv(args.replication_fpkm, sep="\t").set_index("name"),
    )
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    args.audit_out.write_text(render_t790m_cross_system_audit(summary), encoding="utf-8")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.audit_out}")
    print(f"Verdict: {summary.iloc[0]['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
