#!/usr/bin/env python3
"""Run the locked held-out-batch response-ranking replication benchmark."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.external_response_replication import (  # noqa: E402
    benchmark_response_replication,
    paired_response_replication_comparisons,
    render_response_replication_report,
    summarize_response_replication,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=ROOT / "evidence/replogle_essential_generality_contract.tsv")
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--n-bins", type=int, default=20)
    parser.add_argument("--split-seed", default="pgaa-response-replication-v1")
    parser.add_argument("--results-out", type=Path, default=ROOT / "evidence/replogle_essential_response_replication.tsv")
    parser.add_argument("--summary-out", type=Path, default=ROOT / "evidence/replogle_essential_response_replication_summary.tsv")
    parser.add_argument("--comparisons-out", type=Path, default=ROOT / "evidence/replogle_essential_response_replication_comparisons.tsv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/REPLOGLE_ESSENTIAL_RESPONSE_REPLICATION.md")
    args = parser.parse_args(argv)

    contract = pd.read_csv(args.contract, sep="\t")
    input_paths = [Path(str(path)) for path in contract["metadata_csv"]]
    if input_paths and not any(path.is_file() for path in input_paths):
        print(
            "No locked metadata inputs are accessible. The contract table records "
            "absolute paths under the external data tree; see "
            "docs/DATA_ROOT_PROVENANCE.md for how to obtain that tree and remap the "
            "paths, then rerun extraction with --metadata-column batch before "
            "benchmarking.",
            file=sys.stderr,
        )
        return 2
    results = benchmark_response_replication(
        contract,
        top_k=args.top_k,
        n_bins=args.n_bins,
        split_seed=args.split_seed,
        batch_universe=[str(batch) for batch in range(1, 49)],
    )
    summary = summarize_response_replication(results)
    comparisons = paired_response_replication_comparisons(results)
    for path, frame in (
        (args.results_out, results),
        (args.summary_out, summary),
        (args.comparisons_out, comparisons),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_response_replication_report(results, summary, comparisons), encoding="utf-8"
    )
    print(
        f"Benchmarked {results['target_gene'].nunique()} locked targets; "
        f"{results.loc[results['status'].eq('complete'), 'target_gene'].nunique()} completed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
