"""Build the ATM/HDAC branch-vulnerability upgrade package."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from pgaa.core.gse193258_drug_screen_source_audit import (
    build_gse193258_drug_screen_source_audit,
    write_gse193258_drug_screen_source_audit_package,
)
from pgaa.core.gse193258_target_specificity_audit import (
    write_gse193258_target_specificity_audit_package,
)


def _sha256_or_na(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# Rows whose `local_artifact` is a descriptor for a public resource rather than
# a filesystem path. They have no local file to hash, so a path check would
# report them as "missing" forever.
NON_PATH_LOCAL_ARTIFACTS = frozenset({"official_geo_viewer"})
NOT_APPLICABLE_STATUS = "not_applicable_public_ceiling"


def annotate_local_artifacts(audit: pd.DataFrame, root: Path) -> None:
    """Fill the local_artifact_* columns in place.

    Path-valued rows get present/missing; descriptor rows get
    NOT_APPLICABLE_STATUS and a "not_applicable" digest instead of a bogus
    "missing". Relative paths resolve against `root`.
    """
    status: list[str] = []
    digest: list[str] = []
    display: list[str] = []
    for value in audit["local_artifact"].tolist():
        if value in NON_PATH_LOCAL_ARTIFACTS:
            status.append(NOT_APPLICABLE_STATUS)
            digest.append("not_applicable")
            display.append(value)
            continue
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        status.append("present" if path.exists() else "missing")
        digest.append(_sha256_or_na(path))
        display.append(_display_path(path, root))
    audit["local_artifact_status"] = status
    audit["local_sha256"] = digest
    audit["local_artifact"] = display


def build_source_data_audit(source_dir: Path | None = None) -> pd.DataFrame:
    """Summarize whether public GSE335846 materials expose figure source values."""
    source_dir = source_dir or Path("sources/gse335846_dynamic_atm")
    rows = [
        {
            "source_id": "gse335846_geo_family",
            "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE335846",
            "local_artifact": str(source_dir / "GSE335846_family.soft.gz"),
            "public_item_checked": "GEO family metadata and supplementary-file fields",
            "observed_public_data": "Series supplementary file lists GSE335846_RNA-seq_for_GEO.txt.gz; sample supplementary files are NONE.",
            "source_numerical_status": "rna_seq_source_table_available_for_branch_axis",
            "usable_for_current_analysis": "branch_induction",
            "missing_for_upgrade": "Figure 3B replication-origin polarity and Figure 4F confluence source values.",
        },
        {
            "source_id": "gse335846_branch_axis_projection",
            "source_url": "local_projection",
            "local_artifact": "evidence/gse335846_rna_seq_branch_axis_scores.tsv",
            "public_item_checked": "fixed-axis projection of the RNA-seq source table",
            "observed_public_data": "The public GSE335846 RNA-seq source table can be projected onto the frozen GSE249721 branch axis without re-ranking genes.",
            "source_numerical_status": "fixed_branch_axis_projection_available",
            "usable_for_current_analysis": "source_axis_projection",
            "missing_for_upgrade": "Dynamic drug-response source tables for confluence, EdU, and regrowth remain missing.",
        },
        {
            "source_id": "gse335848_superseries",
            "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE335848",
            "local_artifact": str(source_dir / "preprint_733326.txt"),
            "public_item_checked": "preprint data availability accession",
            "observed_public_data": "The preprint data-availability statement points to GSE335848.",
            "source_numerical_status": "geo_accession_available",
            "usable_for_current_analysis": "public_accession_trace",
            "missing_for_upgrade": "Official GEO viewer for GSE335848 states that supplementary data files are not provided, so drug-combination source tables are not public.",
        },
        {
            "source_id": "gse335848_geo_ceiling",
            "source_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE335848",
            "local_artifact": "official_geo_viewer",
            "public_item_checked": "accession viewer supplementary-data statement",
            "observed_public_data": "The official GEO accession viewer states that supplementary data files are not provided.",
            "source_numerical_status": "no_public_supplementary_files",
            "usable_for_current_analysis": "source_ceiling_trace",
            "missing_for_upgrade": "Replicate-level dynamic drug-response tables are not publicly available.",
        },
        {
            "source_id": "biorxiv_preprint_v1",
            "source_url": "https://doi.org/10.64898/2026.06.19.733326",
            "local_artifact": str(source_dir / "biorxiv_supplementary.html"),
            "public_item_checked": "full text, figure legends, supplementary-material page",
            "observed_public_data": "Figure legends report n=3 and statistical tests for PC9/HCC4006 confluence, EdU, and regrowth, but no downloadable CSV/XLSX source-data table was found.",
            "source_numerical_status": "figure_only_for_drug_response",
            "usable_for_current_analysis": "rank_level_digitization",
            "missing_for_upgrade": "Underlying time-point replicate values for confluence, EdU, regrowth, and replication-origin polarity.",
        },
    ]
    return pd.DataFrame(rows)


def build_author_request_rows() -> pd.DataFrame:
    """Define the exact numerical fields needed from the GSE335846 authors."""
    rows = [
        {
            "requested_table": "PC9_Figure3B_replication_polarity",
            "minimum_fields": "day, replicate, initiation_zone_id_or_bin, polarity_or_directionality_metric",
            "preferred_format": "CSV, TSV, or XLSX",
            "shared_metadata": "cell_line, sample_id, plate_id, passage_number, treatment_state, osimertinib_concentration_nM, normalization_method",
            "purpose": "replace figure-digitized replication-branch strength with source numerical values",
        },
        {
            "requested_table": "PC9_Figure4F_confluence",
            "minimum_fields": "day, replicate, treatment, confluence_percent_or_normalized_cell_number",
            "preferred_format": "CSV, TSV, or XLSX",
            "shared_metadata": "cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, imaging_timepoint",
            "purpose": "test branch-strength versus AZD1390 added benefit using replicate-level values",
        },
        {
            "requested_table": "PC9_Figure4G_EdU",
            "minimum_fields": "day, replicate, treatment, edu_positive_fraction",
            "preferred_format": "CSV, TSV, or XLSX",
            "shared_metadata": "cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, EdU_pulse_hours",
            "purpose": "triangulate ATM benefit with replication-readout suppression",
        },
        {
            "requested_table": "PC9_Figure4H_regrowth",
            "minimum_fields": "withdrawal_day, replicate, treatment, time_to_100_percent_confluence_or_auc",
            "preferred_format": "CSV, TSV, or XLSX",
            "shared_metadata": "cell_line, sample_id, plate_id, withdrawal_day, passage_number, post_withdrawal_observation_window, osimertinib_concentration_nM",
            "purpose": "test whether branch strength predicts delayed resistance regrowth",
        },
        {
            "requested_table": "HCC4006_SupplementaryFigure4B_D",
            "minimum_fields": "day, replicate, treatment, confluence_or_edu_or_regrowth_metric",
            "preferred_format": "CSV, TSV, or XLSX",
            "shared_metadata": "cell_line, sample_id, plate_id, passage_number, treatment_dose, osimertinib_concentration_nM, assay_label",
            "purpose": "check whether the PC9 dynamic gradient generalizes to a second EGFR-mutant line",
        },
    ]
    return pd.DataFrame(rows)


def build_experiment_design() -> pd.DataFrame:
    """Specify a prospective branch-stratified ATM dose-response experiment."""
    rows = []
    for branch_state, branch_rule in [
        ("branch_weak", "early DTP or low frozen adaptive-stress score"),
        ("branch_strong", "late DTP or high frozen adaptive-stress score"),
    ]:
        for treatment in [
            "DMSO",
            "osimertinib",
            "osimertinib_plus_AZD1390",
            "osimertinib_plus_AZD0156",
            "osimertinib_plus_quisinostat",
        ]:
            rows.append(
                {
                    "branch_state": branch_state,
                    "branch_assignment_rule": branch_rule,
                    "treatment_arm": treatment,
                    "analysis_unit": "biological replicate nested within branch state and treatment arm",
                    "dose_strategy": "matrix dose-response for ATM arms; matched low-nontoxic dose for HDAC secondary arm",
                    "batch_control": "balance branch_state across plate, passage, and experiment day",
                    "sampling_schedule": "PC9 day 0/7/14/28 with regrowth follow-up after withdrawal; HCC4006 bridge at day 0/3/7/14",
                    "minimum_biological_replicates": 4,
                    "primary_endpoint": "added benefit over osimertinib in confluence or viable-cell area under curve",
                    "mechanistic_endpoints": "EdU, gammaH2AX, phospho-KAP1, phospho-RPA, regrowth after withdrawal",
                    "positive_prediction": "ATM added benefit is larger in branch_strong than branch_weak states",
                    "primary_analysis": "linear mixed model with branch_state, treatment_arm, and branch_state:treatment_arm interaction; add plate or experiment_day random intercepts when pooled; report interaction effect size and confidence interval",
                    "success_rule": "positive ATM interaction for AZD1390 or AZD0156 plus concordant EdU or DNA-damage marker direction on at least one mechanistic readout",
                }
            )
    return pd.DataFrame(rows)


def build_candidate_map(
    drug_associations: pd.DataFrame,
    dynamic_association: pd.DataFrame,
) -> pd.DataFrame:
    """Combine GSE193258 drug associations with the fifth-system ATM result."""
    required = {"drug", "putative_target", "spearman_rho", "exact_one_sided_p"}
    missing = required.difference(drug_associations.columns)
    if missing:
        raise ValueError(f"Missing drug-association columns: {sorted(missing)}")
    dynamic_required = {"spearman_rho", "one_sided_exact_permutation_p"}
    dynamic_missing = dynamic_required.difference(dynamic_association.columns)
    if dynamic_missing:
        raise ValueError(f"Missing dynamic-association columns: {sorted(dynamic_missing)}")

    rows = []
    atm_dynamic = dynamic_association.iloc[0]
    for target, role in [("ATM", "lead_dynamic_vulnerability"), ("HDAC", "secondary_branch_candidate")]:
        subset = drug_associations[drug_associations["putative_target"].eq(target)]
        if subset.empty:
            continue
        row = subset.sort_values(["association_rank"]).iloc[0]
        rows.append(
            {
                "candidate_role": role,
                "target_class": target,
                "lead_drug": row["drug"],
                "gse193258_spearman_rho": float(row["spearman_rho"]),
                "gse193258_exact_p": float(row["exact_one_sided_p"]),
                "gse193258_response_z_range": float(row.get("response_z_range", 0.0)),
                "gse193258_total_hit_calls": int(row.get("total_hit_calls", 0)),
                "gse335846_dynamic_rho": float(atm_dynamic["spearman_rho"]) if target == "ATM" else float("nan"),
                "gse335846_dynamic_exact_p": float(atm_dynamic["one_sided_exact_permutation_p"]) if target == "ATM" else float("nan"),
                "evidence_state": "independent_dynamic_support" if target == "ATM" else "screen_rank_support_followup_needed",
                "manuscript_use": "primary demonstration case" if target == "ATM" else "secondary branch-consistent candidate",
                "claim_ceiling": (
                    "branch-specific preclinical therapeutic hypothesis"
                    if target == "ATM"
                    else "exploratory secondary branch-consistent candidate"
                ),
                "next_upgrade": (
                    "source replicate tables or prospective branch-by-treatment experiment"
                    if target == "ATM"
                    else "independent dynamic or perturbational validation before main-text promotion"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_self_audit() -> pd.DataFrame:
    """Record objective weaknesses and the implemented correction."""
    rows = [
        {
            "issue": "Language overstated prediction-to-phenotype closure.",
            "severity": "important",
            "risk": "Readers could infer validation stronger than the evidence state.",
            "implemented_fix": "Replace closure language with bounded connection and explicit rank-level source boundary.",
            "residual_status": "controlled",
        },
        {
            "issue": "Source-data audit was based on public-source inspection but lacked local file provenance.",
            "severity": "important",
            "risk": "The audit would be harder to reproduce from archived local artifacts.",
            "implemented_fix": "Add local artifact paths and SHA256 checksums to the source-data audit table.",
            "residual_status": "controlled",
        },
        {
            "issue": "Prospective experiment plan did not specify a primary interaction model.",
            "severity": "important",
            "risk": "A positive result could be interpreted post hoc rather than through a predeclared test.",
            "implemented_fix": "Add branch-by-treatment interaction model, effect-size reporting, and mechanistic concordance success rule.",
            "residual_status": "controlled",
        },
        {
            "issue": "HDAC secondary candidate could be overpromoted despite exact p = 0.1667.",
            "severity": "critical",
            "risk": "The manuscript could dilute the clean ATM positive line with an underpowered exploratory candidate.",
            "implemented_fix": "Add claim ceilings and next-upgrade fields that keep HDAC secondary until independent validation exists.",
            "residual_status": "controlled",
        },
        {
            "issue": "ATM support remains based on four model ranks and four digitized dynamic time points.",
            "severity": "residual_limitation",
            "risk": "The evidence is directionally valuable but not definitive pharmacologic validation.",
            "implemented_fix": "Preserve as the main positive hypothesis, not a clinical or source-table-level conclusion.",
            "residual_status": "open_until_source_tables_or_prospective_experiment",
        },
    ]
    return pd.DataFrame(rows)


def render_source_data_audit(audit: pd.DataFrame, requests: pd.DataFrame) -> str:
    """Render the source-data search audit."""
    audit_rows = "\n".join(
        f"| {row.source_id} | {row.source_numerical_status} | {row.usable_for_current_analysis} | {row.local_artifact_status} | {row.missing_for_upgrade} |"
        for row in audit.itertuples()
    )
    request_rows = "\n".join(
        f"| {row.requested_table} | {row.minimum_fields} | {row.purpose} |"
        for row in requests.itertuples()
    )
    return f"""# GSE335846 Source-Data Numerical Audit

## Verdict

The public materials now support the current RNA-seq branch-induction analysis with a local source table, but they do not expose source numerical tables for the replication-origin polarity and ATM-combination response panels. The preprint data-availability statement points to the super-series accession `GSE335848`, while the accessible GEO family record in this package is `GSE335846`; the official GEO accession viewer for `GSE335848` states that supplementary data files are not provided, so the dynamic drug-response association remains rank-level figure-digitized evidence until the source values are obtained.

| Source | Numerical status | Usable now | Local artifact | Missing upgrade item |
|---|---|---|---|---|
{audit_rows}

## Data Request Target

| Requested table | Minimum fields | Purpose |
|---|---|---|
{request_rows}

## Claim Boundary

Use the fifth system as independent dynamic preclinical support, not as a source-table-level pharmacology result. The branch-axis RNA-seq component is now source-table backed; the remaining upgrade target is replicate-level PC9 and HCC4006 values for Figures 3B, 4F, 4G, 4H, and Supplementary Figure 4B-D. Local source artifacts are retained with checksums in the TSV audit so the public-source search can be traced, and the accession split between the preprint and GEO family record is recorded explicitly so the evidence chain stays auditable.
"""


def render_experiment_plan(design: pd.DataFrame) -> str:
    """Render the prospective validation plan."""
    rows = "\n".join(
        f"| {row.branch_state} | {row.treatment_arm} | {row.analysis_unit} | {row.sampling_schedule} | {row.minimum_biological_replicates} | {row.primary_endpoint} | {row.mechanistic_endpoints} | {row.batch_control} | {row.primary_analysis} | {row.success_rule} |"
        for row in design.itertuples()
    )
    return f"""# Prospective ATM Branch-Dose Validation Plan

## Testable Claim

The positive claim to test is branch-stratified and quantitative: DTP states with stronger frozen adaptive-stress/replication-defect scores should gain more from ATM inhibition than branch-weak DTP states.

| Branch state | Treatment arm | Analysis unit | Sampling schedule | Minimum biological replicates | Primary endpoint | Mechanistic endpoints | Batch control | Primary analysis | Success rule |
|---|---|---|---|---:|---|---|---|---|---|
{rows}

## Decision Rule

The primary success criterion is a positive branch-by-treatment interaction for ATM inhibition: the added benefit of AZD1390 or AZD0156 over osimertinib alone is larger in branch-strong states than in branch-weak states, with a reported interaction effect size and confidence interval. The predeclared readouts are confluence or viable-cell area under the curve plus at least one concordant mechanistic endpoint such as EdU or a DNA-damage marker. PC9 is the primary prospective validation platform; HCC4006 is a secondary bridge for generalization. HDAC inhibition is tested as a secondary branch-consistent arm, not as a replacement for the ATM lead.

## Manuscript Value

This converts the computational evidence into a prospective therapeutic stratification experiment. It keeps the manuscript main line as a claim-state compiler while giving reviewers a direct path from state assignment to an actionable experiment.
"""


def render_candidate_map(candidate_map: pd.DataFrame) -> str:
    """Render the ATM/HDAC candidate map."""
    rows = "\n".join(
        f"| {row.target_class} | {row.lead_drug} | {row.candidate_role} | {row.gse193258_spearman_rho:.3f} | {row.gse193258_exact_p:.4f} | {row.gse335846_dynamic_rho if pd.notna(row.gse335846_dynamic_rho) else 'NA'} | {row.evidence_state} | {row.claim_ceiling} |"
        for row in candidate_map.itertuples()
    )
    return f"""# ATM/HDAC Branch-Vulnerability Map

| Target class | Lead drug | Role | GSE193258 rho | GSE193258 exact p | GSE335846 dynamic rho | Evidence state | Claim ceiling |
|---|---|---|---:|---:|---:|---|---|
{rows}

ATM is the primary demonstration case because it has both GSE193258 branch-intensity calibration and independent GSE335846 dynamic support. The matched-screen calibration is source-table-backed via `docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md`, and the companion target-specificity audit shows that ATM is the only exact-significant positive target-class signal in the broad screen landscape. HDAC remains valuable as a secondary branch-consistent candidate because it ranks highly in GSE193258 but lacks the fifth-system dynamic replication layer and does not meet the same claim ceiling.
"""


def render_manuscript_mainline(candidate_map: pd.DataFrame) -> str:
    """Render manuscript-facing language for the upgraded branch-vulnerability story."""
    atm = candidate_map[candidate_map["target_class"].eq("ATM")].iloc[0]
    hdac = candidate_map[candidate_map["target_class"].eq("HDAC")].iloc[0]
    return f"""# Manuscript Mainline Update: Branch-Specific Vulnerability

## Recommended Results Framing

The central manuscript object remains the claim-state compiler: PGAA-derived evidence is promoted only when the evidence state supports the claim. The resistance-state branch is now the strongest positive demonstration case. A frozen adaptive-stress branch discovered in GSE249721 prospectively assigns GSE193258 DTP models and ranks ATM inhibition by branch intensity ({atm.lead_drug}; Spearman rho {atm.gse193258_spearman_rho:.1f}; exact p {atm.gse193258_exact_p:.4f}). The matched-screen calibration is source-table-backed via `docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md`, and `docs/GSE193258_TARGET_SPECIFICITY_AUDIT.md` now shows that ATM is the only exact-significant positive target-class signal in the broad screen landscape. An independent GSE335846 dynamic DTP system then supports the same direction at rank level: stronger replication-defective time points show greater added benefit from AZD1390. The preprint points to `GSE335848`, and the official GEO accession viewer for `GSE335848` states that supplementary data files are not provided, while the local GEO family record is `GSE335846`, so the accession chain and public source ceiling are explicit rather than assumed.

## Recommended Claim Ceiling

Do claim: PGAA supports a branch-specific therapeutic hypothesis in which stronger adaptive-stress/replication-defect states are predicted to be more vulnerable to ATM inhibition.

Do not claim: ATM inhibition is clinically validated, source-table-level pharmacology has been obtained for GSE335846, or the figure-digitized time course substitutes for authors' replicate-level values.

## Secondary Candidate

HDAC inhibition remains in the map as a secondary branch-consistent candidate ({hdac.lead_drug}; Spearman rho {hdac.gse193258_spearman_rho:.1f}; exact p {hdac.gse193258_exact_p:.4f}). Its role is to broaden the vulnerability program beyond a single target while preserving ATM as the primary positive line.

## Submission-Facing Gap Package

The remaining gap is now packaged explicitly in `docs/AUTHOR_DATA_REQUEST_GSE335846.md`, `docs/ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md`, and `docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md`, so the manuscript can move between author-request closure, source-table-backed calibration, and prospective validation without changing its claim ceiling.
"""


def render_self_audit(self_audit: pd.DataFrame) -> str:
    """Render the objective self-audit."""
    rows = "\n".join(
        f"| {row.issue} | {row.severity} | {row.risk} | {row.implemented_fix} | {row.residual_status} |"
        for row in self_audit.itertuples()
    )
    return f"""# ATM/HDAC Upgrade Objective Self-Audit

## Verdict

The upgrade is directionally useful and manuscript-positive because it turns the EGFR-resistance branch into a testable ATM vulnerability program. Its ceiling must remain a preclinical branch-specific therapeutic hypothesis until replicate-level GSE335846 source tables or a prospective branch-by-treatment experiment are available.

| Issue | Severity | Risk | Implemented fix | Residual status |
|---|---|---|---|---|
{rows}

## Modification Priority

The strongest next manuscript-facing version is not a broader list of drugs. It is a cleaner hierarchy: ATM as the primary branch-specific vulnerability, HDAC as a secondary candidate, and source/prospective evidence gates that specify exactly how each candidate can be promoted.
"""


def render_author_request_email(requests: pd.DataFrame) -> str:
    """Render a concise author data-request template."""
    bullet_rows = "\n".join(
        f"- {row.requested_table}: {row.minimum_fields} [preferred format: {row.preferred_format}; shared metadata: {row.shared_metadata}]"
        for row in requests.itertuples()
    )
    return f"""Subject: Request for source numerical data for GSE335846 / osimertinib DTP preprint

Dear GSE335846 authors,

We are reusing your public GSE335846 RNA-seq dataset to study replication-defective drug-tolerant persister states in EGFR-mutant lung cancer. The GEO RNA-seq matrix is available and sufficient for our transcriptomic branch analysis, but we would like to replace figure-level digitization with source numerical values for the replication and ATM-inhibitor response analyses.

If available, a flat CSV, TSV, or XLSX table with one row per biological replicate would be ideal. We only need source numerical values and the minimal sample metadata required to trace each measurement back to its figure panel and replicate.

Would you be willing to share the source numerical tables for:

{bullet_rows}

If the figures are split across multiple worksheets or files, we can reconstruct the merged table ourselves as long as the row-level values and identifiers are present. We would cite the preprint and GEO accession directly, preserve the preprint and non-peer-reviewed status, and use the values only for a bounded computational validation of branch-specific ATM sensitivity.

Best regards,
"""


def write_upgrade_package(
    output_dir: Path,
    evidence_dir: Path,
    docs_dir: Path,
    drug_associations: pd.DataFrame,
    dynamic_association: pd.DataFrame,
    source_dir: Path | None = None,
    gse193258_source_dir: Path | None = None,
) -> dict[str, Path]:
    """Write the complete upgrade package and return produced paths."""
    if source_dir is None:
        source_dir = output_dir / "sources/gse335846_dynamic_atm"
    elif not source_dir.is_absolute():
        source_dir = output_dir / source_dir
    if gse193258_source_dir is None:
        gse193258_source_dir = output_dir / "data/external/GSE193258"
    elif not gse193258_source_dir.is_absolute():
        gse193258_source_dir = output_dir / gse193258_source_dir
    audit = build_source_data_audit(source_dir)
    annotate_local_artifacts(audit, output_dir)
    requests = build_author_request_rows()
    design = build_experiment_design()
    candidate_map = build_candidate_map(drug_associations, dynamic_association)
    self_audit = build_self_audit()

    evidence_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "gse193258_source_audit": evidence_dir / "gse193258_drug_screen_source_audit.tsv",
        "gse193258_source_audit_doc": docs_dir / "GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md",
        "gse193258_target_specificity": evidence_dir / "gse193258_target_specificity.tsv",
        "gse193258_target_specificity_contrast": evidence_dir / "gse193258_target_specificity_contrast.tsv",
        "gse193258_target_specificity_doc": docs_dir / "GSE193258_TARGET_SPECIFICITY_AUDIT.md",
        "source_audit": evidence_dir / "gse335846_source_data_numeric_audit.tsv",
        "author_request_fields": evidence_dir / "gse335846_author_request_fields.tsv",
        "experiment_design": evidence_dir / "atm_branch_prospective_experiment_design.tsv",
        "candidate_map": evidence_dir / "atm_hdac_branch_vulnerability_map.tsv",
        "self_audit": evidence_dir / "atm_hdac_upgrade_self_audit.tsv",
        "source_audit_doc": docs_dir / "GSE335846_SOURCE_DATA_NUMERIC_AUDIT.md",
        "experiment_plan_doc": docs_dir / "ATM_BRANCH_PROSPECTIVE_EXPERIMENT_PLAN.md",
        "candidate_map_doc": docs_dir / "ATM_HDAC_BRANCH_VULNERABILITY_MAP.md",
        "mainline_doc": docs_dir / "MANUSCRIPT_MAINLINE_ATM_HDAC_UPDATE.md",
        "author_request_doc": docs_dir / "AUTHOR_DATA_REQUEST_GSE335846.md",
        "self_audit_doc": docs_dir / "ATM_HDAC_UPGRADE_SELF_AUDIT.md",
    }
    audit.to_csv(paths["source_audit"], sep="\t", index=False)
    requests.to_csv(paths["author_request_fields"], sep="\t", index=False)
    design.to_csv(paths["experiment_design"], sep="\t", index=False)
    candidate_map.to_csv(paths["candidate_map"], sep="\t", index=False)
    self_audit.to_csv(paths["self_audit"], sep="\t", index=False)
    gse193258_paths = write_gse193258_drug_screen_source_audit_package(
        source_dir=gse193258_source_dir,
        evidence_out=paths["gse193258_source_audit"],
        report_out=paths["gse193258_source_audit_doc"],
    )
    _, _, gse193258_target_context = build_gse193258_drug_screen_source_audit(
        gse193258_source_dir
    )
    specificity_paths = write_gse193258_target_specificity_audit_package(
        drug_associations=drug_associations,
        evidence_out=paths["gse193258_target_specificity"],
        report_out=paths["gse193258_target_specificity_doc"],
        target_context=gse193258_target_context,
        figure_out=output_dir / "figures_png/gse193258_target_specificity_map.png",
        figure_pdf_out=output_dir / "figures_png/gse193258_target_specificity_map.pdf",
        caption_out=docs_dir / "GSE193258_TARGET_SPECIFICITY_SUPPORT_TEXT.md",
    )
    paths["gse193258_target_context"] = gse193258_paths["target_context"]
    paths["gse193258_target_specificity"] = specificity_paths["evidence"]
    paths["gse193258_target_specificity_contrast"] = specificity_paths["contrast"]
    paths["gse193258_target_specificity_doc"] = specificity_paths["report"]
    if "figure" in specificity_paths:
        paths["gse193258_target_specificity_figure"] = specificity_paths["figure"]
    if "figure_pdf" in specificity_paths:
        paths["gse193258_target_specificity_figure_pdf"] = specificity_paths["figure_pdf"]
    if "caption" in specificity_paths:
        paths["gse193258_target_specificity_caption"] = specificity_paths["caption"]
    paths["source_audit_doc"].write_text(
        render_source_data_audit(audit, requests), encoding="utf-8"
    )
    paths["experiment_plan_doc"].write_text(
        render_experiment_plan(design), encoding="utf-8"
    )
    paths["candidate_map_doc"].write_text(
        render_candidate_map(candidate_map), encoding="utf-8"
    )
    paths["mainline_doc"].write_text(
        render_manuscript_mainline(candidate_map), encoding="utf-8"
    )
    paths["author_request_doc"].write_text(
        render_author_request_email(requests), encoding="utf-8"
    )
    paths["self_audit_doc"].write_text(
        render_self_audit(self_audit), encoding="utf-8"
    )
    return paths
