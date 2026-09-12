"""Audit EGFR expression across early and late T790M evolutionary paths."""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


EGFR_ENSEMBL_ID = "ENSG00000146648"
STAGES = {
    "parental": ("PC9_VEH.rep1", "PC9_VEH.rep2"),
    "gefitinib_tolerant": ("PC9_GT_VEH.rep1", "PC9_GT_VEH.rep2"),
    "wz4002_tolerant": ("PC9_WT_VEH.rep1", "PC9_WT_VEH.rep2"),
    "early_t790m_gr2": ("PC9_GR2_VEH.rep1", "PC9_GR2_VEH.rep2"),
    "late_t790m_gr3": ("PC9_GR3_VEH.rep1", "PC9_GR3_VEH.rep2"),
}


def _exact_directional_p(first: np.ndarray, second: np.ndarray) -> float:
    values = np.concatenate([first, second])
    observed = float(second.mean() - first.mean())
    differences = []
    for second_indices in combinations(range(len(values)), len(second)):
        mask = np.zeros(len(values), dtype=bool)
        mask[list(second_indices)] = True
        differences.append(float(values[mask].mean() - values[~mask].mean()))
    if observed >= 0:
        return sum(value >= observed - 1e-12 for value in differences) / len(differences)
    return sum(value <= observed + 1e-12 for value in differences) / len(differences)


def audit_t790m_evolution_trajectory(cpm: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build stage summaries and predeclared pairwise trajectory contrasts."""
    if EGFR_ENSEMBL_ID not in cpm.index:
        raise ValueError(f"GSE75602 matrix is missing {EGFR_ENSEMBL_ID}")
    missing = sorted({column for columns in STAGES.values() for column in columns} - set(cpm.columns))
    if missing:
        raise ValueError(f"GSE75602 matrix is missing stage columns: {missing}")
    egfr = cpm.loc[EGFR_ENSEMBL_ID]
    stage_values: dict[str, np.ndarray] = {}
    stage_rows = []
    for stage, columns in STAGES.items():
        values = egfr[list(columns)].to_numpy(dtype=float)
        stage_values[stage] = values
        stage_rows.append(
            {
                "stage": stage,
                "t790m_state": "positive" if "t790m" in stage else "negative_or_not_selected",
                "evolution_path": (
                    "pre_existing_early" if stage == "early_t790m_gr2" else
                    "drug_tolerant_evolved_late" if stage == "late_t790m_gr3" else
                    "precursor_or_parental"
                ),
                "n_replicates": int(len(values)),
                "egfr_cpm_mean": float(values.mean()),
                "egfr_cpm_min": float(values.min()),
                "egfr_cpm_max": float(values.max()),
                "egfr_log1p_cpm_mean": float(np.log1p(values).mean()),
            }
        )
    contrasts = [
        ("parental_to_early_t790m", "parental", "early_t790m_gr2"),
        ("parental_to_late_t790m", "parental", "late_t790m_gr3"),
        ("tolerant_to_late_t790m", "gefitinib_tolerant", "late_t790m_gr3"),
        ("early_to_late_t790m", "early_t790m_gr2", "late_t790m_gr3"),
    ]
    contrast_rows = []
    for contrast, first_stage, second_stage in contrasts:
        first = stage_values[first_stage]
        second = stage_values[second_stage]
        difference = float(np.log1p(second).mean() - np.log1p(first).mean())
        contrast_rows.append(
            {
                "contrast": contrast,
                "first_stage": first_stage,
                "second_stage": second_stage,
                "second_minus_first_log1p_cpm": difference,
                "raw_cpm_fold_change": float(second.mean() / first.mean()),
                "all_pairwise_direction_consistent": bool(
                    second.min() > first.max() if difference > 0 else second.max() < first.min()
                ),
                "exact_directional_p": _exact_directional_p(first, second),
                "inference_state": "descriptive_direction_only_n2_per_stage",
            }
        )
    return pd.DataFrame(stage_rows), pd.DataFrame(contrast_rows)


def evolution_trajectory_verdict(contrasts: pd.DataFrame) -> str:
    """State whether evolution modifies the observed EGFR direction."""
    indexed = contrasts.set_index("contrast")
    parent_early = indexed.loc["parental_to_early_t790m", "second_minus_first_log1p_cpm"]
    parent_late = indexed.loc["parental_to_late_t790m", "second_minus_first_log1p_cpm"]
    tolerant_late = indexed.loc["tolerant_to_late_t790m", "second_minus_first_log1p_cpm"]
    if parent_early > 0 and parent_late > 0 and tolerant_late < 0:
        return "EVOLUTION_STAGE_MODULATES_EGFR_DIRECTION_NO_FIXED_T790M_EFFECT"
    return "EVOLUTION_TRAJECTORY_INCONCLUSIVE"


def render_t790m_evolution_audit(stages: pd.DataFrame, contrasts: pd.DataFrame) -> str:
    """Render a conservative small-sample trajectory report."""
    verdict = evolution_trajectory_verdict(contrasts)
    lines = [
        "# GSE75602 T790M Evolution-Trajectory Audit",
        "",
        f"Verdict: `{verdict}`",
        "",
        "## Vehicle-State EGFR Trajectory",
        "",
        "| Stage | T790M state | Mean CPM | Replicates |",
        "|---|---|---:|---:|",
    ]
    for _, row in stages.iterrows():
        lines.append(
            f"| {row['stage']} | {row['t790m_state']} | {row['egfr_cpm_mean']:.3f} | {row['n_replicates']} |"
        )
    lines.extend(["", "## Locked Contrasts", "", "| Contrast | Fold change | Exact directional p | Direction robust |", "|---|---:|---:|---|"])
    for _, row in contrasts.iterrows():
        lines.append(
            f"| {row['contrast']} | {row['raw_cpm_fold_change']:.3f} | {row['exact_directional_p']:.3f} | {row['all_pairwise_direction_consistent']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Both early pre-existing-path GR2 and late drug-tolerant-path GR3 are T790M-positive and have higher EGFR CPM than parental PC9. However, late GR3 is lower than the gefitinib-tolerant precursor state and lower than early GR2. The observed EGFR direction therefore depends on the comparison state and evolutionary path rather than behaving as a fixed T790M effect.",
            "",
            "Each state has only two RNA-seq replicates. The smallest attainable one-sided exact permutation p value is 1/6 (0.167), so these contrasts are descriptive even when every cross-replicate pair has the same direction.",
            "",
            "This trajectory can explain why clone-level systems show different magnitudes, but it does not rescue the discordance with the GSE112274 same-cell result. The cross-system T790M-expression claim remains failed or unresolved.",
            "",
        ]
    )
    return "\n".join(lines)
