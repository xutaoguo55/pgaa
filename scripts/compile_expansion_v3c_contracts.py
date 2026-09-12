#!/usr/bin/env python3
"""Compile result-blind unit contracts for expansion-v3c rescue platforms."""
from __future__ import annotations

from pathlib import Path
import sys

import anndata as ad
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.cross_platform_dual_gate import build_platform_unit_contract  # noqa: E402
from pgaa.core.expansion_v3 import (  # noqa: E402
    frozen_v3c_rescue_specs,
    load_frozen_v3c_candidate_queue,
)


MIN_SELECTED_UNITS = 8


def main() -> int:
    queue = load_frozen_v3c_candidate_queue(ROOT).set_index("candidate_id")
    platform_rows: list[dict[str, object]] = []
    unit_frames: list[pd.DataFrame] = []
    for spec in frozen_v3c_rescue_specs():
        base = {
            "priority": int(queue.loc[spec.dataset_id, "priority"]),
            "queue_role": queue.loc[spec.dataset_id, "queue_role"],
            "candidate_id": spec.dataset_id,
            "platform": spec.platform,
            "source_h5ad": str(spec.path),
            "laboratory_group": queue.loc[spec.dataset_id, "laboratory_group"],
            "cell_context_class": queue.loc[spec.dataset_id, "cell_context_class"],
            "perturbation_mechanism": queue.loc[spec.dataset_id, "perturbation_mechanism"],
            "adapter": spec.adapter,
            "split_column": spec.batch_column,
            "split_strength": spec.split_strength,
            "minimum_selected_units_gate": MIN_SELECTED_UNITS,
        }
        if not spec.path.is_file():
            platform_rows.append({**base, "contract_status": "source_pending", "n_selected_units": 0})
            continue
        adata = ad.read_h5ad(spec.path, backed="r")
        try:
            contract, split_map, _ = build_platform_unit_contract(
                adata.obs,
                spec,
                max_units=16,
                max_cells_per_group=70,
                min_cells_per_group=20,
                split_seed="pgaa-expansion-v3c-contract-v1",
            )
        except Exception as exc:
            platform_rows.append(
                {
                    **base,
                    "contract_status": "metadata_contract_error",
                    "n_selected_units": 0,
                    "n_recorded_split_levels": 0,
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )
        else:
            status = "ready_for_scoring" if len(contract) >= MIN_SELECTED_UNITS else "below_minimum_units"
            platform_rows.append(
                {
                    **base,
                    "contract_status": status,
                    "n_selected_units": len(contract),
                    "n_recorded_split_levels": len(split_map),
                    "minimum_equal_group_size": int(contract["n_per_group"].min()) if len(contract) else 0,
                    "maximum_equal_group_size": int(contract["n_per_group"].max()) if len(contract) else 0,
                    "detail": "result_blind_contract_compiled",
                }
            )
            if len(contract):
                unit_frames.append(contract)
        finally:
            adata.file.close()

    platform = pd.DataFrame(platform_rows).sort_values("priority")
    units = pd.concat(unit_frames, ignore_index=True) if unit_frames else pd.DataFrame()
    evidence = ROOT / "evidence"
    platform.to_csv(evidence / "expansion_v3c_platform_contract_status.tsv", sep="\t", index=False)
    units.to_csv(evidence / "expansion_v3c_selected_unit_contract.tsv", sep="\t", index=False)

    ready = platform[platform["contract_status"].eq("ready_for_scoring")]
    downloaded = platform[~platform["contract_status"].eq("source_pending")]
    lines = [
        "# Expansion v3c Rescue Platform Contracts",
        "",
        "This is a metadata-only compilation. No expression-derived method outcome was used.",
        "",
        f"- Rescue candidates registered: {len(platform)}",
        f"- Rescue candidates with verified local USB sources: {len(downloaded)}",
        f"- Rescue platforms ready for scoring: {len(ready)}",
        f"- Frozen selected units across rescue candidates: {len(units)}",
        f"- Minimum selected-unit gate per platform: {MIN_SELECTED_UNITS}",
        f"- Independent laboratory groups among ready rescue platforms: {ready['laboratory_group'].nunique()}",
        f"- Perturbation mechanism classes among ready rescue platforms: {ready['perturbation_mechanism'].nunique()}",
        f"- Cell-context classes among ready rescue platforms: {ready['cell_context_class'].nunique()}",
        "",
        "Ready rescue candidates:",
        *[f"- {row.candidate_id}: {int(row.n_selected_units)} selected units" for row in ready.itertuples()],
        "",
        "Candidates below the frozen selected-unit gate, metadata-contract errors, or still source-pending remain visible in the status TSV.",
    ]
    (ROOT / "docs/EXPANSION_V3C_CONTRACT_STATUS.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"Ready v3c rescue platforms: {len(ready)}; selected units: {len(units)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
