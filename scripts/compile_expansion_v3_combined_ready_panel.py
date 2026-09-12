#!/usr/bin/env python3
"""Compile the combined expansion-v3/v3b/v3c ready-panel status."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATUS_FILES = {
    "v3": ROOT / "evidence/expansion_v3_platform_contract_status.tsv",
    "v3b": ROOT / "evidence/expansion_v3b_platform_contract_status.tsv",
    "v3c": ROOT / "evidence/expansion_v3c_platform_contract_status.tsv",
}
OUT_READY = ROOT / "evidence/expansion_v3_combined_ready_panel.tsv"
OUT_ALL = ROOT / "evidence/expansion_v3_combined_platform_contract_status.tsv"
OUT_DOC = ROOT / "docs/EXPANSION_V3_COMBINED_READY_PANEL.md"


def main() -> int:
    frames = []
    for queue, path in STATUS_FILES.items():
        frame = pd.read_csv(path, sep="\t").assign(expansion_queue=queue)
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    ready = combined[combined["contract_status"].eq("ready_for_scoring")].copy()
    ready["context_mechanism_source"] = (
        ready["laboratory_group"].astype(str)
        + "|"
        + ready["cell_context_class"].astype(str)
        + "|"
        + ready["perturbation_mechanism"].astype(str)
    )
    sort_cols = ["expansion_queue", "priority", "candidate_id"]
    combined.sort_values(sort_cols).to_csv(OUT_ALL, sep="\t", index=False)
    ready.sort_values(sort_cols).to_csv(OUT_READY, sep="\t", index=False)

    lines = [
        "# Expansion v3 Combined Ready Panel",
        "",
        "This panel combines only metadata-contract status from v3, v3b, and v3c. No expression-derived method outcome was used to promote any platform.",
        "",
        f"- Registered candidate platforms: {len(combined)}",
        f"- Platforms ready for scoring: {len(ready)}",
        f"- Ready selected units: {int(ready['n_selected_units'].sum())}",
        f"- Independent laboratory groups among ready platforms: {ready['laboratory_group'].nunique()}",
        f"- Cell-context classes among ready platforms: {ready['cell_context_class'].nunique()}",
        f"- Perturbation mechanism classes among ready platforms: {ready['perturbation_mechanism'].nunique()}",
        f"- Unique laboratory/cell-context/mechanism tuples among ready platforms: {ready['context_mechanism_source'].nunique()}",
        "",
        "Ready platforms:",
        *[
            f"- {row.expansion_queue}: {row.candidate_id} ({row.laboratory_group}; {row.cell_context_class}; {row.perturbation_mechanism}; {int(row.n_selected_units)} units)"
            for row in ready.sort_values(sort_cols).itertuples()
        ],
        "",
        "Claim boundary:",
        "- Supported: the frozen metadata contract now yields more than ten ready external perturbation contexts across independent laboratories and cell contexts.",
        "- Not supported: ten distinct perturbation-mechanism classes. The current ready panel spans five mechanism classes.",
    ]
    OUT_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "Combined ready platforms: "
        f"{len(ready)}; selected units: {int(ready['n_selected_units'].sum())}; "
        f"labs: {ready['laboratory_group'].nunique()}; "
        f"contexts: {ready['cell_context_class'].nunique()}; "
        f"mechanisms: {ready['perturbation_mechanism'].nunique()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
