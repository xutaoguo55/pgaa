#!/usr/bin/env python3
"""
PGAA v2: cell-type-aware Perturb-seq analysis.

Fixes the v1 failure on Norman 2019 by adding cell type as covariate.
Uses k-means clustering to assign cell types (since Norman 2019 doesn't
provide fine-grained cell type labels for all 87k cells).
"""

import time
import pickle
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.stats import mannwhitneyu
import statsmodels.stats.multitest as mt
from sklearn.cluster import KMeans

np.random.seed(42)

HK_GENES = ["ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
            "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]

KLF1_TARGETS = ["HBB", "HBA1", "HBA2", "AHSP", "ALAS2", "GYPA", "GYPB",
                "HEMGN", "TFR2", "SLC25A37", "FECH", "HMBS", "UROS", "BLVRB",
                "TFRC", "SLC25A39"]


def virtual_oe_v2(
    X: np.ndarray,            # cells x genes (log-normalized)
    genes: list,
    target: str,
    treatment: np.ndarray,    # binary
    cell_type: np.ndarray,    # categorical
    library_size: np.ndarray,
    hk_genes: list = None,
):
    """
    Y_g ~ D + cell_type_dummies + library_size
    for each gene g != target.
    """
    N, G = X.shape
    tidx = genes.index(target)
    D = treatment.astype(np.float64)
    D_c = D - D.mean()

    # Standardize library size
    lib_z = (library_size - library_size.mean()) / (library_size.std() + 1e-9)

    # One-hot cell type
    ct = pd.Categorical(cell_type)
    ct_dummies = pd.get_dummies(ct, drop_first=True, dtype=float).values
    n_ct = ct_dummies.shape[1]

    # Build design matrix: [intercept, cell_type_dummies, lib_z, D]
    Zd = np.column_stack([np.ones(N), ct_dummies, lib_z, D_c])
    p = Zd.shape[1]

    # Center Y
    Yc = X - X.mean(axis=0, keepdims=True)
    other_idx = [i for i in range(G) if i != tidx]
    Yc_other = Yc[:, other_idx]

    # Vectorized OLS
    ZtZ_inv = np.linalg.pinv(Zd.T @ Zd)
    beta = ZtZ_inv @ (Zd.T @ Yc_other)  # p x (G-1)
    alpha = beta[-1, :]
    resid = Yc_other - Zd @ beta
    dof = N - p
    sigma2 = (resid ** 2).sum(axis=0) / dof
    se_alpha = np.sqrt(np.diag(ZtZ_inv)[-1] * sigma2)
    t_stat = alpha / (se_alpha + 1e-15)
    from scipy.stats import t as tdist
    p_value = 2 * tdist.sf(np.abs(t_stat), dof)

    res = pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "alpha": alpha,
        "se": se_alpha,
        "t_stat": t_stat,
        "p_value": p_value,
    })

    # HK-calibrated Storey BH
    if hk_genes:
        hk_mask = res["gene"].isin(hk_genes)
        if hk_mask.sum() >= 3:
            pi0 = min(1.0, np.median(res.loc[hk_mask, "p_value"].values) * 2)
        else:
            pi0 = 1.0
    else:
        pi0 = 1.0
    m = len(res)
    res = res.sort_values("p_value").reset_index(drop=True)
    res["rank"] = np.arange(1, m + 1)
    res["p_adjusted"] = np.minimum.accumulate(
        (res["p_value"] * m * pi0 / res["rank"]).values[::-1]
    )[::-1]
    res["p_adjusted"] = res["p_adjusted"].clip(upper=1.0)
    res["significant"] = (res["p_adjusted"] < 0.05) & (np.abs(res["alpha"]) > 0.10)

    # Tiers
    a = np.abs(res["alpha"])
    res["tier"] = "NS"
    res.loc[res["significant"] & (a > 0.20), "tier"] = "HIGH"
    res.loc[res["significant"] & (a > 0.15) & (a <= 0.20), "tier"] = "MEDIUM"
    res.loc[res["significant"] & (a > 0.10) & (a <= 0.15), "tier"] = "LOW"
    return res.sort_values("p_value")


def load_norman_with_celltypes():
    print("Loading Norman 2019 with cell type annotation ...")
    adata = sc.read_h5ad("/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_with_symbols.h5ad")
    with open("/Users/guoxutao/.openclaw/workspace/norman2019/ensembl2symbol.pkl", "rb") as f:
        mapping = pickle.load(f)
    keep = [i for i, e in enumerate(adata.var_names) if mapping.get(e, e) != e and mapping.get(e, e) != ""]
    adata = adata[:, keep].copy()
    adata.var_names = [mapping[e] for e in adata.var_names]
    adata.var_names_make_unique()
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)

    # K-means clustering for cell type
    X_hvg = adata.X[:, adata.var["highly_variable"].values]
    if sparse.issparse(X_hvg):
        X_hvg = X_hvg.toarray()
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X_hvg)
    print("K-means clustering for cell types ...")
    km = KMeans(n_clusters=6, random_state=42, n_init=10)
    cell_type = km.fit_predict(X_std)
    adata.obs["cell_type"] = cell_type
    print(f"Cell type distribution: {pd.Series(cell_type).value_counts().to_dict()}")

    # Look for known cell type markers
    markers = {
        "erythroid": ["HBB", "HBA1", "AHSP", "GYPA", "ALAS2"],
        "myeloid": ["CD14", "LYZ", "CSF1R", "MPO", "ELANE"],
        "lymphoid": ["CD3D", "CD3E", "CD19", "MS4A1", "CD79A"],
        "stem": ["CD34", "PROM1", "KIT", "GATA2"],
    }
    for ct_name, mks in markers.items():
        present = [g for g in mks if g in adata.var_names]
        if present:
            X_mk = adata.X[:, [list(adata.var_names).index(g) for g in present]]
            if sparse.issparse(X_mk):
                X_mk = X_mk.toarray()
            mean_per_cluster = pd.DataFrame(X_mk, columns=present).groupby(cell_type).mean()
            top_cluster = mean_per_cluster.sum(axis=1).idxmax()
            print(f"  Cluster {top_cluster} has highest {ct_name} markers")

    return adata


def main():
    adata = load_norman_with_celltypes()
    X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
    genes = list(adata.var_names)
    cell_type = adata.obs["cell_type"].values
    lib_size = adata.obs["n_counts"].values.astype(np.float64)

    labels = adata.obs["perturbation"].astype(str)
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0]

    print("\n" + "="*60)
    print("PGAA v2: KLF1 vs Control")
    print("="*60)

    # Build KLF1 test set
    klf1_pert = labels.str.contains(r"^KLF1_NegCtrl\d+__", regex=True)
    klf1_idx = np.where(klf1_pert)[0]
    test_idx = np.concatenate([klf1_idx, ctrl_idx[:len(klf1_idx) * 3]])  # balanced
    print(f"KLF1 perturbed: {len(klf1_idx)}, Control: {min(len(ctrl_idx), len(klf1_idx)*3)}")

    X_sub = X[test_idx]
    cell_type_sub = cell_type[test_idx]
    lib_sub = lib_size[test_idx]
    treatment_sub = np.zeros(len(test_idx), dtype=int)
    treatment_sub[:len(klf1_idx)] = 1

    t0 = time.time()
    res_klf1 = virtual_oe_v2(
        X_sub, genes, "KLF1", treatment_sub, cell_type_sub, lib_sub,
        hk_genes=HK_GENES,
    )
    elapsed = time.time() - t0
    n_sig = int(res_klf1["significant"].sum())
    print(f"  sig (FDR<0.05, |alpha|>0.10): {n_sig}, time={elapsed:.2f}s")
    print("Top 20:")
    print(res_klf1.head(20)[["gene", "alpha", "p_value", "p_adjusted", "tier"]].to_string(index=False))

    # Check KLF1 known targets
    known = [g for g in KLF1_TARGETS if g in res_klf1["gene"].values]
    known_pvals = res_klf1[res_klf1["gene"].isin(known)].sort_values("p_value")
    print(f"\nKLF1 known targets ({len(known)}):")
    print(known_pvals[["gene", "alpha", "p_value", "p_adjusted"]].to_string(index=False))

    sig_known = res_klf1[(res_klf1["gene"].isin(known)) & (res_klf1["significant"])]
    print(f"\nKnown targets in significant set: {len(sig_known)} / {len(known)}")
    if len(sig_known) > 0:
        print(sig_known[["gene", "alpha", "p_value", "p_adjusted"]].to_string(index=False))

    # Negative control: GAPDH (in KLF1 cells, GAPDH is not perturbed)
    print("\n" + "="*60)
    print("Negative control: GAPDH (not actually perturbed)")
    print("="*60)
    res_gapdh = virtual_oe_v2(
        X_sub, genes, "GAPDH", treatment_sub, cell_type_sub, lib_sub,
        hk_genes=HK_GENES,
    )
    n_sig_g = int(res_gapdh["significant"].sum())
    print(f"  sig (FDR<0.05, |alpha|>0.10): {n_sig_g}")
    print("Top 10:")
    print(res_gapdh.head(10)[["gene", "alpha", "p_value", "p_adjusted"]].to_string(index=False))

    # Summary table
    print("\n" + "="*60)
    print("PGAA v2 Summary on Norman 2019 (KLF1 perturbation)")
    print("="*60)
    summary = pd.DataFrame({
        "Target": ["KLF1 (true positive)", "GAPDH (false positive)"],
        "Significant": [n_sig, n_sig_g],
        "Top_hit": [res_klf1.iloc[0]["gene"], res_gapdh.iloc[0]["gene"]],
    })
    print(summary.to_string(index=False))
    summary.to_csv("scripts/norman2019_v2_summary.csv", index=False)


if __name__ == "__main__":
    main()
