#!/usr/bin/env python3
"""Run or compile the frozen expansion-v3 combined ready-panel benchmark."""
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
from pgaa.core.expansion_v3 import frozen_v3_combined_ready_specs  # noqa: E402
from pgaa.core.expansion_v3_claims import evaluate_expansion_v3_endpoint  # noqa: E402


FROZEN_MAX_UNITS = 16
FROZEN_MAX_CELLS_PER_GROUP = 70
FROZEN_MIN_CELLS_PER_GROUP = 20
FROZEN_MAX_FEATURES = 5000
FROZEN_TOP_K = 100
FROZEN_N_REPEATS = 5
DEFAULT_ANALYSIS_PREFIX = "expansion_v3_ready_panel"


def _merge(path: Path, incoming: pd.DataFrame, dataset_ids: set[str]) -> pd.DataFrame:
    if not path.exists():
        return incoming
    old = pd.read_csv(path, sep="\t")
    return pd.concat([old[~old["dataset_id"].isin(dataset_ids)], incoming], ignore_index=True)


def _write_execution_plan(specs, output_path: Path, ready_panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metadata = ready_panel.set_index("candidate_id")
    for spec in specs:
        source = Path(spec.path)
        row = metadata.loc[spec.dataset_id]
        rows.append(
            {
                "dataset_id": spec.dataset_id,
                "platform": spec.platform,
                "source_h5ad": str(source),
                "source_size_bytes": source.stat().st_size if source.is_file() else 0,
                "laboratory_group": row["laboratory_group"],
                "cell_context_class": row["cell_context_class"],
                "perturbation_mechanism": row["perturbation_mechanism"],
                "adapter": spec.adapter,
                "split_column": spec.batch_column,
                "split_strength": spec.split_strength,
                "ready_selected_units": int(row["n_selected_units"]),
                "source_available": source.is_file(),
            }
        )
    plan = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plan.to_csv(output_path, sep="\t", index=False)
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", action="append")
    parser.add_argument("--merge-existing", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--analysis-prefix", default=DEFAULT_ANALYSIS_PREFIX)
    parser.add_argument("--max-units", type=int, default=FROZEN_MAX_UNITS)
    parser.add_argument("--max-cells-per-group", type=int, default=FROZEN_MAX_CELLS_PER_GROUP)
    parser.add_argument("--min-cells-per-group", type=int, default=FROZEN_MIN_CELLS_PER_GROUP)
    parser.add_argument("--max-features", type=int, default=FROZEN_MAX_FEATURES)
    parser.add_argument("--top-k", type=int, default=FROZEN_TOP_K)
    parser.add_argument("--n-repeats", type=int, default=FROZEN_N_REPEATS)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence")
    args = parser.parse_args(argv)

    ready_panel = pd.read_csv(ROOT / "evidence/expansion_v3_combined_ready_panel.tsv", sep="\t")
    specs = frozen_v3_combined_ready_specs()
    known = {spec.dataset_id for spec in specs}
    requested = set(args.dataset_id or known)
    if unknown := sorted(requested - known):
        parser.error(f"unknown or not-ready dataset ids: {unknown}")
    selected_specs = tuple(spec for spec in specs if spec.dataset_id in requested)

    contract_path = args.output_dir / f"{args.analysis_prefix}_scored_contract.tsv"
    detail_path = args.output_dir / f"{args.analysis_prefix}_dual_gate_detail.tsv"
    plan_path = args.output_dir / f"{args.analysis_prefix}_execution_plan.tsv"

    if args.dry_run:
        plan = _write_execution_plan(selected_specs, plan_path, ready_panel)
        print(
            f"Dry-run ready platforms: {len(plan)}; "
            f"available sources: {int(plan['source_available'].sum())}; "
            f"total source GiB: {plan['source_size_bytes'].sum() / 1024**3:.2f}",
            flush=True,
        )
        # A dry-run only compiles the frozen execution plan. Missing external
        # volumes are reported in the plan and must block an actual run, but
        # they are not a dry-run failure.
        return 0

    if args.compile_only:
        if args.dataset_id or args.merge_existing:
            parser.error("--compile-only cannot be combined with subset-run options")
        contract = pd.read_csv(contract_path, sep="\t")
        detail = pd.read_csv(detail_path, sep="\t")
    else:
        frozen_parameter_tuple = (
            FROZEN_MAX_UNITS,
            FROZEN_MAX_CELLS_PER_GROUP,
            FROZEN_MIN_CELLS_PER_GROUP,
            FROZEN_MAX_FEATURES,
            FROZEN_TOP_K,
            FROZEN_N_REPEATS,
        )
        observed_parameter_tuple = (
            args.max_units,
            args.max_cells_per_group,
            args.min_cells_per_group,
            args.max_features,
            args.top_k,
            args.n_repeats,
        )
        if (
            observed_parameter_tuple != frozen_parameter_tuple
            and args.analysis_prefix == DEFAULT_ANALYSIS_PREFIX
        ):
            parser.error(
                "non-frozen scoring parameters require --analysis-prefix to avoid "
                "overwriting the primary endpoint outputs"
            )
        if args.merge_existing and not args.dataset_id:
            parser.error("--merge-existing requires at least one --dataset-id")
        _write_execution_plan(selected_specs, plan_path, ready_panel)
        missing = [str(spec.path) for spec in selected_specs if not Path(spec.path).is_file()]
        if missing:
            raise FileNotFoundError(f"ready-panel source h5ad files are missing: {missing}")
        contracts = []
        details = []
        for spec in selected_specs:
            print(f"Running {spec.dataset_id}: {spec.path}", flush=True)
            contract, detail = benchmark_platform_dual_gate(
                spec,
                max_units=args.max_units,
                max_cells_per_group=args.max_cells_per_group,
                min_cells_per_group=args.min_cells_per_group,
                max_features=args.max_features,
                top_k=args.top_k,
                n_repeats=args.n_repeats,
                split_seed="pgaa-expansion-v3-ready-panel-v1",
                sampling_seed="pgaa-expansion-v3-ready-panel-matched-controls-v1",
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
    endpoint = evaluate_expansion_v3_endpoint(states, ready_panel)
    outputs = {
        contract_path: contract,
        detail_path: detail,
        args.output_dir / f"{args.analysis_prefix}_dual_gate_target_summary.tsv": target,
        args.output_dir / f"{args.analysis_prefix}_dual_gate_method_summary.tsv": method,
        args.output_dir / f"{args.analysis_prefix}_dual_gate_states.tsv": states,
        args.output_dir / f"{args.analysis_prefix}_primary_endpoint_claim_state.tsv": endpoint,
    }
    for path, frame in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep="\t", index=False)
    print(endpoint.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
