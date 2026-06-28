#!/usr/bin/env python3
"""Rebuild the Adamson 2016 full benchmark table from figure source data.

This script does not rerun raw-data preprocessing. It makes the manuscript
build table reproducible from the curated source-data CSV that also backs the
Adamson benchmark figure.
"""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figure_source_data" / "fig6_adamson_results.csv"
OUT = ROOT / "scripts" / "adamson2016_full_results.csv"
AUPRC_OUT = ROOT / "scripts" / "auprc_comparison.csv"
CI_OUT = ROOT / "scripts" / "adamson2016_method_summary_ci.csv"

EXPECTED_COLUMNS = [
    "target",
    "n_pert",
    "auroc_s1",
    "auprc_s1",
    "auroc_s2",
    "auprc_s2",
    "auroc_wilcox",
    "auprc_wilcox",
    "auroc_ttest",
    "auprc_ttest",
    "auroc_mast",
    "auprc_mast",
]

METHOD_COLUMNS = {
    "S1 Wasserstein": ("auroc_s1", "auprc_s1"),
    "S2 persistence": ("auroc_s2", "auprc_s2"),
    "Wilcoxon rank-sum": ("auroc_wilcox", "auprc_wilcox"),
    "t-test": ("auroc_ttest", "auprc_ttest"),
    "MAST": ("auroc_mast", "auprc_mast"),
}


def mean_ci(values: pd.Series) -> tuple[float, float, float]:
    """Mean and descriptive 95% t interval across five perturbations."""
    mean = float(values.mean())
    sem = float(values.std(ddof=1) / (len(values) ** 0.5))
    tcrit_df4 = 2.7764451051977987
    return mean, mean - tcrit_df4 * sem, mean + tcrit_df4 * sem


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Missing source-data file: {SRC}")

    df = pd.read_csv(SRC)
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected Adamson source-data columns:\n"
            f"observed={list(df.columns)}\nexpected={EXPECTED_COLUMNS}"
        )
    if len(df) != 5:
        raise ValueError(f"Expected 5 Adamson perturbations, found {len(df)}")

    df.to_csv(OUT, index=False)

    auprc = pd.DataFrame(
        {
            "method": ["S1", "S2", "Wilcoxon", "t-test", "MAST"],
            "mean_auprc": [
                df["auprc_s1"].mean(),
                df["auprc_s2"].mean(),
                df["auprc_wilcox"].mean(),
                df["auprc_ttest"].mean(),
                df["auprc_mast"].mean(),
            ],
        }
    )
    auprc.to_csv(AUPRC_OUT, index=False)

    ci_rows = []
    for method, (auroc_col, auprc_col) in METHOD_COLUMNS.items():
        auroc_mean, auroc_low, auroc_high = mean_ci(df[auroc_col])
        auprc_mean, auprc_low, auprc_high = mean_ci(df[auprc_col])
        ci_rows.append(
            {
                "method": method,
                "n_perturbations": len(df),
                "mean_auroc": auroc_mean,
                "auroc_ci95_low": auroc_low,
                "auroc_ci95_high": auroc_high,
                "mean_auprc": auprc_mean,
                "auprc_ci95_low": auprc_low,
                "auprc_ci95_high": auprc_high,
            }
        )
    ci = pd.DataFrame(ci_rows)
    ci.to_csv(CI_OUT, index=False)

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Wrote {AUPRC_OUT.relative_to(ROOT)}")
    print(f"Wrote {CI_OUT.relative_to(ROOT)}")
    print("Mean AUROC:")
    print(
        df[
            ["auroc_s1", "auroc_s2", "auroc_wilcox", "auroc_ttest", "auroc_mast"]
        ]
        .mean()
        .round(3)
        .to_string()
    )
    print("Mean AUPRC:")
    print(auprc.round(4).to_string(index=False))
    print("Descriptive 95% t intervals across perturbations:")
    print(ci.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
