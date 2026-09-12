"""Rebuild the GSE75602 resistance-module biology audit."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


THEME_SPECS = (
    {
        "theme": "iron_handling",
        "example_gene_or_term": "CP; SLC40A1; HFE; TFRC; STEAP4",
        "evidence": "Iron uptake and transport / defective CP / HFE4 enrichment",
        "p_value_term": "Iron uptake and transport",
        "interpretation": "transferable iron-homeostasis program",
        "genes": ("CP", "SLC40A1", "HFE", "TFRC", "STEAP4"),
    },
    {
        "theme": "carbonic_anhydrase_and_pH",
        "example_gene_or_term": "CA9; CA12; CA2",
        "evidence": "Reversible hydration of carbon dioxide",
        "p_value_term": "Reversible hydration of carbon dioxide",
        "interpretation": "pH-adaptation component",
        "genes": ("CA9", "CA12", "CA2"),
    },
    {
        "theme": "vdr_axis",
        "example_gene_or_term": "CYP24A1; vitamin D receptor pathway",
        "evidence": "Vitamin D receptor pathway",
        "p_value_term": "Vitamin D receptor pathway",
        "interpretation": "differentiation/metabolic-control component",
        "genes": ("CYP24A1",),
    },
    {
        "theme": "epithelial_stress_state",
        "example_gene_or_term": "RARRES1; STC1; PSCA; HOPX; ELF5; MUC6; KRT4; KRT13",
        "evidence": "annotated module membership",
        "p_value_term": None,
        "interpretation": "epithelial stress/differentiation signature",
        "genes": ("RARRES1", "STC1", "PSCA", "HOPX", "ELF5", "MUC6", "KRT4", "KRT13"),
    },
    {
        "theme": "redox_or_metabolic_state",
        "example_gene_or_term": "BCAS1; SERPINE1; LRG1; CYP26A1",
        "evidence": "annotated module membership",
        "p_value_term": None,
        "interpretation": "redox/metabolic support signature",
        "genes": ("BCAS1", "SERPINE1", "LRG1", "CYP26A1"),
    },
)


def _require_genes(annotation: pd.DataFrame) -> set[str]:
    if "display_name" not in annotation.columns:
        raise ValueError("Annotation table is missing a display_name column")
    present = {
        str(value)
        for value in annotation["display_name"].fillna("").astype(str)
        if str(value).strip()
    }
    missing = sorted(
        gene
        for spec in THEME_SPECS
        for gene in spec["genes"]
        if gene not in present
    )
    if missing:
        raise ValueError(f"Annotation table is missing representative genes: {missing}")
    return present


def _lookup_pathway_p_value(pathway_enrichment: pd.DataFrame, term: str) -> str:
    if "name" not in pathway_enrichment.columns or "p_value" not in pathway_enrichment.columns:
        raise ValueError("Pathway table must contain name and p_value columns")
    matched = pathway_enrichment.loc[pathway_enrichment["name"].astype(str).eq(term)]
    if matched.empty:
        raise ValueError(f"Pathway table is missing required term: {term}")
    return f"{float(matched.iloc[0]['p_value']):.6f}"


def build_module_biology_summary(
    annotation: pd.DataFrame,
    pathway_enrichment: pd.DataFrame,
) -> pd.DataFrame:
    """Build the compact mechanism summary from the evidence tables."""
    _require_genes(annotation)
    rows: list[dict[str, str]] = []
    for spec in THEME_SPECS:
        rows.append(
            {
                "theme": spec["theme"],
                "example_gene_or_term": spec["example_gene_or_term"],
                "evidence": spec["evidence"],
                "p_value": (
                    _lookup_pathway_p_value(pathway_enrichment, spec["p_value_term"])
                    if spec["p_value_term"] is not None
                    else "n/a"
                ),
                "interpretation": spec["interpretation"],
            }
        )
    return pd.DataFrame(rows)


def _render_gene_theme_bullets() -> str:
    lines: list[str] = []
    for spec in THEME_SPECS:
        lines.append(f"- `{spec['theme']}`: {spec['example_gene_or_term']}")
    return "\n".join(lines)


def _render_pathway_table(pathway_enrichment: pd.DataFrame) -> str:
    selected_terms = [
        spec["p_value_term"] for spec in THEME_SPECS if spec["p_value_term"] is not None
    ]
    selected = pathway_enrichment.loc[pathway_enrichment["name"].astype(str).isin(selected_terms)].copy()
    if selected.empty:
        return "No matching pathway rows were found."
    selected["p_value"] = selected["p_value"].map(lambda value: f"{float(value):.6f}")
    selected = selected.loc[:, ["name", "p_value", "term_size", "intersection_size"]]
    selected = selected.rename(columns={"name": "example_pathway_or_term"})
    return selected.to_csv(sep="\t", index=False).strip()


def render_module_biology_audit(
    summary: pd.DataFrame,
    pathway_enrichment: pd.DataFrame,
) -> str:
    """Render the manuscript-facing audit document."""
    return "\n".join(
        [
            "# GSE75602 Resistance Module Biology Audit",
            "",
            "Date: 2026-08-03",
            "",
            "## Purpose",
            "",
            "This audit records the biological themes carried by the locked `shared_resistance_down_module` so the manuscript can explain the module as more than a purely statistical transfer result.",
            "",
            "## Module composition",
            "",
            "The 50-gene down module selected from `GSE75602` is dominated by genes associated with:",
            "",
            "- iron handling and transport,",
            "- carbonic-anhydrase / pH adaptation,",
            "- epithelial differentiation and stress-state markers,",
            "- VDR-linked metabolic signaling.",
            "",
            "Representative members from the annotated module include:",
            "",
            _render_gene_theme_bullets(),
            "",
            "## Pathway enrichment",
            "",
            "The locked 50-gene down module is enriched for the following pathway themes:",
            "",
            _render_pathway_table(pathway_enrichment),
            "",
            "## Interpretation",
            "",
            "The module is biologically coherent, but the enrichment structure is fragmented and driven by a small number of recurring themes. That is enough to support a mechanistic hypothesis, not enough to relabel the module as T790M-specific or to claim a single pathway driver.",
            "",
            "The most defensible manuscript interpretation is:",
            "",
            "- the locked `shared_resistance_down_module` is a transferable resistance-state program;",
            "- its leading biology points to iron homeostasis, pH adaptation, and epithelial stress/differentiation;",
            "- the module transfers across clone-level systems even though same-cell T790M directionality remains unresolved;",
            "- pathway biology should be described as supportive context, not as the primary discovery claim.",
            "",
            "## Manuscript use",
            "",
            "This audit supports a mechanism paragraph in the Discussion and a supplemental pathway annotation table, but it does not change the claim ceiling or the route gate.",
            "",
            "## Summary Table",
            "",
            summary.to_csv(sep="\t", index=False).strip(),
            "",
        ]
    )


def write_module_biology_audit_package(
    annotation_path: Path,
    pathway_enrichment_path: Path,
    summary_out: Path,
    report_out: Path,
) -> dict[str, Path]:
    """Write the summary table and audit markdown from source evidence tables."""
    annotation = pd.read_csv(annotation_path, sep="\t")
    pathway_enrichment = pd.read_csv(pathway_enrichment_path, sep="\t")
    summary = build_module_biology_summary(annotation, pathway_enrichment)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_out, sep="\t", index=False)
    report_out.write_text(
        render_module_biology_audit(summary, pathway_enrichment),
        encoding="utf-8",
    )
    return {"summary": summary_out, "report": report_out}
