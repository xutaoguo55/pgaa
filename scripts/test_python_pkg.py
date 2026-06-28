#!/usr/bin/env python3
"""Comprehensive test of PGAA Python package."""
import numpy as np; np.random.seed(42)
import sys; sys.path.insert(0, '.')
from pgaa.core.prt import wasserstein_1d, prt_s1_test
from pgaa.core.prt_s2 import compute_persistence_1d, persistence_landscape_distance, s2_test
from sklearn.cluster import KMeans

errors = []

# T1: wasserstein_1d basic
x = np.random.normal(0, 1, 500); y = np.random.normal(0.8, 1, 500)
w = wasserstein_1d(x, y)
assert w > 0.5, f'T1 expected W>0.5, got {w:.3f}'
print(f'✅ T1 wasserstein: W={w:.4f}')

# T2: same distribution
x2 = np.random.normal(2, 0.5, 1000); y2 = np.random.normal(2, 0.5, 1000)
w2 = wasserstein_1d(x2, y2)
assert w2 < 0.2, f'T2 expected W<0.2, got {w2:.3f}'
print(f'✅ T2 same dist: W={w2:.4f}')

# T3: shifted
y3 = np.random.normal(4, 0.5, 1000)
w3 = wasserstein_1d(x2, y3)
assert w3 > 1.5, f'T3 expected W>1.5, got {w3:.3f}'
print(f'✅ T3 shifted: W={w3:.4f}')

# T4: persistence single peak
h = np.array([0.1, 0.5, 1.0, 0.5, 0.1]); bc = np.arange(1, 6, dtype=float)
pd = compute_persistence_1d(h, bc)
assert pd.shape[0] == 1, f'T4 expected 1 peak, got {pd.shape[0]}'
print(f'✅ T4 single peak: 1 peak, pers={pd[0,2]:.4f}')

# T5: flat histogram
h_flat = np.ones(10)
pd_flat = compute_persistence_1d(h_flat, np.arange(10, dtype=float))
assert pd_flat[0, 2] == 0, f'T5 expected pers=0, got {pd_flat[0,2]:.3f}'
print(f'✅ T5 flat: pers=0')

# T6: bimodal
h2 = np.array([0.1, 0.8, 0.3, 0.8, 0.1])
pd1 = compute_persistence_1d(h, bc); pd2 = compute_persistence_1d(h2, bc)
d = persistence_landscape_distance(pd1, pd2)
assert d > 0.2, f'T6 expected dist>0.2, got {d:.3f}'
print(f'✅ T6 bimodality: dist={d:.4f}')

# T7: prt_s1_test full pipeline
X = np.random.normal(0, 1, (500, 30))
genes = [f'gene_{i:04d}' for i in range(30)]
ct = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(X)
X[0:100, 2] += 2.0  # strong effect on gene_0002
res_s1 = prt_s1_test(X, genes, 'gene_0001',
                      np.arange(100), np.arange(100, 400),
                      n_perms=200, cell_type=ct,
                      library_size=np.ones(500)*10000)
p_g2 = float(res_s1[res_s1.gene == 'gene_0002']['p_value_perm'].iloc[0])
assert p_g2 < 0.1, f'T7 expected gene_0002 sig, got p={p_g2:.4f}'
assert len(res_s1) == 29, f'T7 expected 29 genes, got {len(res_s1)}'
print(f'✅ T7 prt_s1_test: {len(res_s1)} genes, gene_0002 p={p_g2:.4f}')

# T8: s2_test with bimodal signal
X_bimodal = np.random.normal(0, 1, (400, 20))
genes20 = [f'gene_{i:04d}' for i in range(20)]
X_bimodal[0:50, 3] += 2.0   # half high
X_bimodal[50:80, 3] -= 2.0  # half low
res_s2 = s2_test(X_bimodal, genes20, 'gene_0001',
                 np.arange(80), np.arange(80, 300),
                 n_bins=20)
assert len(res_s2) == 19, f'T8 expected 19 genes, got {len(res_s2)}'
s2_g3 = float(res_s2[res_s2.gene == 'gene_0003']['S2'].iloc[0])
assert s2_g3 > 0, f'T8 expected PGAA-H/S2>0 for gene_0003'
print(f'✅ T8 PGAA-H test: {len(res_s2)} genes, gene_0003 S2={s2_g3:.4f}')

# T9: prt_s1_test random_state consistency
np.random.seed(123)
r1 = prt_s1_test(X, genes, 'gene_0001', np.arange(100), np.arange(100, 400), n_perms=100)
np.random.seed(123)
r2 = prt_s1_test(X, genes, 'gene_0001', np.arange(100), np.arange(100, 400), n_perms=100)
assert np.allclose(r1['W_observed'].values, r2['W_observed'].values), 'T9 W_observed not reproducible'
print(f'✅ T9 reproducibility: W_observed match')

# T10: wasserstein_1d with extreme values
x_nan = np.array([1.0, 2.0, np.nan])
try:
    wasserstein_1d(x_nan, x_nan)
    errors.append('T10 should fail on NaN')
    print('❌ T10 NaN handling: did not raise')
except Exception:
    print('✅ T10 NaN handling: raises (as expected from np.quantile)')

print(f'\n{"="*50}')
if errors:
    print(f'❌ {len(errors)} tests FAILED:')
    for e in errors: print(f'  {e}')
else:
    print('✅ All 9 core tests PASSED')
print(f'{"="*50}')
