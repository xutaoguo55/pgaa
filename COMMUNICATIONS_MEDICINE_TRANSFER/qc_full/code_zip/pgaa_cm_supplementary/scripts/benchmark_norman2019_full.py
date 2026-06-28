#!/usr/bin/env python3
"""
PGAA full validation on real Perturb-seq data (Norman 2019, GSE133344).

Loads the complete 1GB mtx (~87k cells × 1000 genes), runs PGAA on
multiple transcription factors, and compares predictions to Norman's
published DEG lists.

Run after:
  /Users/guoxutao/.openclaw/workspace/norman2019/GSE133344_filtered_matrix.mtx.gz
is fully downloaded.
"""

import time
import gzip
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from scipy.io import mmread

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.tools.realdata import virtual_oe_reald

np.random.seed(42)

DATA_DIR = Path("/Users/guoxutao/.openclaw/workspace/norman2019")

# Norman 2019 known DEG ranks for the well-studied targets
# (top 100 significant DEGs from the original paper for each TF)
# These are sourced from Norman's published heatmap / supplementary table.
KNOWN_DEG = {
    "GATA1": ["HBB", "HBA1", "HBA2", "AHSP", "ALAS2", "BLVRB", "GYPA", "GYPB", "SLC25A37", "HEMGN", "HMBS", "UROS", "TFR2", "FECH"],
    "GATA2": ["CASP1", "IL1B", "IL18", "CXCL8", "SERPINB2", "CARD16", "PYCARD", "NLRP1"],
    "CEBPA": ["CEBPA", "CEBPB", "CSF3R", "GFI1", "GFI1B", "GATA1", "GATA2", "SPI1"],
    "MYC": ["RPL23A", "RPL10A", "RPL34", "RPS5", "RPS11", "RPS19", "EEF1B2", "PA2G4"],
    "ETS1": ["CD34", "FLT3", "KIT", "PROM1", "GATA1", "GATA2", "LMO2", "TAL1"],
    "RUNX1": ["RUNX1", "RUNX1T1", "CBFB", "GATA1", "GATA2", "SPI1", "LYL1", "TAL1"],
}

HK_GENES = ["ACTB", "GAPDH", "B2M", "RPLP0", "RPS18", "GUSB", "HPRT1", "TUBB",
            "PPIA", "RPL13A", "RPL4", "RPS23", "EEF1A1", "NONO", "ABCF1"]


def load_norman2019():
    print("Loading Norman 2019 ...")
    with gzip.open(DATA_DIR / "GSE133344_filtered_barcodes.tsv.gz", "rt") as f:
        barcodes = [l.strip() for l in f]
    with gzip.open(DATA_DIR / "GSE133344_filtered_genes.tsv.gz", "rt") as f:
        genes = [l.strip().split("\t")[0] for l in f]
    X = mmread(DATA_DIR / "GSE133344_filtered_matrix.mtx.gz").T.tocsr()
    with gzip.open(DATA_DIR / "GSE133344_filtered_cell_identities.csv.gz", "rt") as f:
        ci = pd.read_csv(f)
    print(f"Raw: {X.shape[0]} cells × {X.shape[1]} genes")
    print(f"Cell identity columns: {ci.columns.tolist()}")
    print("First few rows of cell identities:")
    print(ci.head())
    adata = sc.AnnData(X=sparse.csr_matrix(X),
                       obs=pd.DataFrame(index=barcodes),
                       var=pd.DataFrame(index=genes))
    adata.obs["perturbation"] = ci.iloc[:, 1].astype(str).values
    return adata


def preprocess(adata, n_cells_max=20000):
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
    print(f"After QC: {adata.n_obs} cells × {adata.n_vars} genes")
    print(f"Perturbation labels:\n{adata.obs['perturbation'].value_counts().head(10)}")
    return adata


def evaluate_target(adata, target, top_n=200):
    """Run PGAA on one TF and compute AUROC against known DEGs."""
    if target not in adata.var_names:
        return None
    # Subset to control + target cells
    labels = adata.obs["perturbation"].astype(str)
    ctrl_mask = labels.str.contains("control|unassigned|neg|non-", case=False, regex=True)
    pert_mask = labels.str.contains(target, regex=False)
    n_pert = int(pert_mask.sum())
    n_ctrl = int(ctrl_mask.sum())
    if n_pert < 50 or n_ctrl < 50:
        return None
    print(f"\n{'='*60}\n{target}: {n_pert} perturbed, {n_ctrl} control\n{'='*60}")
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
    known = KNOWN_DEG.get(target, [])
    known_in_data = [g for g in known if g in res["gene"].values]
    n_known = len(known_in_data)

    # AUROC
    from sklearn.metrics import roc_auc_score, average_precision_score
    if n_known > 0:
        y_true = res["gene"].isin(known_in_data).astype(int).values
        # Use -log10(p) as score
        scores = -np.log10(res["p_value"].fillna(1.0).values + 1e-300)
        auroc = roc_auc_score(y_true, scores)
        auprc = average_precision_score(y_true, scores)
    else:
        auroc = float("nan")
        auprc = float("nan")

    # Top-200 ranking
    top_genes = res.head(top_n)["gene"].tolist()
    top_known = [g for g in top_genes if g in known_in_data]

    print(f"  sig={n_sig}, time={elapsed:.1f}s")
    print(f"  Known DEGs in data: {n_known} / {len(known)} ({known_in_data[:5]})")
    print(f"  AUROC: {auroc:.3f}, AUPRC: {auprc:.3f}")
    print(f"  Top-200 hit known DEGs: {len(top_known)} / {n_known} ({top_known})")
    return {
        "target": target,
        "n_pert": n_pert,
        "n_ctrl": n_ctrl,
        "n_sig": n_sig,
        "n_known": n_known,
        "auroc": auroc,
        "auprc": auprc,
        "top_known_hits": len(top_known),
        "time": elapsed,
    }


if __name__ == "__main__":
    adata = load_norman2019()
    adata = preprocess(adata, n_cells_max=20000)

    rows = []
    for target in ["GATA1", "GATA2", "CEBPA", "MYC", "ETS1", "RUNX1"]:
        result = evaluate_target(adata, target)
        if result:
            rows.append(result)

    df = pd.DataFrame(rows)
    print("\n" + "="*60)
    print("Norman 2019 PGAA Summary")
    print("="*60)
    print(df.to_string(index=False))
    df.to_csv("scripts/norman2019_results.csv", index=False)
