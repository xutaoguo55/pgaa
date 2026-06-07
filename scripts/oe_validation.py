#!/usr/bin/env python3
"""
OE 论文方法在现代大样本数据上的 robustness 评估。

OE 论文 v7 关键声明：
1. 67% (10/15) CLL marker gene 命中
2. TCL1A 调控 BCR markers (CD24 α=0.153, MS4A1 α=-0.063)
3. LYN 调控 BCR adaptors (BLNK α=0.030, LAT α=-0.066)
4. HK 基因 FDR < 5%
5. 与 scTenifoldKnk 正交

我们用 OE 论文的相同方法（PCA residualization + Spearman/Fisher-z）在：
- CLL 36k cells（论文中使用的同一数据集）
- Norman 2019 真实 Perturb-seq 13k cells
重新评估这些声明是否在大样本下仍然成立。
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.io import mmread
from scipy.stats import spearmanr, t as tdist
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.tools.realdata import virtual_oe_reald

np.random.seed(42)

CLL_MARKERS = ["CD19", "CD22", "CD24", "CD5", "MS4A1", "CD79A", "CD79B", "BANK1",
               "LYN", "BLNK", "SYK", "BTK", "PLCG2", "PIK3CD", "TCL1A"]
HK_GENES = ["ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
            "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]
BCR_MARKERS = ["CD79A", "CD79B", "BANK1", "LYN", "BLNK", "SYK", "BTK",
               "PLCG2", "PIK3CD", "MS4A1", "CD19", "CD22"]


def load_cll(n_cells_max=None):
    print("Loading CLL data ...")
    counts = sparse.csr_matrix(mmread("/Users/guoxutao/.openclaw/workspace/cll_counts.mtx").T)
    genes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_genes.txt", header=None)[0].values
    barcodes = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_barcodes.txt", header=None)[0].values
    meta = pd.read_csv("/Users/guoxutao/.openclaw/workspace/cll_meta.csv", index_col=0)
    adata = sc.AnnData(X=counts, obs=meta, var=pd.DataFrame(index=genes))
    adata.obs_names = barcodes
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=50)
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
    adata = adata[adata.obs.pct_counts_mt < 20].copy()
    adata = adata[adata.obs.n_genes_by_counts.between(200, 6000)].copy()
    if n_cells_max and adata.n_obs > n_cells_max:
        sc.pp.subsample(adata, n_obs=n_cells_max, random_state=42)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
    return adata


def oe_method(adata, target, hk_genes, n_pcs=10):
    """OE-style: Y~D + cell covariates + Storey-BH."""
    return virtual_oe_reald(adata, target, hk_genes=hk_genes, n_pcs=n_pcs, random_state=42)


def evaluate_oe(adata, target, label, hk_genes=HK_GENES, top_n=200):
    if target not in adata.var_names:
        return None
    res = oe_method(adata, target, hk_genes=hk_genes)
    n_sig = int(res["significant"].sum())
    hits = res.head(top_n)["gene"].tolist()

    # OE's claim 1: marker gene recovery
    n_marker_in_top = len([g for g in CLL_MARKERS if g in hits])
    n_bcr_in_top = len([g for g in BCR_MARKERS if g in hits])
    n_hk_in_top = len([g for g in hk_genes if g in hits])

    # TCL1A specific: BCR markers (CD24, MS4A1) per OE paper
    tcl1a_specific = {}
    for g in ["CD24", "MS4A1", "CD79A", "CD79B", "BANK1", "BLNK", "SYK", "BTK", "LYN"]:
        if g in res["gene"].values:
            row = res[res["gene"] == g].iloc[0]
            tcl1a_specific[g] = {"alpha": row["alpha"], "p_value": row["p_value"],
                                  "significant": row["significant"]}

    return {
        "target": target, "label": label, "sig": n_sig,
        "marker_in_top": n_marker_in_top, "bcr_in_top": n_bcr_in_top,
        "hk_in_top": n_hk_in_top, "specific": tcl1a_specific,
    }


def main():
    print("="*60)
    print("OE 论文方法在大样本 CLL + Norman 2019 上的 robustness")
    print("="*60)

    # Part 1: CLL 36k cells
    print("\n## Part 1: CLL scRNA-seq (downsample to 5k for speed)")
    adata_5k = load_cll(n_cells_max=5000)
    print(f"Using {adata_5k.n_obs} cells × {adata_5k.n_vars} genes")

    rows = []
    for target, label in [("TCL1A", "POS-OE-paper"), ("LYN", "POS-OE-paper"),
                          ("GAPDH", "NEG-HK"), ("ACTB", "NEG-HK")]:
        result = evaluate_oe(adata_5k, target, label)
        if result:
            rows.append(result)
            print(f"\n{target} ({label}):")
            print(f"  sig={result['sig']}, BCR-in-top200={result['bcr_in_top']}, "
                  f"marker-in-top200={result['marker_in_top']}, HK-in-top200={result['hk_in_top']}")
            if result["specific"]:
                for g, info in result["specific"].items():
                    print(f"    {g}: alpha={info['alpha']:.3f}, sig={info['significant']}")

    # Part 2: Bigger sample for TCL1A to see if OE's specific alpha values hold
    print("\n## Part 2: Sample size sensitivity (TCL1A)")
    for n in [2000, 5000, 10000, 20000, 36568]:
        try:
            adata = load_cll(n_cells_max=n)
            t0 = time.time()
            res = oe_method(adata, "TCL1A", hk_genes=HK_GENES)
            elapsed = time.time() - t0
            n_sig = int(res["significant"].sum())
            # Check specific genes OE paper claims
            cd24 = res[res["gene"] == "CD24"].iloc[0] if "CD24" in res["gene"].values else None
            ms4a1 = res[res["gene"] == "MS4A1"].iloc[0] if "MS4A1" in res["gene"].values else None
            cd24_a = cd24["alpha"] if cd24 is not None else None
            ms4a1_a = ms4a1["alpha"] if ms4a1 is not None else None
            print(f"  N={n:5d}: sig={n_sig:4d}, CD24_alpha={cd24_a}, MS4A1_alpha={ms4a1_a}, time={elapsed:.1f}s")
        except Exception as e:
            print(f"  N={n}: ERROR {e}")

    # Part 3: Norman 2019 13k
    print("\n## Part 3: Norman 2019 Perturb-seq (CEBPE as positive control)")
    adata_n = sc.read_h5ad("/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_with_symbols.h5ad")
    import pickle
    with open("/Users/guoxutao/.openclaw/workspace/norman2019/ensembl2symbol.pkl", "rb") as f:
        mapping = pickle.load(f)
    keep = [i for i, e in enumerate(adata_n.var_names) if mapping.get(e, e) != e]
    adata_n = adata_n[:, keep].copy()
    adata_n.var_names = [mapping[e] for e in adata_n.var_names]
    adata_n.var_names_make_unique()
    sc.pp.normalize_total(adata_n, target_sum=1e4)
    sc.pp.log1p(adata_n)
    sc.pp.highly_variable_genes(adata_n, n_top_genes=2000, subset=False)
    print(f"Norman: {adata_n.n_obs} cells × {adata_n.n_vars} genes")

    cebpe_pert = adata_n.obs["perturbation"].str.contains(r"^CEBPE_NegCtrl\d+__", regex=True)
    ctrl_mask = adata_n.obs["perturbation"].str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ad_n_sub = adata_n[cebpe_pert | ctrl_mask].copy()
    print(f"CEBPE: {cebpe_pert.sum()} perturbed + {ctrl_mask.sum()} control")

    if "CEBPE" in ad_n_sub.var_names:
        res_cebpe = oe_method(ad_n_sub, "CEBPE", hk_genes=HK_GENES)
        cebpe_targets = ["ELANE", "CTSG", "LYZ", "MPO", "GFI1"]
        top200 = res_cebpe.head(200)["gene"].tolist()
        known_hit = [g for g in cebpe_targets if g in top200]
        print(f"  CEBPE sig: {int(res_cebpe['significant'].sum())}, "
              f"known targets in top200: {len(known_hit)}/{len(cebpe_targets)} ({known_hit})")
        if "ELANE" in res_cebpe["gene"].values:
            elane = res_cebpe[res_cebpe["gene"] == "ELANE"].iloc[0]
            print(f"  ELANE alpha: {elane['alpha']}, p={elane['p_value']:.3f}, sig={elane['significant']}")

    print("\n" + "="*60)
    print("OE 论文 v7 真实数据 robustness 总结")
    print("="*60)
    print("1. 67% CLL marker 命中: 在 5k cells 下检验")
    print("2. TCL1A 调控 BCR (CD24, MS4A1): 在 2k-36k cells 范围内跟踪")
    print("3. HK 阴性对照 FDR<5%: GAPDH/ACTB sig 数")
    print("4. Norman 真实 Perturb-seq 表现: CEBPE 命中 ELANE/LYZ/MPO?")


if __name__ == "__main__":
    main()
