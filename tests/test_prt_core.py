import numpy as np

from pgaa.core.prt import wasserstein_1d, wasserstein_1d_by_column


def test_wasserstein_1d_by_column_matches_scalar_definition():
    rng = np.random.default_rng(42)
    x = rng.normal(size=(25, 4))
    y = rng.normal(loc=0.3, size=(35, 4))

    vectorized = wasserstein_1d_by_column(x, y)
    scalar = np.array([wasserstein_1d(x[:, i], y[:, i]) for i in range(x.shape[1])])

    np.testing.assert_allclose(vectorized, scalar)
