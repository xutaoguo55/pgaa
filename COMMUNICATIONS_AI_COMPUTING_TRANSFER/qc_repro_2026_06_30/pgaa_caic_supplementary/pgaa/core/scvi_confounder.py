"""scVI-based nonlinear confounder extraction for PGAA."""

from typing import List, Optional, Tuple

import numpy as np
from scipy import sparse


class SCVIConfounder:
    """
    Train scVI on count data to obtain a nonlinear latent representation
    of cell state, then provide cross-fitted residualization.
    """

    def __init__(
        self,
        n_latent: int = 10,
        n_layers: int = 2,
        n_hidden: int = 128,
        max_epochs: int = 100,
        batch_size: int = 256,
        random_state: int = 42,
    ):
        self.n_latent = n_latent
        self.n_layers = n_layers
        self.n_hidden = n_hidden
        self.max_epochs = max_epochs
        self.batch_size = batch_size
        self.random_state = random_state

        self._model = None
        self._latent = None  # N x n_latent
        self._is_trained = False

    def fit(
        self,
        counts: np.ndarray,  # G x N, raw counts (int)
        genes: List[str],
        batch_labels: Optional[np.ndarray] = None,
        exclude_idx: Optional[int] = None,
    ) -> "SCVIConfounder":
        """
        Fit scVI on raw counts.

        Parameters
        ----------
        counts : np.ndarray, shape (G, N)
            Raw count matrix (genes as rows, cells as columns).
        genes : list of str
            Gene names.
        batch_labels : np.ndarray, optional
            Batch labels for each cell. If provided, scVI performs
            batch correction automatically.
        exclude_idx : int, optional
            Index of target gene to exclude from training, preventing
            perturbation signal from entering the latent space.
        """
        try:
            import anndata
            import scvi
        except ImportError as exc:
            raise ImportError(
                "scvi-tools and anndata are required for use_scvi=True. "
                "Install: pip install scvi-tools anndata"
            ) from exc

        if sparse.issparse(counts):
            counts = counts.toarray()
        counts = np.asarray(counts, dtype=np.float32)
        G, N = counts.shape

        # Exclude target gene if requested
        if exclude_idx is not None:
            mask = np.ones(G, dtype=bool)
            mask[exclude_idx] = False
            counts_train = counts[mask, :]
            genes_train = [g for i, g in enumerate(genes) if i != exclude_idx]
        else:
            counts_train = counts
            genes_train = genes

        # Build AnnData
        adata = anndata.AnnData(
            X=sparse.csr_matrix(counts_train.T, dtype=np.float32),
            var=pd.DataFrame(index=genes_train),
        )
        if batch_labels is not None:
            adata.obs["batch"] = pd.Categorical(batch_labels)
            scvi.model.SCVI.setup_anndata(adata, batch_key="batch")
        else:
            scvi.model.SCVI.setup_anndata(adata)

        scvi.settings.seed = self.random_state
        self._model = scvi.model.SCVI(
            adata,
            n_layers=self.n_layers,
            n_latent=self.n_latent,
            n_hidden=self.n_hidden,
        )
        self._model.train(
            max_epochs=self.max_epochs,
            batch_size=self.batch_size,
            enable_progress_bar=False,
            plan_kwargs={"lr": 1e-3},
        )

        # Latent representation for ALL cells
        self._latent = self._model.get_latent_representation()  # N x n_latent
        self._is_trained = True
        return self

    @property
    def latent(self) -> Optional[np.ndarray]:
        return self._latent

    def get_corrected_expression(
        self,
        genes: List[str],
        library_size: float = 1e4,
    ) -> np.ndarray:
        """
        Return scVI-denoised, batch-corrected expression matrix.

        This uses scVI as a preprocessing layer: dropout and library-size
        effects are removed, but biological variation is preserved.
        The returned matrix is log1p(normalized).

        Parameters
        ----------
        genes : list of str
            Full gene list (must match the gene list used during training).
        library_size : float
            Target library size for normalization.

        Returns
        -------
        expr_corrected : np.ndarray, shape (G, N)
            Genes as rows, cells as columns.  log1p(normalized).
        """
        if self._model is None:
            raise RuntimeError("Call fit() first.")

        import anndata
        import scvi

        G = len(genes)
        N = self._latent.shape[0]
        dummy = anndata.AnnData(
            X=np.zeros((N, G), dtype=np.float32),
            var=pd.DataFrame(index=genes),
        )
        scvi.model.SCVI.setup_anndata(dummy)

        norm_expr = self._model.get_normalized_expression(
            adata=dummy,
            library_size=library_size,
        )
        if hasattr(norm_expr, "values"):
            norm_expr = norm_expr.values
        norm_expr = np.asarray(norm_expr, dtype=np.float64)
        expr_corrected = np.log1p(norm_expr)
        return expr_corrected.T  # G x N

    def get_residuals(
        self,
        X_cell: np.ndarray,
        linear: bool = True,
        n_folds: int = 5,
        random_state: int = 42,
    ) -> np.ndarray:
        """Deprecated: latent-space OLS overfits. Use preprocessed expr."""
        raise RuntimeError(
            "get_residuals() is disabled for scVI because latent-space "
            "OLS collapses residual variance."
        )


import pandas as pd
