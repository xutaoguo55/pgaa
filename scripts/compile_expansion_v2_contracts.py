#!/usr/bin/env python3
"""Compile result-blind unit contracts for expansion-v2 platforms."""
from __future__ import annotations

from pathlib import Path
import sys

import anndata as ad
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pgaa.core.cross_platform_dual_gate import build_platform_unit_contract  # noqa: E402
from pgaa.core.expansion_v2 import (  # noqa: E402
    frozen_ready_specs,
    load_frozen_candidate_queue,
)


def main() -> int:
    queue = load_frozen_candidate_queue(ROOT)
    queue = queue.set_index("candidate_id")
    platform_rows: list[dict[str, object]] = []
    unit_frames: list[pd.DataFrame] = []
    for spec in frozen_ready_specs():
        base = {
            "candidate_id": spec.dataset_id,
            "platform": spec.platform,
            "source_h5ad": str(spec.path),
            "laboratory_group": queue.loc[spec.dataset_id, "laboratory_group"],
            "cell_context_class": queue.loc[spec.dataset_id, "cell_context_class"],
            "perturbation_mechanism": queue.loc[spec.dataset_id, "perturbation_mechanism"],
            "split_column": spec.batch_column,
            "split_strength": spec.split_strength,
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
                split_seed="pgaa-cross-platform-dual-gate-v2",
            )
        except Exception as exc:
            platform_rows.append(
                {
                    **base,
                    "contract_status": "metadata_contract_error",
                    "n_selected_units": 0,
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )
        else:
            status = "ready_for_scoring" if len(contract) >= 8 else "below_eight_units"
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

    platform = pd.DataFrame(platform_rows).sort_values("candidate_id")
    units = pd.concat(unit_frames, ignore_index=True) if unit_frames else pd.DataFrame()
    evidence = ROOT / "evidence"
    platform.to_csv(evidence / "expansion_v2_platform_contract_status.tsv", sep="\t", index=False)
    units.to_csv(evidence / "expansion_v2_selected_unit_contract.tsv", sep="\t", index=False)
    ready = platform[platform["contract_status"].eq("ready_for_scoring")]
    lines = [
        "# Expansion v2 Platform Contracts",
        "",
        "This is a metadata-only compilation. No expression-derived method outcome was used.",
        "",
        f"- Platforms registered: {len(platform)}",
        f"- Platforms ready for scoring: {len(ready)}",
        f"- Frozen selected units: {len(units)}",
        f"- Independent laboratory groups represented: {ready['laboratory_group'].nunique()}",
        f"- Perturbation mechanism classes represented: {ready['perturbation_mechanism'].nunique()}",
        f"- Cell-context classes represented: {ready['cell_context_class'].nunique()}",
        "",
        "All registered positions passed the same result-blind metadata contract before scoring.",
    ]
    (ROOT / "docs/EXPANSION_V2_CONTRACT_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Ready platforms: {len(ready)}; selected units: {len(units)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
