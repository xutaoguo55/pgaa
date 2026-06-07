#!/usr/bin/env python3
"""
Perturbation-type simulation study for PRT.

Compares S₁, S₂, and S₁+S₂ mean z power under 3 perturbation types:
  (A) Mean shift: ALL perturbed cells get the same log-FC
  (B) Bimodality shift: only a SUBSET of perturbed cells get the log-FC
  (C) Both: mean + bimodality

Vary effect size θ ∈ {0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0}.
Measure TPR @ FPR=0.05 (using known ground truth).

Expected (paper hypothesis):
  - S₁ best for Type A
  - S₂ best for Type B
  - Combined z best for Type C
"""

import time
import numpy as np
import pandas as pd
import scanpy as sc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pgaa.core.prt_s2 import compute_persistence_1d, persistence_landscape_distance
from pgaa.core.prt import prt_s1_test
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from scipy.stats import norm

np.random.seed(42)


def simulate(
    n_cells=2000,
    n_genes=500,
    n_confounders=5,
    n_targets=10,
    n_downstream_per_target=20,
    theta=0.4,
    overdispersion=2.0,
    perturbation_type="A",  # A, B, C
    bimodality_fraction=0.4,  # for B/C: fraction of perturbed cells that get the shift
    seed=42,
):
    """Simulate with controlled perturbation type."""
    rng = np.random.default_rng(seed)

    Z = rng.normal(size=(n_cells, n_confounders))
    beta = rng.normal(size=(n_confounders, n_genes), scale=0.5)
    intercept = rng.lognormal(mean=1.5, sigma=1.0, size=n_genes)
    mu_log = Z @ beta + intercept
    mu_log = np.clip(mu_log, -2, 8)
    mu = np.exp(mu_log)
    lib_size = rng.lognormal(mean=0, sigma=0.3, size=n_cells)[:, None]
    mu = mu * lib_size

    alpha = 1.0 / overdispersion
    n_nb = 1.0 / alpha
    p_nb = n_nb / (n_nb + mu)
    counts = rng.negative_binomial(n_nb, p_nb).astype(np.float64)

    dropout_prob = 0.10 * np.exp(-mu_log)
    dropout_prob = np.clip(dropout_prob, 0, 0.8)
    mask = rng.random(counts.shape) < dropout_prob
    counts[mask] = 0

    gene_names = [f"gene_{i:04d}" for i in range(n_genes)]
    cell_names = [f"cell_{i:04d}" for i in range(n_cells)]
    # Always include gene_0000 as the first target
    if n_targets > 1:
        other_targets = rng.choice(np.arange(1, n_genes), size=n_targets - 1, replace=False)
        target_idx = np.concatenate([[0], other_targets])
    else:
        target_idx = np.array([0])

    gt_rows = []
    downstream_map = {}
    for tidx in target_idx:
        available = [i for i in range(n_genes) if i != tidx]
        didx = rng.choice(available, size=n_downstream_per_target, replace=False)
        thetas = rng.normal(loc=theta, scale=0.1, size=n_downstream_per_target)
        downstream_map[tidx] = (didx, thetas)
        for d, th in zip(didx, thetas):
            gt_rows.append({"target": gene_names[tidx], "downstream": gene_names[d], "theta": float(th)})

    n_pert = n_cells // 2
    pert_cells = rng.choice(n_cells, size=n_pert, replace=False)
    pert_labels = np.full(n_cells, "control", dtype=object)

    for i, cidx in enumerate(pert_cells):
        tidx = target_idx[i % n_targets]
        pert_labels[cidx] = gene_names[tidx]
        # KO target
        counts[cidx, tidx] = rng.poisson(0.5)
        # Apply downstream effect depending on type
        didx_list, thetas = downstream_map[tidx]
        apply_shift = True
        if perturbation_type in ("B", "C"):
            # Only bimodality_fraction of perturbed cells get the shift
            if rng.random() > bimodality_fraction:
                apply_shift = False
        for d, th in zip(didx_list, thetas):
            if apply_shift:
                fc = np.exp(th)
                new_mu = counts[cidx, d] * fc
                counts[cidx, d] = rng.poisson(np.clip(new_mu, 0, 500))

    adata = sc.AnnData(
        X=counts,  # dense
        obs=pd.DataFrame({"perturbation": pert_labels}, index=cell_names),
        var=pd.DataFrame(index=gene_names),
    )
    adata.uns["ground_truth"] = pd.DataFrame(gt_rows)
    return adata


def s2_test_fast(Y_on, Y_off, n_bins=30):
    g_min = min(Y_on.min(), Y_off.min())
    g_max = max(Y_on.max(), Y_off.max())
    bins = np.linspace(g_min, g_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    n_genes = Y_on.shape[1]
    s2 = np.zeros(n_genes)
    for g in range(n_genes):
        h_on, _ = np.histogram(Y_on[:, g], bins=bins, density=True)
        h_off, _ = np.histogram(Y_off[:, g], bins=bins, density=True)
        pd_on = compute_persistence_1d(h_on, bin_centers)
        pd_off = compute_persistence_1d(h_off, bin_centers)
        s2[g] = persistence_landscape_distance(pd_on, pd_off, n_top=3)
    return s2


def main():
    results = []
    types = ["A", "B", "C"]
    thetas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
    n_reps = 3  # 3 replicates per condition for stability

    total = len(types) * len(thetas) * n_reps
    count = 0
    for ptype in types:
        for theta in thetas:
            for rep in range(n_reps):
                count += 1
                t0 = time.time()
                adata = simulate(
                    n_cells=2000, n_genes=500,
                    n_targets=10, n_downstream_per_target=20,
                    theta=theta, perturbation_type=ptype,
                    bimodality_fraction=0.4,
                    seed=42 + rep * 100,
                )
                # Normalize
                sc.pp.normalize_total(adata, target_sum=1e4)
                sc.pp.log1p(adata)

                # Use first target only
                labels = adata.obs["perturbation"].astype(str)
                pert_idx = np.where(labels == "gene_0000")[0]
                ctrl_idx = np.where(labels == "control")[0][:len(pert_idx) * 3]
                if len(pert_idx) < 30:
                    continue

                X = adata.X
                genes = list(adata.var_names)
                lib_size = np.array(X.sum(axis=1)).ravel()

                # Get ground truth for this target
                gt = adata.uns["ground_truth"]
                gt = gt[gt["target"] == "gene_0000"]
                causal_genes = set(gt["downstream"].tolist())
                # gene_0000 itself is excluded from the test (it's the target)
                # so we evaluate only the DOWNSTREAM causal genes

                is_causal = np.array([g in causal_genes and g != "gene_0000" for g in genes])
                if is_causal.sum() == 0:
                    continue

                # S₁
                t_s1 = time.time()
                res_s1 = prt_s1_test(X, genes, "gene_0000", pert_idx, ctrl_idx, n_perms=200)
                t_s1 = time.time() - t_s1
                # gene_0000 itself is excluded; we set its p=1.0
                p_s1 = np.ones(len(genes))
                p_s1_dict = res_s1.set_index("gene")["p_value_perm"].to_dict()
                for i, g in enumerate(genes):
                    if g in p_s1_dict:
                        p_s1[i] = p_s1_dict[g]

                # S₂ (fast version, no perm for simulation — use rank-based)
                # Subset to relevant cells
                test_idx = np.concatenate([pert_idx, ctrl_idx])
                Y = X[test_idx]
                D = np.zeros(len(test_idx), dtype=bool)
                D[:len(pert_idx)] = True
                Y_on = Y[D]; Y_off = Y[~D]
                s2_obs = s2_test_fast(Y_on, Y_off, n_bins=30)
                # Convert S₂ to p via rank (since S₂ has no built-in perm)
                # Use rank normalized as z-score
                s2_rank = pd.Series(s2_obs).rank(method='average').values
                s2_p = (s2_rank - 0.5) / len(s2_rank)
                # Two-sided: take 1 - abs(2p-1)
                # Actually use right-tail: high S₂ = significant
                s2_p_one = 1 - (s2_rank - 0.5) / len(s2_rank)
                p_s2 = s2_p_one

                # Combined z = (z_S1 + z_S2) / sqrt(2)
                z_s1 = norm.ppf(1 - np.clip(p_s1, 1e-10, 1 - 1e-10))
                z_s2 = norm.ppf(1 - np.clip(p_s2, 1e-10, 1 - 1e-10))
                p_comb = 1 - norm.cdf((z_s1 + z_s2) / np.sqrt(2))

                # TPR @ FPR=0.05
                def tpr_at_fpr(p, is_causal, fpr_target=0.05):
                    # Use roc_auc to get ranking
                    score = -np.log10(np.clip(p, 1e-300, 1))
                    if is_causal.sum() == 0 or (~is_causal).sum() == 0:
                        return np.nan
                    # Rank all genes
                    order = np.argsort(-score)  # highest score first
                    is_causal_ordered = is_causal[order]
                    cum_tp = np.cumsum(is_causal_ordered)
                    cum_fp = np.cumsum(~is_causal_ordered)
                    tpr = cum_tp / max(is_causal.sum(), 1)
                    fpr = cum_fp / max((~is_causal).sum(), 1)
                    # Find FPR=0.05
                    idx = np.searchsorted(fpr, fpr_target)
                    idx = min(idx, len(fpr) - 1)
                    return float(tpr[idx])

                tpr_s1 = tpr_at_fpr(p_s1, is_causal)
                tpr_s2 = tpr_at_fpr(p_s2, is_causal)
                tpr_comb = tpr_at_fpr(p_comb, is_causal)
                # Also AUROC
                auroc_s1 = roc_auc_score(is_causal, -np.log10(np.clip(p_s1, 1e-300, 1)))
                auroc_s2 = roc_auc_score(is_causal, -np.log10(np.clip(p_s2, 1e-300, 1)))
                auroc_comb = roc_auc_score(is_causal, -np.log10(np.clip(p_comb, 1e-300, 1)))

                elapsed = time.time() - t0
                results.append({
                    "type": ptype, "theta": theta, "rep": rep,
                    "n_pert": len(pert_idx), "n_causal": int(is_causal.sum()),
                    "TPR_S1": tpr_s1, "TPR_S2": tpr_s2, "TPR_comb": tpr_comb,
                    "AUROC_S1": auroc_s1, "AUROC_S2": auroc_s2, "AUROC_comb": auroc_comb,
                    "time": elapsed,
                })
                print(f"  [{count}/{total}] type={ptype} θ={theta} rep={rep} "
                      f"TPR: S1={tpr_s1:.2f} S2={tpr_s2:.2f} comb={tpr_comb:.2f} "
                      f"({int(elapsed)}s)", flush=True)

    df = pd.DataFrame(results)
    df.to_csv("scripts/simulation_powers.csv", index=False)
    print(f"\nSaved: scripts/simulation_powers.csv")

    # Aggregate by type × theta
    print("\n=== Mean TPR @ FPR=0.05 across reps ===")
    print(f"{'Type':<6} {'θ':<6} {'TPR_S1':>8} {'TPR_S2':>8} {'TPR_comb':>10} {'Best':>8}")
    for ptype in types:
        for theta in thetas:
            sub = df[(df["type"] == ptype) & (df["theta"] == theta)]
            if len(sub) == 0:
                continue
            s1 = sub["TPR_S1"].mean()
            s2 = sub["TPR_S2"].mean()
            cb = sub["TPR_comb"].mean()
            best = "S1" if s1 >= s2 and s1 >= cb else ("S2" if s2 >= cb else "comb")
            print(f"{ptype:<6} {theta:<6.1f} {s1:>8.3f} {s2:>8.3f} {cb:>10.3f} {best:>8}")


if __name__ == "__main__":
    main()
