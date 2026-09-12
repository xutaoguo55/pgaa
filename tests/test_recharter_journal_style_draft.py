from pgaa.core.recharter_journal_style_draft import (
    build_and_render_recharter_journal_style_draft,
)
from pgaa.core.recharter_manuscript_audit import audit_recharter_manuscript_draft
from tests.test_recharter_manuscript_draft import (
    _claim_states,
    _figure_sources,
    _matrix,
    _readiness,
    _route_scores,
    _stability,
    _units,
)
from tests.test_recharter_manuscript_skeleton import _novelty_upgrades


def _formal_audit():
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "invariant_id": "I01",
                "status": "pass",
                "n_checked": 3,
                "n_violations": 0,
            },
            {
                "invariant_id": "I02",
                "status": "pass",
                "n_checked": 2,
                "n_violations": 0,
            },
        ]
    )


def _promotion_summary():
    import pandas as pd

    rows = []
    for method, false_rate, sensitivity in (
        ("claim_state_compiler", 0.0, 1.0),
        ("state_blind_frozen_baseline", 0.70, 0.5),
        ("decision_only_baseline", 0.0, 0.0),
        ("external_only_baseline", 0.19, 1.0),
    ):
        rows.append(
            {
                "method": method,
                "scope": "all_scenarios",
                "n_scenarios": 960,
                "false_promotion_rate": false_rate,
                "under_promotion_rate": 0.0,
                "exact_permission_rate": 1.0 - false_rate,
                "replication_false_positive_rate": false_rate,
                "replication_sensitivity": sensitivity,
            }
        )
    return pd.DataFrame(rows)


def _response_summaries():
    import pandas as pd

    replication = pd.DataFrame(
        [
            {"method": "pgaa_w", "median_top_k_overlap_fraction": 0.82},
            {"method": "pgaa_h", "median_top_k_overlap_fraction": 0.03},
            {"method": "absolute_mean_shift", "median_top_k_overlap_fraction": 0.725},
            {"method": "welch_abs_t", "median_top_k_overlap_fraction": 0.115},
        ]
    )
    specificity = pd.DataFrame(
        [
            {"method": "pgaa_w", "median_pseudo_top_k_overlap_fraction": 0.81, "median_specificity_margin": 0.015, "holm_adjusted_p": 0.14},
            {"method": "pgaa_h", "median_pseudo_top_k_overlap_fraction": 0.015, "median_specificity_margin": 0.015, "holm_adjusted_p": 0.0093},
            {"method": "absolute_mean_shift", "median_pseudo_top_k_overlap_fraction": 0.575, "median_specificity_margin": 0.08, "holm_adjusted_p": 0.018},
            {"method": "welch_abs_t", "median_pseudo_top_k_overlap_fraction": 0.01, "median_specificity_margin": 0.065, "holm_adjusted_p": 0.002},
        ]
    )
    return replication, specificity


def _cross_platform_evidence():
    import pandas as pd

    gates = pd.DataFrame(
        [
            {
                "dataset_id": dataset,
                "method": method,
                "dual_gate_state": state,
                "stability_gate_pass": state in {"stable_and_specific", "stable_but_not_specific"},
                "specificity_gate_pass": state in {"stable_and_specific", "specific_but_not_stable"},
            }
            for dataset in ("d1", "d2")
            for method, state in (
                ("pgaa_w", "stable_but_not_specific"),
                ("absolute_mean_shift", "stable_and_specific"),
            )
        ]
    )
    sensitivity = pd.DataFrame(
        [
            {
                "method": method,
                "stability_threshold": threshold,
                "cross_platform_interpretation": interpretation,
            }
            for method, interpretation in (
                ("pgaa_w", "recurrent_stability_specificity_decoupling"),
                ("absolute_mean_shift", "no_recurrent_decoupling_demonstrated"),
            )
            for threshold in (0.10, 0.20, 0.30)
        ]
    )
    return gates, sensitivity


def _journal_text(readiness=None) -> str:
    return build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        readiness if readiness is not None else _readiness(),
        _claim_states(),
        _units(),
        _stability(),
    )


def test_journal_style_draft_reframes_title_and_method_object():
    text = _journal_text()

    assert "Claim-state compilation controls evidentiary inflation" in text
    assert "The contribution is not a new biological claim" in text
    assert "claim-controlled benchmark compiler" in text
    assert "typed manuscript decisions" in text
    assert "Evidence source: `evidence/result_claim_states.tsv`." in text


def test_journal_style_draft_records_novelty_spine_provenance():
    text = build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        novelty_upgrades=_novelty_upgrades(),
    )

    assert "evidence/novelty_upgrade_map.tsv" in text
    assert "2 upgrade points; 2 tier-1 thesis points" in text


def test_journal_style_draft_integrates_executable_formal_audit():
    text = build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        formal_invariant_audit=_formal_audit(),
    )

    assert "Executable invariants make evidence-to-claim translation falsifiable" in text
    assert "2 compiler invariants; 2 passed with 0 observed violations" in text
    assert "evidence/claim_state_invariant_audit.tsv" in text
    assert "if and only if it is internally supported" in text


def test_journal_style_draft_integrates_claim_promotion_stress_test():
    text = build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        promotion_benchmark_summary=_promotion_summary(),
    )

    assert "Across 960 exhaustive finite-state scenarios" in text
    assert "state-blind frozen-output baseline produced 70.0% false promotions" in text
    assert "not independent biological ground truth" in text
    assert "evidence/claim_promotion_benchmark_summary.tsv" in text


def test_journal_style_draft_integrates_response_specificity_gate():
    replication, specificity = _response_summaries()
    text = build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        response_replication_summary=replication,
        response_specificity_summary=specificity,
    )

    assert "pseudo-perturbation gate separates reproducibility" in text
    assert "pseudo overlap was 0.810" in text
    assert "rejects a PGAA-W response-specific superiority interpretation" in text
    assert "absolute mean shift was the only method to pass both gates" in text
    assert "evidence/response_stability_specificity_dual_gate.tsv" in text


def test_journal_style_draft_integrates_cross_platform_dual_gate():
    gates, sensitivity = _cross_platform_evidence()
    text = build_and_render_recharter_journal_style_draft(
        _route_scores(),
        _matrix(),
        _figure_sources(),
        _readiness(),
        _claim_states(),
        _units(),
        _stability(),
        cross_platform_gates=gates,
        cross_platform_sensitivity=sensitivity,
    )

    assert "dual gate exposes recurrent cross-platform decoupling" in text
    assert "Across 2 independent perturbation datasets" in text
    assert "pgaa_w=stable_but_not_specific" in text
    assert "not proof of a universal law" in text
    assert "evidence/cross_platform_dual_gate_threshold_sensitivity.tsv" in text
    assert "platform-sensitive rather than platform-robust" in text
    assert "evidence/cross_platform_dual_gate_leave_one_out.tsv" in text


def test_journal_style_draft_passes_claim_audit_with_readiness_blockers():
    readiness = _readiness()
    text = _journal_text(readiness)

    result = audit_recharter_manuscript_draft(text, readiness)

    assert result.verdict == "CLAIM_SAFE_WITH_BLOCKERS"
    assert set(result.audit["status"]) == {"pass"}


def test_journal_style_draft_preserves_blocked_evidence_table():
    text = _journal_text()

    assert "## Still-Blocked Evidence" in text
    assert "evidence/event_sequence_contexts.tsv" in text
    assert "## Forbidden Phrases For This Draft" in text
