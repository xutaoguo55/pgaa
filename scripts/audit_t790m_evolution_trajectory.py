#!/usr/bin/env python3
"""Audit GSE75602 early/late T790M EGFR expression trajectories."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.t790m_evolution_trajectory import (  # noqa: E402
    audit_t790m_evolution_trajectory,
    evolution_trajectory_verdict,
    render_t790m_evolution_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpm", type=Path, required=True)
    parser.add_argument("--stages-out", type=Path, required=True)
    parser.add_argument("--contrasts-out", type=Path, required=True)
    parser.add_argument("--audit-out", type=Path, required=True)
    args = parser.parse_args()
    cpm = pd.read_csv(args.cpm, sep="\t").set_index("Unnamed: 0")
    stages, contrasts = audit_t790m_evolution_trajectory(cpm)
    for path in (args.stages_out, args.contrasts_out, args.audit_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    stages.to_csv(args.stages_out, sep="\t", index=False)
    contrasts.to_csv(args.contrasts_out, sep="\t", index=False)
    args.audit_out.write_text(render_t790m_evolution_audit(stages, contrasts), encoding="utf-8")
    print(f"Wrote {args.stages_out}")
    print(f"Wrote {args.contrasts_out}")
    print(f"Wrote {args.audit_out}")
    print(f"Verdict: {evolution_trajectory_verdict(contrasts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
