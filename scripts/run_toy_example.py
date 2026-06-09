#!/usr/bin/env python3
"""Run a small synthetic PGAA example.

This script is meant as a reviewer-facing smoke test: it constructs a tiny
Perturb-seq-like matrix, runs both PGAA statistics, and checks that planted
distributional responses are recovered near the top of the rankings.
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
    n_perturbed = 80
    n_control = 160
    n_cells = n_perturbed + n_control
    genes = ["TARGET", "S1_SHIFT", "S2_BIMODAL"] + [
        f"NULL_{i:02d}" for i in range(11)
    ]

    X = rng.normal(0.0, 0.35, size=(n_cells, len(genes)))
    perturbed_idx = np.arange(n_perturbed)
    control_idx = np.arange(n_perturbed, n_cells)

    X[perturbed_idx, genes.index("S1_SHIFT")] += 2.2

    half = n_perturbed // 2
    bimodal_col = genes.index("S2_BIMODAL")
    X[perturbed_idx[:half], bimodal_col] -= 2.0
    X[perturbed_idx[half:], bimodal_col] += 2.0

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
        n_bins=24,
        cell_type=cell_type,
        library_size=library_size,
    )

    top_s1 = list(res_s1.head(3)["gene"])
    top_s2 = list(res_s2.head(3)["gene"])
    if "S1_SHIFT" not in top_s1:
        raise SystemExit(f"Toy S1 check failed: top S1 genes were {top_s1}")
    if "S2_BIMODAL" not in top_s2:
        raise SystemExit(f"Toy S2 check failed: top S2 genes were {top_s2}")

    print("\nTop S1 results")
    print(res_s1[["gene", "W_observed", "p_value_perm"]].head(5).to_string(index=False))
    print("\nTop S2 results")
    print(res_s2[["gene", "S2", "n_peaks_on"]].head(5).to_string(index=False))
    print("\nTOY EXAMPLE PASSED")


if __name__ == "__main__":
    main()
