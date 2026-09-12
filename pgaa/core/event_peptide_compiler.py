"""Compile molecular event rows into peptide-HLA candidate units.

This module is intentionally conservative. It does not infer peptides from a
gene symbol alone. Each input event must provide an altered amino-acid sequence
context and the zero-based event position within that context.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pgaa.core.immune_evidence import VALID_AMINO_ACIDS


HLA_I_LENGTHS = (8, 9, 10, 11)
HLA_II_LENGTHS = tuple(range(12, 26))


@dataclass(frozen=True)
class EventCompilerConfig:
    hla_i_lengths: tuple[int, ...] = HLA_I_LENGTHS
    hla_ii_lengths: tuple[int, ...] = HLA_II_LENGTHS
    max_decoys_per_candidate: int = 1


REQUIRED_EVENT_COLUMNS = {
    "source_event_id",
    "source_event_type",
    "source_gene",
    "event_coordinate",
    "altered_sequence_context",
    "event_index",
    "hla_allele",
    "hla_class",
}


OPTIONAL_PASSTHROUGH_COLUMNS = [
    "pgaa_rank",
    "pgaa_score",
    "cohort_or_dataset",
    "disease_or_context",
]


def peptide_lengths_for_hla_class(hla_class: object, config: EventCompilerConfig) -> tuple[int, ...]:
    normalized = str(hla_class).strip().upper().replace("HLA-", "")
    if normalized in {"I", "1", "CLASSI", "CLASS_I"}:
        return config.hla_i_lengths
    if normalized in {"II", "2", "CLASSII", "CLASS_II"}:
        return config.hla_ii_lengths
    raise ValueError(f"unsupported hla_class: {hla_class}")


def _clean_sequence(sequence: object) -> str:
    if pd.isna(sequence):
        return ""
    return str(sequence).strip().upper()


def _event_index(value: object, sequence: str) -> int:
    try:
        index = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"event_index must be an integer, got {value!r}") from exc
    if index < 0 or index >= len(sequence):
        raise ValueError(
            f"event_index {index} is outside altered_sequence_context length {len(sequence)}"
        )
    return index


def _validate_sequence(sequence: str, event_id: object) -> None:
    if not sequence:
        raise ValueError(f"{event_id}: altered_sequence_context is empty")
    invalid = sorted(set(sequence) - VALID_AMINO_ACIDS)
    if invalid:
        raise ValueError(
            f"{event_id}: altered_sequence_context contains invalid amino acids: "
            f"{''.join(invalid)}"
        )


def event_containing_windows(sequence: str, event_index: int, lengths: tuple[int, ...]) -> list[tuple[str, int, int]]:
    """Return peptide windows that contain the event index.

    Output tuples are `(peptide, start, event_position_in_peptide)` where start
    is zero-based within the altered sequence context.
    """
    windows: list[tuple[str, int, int]] = []
    seen: set[tuple[str, int, int]] = set()
    for length in lengths:
        if length > len(sequence):
            continue
        first_start = max(0, event_index - length + 1)
        last_start = min(event_index, len(sequence) - length)
        for start in range(first_start, last_start + 1):
            peptide = sequence[start : start + length]
            event_position = event_index - start
            key = (peptide, start, event_position)
            if key not in seen:
                windows.append(key)
                seen.add(key)
    return windows


def _decoy_windows(
    sequence: str,
    event_index: int,
    lengths: tuple[int, ...],
    max_per_candidate: int,
) -> list[tuple[str, int]]:
    decoys: list[tuple[str, int]] = []
    for length in lengths:
        if length > len(sequence):
            continue
        for start in range(0, len(sequence) - length + 1):
            stop = start + length
            if not (start <= event_index < stop):
                decoys.append((sequence[start:stop], start))
    if max_per_candidate <= 0:
        return []
    return decoys[:max_per_candidate]


def compile_event_peptides(
    events: pd.DataFrame,
    config: EventCompilerConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compile event rows into candidate peptide and matched decoy tables."""
    config = config or EventCompilerConfig()
    missing = sorted(REQUIRED_EVENT_COLUMNS - set(events.columns))
    if missing:
        raise ValueError(f"event table is missing required columns: {missing}")

    candidates: list[dict[str, object]] = []
    decoys: list[dict[str, object]] = []
    for _, row in events.iterrows():
        event_id = row["source_event_id"]
        sequence = _clean_sequence(row["altered_sequence_context"])
        _validate_sequence(sequence, event_id)
        event_index = _event_index(row["event_index"], sequence)
        lengths = peptide_lengths_for_hla_class(row["hla_class"], config)
        windows = event_containing_windows(sequence, event_index, lengths)
        if not windows:
            raise ValueError(f"{event_id}: no event-containing peptide windows emitted")

        common = {
            "source_event_type": row["source_event_type"],
            "source_event_id": event_id,
            "source_gene": row["source_gene"],
            "event_coordinate": row["event_coordinate"],
            "hla_allele": row["hla_allele"],
            "hla_class": row["hla_class"],
        }
        for column in OPTIONAL_PASSTHROUGH_COLUMNS:
            common[column] = row[column] if column in row and not pd.isna(row[column]) else ""

        for window_index, (peptide, start, event_position) in enumerate(windows, start=1):
            candidate_id = f"{event_id}|{row['hla_allele']}|{len(peptide)}mer|{start}"
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    **common,
                    "peptide_sequence": peptide,
                    "peptide_length": len(peptide),
                    "event_position_in_peptide": event_position,
                    "altered_sequence_start": start,
                    "negative_control_group": "none",
                    "notes": "compiled_from_event_sequence",
                }
            )

            for decoy_index, (decoy_peptide, decoy_start) in enumerate(
                _decoy_windows(
                    sequence,
                    event_index,
                    (len(peptide),),
                    config.max_decoys_per_candidate,
                ),
                start=1,
            ):
                decoys.append(
                    {
                        "decoy_id": f"{candidate_id}|decoy{decoy_index}",
                        "matched_candidate_id": candidate_id,
                        "peptide_sequence": decoy_peptide,
                        "peptide_length": len(decoy_peptide),
                        "hla_allele": row["hla_allele"],
                        "hla_class": row["hla_class"],
                        "decoy_type": "same_context_non_event_window",
                        "source_event_id": event_id,
                        "source_gene": row["source_gene"],
                        "altered_sequence_start": decoy_start,
                        "notes": "does_not_cover_event_index",
                    }
                )

    return pd.DataFrame(candidates), pd.DataFrame(decoys)
