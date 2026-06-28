#!/usr/bin/env python3
"""
PGAA benchmark on Adamson et al. 2016 UPR CRISPRi Perturb-seq (GSE90546).

~65K K562 cells, 91 sgRNAs targeting 82 genes involved in the
unfolded protein response (UPR). Each cell receives one sgRNA
(CRISPRi knockdown of a UPR gene) or a non-targeting control.

Ground truth: known UPR pathway members (IRE1, PERK, ATF6 branches)
should show downstream transcriptional effects when knocked down.

Reference: Adamson et al. (2016) Cell 167(7):1867-1882.
"""
import argparse
import numpy as np, pandas as pd, scanpy as sc, sys, time, os, gzip
from pathlib import Path
from scipy import sparse
from scipy.io import mmread
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt import prt_s1_test
from pgaa.core.prt_s2 import s2_test
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, average_precision_score

np.random.seed(42)

# UPR pathway genes — known members from Adamson 2016
UPR_GENES = {
    "IRE1 branch": ["ERN1", "XBP1", "HSPA5", "DNAJB9", "DNAJC3", "SEC61A1"],
    "PERK branch": ["EIF2AK3", "ATF4", "DDIT3", "PPP1R15A", "TRIB3", "CHAC1"],
    "ATF6 branch": ["ATF6", "MBTPS1", "MBTPS2", "CALR", "PDIA4", "HYOU1"],
    "ERAD": ["EDEM1", "SYVN1", "SEL1L", "HERPUD1", "DERL1"],
    "Chaperones": ["HSPA5", "HSP90B1", "CALR", "PDIA3", "PDIA6", "ERP29"],
}
ALL_UPR = list(set(sum(UPR_GENES.values(), [])))


PAPER_TARGETS = [
    "SPI1_pDS255",
    "ZNF326_pDS262",
    "BHLHE40_pDS258",
    "CREB1_pDS269",
    "DDIT3_pDS263",
]
CONTROL_LABEL = "62(mod)_pBA581"


def load_adamson(tar_path, extract_dir="/tmp/adamson2016", sample_prefix="GSM2406675_10X001"):
    """Extract and load the Adamson 10X001 UPR perturbation batch from GEO."""
    os.makedirs(extract_dir, exist_ok=True)

    expected = [
        f"{sample_prefix}_matrix.mtx.txt.gz",
        f"{sample_prefix}_barcodes.tsv.gz",
        f"{sample_prefix}_genes.tsv.gz",
        f"{sample_prefix}_cell_identities.csv.gz",
    ]
    if not all((Path(extract_dir) / name).exists() for name in expected):
        import tarfile
        print(f"Extracting {tar_path} ...")
        with tarfile.open(tar_path) as tf:
            tf.extractall(extract_dir)
        print(f"Extracted to {extract_dir}")

    base = Path(extract_dir)
    mtx_path = base / f"{sample_prefix}_matrix.mtx.txt.gz"
    barcode_path = base / f"{sample_prefix}_barcodes.tsv.gz"
    gene_path = base / f"{sample_prefix}_genes.tsv.gz"
    meta_path = base / f"{sample_prefix}_cell_identities.csv.gz"
    missing = [str(p) for p in [mtx_path, barcode_path, gene_path, meta_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing expected Adamson files: {missing}")

    print(f"Loading Adamson {sample_prefix} MatrixMarket files ...")
    X = sparse.csr_matrix(mmread(mtx_path).T)
    with gzip.open(barcode_path, "rt") as handle:
        barcodes = [line.strip() for line in handle]
    genes_df = pd.read_csv(gene_path, sep="\t", header=None)
    gene_symbols = genes_df.iloc[:, 1].astype(str).tolist()
    meta = pd.read_csv(meta_path)
    meta = meta.rename(columns={"cell BC": "cell_barcode", "guide identity": "guide_identity"})
    meta = meta.set_index("cell_barcode")

    adata = sc.AnnData(
        X=X,
        obs=pd.DataFrame(index=barcodes).join(meta, how="left"),
        var=pd.DataFrame(index=gene_symbols),
    )
    adata.obs["perturbation"] = adata.obs["guide_identity"].astype(str)

    print(f"Loaded: {adata.shape}")
    return adata


def preprocess_perturbseq(adata):
    """Standard PGAA preprocessing for Perturb-seq data."""
    sc.pp.filter_cells(adata, min_counts=500)
    sc.pp.filter_genes(adata, min_cells=10)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)
    return adata


def benchmark_sgRNA(adata, sgRNA_label, n_perms=200, n_bins=20):
    """Run PGAA on cells with a specific sgRNA vs non-targeting controls."""
    target_gene = sgRNA_label.split("_pDS", 1)[0]
    # Find perturbed cells (containing this sgRNA)
    if 'perturbation' in adata.obs.columns:
        labels = adata.obs['perturbation'].astype(str)
    elif 'guide_identity' in adata.obs.columns:
        labels = adata.obs['guide_identity'].astype(str)
    else:
        # Use the cell barcode prefix or any available label
        print(f"  Available obs columns: {list(adata.obs.columns)[:10]}")
        raise ValueError("No perturbation label column found")

    pert_idx = np.where(labels.str.contains(sgRNA_label, case=False, na=False))[0]
    ctrl_idx = np.where(
        (labels == CONTROL_LABEL)
        | labels.str.contains("non-targeting|NegCtrl|negative|control", case=False, na=False)
    )[0]

    if len(pert_idx) < 20 or len(ctrl_idx) < 20:
        return None

    ctrl_idx = ctrl_idx[:len(pert_idx) * 3]
    X = adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X
    genes = list(adata.var_names)
    lib = np.array(X.sum(1)).ravel()
    ct = KMeans(n_clusters=5, random_state=42, n_init=10).fit_predict(X)

    t0 = time.time()
    if target_gene not in genes:
        raise ValueError(f"Target gene {target_gene} not present in HVG universe")

    res_s1 = prt_s1_test(X, genes, target_gene, pert_idx, ctrl_idx,
                         n_perms=n_perms, cell_type=ct, library_size=lib)
    t_s1 = time.time() - t0

    # Get S2 scores (no permutation for speed)
    res_s2 = s2_test(X, genes, target_gene, pert_idx, ctrl_idx,
                     n_bins=n_bins, cell_type=ct, library_size=lib)

    return {"s1": res_s1, "s2": res_s2, "t_s1": t_s1,
            "n_pert": len(pert_idx), "n_ctrl": len(ctrl_idx),
            "target_gene": target_gene}


def compute_metrics(results, known_genes, target_label, gene_column='gene'):
    """Compute AUROC and enrichment for known UPR genes."""
    s1_ranks = results['s1'].sort_values('W_observed', ascending=False)
    s2_ranks = results['s2'].sort_values('S2', ascending=False)

    found_known = [g for g in known_genes if g in s1_ranks[gene_column].values]
    if len(found_known) < 3:
        return None

    # S1 metrics
    labels = s1_ranks[gene_column].isin(known_genes).astype(int).values
    auroc_s1 = roc_auc_score(labels, s1_ranks['W_observed'].values)

    # S2 metrics
    labels2 = s2_ranks[gene_column].isin(known_genes).astype(int).values
    auroc_s2 = roc_auc_score(labels2, s2_ranks['S2'].values)

    # Top-20 enrichment
    top20_s1 = s1_ranks.head(20)[gene_column].isin(known_genes).sum()
    top20_s2 = s2_ranks.head(20)[gene_column].isin(known_genes).sum()

    return {"target": target_label,
            "n_pert": results['n_pert'], "n_found": len(found_known),
            "auroc_s1": auroc_s1, "auroc_s2": auroc_s2,
            "top20_s1": top20_s1, "top20_s2": top20_s2,
            "t_s1": results['t_s1']}


def main():
    parser = argparse.ArgumentParser(description="Raw GEO sanity rerun for the Adamson 2016 UPR benchmark.")
    parser.add_argument(
        "--tar",
        default=os.environ.get("ADAMSON2016_RAW_TAR", "adamson2016_RAW.tar"),
        help="Path to the downloaded GSE90546 Adamson 2016 raw tar archive. "
        "May also be provided with ADAMSON2016_RAW_TAR.",
    )
    args = parser.parse_args()

    tar_path = args.tar
    if not os.path.exists(tar_path):
        print(f"ERROR: {tar_path} not found. Download the GSE90546 raw archive first, then pass --tar or set ADAMSON2016_RAW_TAR.")
        sys.exit(1)

    # Load and preprocess
    adata = load_adamson(tar_path)
    adata = preprocess_perturbseq(adata)

    # Find the perturbation labels
    print(f"\nobs columns: {list(adata.obs.columns)}")
    if 'perturbation' in adata.obs.columns:
        pert_counts = adata.obs['perturbation'].value_counts()
    elif 'guide_identity' in adata.obs.columns:
        pert_counts = adata.obs['guide_identity'].value_counts()
    else:
        print("Trying to identify perturbation labels from barcodes...")
        # Fallback: look for column with sgRNA/gene names
        for col in adata.obs.columns:
            if adata.obs[col].nunique() > 5 and adata.obs[col].nunique() < 200:
                print(f"  {col}: {adata.obs[col].nunique()} unique values — possible label column")

    top_targets = PAPER_TARGETS

    print(f"\nBenchmarking {len(top_targets)} perturbations...")
    results = []
    for t in top_targets:
        print(f"  {t}...", end=" ", flush=True)
        try:
            res = benchmark_sgRNA(adata, t, n_perms=200)
            if res:
                metrics = compute_metrics(res, ALL_UPR, t)
                if metrics:
                    results.append(metrics)
                    print(f"OK (n={res['n_pert']}, AUROC_S1={metrics['auroc_s1']:.3f})")
                else:
                    print(f"OK but <3 known UPR genes found")
            else:
                print("SKIP (too few cells)")
        except Exception as e:
            print(f"ERROR: {e}")

    if results:
        df = pd.DataFrame(results)
        df.to_csv("scripts/adamson2016_results.csv", index=False)
        print(f"\nSaved: scripts/adamson2016_results.csv")
        print(f"\nSummary:")
        print(f"  S1 mean AUROC: {df['auroc_s1'].mean():.3f}")
        print(f"  S2 mean AUROC: {df['auroc_s2'].mean():.3f}")
        print(f"  S1 top-20 hits (mean): {df['top20_s1'].mean():.1f}")
        print(f"  S2 top-20 hits (mean): {df['top20_s2'].mean():.1f}")
    else:
        print("No results — check data structure")


if __name__ == "__main__":
    main()
