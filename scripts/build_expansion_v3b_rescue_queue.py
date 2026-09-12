#!/usr/bin/env python3
"""Build a result-blind rescue queue for expansion-v3 metadata shortfall."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evidence/scperturb_zenodo_13350497_h5ad_catalog.tsv"


RESCUE_CANDIDATES = [
    {
        "priority": 15,
        "candidate_id": "datlinger2021_jurkat_crispr",
        "source_study": "DatlingerBock2021",
        "laboratory_group": "Datlinger_Bock",
        "cell_context_class": "Jurkat_T_cell",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "DatlingerBock2021.h5ad",
        "rescue_reason": "small independent CRISPR perturb-seq file; likely has recorded replicate/control metadata",
    },
    {
        "priority": 16,
        "candidate_id": "srivatsan2020_sciplex2",
        "source_study": "SrivatsanTrapnell2020",
        "laboratory_group": "Srivatsan_Trapnell",
        "cell_context_class": "cancer_cell_line",
        "perturbation_mechanism": "drug",
        "source_file": "SrivatsanTrapnell2020_sciplex2.h5ad",
        "rescue_reason": "moderate-size drug screen with expected vehicle/dose structure",
    },
    {
        "priority": 17,
        "candidate_id": "srivatsan2020_sciplex4",
        "source_study": "SrivatsanTrapnell2020",
        "laboratory_group": "Srivatsan_Trapnell",
        "cell_context_class": "cancer_cell_line",
        "perturbation_mechanism": "drug",
        "source_file": "SrivatsanTrapnell2020_sciplex4.h5ad",
        "rescue_reason": "second SciPlex design for metadata screening; not automatically counted as independent of sciplex2",
    },
    {
        "priority": 18,
        "candidate_id": "tian2019_ipsc_crispri",
        "source_study": "TianKampmann2019",
        "laboratory_group": "Tian_Kampmann",
        "cell_context_class": "iPSC",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "TianKampmann2019_iPSC.h5ad",
        "rescue_reason": "human iPSC CRISPRi file with expected batch metadata",
    },
    {
        "priority": 19,
        "candidate_id": "tian2021_crispri",
        "source_study": "TianKampmann2021",
        "laboratory_group": "Tian_Kampmann",
        "cell_context_class": "iPSC_neuron",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "TianKampmann2021_CRISPRi.h5ad",
        "rescue_reason": "paired CRISPRi complement to existing CRISPRa design; screened as same-lab backup",
    },
    {
        "priority": 20,
        "candidate_id": "adamson2016_10x001",
        "source_study": "AdamsonWeissman2016",
        "laboratory_group": "Adamson_Weissman",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "AdamsonWeissman2016_GSM2406675_10X001.h5ad",
        "rescue_reason": "small CRISPRi stress-response file; useful for quick metadata gate",
    },
    {
        "priority": 21,
        "candidate_id": "adamson2016_10x005",
        "source_study": "AdamsonWeissman2016",
        "laboratory_group": "Adamson_Weissman",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "AdamsonWeissman2016_GSM2406677_10X005.h5ad",
        "rescue_reason": "same study backup for split/control feasibility, not independent of adamson2016_10x001",
    },
    {
        "priority": 22,
        "candidate_id": "norman2019_k562_crispra",
        "source_study": "NormanWeissman2019",
        "laboratory_group": "Norman_Weissman",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPRa",
        "source_file": "NormanWeissman2019_filtered.h5ad",
        "rescue_reason": "known high-quality combinatorial perturb-seq benchmark; excluded from final if Replogle-family overlap is disallowed",
    },
    {
        "priority": 23,
        "candidate_id": "replogle2022_rpe1_crispri",
        "source_study": "ReplogleWeissman2022",
        "laboratory_group": "Replogle_Weissman",
        "cell_context_class": "RPE1_epithelial_cell_line",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "ReplogleWeissman2022_rpe1.h5ad",
        "rescue_reason": "different cell type from K562 Replogle; treated as same-lab backup until independence audit",
    },
    {
        "priority": 24,
        "candidate_id": "lara2023_bone_marrow_invivo",
        "source_study": "LaraAstiasoHuntly2023",
        "laboratory_group": "Lara_Astiaso_Huntly",
        "cell_context_class": "bone_marrow_in_vivo",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "LaraAstiasoHuntly2023_invivo.h5ad",
        "rescue_reason": "in vivo mouse perturbation context; same lab as v2 ex vivo file",
    },
    {
        "priority": 25,
        "candidate_id": "schiebinger2019_reprogramming_gse106340",
        "source_study": "SchiebingerLander2019",
        "laboratory_group": "Schiebinger_Lander",
        "cell_context_class": "cell_reprogramming",
        "perturbation_mechanism": "cytokine_state_transition",
        "source_file": "SchiebingerLander2019_GSE106340.h5ad",
        "rescue_reason": "state-transition context distinct from perturb-seq screens; screened as same-lab backup",
    },
    {
        "priority": 26,
        "candidate_id": "schraivogel2020_k562_tapseq_chr8",
        "source_study": "SchraivogelSteinmetz2020",
        "laboratory_group": "Schraivogel_Steinmetz",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPR_Cas9_TAPseq",
        "source_file": "SchraivogelSteinmetz2020_TAP_SCREEN__chromosome_8_screen.h5ad",
        "rescue_reason": "small independent TAP-seq chromosome screen; same lab as chr11 backup",
    },
]


def main() -> int:
    catalog = pd.read_csv(CATALOG, sep="\t").set_index("source_file")
    rows = []
    for candidate in RESCUE_CANDIDATES:
        source_file = candidate["source_file"]
        if source_file not in catalog.index:
            raise SystemExit(f"missing source file in catalog: {source_file}")
        source = catalog.loc[source_file]
        rows.append(
            {
                **candidate,
                "queue_role": "v3b_rescue_screen",
                "size_bytes": int(source["size_bytes"]),
                "source_url": source["source_url"],
                "source_md5": source["source_md5"],
                "expression_outcome_status": "not_scored_by_pgaa",
                "metadata_gate_status": "not_audited",
            }
        )
    out = pd.DataFrame(rows).sort_values("priority")
    out.to_csv(ROOT / "evidence/expansion_v3b_rescue_candidate_queue.tsv", sep="\t", index=False)
    print(f"wrote {len(out)} rescue candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
