"""
DML/GCM exploratory association engine for PGAA.

Implements Double Machine Learning (Chernozhukov et al. 2018) and
Generalized Covariance Measure (Shah & Peters 2020) style residual scoring
for observational scRNA-seq data. This module is not used for the primary
claims in the manuscript and should not be presented as causal discovery.
"""

import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import sparse, stats
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler


class DMLEngine:
    """
    Double Machine Learning style engine for virtual KO/OE association scoring.

    Parameters
    ----------
    n_confounders : int
        Number of top PCs to use as confounders (linear) or max dimensions
        for nonlinear nuisance estimation.
    ml_method : str
        ML method for nuisance estimation: 'rf' (RandomForest), 'ridge',
        or 'linear' (fast OLS fallback).
    n_folds : int
        Number of folds for cross-fitting.
    use_linear_stage1 : bool
        If True, use linear PCA regression for Stage 1 (fast, compatible
        with original SPECTRA). If False, use ML-based residualization.
    random_state : int
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_confounders: int = 5,
        ml_method: str = "rf",
        n_folds: int = 5,
        use_linear_stage1: bool = False,
        use_scvi: bool = False,
        scvi_kwargs: Optional[dict] = None,
        random_state: int = 42,
    ):
        self.n_confounders = n_confounders
        self.ml_method = ml_method
        self.n_folds = n_folds
        self.use_linear_stage1 = use_linear_stage1
        self.use_scvi = use_scvi
        self.scvi_kwargs = scvi_kwargs or {}
        self.random_state = random_state

        self._expr = None          # G x N dense array
        self._genes = None         # list of gene names
        self._confounders = None   # N x K matrix
        self._residuals = None     # G x N residual matrix (after Stage 1)
        self._target_residuals = None  # cached for current target
        self._target_gene = None
        self._var_eta = None
        self._scvi_engine = None

    # ------------------------------------------------------------------ #
    # Stage 1: Confounder extraction & residualization
    # ------------------------------------------------------------------ #

    def fit_confounders(
        self,
        expr: np.ndarray,
        genes: Optional[List[str]] = None,
        exclude_idx: Optional[int] = None,
        control_mask: Optional[np.ndarray] = None,
        batch_labels: Optional[np.ndarray] = None,
    ) -> "DMLEngine":
        """
        Fit confounder model on expression matrix.

        Parameters
        ----------
        expr : np.ndarray, shape (G, N)
            Gene expression matrix (genes as rows, cells as columns).
            For linear mode: should be log-normalized.
            For scVI mode: should be raw counts (scVI handles normalization).
        genes : list of str, optional
            Gene names. If None, uses indices.
        exclude_idx : int, optional
            Index of a gene to exclude from confounder PCA (e.g. the
            target gene), preventing over-control of its own variation.
        control_mask : np.ndarray, optional
            Boolean mask of length N. If provided, PCA loadings are
            estimated on control cells only to avoid absorbing
            perturbation-induced variation.  Ignored when use_scvi=True.
        batch_labels : np.ndarray, optional
            Batch labels for each cell.  Only used when use_scvi=True
            so that scVI can perform batch correction.

        Returns
        -------
        self
        """
        if sparse.issparse(expr):
            expr = expr.toarray()
        self._expr = np.asarray(expr, dtype=np.float64)
        G, N = self._expr.shape

        if genes is None:
            genes = [f"gene_{i}" for i in range(G)]
        self._genes = list(genes)

        X_cell = self._expr.T  # N x G

        if self.use_scvi:
            from pgaa.core.scvi_confounder import SCVIConfounder
            self._scvi_engine = SCVIConfounder(
                n_latent=self.n_confounders,
                random_state=self.random_state,
                **self.scvi_kwargs,
            )
            self._scvi_engine.fit(
                self._expr,  # G x N raw counts (or log1p if user passed that)
                genes=self._genes,
                batch_labels=batch_labels,
                exclude_idx=exclude_idx,
            )
            # Get scVI-corrected expression (denoised, batch-corrected, log1p)
            # then run standard linear PCA + cross-fitted residualization on it.
            self._expr_corrected = self._scvi_engine.get_corrected_expression(
                genes=self._genes
            )  # G x N
            X_cell_corr = self._expr_corrected.T  # N x G
            scaler_ref = StandardScaler()
            X_std = scaler_ref.fit_transform(X_cell_corr)
            K = min(self.n_confounders, N, G)
            if exclude_idx is not None:
                mask = np.ones(G, dtype=bool)
                mask[exclude_idx] = False
                X_std_pca = X_std[:, mask]
            else:
                X_std_pca = X_std
            U, s, Vt = np.linalg.svd(X_std_pca, full_matrices=False)
            self._confounders = U[:, :K] * s[:K]  # N x K
            self._pca_variance_ratio = (s[:K] ** 2) / np.sum(s ** 2)
            self._residuals = self._cross_fitted_stage1(
                X_cell_corr, linear=self.use_linear_stage1, exclude_idx=exclude_idx
            )
            return self

        K = min(self.n_confounders, N, G)

        if control_mask is not None and control_mask.sum() > K:
            self._confounders, self._pca_variance_ratio, self._residuals = \
                self._control_only_stage1(X_cell, control_mask, exclude_idx, linear=self.use_linear_stage1)
        else:
            scaler_ref = StandardScaler()
            X_std = scaler_ref.fit_transform(X_cell)

            # Exclude target from PCA to avoid over-control
            if exclude_idx is not None:
                mask = np.ones(G, dtype=bool)
                mask[exclude_idx] = False
                X_std_pca = X_std[:, mask]
            else:
                X_std_pca = X_std

            U, s, Vt = np.linalg.svd(X_std_pca, full_matrices=False)
            self._confounders = U[:, :K] * s[:K]  # N x K
            self._pca_variance_ratio = (s[:K] ** 2) / np.sum(s ** 2)

            self._residuals = self._cross_fitted_stage1(
                X_cell, linear=self.use_linear_stage1, exclude_idx=exclude_idx
            )

        return self

    def _get_ml_estimator(self):
        if self.ml_method == "rf":
            return RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=max(5, self._expr.shape[1] // 20),
                max_features="sqrt",
                random_state=self.random_state,
                n_jobs=-1,
            )
        elif self.ml_method == "ridge":
            return RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0])
        elif self.ml_method == "linear":
            return None
        else:
            raise ValueError(f"Unknown ml_method: {self.ml_method}")

    def _cross_fitted_stage1(
        self,
        X_cell: np.ndarray,       # N x G
        linear: bool = False,
        exclude_idx: Optional[int] = None,
    ) -> np.ndarray:              # G x N
        """
        Split-sample PCA + cross-fitted residualization.
        PCA loadings are estimated on training folds only to ensure
        out-of-sample confounder projections.
        """
        N, G = X_cell.shape
        residuals = np.zeros((G, N), dtype=np.float64)
        kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)

        # Mask for genes included in PCA
        pca_mask = np.ones(G, dtype=bool)
        if exclude_idx is not None:
            pca_mask[exclude_idx] = False

        for train_idx, test_idx in kf.split(X_cell):
            X_train = X_cell[train_idx, :]   # N_train x G
            X_test = X_cell[test_idx, :]     # N_test x G

            # Standardize using train statistics
            mean_train = X_train.mean(axis=0)
            std_train = X_train.std(axis=0, ddof=1) + 1e-8
            X_train_std = (X_train - mean_train) / std_train
            X_test_std = (X_test - mean_train) / std_train

            # PCA on train data only (excluding target gene)
            X_train_pca = X_train_std[:, pca_mask]
            X_test_pca = X_test_std[:, pca_mask]
            K_fold = min(self.n_confounders, X_train_pca.shape[0], X_train_pca.shape[1])
            _, _, Vt = np.linalg.svd(X_train_pca, full_matrices=False)
            V = Vt[:K_fold, :].T  # (G-1) x K_fold

            # Project train and test onto loadings
            Z_train = X_train_pca @ V   # N_train x K_fold
            Z_test = X_test_pca @ V     # N_test x K_fold

            for g_idx in range(G):
                y_train = X_train[:, g_idx]
                y_test = X_test[:, g_idx]

                if linear:
                    Zd_train = np.column_stack([np.ones(len(Z_train)), Z_train])
                    Zd_test = np.column_stack([np.ones(len(Z_test)), Z_test])
                    beta = np.linalg.pinv(Zd_train.T @ Zd_train) @ (Zd_train.T @ y_train)
                    y_pred = Zd_test @ beta
                else:
                    estimator = self._get_ml_estimator()
                    estimator.fit(Z_train, y_train)
                    y_pred = estimator.predict(Z_test)

                residuals[g_idx, test_idx] = y_test - y_pred

        return residuals

    def _control_only_stage1(
        self,
        X_cell: np.ndarray,
        control_mask: np.ndarray,
        exclude_idx: Optional[int],
        linear: bool,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        PCA fit on control cells only, residualization on all cells.
        Prevents perturbation-induced variation from entering confounders.
        """
        N, G = X_cell.shape
        scaler = StandardScaler()
        scaler.fit(X_cell[control_mask])
        X_std = scaler.transform(X_cell)

        pca_mask = np.ones(G, dtype=bool)
        if exclude_idx is not None:
            pca_mask[exclude_idx] = False

        X_ctrl_std = X_std[control_mask][:, pca_mask]
        K = min(self.n_confounders, X_ctrl_std.shape[0], X_ctrl_std.shape[1])
        _, s, Vt = np.linalg.svd(X_ctrl_std, full_matrices=False)
        V = Vt[:K, :].T  # (G-1) x K

        # Confounders for all cells
        confounders = (X_std[:, pca_mask] @ V)
        var_ratio = (s[:K] ** 2) / np.sum(s ** 2)

        # Residualize every gene w.r.t confounders
        residuals = np.zeros((G, N), dtype=np.float64)
        Z_all = confounders  # N x K
        for g_idx in range(G):
            y = X_cell[:, g_idx]
            if linear:
                Zd = np.column_stack([np.ones(len(Z_all)), Z_all])
                beta = np.linalg.pinv(Zd.T @ Zd) @ (Zd.T @ y)
                y_pred = Zd @ beta
            else:
                estimator = self._get_ml_estimator()
                estimator.fit(Z_all[control_mask], y[control_mask])
                y_pred = estimator.predict(Z_all)
            residuals[g_idx, :] = y - y_pred

        return confounders, var_ratio, residuals

    # ------------------------------------------------------------------ #
    # Stage 2: Neyman-orthogonal association scoring
    # ------------------------------------------------------------------ #

    def estimate_target(
        self,
        target_gene: Union[str, int],
        hk_genes: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Estimate residual association scores for a target gene against all other genes.

        Uses the Generalized Covariance Measure (GCM) test statistic
        for analytical p-values without permutation.

        Parameters
        ----------
        target_gene : str or int
            Name or index of query gene.
        hk_genes : list of str, optional
            Housekeeping gene names.  If provided, their p-values are
            used to estimate an empirical null distribution and calibrate
            FDR (storey-like π0 estimate from HK genes).

        Returns
        -------
        pd.DataFrame
            Columns: gene, alpha, se, z_score, p_value, p_adjusted,
                     ci_lower, ci_upper, significant
        """
        if self._residuals is None:
            raise RuntimeError("Call fit_confounders() first.")

        tidx = self._get_gene_index(target_gene)
        self._target_gene = target_gene

        D = self._residuals[tidx, :]  # N
        other_idx = [i for i in range(len(self._genes)) if i != tidx]
        other_genes = [self._genes[i] for i in other_idx]

        # Center target residual (eta)
        D_c = D - np.mean(D)
        self._var_eta = np.var(D_c, ddof=1)
        var_eta_denom = np.sum(D_c ** 2)  # N * Var_eta

        if var_eta_denom < 1e-12:
            warnings.warn(f"Target {target_gene} has near-zero residual variance.")
            return self._empty_results(other_genes)

        # Vectorized OLS for all other genes simultaneously
        Y = self._residuals[other_idx, :]  # (G-1) x N
        Y_c = Y - np.mean(Y, axis=1, keepdims=True)

        alphas = (Y_c @ D_c) / var_eta_denom  # G-1

        # ---- GCM test statistic (Shah & Peters 2020) ----
        # S_{g,i} = R_D[i] * R_{Y_g}[i]
        S = Y_c * D_c  # (G-1) x N, element-wise
        S_bar = np.mean(S, axis=1)  # G-1
        # Sample variance of S (with ddof=1 for small-sample safety)
        sigma2_S = np.var(S, axis=1, ddof=1)  # G-1
        sigma_S = np.sqrt(sigma2_S + 1e-15)

        N = len(D_c)
        z_scores = np.sqrt(N) * S_bar / sigma_S  # G-1
        p_values = 2 * stats.norm.sf(np.abs(z_scores))

        # ---- Neyman-orthogonal standard error for alpha ----
        # SE(alpha) = sigma_S / (sqrt(N) * Var(D_c))
        ses = sigma_S / (np.sqrt(N) * var_eta_denom / N)  # G-1
        ci_lower = alphas - 1.96 * ses
        ci_upper = alphas + 1.96 * ses

        res = pd.DataFrame({
            "gene": other_genes,
            "alpha": alphas,
            "se": ses,
            "z_score": z_scores,
            "p_value": p_values,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
        })

        # ---- FDR with optional HK calibration ----
        from pgaa.core.multiple_testing import apply_fdr
        if hk_genes:
            # π0 estimate from HK genes (proportion of truly null)
            hk_mask = res["gene"].isin(hk_genes)
            if hk_mask.sum() > 0:
                hk_pvals = res.loc[hk_mask, "p_value"].values
                # Storey π0 = median(p) * 2  (conservative estimate)
                pi0 = min(1.0, np.median(hk_pvals) * 2)
                # Adjusted BH-FDR using π0
                m = len(res)
                res = res.sort_values("p_value").reset_index(drop=True)
                res["rank"] = np.arange(1, m + 1)
                res["p_adjusted"] = np.minimum.accumulate(
                    res["p_value"] * m * pi0 / res["rank"][::-1].values
                )[::-1]
                res["significant"] = res["p_adjusted"] < 0.05
                res = res.sort_values("p_value")
            else:
                res = apply_fdr(res, p_col="p_value", method="bh")
        else:
            res = apply_fdr(res, p_col="p_value", method="bh")

        # Effect size tiers
        res["tier"] = "NS"
        res.loc[res["significant"] & (np.abs(res["alpha"]) > 0.20), "tier"] = "HIGH"
        res.loc[
            res["significant"]
            & (np.abs(res["alpha"]) > 0.15)
            & (np.abs(res["alpha"]) <= 0.20),
            "tier",
        ] = "MEDIUM"
        res.loc[
            res["significant"]
            & (np.abs(res["alpha"]) > 0.10)
            & (np.abs(res["alpha"]) <= 0.15),
            "tier",
        ] = "LOW"

        res = res.sort_values("p_value")
        return res

    def _get_gene_index(self, gene: Union[str, int]) -> int:
        if isinstance(gene, int):
            return gene
        try:
            return self._genes.index(gene)
        except ValueError:
            raise ValueError(f"Gene {gene} not found.")

    def _empty_results(self, other_genes: List[str]) -> pd.DataFrame:
        return pd.DataFrame({
            "gene": other_genes,
            "alpha": np.nan,
            "se": np.nan,
            "z_score": np.nan,
            "p_value": np.nan,
            "p_adjusted": np.nan,
            "significant": False,
            "ci_lower": np.nan,
            "ci_upper": np.nan,
            "tier": "NS",
        })

    def estimate_target_binary(
        self,
        treatment: np.ndarray,
        target_gene: Union[str, int],
    ) -> pd.DataFrame:
        """
        Estimate residual association scores using a binary treatment indicator
        (e.g. CRISPR perturbation label).

        Uses control-only confounder estimation (fit_confounders must
        have been called with control_mask).  Tests whether residuals
        differ between treated and control cells.

        Parameters
        ----------
        treatment : np.ndarray, shape (N,)
            Binary indicator (0 = control, 1 = treated).
        target_gene : str or int
            Name or index of the perturbed gene (used only for
            exclusion from the result table).

        Returns
        -------
        pd.DataFrame
        """
        if self._residuals is None:
            raise RuntimeError("Call fit_confounders() first.")

        tidx = self._get_gene_index(target_gene)
        other_idx = [i for i in range(len(self._genes)) if i != tidx]
        other_genes = [self._genes[i] for i in other_idx]

        treat = np.asarray(treatment, dtype=bool)
        n1 = treat.sum()
        n0 = (~treat).sum()
        if n1 == 0 or n0 == 0:
            warnings.warn("Treatment vector has no variation.")
            return self._empty_results(other_genes)

        Y = self._residuals[other_idx, :]  # (G-1) x N

        # Group means and variances
        mean1 = Y[:, treat].mean(axis=1)
        mean0 = Y[:, ~treat].mean(axis=1)
        var1 = Y[:, treat].var(axis=1, ddof=1)
        var0 = Y[:, ~treat].var(axis=1, ddof=1)

        alphas = mean1 - mean0
        ses = np.sqrt(var1 / n1 + var0 / n0 + 1e-15)
        z_scores = alphas / ses
        p_values = 2 * stats.norm.sf(np.abs(z_scores))
        ci_lower = alphas - 1.96 * ses
        ci_upper = alphas + 1.96 * ses

        res = pd.DataFrame({
            "gene": other_genes,
            "alpha": alphas,
            "se": ses,
            "z_score": z_scores,
            "p_value": p_values,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
        })

        from pgaa.core.multiple_testing import apply_fdr
        res = apply_fdr(res, p_col="p_value", method="bh")

        res["tier"] = "NS"
        res.loc[res["significant"] & (np.abs(res["alpha"]) > 0.20), "tier"] = "HIGH"
        res.loc[
            res["significant"]
            & (np.abs(res["alpha"]) > 0.15)
            & (np.abs(res["alpha"]) <= 0.20),
            "tier",
        ] = "MEDIUM"
        res.loc[
            res["significant"]
            & (np.abs(res["alpha"]) > 0.10)
            & (np.abs(res["alpha"]) <= 0.15),
            "tier",
        ] = "LOW"

        res = res.sort_values("p_value")
        return res

    # ------------------------------------------------------------------ #
    # Permutation calibration (optional, for small N calibration checks)
    # ------------------------------------------------------------------ #

    def permutation_test(
        self,
        target_gene: Union[str, int],
        n_perms: int = 5000,
        use_spearman: bool = True,
        n_jobs: int = 1,
    ) -> pd.DataFrame:
        """
        Permutation test. Default uses Spearman on residuals
        (robust to in-sample PCA bias). Can use Pearson alpha if needed.
        """
        from joblib import Parallel, delayed

        tidx = self._get_gene_index(target_gene)
        other_idx = [i for i in range(len(self._genes)) if i != tidx]
        Gm1 = len(other_idx)
        N = self._expr.shape[1]

        def _statistic(resid_mat, use_spearman):
            D = resid_mat[tidx, :]
            Y = resid_mat[other_idx, :]
            if use_spearman:
                from scipy.stats import spearmanr
                return np.array([
                    spearmanr(D, Y[g, :])[0] for g in range(Gm1)
                ])
            else:
                Dc = D - np.mean(D)
                Yc = Y - np.mean(Y, axis=1, keepdims=True)
                return (Yc @ Dc) / np.sum(Dc ** 2)

        obs_stat = _statistic(self._residuals, use_spearman)

        def _one_perm(seed):
            rng = np.random.default_rng(seed)
            expr_perm = self._expr.copy()
            expr_perm[tidx, :] = rng.permutation(expr_perm[tidx, :])
            resids = self._cross_fitted_stage1(expr_perm.T, linear=self.use_linear_stage1)
            return _statistic(resids, use_spearman)

        seeds = self.random_state + np.arange(n_perms)
        null_stats = np.array(
            Parallel(n_jobs=n_jobs)(
                delayed(_one_perm)(s) for s in seeds
            )
        )  # n_perms x Gm1

        obs_abs = np.abs(obs_stat)
        null_abs = np.abs(null_stats.T)
        p_perm = (np.sum(null_abs >= obs_abs[:, None], axis=1) + 1) / (n_perms + 1)

        res = pd.DataFrame({
            "gene": [self._genes[i] for i in other_idx],
            "observed": obs_stat,
            "p_value_perm": p_perm,
        })
        from pgaa.core.multiple_testing import apply_fdr
        res = apply_fdr(res, p_col="p_value_perm", method="bh")
        return res.sort_values("p_value_perm")

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def confounders(self) -> Optional[np.ndarray]:
        return self._confounders

    @property
    def residuals(self) -> Optional[np.ndarray]:
        return self._residuals

    @property
    def genes(self) -> List[str]:
        return self._genes

    @property
    def n_cells(self) -> int:
        return self._expr.shape[1] if self._expr is not None else 0

    @property
    def n_genes(self) -> int:
        return self._expr.shape[0] if self._expr is not None else 0
