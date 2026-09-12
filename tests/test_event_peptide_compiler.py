import pandas as pd
import pytest

from pgaa.core.event_peptide_compiler import (
    EventCompilerConfig,
    compile_event_peptides,
    event_containing_windows,
)


def test_event_containing_windows_cover_event_index():
    windows = event_containing_windows("ACDEFGHIKLMNPQRSTVWY", 9, (8, 9))

    assert windows
    for peptide, start, event_position in windows:
        assert peptide == "ACDEFGHIKLMNPQRSTVWY"[start : start + len(peptide)]
        assert 0 <= event_position < len(peptide)
        assert start + event_position == 9


def test_compile_event_peptides_emits_candidates_and_decoys():
    events = pd.DataFrame(
        [
            {
                "source_event_id": "EVT1",
                "source_event_type": "mutation",
                "source_gene": "GENE1",
                "event_coordinate": "p.K10M",
                "altered_sequence_context": "ACDEFGHIKLMNPQRSTVWY",
                "event_index": 9,
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
                "pgaa_rank": 1,
                "pgaa_score": 0.91,
                "cohort_or_dataset": "dataset1",
                "disease_or_context": "context1",
            }
        ]
    )

    candidates, decoys = compile_event_peptides(
        events,
        EventCompilerConfig(hla_i_lengths=(8,), max_decoys_per_candidate=1),
    )

    assert not candidates.empty
    assert not decoys.empty
    assert set(candidates["peptide_length"]) == {8}
    assert set(candidates["source_event_id"]) == {"EVT1"}
    for _, row in candidates.iterrows():
        start = int(row["altered_sequence_start"])
        event_position = int(row["event_position_in_peptide"])
        assert start + event_position == 9
        assert row["peptide_sequence"] == "ACDEFGHIKLMNPQRSTVWY"[start : start + 8]
    for _, row in decoys.iterrows():
        start = int(row["altered_sequence_start"])
        assert not (start <= 9 < start + int(row["peptide_length"]))


def test_compile_event_peptides_requires_real_sequence_context():
    events = pd.DataFrame(
        [
            {
                "source_event_id": "EVT_BAD",
                "source_event_type": "mutation",
                "source_gene": "GENE1",
                "event_coordinate": "p.X1X",
                "altered_sequence_context": "PEPTIDEX",
                "event_index": 2,
                "hla_allele": "HLA-A*02:01",
                "hla_class": "I",
            }
        ]
    )

    with pytest.raises(ValueError, match="invalid amino acids"):
        compile_event_peptides(events)


def test_compile_event_peptides_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        compile_event_peptides(pd.DataFrame([{"source_gene": "GENE1"}]))
