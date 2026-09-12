from pathlib import Path

import pandas as pd

from scripts.download_expansion_v3_sources import resolve_existing


def test_v3_queue_is_ordered_and_expression_unseen():
    root = Path(__file__).resolve().parents[1]
    queue = pd.read_csv(root / "evidence/expansion_v3_candidate_queue.tsv", sep="\t")
    assert queue["priority"].tolist() == list(range(1, 15))
    assert queue["expression_outcome_status"].eq("not_scored_by_pgaa").all()
    assert queue.iloc[:10]["laboratory_group"].nunique() == 10


def test_resolver_does_not_use_local_project_storage(monkeypatch, tmp_path):
    import scripts.download_expansion_v3_sources as downloader

    v2 = tmp_path / "v2"
    v3 = tmp_path / "v3"
    monkeypatch.setattr(downloader, "V2_SOURCES", v2)
    monkeypatch.setattr(downloader, "V3_SOURCES", v3)
    candidate = pd.Series({"candidate_id": "d1", "source_file": "x.h5ad"})
    assert resolve_existing(candidate) is None
    path = v2 / "d1/x.h5ad"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"test")
    assert resolve_existing(candidate) == path
