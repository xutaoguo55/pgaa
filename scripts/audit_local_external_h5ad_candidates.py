#!/usr/bin/env python3
"""Audit local USB h5ad candidates for identity, controls, and target coverage."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.data_root import data_root  # noqa: E402
from pgaa.core.local_h5ad_candidate_audit import (  # noqa: E402
    audit_local_h5ad_candidates,
    render_local_h5ad_candidate_report,
)


DEFAULT_CANDIDATES = [
    ("replogle_essential_compact", data_root("claude code大电脑备份data/data/data/replogle_2022_k562_essential.h5ad")),
    ("replogle_essential_large", data_root("claude code大电脑备份data/data/perturbseq/replogle_2022_k562_essential.h5ad")),
    ("replogle_exp6", data_root("Mac_backup_20260713/WorkBuddy/20260330230010/foundation_model_benchmark/carf_benchmark/raw/replogle_2022_genome_scale/Replogle_exp6.h5ad")),
    ("replogle_k562_gwps_reference", data_root("pgaa_replogle/K562_gwps_raw_singlecell_01.h5ad")),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only audit of local external h5ad candidates.")
    parser.add_argument("--objects", type=Path, default=ROOT / "evidence/formal_decision_objects.tsv")
    parser.add_argument("--audit-out", type=Path, default=ROOT / "evidence/local_external_h5ad_candidate_audit.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/LOCAL_EXTERNAL_H5AD_CANDIDATE_AUDIT.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    objects = pd.read_csv(args.objects, sep="\t")
    targets = {str(context).split("_")[0] for context in objects["context"]}
    audit = audit_local_h5ad_candidates(DEFAULT_CANDIDATES, targets)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.audit_out, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(render_local_h5ad_candidate_report(audit, targets), encoding="utf-8")
    print(f"Wrote {args.report_out}")
    print(f"Replication-eligible distinct matrices: {int(audit['replication_claim_eligible'].sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
