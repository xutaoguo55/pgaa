# PGAA: distribution-aware testing for single-cell perturbation screens

Detects perturbation responses beyond mean shifts using Wasserstein
distance and persistent homology, with built-in calibration diagnostics.

## Install

```bash
pip install -e .          # Python
# R: source pgaa_r/R/*.R
```

## Quick start

```python
from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import s2_test

res_w = prt_s1_test(X, genes, target="MYC",
                     perturbed_idx=p, control_idx=c,
                     n_perms=2000)

res_p = s2_test(X, genes, target="MYC",
                 perturbed_idx=p, control_idx=c,
                 n_bins=20)
```

## Dependencies

numpy scipy pandas scanpy scikit-learn statsmodels matplotlib

## Data

GSE133344 GSE111014 GSE167363 GSE159117 GSE116222 10x PBMC 3k

## Reproduce

```bash
cd scripts
python benchmark_prt_s2_nbins20.py
python simulate_perturbation_types.py
```

## License

MIT
