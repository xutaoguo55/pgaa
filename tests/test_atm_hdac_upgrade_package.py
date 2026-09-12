from pathlib import Path

import pandas as pd

from pgaa.core.atm_hdac_upgrade_package import (
    build_author_request_rows,
    build_candidate_map,
    build_experiment_design,
    build_self_audit,
    build_source_data_audit,
    render_author_request_email,
    write_upgrade_package,
)


def test_source_data_audit_keeps_figure_only_boundary() -> None:
    audit = build_source_data_audit()

    assert "figure_only_for_drug_response" in set(audit["source_numerical_status"])
    assert "no_public_supplementary_files" in set(audit["source_numerical_status"])
    assert "gse335848_geo_ceiling" in set(audit["source_id"])
    assert "local_artifact" in audit.columns
    assert any(audit["missing_for_upgrade"].str.contains("Figure 4F"))


def test_author_request_fields_include_replicate_level_confluence() -> None:
    requests = build_author_request_rows()
    confluence = requests[
        requests["requested_table"].eq("PC9_Figure4F_confluence")
    ].iloc[0]

    assert "replicate" in confluence["minimum_fields"]
    assert "confluence" in confluence["minimum_fields"]
    assert confluence["preferred_format"] == "CSV, TSV, or XLSX"
    assert "plate_id" in confluence["shared_metadata"]
    assert "cell_line" in confluence["shared_metadata"]
    assert "osimertinib_concentration_nM" in confluence["shared_metadata"]


def test_author_request_uses_neutral_salutation() -> None:
    email = render_author_request_email(build_author_request_rows())

    assert "Dear GSE335846 authors," in email
    assert "Dear Dr." not in email
    assert "flat CSV, TSV, or XLSX table" in email
    assert "preferred format: CSV, TSV, or XLSX" in email
    assert "osimertinib_concentration_nM" in email


def test_candidate_map_keeps_atm_primary_and_hdac_secondary() -> None:
    drug_associations = pd.DataFrame(
        [
            {
                "drug": "AZD0156",
                "putative_target": "ATM",
                "spearman_rho": 1.0,
                "exact_one_sided_p": 1 / 24,
                "response_z_range": 2.1,
                "total_hit_calls": 3,
                "association_rank": 1,
            },
            {
                "drug": "Quisinostat",
                "putative_target": "HDAC",
                "spearman_rho": 0.8,
                "exact_one_sided_p": 1 / 6,
                "response_z_range": 2.3,
                "total_hit_calls": 1,
                "association_rank": 3,
            },
        ]
    )
    dynamic = pd.DataFrame(
        [{"spearman_rho": 1.0, "one_sided_exact_permutation_p": 1 / 24}]
    )

    candidate_map = build_candidate_map(drug_associations, dynamic)

    atm = candidate_map[candidate_map["target_class"].eq("ATM")].iloc[0]
    hdac = candidate_map[candidate_map["target_class"].eq("HDAC")].iloc[0]
    assert atm["candidate_role"] == "lead_dynamic_vulnerability"
    assert atm["evidence_state"] == "independent_dynamic_support"
    assert atm["claim_ceiling"] == "branch-specific preclinical therapeutic hypothesis"
    assert hdac["candidate_role"] == "secondary_branch_candidate"
    assert hdac["evidence_state"] == "screen_rank_support_followup_needed"
    assert hdac["claim_ceiling"] == "exploratory secondary branch-consistent candidate"


def test_experiment_design_predeclares_interaction_success_rule() -> None:
    design = build_experiment_design()

    assert design["minimum_biological_replicates"].min() == 4
    assert "analysis_unit" in design.columns
    assert "batch_control" in design.columns
    assert "sampling_schedule" in design.columns
    assert any(design["primary_analysis"].str.contains("branch_state:treatment_arm"))
    assert any(design["primary_analysis"].str.contains("linear mixed model"))
    assert any(design["batch_control"].str.contains("plate"))
    assert any(design["sampling_schedule"].str.contains("PC9 day 0/7/14/28"))
    assert any(design["sampling_schedule"].str.contains("HCC4006 bridge"))
    assert any(design["success_rule"].str.contains("concordant EdU"))


def test_self_audit_records_residual_atm_limitation() -> None:
    self_audit = build_self_audit()

    residual = self_audit[
        self_audit["residual_status"].eq("open_until_source_tables_or_prospective_experiment")
    ]
    assert not residual.empty
    assert any(self_audit["implemented_fix"].str.contains("claim ceilings"))


def test_write_package_resolves_relative_source_dir_against_output_dir(tmp_path) -> None:
    source_dir = tmp_path / "sources/gse335846_dynamic_atm"
    source_dir.mkdir(parents=True)
    for name in [
        "GSE335846_family.soft.gz",
        "preprint_733326.txt",
        "biorxiv_supplementary.html",
    ]:
        (source_dir / name).write_text(f"{name}\n", encoding="utf-8")

    gse193258_dir = tmp_path / "data/external/GSE193258"
    gse193258_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "Cell line": "PC9",
                "Drug": "AZD0156",
                "Dose (nM)": 10,
                "Putative Target": "ATM",
                "Screen format": "Upfront",
                "AUC osi. DTP control": 0.1,
                "AUC osi. DTP combo": 0.2,
                "AUC DMSO": 0.3,
                "AUC monotherapy": 0.4,
            }
        ]
    ).to_excel(gse193258_dir / "41698_2022_337_MOESM2_ESM.xlsx", index=False, startrow=2)
    pd.DataFrame(
        [
            {
                "Cell line": "PC9",
                "Drug ID": "AZD0156",
                "Putative target": "ATM",
                "Screen format": "upfront",
                "Avg. AUC DTP": 0.1,
                "Avg. AUC DTP Combination": 0.2,
                "Avg. AUC DMSO": 0.3,
                "Avg. AUC monotherapy": 0.4,
                "Combination activity": 1.2,
                "Monotherapy activity": 0.7,
                "Label": "hit",
                "Screen hit status": "hit",
            }
        ]
    ).to_excel(gse193258_dir / "41698_2022_337_MOESM3_ESM.xlsx", index=False, startrow=2)
    pd.DataFrame({"PC9_DMSO_1": [1.0]}, index=["gene1"]).to_csv(
        gse193258_dir / "GSE193258_RNAseq_log2TPM_abundance.tsv.gz", sep="\t"
    )

    drug_associations = pd.DataFrame(
        [
            {
                "drug": "AZD0156",
                "putative_target": "ATM",
                "spearman_rho": 1.0,
                "exact_one_sided_p": 1 / 24,
                "response_z_range": 2.1,
                "total_hit_calls": 3,
                "association_rank": 1,
            },
            {
                "drug": "Quisinostat",
                "putative_target": "HDAC",
                "spearman_rho": 0.8,
                "exact_one_sided_p": 1 / 6,
                "response_z_range": 2.3,
                "total_hit_calls": 1,
                "association_rank": 3,
            },
        ]
    )
    dynamic = pd.DataFrame(
        [{"spearman_rho": 1.0, "one_sided_exact_permutation_p": 1 / 24}]
    )

    paths = write_upgrade_package(
        output_dir=tmp_path,
        evidence_dir=tmp_path / "evidence",
        docs_dir=tmp_path / "docs",
        drug_associations=drug_associations,
        dynamic_association=dynamic,
        source_dir=Path("sources/gse335846_dynamic_atm"),
    )
    audit = pd.read_csv(paths["source_audit"], sep="\t")

    assert "present" in set(audit["local_artifact_status"])
    assert "missing" in set(audit["local_artifact_status"])
    assert "missing" in set(audit["local_sha256"])
    present_sha = audit.loc[audit["local_artifact_status"].eq("present"), "local_sha256"]
    assert present_sha.str.fullmatch(r"[0-9a-f]{64}").all()
    assert not any(Path(value).is_absolute() for value in audit["local_artifact"])


def test_write_package_includes_gse193258_source_audit(tmp_path) -> None:
    source_dir = tmp_path / "sources/gse335846_dynamic_atm"
    source_dir.mkdir(parents=True)
    for name in [
        "GSE335846_family.soft.gz",
        "preprint_733326.txt",
        "biorxiv_supplementary.html",
    ]:
        (source_dir / name).write_text(f"{name}\n", encoding="utf-8")

    gse193258_dir = tmp_path / "data/external/GSE193258"
    gse193258_dir.mkdir(parents=True)
    replicate = pd.DataFrame(
        [
            {
                "Cell line": "PC9",
                "Drug": "AZD0156",
                "Dose (nM)": 10,
                "Putative Target": "ATM",
                "Screen format": "Upfront",
                "AUC osi. DTP control": 0.1,
                "AUC osi. DTP combo": 0.2,
                "AUC DMSO": 0.3,
                "AUC monotherapy": 0.4,
            },
            {
                "Cell line": "PC9",
                "Drug": "Quisinostat",
                "Dose (nM)": 10,
                "Putative Target": "HDAC",
                "Screen format": "Upfront",
                "AUC osi. DTP control": 0.15,
                "AUC osi. DTP combo": 0.25,
                "AUC DMSO": 0.35,
                "AUC monotherapy": 0.45,
            }
        ]
    )
    summary = pd.DataFrame(
        [
            {
                "Cell line": "PC9",
                "Drug ID": "AZD0156",
                "Putative target": "ATM",
                "Screen format": "upfront",
                "Avg. AUC DTP": 0.1,
                "Avg. AUC DTP Combination": 0.2,
                "Avg. AUC DMSO": 0.3,
                "Avg. AUC monotherapy": 0.4,
                "Combination activity": 1.2,
                "Monotherapy activity": 0.7,
                "Label": "hit",
                "Screen hit status": "hit",
            },
            {
                "Cell line": "PC9",
                "Drug ID": "Quisinostat",
                "Putative target": "HDAC",
                "Screen format": "upfront",
                "Avg. AUC DTP": 0.15,
                "Avg. AUC DTP Combination": 0.25,
                "Avg. AUC DMSO": 0.35,
                "Avg. AUC monotherapy": 0.45,
                "Combination activity": 1.3,
                "Monotherapy activity": 0.8,
                "Label": "hit",
                "Screen hit status": "hit",
            }
        ]
    )
    rnaseq = pd.DataFrame({"PC9_DMSO_1": [1.0]}, index=["gene1"])
    replicate.to_excel(gse193258_dir / "41698_2022_337_MOESM2_ESM.xlsx", index=False, startrow=2)
    summary.to_excel(gse193258_dir / "41698_2022_337_MOESM3_ESM.xlsx", index=False, startrow=2)
    rnaseq.to_csv(gse193258_dir / "GSE193258_RNAseq_log2TPM_abundance.tsv.gz", sep="\t")

    drug_associations = pd.DataFrame(
        [
            {
                "drug": "AZD0156",
                "putative_target": "ATM",
                "spearman_rho": 1.0,
                "exact_one_sided_p": 1 / 24,
                "response_z_range": 2.1,
                "total_hit_calls": 3,
                "association_rank": 1,
            },
            {
                "drug": "Quisinostat",
                "putative_target": "HDAC",
                "spearman_rho": 0.8,
                "exact_one_sided_p": 1 / 6,
                "response_z_range": 2.3,
                "total_hit_calls": 1,
                "association_rank": 3,
            },
        ]
    )
    dynamic = pd.DataFrame(
        [{"spearman_rho": 1.0, "one_sided_exact_permutation_p": 1 / 24}]
    )

    paths = write_upgrade_package(
        output_dir=tmp_path,
        evidence_dir=tmp_path / "evidence",
        docs_dir=tmp_path / "docs",
        drug_associations=drug_associations,
        dynamic_association=dynamic,
        source_dir=Path("sources/gse335846_dynamic_atm"),
        gse193258_source_dir=Path("data/external/GSE193258"),
    )

    audit = pd.read_csv(paths["gse193258_source_audit"], sep="\t")
    target_context = pd.read_csv(paths["gse193258_target_context"], sep="\t")
    specificity = pd.read_csv(paths["gse193258_target_specificity"], sep="\t")
    contrast = pd.read_csv(paths["gse193258_target_specificity_contrast"], sep="\t")
    assert paths["gse193258_source_audit_doc"].exists()
    assert paths["gse193258_target_specificity_doc"].exists()
    assert paths["gse193258_target_specificity_figure"].exists()
    assert paths["gse193258_target_specificity_figure"].stat().st_size > 0
    assert paths["gse193258_target_specificity_caption"].exists()
    assert paths["gse193258_target_specificity_caption"].read_text(encoding="utf-8").startswith(
        "# GSE193258 Target Specificity Figure Support Text"
    )
    assert "GSE193258_RNAseq" in set(audit["table_id"])
    assert {"ATM", "HDAC"}.issubset(set(target_context["target_class"]))
    assert "ATM" in set(specificity["target_class"])
    assert int(contrast.iloc[0]["exact_significant_positive_count"]) >= 1
    assert set(audit["local_artifact_status"]) == {"present"}
