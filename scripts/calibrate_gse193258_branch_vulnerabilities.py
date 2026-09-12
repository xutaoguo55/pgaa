#!/usr/bin/env python3
"""Calibrate frozen branch scores against GSE193258 drug-screen activity."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.branch_vulnerability_calibration import (
    calibrate_branch_vulnerabilities,
    normalize_combination_activity,
    render_calibration_audit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen", required=True)
    parser.add_argument("--assignments", required=True)
    parser.add_argument("--normalized-out", required=True)
    parser.add_argument("--associations-out", required=True)
    parser.add_argument("--lead-out", required=True)
    parser.add_argument("--audit-out", required=True)
    args = parser.parse_args()
    screen = pd.read_excel(args.screen, header=2)
    assignments = pd.read_csv(args.assignments, sep="\t")
    normalized = normalize_combination_activity(screen)
    associations, lead = calibrate_branch_vulnerabilities(screen, assignments)
    for path, frame in (
        (args.normalized_out, normalized),
        (args.associations_out, associations),
        (args.lead_out, lead),
    ):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
        print(f"Wrote {path}")
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_calibration_audit(associations, lead), encoding="utf-8"
    )
    print(f"Wrote {args.audit_out}")


if __name__ == "__main__":
    main()
