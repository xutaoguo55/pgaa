import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_expansion_v2_protocol_is_frozen_and_self_consistent():
    protocol_path = ROOT / "evidence/expansion_v2_protocol.json"
    raw = protocol_path.read_bytes()
    protocol = json.loads(raw)
    expected = (ROOT / "evidence/expansion_v2_protocol.sha256").read_text().split()[0]

    assert hashlib.sha256(raw).hexdigest() == expected
    assert protocol["scope"]["new_confirmatory_platforms_required"] == 10
    assert protocol["scope"]["minimum_independent_laboratory_groups"] == 10
    assert protocol["analysis"]["primary_method"] == "pgaa_w"
    assert protocol["analysis"]["stability_threshold"] == 0.2
    assert protocol["analysis"]["specificity_alpha"] == 0.05
    assert protocol["failure_policy"]["unfavorable_outcome"] == "retain_platform_in_primary_analysis"
    assert protocol["claim_rules"]["universal_law_prohibited"] is True


def test_expansion_v2_primary_queue_has_ten_independent_contexts():
    queue_path = ROOT / "evidence/expansion_v2_candidate_queue.tsv"
    raw = queue_path.read_bytes()
    expected = (ROOT / "evidence/expansion_v2_candidate_queue.sha256").read_text().split()[0]
    queue = pd.read_csv(queue_path, sep="\t")
    primary = queue[queue["queue_role"].eq("primary")]

    assert hashlib.sha256(raw).hexdigest() == expected
    assert list(primary["priority"]) == list(range(1, 11))
    assert primary["source_study"].nunique() == 10
    assert primary["laboratory_group"].nunique() == 10
    assert primary["cell_context_class"].nunique() == 10
    assert primary["perturbation_mechanism"].nunique() >= 3
