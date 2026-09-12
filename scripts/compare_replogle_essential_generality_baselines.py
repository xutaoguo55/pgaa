#!/usr/bin/env python3
"""Run simple target-recovery baselines on the locked generality inputs."""
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_generality_baselines import (  # noqa: E402
    compile_generality_baselines,
    render_generality_baseline_report,
    summarize_generality_baselines,
)


def main() -> int:
    contract = pd.read_csv(ROOT / "evidence/replogle_essential_generality_contract.tsv", sep="\t")
    pgaa = pd.read_csv(ROOT / "evidence/replogle_essential_generality_results.tsv", sep="\t")
    comparison = compile_generality_baselines(contract, pgaa)
    summary = summarize_generality_baselines(comparison)
    comparison.to_csv(ROOT / "evidence/replogle_essential_generality_baseline_comparison.tsv", sep="\t", index=False)
    summary.to_csv(ROOT / "evidence/replogle_essential_generality_baseline_summary.tsv", sep="\t", index=False)
    (ROOT / "docs/REPLOGLE_ESSENTIAL_GENERALITY_BASELINE_AUDIT.md").write_text(
        render_generality_baseline_report(comparison, summary), encoding="utf-8"
    )
    print(f"Compared {len(comparison)} locked targets with two simple baselines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
