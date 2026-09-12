import pandas as pd

from pgaa.core.t790m_cross_system_replication import (
    EGFR_ENSEMBL_ID,
    audit_t790m_cross_system_replication,
    render_t790m_cross_system_audit,
)


def test_cross_system_audit_preserves_directional_discordance():
    cortad_expression = pd.DataFrame({"EGFR": [2.0, 1.8, 4.0, 4.2]}, index=["h1", "h2", "l1", "l2"])
    cortad_metadata = pd.DataFrame(
        {"cell_id": ["h1", "h2", "l1", "l2"], "group": ["perturbed", "perturbed", "control", "control"]}
    )
    replication = pd.DataFrame(
        {"A1": [10.0], "A2": [11.0], "A3": [12.0], "C1": [20.0], "C2": [21.0], "C3": [22.0]},
        index=[EGFR_ENSEMBL_ID],
    )

    summary = audit_t790m_cross_system_replication(cortad_expression, cortad_metadata, replication)

    assert not bool(summary.iloc[0]["direction_concordant"])
    assert summary.iloc[0]["verdict"] == "CROSS_SYSTEM_NOT_REPLICATED_DIRECTION_DISCORDANT_UNDERPOWERED"
    assert "failed or unresolved" in render_t790m_cross_system_audit(summary)
