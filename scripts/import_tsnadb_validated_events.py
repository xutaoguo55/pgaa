#!/usr/bin/env python3
"""Import experimentally validated TSNAdb v2.0 neoantigens."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


COLUMNS = [
    "level",
    "patient_id",
    "tumor_type",
    "tumor_detail",
    "mutation_type",
    "gene",
    "mutation",
    "position",
    "peptide",
    "hla",
    "pmid",
    "title",
    "journal",
    "year",
    "url",
    "source_databases",
    "source_count",
]
VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
CLASS_I_LOCI = ("A", "B", "C")
CLASS_II_LOCI = ("DPA", "DPB", "DQA", "DQB", "DRA", "DRB")


def normalize_hla(value: object) -> tuple[str, str] | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper().replace("HLA-", "").replace("*", "")
    if not text or text.startswith("H2"):
        return None
    locus = text.split(":", 1)[0]
    if any(locus.startswith(prefix) for prefix in CLASS_II_LOCI):
        hla_class = "II"
    elif locus.startswith(CLASS_I_LOCI):
        hla_class = "I"
    else:
        return None
    if ":" not in text:
        return None
    locus, allele = text.split(":", 1)
    return f"HLA-{locus}*{allele}", hla_class


def import_tsnadb(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(
        path,
        sep="\t",
        skiprows=1,
        header=None,
        names=COLUMNS,
        dtype=str,
    )
    events: list[dict[str, object]] = []
    ligands: list[dict[str, object]] = []
    tcells: list[dict[str, object]] = []
    audit: list[dict[str, object]] = []
    for row_number, row in source.iterrows():
        source_id = f"TSNADB2_{row_number + 1:06d}"
        peptide = "" if pd.isna(row["peptide"]) else str(row["peptide"]).strip().upper()
        position_text = "" if pd.isna(row["position"]) else str(row["position"]).strip()
        hla = normalize_hla(row["hla"])
        exclusion = ""
        if not peptide or set(peptide) - VALID_AMINO_ACIDS:
            exclusion = "invalid_or_missing_peptide"
        elif not 8 <= len(peptide) <= 25:
            exclusion = "peptide_length_outside_8_25"
        elif not position_text.isdigit():
            exclusion = "missing_or_ambiguous_event_position"
        elif not 1 <= int(position_text) <= len(peptide):
            exclusion = "event_position_outside_peptide"
        elif hla is None:
            exclusion = "missing_or_nonhuman_hla"
        elif hla[1] == "I" and not 8 <= len(peptide) <= 11:
            exclusion = "hla_i_peptide_length_outside_8_11"
        elif hla[1] == "II" and not 12 <= len(peptide) <= 25:
            exclusion = "hla_ii_peptide_length_outside_12_25"

        audit.append(
            {
                "source_event_id": source_id,
                "source_row": row_number + 2,
                "import_status": "excluded" if exclusion else "included",
                "exclusion_reason": exclusion,
                "validation_level": row["level"],
                "mutation_type": row["mutation_type"],
                "gene": row["gene"],
                "mutation": row["mutation"],
                "peptide_sequence": peptide,
                "hla_raw": row["hla"],
                "pmid": row["pmid"],
            }
        )
        if exclusion:
            continue

        hla_allele, hla_class = hla
        common_evidence = {
            "peptide_sequence": peptide,
            "hla_allele": hla_allele,
            "source_id": source_id,
            "database": "TSNAdb_v2.0",
            "disease_or_context": row["tumor_detail"],
            "reference_id": row["pmid"],
            "reference_url": row["url"],
            "validation_level": row["level"],
        }
        events.append(
            {
                "source_event_id": source_id,
                "source_event_type": str(row["mutation_type"]).strip().lower().replace(" ", "_"),
                "source_gene": row["gene"],
                "event_coordinate": row["mutation"],
                "altered_sequence_context": peptide,
                "event_index": int(position_text) - 1,
                "hla_allele": hla_allele,
                "hla_class": hla_class,
                "pgaa_rank": "",
                "pgaa_score": "",
                "cohort_or_dataset": "TSNAdb_v2.0_validated",
                "disease_or_context": row["tumor_detail"],
                "notes": (
                    f"validation_level={row['level']};reference={row['pmid']};"
                    "domain_transfer_event_not_pgaa_ranked"
                ),
            }
        )
        if row["level"] in {"tier1", "tier3"}:
            ligands.append(
                {
                    **common_evidence,
                    "match_notes": "experimentally_presented_mutant_pHLA",
                }
            )
        if row["level"] in {"tier1", "tier2"}:
            tcells.append(
                {
                    **common_evidence,
                    "response_type": "experimentally_immunogenic_mutant_peptide",
                    "match_notes": "experimentally_validated_tcell_immunogenicity",
                }
            )
    return pd.DataFrame(events), pd.DataFrame(ligands), pd.DataFrame(tcells), pd.DataFrame(audit)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--events-out", required=True, type=Path)
    parser.add_argument("--ligands-out", required=True, type=Path)
    parser.add_argument("--tcells-out", required=True, type=Path)
    parser.add_argument("--audit-out", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    events, ligands, tcells, audit = import_tsnadb(args.source)
    for path, table in (
        (args.events_out, events),
        (args.ligands_out, ligands),
        (args.tcells_out, tcells),
        (args.audit_out, audit),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, sep="\t", index=False)
        print(f"Wrote {path} ({len(table)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
