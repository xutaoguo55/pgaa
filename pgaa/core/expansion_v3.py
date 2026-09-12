"""Frozen result-blind registry for expansion-v3 external platforms."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.cross_platform_dual_gate import PlatformSpec
from pgaa.core.data_root import data_root


DEFAULT_USB_ROOT = data_root("pgaa_cross_platform")


def load_frozen_v3_candidate_queue(root: Path | None = None) -> pd.DataFrame:
    project_root = root or Path(__file__).resolve().parents[2]
    return (
        pd.read_csv(project_root / "evidence/expansion_v3_candidate_queue.tsv", sep="\t")
        .sort_values("priority")
        .reset_index(drop=True)
    )


def load_frozen_v3b_candidate_queue(root: Path | None = None) -> pd.DataFrame:
    project_root = root or Path(__file__).resolve().parents[2]
    return (
        pd.read_csv(project_root / "evidence/expansion_v3b_rescue_candidate_queue.tsv", sep="\t")
        .sort_values("priority")
        .reset_index(drop=True)
    )


def load_frozen_v3c_candidate_queue(root: Path | None = None) -> pd.DataFrame:
    project_root = root or Path(__file__).resolve().parents[2]
    return (
        pd.read_csv(project_root / "evidence/expansion_v3c_rescue_candidate_queue.tsv", sep="\t")
        .sort_values("priority")
        .reset_index(drop=True)
    )


def _source_paths(manifest_name: str) -> dict[str, Path]:
    manifest_path = Path(__file__).resolve().parents[2] / "evidence" / manifest_name
    if not manifest_path.is_file():
        return {}
    manifest = pd.read_csv(manifest_path, sep="\t")
    return {
        str(row["candidate_id"]): Path(str(row["resolved_source_path"]))
        for _, row in manifest.iterrows()
    }


def _v3b_path(candidate_id: str, source_file: str) -> Path:
    return DEFAULT_USB_ROOT / "v3b" / "sources" / candidate_id / source_file


def _v3c_path(candidate_id: str, source_file: str) -> Path:
    return DEFAULT_USB_ROOT / "v3c" / "sources" / candidate_id / source_file


def frozen_v3_candidate_specs(root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return frozen metadata adapters for the v3 candidate queue.

    These specs are result-blind: they use only source paths and observation
    metadata fields audited before expression scoring.
    """
    paths = _source_paths("expansion_v3_source_manifest.tsv")
    return (
        PlatformSpec(
            "papalexi2021_thp1_crispr",
            "Human THP-1 ECCITE-seq CRISPR screen",
            paths["papalexi2021_thp1_crispr"],
            "single_gene_nperts",
            "hto",
            None,
            "log1p_1e4",
            "recorded_hash_tag_holdout_5_levels",
        ),
        PlatformSpec(
            "frangieh2021_melanoma_crispr",
            "Human melanoma CRISPR perturb-seq",
            paths["frangieh2021_melanoma_crispr"],
            "single_gene_nperts",
            "MOI",
            None,
            "log1p_1e4",
            "recorded_moi_holdout_20_levels",
        ),
        PlatformSpec(
            "joung2023_hesc_tf_overexpression",
            "Human hESC TF overexpression",
            paths["joung2023_hesc_tf_overexpression"],
            "generic_condition",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_9_levels",
            analysis_unit_columns=("perturbation",),
            control_column="TF",
            control_values=("TFORF3549-GFP",),
        ),
        PlatformSpec(
            "xu2023_hek293_crispri",
            "Human HEK293 CRISPRi screen",
            paths["xu2023_hek293_crispri"],
            "single_gene_nperts",
            "guide_id",
            None,
            "log1p_1e4",
            "recorded_guide_holdout_489_levels",
        ),
        PlatformSpec(
            "zhao2021_glioblastoma_drug",
            "Human glioblastoma drug perturbation",
            paths["zhao2021_glioblastoma_drug"],
            "generic_condition",
            "library",
            None,
            "log1p_1e4",
            "recorded_library_holdout_43_levels",
            analysis_unit_columns=("perturbation", "dose_value"),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "aissa2021_pc9_drug",
            "Human PC9 xenograft drug perturbation",
            paths["aissa2021_pc9_drug"],
            "generic_condition",
            "batch",
            None,
            "log1p_1e4",
            "single_recorded_batch",
            analysis_unit_columns=("perturbation",),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "lotfollahi2023_perturbation_atlas",
            "Human A549 perturbation atlas",
            paths["lotfollahi2023_perturbation_atlas"],
            "single_gene_nperts",
            "RT_well",
            None,
            "log1p_1e4",
            "recorded_well_holdout_96_levels",
        ),
        PlatformSpec(
            "weinreb2020_hematopoietic_cytokine",
            "Mouse hematopoietic cytokine perturbation",
            paths["weinreb2020_hematopoietic_cytokine"],
            "generic_condition",
            "library_names",
            None,
            "log1p_1e4",
            "recorded_library_holdout_29_levels",
            analysis_unit_columns=("perturbation", "celltype"),
            control_stratum_columns=("celltype",),
            control_column="perturbation",
            control_values=("full cocktail",),
        ),
        PlatformSpec(
            "xie2017_stem_cell_perturbation",
            "Mouse stem-cell genetic perturbation",
            paths["xie2017_stem_cell_perturbation"],
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_16_levels",
        ),
        PlatformSpec(
            "gehring2019_neural_stem_drug",
            "Mouse neural stem-cell drug perturbation",
            paths["gehring2019_neural_stem_drug"],
            "generic_condition",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_4_levels",
            analysis_unit_columns=("perturbation",),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "gasperini2019_k562_enhancer_crispr",
            "Human K562 enhancer CRISPRi high-MOI screen",
            paths["gasperini2019_k562_enhancer_crispr"],
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_6_levels",
        ),
        PlatformSpec(
            "schraivogel2020_k562_tapseq",
            "Human K562 TAP-seq perturbation screen",
            paths["schraivogel2020_k562_tapseq"],
            "single_gene_nperts",
            "replicate",
            None,
            "log1p_1e4",
            "recorded_replicate_holdout_13_levels",
        ),
        PlatformSpec(
            "dixit2016_k562_tf_crispr",
            "Human K562 TF CRISPR perturb-seq",
            paths["dixit2016_k562_tf_crispr"],
            "generic_condition",
            "guide_id",
            None,
            "log1p_1e4",
            "recorded_guide_holdout_30_levels",
            analysis_unit_columns=("target",),
            control_column="perturbation",
            control_values=("control", "nan"),
        ),
        PlatformSpec(
            "chang2021_pc9_drug",
            "Human PC9 drug perturbation",
            paths["chang2021_pc9_drug"],
            "generic_condition",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_4_levels",
            analysis_unit_columns=("perturbation", "dose_value"),
            control_column="perturbation",
            control_values=("control",),
        ),
    )


def frozen_v3b_rescue_specs(root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return frozen metadata adapters for the v3b rescue queue.

    The rescue specs are source/metadata-only definitions. They are not
    promoted by expression outcomes; every candidate remains subject to the
    same selected-unit gate in the contract compiler.
    """
    queue = load_frozen_v3b_candidate_queue()
    source_files = queue.set_index("candidate_id")["source_file"].astype(str).to_dict()
    paths = _source_paths("expansion_v3b_source_manifest.tsv")

    def path(candidate_id: str) -> Path:
        return paths.get(candidate_id, _v3b_path(candidate_id, source_files[candidate_id]))

    return (
        PlatformSpec(
            "datlinger2021_jurkat_crispr",
            "Human Jurkat T-cell CRISPR plus stimulation",
            path("datlinger2021_jurkat_crispr"),
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_384_levels",
        ),
        PlatformSpec(
            "srivatsan2020_sciplex2",
            "Human A549 SciPlex-2 drug perturbation",
            path("srivatsan2020_sciplex2"),
            "generic_condition",
            "well",
            None,
            "log1p_1e4",
            "recorded_well_holdout_192_levels",
            analysis_unit_columns=("perturbation", "dose_value"),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "srivatsan2020_sciplex4",
            "Human A549 SciPlex-4 drug perturbation",
            path("srivatsan2020_sciplex4"),
            "generic_condition",
            "well",
            None,
            "log1p_1e4",
            "recorded_well_holdout",
            analysis_unit_columns=("perturbation", "dose_value"),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "tian2019_ipsc_crispri",
            "Human iPSC CRISPRi screen",
            path("tian2019_ipsc_crispri"),
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_2_levels",
        ),
        PlatformSpec(
            "tian2021_crispri",
            "Human iPSC-derived neuron CRISPRi screen",
            path("tian2021_crispri"),
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_4_levels",
        ),
        PlatformSpec(
            "adamson2016_10x001",
            "Human K562 CRISPRi stress-response screen 10X001",
            path("adamson2016_10x001"),
            "single_gene_nperts",
            "perturbation",
            None,
            "log1p_1e4",
            "recorded_perturbation_holdout",
        ),
        PlatformSpec(
            "adamson2016_10x005",
            "Human K562 CRISPRi stress-response screen 10X005",
            path("adamson2016_10x005"),
            "single_gene_nperts",
            "perturbation",
            None,
            "log1p_1e4",
            "recorded_perturbation_holdout",
        ),
        PlatformSpec(
            "norman2019_k562_crispra",
            "Human K562 CRISPRa perturb-seq",
            path("norman2019_k562_crispra"),
            "single_gene_nperts",
            "gemgroup",
            None,
            "log1p_1e4",
            "recorded_gemgroup_holdout_8_levels",
        ),
        PlatformSpec(
            "replogle2022_rpe1_crispri",
            "Human RPE1 CRISPRi perturb-seq",
            path("replogle2022_rpe1_crispri"),
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout_56_levels",
        ),
        PlatformSpec(
            "lara2023_bone_marrow_invivo",
            "Mouse in vivo bone-marrow CRISPR-Cas9 perturbation",
            path("lara2023_bone_marrow_invivo"),
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_12_levels",
        ),
        PlatformSpec(
            "schiebinger2019_reprogramming_gse106340",
            "Mouse reprogramming 2i state-transition perturbation",
            path("schiebinger2019_reprogramming_gse106340"),
            "generic_condition",
            "GSM",
            None,
            "log1p_1e4",
            "recorded_gsm_holdout_22_levels",
            analysis_unit_columns=("perturbation", "age"),
            control_stratum_columns=("age",),
            control_column="perturbation",
            control_values=("control",),
        ),
        PlatformSpec(
            "schraivogel2020_k562_tapseq_chr8",
            "Human K562 TAP-seq chromosome 8 CRISPR screen",
            path("schraivogel2020_k562_tapseq_chr8"),
            "single_gene_nperts",
            "replicate",
            None,
            "log1p_1e4",
            "recorded_replicate_holdout_14_levels",
        ),
    )


def frozen_v3c_rescue_specs(root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return frozen metadata adapters for the v3c rescue queue."""
    queue = load_frozen_v3c_candidate_queue()
    source_files = queue.set_index("candidate_id")["source_file"].astype(str).to_dict()
    paths = _source_paths("expansion_v3c_source_manifest.tsv")

    def path(candidate_id: str) -> Path:
        return paths.get(candidate_id, _v3c_path(candidate_id, source_files[candidate_id]))

    return (
        PlatformSpec(
            "datlinger2017_jurkat_crispr",
            "Human Jurkat T-cell CRISPR plus stimulation",
            path("datlinger2017_jurkat_crispr"),
            "datlinger2017",
            "replicate",
            None,
            "log1p_1e4",
            "recorded_replicate_holdout_6_levels",
        ),
        PlatformSpec(
            "dixit2016_k562_tf_7d",
            "Human K562 TF CRISPR perturb-seq 7 days",
            path("dixit2016_k562_tf_7d"),
            "generic_condition",
            "guide_id",
            None,
            "log1p_1e4",
            "recorded_guide_holdout_30_levels",
            analysis_unit_columns=("target",),
            control_column="perturbation",
            control_values=("control", "nan"),
        ),
        PlatformSpec(
            "dixit2016_k562_tf_high_moi",
            "Human K562 TF CRISPR perturb-seq high MOI",
            path("dixit2016_k562_tf_high_moi"),
            "generic_condition",
            "guide_id",
            None,
            "log1p_1e4",
            "recorded_guide_holdout_1728_levels",
            analysis_unit_columns=("target",),
            control_column="perturbation",
            control_values=("control", "nan"),
        ),
        PlatformSpec(
            "adamson2016_10x010",
            "Human K562 CRISPRi stress-response screen 10X010",
            path("adamson2016_10x010"),
            "single_gene_nperts",
            "perturbation",
            None,
            "log1p_1e4",
            "recorded_perturbation_holdout",
        ),
        PlatformSpec(
            "gasperini2019_lowmoi",
            "Human K562 low-MOI enhancer CRISPRi screen",
            path("gasperini2019_lowmoi"),
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout_6_levels",
        ),
        PlatformSpec(
            "papalexi2021_arrayed_rna",
            "Human THP-1 arrayed ECCITE-seq CRISPR RNA",
            path("papalexi2021_arrayed_rna"),
            "single_gene_nperts",
            "hto",
            None,
            "log1p_1e4",
            "recorded_hash_tag_holdout_15_levels",
        ),
        PlatformSpec(
            "nadig2024_hepg2",
            "Human HepG2 CRISPR perturbation screen",
            path("nadig2024_hepg2"),
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout",
        ),
        PlatformSpec(
            "nadig2024_jurkat",
            "Human Jurkat CRISPR perturbation screen",
            path("nadig2024_jurkat"),
            "single_gene_nperts",
            "batch",
            None,
            "log1p_1e4",
            "recorded_batch_holdout",
        ),
        PlatformSpec(
            "lara2023_leukemia",
            "Mouse leukemia in vivo CRISPR-Cas9 perturbation",
            path("lara2023_leukemia"),
            "single_gene_nperts",
            "sample",
            None,
            "log1p_1e4",
            "recorded_sample_holdout",
        ),
    )


def frozen_v3_ready_specs(root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return specs that passed the frozen metadata contract status file."""
    status_path = Path(__file__).resolve().parents[2] / "evidence/expansion_v3_platform_contract_status.tsv"
    status = pd.read_csv(status_path, sep="\t").set_index("candidate_id")
    ready = set(status.index[status["contract_status"].eq("ready_for_scoring")])
    return tuple(spec for spec in frozen_v3_candidate_specs(root) if spec.dataset_id in ready)


def frozen_v3_combined_ready_specs(root: Path = DEFAULT_USB_ROOT) -> tuple[PlatformSpec, ...]:
    """Return all v3/v3b/v3c specs that passed their frozen metadata contracts."""
    combined_status = (
        pd.read_csv(
            Path(__file__).resolve().parents[2]
            / "evidence/expansion_v3_combined_ready_panel.tsv",
            sep="\t",
        )
        .sort_values(["expansion_queue", "priority"])
        .reset_index(drop=True)
    )
    ready_ids = combined_status["candidate_id"].astype(str).tolist()
    by_id = {
        spec.dataset_id: spec
        for spec in (
            *frozen_v3_candidate_specs(root),
            *frozen_v3b_rescue_specs(root),
            *frozen_v3c_rescue_specs(root),
        )
    }
    missing = sorted(set(ready_ids) - set(by_id))
    if missing:
        raise ValueError(f"combined ready panel lacks specs for: {missing}")
    return tuple(by_id[dataset_id] for dataset_id in ready_ids)
