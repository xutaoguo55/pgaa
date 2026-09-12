"""Public-evidence ladder for event-derived immune candidates.

The utilities here do not validate antigen presentation or T-cell function.
They convert peptide/HLA candidate rows plus optional public-evidence columns
into auditable claim tiers that preserve missing evidence.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
HYDROPHOBIC = set("AILMFWVY")
POSITIVE = set("KRH")
NEGATIVE = set("DE")
PLACEHOLDER_PATTERNS = ("PEPTIDEX", "REPLACE_WITH", "SMOKE", "EXAMPLE_")


@dataclass(frozen=True)
class EvidenceColumns:
    """Optional input columns recognized by the evidence ladder."""

    ligand_exact: str = "presentation_exact_count"
    ligand_overlap: str = "presentation_overlap_count"
    binding_affinity_nm: str = "binding_affinity_nm"
    binding_percentile_rank: str = "binding_percentile_rank"
    tcell_exact: str = "tcell_exact_count"
    tcell_region: str = "tcell_region_count"
    immune_context_score: str = "immune_context_score"
    decoy_match_rate: str = "decoy_match_rate"
    candidate_match_rate: str = "candidate_match_rate"


EVIDENCE_COLUMNS = [
    "presentation_exact_count",
    "presentation_overlap_count",
    "presentation_source_ids",
    "tcell_exact_count",
    "tcell_region_count",
    "tcell_source_ids",
    "candidate_match_rate",
    "decoy_match_rate",
]


def _number(row: pd.Series, column: str, default: float = 0.0) -> float:
    if column not in row or pd.isna(row[column]):
        return default
    try:
        return float(row[column])
    except (TypeError, ValueError):
        return default


def _text(row: pd.Series, column: str, default: str = "") -> str:
    if column not in row or pd.isna(row[column]):
        return default
    return str(row[column])


def _normalized_peptide(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def _normalized_hla(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper().replace(" ", "")


def _hla_compatible(candidate_hla: str, evidence_hla: str) -> bool:
    if not evidence_hla or evidence_hla in {"NA", "UNKNOWN", "UNSPECIFIED", "*"}:
        return True
    if not candidate_hla:
        return False
    if candidate_hla == evidence_hla:
        return True
    candidate_prefix = candidate_hla.split(":")[0]
    evidence_prefix = evidence_hla.split(":")[0]
    return bool(candidate_prefix and candidate_prefix == evidence_prefix)


def _overlaps(candidate: str, evidence: str) -> bool:
    if not candidate or not evidence or candidate == evidence:
        return False
    return candidate in evidence or evidence in candidate


def _source_ids(matches: pd.DataFrame) -> str:
    if matches.empty:
        return ""
    for column in ("source_id", "reference_id", "database_id", "evidence_id"):
        if column in matches.columns:
            values = sorted({str(value) for value in matches[column].dropna()})
            return ";".join(values)
    return ""


def _match_evidence(
    row: pd.Series,
    evidence: pd.DataFrame | None,
) -> tuple[int, int, str]:
    if evidence is None or evidence.empty:
        return 0, 0, ""
    candidate_peptide = _normalized_peptide(row["peptide_sequence"])
    candidate_hla = _normalized_hla(row.get("hla_allele", ""))
    if not candidate_peptide:
        return 0, 0, ""

    exact_mask = []
    overlap_mask = []
    for _, evidence_row in evidence.iterrows():
        evidence_peptide = _normalized_peptide(evidence_row.get("peptide_sequence", ""))
        evidence_hla = _normalized_hla(evidence_row.get("hla_allele", ""))
        compatible = _hla_compatible(candidate_hla, evidence_hla)
        exact_mask.append(compatible and candidate_peptide == evidence_peptide)
        overlap_mask.append(compatible and _overlaps(candidate_peptide, evidence_peptide))

    exact_matches = evidence[pd.Series(exact_mask, index=evidence.index)]
    overlap_matches = evidence[pd.Series(overlap_mask, index=evidence.index)]
    all_matches = pd.concat([exact_matches, overlap_matches]).drop_duplicates()
    return len(exact_matches), len(overlap_matches), _source_ids(all_matches)


def annotate_public_evidence(
    candidates: pd.DataFrame,
    ligand_evidence: pd.DataFrame | None = None,
    tcell_evidence: pd.DataFrame | None = None,
    decoys: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Annotate candidates with local public ligand/T-cell evidence tables.

    Evidence tables are deliberately simple TSV-compatible data frames. They
    should contain at least `peptide_sequence`; `hla_allele` and source-id
    columns are optional. Exact peptide-HLA matches are counted separately from
    overlapping peptide-region matches.
    """
    required = {"candidate_id", "peptide_sequence", "hla_allele"}
    missing = sorted(required - set(candidates.columns))
    if missing:
        raise ValueError(f"candidate table is missing required columns: {missing}")

    annotated = candidates.copy()
    for column in EVIDENCE_COLUMNS:
        if column not in annotated.columns:
            annotated[column] = 0 if column.endswith("_count") or column.endswith("_rate") else ""

    for idx, row in annotated.iterrows():
        ligand_exact, ligand_overlap, ligand_sources = _match_evidence(row, ligand_evidence)
        tcell_exact, tcell_region, tcell_sources = _match_evidence(row, tcell_evidence)
        annotated.at[idx, "presentation_exact_count"] = ligand_exact
        annotated.at[idx, "presentation_overlap_count"] = ligand_overlap
        annotated.at[idx, "presentation_source_ids"] = ligand_sources
        annotated.at[idx, "tcell_exact_count"] = tcell_exact
        annotated.at[idx, "tcell_region_count"] = tcell_region
        annotated.at[idx, "tcell_source_ids"] = tcell_sources

    candidate_hits = (
        (annotated["presentation_exact_count"].astype(float) > 0)
        | (annotated["presentation_overlap_count"].astype(float) > 0)
        | (annotated["tcell_exact_count"].astype(float) > 0)
        | (annotated["tcell_region_count"].astype(float) > 0)
    )
    candidate_rate = float(candidate_hits.mean()) if len(candidate_hits) else 0.0
    annotated["candidate_match_rate"] = candidate_rate

    decoy_rate = 0.0
    if decoys is not None and not decoys.empty:
        decoy_rows = decoys.copy()
        if "candidate_id" not in decoy_rows.columns:
            decoy_rows["candidate_id"] = [f"decoy_{i}" for i in range(len(decoy_rows))]
        if "hla_allele" not in decoy_rows.columns and "hla_allele" in candidates.columns:
            fallback_hla = str(candidates["hla_allele"].iloc[0])
            decoy_rows["hla_allele"] = fallback_hla
        ligand_hit = []
        tcell_hit = []
        for _, decoy_row in decoy_rows.iterrows():
            ligand_exact, ligand_overlap, _ = _match_evidence(decoy_row, ligand_evidence)
            tcell_exact, tcell_overlap, _ = _match_evidence(decoy_row, tcell_evidence)
            ligand_hit.append(ligand_exact > 0 or ligand_overlap > 0)
            tcell_hit.append(tcell_exact > 0 or tcell_overlap > 0)
        any_hit = [left or right for left, right in zip(ligand_hit, tcell_hit)]
        decoy_rate = float(sum(any_hit) / len(any_hit)) if any_hit else 0.0
    annotated["decoy_match_rate"] = decoy_rate
    return annotated


def scan_placeholder_artifacts(
    table: pd.DataFrame,
    table_name: str = "table",
    patterns: tuple[str, ...] = PLACEHOLDER_PATTERNS,
) -> list[str]:
    """Return placeholder/smoke tokens that should not enter real analyses."""
    hits: list[str] = []
    object_columns = table.select_dtypes(include=["object"]).columns
    for column in object_columns:
        values = table[column].dropna().astype(str)
        for pattern in patterns:
            matched = values[values.str.upper().str.contains(pattern, regex=False)]
            if not matched.empty:
                example = matched.iloc[0]
                hits.append(f"{table_name}.{column}:{pattern}:{example}")
    return hits


def longest_hydrophobic_run(peptide: str) -> int:
    longest = 0
    current = 0
    for residue in peptide:
        if residue in HYDROPHOBIC:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def synthesis_category(peptide: str, hla_class: str) -> tuple[str, list[str]]:
    """Classify peptide assay-readiness from simple chemistry flags."""
    peptide = peptide.strip().upper()
    flags: list[str] = []
    invalid = sorted(set(peptide) - VALID_AMINO_ACIDS)
    if invalid:
        flags.append("invalid_residue:" + "".join(invalid))

    length = len(peptide)
    hla_class = hla_class.upper().replace("HLA-", "")
    if hla_class in {"I", "1", "CLASSI", "CLASS_I"}:
        if length < 8 or length > 11:
            flags.append("hla_i_length_outside_8_11")
    elif hla_class in {"II", "2", "CLASSII", "CLASS_II"}:
        if length < 12 or length > 25:
            flags.append("hla_ii_length_outside_12_25")
    elif length < 8 or length > 25:
        flags.append("length_outside_8_25")

    cysteine_count = peptide.count("C")
    methionine_count = peptide.count("M")
    hydrophobic_run = longest_hydrophobic_run(peptide)
    net_charge = sum(peptide.count(aa) for aa in POSITIVE) - sum(
        peptide.count(aa) for aa in NEGATIVE
    )

    if cysteine_count >= 3:
        flags.append("high_cysteine_count")
    if methionine_count >= 2:
        flags.append("oxidation_risk")
    if hydrophobic_run >= 5:
        flags.append("long_hydrophobic_run")
    if abs(net_charge) >= 5:
        flags.append("high_net_charge")

    severe = any(
        flag.startswith("invalid_residue") or flag.endswith("length_outside_8_11")
        or flag.endswith("length_outside_12_25")
        or flag == "long_hydrophobic_run"
        for flag in flags
    )
    if severe:
        return "synthesis-risk", flags
    if flags:
        return "synthesis-caution", flags
    return "synthesis-ready", []


def presentation_category(row: pd.Series, columns: EvidenceColumns) -> tuple[str, str, int]:
    exact = int(_number(row, columns.ligand_exact))
    overlap = int(_number(row, columns.ligand_overlap))
    if exact > 0:
        return "presented-same-event", "exact_peptide_or_junction", exact
    if overlap > 0:
        return "presented-overlap", "overlap_or_event_region", overlap
    return "binding-only", "none", 0


def binding_prediction_category(row: pd.Series, columns: EvidenceColumns) -> str:
    explicit = _text(row, "binding_prediction_category")
    if explicit:
        return explicit
    affinity = _number(row, columns.binding_affinity_nm, default=float("nan"))
    rank = _number(row, columns.binding_percentile_rank, default=float("nan"))
    if affinity == affinity:
        if affinity <= 50:
            return "strong_predicted_binding"
        if affinity <= 500:
            return "predicted_binding"
        return "weak_or_no_predicted_binding"
    if rank == rank:
        if rank <= 0.5:
            return "strong_predicted_binding"
        if rank <= 2.0:
            return "predicted_binding"
        return "weak_or_no_predicted_binding"
    return "not_assessed"


def tcell_category(row: pd.Series, columns: EvidenceColumns) -> tuple[str, int]:
    exact = int(_number(row, columns.tcell_exact))
    region = int(_number(row, columns.tcell_region))
    context = _number(row, columns.immune_context_score)
    if exact > 0:
        return "tcell-recognized-exact-peptide", exact
    if region > 0:
        return "tcell-recognized-region", region
    if context > 0:
        return "immune-context-support", 0
    return "no_tcell_evidence", 0


def integrated_tier(
    presentation: str,
    binding: str,
    synthesis: str,
    tcell: str,
) -> str:
    if synthesis == "synthesis-risk":
        return "D"
    has_presentation = presentation in {"presented-same-event", "presented-overlap"}
    has_tcell = tcell in {
        "tcell-recognized-exact-peptide",
        "tcell-recognized-region",
    }
    if has_presentation and synthesis == "synthesis-ready" and has_tcell:
        return "A"
    if has_presentation and synthesis in {"synthesis-ready", "synthesis-caution"}:
        return "B"
    if (
        presentation == "binding-only"
        and binding in {"strong_predicted_binding", "predicted_binding"}
        and synthesis == "synthesis-ready"
        and tcell == "immune-context-support"
    ):
        return "C"
    return "D"


def allowed_claim(tier: str, presentation: str, tcell: str) -> str:
    if tier == "A":
        return (
            "strong public-data-supported follow-up candidate; no new wet-lab "
            "presentation or T-cell validation performed"
        )
    if tier == "B":
        return "presented candidate suitable for future functional testing"
    if tier == "C":
        return "plausible candidate requiring future presentation and T-cell validation"
    if presentation == "binding-only" and tcell == "no_tcell_evidence":
        return "prediction-only candidate with no public ligand or T-cell support"
    return "exploratory candidate with incomplete immune-evidence support"


def missing_flags(
    presentation: str,
    binding: str,
    synthesis: str,
    tcell: str,
) -> str:
    flags: list[str] = []
    if presentation == "binding-only":
        flags.append("no_public_ligand")
    if binding in {"weak_or_no_predicted_binding", "not_assessed"}:
        flags.append("weak_or_missing_binding_prediction")
    if synthesis != "synthesis-ready":
        flags.append(synthesis)
    if tcell == "no_tcell_evidence":
        flags.append("no_tcell_function")
    elif tcell == "immune-context-support":
        flags.append("no_peptide_specific_tcell_function")
    return ";".join(flags) if flags else "none"


def build_immune_evidence_ladder(
    candidates: pd.DataFrame,
    columns: EvidenceColumns | None = None,
) -> pd.DataFrame:
    """Build an A-D immune-evidence tier table from candidate peptide rows."""
    columns = columns or EvidenceColumns()
    required = {"candidate_id", "peptide_sequence", "hla_allele"}
    missing = sorted(required - set(candidates.columns))
    if missing:
        raise ValueError(f"candidate table is missing required columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, row in candidates.iterrows():
        peptide = str(row["peptide_sequence"]).strip().upper()
        hla_class = _text(row, "hla_class", "I")
        synth, synth_flags = synthesis_category(peptide, hla_class)
        presentation, best_match, source_count = presentation_category(row, columns)
        binding = binding_prediction_category(row, columns)
        tcell, tcell_count = tcell_category(row, columns)
        tier = integrated_tier(presentation, binding, synth, tcell)
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "peptide_sequence": peptide,
                "hla_allele": row["hla_allele"],
                "presentation_category": presentation,
                "presentation_source_count": source_count,
                "presentation_best_match_type": best_match,
                "binding_prediction_category": binding,
                "synthesis_category": synth,
                "synthesis_flags": ";".join(synth_flags) if synth_flags else "none",
                "tcell_category": tcell,
                "tcell_source_count": tcell_count,
                "decoy_match_rate": _number(row, columns.decoy_match_rate),
                "candidate_match_rate": _number(row, columns.candidate_match_rate),
                "integrated_tier": tier,
                "allowed_claim": allowed_claim(tier, presentation, tcell),
                "missing_evidence_flags": missing_flags(
                    presentation, binding, synth, tcell
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize_immune_evidence(tiers: pd.DataFrame) -> dict[str, object]:
    """Summarize tier and evidence support for reviewer-facing claim control."""
    if tiers.empty:
        return {
            "total_candidates": 0,
            "tier_counts": {},
            "exact_or_region_tcell_count": 0,
            "presented_count": 0,
            "exact_presentation_count": 0,
            "overlap_presentation_count": 0,
            "mean_candidate_match_rate": 0.0,
            "mean_decoy_match_rate": 0.0,
            "headline_claim": "No candidates were supplied.",
        }

    tier_counts = tiers["integrated_tier"].value_counts().sort_index().to_dict()
    presentation = tiers["presentation_category"]
    tcell = tiers["tcell_category"]
    exact_presentation = presentation == "presented-same-event"
    overlap_presentation = presentation == "presented-overlap"
    tcell_specific = tcell.isin(
        {"tcell-recognized-exact-peptide", "tcell-recognized-region"}
    )

    candidate_match_rate = float(
        tiers.get("candidate_match_rate", pd.Series([0.0])).astype(float).mean()
    )
    decoy_match_rate = float(
        tiers.get("decoy_match_rate", pd.Series([0.0])).astype(float).mean()
    )
    decoy_guard_assessed = max(candidate_match_rate, decoy_match_rate) > 0.0
    decoy_guard_failed = (
        decoy_guard_assessed and decoy_match_rate >= candidate_match_rate
    )
    has_tier_a = (tiers["integrated_tier"] == "A").any()
    has_presented = (exact_presentation | overlap_presentation).any()
    if decoy_guard_failed:
        headline = (
            "Public immune-evidence enrichment is not supported because the "
            "candidate match rate does not exceed the matched-decoy rate; retain "
            "the event-peptide results as a domain-transfer sensitivity analysis."
        )
    elif has_tier_a:
        headline = (
            "At least one candidate has public ligand evidence plus peptide/region "
            "T-cell evidence; claim only public-data-supported prioritization."
        )
    elif has_presented:
        headline = (
            "At least one candidate has public ligand evidence; claim suitability "
            "for future functional testing, not immunogenicity."
        )
    else:
        headline = (
            "No public ligand-supported candidate is present; keep claims at "
            "prediction-only prioritization."
        )

    return {
        "total_candidates": int(len(tiers)),
        "tier_counts": {str(key): int(value) for key, value in tier_counts.items()},
        "exact_or_region_tcell_count": int(tcell_specific.sum()),
        "presented_count": int((exact_presentation | overlap_presentation).sum()),
        "exact_presentation_count": int(exact_presentation.sum()),
        "overlap_presentation_count": int(overlap_presentation.sum()),
        "mean_candidate_match_rate": candidate_match_rate,
        "mean_decoy_match_rate": decoy_match_rate,
        "decoy_guard_status": (
            "failed_candidate_not_above_decoy"
            if decoy_guard_failed
            else "passed_candidate_above_decoy"
            if decoy_guard_assessed
            else "not_assessed"
        ),
        "headline_claim": headline,
    }


def render_claim_audit_markdown(tiers: pd.DataFrame) -> str:
    """Render a concise claim-control report from an immune-evidence tier table."""
    summary = summarize_immune_evidence(tiers)
    tier_counts = summary["tier_counts"]
    tier_lines = [
        f"- Tier {tier}: {tier_counts.get(tier, 0)}"
        for tier in ("A", "B", "C", "D")
    ]
    prohibited = [
        "validated antigen",
        "experimentally confirmed presentation",
        "demonstrated T-cell activation",
        "therapeutic target validated by this study",
    ]
    missing = (
        tiers["missing_evidence_flags"].value_counts().head(8).to_dict()
        if not tiers.empty and "missing_evidence_flags" in tiers.columns
        else {}
    )
    missing_lines = [
        f"- {flag}: {count}" for flag, count in missing.items()
    ] or ["- none"]
    return "\n".join(
        [
            "# Immune Evidence Claim Audit",
            "",
            "## Summary",
            "",
            f"- Total candidates: {summary['total_candidates']}",
            f"- Presented candidates: {summary['presented_count']}",
            f"- Exact public ligand matches: {summary['exact_presentation_count']}",
            f"- Overlap public ligand matches: {summary['overlap_presentation_count']}",
            f"- Peptide/region T-cell evidence: {summary['exact_or_region_tcell_count']}",
            f"- Mean candidate match rate: {summary['mean_candidate_match_rate']:.3f}",
            f"- Mean decoy match rate: {summary['mean_decoy_match_rate']:.3f}",
            f"- Decoy enrichment gate: {summary['decoy_guard_status']}",
            "",
            "## Tier Counts",
            "",
            *tier_lines,
            "",
            "## Allowed Headline Claim",
            "",
            str(summary["headline_claim"]),
            "",
            "## Prohibited Phrases",
            "",
            *[f"- {phrase}" for phrase in prohibited],
            "",
            "## Frequent Missing Evidence Flags",
            "",
            *missing_lines,
            "",
            "## Claim Boundary",
            "",
            (
                "This report audits public evidence and assay-readiness only. It does "
                "not provide new wet-lab immunopeptidome evidence, synthetic peptide "
                "assay results, or T-cell functional validation."
            ),
            "",
        ]
    )
