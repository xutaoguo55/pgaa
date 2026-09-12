#!/usr/bin/env python3
"""Run or compile the frozen ten-study expansion-v2 benchmark."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.cross_platform_dual_gate import (  # noqa: E402
    benchmark_platform_dual_gate,
    summarize_platform_dual_gate,
)
from pgaa.core.expansion_v2 import (  # noqa: E402
    frozen_ready_specs,
    load_frozen_candidate_queue,
)
from pgaa.core.expansion_v2_claims import (  # noqa: E402
    evaluate_expansion_v2_claim,
    summarize_expansion_v2_landscape,
)


def _merge(path: Path, incoming: pd.DataFrame, dataset_ids: set[str]) -> pd.DataFrame:
    if not path.exists():
        return incoming
    old = pd.read_csv(path, sep="\t")
    return pd.concat([old[~old["dataset_id"].isin(dataset_ids)], incoming], ignore_index=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", action="append")
    parser.add_argument("--merge-existing", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence")
    args = parser.parse_args(argv)
    specs = frozen_ready_specs()
    known = {spec.dataset_id for spec in specs}
    requested = set(args.dataset_id or known)
    if unknown := sorted(requested - known):
        parser.error(f"unknown or not-yet-contracted dataset ids: {unknown}")
    contract_path = args.output_dir / "expansion_v2_scored_contract.tsv"
    detail_path = args.output_dir / "expansion_v2_dual_gate_detail.tsv"

    if args.compile_only:
        contract = pd.read_csv(contract_path, sep="\t")
        detail = pd.read_csv(detail_path, sep="\t")
    else:
        contracts = []
        details = []
        for spec in specs:
            if spec.dataset_id not in requested:
                continue
            print(f"Running {spec.dataset_id}", flush=True)
            contract, detail = benchmark_platform_dual_gate(
                spec,
                max_units=16,
                max_cells_per_group=70,
                min_cells_per_group=20,
                max_features=5000,
                top_k=100,
                n_repeats=5,
                split_seed="pgaa-cross-platform-dual-gate-v2",
                sampling_seed="pgaa-cross-platform-matched-controls-v2",
            )
            contracts.append(contract)
            details.append(detail)
            print(f"Completed {spec.dataset_id}: {len(contract)} units", flush=True)
        contract = pd.concat(contracts, ignore_index=True)
        detail = pd.concat(details, ignore_index=True)
        if args.merge_existing:
            contract = _merge(contract_path, contract, requested)
            detail = _merge(detail_path, detail, requested)

    target, method, states = summarize_platform_dual_gate(detail)
    metadata = load_frozen_candidate_queue(ROOT)
    claim = evaluate_expansion_v2_claim(states, metadata)
    landscape, portability = summarize_expansion_v2_landscape(states, metadata)
    outputs = {
        contract_path: contract,
        detail_path: detail,
        args.output_dir / "expansion_v2_dual_gate_target_summary.tsv": target,
        args.output_dir / "expansion_v2_dual_gate_method_summary.tsv": method,
        args.output_dir / "expansion_v2_dual_gate_states.tsv": states,
        args.output_dir / "expansion_v2_confirmatory_claim_state.tsv": claim,
        args.output_dir / "expansion_v2_state_landscape.tsv": landscape,
        args.output_dir / "expansion_v2_joint_portability_secondary.tsv": portability,
    }
    for path, frame in outputs.items():
        frame.to_csv(path, sep="\t", index=False)
    print(claim.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
