from pathlib import Path

from pgaa.core.expansion_v2 import (
    DEFAULT_USB_ROOT,
    frozen_ready_specs,
    load_frozen_candidate_queue,
)


def test_expansion_v2_registry_is_source_and_lab_unique():
    specs = frozen_ready_specs()
    assert len(specs) == 10
    assert len({spec.dataset_id for spec in specs}) == len(specs)
    # The exact mount point is an environment fact (PGAA_DATA_ROOT), so assert
    # the structural property: every source lives under the configured data
    # root and outside the repository.
    root = Path(__file__).resolve().parents[1]
    assert all(DEFAULT_USB_ROOT in Path(spec.path).parents for spec in specs)
    assert not any(str(spec.path).startswith(str(root)) for spec in specs)
    assert all(spec.normalization in {"log1p_1e4", "precomputed_log"} for spec in specs)


def test_contextual_specs_declare_units_and_controls():
    contextual = [spec for spec in frozen_ready_specs() if spec.adapter == "generic_condition"]
    assert len(contextual) == 3
    assert all(spec.analysis_unit_columns for spec in contextual)
    assert all(spec.control_values for spec in contextual)


def test_frozen_candidate_queue_includes_amendments_without_duplicates():
    queue = load_frozen_candidate_queue()
    assert "dixit2016_k562_tf_crispr" in set(queue["candidate_id"])
    assert not queue["candidate_id"].duplicated().any()
