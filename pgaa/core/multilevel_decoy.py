"""Multi-level peptide decoys and stratified public-evidence enrichment."""
from __future__ import annotations

import hashlib
import random

import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.proportion import proportion_confint

from pgaa.core.immune_evidence import _normalized_hla, _normalized_peptide


REQUIRED_CANDIDATE_COLUMNS = {
    "candidate_id",
    "source_event_id",
    "source_gene",
    "peptide_sequence",
    "peptide_length",
    "hla_allele",
    "hla_class",
}


def _composition_shuffle(peptide: str, candidate_id: str) -> str:
    residues = list(peptide)
    if len(set(residues)) < 2:
        return ""
    seed = int(hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()[:16], 16)
    generator = random.Random(seed)
    for _ in range(20):
        shuffled = residues.copy()
        generator.shuffle(shuffled)
        sequence = "".join(shuffled)
        if sequence != peptide:
            return sequence
    return ""


def build_multilevel_decoys(
    candidates: pd.DataFrame,
    existing_decoys: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build same-context, composition, and cross-event matched controls."""
    missing = sorted(REQUIRED_CANDIDATE_COLUMNS - set(candidates.columns))
    if missing:
        raise ValueError(f"candidate table is missing required columns: {missing}")

    rows: list[dict[str, object]] = []
    if existing_decoys is not None and not existing_decoys.empty:
        rows.extend(existing_decoys.to_dict("records"))

    candidate_rows = candidates.reset_index(drop=True)
    for _, candidate in candidate_rows.iterrows():
        candidate_id = str(candidate["candidate_id"])
        peptide = str(candidate["peptide_sequence"])
        common = {
            "matched_candidate_id": candidate_id,
            "peptide_length": int(candidate["peptide_length"]),
            "hla_allele": candidate["hla_allele"],
            "hla_class": candidate["hla_class"],
            "source_event_id": candidate["source_event_id"],
            "source_gene": candidate["source_gene"],
        }
        shuffled = _composition_shuffle(peptide, candidate_id)
        if shuffled:
            rows.append(
                {
                    "decoy_id": f"{candidate_id}|composition_shuffle",
                    **common,
                    "peptide_sequence": shuffled,
                    "decoy_type": "composition_matched_shuffle",
                    "altered_sequence_start": "",
                    "notes": "same_residue_composition_deterministic_shuffle",
                }
            )

        pool = candidate_rows[
            candidate_rows["peptide_length"].eq(candidate["peptide_length"])
            & candidate_rows["hla_class"].astype(str).eq(str(candidate["hla_class"]))
            & candidate_rows["source_event_id"].astype(str).ne(str(candidate["source_event_id"]))
        ]
        if not pool.empty:
            digest = int(hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()[-16:], 16)
            donor = pool.iloc[digest % len(pool)]
            rows.append(
                {
                    "decoy_id": f"{candidate_id}|cross_event",
                    **common,
                    "peptide_sequence": donor["peptide_sequence"],
                    "decoy_type": "cross_event_length_class_matched",
                    "altered_sequence_start": donor.get("altered_sequence_start", ""),
                    "notes": f"donor_event={donor['source_event_id']};donor_gene={donor['source_gene']}",
                }
            )

    decoys = pd.DataFrame(rows)
    if decoys.empty:
        return decoys
    return decoys.drop_duplicates(subset=["decoy_id"]).reset_index(drop=True)


def _evidence_index(*evidence_tables: pd.DataFrame) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for evidence in evidence_tables:
        for _, row in evidence.iterrows():
            peptide = _normalized_peptide(row.get("peptide_sequence", ""))
            hla = _normalized_hla(row.get("hla_allele", ""))
            if not peptide:
                continue
            hla_keys = {hla, hla.split(":")[0]} if hla else {"*"}
            for length in range(8, len(peptide) + 1):
                for start in range(0, len(peptide) - length + 1):
                    subsequence = peptide[start : start + length]
                    for key in hla_keys:
                        index.setdefault(key, set()).add(subsequence)
    return index


def _evidence_hits(table: pd.DataFrame, evidence_index: dict[str, set[str]]) -> pd.Series:
    hits = []
    wildcard = evidence_index.get("*", set())
    for _, row in table.iterrows():
        peptide = _normalized_peptide(row.get("peptide_sequence", ""))
        hla = _normalized_hla(row.get("hla_allele", ""))
        hits.append(
            peptide in wildcard
            or peptide in evidence_index.get(hla, set())
            or peptide in evidence_index.get(hla.split(":")[0], set())
        )
    return pd.Series(hits, index=table.index, dtype=bool)


def _rate_row(label: str, hits: pd.Series) -> dict[str, object]:
    count = int(hits.sum())
    total = int(len(hits))
    low, high = proportion_confint(count, total, method="wilson") if total else (0.0, 0.0)
    return {
        "group": label,
        "hit_count": count,
        "total_count": total,
        "match_rate": count / total if total else 0.0,
        "wilson_ci_low": float(low),
        "wilson_ci_high": float(high),
    }


def compare_multilevel_decoy_enrichment(
    candidates: pd.DataFrame,
    decoys: pd.DataFrame,
    ligand_evidence: pd.DataFrame,
    tcell_evidence: pd.DataFrame,
) -> pd.DataFrame:
    """Compare candidate public-evidence hits with each decoy family."""
    evidence_index = _evidence_index(ligand_evidence, tcell_evidence)
    candidate_hits = _evidence_hits(candidates, evidence_index)
    candidate_row = _rate_row("candidate", candidate_hits)
    rows = [
        {
            **candidate_row,
            "odds_ratio_vs_candidate": 1.0,
            "fisher_p_value": 1.0,
            "decoy_gate": "reference_candidate_group",
        }
    ]
    for decoy_type, group in decoys.groupby("decoy_type", sort=True):
        decoy_hits = _evidence_hits(group, evidence_index)
        row = _rate_row(str(decoy_type), decoy_hits)
        odds_ratio, p_value = fisher_exact(
            [
                [candidate_row["hit_count"], candidate_row["total_count"] - candidate_row["hit_count"]],
                [row["hit_count"], row["total_count"] - row["hit_count"]],
            ],
            alternative="greater",
        )
        row["odds_ratio_vs_candidate"] = float(odds_ratio)
        row["fisher_p_value"] = float(p_value)
        row["decoy_gate"] = (
            "passed_candidate_above_decoy"
            if candidate_row["wilson_ci_low"] > row["wilson_ci_high"] and p_value < 0.05
            else "failed_candidate_not_above_decoy"
        )
        rows.append(row)
    return pd.DataFrame(rows)


def multilevel_decoy_verdict(summary: pd.DataFrame) -> str:
    """Return a conservative verdict across all decoy families."""
    decoys = summary[summary["group"] != "candidate"]
    if decoys.empty:
        return "NO_DECOY_GROUPS"
    passed = decoys["decoy_gate"].eq("passed_candidate_above_decoy")
    if passed.all():
        return "ALL_DECOY_LEVELS_SEPARATED"
    if passed.any():
        return "MIXED_DECOY_SENSITIVITY_NO_GLOBAL_ENRICHMENT_CLAIM"
    return "NO_DECOY_LEVEL_SEPARATION"


def render_multilevel_decoy_audit(summary: pd.DataFrame) -> str:
    """Render a claim-safe interpretation of stratified decoy results."""
    verdict = multilevel_decoy_verdict(summary)
    lines = [
        "# Multi-level Decoy Enrichment Audit",
        "",
        f"Verdict: `{verdict}`",
        "",
        "| Group | Hits / total | Rate | Gate | Fisher p |",
        "|---|---:|---:|---|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['group']} | {row['hit_count']} / {row['total_count']} | "
            f"{row['match_rate']:.6f} | {row['decoy_gate']} | {row['fisher_p_value']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A decoy family is passed only when the candidate Wilson interval is entirely above "
            "the decoy interval and the one-sided Fisher test is below 0.05.",
            "",
            "Any failed decoy family blocks a global enrichment claim. Because the candidate set "
            "originates from previously validated events, separation is a positive-control property "
            "of the evidence-matching layer, not PGAA discovery evidence.",
            "",
        ]
    )
    return "\n".join(lines)
