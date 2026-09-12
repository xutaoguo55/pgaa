#!/usr/bin/env python3
"""Validate the top-journal recharter benchmark matrix."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "benchmark_id",
    "required_input",
    "comparator",
    "endpoint",
    "pass_condition",
    "current_status",
    "blocking_file",
    "next_action",
]

ALLOWED_STATUS = {"not_started", "in_progress", "complete", "blocked"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check that the top-journal benchmark matrix is actionable."
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("evidence/top_journal_benchmark_matrix_template.tsv"),
    )
    return parser


def validate_matrix(matrix: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in matrix.columns]
    if missing_columns:
        errors.append(f"missing columns: {missing_columns}")
        return errors

    if matrix.empty:
        errors.append("matrix has no benchmark rows")
        return errors

    for idx, row in matrix.iterrows():
        row_id = row.get("benchmark_id", f"row_{idx}")
        for column in REQUIRED_COLUMNS:
            value = row[column]
            if pd.isna(value) or str(value).strip() == "":
                errors.append(f"{row_id}: empty {column}")
        status = str(row["current_status"]).strip()
        if status not in ALLOWED_STATUS:
            errors.append(
                f"{row_id}: invalid current_status '{status}', expected one of "
                f"{sorted(ALLOWED_STATUS)}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    matrix = pd.read_csv(args.matrix, sep="\t")
    errors = validate_matrix(matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Benchmark matrix OK: {args.matrix} ({len(matrix)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
