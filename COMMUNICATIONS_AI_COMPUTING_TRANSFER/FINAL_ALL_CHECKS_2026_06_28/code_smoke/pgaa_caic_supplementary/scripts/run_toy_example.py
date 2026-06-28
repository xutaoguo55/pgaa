#!/usr/bin/env python3
"""Run a small synthetic PGAA example.

This script is meant as a package smoke test: it constructs a synthetic
Perturb-seq-like matrix, runs both PGAA statistics, and checks that clearly
planted distributional responses are recovered near the top of the rankings.
It is not a genome-scale validation benchmark.
"""
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pgaa.core.prt import prt_s1_test  # noqa: E402
from pgaa.core.prt_s2 import s2_test  # noqa: E402


def build_toy_data(seed: int = 42):
    rng = np.random.default_rng(seed)
    n_perturbed = 200
    n_control = 400
    n_cells = n_perturbed + n_control
    genes = ["TARGET", "PGAAW_SHIFT", "PGAAH_BIMODAL"] + [
        f"NULL_{i:02d}" for i in range(11)
    ]

    X = rng.normal(0.0, 0.08, size=(n_cells, len(genes)))
    perturbed_idx = np.arange(n_perturbed)
    control_idx = np.arange(n_perturbed, n_cells)

    X[perturbed_idx, genes.index("PGAAW_SHIFT")] += 2.0

    half = n_perturbed // 2
    bimodal_col = genes.index("PGAAH_BIMODAL")
    X[perturbed_idx[:half], bimodal_col] -= 2.5
    X[perturbed_idx[half:], bimodal_col] += 2.5

    cell_type = np.resize(np.array([0, 1, 2]), n_cells)
    library_size = np.full(n_cells, 10000.0)
    return X, genes, perturbed_idx, control_idx, cell_type, library_size


def main() -> None:
    X, genes, perturbed_idx, control_idx, cell_type, library_size = build_toy_data()

    res_s1 = prt_s1_test(
        X,
        genes,
        target="TARGET",
        perturbed_idx=perturbed_idx,
        control_idx=control_idx,
        n_perms=99,
        cell_type=cell_type,
        library_size=library_size,
        random_state=42,
    )
    res_s1 = res_s1.sort_values(["p_value_perm", "W_observed"], ascending=[True, False])

    res_s2 = s2_test(
        X,
        genes,
        target="TARGET",
        perturbed_idx=perturbed_idx,
        control_idx=control_idx,
        n_bins=12,
        cell_type=cell_type,
        library_size=library_size,
    )

    top_s1 = list(res_s1.head(3)["gene"])
    top_s2 = list(res_s2.head(3)["gene"])
    if "PGAAW_SHIFT" not in top_s1:
        raise SystemExit(f"Toy PGAA-W check failed: top PGAA-W genes were {top_s1}")
    if "PGAAH_BIMODAL" not in top_s2:
        raise SystemExit(f"Toy PGAA-H check failed: top PGAA-H genes were {top_s2}")

    print("\nTop PGAA-W results")
    print(res_s1[["gene", "W_observed", "p_value_perm"]].head(5).to_string(index=False))
    print("\nTop PGAA-H results")
    print(res_s2[["gene", "S2", "n_peaks_on"]].head(5).to_string(index=False))
    print("\nTOY EXAMPLE PASSED")


if __name__ == "__main__":
    main()
