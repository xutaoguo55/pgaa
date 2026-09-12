#!/usr/bin/env python3
"""Build the executable claim-state specification and invariant audit."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.claim_state_formalization import (  # noqa: E402
    audit_claim_state_invariants,
    build_claim_state_space,
    build_claim_transition_rules,
    build_formal_decision_objects,
    render_claim_state_formalization_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Formalize and audit the PGAA claim-state compiler.")
    parser.add_argument("--claims", type=Path, default=ROOT / "evidence/result_claim_states.tsv")
    parser.add_argument("--units", type=Path, default=ROOT / "evidence/responder_state_units.tsv")
    parser.add_argument("--stability", type=Path, default=ROOT / "evidence/responder_state_stability_summary.tsv")
    parser.add_argument("--integrated", type=Path, default=ROOT / "evidence/external_responder_state_stability_integrated.tsv")
    parser.add_argument("--state-space-out", type=Path, default=ROOT / "evidence/claim_state_space.tsv")
    parser.add_argument("--transitions-out", type=Path, default=ROOT / "evidence/claim_transition_rules.tsv")
    parser.add_argument("--objects-out", type=Path, default=ROOT / "evidence/formal_decision_objects.tsv")
    parser.add_argument("--audit-out", type=Path, default=ROOT / "evidence/claim_state_invariant_audit.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/CLAIM_STATE_COMPILER_FORMALIZATION.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    claims = pd.read_csv(args.claims, sep="\t")
    units = pd.read_csv(args.units, sep="\t")
    stability = pd.read_csv(args.stability, sep="\t")
    integrated = pd.read_csv(args.integrated, sep="\t")
    state_space = build_claim_state_space()
    transitions = build_claim_transition_rules()
    objects = build_formal_decision_objects(units, stability, integrated)
    audit = audit_claim_state_invariants(claims, units, stability, integrated, objects)

    for path, frame in (
        (args.state_space_out, state_space),
        (args.transitions_out, transitions),
        (args.objects_out, objects),
        (args.audit_out, audit),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_claim_state_formalization_report(state_space, transitions, objects, audit),
        encoding="utf-8",
    )
    print(f"Wrote {args.report_out}")
    print(f"Invariant verdict: {'PASS' if (audit['status'] == 'pass').all() else 'FAIL'}")
    return 0 if (audit["status"] == "pass").all() else 1


if __name__ == "__main__":
    raise SystemExit(main())
