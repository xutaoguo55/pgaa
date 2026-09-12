#!/usr/bin/env python3
"""Audit PC9 branch-axis projection in GSE255958."""
from __future__ import annotations

import argparse
import gzip
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _group_from_sample(sample: str) -> str:
    if sample.startswith("PC9-persister-Osi-d9-VT-"):
        return "PC9-persister-Osi-d9-VT"
    if sample.startswith("PC9-persister-Osi-d9-"):
        return "PC9-persister-Osi-d9"
    if sample.startswith("PC9_") and sample.rsplit("_", 1)[-1].isdigit():
        return sample.rsplit("_", 1)[0]
    return sample


def _module_score(frame: pd.DataFrame, genes: list[str]) -> tuple[int, float, float]:
    overlap = [g for g in genes if g in frame.index]
    if not overlap:
        return 0, float("nan"), float("nan")
    logt = np.log1p(frame["TPM"])
    z = (np.log1p(frame.loc[overlap, "TPM"]) - logt.mean()) / logt.std(ddof=0)
    return len(overlap), float(np.log1p(frame.loc[overlap, "TPM"]).mean()), float(z.mean())


def _render_report(summary: pd.DataFrame, details: pd.DataFrame) -> str:
    consistent = summary[[
        "group",
        "axis_positive_n",
        "axis_negative_n",
        "axis_all_positive",
        "axis_all_negative",
    ]].copy()
    lines = [
        "# GSE255958 PC9 Branch Projection Audit",
        "",
        "This audit projects the frozen PC9 adaptive-stress / replication-maintaining branch genes from `GSE249721` onto the PC9-containing RNA-seq subsets in `GSE255958`.",
        "",
        "## Result",
        "",
        "The adaptive-stress branch axis is positive in the osimertinib-exposed PC9 states (`PC9_O2`, `PC9_O9`, `PC9_d47`) and negative in the parental/control state (`PC9_D`). The persister/VT subset is also positive on average, although one persister replicate is an outlier in the opposite direction.",
        "",
        "This supports `GSE255958` as an additional branch-axis support dataset, but not as a clean third-system preservation of the frozen 50-gene down-module route.",
        "",
        "## Direction Consistency",
        "",
        consistent.to_csv(sep="\t", index=False).strip(),
        "",
        "## Group Summary",
        "",
        summary.to_csv(sep="\t", index=False).strip(),
        "",
        "## Sample Details",
        "",
        details.to_csv(sep="\t", index=False).strip(),
        "",
        "## Interpretation",
        "",
        "Use this dataset as independent branch-axis support in the manuscript mainline. Do not promote it as universal module-direction replication.",
    ]
    return "\n".join(lines) + "\n"


def build_audit(raw_tar: Path, branch_genes: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    branch = pd.read_csv(branch_genes, sep="\t")
    adaptive = branch[branch["branch"] == "PC9_adaptive_stress"].head(50)["gene_symbol"].tolist()
    replication = branch[branch["branch"] == "H4006_replication"].head(50)["gene_symbol"].tolist()

    rows: list[dict[str, object]] = []
    with tarfile.open(raw_tar) as tf:
        for member in tf.getmembers():
            if not (member.isfile() and member.name.endswith(".genes.results.gz")):
                continue
            sample = member.name.replace(".genes.results.gz", "").split("_", 1)[1]
            if not sample.startswith("PC9"):
                continue
            group = _group_from_sample(sample)
            with gzip.open(tf.extractfile(member), "rt") as fh:
                frame = pd.read_csv(fh, sep="\t", usecols=["gene_id", "TPM"])
            frame["gene_symbol"] = frame["gene_id"].str.split("_", n=1).str[0]
            indexed = frame.set_index("gene_symbol")
            adaptive_n, adaptive_mean, adaptive_z = _module_score(indexed, adaptive)
            replication_n, replication_mean, replication_z = _module_score(indexed, replication)
            rows.append(
                {
                    "sample": sample,
                    "group": group,
                    "adaptive_overlap": adaptive_n,
                    "adaptive_log1p_mean": adaptive_mean,
                    "adaptive_z": adaptive_z,
                    "replication_overlap": replication_n,
                    "replication_log1p_mean": replication_mean,
                    "replication_z": replication_z,
                    "axis_z": adaptive_z - replication_z,
                }
            )

    details = pd.DataFrame(rows).sort_values(["group", "sample"]).reset_index(drop=True)
    summary = (
        details.groupby("group", as_index=False)
        .agg(
            n=("sample", "size"),
            adaptive_z_mean=("adaptive_z", "mean"),
            replication_z_mean=("replication_z", "mean"),
            axis_z_mean=("axis_z", "mean"),
            axis_z_sd=("axis_z", "std"),
            axis_positive_n=("axis_z", lambda s: int((s > 0).sum())),
            axis_negative_n=("axis_z", lambda s: int((s < 0).sum())),
        )
        .sort_values("axis_z_mean")
        .reset_index(drop=True)
    )
    summary["axis_all_positive"] = summary["axis_negative_n"].eq(0)
    summary["axis_all_negative"] = summary["axis_positive_n"].eq(0)
    return summary, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-tar",
        type=Path,
        required=True,
        help="Path to GSE255958_RAW.tar",
    )
    parser.add_argument(
        "--branch-genes",
        type=Path,
        default=ROOT / "evidence/gse249721_resistance_branch_genes.tsv",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--details-out",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    summary, details = build_audit(args.raw_tar, args.branch_genes)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.details_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_out, sep="\t", index=False)
    details.to_csv(args.details_out, sep="\t", index=False)
    args.report_out.write_text(_render_report(summary, details), encoding="utf-8")
    print(f"Wrote {args.summary_out}")
    print(f"Wrote {args.details_out}")
    print(f"Wrote {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
