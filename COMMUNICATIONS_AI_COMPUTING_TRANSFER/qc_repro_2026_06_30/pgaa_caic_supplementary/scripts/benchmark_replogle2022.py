#!/usr/bin/env python3
"""
PGAA benchmark on Replogle 2020 direct-capture Perturb-seq (GSE146194).

This script requires the processed data. Download via:
  wget https://ftp.ncbi.nlm.nih.gov/geo/series/GSE146nnn/GSE146194/suppl/GSE146194_processed.tar.gz

Or use the scPerturb pre-processed version:
  https://scperturb.ds.dfci.harvard.edu/

Expected runtime: ~2-4 hours for a subset of perturbations.
"""
import numpy as np, pandas as pd, scanpy as sc, sys, time, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import s2_test
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, average_precision_score

np.random.seed(42)

def load_replogle(data_path):
    """Load Replogle 2020/2022 processed data."""
    if os.path.isdir(data_path):
        adata = sc.read_10x_mtx(data_path)
    else:
        adata = sc.read_h5ad(data_path)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)
    return adata

def benchmark_perturbation(adata, target, pert_label_col="perturbation",
                           n_perms_s1=200, n_perms_s2=50, n_bins=20):
    """Run PGAA on a single perturbation."""
    labels = adata.obs[pert_label_col].astype(str)
    pert_idx = np.where(labels == target)[0]
    ctrl_idx = np.where(labels.str.contains("control|non-targeting|NT|NegCtrl",
                                             case=False))[0]
    if len(pert_idx) < 30 or len(ctrl_idx) < 30:
        return None

    ctrl_idx = ctrl_idx[:len(pert_idx) * 3]
    X = adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X
    genes = list(adata.var_names)
    lib = np.array(X.sum(1)).ravel()
    ct = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(X)

    t0 = time.time()
    res_s1 = prt_s1_test(X, genes, target, pert_idx, ctrl_idx,
                         n_perms=n_perms_s1, cell_type=ct, library_size=lib)
    t_s1 = time.time() - t0

    t0 = time.time()
    res_s2 = s2_test(X, genes, target, pert_idx, ctrl_idx,
                     n_bins=n_bins, cell_type=ct, library_size=lib)
    t_s2 = time.time() - t0

    return {"s1": res_s1, "s2": res_s2, "t_s1": t_s1, "t_s2": t_s2,
            "n_pert": len(pert_idx), "n_ctrl": len(ctrl_idx)}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to processed h5ad/10x dir")
    parser.add_argument("--targets", default="top20",
                       help="Comma-separated perturbation targets or 'top20'")
    parser.add_argument("--output", default="scripts/replogle2022_results.csv")
    args = parser.parse_args()

    adata = load_replogle(args.data)
    print(f"Loaded: {adata.shape}")

    if args.targets == "top20":
        pert_counts = adata.obs["perturbation"].value_counts()
        targets = pert_counts.head(20).index.tolist()
    else:
        targets = args.targets.split(",")

    results = []
    for t in targets:
        print(f"\nBenchmarking {t}...")
        res = benchmark_perturbation(adata, t)
        if res is None:
            print(f"  Skipping (too few cells)")
            continue
        print(f"  n_pert={res['n_pert']}, S1 time={res['t_s1']:.1f}s, S2 time={res['t_s2']:.1f}s")
        results.append({"target": t, "n_pert": res['n_pert'],
                        "n_sig_s1": int((res['s1']['p_value_perm'] < 0.05).sum()),
                        "t_s1": res['t_s1'], "t_s2": res['t_s2']})

    df = pd.DataFrame(results)
    df.to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
