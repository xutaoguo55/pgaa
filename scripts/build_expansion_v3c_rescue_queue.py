#!/usr/bin/env python3
"""Build a focused expansion-v3c rescue queue from the scPerturb H5AD catalog."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evidence/scperturb_zenodo_13350497_h5ad_catalog.tsv"
OUT = ROOT / "evidence/expansion_v3c_rescue_candidate_queue.tsv"


SELECTED = [
    {
        "priority": 27,
        "candidate_id": "datlinger2017_jurkat_crispr",
        "source_study": "DatlingerBock2017",
        "laboratory_group": "Datlinger_Bock",
        "cell_context_class": "Jurkat_T_cell",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "DatlingerBock2017.h5ad",
        "rescue_reason": "small independent Jurkat CRISPR stimulation design; screened for explicit target/control metadata",
    },
    {
        "priority": 28,
        "candidate_id": "dixit2016_k562_tf_7d",
        "source_study": "DixitRegev2016",
        "laboratory_group": "Dixit_Regev",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "DixitRegev2016_K562_TFs_7_days.h5ad",
        "rescue_reason": "classic Perturb-seq TF screen; distinct laboratory source from current ready set",
    },
    {
        "priority": 29,
        "candidate_id": "dixit2016_k562_tf_high_moi",
        "source_study": "DixitRegev2016",
        "laboratory_group": "Dixit_Regev",
        "cell_context_class": "K562_leukemia_high_moi",
        "perturbation_mechanism": "CRISPR_Cas9_high_MOI",
        "source_file": "DixitRegev2016_K562_TFs_High_MOI.h5ad",
        "rescue_reason": "same study backup with high-MOI structure; counted only as same-lab backup if both pass",
    },
    {
        "priority": 30,
        "candidate_id": "adamson2016_10x010",
        "source_study": "AdamsonWeissman2016",
        "laboratory_group": "Adamson_Weissman",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "CRISPRi",
        "source_file": "AdamsonWeissman2016_GSM2406681_10X010.h5ad",
        "rescue_reason": "larger Adamson file may have enough matched controls where smaller 10X001/10X005 did not",
    },
    {
        "priority": 31,
        "candidate_id": "gasperini2019_lowmoi",
        "source_study": "GasperiniShendure2019",
        "laboratory_group": "Gasperini_Shendure",
        "cell_context_class": "K562_leukemia",
        "perturbation_mechanism": "enhancer_CRISPRi_low_MOI",
        "source_file": "GasperiniShendure2019_lowMOI.h5ad",
        "rescue_reason": "low-MOI complement to high-MOI enhancer screen; may expose cleaner single-perturbation contracts",
    },
    {
        "priority": 32,
        "candidate_id": "papalexi2021_arrayed_rna",
        "source_study": "PapalexiSatija2021",
        "laboratory_group": "Papalexi_Satija",
        "cell_context_class": "THP1_immune_state_arrayed",
        "perturbation_mechanism": "arrayed_CRISPR_Cas9",
        "source_file": "PapalexiSatija2021_eccite_arrayed_RNA.h5ad",
        "rescue_reason": "small arrayed ECCITE-seq RNA file; same lab as ready THP1 but different experimental layout",
    },
    {
        "priority": 33,
        "candidate_id": "nadig2024_hepg2",
        "source_study": "NadigOConner2024",
        "laboratory_group": "Nadig_OConner",
        "cell_context_class": "HepG2_liver_cell_line",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "NadigOConner2024_hepg2.h5ad",
        "rescue_reason": "new laboratory and HepG2 context; screened as strong candidate for the tenth ready platform",
    },
    {
        "priority": 34,
        "candidate_id": "nadig2024_jurkat",
        "source_study": "NadigOConner2024",
        "laboratory_group": "Nadig_OConner",
        "cell_context_class": "Jurkat_T_cell",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "NadigOConner2024_jurkat.h5ad",
        "rescue_reason": "new laboratory Jurkat perturbation context; backup if HepG2 metadata fails",
    },
    {
        "priority": 35,
        "candidate_id": "lara2023_leukemia",
        "source_study": "LaraAstiasoHuntly2023",
        "laboratory_group": "Lara_Astiaso_Huntly",
        "cell_context_class": "leukemia_in_vivo",
        "perturbation_mechanism": "CRISPR_Cas9",
        "source_file": "LaraAstiasoHuntly2023_leukemia.h5ad",
        "rescue_reason": "disease-context counterpart to the ready Lara in-vivo bone-marrow platform; same-lab backup",
    },
]


def main() -> int:
    catalog = pd.read_csv(CATALOG, sep="\t").set_index("source_file")
    rows = []
    for row in SELECTED:
        source = catalog.loc[row["source_file"]]
        rows.append(
            {
                **row,
                "queue_role": "v3c_rescue_screen",
                "size_bytes": int(source["size_bytes"]),
                "source_url": source["source_url"],
                "source_md5": source["source_md5"],
                "expression_outcome_status": "not_scored_by_pgaa",
                "metadata_gate_status": "not_audited",
            }
        )
    out = pd.DataFrame(rows).sort_values("priority")
    out.to_csv(OUT, sep="\t", index=False)
    print(f"Wrote {len(out)} v3c rescue candidates to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
