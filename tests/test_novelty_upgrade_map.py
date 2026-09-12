import pandas as pd
import pytest

from pgaa.core.novelty_upgrade_map import (
    build_novelty_upgrade_map,
    render_novelty_upgrade_report,
    summarize_novelty_upgrade_map,
)


def test_novelty_upgrade_map_contains_more_than_100_large_upgrades():
    upgrades = build_novelty_upgrade_map()

    assert len(upgrades) >= 100
    assert upgrades["pillar_id"].nunique() >= 10
    assert "Claim-state compiler" in set(upgrades["pillar_name"])
    assert "Typed replication state" in set(upgrades["pillar_name"])
    assert "Epistemic inflation control" in set(upgrades["pillar_name"])


def test_novelty_upgrade_summary_and_report_preserve_claim_boundary():
    upgrades = build_novelty_upgrade_map()
    summary = summarize_novelty_upgrade_map(upgrades)
    report = render_novelty_upgrade_report(upgrades, summary)

    assert summary["n_upgrade_points"].sum() == len(upgrades)
    assert "PGAA should be positioned as a claim-state compiler" in report
    assert "bounded computational same-context concordance only" in report
    assert "validated antigens" in report


def test_novelty_upgrade_summary_requires_schema():
    with pytest.raises(ValueError, match="novelty upgrade map is missing columns"):
        summarize_novelty_upgrade_map(pd.DataFrame({"x": [1]}))
