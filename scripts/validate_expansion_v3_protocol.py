#!/usr/bin/env python3
"""Validate the prospective v3 protocol, queue, and frozen model digests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def _validate_digest(path: Path, digest_path: Path) -> str:
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = digest_path.read_text(encoding="ascii").split()[0]
    if observed != expected:
        raise SystemExit(f"digest mismatch for {path.name}: expected {expected}, observed {observed}")
    return observed


def main() -> int:
    protocol_path = EVIDENCE / "expansion_v3_protocol.json"
    queue_path = EVIDENCE / "expansion_v3_candidate_queue.tsv"
    model_path = EVIDENCE / "context_moderator_model_frozen.json"
    protocol_sha = _validate_digest(protocol_path, EVIDENCE / "expansion_v3_protocol.sha256")
    queue_sha = _validate_digest(queue_path, EVIDENCE / "expansion_v3_candidate_queue.sha256")
    model_sha = _validate_digest(model_path, EVIDENCE / "context_moderator_model_frozen.sha256")

    protocol = json.loads(protocol_path.read_text(encoding="ascii"))
    assert protocol["status"] == "frozen_before_v3_expression_outcomes"
    assert protocol["primary_endpoint"]["event"] == "pgaa_w_stable_and_specific"
    assert protocol["cohort"]["target_test_platforms"] == 10
    assert protocol["temporal_lock"]["prediction_file_and_sha256_before_expression_scoring"]
    assert protocol["context_model"]["feature_order"] == [
        "genetic_perturbation",
        "primary_or_in_vivo",
        "mouse_system",
        "split_independence_tier",
        "log2_recorded_split_levels",
        "minimum_equal_group_fraction",
    ]

    queue = pd.read_csv(queue_path, sep="\t")
    primary = queue[queue["queue_role"].eq("primary_priority")]
    assert len(primary) == 10
    assert primary["source_study"].nunique() == 10
    assert primary["laboratory_group"].nunique() == 10
    assert primary["cell_context_class"].nunique() == 10
    assert queue["expression_outcome_status"].eq("not_scored_by_pgaa").all()
    v2_scored = set(pd.read_csv(EVIDENCE / "expansion_v2_platform_contract_status.tsv", sep="\t")["candidate_id"])
    assert not set(queue["candidate_id"]) & v2_scored

    model = json.loads(model_path.read_text(encoding="ascii"))
    assert model["status"] == "frozen_before_v3_expression_outcomes"
    assert model["training_cohort"] == "expansion_v2_only"
    assert model["n_training_platforms"] == 10
    print(f"EXPANSION V3 PROTOCOL VALID: {protocol_sha}")
    print(f"EXPANSION V3 QUEUE VALID: {queue_sha}")
    print(f"CONTEXT MODERATOR MODEL VALID: {model_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
