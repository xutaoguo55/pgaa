#!/usr/bin/env python3
"""Run matched control-vs-control specificity stress testing."""
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_response_specificity import (  # noqa: E402
    benchmark_response_specificity,
    render_response_specificity_report,
    summarize_response_specificity,
)


def main() -> int:
    contract = pd.read_csv(ROOT / "evidence/replogle_essential_generality_contract.tsv", sep="\t")
    results = benchmark_response_specificity(contract)
    target_level, summary = summarize_response_specificity(results)
    results.to_csv(ROOT / "evidence/replogle_essential_response_specificity.tsv", sep="\t", index=False)
    target_level.to_csv(
        ROOT / "evidence/replogle_essential_response_specificity_target_summary.tsv",
        sep="\t",
        index=False,
    )
    summary.to_csv(
        ROOT / "evidence/replogle_essential_response_specificity_summary.tsv",
        sep="\t",
        index=False,
    )
    (ROOT / "docs/REPLOGLE_ESSENTIAL_RESPONSE_SPECIFICITY.md").write_text(
        render_response_specificity_report(target_level, summary), encoding="utf-8"
    )
    print(
        f"Stress-tested {results['target_gene'].nunique()} targets across "
        f"{results['repeat'].nunique()} matched-control repeats"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
