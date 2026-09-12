import pandas as pd

from pgaa.core.event_source_audit import (
    audit_event_sources,
    classify_source_table,
    render_event_source_audit_markdown,
)


def test_classify_event_ready_table():
    table = pd.DataFrame(
        [
            {
                "source_event_id": "evt1",
                "source_event_type": "missense",
                "source_gene": "GENE1",
                "event_coordinate": "p.A10V",
                "altered_sequence_context": "SLYNTVATLAA",
                "event_index": 4,
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
            }
        ]
    )

    status, detail = classify_source_table(table, "real_events")

    assert status == "event_ready"
    assert "required event columns" in detail


def test_classify_gene_level_table_as_not_event_ready():
    table = pd.DataFrame(
        [{"target": "CEBPE", "gene": "ELANE", "s1_wasserstein": 0.2, "pgaa_rank": 1}]
    )

    status, detail = classify_source_table(table, "gene_scores")

    assert status == "gene_level_only"
    assert "missing event columns" in detail


def test_event_source_audit_renders_no_event_ready_interpretation(tmp_path):
    source = tmp_path / "gene_scores.csv"
    pd.DataFrame([{"gene": "ELANE", "target": "CEBPE"}]).to_csv(source, index=False)
    manifest = pd.DataFrame(
        [{"source_id": "gene_scores", "path": "gene_scores.csv", "source_family": "PGAA"}]
    )

    audit = audit_event_sources(manifest, tmp_path)
    report = render_event_source_audit_markdown(audit)

    assert audit.loc[0, "status"] == "gene_level_only"
    assert "No inspected source table currently supports real event-peptide compilation" in report
