#!/usr/bin/env python3
"""Validate the frozen PGAA dual-gate expansion protocol and digest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "evidence/expansion_v2_protocol.json"
DIGEST = ROOT / "evidence/expansion_v2_protocol.sha256"
QUEUE = ROOT / "evidence/expansion_v2_candidate_queue.tsv"
QUEUE_DIGEST = ROOT / "evidence/expansion_v2_candidate_queue.sha256"


def main() -> int:
    raw = PROTOCOL.read_bytes()
    protocol = json.loads(raw)
    assert protocol["status"] == "frozen_before_new_expression_outcomes"
    assert protocol["scope"]["new_confirmatory_platforms_required"] == 10
    assert protocol["analysis"]["primary_method"] == "pgaa_w"
    assert protocol["analysis"]["stability_threshold"] == 0.2
    assert protocol["analysis"]["specificity_alpha"] == 0.05
    assert protocol["analysis"]["top_k"] == 100
    assert protocol["analysis"]["matched_resampling_repeats"] == 5
    expected = DIGEST.read_text(encoding="ascii").split()[0]
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected:
        raise SystemExit(f"protocol digest mismatch: expected {expected}, observed {observed}")
    queue_raw = QUEUE.read_bytes()
    queue_expected = QUEUE_DIGEST.read_text(encoding="ascii").split()[0]
    queue_observed = hashlib.sha256(queue_raw).hexdigest()
    if queue_observed != queue_expected:
        raise SystemExit(
            f"candidate queue digest mismatch: expected {queue_expected}, observed {queue_observed}"
        )
    queue = pd.read_csv(QUEUE, sep="\t")
    primary = queue[queue["queue_role"].eq("primary")]
    assert len(primary) == 10
    assert primary["source_study"].nunique() == 10
    assert primary["laboratory_group"].nunique() == 10
    assert primary["cell_context_class"].nunique() == 10
    assert primary["perturbation_mechanism"].nunique() >= 3
    print(f"EXPANSION V2 PROTOCOL VALID: {observed}")
    print(f"EXPANSION V2 CANDIDATE QUEUE VALID: {queue_observed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
