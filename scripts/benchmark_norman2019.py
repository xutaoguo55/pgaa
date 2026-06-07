#!/usr/bin/env python3
"""PGAA validation on real Perturb-seq: Norman 2019."""

import time
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.tools.realdata import virtual_oe_reald

np.random.seed(42)

HK_GENES = ["ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
            "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]


def load():
    adata = sc.read_h5ad("/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_with_symbols.h5ad")
    # Switch index from Ensembl ID to gene symbol (with deduplication)
    import pandas as pd
    symbols = adata.var["gene_symbol"].values
    # If duplicate symbols, keep first
    seen = {}
    keep = []
    for i, s in enumerate(symbols):
        if s not in seen:
            seen[s] = True
            keep.append(i)
    adata = adata[:, keep].copy()
    adata.var_names = adata.var["gene_symbol"].values
    adata.var_names_make_unique()
    # Normalize and log
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)
    print(f"Adata: {adata}")
    print(f"Perturbation top 5:\n{adata.obs['perturbation'].value_counts().head(5)}")
    return adata


def evaluate_target(adata, target, neg_ctrl_pattern="NegCtrl"):
    """Find cells with target perturbation and compare to negative control cells."""
    labels = adata.obs["perturbation"].astype(str)

    # Match "TARGET_NegCtrl*" but not "TARGET_OTHERGENE*"
    # Format: "TARGET_NegCtrl0__TARGET_NegCtrl0"
    # Cells with target as the real gene (paired with NegCtrl only):
    pert_mask = labels.str.contains(rf"^{target}_NegCtrl\d+__", regex=True) | \
                labels.str.contains(rf"__\w*{target}_NegCtrl\d+$", regex=True)
    if not pert_mask.any():
        return None

    ctrl_mask = labels.str.contains(rf"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    n_pert = int(pert_mask.sum())
    n_ctrl = int(ctrl_mask.sum())
    if n_pert < 30 or n_ctrl < 30:
        return None

    print(f"\n{target}: {n_pert} perturbed, {n_ctrl} control")
    ad_sub = adata[ctrl_mask | pert_mask].copy()

    t0 = time.time()
    res = virtual_oe_reald(
        ad_sub, target,
        hk_genes=HK_GENES,
        n_pcs=10,
        random_state=42,
    )
    elapsed = time.time() - t0

    n_sig = int(res["significant"].sum())
    top10 = res.head(10)["gene"].tolist()
    return {
        "target": target, "n_pert": n_pert, "n_ctrl": n_ctrl,
        "n_sig": n_sig, "time": elapsed, "top10": top10,
    }


if __name__ == "__main__":
    adata = load()

    # Single-gene perturbations: parse "Target_NegCtrl0__Target_NegCtrl0" format
    labels = adata.obs["perturbation"].astype(str)
    counts = labels.value_counts()
    # Extract target name: split on "__" then on "_" and remove "NegCtrl"
    single_gene_pert = []
    for name, cnt in counts.items():
        # Name format: "TARGET_NegCtrl0__TARGET_NegCtrl0"
        if "__" not in name:
            continue
        parts = name.split("__")[0]  # first half: "TARGET_NegCtrl0"
        tokens = parts.split("_")
        # Real gene names don't have "NegCtrl" - find the gene token(s)
        gene_tokens = [t for t in tokens if "NegCtrl" not in t]
        if len(gene_tokens) == 1:  # single-gene perturbation
            target = gene_tokens[0]
            if target and cnt >= 30:
                single_gene_pert.append((target, cnt))
    # Dedupe targets (same gene might appear in 2-3 different controls)
    target_seen = {}
    for t, c in single_gene_pert:
        target_seen[t] = target_seen.get(t, 0) + c
    single_gene_sorted = sorted(target_seen.items(), key=lambda x: -x[1])
    targets = [t for t, c in single_gene_sorted[:10]]
    print(f"\nTop single-gene targets: {targets}")
    for t, c in single_gene_sorted[:10]:
        print(f"  {t}: {c} cells")

    rows = []
    for target in targets:
        result = evaluate_target(adata, target)
        if result:
            rows.append(result)
            print(f"  sig={result['n_sig']}, time={result['time']:.1f}s, top10={result['top10'][:5]}")

    df = pd.DataFrame(rows)
    print("\n" + "="*60)
    print("Norman 2019 PGAA Summary")
    print("="*60)
    print(df[["target", "n_pert", "n_ctrl", "n_sig", "time"]].to_string(index=False))
    df.to_csv("scripts/norman2019_results.csv", index=False)
