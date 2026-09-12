#!/usr/bin/env python3
"""Build the USB-backed PGAA execution contract for the locked generality panel."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.data_root import data_root  # noqa: E402
from pgaa.core.external_generality_panel import build_generality_execution_contract  # noqa: E402


DEFAULT_H5AD = data_root(
    "claude code大电脑备份data/data/data/"
    "replogle_2022_k562_essential.h5ad"
)
DEFAULT_OUTPUT_DIR = data_root("pgaa_replogle/essential_generality_v1")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=ROOT / "evidence/replogle_essential_generality_panel.tsv")
    parser.add_argument("--h5ad", type=Path, default=DEFAULT_H5AD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--contract-out", type=Path, default=ROOT / "evidence/replogle_essential_generality_contract.tsv")
    args = parser.parse_args(argv)

    contract = build_generality_execution_contract(
        pd.read_csv(args.panel, sep="\t"), args.h5ad, args.output_dir
    )
    args.contract_out.parent.mkdir(parents=True, exist_ok=True)
    contract.to_csv(args.contract_out, sep="\t", index=False)
    print(f"Wrote {len(contract)} locked execution rows to {args.contract_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
