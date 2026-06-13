"""Scanpy/AnnData native API for PGAA."""

from typing import List, Optional

import anndata
import numpy as np
import pandas as pd

from pgaa.core.dml_engine import DMLEngine
from pgaa.core.null_calibrator import NullCalibrator


def virtual_oe(
    adata: anndata.AnnData,
    target: str,
    layer: str = None,
    n_confounders: int = 5,
    ml_method: str = "rf",
    use_linear_stage1: bool = False,
    use_scvi: bool = False,
    scvi_kwargs: Optional[dict] = None,
    hk_genes: Optional[List[str]] = None,
    n_top_genes: int = 2000,
    random_state: int = 42,
    inplace: bool = True,
) -> pd.DataFrame:
    """
    Virtual overexpression analysis on an AnnData object.

    Parameters
    ----------
    adata : AnnData
    target : str
        Target gene symbol (must be in adata.var_names).
    layer : str, optional
        Layer to use. If None, uses adata.X.
    n_confounders : int
        Number of PCs to use as confounders.
    ml_method : str
        ML method for nuisance estimation.
    use_linear_stage1 : bool
        If True, use fast linear PCA residualization.
    n_top_genes : int
        Number of highly variable genes to use.
    random_state : int
    inplace : bool
        If True, stores results in adata.uns['pgaa_oe_{target}'].

    Returns
    -------
    pd.DataFrame with causal effect estimates.
    """
    if target not in adata.var_names:
        raise ValueError(f"Target gene '{target}' not found in adata.var_names.")

    # Select HVGs + target
    if "highly_variable" in adata.var.columns:
        hvg_mask = adata.var["highly_variable"].values
    else:
        # fallback: top variable genes
        if layer is not None:
            X = adata.layers[layer]
        else:
            X = adata.X
        if hasattr(X, "toarray"):
            X = X.toarray()
        gene_var = np.var(X, axis=0)
        top_idx = np.argsort(gene_var)[::-1][:n_top_genes]
        hvg_mask = np.zeros(adata.n_vars, dtype=bool)
        hvg_mask[top_idx] = True

    # Ensure target is included
    target_idx = np.where(adata.var_names == target)[0][0]
    hvg_mask[target_idx] = True

    adata_sub = adata[:, hvg_mask].copy()

    if layer is not None:
        expr = adata_sub.layers[layer]
    else:
        expr = adata_sub.X

    if hasattr(expr, "toarray"):
        expr = expr.toarray()
    expr = np.asarray(expr, dtype=np.float64).T  # G x N

    genes = list(adata_sub.var_names)

    engine = DMLEngine(
        n_confounders=n_confounders,
        ml_method=ml_method,
        use_linear_stage1=use_linear_stage1,
        use_scvi=use_scvi,
        scvi_kwargs=scvi_kwargs,
        random_state=random_state,
    )
    tidx = genes.index(target)

    # scVI requires raw counts; if user passed log-normalized data
    # with use_scvi=True, warn but proceed (scVI will still train,
    # though sub-optimally).  Best practice: pass layer="counts".
    batch_labels = adata_sub.obs.get("batch", None)
    if batch_labels is not None:
        batch_labels = batch_labels.values
    engine.fit_confounders(
        expr, genes=genes, exclude_idx=tidx, batch_labels=batch_labels
    )
    results = engine.estimate_target(target, hk_genes=hk_genes)

    # Add exogenous variance ratio
    tidx = genes.index(target)
    target_expr = expr[tidx, :]
    var_total = np.var(target_expr, ddof=1)
    var_eta = np.var(engine.residuals[tidx, :], ddof=1)
    results["var_eta_ratio"] = var_eta / var_total if var_total > 0 else np.nan

    if inplace:
        adata.uns[f"pgaa_oe_{target}"] = {
            "results": results,
            "parameters": {
                "n_confounders": n_confounders,
                "ml_method": ml_method,
                "use_linear_stage1": use_linear_stage1,
                "use_scvi": use_scvi,
                "n_top_genes": n_top_genes,
            },
        }

    return results


def virtual_ko(
    adata: anndata.AnnData,
    target: str,
    use_permutation: bool = True,
    n_perms: int = 5000,
    perturbation_col: str = "perturbation",
    **kwargs,
) -> pd.DataFrame:
    """
    Virtual knockout analysis.

    Two modes:
      1. Continuous (default): uses target gene expression as treatment
         (same as virtual_oe). Suitable for natural variation / eQTL.
      2. Perturb-seq: if ``adata.obs[perturbation_col]`` exists and
         contains binary/control labels, uses control-only PCA and a
         binary treatment indicator.  This avoids absorbing perturbation
         effects into confounders.
    """
    # Detect Perturb-seq mode
    has_pert = perturbation_col in adata.obs.columns
    if has_pert:
        labels = adata.obs[perturbation_col].astype(str)
        # Heuristic: presence of 'control' and at least one non-control
        pert_mode = (labels == "control").any() and (labels != "control").any()
    else:
        pert_mode = False

    if not pert_mode:
        # Fall back to continuous mode
        results = virtual_oe(adata, target, inplace=False, **kwargs)
        if use_permutation:
            layer = kwargs.get("layer", None)
            n_confounders = kwargs.get("n_confounders", 5)
            ml_method = kwargs.get("ml_method", "rf")
            use_linear = kwargs.get("use_linear_stage1", False)
            n_top_genes = kwargs.get("n_top_genes", 2000)
            random_state = kwargs.get("random_state", 42)

            sub = adata[:, adata.var_names.isin(results["gene"].tolist() + [target])]
            expr = sub.layers[layer] if layer is not None else sub.X
            if hasattr(expr, "toarray"):
                expr = expr.toarray()
            expr = np.asarray(expr, dtype=np.float64).T
            genes = list(sub.var_names)

            engine = DMLEngine(
                n_confounders=n_confounders, ml_method=ml_method,
                use_linear_stage1=use_linear, random_state=random_state,
            )
            tidx = genes.index(target)
            engine.fit_confounders(expr, genes=genes, exclude_idx=tidx)
            perm_res = engine.permutation_test(target, n_perms=n_perms)
            results = results.merge(
                perm_res[["gene", "p_value_perm"]], on="gene", how="left"
            )
        return results

    # ---- Perturb-seq binary mode ----
    layer = kwargs.get("layer", None)
    n_confounders = kwargs.get("n_confounders", 5)
    use_linear = kwargs.get("use_linear_stage1", False)
    use_scvi = kwargs.get("use_scvi", False)
    scvi_kwargs = kwargs.get("scvi_kwargs", None)
    hk_genes = kwargs.get("hk_genes", None)
    n_top_genes = kwargs.get("n_top_genes", 2000)
    random_state = kwargs.get("random_state", 42)

    # Subset to HVGs + target
    if "highly_variable" in adata.var.columns:
        hvg_mask = adata.var["highly_variable"].values
    else:
        X = adata.layers[layer] if layer is not None else adata.X
        if hasattr(X, "toarray"):
            X = X.toarray()
        gene_var = np.var(X, axis=0)
        top_idx = np.argsort(gene_var)[::-1][:n_top_genes]
        hvg_mask = np.zeros(adata.n_vars, dtype=bool)
        hvg_mask[top_idx] = True
    target_idx = np.where(adata.var_names == target)[0][0]
    hvg_mask[target_idx] = True
    adata_sub = adata[:, hvg_mask].copy()

    expr = adata_sub.layers[layer] if layer is not None else adata_sub.X
    if hasattr(expr, "toarray"):
        expr = expr.toarray()
    expr = np.asarray(expr, dtype=np.float64).T  # G x N
    genes = list(adata_sub.var_names)

    control_mask = (labels == "control").values
    treatment = (labels == target).values

    engine = DMLEngine(
        n_confounders=n_confounders,
        ml_method="linear" if use_linear else "rf",
        use_linear_stage1=use_linear,
        use_scvi=use_scvi,
        scvi_kwargs=scvi_kwargs,
        random_state=random_state,
    )
    tidx = genes.index(target)
    batch_labels = adata_sub.obs.get("batch", None)
    if batch_labels is not None:
        batch_labels = batch_labels.values
    engine.fit_confounders(
        expr, genes=genes, exclude_idx=tidx, control_mask=control_mask,
        batch_labels=batch_labels,
    )
    results = engine.estimate_target_binary(treatment, target)

    # Add var-eta ratio (interpreted as residual variance after control)
    target_expr = expr[tidx, :]
    var_total = np.var(target_expr, ddof=1)
    var_eta = np.var(engine.residuals[tidx, :], ddof=1)
    results["var_eta_ratio"] = var_eta / var_total if var_total > 0 else np.nan
    return results


def power_table(n_cells_list, alpha_effects, sigma_eta=0.28, sigma_nu=1.0):
    """Generate power analysis table."""
    rows = []
    for n in n_cells_list:
        for a in alpha_effects:
            rows.append(
                NullCalibrator.power_analysis(
                    n, a, sigma_eta=sigma_eta, sigma_nu=sigma_nu
                )
            )
    return pd.DataFrame(rows)
