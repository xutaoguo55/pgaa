#!/usr/bin/env python3
"""Import GSE112274 same-cell EGFR T790M and expression data."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.matched_event_expression import (  # noqa: E402
    import_gse112274_event_expression,
    render_gse112274_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression", type=Path, required=True)
    parser.add_argument("--mutation-af", type=Path, required=True)
    parser.add_argument("--mutation-dp", type=Path, required=True)
    parser.add_argument("--expression-out", type=Path, required=True)
    parser.add_argument("--metadata-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--audit-out", type=Path, required=True)
    args = parser.parse_args()

    summary = import_gse112274_event_expression(
        args.expression,
        args.mutation_af,
        args.mutation_dp,
        args.expression_out,
        args.metadata_out,
        args.summary_out,
    )
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.audit_out.write_text(render_gse112274_audit(summary), encoding="utf-8")
    print(f"Wrote {args.expression_out}")
    print(f"Wrote {args.metadata_out}")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.audit_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
