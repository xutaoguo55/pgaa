from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

from pgaa.core.local_h5ad_candidate_audit import (
    audit_local_h5ad_candidates,
    render_local_h5ad_candidate_report,
)


def _write(path: Path, labels: list[str], seed: int = 1) -> None:
    rng = np.random.default_rng(seed)
    obs = pd.DataFrame(
        {"gene": labels, "perturbation": labels},
        index=[f"cell_{i}" for i in range(len(labels))],
    )
    var = pd.DataFrame(index=[f"g{i}" for i in range(6)])
    ad.AnnData(rng.poisson(1, (len(labels), 6)).astype("float32"), obs=obs, var=var).write_h5ad(path)


def test_audit_detects_logical_duplicate_and_target_coverage(tmp_path):
    first = tmp_path / "first.h5ad"
    duplicate = tmp_path / "duplicate.h5ad"
    other = tmp_path / "other.h5ad"
    _write(first, ["BHLHE40", "control", "BHLHE40"])
    _write(duplicate, ["BHLHE40", "control", "BHLHE40"])
    _write(other, ["OTHER", "control", "OTHER"], seed=2)

    audit = audit_local_h5ad_candidates(
        [("first", first), ("duplicate", duplicate), ("other", other)], {"BHLHE40"}
    ).set_index("candidate_id")

    assert audit.loc["first", "logical_duplicate_group"] == audit.loc["duplicate", "logical_duplicate_group"]
    assert audit.loc["first", "independence_status"] == "duplicate_representation_not_independent"
    assert not audit.loc["first", "replication_claim_eligible"]
    assert audit.loc["other", "candidate_role"] == "cross_target_generality_candidate"


def test_distinct_target_matrix_is_replication_candidate(tmp_path):
    path = tmp_path / "target.h5ad"
    _write(path, ["BHLHE40", "control", "BHLHE40"])
    audit = audit_local_h5ad_candidates([("target", path)], {"BHLHE40"})
    report = render_local_h5ad_candidate_report(audit, {"BHLHE40"})

    assert audit.loc[0, "replication_claim_eligible"]
    assert "Replication-eligible distinct matrices: 1" in report
    assert "No source file was copied, modified, or deleted" in report
