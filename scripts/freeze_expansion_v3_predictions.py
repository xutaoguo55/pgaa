#!/usr/bin/env python3
"""Lock v3 state predictions before any v3 expression outcome is scored."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from pgaa.core.context_moderator_model import predict_from_serialized


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("context_table", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "evidence/expansion_v3_locked_predictions.tsv",
    )
    args = parser.parse_args()
    outcome_path = ROOT / "evidence/expansion_v3_dual_gate_states.tsv"
    if outcome_path.exists():
        raise SystemExit("refusing to create or replace predictions after v3 outcomes exist")
    model_path = ROOT / "evidence/context_moderator_model_frozen.json"
    model = json.loads(model_path.read_text(encoding="ascii"))
    context = pd.read_csv(args.context_table, sep="\t")
    predictions = predict_from_serialized(context, model)
    if len(predictions) != 10 or predictions["candidate_id"].nunique() != 10:
        raise SystemExit("prediction lock requires exactly 10 unique eligible v3 platforms")
    predictions.insert(1, "model_sha256", hashlib.sha256(model_path.read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output, sep="\t", index=False)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(".sha256").write_text(
        f"{digest}  {args.output.name}\n", encoding="ascii"
    )
    print(f"V3 PREDICTIONS LOCKED: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
