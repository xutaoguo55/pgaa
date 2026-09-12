#!/usr/bin/env python3
"""Train and freeze the context moderator model using expansion v2 only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import sklearn

from pgaa.core.context_moderator_model import (
    ModeratorModelSpec,
    build_training_table,
    fit_final_models,
    leave_one_platform_out,
    serialize_models,
    summarize_lopo,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gates_path = EVIDENCE / "expansion_v2_dual_gate_states.tsv"
    contracts_path = EVIDENCE / "expansion_v2_platform_contract_status.tsv"
    moderators_path = EVIDENCE / "expansion_v2_context_moderators.tsv"
    table = build_training_table(
        pd.read_csv(gates_path, sep="\t"),
        pd.read_csv(contracts_path, sep="\t"),
        pd.read_csv(moderators_path, sep="\t"),
    )
    spec = ModeratorModelSpec()
    predictions = leave_one_platform_out(table, spec)
    metrics = summarize_lopo(predictions)
    models, coefficients = fit_final_models(table, spec)
    payload = serialize_models(models, spec)
    payload.update(
        {
            "status": "frozen_before_v3_expression_outcomes",
            "training_cohort": "expansion_v2_only",
            "n_training_platforms": len(table),
            "sklearn_version": sklearn.__version__,
            "training_inputs_sha256": {
                gates_path.name: _sha256(gates_path),
                contracts_path.name: _sha256(contracts_path),
                moderators_path.name: _sha256(moderators_path),
            },
            "lopo_primary_metrics": metrics.iloc[0].to_dict(),
        }
    )

    table.to_csv(EVIDENCE / "context_moderator_v2_training_table.tsv", sep="\t", index=False)
    predictions.to_csv(EVIDENCE / "context_moderator_v2_lopo_predictions.tsv", sep="\t", index=False)
    metrics.to_csv(EVIDENCE / "context_moderator_v2_metrics.tsv", sep="\t", index=False)
    coefficients.to_csv(EVIDENCE / "context_moderator_v2_coefficients.tsv", sep="\t", index=False)
    model_path = EVIDENCE / "context_moderator_model_frozen.json"
    model_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    digest = _sha256(model_path)
    (EVIDENCE / "context_moderator_model_frozen.sha256").write_text(
        f"{digest}  {model_path.name}\n", encoding="ascii"
    )
    print(metrics.to_string(index=False))
    print(f"MODEL FROZEN: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
