from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.gse193258_drug_screen_source_audit import (
    write_gse193258_drug_screen_source_audit_package,
)


def _build_replicate_frame() -> pd.DataFrame:
    rows = []
    for cell_line in ["PC9", "HCC827", "H1975", "HCC2935", "HCC2279", "HCC4006", "II-18"]:
        for drug, target in [("AZD0156", "ATM"), ("Quisinostat", "HDAC")]:
            for screen_format in ["Upfront", "Sequential"]:
                rows.append(
                    {
                        "Cell line": cell_line,
                        "Drug": drug,
                        "Dose (nM)": 10,
                        "Putative Target": target,
                        "Screen format": screen_format,
                        "AUC osi. DTP control": 0.1,
                        "AUC osi. DTP combo": 0.2,
                        "AUC DMSO": 0.3,
                        "AUC monotherapy": 0.4,
                    }
                )
    return pd.DataFrame(rows)


def _build_summary_frame() -> pd.DataFrame:
    rows = []
    for cell_line in ["PC9", "HCC827", "H1975", "HCC2935", "HCC2279", "HCC4006", "II-18"]:
        for drug, target in [("AZD0156", "ATM"), ("Quisinostat", "HDAC")]:
            for screen_format in ["upfront", "sequential"]:
                rows.append(
                    {
                        "Cell line": cell_line,
                        "Drug ID": drug,
                        "Putative target": target,
                        "Screen format": screen_format,
                        "Avg. AUC DTP": 0.1,
                        "Avg. AUC DTP Combination": 0.2,
                        "Avg. AUC DMSO": 0.3,
                        "Avg. AUC monotherapy": 0.4,
                        "Combination activity": 1.2,
                        "Monotherapy activity": 0.7,
                        "Label": "hit",
                        "Screen hit status": "hit" if cell_line in {"PC9", "H1975"} else "none",
                    }
                )
    return pd.DataFrame(rows)


def test_gse193258_drug_screen_source_audit_package_rebuilds_outputs(tmp_path: Path) -> None:
    source_dir = tmp_path / "data/external/GSE193258"
    source_dir.mkdir(parents=True)
    replicate = _build_replicate_frame()
    summary = _build_summary_frame()
    rnaseq = pd.DataFrame(
        {
            "PC9_DMSO_1": [1.0, 2.0],
            "HCC827_DMSO_1": [1.1, 2.1],
            "H1975_DMSO_1": [1.2, 2.2],
            "HCC2935_DMSO_1": [1.3, 2.3],
        },
        index=["gene1", "gene2"],
    )
    replicate.to_excel(source_dir / "41698_2022_337_MOESM2_ESM.xlsx", index=False, startrow=2)
    summary.to_excel(source_dir / "41698_2022_337_MOESM3_ESM.xlsx", index=False, startrow=2)
    rnaseq.to_csv(source_dir / "GSE193258_RNAseq_log2TPM_abundance.tsv.gz", sep="\t")

    evidence_out = tmp_path / "evidence/gse193258_drug_screen_source_audit.tsv"
    report_out = tmp_path / "docs/GSE193258_DRUG_SCREEN_SOURCE_AUDIT.md"
    paths = write_gse193258_drug_screen_source_audit_package(
        source_dir=source_dir,
        evidence_out=evidence_out,
        report_out=report_out,
    )

    audit = pd.read_csv(evidence_out, sep="\t")
    target_context = pd.read_csv(
        tmp_path / "evidence/gse193258_drug_screen_target_context.tsv", sep="\t"
    )
    assert paths["evidence"] == evidence_out
    assert paths["target_context"] == tmp_path / "evidence/gse193258_drug_screen_target_context.tsv"
    assert paths["report"] == report_out
    assert set(audit["local_artifact_status"]) == {"present"}
    assert set(audit["table_id"]) == {
        "Supplementary_Data_1",
        "Supplementary_Data_2",
        "GSE193258_RNAseq",
    }
    assert "ATM" in set(target_context["target_class"])
    assert "HDAC" in set(target_context["target_class"])
    assert "missing" not in set(audit["local_sha256"])
    assert report_out.read_text(encoding="utf-8").startswith(
        "# GSE193258 Drug-Screen Source Audit"
    )
    assert "source-table-backed" in report_out.read_text(encoding="utf-8")
    assert "Target Breadth" in report_out.read_text(encoding="utf-8")
