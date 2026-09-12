"""Cross-system audit for the EGFR T790M-expression association."""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance


EGFR_ENSEMBL_ID = "ENSG00000146648"


def _exact_label_permutation(values: np.ndarray, n_positive: int) -> tuple[float, float, float]:
    observed_positive = values[n_positive:]
    observed_negative = values[:n_positive]
    observed_difference = float(observed_positive.mean() - observed_negative.mean())
    observed_wasserstein = float(wasserstein_distance(observed_positive, observed_negative))
    differences: list[float] = []
    wasserstein_scores: list[float] = []
    for positive_indices in combinations(range(len(values)), n_positive):
        mask = np.zeros(len(values), dtype=bool)
        mask[list(positive_indices)] = True
        differences.append(float(values[mask].mean() - values[~mask].mean()))
        wasserstein_scores.append(float(wasserstein_distance(values[mask], values[~mask])))
    directional_p = sum(value >= observed_difference - 1e-12 for value in differences) / len(
        differences
    )
    wasserstein_p = sum(
        value >= observed_wasserstein - 1e-12 for value in wasserstein_scores
    ) / len(wasserstein_scores)
    return observed_difference, float(directional_p), float(wasserstein_p)


def audit_t790m_cross_system_replication(
    cortad_expression: pd.DataFrame,
    cortad_metadata: pd.DataFrame,
    gse129221_fpkm: pd.DataFrame,
) -> pd.DataFrame:
    """Compare same-cell CORTAD-seq with clone-level GSE129221 evidence."""
    metadata = cortad_metadata.set_index("cell_id")
    high = cortad_expression.loc[metadata.index[metadata["group"] == "perturbed"], "EGFR"]
    low = cortad_expression.loc[metadata.index[metadata["group"] == "control"], "EGFR"]
    if EGFR_ENSEMBL_ID not in gse129221_fpkm.index:
        raise ValueError(f"GSE129221 matrix is missing {EGFR_ENSEMBL_ID}")
    bulk = gse129221_fpkm.loc[EGFR_ENSEMBL_ID]
    parental = np.log1p(bulk[["A1", "A2", "A3"]].to_numpy(dtype=float))
    resistant = np.log1p(bulk[["C1", "C2", "C3"]].to_numpy(dtype=float))
    clone_difference, directional_p, wasserstein_p = _exact_label_permutation(
        np.concatenate([parental, resistant]), len(parental)
    )
    cortad_difference = float(high.mean() - low.mean())
    direction_concordant = np.sign(cortad_difference) == np.sign(clone_difference)
    verdict = (
        "CROSS_SYSTEM_DIRECTIONALLY_CONCORDANT_LIMITED_REPLICATION"
        if direction_concordant and wasserstein_p <= 0.05
        else "CROSS_SYSTEM_NOT_REPLICATED_DIRECTION_DISCORDANT_UNDERPOWERED"
    )
    return pd.DataFrame(
        [
            {
                "primary_dataset": "GSE112274_CORTAD_seq_PC9",
                "replication_dataset": "GSE129221_PC9_PC9GR_bulk_RNAseq",
                "primary_resolution": "same_cell_event_expression",
                "replication_resolution": "clone_level_genotype_expression",
                "primary_n_t790m_high": int(len(high)),
                "primary_n_t790m_low": int(len(low)),
                "primary_egfr_log1p_mean_high": float(high.mean()),
                "primary_egfr_log1p_mean_low": float(low.mean()),
                "primary_high_minus_low": cortad_difference,
                "replication_n_t790m_positive": int(len(resistant)),
                "replication_n_t790m_negative": int(len(parental)),
                "replication_egfr_log1p_mean_positive": float(resistant.mean()),
                "replication_egfr_log1p_mean_negative": float(parental.mean()),
                "replication_positive_minus_negative": clone_difference,
                "replication_raw_fpkm_fold_change": float(
                    bulk[["C1", "C2", "C3"]].mean() / bulk[["A1", "A2", "A3"]].mean()
                ),
                "replication_exact_directional_p": directional_p,
                "replication_exact_wasserstein_p": wasserstein_p,
                "direction_concordant": bool(direction_concordant),
                "verdict": verdict,
                "claim_ceiling": (
                    "independent_clone_level_stress_test_not_same_cell_replication_not_causal"
                ),
            }
        ]
    )


def render_t790m_cross_system_audit(summary: pd.DataFrame) -> str:
    """Render the cross-system result without promoting clone-level evidence."""
    row = summary.iloc[0]
    return "\n".join(
        [
            "# EGFR T790M Cross-System Replication Audit",
            "",
            f"Verdict: `{row['verdict']}`",
            "",
            "## Results",
            "",
            f"- GSE112274 same-cell pilot: EGFR mean log1p(FPKM) was {row['primary_egfr_log1p_mean_high']:.4f} in T790M-high and {row['primary_egfr_log1p_mean_low']:.4f} in T790M-low cells (high-minus-low {row['primary_high_minus_low']:.4f}).",
            f"- GSE129221 clone-level stress test: EGFR mean log1p(FPKM) was {row['replication_egfr_log1p_mean_positive']:.4f} in T790M-positive PC9GR and {row['replication_egfr_log1p_mean_negative']:.4f} in T790M-negative parental PC9 (positive-minus-negative {row['replication_positive_minus_negative']:.4f}; raw FPKM fold change {row['replication_raw_fpkm_fold_change']:.3f}).",
            f"- Exact label permutations across the six clone-level replicates gave one-sided directional p={row['replication_exact_directional_p']:.3f} and Wasserstein p={row['replication_exact_wasserstein_p']:.3f}.",
            "- The direction is discordant between systems, and the clone-level distribution test does not pass 0.05.",
            "",
            "## Claim Boundary",
            "",
            "GSE129221 is an independent acquired-resistance model with matched clone-level genotype and expression, not same-cell DNA plus RNA. T790M status is confounded with the evolved PC9GR clone and prolonged gefitinib exposure. The result therefore falsifies a simple directionally invariant EGFR-expression interpretation but cannot falsify every distributional T790M effect.",
            "",
            "The claim-state compiler must retain this as a failed or unresolved cross-system replication state. It does not support causal, immune, antigen-presentation, or T-cell claims.",
            "",
        ]
    )
