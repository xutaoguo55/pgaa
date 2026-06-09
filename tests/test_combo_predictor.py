"""Unit tests for ComboPredictor."""

import numpy as np
import pandas as pd
import pytest

from pgaa.core.combo_predictor import ComboPredictor


class TestComboPredictor:
    def test_additive_simple(self):
        """Additive prediction should sum single-gene alphas."""
        df_a = pd.DataFrame({
            "gene": ["g1", "g2", "g3"],
            "alpha": [0.5, -0.3, 0.0],
        })
        df_b = pd.DataFrame({
            "gene": ["g1", "g2", "g3"],
            "alpha": [0.2, 0.4, -0.1],
        })
        cp = ComboPredictor({"A": df_a, "B": df_b})
        pred = cp.predict_additive("A", "B")
        assert np.isclose(pred.set_index("gene").loc["g1", "alpha_pred"], 0.7)
        assert np.isclose(pred.set_index("gene").loc["g2", "alpha_pred"], 0.1)
        assert np.isclose(pred.set_index("gene").loc["g3", "alpha_pred"], -0.1)

    def test_synergy_bliss(self):
        """Bliss synergy = pred - (a + b). With additive data this is ~0."""
        df_a = pd.DataFrame({"gene": ["g1"], "alpha": [0.5]})
        df_b = pd.DataFrame({"gene": ["g1"], "alpha": [0.3]})
        cp = ComboPredictor({"A": df_a, "B": df_b})
        syn = cp.predict_synergy("A", "B", model="bliss")
        assert np.isclose(syn["synergy"].iloc[0], 0.0)

    def test_synergy_with_interaction(self):
        """If true combo = a + b + 0.5, Bliss synergy = 0.5."""
        df_a = pd.DataFrame({"gene": ["g1"], "alpha": [0.5]})
        df_b = pd.DataFrame({"gene": ["g1"], "alpha": [0.3]})
        cp = ComboPredictor({"A": df_a, "B": df_b})
        # manually override to simulate true combo = 0.5 + 0.3 + 0.5 = 1.3
        pred = cp.predict_additive("A", "B")
        pred["alpha_pred"] = pred["alpha_a"] + pred["alpha_b"] + 0.5
        bliss = pred["alpha_pred"] - (pred["alpha_a"] + pred["alpha_b"])
        assert np.isclose(bliss.iloc[0], 0.5)

    def test_predict_matrix_shape(self):
        """Pairwise matrix for 3 targets should have 3*(3+1)/2 = 6 pairs."""
        df = pd.DataFrame({"gene": ["g1", "g2"], "alpha": [0.1, 0.2]})
        cp = ComboPredictor({"A": df, "B": df, "C": df})
        mat = cp.predict_matrix()
        assert len(mat["target_a"].unique()) == 3
        assert mat[["target_a", "target_b"]].drop_duplicates().shape[0] == 6

    def test_missing_target_raises(self):
        cp = ComboPredictor({"A": pd.DataFrame({"gene": ["g1"], "alpha": [0.1]})})
        with pytest.raises(ValueError):
            cp.predict_additive("A", "B")
