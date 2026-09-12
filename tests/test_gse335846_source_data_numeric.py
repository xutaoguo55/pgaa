from __future__ import annotations

from pathlib import Path

import pandas as pd

from pgaa.core.atm_hdac_upgrade_package import NOT_APPLICABLE_STATUS
from scripts.audit_gse335846_source_data_numeric import (
    build_source_data_numeric_audit_package,
)


def test_source_data_numeric_audit_package_rebuilds_outputs(tmp_path: Path) -> None:
    source_dir = tmp_path / "sources/gse335846_dynamic_atm"
    source_dir.mkdir(parents=True)
    for name in [
        "GSE335846_family.soft.gz",
        "preprint_733326.txt",
        "biorxiv_supplementary.html",
    ]:
        (source_dir / name).write_text(f"{name}\n", encoding="utf-8")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "gse335846_rna_seq_branch_axis_scores.tsv").write_text(
        "gene\tscore\n", encoding="utf-8"
    )

    evidence_out = tmp_path / "evidence/gse335846_source_data_numeric_audit.tsv"
    report_out = tmp_path / "docs/GSE335846_SOURCE_DATA_NUMERIC_AUDIT.md"
    paths = build_source_data_numeric_audit_package(
        source_dir=source_dir,
        output_dir=tmp_path,
        evidence_out=evidence_out,
        report_out=report_out,
    )

    audit = pd.read_csv(evidence_out, sep="\t")
    assert paths["evidence"] == evidence_out
    assert paths["report"] == report_out
    # Every artifact is either present on disk or explicitly declared a
    # non-path public-resource descriptor; "missing" is never acceptable.
    assert set(audit["local_artifact_status"]) == {
        "present",
        NOT_APPLICABLE_STATUS,
    }
    assert "missing" not in set(audit["local_sha256"])
    assert report_out.read_text(encoding="utf-8").startswith("# GSE335846 Source-Data Numerical Audit")
