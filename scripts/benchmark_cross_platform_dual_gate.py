#!/usr/bin/env python3
"""Run the common stability-specificity dual gate on independent platforms."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.cross_platform_dual_gate import (  # noqa: E402
    PlatformSpec,
    benchmark_platform_dual_gate,
    evaluate_platform_leave_one_out,
    evaluate_stability_threshold_sensitivity,
    render_platform_robustness_report,
    render_cross_platform_report,
    render_threshold_sensitivity_report,
    summarize_platform_dual_gate,
    summarize_platform_state_uncertainty,
    synthesize_cross_platform_gates,
)
from pgaa.core.data_root import data_root  # noqa: E402


DEFAULT_SPECS = (
    PlatformSpec(
        "norman2019_k562_crispra",
        "K562 CRISPRa Perturb-seq",
        data_root("public_db_backup_2026-05-06/.openclaw/agents/stat_expert/projects/scRipple/data/norman_k562_sc.h5ad"),
        "norman2019",
        "gemgroup",
        None,
        "log1p_1e4",
        "technical_batch_holdout_4_vs_4",
    ),
    PlatformSpec(
        "datlinger2017_jurkat_crispr",
        "Jurkat CRISPR with TCR stimulation",
        data_root("pgaa_cross_platform/v1/sources/DatlingerBock2017/DatlingerBock2017.h5ad"),
        "datlinger2017",
        "replicate",
        None,
        "log1p_1e4",
        "experimental_replicate_holdout_3_vs_3",
    ),
    PlatformSpec(
        "sciplex3_a549_drug",
        "A549 multiplexed drug perturbation",
        data_root("pgaa_cross_platform/v1/sources/SciPlex3_A549/sciplex3_A549.h5ad"),
        "sciplex3",
        "replicate",
        "logNor",
        "precomputed_log",
        "biological_replicate_holdout_1_vs_1",
    ),
    PlatformSpec(
        "nadig2024_hepg2_crispri",
        "HepG2 CRISPRi Perturb-seq",
        data_root("pgaa_cross_platform/v1/sources/NadigOConner2024/NadigOConner2024_hepg2.h5ad"),
        "nadig2024",
        "batch",
        None,
        "log1p_1e4",
        "experimental_batch_holdout_28_vs_28",
    ),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-units", type=int, default=16)
    parser.add_argument("--max-cells-per-group", type=int, default=70)
    parser.add_argument("--max-features", type=int, default=5000)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--n-repeats", type=int, default=5)
    parser.add_argument(
        "--dataset-id",
        action="append",
        choices=[spec.dataset_id for spec in DEFAULT_SPECS],
        help="Run only the named dataset; may be repeated.",
    )
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="When running a subset, replace its rows in existing contract/detail tables.",
    )
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Recompile summaries from existing detail output without rerunning h5ad scoring.",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence")
    parser.add_argument("--report-out", type=Path, default=ROOT / "docs/CROSS_PLATFORM_DUAL_GATE.md")
    args = parser.parse_args(argv)

    contract_path = args.output_dir / "cross_platform_dual_gate_contract.tsv"
    detail_path = args.output_dir / "cross_platform_dual_gate_detail.tsv"
    if args.compile_only:
        if args.dataset_id or args.merge_existing:
            parser.error("--compile-only cannot be combined with subset-run options")
        contract = pd.read_csv(contract_path, sep="\t")
        detail = pd.read_csv(detail_path, sep="\t")
    else:
        selected_specs = tuple(
            spec for spec in DEFAULT_SPECS
            if not args.dataset_id or spec.dataset_id in set(args.dataset_id)
        )
        if args.merge_existing and not args.dataset_id:
            parser.error("--merge-existing requires at least one --dataset-id")
        missing = [str(spec.path) for spec in selected_specs if not spec.path.is_file()]
        if missing:
            raise FileNotFoundError(f"cross-platform source h5ad files are missing: {missing}")
        contracts: list[pd.DataFrame] = []
        details: list[pd.DataFrame] = []
        for spec in selected_specs:
            print(f"Running {spec.dataset_id}: {spec.path}", flush=True)
            current_contract, current_detail = benchmark_platform_dual_gate(
                spec,
                max_units=args.max_units,
                max_cells_per_group=args.max_cells_per_group,
                max_features=args.max_features,
                top_k=args.top_k,
                n_repeats=args.n_repeats,
            )
            contracts.append(current_contract)
            details.append(current_detail)
            print(f"Completed {spec.dataset_id}: {len(current_contract)} units", flush=True)
        contract = pd.concat(contracts, ignore_index=True)
        detail = pd.concat(details, ignore_index=True)
        if args.merge_existing:
            replaced = set(args.dataset_id)
            old_contract = pd.read_csv(contract_path, sep="\t")
            old_detail = pd.read_csv(detail_path, sep="\t")
            contract = pd.concat(
                [old_contract[~old_contract["dataset_id"].isin(replaced)], contract],
                ignore_index=True,
            )
            detail = pd.concat(
                [old_detail[~old_detail["dataset_id"].isin(replaced)], detail],
                ignore_index=True,
            )
    target, method, gates = summarize_platform_dual_gate(detail)
    replogle_path = ROOT / "evidence/response_stability_specificity_dual_gate.tsv"
    if replogle_path.exists():
        replogle = pd.read_csv(replogle_path, sep="\t")
        replogle_gates = pd.DataFrame(
            {
                "dataset_id": "replogle2022_k562_crispri",
                "platform": "K562 CRISPRi genome-scale Perturb-seq",
                "split_strength": "technical_batch_holdout_24_vs_24",
                "method": replogle["method"],
                "n_units": 16,
                "median_observed_overlap": replogle["observed_overlap"],
                "median_pseudo_overlap": replogle["pseudo_overlap"],
                "median_specificity_margin": replogle["specificity_margin"],
                "n_units_positive_margin": float("nan"),
                "wilcoxon_one_sided_p": float("nan"),
                "holm_adjusted_p": replogle["holm_adjusted_p"],
                "stability_threshold": replogle["minimum_stable_overlap"],
                "specificity_alpha": replogle["specificity_alpha"],
                "stability_gate_pass": replogle["stability_gate_pass"],
                "specificity_gate_pass": replogle["specificity_gate_pass"],
                "dual_gate_state": replogle["dual_gate_state"],
            }
        )
        gates = pd.concat([gates, replogle_gates], ignore_index=True)
    synthesis = synthesize_cross_platform_gates(gates)
    sensitivity = evaluate_stability_threshold_sensitivity(gates)
    leave_one_out = evaluate_platform_leave_one_out(gates)
    uncertainty = summarize_platform_state_uncertainty(gates)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "cross_platform_dual_gate_contract.tsv": contract,
        "cross_platform_dual_gate_detail.tsv": detail,
        "cross_platform_dual_gate_target_summary.tsv": target,
        "cross_platform_dual_gate_method_summary.tsv": method,
        "cross_platform_dual_gate_states.tsv": gates,
        "cross_platform_dual_gate_synthesis.tsv": synthesis,
        "cross_platform_dual_gate_threshold_sensitivity.tsv": sensitivity,
        "cross_platform_dual_gate_leave_one_out.tsv": leave_one_out,
        "cross_platform_dual_gate_platform_uncertainty.tsv": uncertainty,
    }
    for name, frame in outputs.items():
        frame.to_csv(args.output_dir / name, sep="\t", index=False)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        render_cross_platform_report(contract, gates, synthesis), encoding="utf-8"
    )
    sensitivity_report = args.report_out.with_name(
        "CROSS_PLATFORM_DUAL_GATE_THRESHOLD_SENSITIVITY.md"
    )
    sensitivity_report.write_text(
        render_threshold_sensitivity_report(sensitivity), encoding="utf-8"
    )
    robustness_report = args.report_out.with_name(
        "CROSS_PLATFORM_DUAL_GATE_ROBUSTNESS.md"
    )
    robustness_report.write_text(
        render_platform_robustness_report(leave_one_out, uncertainty), encoding="utf-8"
    )
    print(f"Wrote {args.report_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
