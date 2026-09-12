#!/usr/bin/env python3
"""Compile PGAA outputs for the locked Replogle essential panel."""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_generality_results import (  # noqa: E402
    compile_generality_results,
    render_generality_results_report,
    summarize_generality_results,
)


def main() -> int:
    contract = pd.read_csv(ROOT / "evidence/replogle_essential_generality_contract.tsv", sep="\t")
    results = compile_generality_results(contract)
    summary = summarize_generality_results(results)
    results.to_csv(ROOT / "evidence/replogle_essential_generality_results.tsv", sep="\t", index=False)
    summary.to_csv(ROOT / "evidence/replogle_essential_generality_results_summary.tsv", sep="\t", index=False)
    (ROOT / "docs/REPLOGLE_ESSENTIAL_GENERALITY_RESULTS.md").write_text(
        render_generality_results_report(results, summary), encoding="utf-8"
    )
    print(f"Compiled {len(results)} locked targets; {int((results['execution_status'] == 'complete').sum())} complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
