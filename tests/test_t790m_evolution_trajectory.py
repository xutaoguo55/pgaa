import pandas as pd

from pgaa.core.t790m_evolution_trajectory import (
    EGFR_ENSEMBL_ID,
    STAGES,
    audit_t790m_evolution_trajectory,
    evolution_trajectory_verdict,
    render_t790m_evolution_audit,
)


def test_evolution_trajectory_detects_state_dependent_direction():
    values = {
        "parental": [10.0, 11.0],
        "gefitinib_tolerant": [30.0, 31.0],
        "wz4002_tolerant": [28.0, 29.0],
        "early_t790m_gr2": [25.0, 26.0],
        "late_t790m_gr3": [20.0, 21.0],
    }
    row = {}
    for stage, columns in STAGES.items():
        row.update(dict(zip(columns, values[stage])))
    cpm = pd.DataFrame([row], index=[EGFR_ENSEMBL_ID])

    stages, contrasts = audit_t790m_evolution_trajectory(cpm)

    assert evolution_trajectory_verdict(contrasts) == "EVOLUTION_STAGE_MODULATES_EGFR_DIRECTION_NO_FIXED_T790M_EFFECT"
    assert set(contrasts["exact_directional_p"]) == {1 / 6}
    assert contrasts["all_pairwise_direction_consistent"].all()
    assert "does not rescue the discordance" in render_t790m_evolution_audit(stages, contrasts)
