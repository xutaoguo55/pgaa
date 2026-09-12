#!/usr/bin/env python3
"""Build Bioinformatics-first method-upgrade artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.bioinformatics_method_upgrade import (  # noqa: E402
    write_bioinformatics_upgrade_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write Bioinformatics method-positioning and upgrade artifacts."
    )
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "evidence")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = write_bioinformatics_upgrade_package(
        evidence_dir=args.evidence_dir,
        docs_dir=args.docs_dir,
    )
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
