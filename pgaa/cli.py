"""Command-line interface for running PGAA S1/S2 tests from CSV files."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import s2_test


def _read_expression(path: Path) -> tuple[np.ndarray, list[str], list[str]]:
    expr = pd.read_csv(path, index_col=0)
    if expr.empty:
        raise ValueError("Expression CSV is empty")
    if expr.columns.duplicated().any():
        duplicated = list(expr.columns[expr.columns.duplicated()])
        raise ValueError(f"Expression CSV has duplicated gene columns: {duplicated[:5]}")
    X = expr.to_numpy(dtype=float)
    if not np.isfinite(X).all():
        raise ValueError("Expression CSV contains NaN or Inf values")
    return X, list(expr.columns), list(expr.index.astype(str))


def _read_metadata(
    path: Path,
    cells: list[str],
    group_column: str,
    cell_type_column: str | None,
    library_size_column: str | None,
) -> pd.DataFrame:
    meta = pd.read_csv(path)
    if "cell_id" not in meta.columns:
        raise ValueError("Metadata CSV must contain a 'cell_id' column")
    if group_column not in meta.columns:
        raise ValueError(f"Metadata CSV does not contain group column '{group_column}'")
    if cell_type_column and cell_type_column not in meta.columns:
        raise ValueError(f"Metadata CSV does not contain cell type column '{cell_type_column}'")
    if library_size_column and library_size_column not in meta.columns:
        raise ValueError(
            f"Metadata CSV does not contain library size column '{library_size_column}'"
        )

    meta = meta.drop_duplicates("cell_id").set_index("cell_id")
    missing = [cell for cell in cells if cell not in meta.index]
    if missing:
        raise ValueError(f"Metadata is missing {len(missing)} expression cell IDs")
    return meta.loc[cells]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run PGAA S1 and/or S2 tests from a cell-by-gene expression CSV and "
            "a metadata CSV."
        )
    )
    parser.add_argument("--expression", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--target", required=True)
    parser.add_argument("--out-prefix", required=True, type=Path)
    parser.add_argument("--group-column", default="group")
    parser.add_argument("--perturbed-value", default="perturbed")
    parser.add_argument("--control-value", default="control")
    parser.add_argument("--cell-type-column")
    parser.add_argument("--library-size-column")
    parser.add_argument("--n-perms", type=int, default=2000)
    parser.add_argument("--n-bins", type=int, default=20)
    parser.add_argument("--skip-s1", action="store_true")
    parser.add_argument("--skip-s2", action="store_true")
    parser.add_argument("--random-state", type=int, default=42)
    return parser


def run(args: argparse.Namespace) -> tuple[Path | None, Path | None]:
    X, genes, cells = _read_expression(args.expression)
    if args.target not in genes:
        raise ValueError(f"Target gene '{args.target}' is not in expression columns")

    meta = _read_metadata(
        args.metadata,
        cells,
        args.group_column,
        args.cell_type_column,
        args.library_size_column,
    )
    groups = meta[args.group_column].astype(str)
    perturbed_idx = np.where(groups.to_numpy() == args.perturbed_value)[0]
    control_idx = np.where(groups.to_numpy() == args.control_value)[0]
    if len(perturbed_idx) == 0:
        raise ValueError(f"No cells matched perturbed value '{args.perturbed_value}'")
    if len(control_idx) == 0:
        raise ValueError(f"No cells matched control value '{args.control_value}'")

    cell_type = None
    if args.cell_type_column:
        cell_type = pd.Categorical(meta[args.cell_type_column]).codes

    library_size = None
    if args.library_size_column:
        library_size = meta[args.library_size_column].to_numpy(dtype=float)

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    s1_path = None
    s2_path = None

    if not args.skip_s1:
        res_s1 = prt_s1_test(
            X,
            genes,
            target=args.target,
            perturbed_idx=perturbed_idx,
            control_idx=control_idx,
            n_perms=args.n_perms,
            cell_type=cell_type,
            library_size=library_size,
            random_state=args.random_state,
        )
        s1_path = args.out_prefix.with_suffix(".s1.csv")
        res_s1.to_csv(s1_path, index=False)

    if not args.skip_s2:
        res_s2 = s2_test(
            X,
            genes,
            target=args.target,
            perturbed_idx=perturbed_idx,
            control_idx=control_idx,
            n_bins=args.n_bins,
            cell_type=cell_type,
            library_size=library_size,
        )
        s2_path = args.out_prefix.with_suffix(".s2.csv")
        res_s2.to_csv(s2_path, index=False)

    return s1_path, s2_path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    s1_path, s2_path = run(args)
    if s1_path:
        print(f"Wrote {s1_path}")
    if s2_path:
        print(f"Wrote {s2_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
