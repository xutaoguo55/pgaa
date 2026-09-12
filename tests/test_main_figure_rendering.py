import pandas as pd
import pytest

from pgaa.core.main_figure_rendering import (
    build_figure1_payload,
    render_figure1,
    render_figure1_report,
)


def _figure_sources() -> pd.DataFrame:
    common = {
        "figure_id": "Figure 1",
        "evidence_type": "",
        "primary_method": "",
        "n_methods": "",
        "n_pgaa_methods": "",
        "n_comparative_support": "",
        "n_descriptive_only": "",
        "n_failure_or_guardrail": "",
        "allowed_manuscript_use": "",
    }
    return pd.DataFrame(
        [
            {
                **common,
                "panel_id": "A_claim_state_distribution",
                "source_kind": "claim_summary",
                "context": "",
                "state": "comparative_support",
                "stability_class": "",
                "cross_dataset_status": "",
                "x_group": "decision_benchmark",
                "y_value": 2,
                "secondary_value": "",
                "label": "comparative_support (low)",
            },
            {
                **common,
                "panel_id": "B_responder_state_units",
                "source_kind": "responder_state_unit",
                "context": "BHLHE40_pDS258",
                "primary_method": "PGAA-H",
                "state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "x_group": "adamson_decision_benchmark",
                "y_value": 0.83,
                "secondary_value": 0.05,
                "n_methods": 5,
                "n_comparative_support": 2,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 3,
                "label": "BHLHE40 / supported_responder_state",
            },
            {
                **common,
                "panel_id": "C_unit_stability",
                "source_kind": "stability_summary",
                "context": "BHLHE40_pDS258",
                "primary_method": "PGAA-H",
                "state": "supported_responder_state",
                "stability_class": "leave_one_method_stable",
                "cross_dataset_status": "no_cross_dataset_same_context",
                "x_group": "leave_one_method_stable",
                "y_value": 5,
                "secondary_value": 0,
                "n_methods": 5,
                "n_comparative_support": 2,
                "n_descriptive_only": 0,
                "n_failure_or_guardrail": 3,
                "label": "BHLHE40: 5/5 preserved",
            },
        ]
    )


def test_build_figure1_payload_splits_panels():
    payload = build_figure1_payload(_figure_sources())

    assert set(payload) == {"panel_a", "panel_b", "panel_c"}
    assert len(payload["panel_a"]) == 1
    assert payload["panel_b"]["y_value"].iloc[0] == pytest.approx(0.83)


def test_render_figure1_writes_png_pdf_and_report(tmp_path):
    figure_sources = _figure_sources()
    png_out = tmp_path / "figure1.png"
    pdf_out = tmp_path / "figure1.pdf"

    metadata = render_figure1(figure_sources, png_out, pdf_out)
    report = render_figure1_report(metadata, figure_sources)

    assert png_out.exists()
    assert pdf_out.exists()
    assert png_out.stat().st_size > 0
    assert pdf_out.stat().st_size > 0
    assert metadata["n_source_rows"] == 3
    assert "no_cross_dataset_same_context" in report


def test_build_figure1_payload_requires_schema():
    with pytest.raises(ValueError, match="main-figure source table is missing columns"):
        build_figure1_payload(pd.DataFrame({"x": [1]}))
