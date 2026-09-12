from __future__ import annotations

import importlib.util
import io
import gzip
import tarfile
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_gse255958_pc9_branch_projection.py"
SPEC = importlib.util.spec_from_file_location("audit_gse255958_pc9_branch_projection", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
build_audit = MODULE.build_audit
_group_from_sample = MODULE._group_from_sample


def _write_genes_results(member_path: Path, genes: list[tuple[str, float]]) -> None:
    frame = pd.DataFrame(
        {
            "gene_id": [f"{gene}_{gene}" for gene, _ in genes],
            "transcript_id(s)": [gene for gene, _ in genes],
            "length": [1000.0] * len(genes),
            "effective_length": [900.0] * len(genes),
            "expected_count": [1.0] * len(genes),
            "TPM": [value for _, value in genes],
            "FPKM": [value for _, value in genes],
        }
    )
    text = frame.to_csv(sep="\t", index=False)
    with gzip.open(member_path, "wt") as fh:
        fh.write(text)


def test_gse255958_branch_projection_supports_directional_axis(tmp_path: Path) -> None:
    adaptive = [f"A{index}" for index in range(1, 51)]
    replication = [f"R{index}" for index in range(1, 51)]
    branch_rows = pd.DataFrame(
        {
            "gene_id": adaptive + replication,
            "gene_symbol": adaptive + replication,
            "branch": ["PC9_adaptive_stress"] * 50 + ["H4006_replication"] * 50,
        }
    )
    branch_path = tmp_path / "branch.tsv"
    branch_rows.to_csv(branch_path, sep="\t", index=False)

    tar_path = tmp_path / "GSE255958_RAW.tar"
    with tarfile.open(tar_path, "w") as tf:
        samples = {
            "GSM0000001_PC9_D_1.genes.results.gz": [(g, 1.0) for g in adaptive] + [(g, 10.0) for g in replication],
            "GSM0000002_PC9_O2_1.genes.results.gz": [(g, 10.0) for g in adaptive] + [(g, 1.0) for g in replication],
            "GSM0000003_PC9-persister-Osi-d9-1.genes.results.gz": [(g, 5.0) for g in adaptive] + [(g, 3.0) for g in replication],
        }
        for name, genes in samples.items():
            member = tarfile.TarInfo(name)
            gz_path = tmp_path / name
            _write_genes_results(gz_path, genes)
            data = gz_path.read_bytes()
            member.size = len(data)
            tf.addfile(member, io.BytesIO(data))

    summary, details = build_audit(tar_path, branch_path)
    assert _group_from_sample("PC9-persister-Osi-d9-VT-1") == "PC9-persister-Osi-d9-VT"
    assert _group_from_sample("PC9_D_1") == "PC9_D"
    assert set(summary["group"]) == {"PC9_D", "PC9_O2", "PC9-persister-Osi-d9"}
    assert summary.set_index("group").loc["PC9_D", "axis_negative_n"] == 1
    assert summary.set_index("group").loc["PC9_D", "axis_positive_n"] == 0
    assert summary.set_index("group").loc["PC9_O2", "axis_positive_n"] == 1
    assert summary.set_index("group").loc["PC9_O2", "axis_negative_n"] == 0
    assert summary.set_index("group").loc["PC9_O2", "axis_all_positive"]
    assert summary.set_index("group").loc["PC9_D", "axis_all_negative"]
    assert details["axis_z"].notna().all()
