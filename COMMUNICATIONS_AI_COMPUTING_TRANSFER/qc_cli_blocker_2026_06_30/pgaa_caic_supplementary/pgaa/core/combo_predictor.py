"""Combination perturbation predictor from single-gene PGAA estimates."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class ComboPredictor:
    """
    Predict combinatorial perturbation scores from single-gene alpha scores.

    Supports additive, Bliss independence, and Loewe synergy models.
    """

    def __init__(self, results_map: Dict[str, pd.DataFrame], alpha_col: str = "alpha"):
        """
        Parameters
        ----------
        results_map : dict
            Mapping target_gene -> DataFrame from PGAA estimate_target().
            Each DataFrame must contain 'gene' and alpha_col columns.
        alpha_col : str
            Column name for alpha scores.
        """
        self.results_map = {k: v.copy() for k, v in results_map.items()}
        self.alpha_col = alpha_col
        self._gene_pool = set()
        for df in self.results_map.values():
            self._gene_pool.update(df["gene"].tolist())

    def predict_additive(
        self,
        target_a: str,
        target_b: str,
        interaction_weight: float = 0.0,
    ) -> pd.DataFrame:
        """
        Additive prediction: alpha_{g|AB} = alpha_{g|A} + alpha_{g|B}.

        Parameters
        ----------
        target_a, target_b
            Genes to perturb simultaneously.
        interaction_weight
            Optional global interaction penalty (0 = pure additive).

        Returns
        -------
        DataFrame with columns: gene, alpha_pred, alpha_a, alpha_b
        """
        if target_a not in self.results_map or target_b not in self.results_map:
            raise ValueError("Both targets must be present in results_map.")

        df_a = self.results_map[target_a][["gene", self.alpha_col]].rename(
            columns={self.alpha_col: "alpha_a"}
        )
        df_b = self.results_map[target_b][["gene", self.alpha_col]].rename(
            columns={self.alpha_col: "alpha_b"}
        )
        merged = df_a.merge(df_b, on="gene", how="outer").fillna(0.0)
        merged["alpha_pred"] = merged["alpha_a"] + merged["alpha_b"]
        if interaction_weight != 0.0:
            merged["alpha_pred"] += interaction_weight * merged["alpha_a"] * merged["alpha_b"]
        return merged[["gene", "alpha_pred", "alpha_a", "alpha_b"]]

    def predict_synergy(
        self,
        target_a: str,
        target_b: str,
        model: str = "bliss",
    ) -> pd.DataFrame:
        """
        Predict synergy score for each downstream gene.

        Models
        ------
        bliss : S = alpha_AB - (alpha_A + alpha_B)
                Positive = synergistic; Negative = antagonistic.
        loewe  : S = alpha_AB / (alpha_A + alpha_B) - 1
                 (Requires single-gene dose-response assumption; approximated
                 here by treating alpha as log-fold-change.)
        """
        pred = self.predict_additive(target_a, target_b)
        if model == "bliss":
            pred["synergy"] = pred["alpha_pred"] - (pred["alpha_a"] + pred["alpha_b"])
        elif model == "loewe":
            denom = pred["alpha_a"] + pred["alpha_b"]
            # guard against division by zero
            pred["synergy"] = np.where(
                np.abs(denom) > 1e-12,
                pred["alpha_pred"] / denom - 1.0,
                np.nan,
            )
        else:
            raise ValueError(f"Unknown synergy model: {model}")
        return pred

    def predict_matrix(
        self,
        targets: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Compute pairwise additive predictions for all target combinations.

        Returns
        -------
        Long-format DataFrame: target_a, target_b, gene, alpha_pred
        """
        if targets is None:
            targets = list(self.results_map.keys())
        rows = []
        for i, a in enumerate(targets):
            for b in targets[i:]:
                pred = self.predict_additive(a, b)
                for _, r in pred.iterrows():
                    rows.append({
                        "target_a": a,
                        "target_b": b,
                        "gene": r["gene"],
                        "alpha_pred": r["alpha_pred"],
                    })
        return pd.DataFrame(rows)
