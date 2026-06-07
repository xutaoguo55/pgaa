#!/usr/bin/env python3
"""
PRT-S₃ fast: MI delta ranking, no permutation.
Tests if CEBPE known targets have higher S₃ than random genes.

S₃_g = median_{partner in myel_genes} |I(Y_g; Y_partner | D=1) - I(Y_g; Y_partner | D=0)|
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt_s3 import kraskov_mi
from sklearn.metrics import roc_auc_score

np.random.seed(42)


def main():
    adata = sc.read_h5ad(
        "/Users/guoxutao/.openclaw/workspace/norman2019/norman2019_full_log.h5ad"
    )
    labels = adata.obs["perturbation"].astype(str)
    cebpe_pert = np.where(labels.str.contains(r"^CEBPE_NegCtrl\d+__", regex=True))[0]
    ctrl_mask = labels.str.contains(r"^NegCtrl\d+_NegCtrl\d+__", regex=True)
    ctrl_idx = np.where(ctrl_mask)[0][: len(cebpe_pert) * 3]

    hvg = adata.var["highly_variable"].values.copy()
    myeloid_partners = [
        "ELANE", "CTSG", "LYZ", "MPO", "AZU1", "PRTN3", "DEFA1",
        "CEBPE", "CEBPA", "GFI1", "SPI1",
    ]
    cebpe_targets = [
        "ELANE", "CTSG", "LYZ", "MPO", "GFI1", "AZU1", "PRTN3",
        "DEFA1", "RNASE2",
    ]
    for g in myeloid_partners + cebpe_targets + ["GAPDH", "ACTB", "B2M", "RNASE2"]:
        if g in adata.var_names:
            hvg[list(adata.var_names).index(g)] = True
    adata_hvg = adata[:, hvg].copy()
    X = adata_hvg.X.toarray() if hasattr(adata_hvg.X, "toarray") else adata_hvg.X
    genes = list(adata_hvg.var_names)

    test_idx = np.concatenate([cebpe_pert, ctrl_idx])
    X_sub = X[test_idx]
    N_sub = len(test_idx)
    n_pert = len(cebpe_pert)
    D = np.zeros(N_sub, dtype=bool)
    D[:n_pert] = True

    # Select myeloid partners present in data
    partner_idx = [genes.index(g) for g in myeloid_partners if g in genes]
    print(f"Using {len(partner_idx)} myeloid partner genes")
    tidx = genes.index("CEBPE") if "CEBPE" in genes else partner_idx[0]
    other_idx = [i for i in range(len(genes)) if i != tidx]

    # ─── S₃ for each gene (MI delta with each myeloid partner) ───
    print(f"Computing S₃ for {len(other_idx)} genes × {len(partner_idx)} partners ...\n"
          f"  CEBPE perturbed: {n_pert}, control: {n_pert*3}")

    t0 = time.time()
    s3_values = np.zeros(len(other_idx))
    for g_idx, g_orig in enumerate(other_idx):
        if g_idx % 200 == 0:
            elapsed = time.time() - t0
            eta = (elapsed / (g_idx + 1)) * (len(other_idx) - g_idx)
            print(f"  {g_idx}/{len(other_idx)}, {int(elapsed)}s, ~{int(eta)}s left")
        y_g = X_sub[:, g_orig]
        mi_deltas = []
        for h_orig in partner_idx:
            if h_orig == g_orig:
                continue
            y_h = X_sub[:, h_orig]
            mi_on = kraskov_mi(y_g[D], y_h[D], k=5)
            mi_off = kraskov_mi(y_g[~D], y_h[~D], k=5)
            mi_deltas.append(abs(mi_on - mi_off))
        s3_values[g_idx] = np.median(mi_deltas) if mi_deltas else 0.0

    elapsed = time.time() - t0
    print(f"S₃ done in {elapsed:.0f}s")

    # ─── Ranking ──────────────────────────────────────────────
    res = pd.DataFrame({
        "gene": [genes[i] for i in other_idx],
        "S3": s3_values,
    }).sort_values("S3", ascending=False)

    print("\nTop 20 by S₃:")
    print(res.head(20).to_string(index=False))

    # Known targets
    s3_known = res[res["gene"].isin(cebpe_targets)]
    print(f"\nCEBPE known targets S₃ ranking:")
    s3_known_sorted = s3_known.sort_values("S3", ascending=False)
    for _, row in s3_known_sorted.iterrows():
        rank = (res["S3"] > row["S3"]).sum() + 1
        print(f"  {row['gene']:6s}  S₃={row['S3']:.3f}  rank={rank}/{len(res)}  "
              f"percentile={rank/len(res)*100:.1f}%")

    # How many known targets in top 100?
    top100 = res.head(100)["gene"].tolist()
    n_in_top100 = len([g for g in cebpe_targets if g in top100])
    print(f"\nCEBPE targets in top-100: {n_in_top100}/{len(cebpe_targets)}")

    # AUROC
    y_true = res["gene"].isin(cebpe_targets).astype(int).values
    if y_true.sum() > 0:
        auroc = roc_auc_score(y_true, res["S3"].values)
    else:
        auroc = float("nan")
    print(f"AUROC: {auroc:.3f}")

    # ─── GAPDH negative control ───────────────────────────────
    print("\n" + "=" * 60)
    print("GAPDH negative control")
    print("=" * 60)
    tidx_g = genes.index("GAPDH") if "GAPDH" in genes else tidx
    other_idx_g = [i for i in range(len(genes)) if i != tidx_g]
    s3_values_g = np.zeros(len(other_idx_g))
    for g_idx, g_orig in enumerate(other_idx_g):
        y_g = X_sub[:, g_orig]
        mi_deltas = []
        for h_orig in partner_idx:
            if h_orig == g_orig:
                continue
            y_h = X_sub[:, h_orig]
            mi_deltas.append(abs(
                kraskov_mi(y_g[D], y_h[D], k=5)
                - kraskov_mi(y_g[~D], y_h[~D], k=5)
            ))
        s3_values_g[g_idx] = np.median(mi_deltas) if mi_deltas else 0.0

    res_g = pd.DataFrame({
        "gene": [genes[i] for i in other_idx_g],
        "S3": s3_values_g,
    }).sort_values("S3", ascending=False)

    # CEBPE targets in GAPDH scoring
    gapdh_hits = res_g[res_g["gene"].isin(cebpe_targets)]
    print(f"CEBPE targets in GAPDH-S₃ top-100: "
          f"{len([g for g in top100 if g in gapdh_hits['gene'].values])}"
          f"/{len(cebpe_targets)}")
    print("GAPDH S₃ for CEBPE targets:")
    for _, row in gapdh_hits.sort_values("S3", ascending=False).iterrows():
        rank = np.sum(res_g["S3"] > row["S3"]) + 1
        print(f"  {row['gene']:6s}  S₃={row['S3']:.3f}  rank={rank}/{len(res_g)}")

    # ─── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PRT-S₃ fast summary (MI delta ranking)")
    print("=" * 60)
    print(f"  CEBPE known targets in top-100: {n_in_top100}/{len(cebpe_targets)}")
    print(f"  CEBPE AUROC: {auroc:.3f}")
    print(f"  GAPDH neg: CEBPE targets rank {n_in_top100}/9 (vs {n_in_top100} for CEBPE)")

    res.to_csv("scripts/prt_s3_fast.csv", index=False)


if __name__ == "__main__":
    main()
