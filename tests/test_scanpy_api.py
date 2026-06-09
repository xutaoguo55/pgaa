"""Integration tests for Scanpy API."""

import anndata
import numpy as np
import pandas as pd
import pytest

from pgaa.tools.scanpy_api import virtual_oe


class TestScanpyAPI:
    def test_virtual_oe_basic(self):
        rng = np.random.default_rng(42)
        n = 200
        G = 50

        X = rng.lognormal(size=(n, G))  # raw-ish counts
        var = pd.DataFrame(index=[f"gene_{i}" for i in range(G)])
        obs = pd.DataFrame(index=[f"cell_{i}" for i in range(n)])
        adata = anndata.AnnData(X=X, obs=obs, var=var)

        # Add some fake HVG
        adata.var["highly_variable"] = False
        adata.var.iloc[:20, adata.var.columns.get_loc("highly_variable")] = True

        res = virtual_oe(adata, target="gene_0", use_linear_stage1=True, inplace=False)
        assert isinstance(res, pd.DataFrame)
        assert "alpha" in res.columns
        assert "p_value" in res.columns
        assert "significant" in res.columns

    def test_target_not_found_raises(self):
        adata = anndata.AnnData(X=np.zeros((10, 10)))
        with pytest.raises(ValueError):
            virtual_oe(adata, target="missing_gene", inplace=False)
