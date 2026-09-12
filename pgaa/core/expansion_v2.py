"""Frozen platform registry for the ten-study dual-gate expansion."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.cross_platform_dual_gate import PlatformSpec
from pgaa.core.data_root import data_root


DEFAULT_USB_ROOT = data_root("pgaa_cross_platform/v2")


def load_frozen_candidate_queue(root: Path | None = None) -> pd.DataFrame:
    """Load the original result-blind queue plus every frozen queue amendment."""
    project_root = root or Path(__file__).resolve().parents[2]
    evidence = project_root / "evidence"
    paths = [evidence / "expansion_v2_candidate_queue.tsv"]
    paths.extend(sorted(evidence.glob("expansion_v2_candidate_queue_amendment_*.tsv")))
    queue = pd.concat((pd.read_csv(path, sep="\t") for path in paths), ignore_index=True)
    if queue["candidate_id"].duplicated().any():
        duplicates = sorted(queue.loc[queue["candidate_id"].duplicated(), "candidate_id"].unique())
        raise ValueError(f"duplicate candidate IDs in frozen queues: {duplicates}")
    return queue.sort_values("priority").reset_index(drop=True)


def frozen_ready_specs(usb_root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return result-blind specifications whose metadata contracts are established."""
    source = usb_root / "sources"
    return (
        PlatformSpec(
            "cui2023_lymph_node_cytokine",
            "Primary lymph-node immune cells, cytokine stimulation",
            source / "cui2023_lymph_node_cytokine/CuiHacohen2023.h5ad",
            "generic_condition",
            "bio_replicate",
            None,
            "log1p_1e4",
            "biological_replicate_holdout_7_vs_7",
            analysis_unit_columns=("celltype", "perturbation"),
            control_stratum_columns=("celltype",),
            control_column="nperts",
            control_values=("0",),
        ),
        PlatformSpec(
            "liang2023_liver_organoid_crispr",
            "Mouse liver organoid CRISPR-Cas9",
            source / "liang2023_liver_organoid_crispr/LiangWang2023.h5ad",
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_4_vs_5",
        ),
        PlatformSpec(
            "santinha2023_brain_aav_crispr",
            "Mouse in vivo brain AAV CRISPR-Cas9",
            source / "santinha2023_brain_aav_crispr/SantinhaPlatt2023.h5ad",
            "single_gene_nperts",
            "lane",
            None,
            "log1p_1e4",
            "recorded_sequencing_lane_holdout_6_vs_6",
        ),
        PlatformSpec(
            "shifrut2018_primary_t_crispr",
            "Primary human T-cell CRISPR-Cas9",
            source / "shifrut2018_primary_t_crispr/ShifrutMarson2018.h5ad",
            "single_gene_nperts",
            "patient",
            None,
            "log1p_1e4",
            "donor_holdout_1_vs_1",
        ),
        PlatformSpec(
            "sunshine2023_calu3_crispri",
            "Human Calu-3 epithelial CRISPRi",
            source / "sunshine2023_calu3_crispri/SunshineHein2023.h5ad",
            "single_gene_nperts",
            "gem_group",
            None,
            "log1p_1e4",
            "recorded_gem_group_holdout_4_vs_4",
        ),
        PlatformSpec(
            "tian2021_ipsc_neuron_crispra",
            "Human iPSC-derived neuron CRISPRa",
            source / "tian2021_ipsc_neuron_crispra/TianKampmann2021_CRISPRa.h5ad",
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "experimental_batch_holdout_1_vs_1",
        ),
        PlatformSpec(
            "wessels2023_myeloid_cas13",
            "Human myeloid-cell CRISPR-Cas13",
            source / "wessels2023_myeloid_cas13/WesselsSatija2023.h5ad",
            "single_gene_nperts",
            "HTO",
            None,
            "log1p_1e4",
            "sample_tag_holdout_4_vs_4",
        ),
        PlatformSpec(
            "lara2023_bone_marrow_crispr",
            "Mouse bone-marrow transplant CRISPR-Cas9",
            source / "lara2023_bone_marrow_crispr/LaraAstiasoHuntly2023_exvivo.h5ad",
            "single_gene_nperts",
            "time",
            None,
            "log1p_1e4",
            "recorded_timepoint_holdout_1_vs_1",
        ),
        PlatformSpec(
            "mcfarland2020_cancer_mixseq_drug",
            "Human multi-lineage cancer Mix-seq drug panel",
            source / "mcfarland2020_cancer_mixseq_drug/McFarlandTsherniak2020.h5ad",
            "generic_condition",
            "time",
            None,
            "log1p_1e4",
            "treatment_time_holdout_1_vs_1",
            obs_filters=(("cell_quality", "normal"), ("perturbation_type", "drug")),
            obs_value_sets=(("time", ("6", "24")),),
            analysis_unit_columns=("cell_line", "perturbation", "dose_value"),
            control_stratum_columns=("cell_line",),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "schiebinger2019_mesc_cytokine",
            "Mouse embryonic stem-cell state transition",
            source / "schiebinger2019_mesc_cytokine/SchiebingerLander2019_GSE115943.h5ad",
            "generic_condition",
            "replicate",
            None,
            "log1p_1e4",
            "biological_replicate_holdout_1_vs_1",
            analysis_unit_columns=("perturbation", "age"),
            control_stratum_columns=("age",),
            control_column="perturbation",
            control_values=("control",),
        ),
    )
