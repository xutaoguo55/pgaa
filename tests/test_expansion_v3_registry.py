from pathlib import Path

import pandas as pd

from pgaa.core.expansion_v3 import (
    frozen_v3_candidate_specs,
    frozen_v3_combined_ready_specs,
    frozen_v3b_rescue_specs,
    frozen_v3c_rescue_specs,
    load_frozen_v3_candidate_queue,
    load_frozen_v3b_candidate_queue,
    load_frozen_v3c_candidate_queue,
)


def test_v3_candidate_specs_match_frozen_queue():
    root = Path(__file__).resolve().parents[1]
    queue = load_frozen_v3_candidate_queue(root)
    specs = frozen_v3_candidate_specs()
    assert [spec.dataset_id for spec in specs] == queue["candidate_id"].tolist()
    assert len(specs) == 14
    assert queue["expression_outcome_status"].eq("not_scored_by_pgaa").all()


def test_v3_source_manifest_uses_external_storage_only():
    root = Path(__file__).resolve().parents[1]
    manifest = pd.read_csv(root / "evidence/expansion_v3_source_manifest.tsv", sep="\t")
    assert manifest["status"].isin({"verified_existing", "downloaded_and_verified"}).all()
    # Frozen manifests record external storage, never repo-local paths. The
    # mount point itself is an environment fact and is not asserted.
    paths = manifest["resolved_source_path"]
    assert paths.map(lambda value: Path(value).is_absolute()).all()
    assert not paths.str.startswith(str(root)).any()


def test_v3b_rescue_specs_match_frozen_queue():
    root = Path(__file__).resolve().parents[1]
    queue = load_frozen_v3b_candidate_queue(root)
    specs = frozen_v3b_rescue_specs()
    assert [spec.dataset_id for spec in specs] == queue["candidate_id"].tolist()
    assert len(specs) == 12
    assert queue["expression_outcome_status"].eq("not_scored_by_pgaa").all()


def test_v3b_source_manifest_uses_external_storage_only():
    root = Path(__file__).resolve().parents[1]
    manifest = pd.read_csv(root / "evidence/expansion_v3b_source_manifest.tsv", sep="\t")
    assert manifest["status"].isin({"verified_existing", "downloaded_and_verified"}).all()
    paths = manifest["resolved_source_path"]
    assert paths.map(lambda value: Path(value).is_absolute()).all()
    assert not paths.str.startswith(str(root)).any()


def test_v3c_rescue_specs_match_frozen_queue():
    root = Path(__file__).resolve().parents[1]
    queue = load_frozen_v3c_candidate_queue(root)
    specs = frozen_v3c_rescue_specs()
    assert [spec.dataset_id for spec in specs] == queue["candidate_id"].tolist()
    assert len(specs) == 9
    assert queue["expression_outcome_status"].eq("not_scored_by_pgaa").all()


def test_v3c_source_manifest_uses_external_storage_only_when_present():
    root = Path(__file__).resolve().parents[1]
    manifest = pd.read_csv(root / "evidence/expansion_v3c_source_manifest.tsv", sep="\t")
    assert manifest["status"].isin({"verified_existing", "downloaded_and_verified"}).all()
    paths = manifest["resolved_source_path"]
    assert paths.map(lambda value: Path(value).is_absolute()).all()
    assert not paths.str.startswith(str(root)).any()


def test_combined_ready_specs_match_ready_panel():
    root = Path(__file__).resolve().parents[1]
    panel = pd.read_csv(root / "evidence/expansion_v3_combined_ready_panel.tsv", sep="\t")
    specs = frozen_v3_combined_ready_specs()
    assert [spec.dataset_id for spec in specs] == panel["candidate_id"].tolist()
    assert len(specs) == 14
    # The frozen panel is metadata-ready, while its h5ad sources live on an
    # external volume and are intentionally not bundled with the repository.
    assert [str(spec.path) for spec in specs] == panel["source_h5ad"].tolist()
