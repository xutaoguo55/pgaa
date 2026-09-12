#!/usr/bin/env python3
"""Build immune-evidence tiers for PGAA event-peptide-HLA candidates."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.immune_evidence import (
    annotate_public_evidence,
    build_immune_evidence_ladder,
    render_claim_audit_markdown,
    scan_placeholder_artifacts,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert PGAA event-peptide-HLA candidates into a public-evidence "
            "A-D tier table. This is a prioritization audit, not wet-lab validation."
        )
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--annotated-candidates",
        type=Path,
        help="Optional path for candidates after ligand/T-cell evidence annotation.",
    )
    parser.add_argument(
        "--ligand-evidence",
        type=Path,
        help="Optional TSV with public immunopeptidome/HLA ligand evidence.",
    )
    parser.add_argument(
        "--tcell-evidence",
        type=Path,
        help="Optional TSV with public peptide/T-cell evidence.",
    )
    parser.add_argument(
        "--decoys",
        type=Path,
        help="Optional TSV with matched decoy peptides for background match rates.",
    )
    parser.add_argument(
        "--claim-audit",
        type=Path,
        help="Optional Markdown report summarizing allowed and prohibited claims.",
    )
    parser.add_argument(
        "--allow-smoke",
        action="store_true",
        help="Allow template/smoke/example tokens in inputs and outputs.",
    )
    return parser


def _read_optional_tsv(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    return pd.read_csv(path, sep="\t")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidates = pd.read_csv(args.candidates, sep="\t")
    ligand_evidence = _read_optional_tsv(args.ligand_evidence)
    tcell_evidence = _read_optional_tsv(args.tcell_evidence)
    decoys = _read_optional_tsv(args.decoys)

    if not args.allow_smoke:
        placeholder_hits = []
        placeholder_hits.extend(scan_placeholder_artifacts(candidates, "candidates"))
        if ligand_evidence is not None:
            placeholder_hits.extend(
                scan_placeholder_artifacts(ligand_evidence, "ligand_evidence")
            )
        if tcell_evidence is not None:
            placeholder_hits.extend(
                scan_placeholder_artifacts(tcell_evidence, "tcell_evidence")
            )
        if decoys is not None:
            placeholder_hits.extend(scan_placeholder_artifacts(decoys, "decoys"))
        if placeholder_hits:
            joined = "\n  - ".join(placeholder_hits)
            raise ValueError(
                "Smoke/template tokens detected. Use --allow-smoke only for "
                f"examples, never for manuscript analyses:\n  - {joined}"
            )

    annotated = annotate_public_evidence(
        candidates,
        ligand_evidence=ligand_evidence,
        tcell_evidence=tcell_evidence,
        decoys=decoys,
    )
    if args.annotated_candidates:
        args.annotated_candidates.parent.mkdir(parents=True, exist_ok=True)
        annotated.to_csv(args.annotated_candidates, sep="\t", index=False)
    tiers = build_immune_evidence_ladder(annotated)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tiers.to_csv(args.output, sep="\t", index=False)
    if args.claim_audit:
        args.claim_audit.parent.mkdir(parents=True, exist_ok=True)
        args.claim_audit.write_text(render_claim_audit_markdown(tiers), encoding="utf-8")
    print(f"Wrote {args.output} ({len(tiers)} candidates)")
    if args.claim_audit:
        print(f"Wrote {args.claim_audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
