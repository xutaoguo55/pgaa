import pandas as pd

from pgaa.core.recharter_route_selection import (
    render_route_report,
    score_routes,
    validate_route_matrix,
)


def _route_matrix():
    return pd.DataFrame(
        [
            {
                "route_id": "blocked_high_upside",
                "route_name": "Blocked high-upside route",
                "central_object": "unsupported event unit",
                "evidence_fit": 1,
                "novelty_potential": 5,
                "implementation_burden": 5,
                "fatal_blocker_count": 2,
                "claim_risk": 5,
                "current_support": "Prototype only.",
                "next_decisive_action": "Add missing source data.",
            },
            {
                "route_id": "supported_method_route",
                "route_name": "Supported method route",
                "central_object": "auditable state unit",
                "evidence_fit": 4,
                "novelty_potential": 4,
                "implementation_burden": 3,
                "fatal_blocker_count": 0,
                "claim_risk": 2,
                "current_support": "Existing outputs support this route.",
                "next_decisive_action": "Build the state table.",
            },
        ]
    )


def test_validate_route_matrix_accepts_complete_rows():
    assert validate_route_matrix(_route_matrix()) == []


def test_score_routes_prefers_supported_route_over_blocked_upside():
    scored = score_routes(_route_matrix())

    assert scored.loc[0, "route_id"] == "supported_method_route"
    assert scored.loc[0, "recommended_now"]
    assert not scored.loc[1, "recommended_now"]


def test_route_report_contains_recommendation():
    scored = score_routes(_route_matrix())
    report = render_route_report(scored)

    assert "Recommended route now" in report
    assert "supported_method_route" in report


def test_route_report_exposes_real_evidence_transition():
    routes = _route_matrix()
    routes["readiness_state"] = "READY_REAL_EVIDENCE"

    report = render_route_report(score_routes(routes))

    assert "Real-evidence transition: `READY_REAL_EVIDENCE`" in report


def test_validate_route_matrix_rejects_out_of_range_scores():
    routes = _route_matrix()
    routes.loc[0, "evidence_fit"] = 9

    errors = validate_route_matrix(routes)

    assert any("evidence_fit must be between 0 and 5" in error for error in errors)
