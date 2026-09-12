# GSE75602 Resistance Module Biology Audit

Date: 2026-08-03

## Purpose

This audit records the biological themes carried by the locked `shared_resistance_down_module` so the manuscript can explain the module as more than a purely statistical transfer result.

## Module composition

The 50-gene down module selected from `GSE75602` is dominated by genes associated with:

- iron handling and transport,
- carbonic-anhydrase / pH adaptation,
- epithelial differentiation and stress-state markers,
- VDR-linked metabolic signaling.

Representative members from the annotated module include:

- `iron_handling`: CP; SLC40A1; HFE; TFRC; STEAP4
- `carbonic_anhydrase_and_pH`: CA9; CA12; CA2
- `vdr_axis`: CYP24A1; vitamin D receptor pathway
- `epithelial_stress_state`: RARRES1; STC1; PSCA; HOPX; ELF5; MUC6; KRT4; KRT13
- `redox_or_metabolic_state`: BCAS1; SERPINE1; LRG1; CYP26A1

## Pathway enrichment

The locked 50-gene down module is enriched for the following pathway themes:

example_pathway_or_term	p_value	term_size	intersection_size
Reversible hydration of carbon dioxide	0.009343	7	2
Iron uptake and transport	0.020301	51	3
Vitamin D receptor pathway	0.031766	134	4

## Interpretation

The module is biologically coherent, but the enrichment structure is fragmented and driven by a small number of recurring themes. That is enough to support a mechanistic hypothesis, not enough to relabel the module as T790M-specific or to claim a single pathway driver.

The most defensible manuscript interpretation is:

- the locked `shared_resistance_down_module` is a transferable resistance-state program;
- its leading biology points to iron homeostasis, pH adaptation, and epithelial stress/differentiation;
- the module transfers across clone-level systems even though same-cell T790M directionality remains unresolved;
- pathway biology should be described as supportive context, not as the primary discovery claim.

## Manuscript use

This audit supports a mechanism paragraph in the Discussion and a supplemental pathway annotation table, but it does not change the claim ceiling or the route gate.

## Summary Table

theme	example_gene_or_term	evidence	p_value	interpretation
iron_handling	CP; SLC40A1; HFE; TFRC; STEAP4	Iron uptake and transport / defective CP / HFE4 enrichment	0.020301	transferable iron-homeostasis program
carbonic_anhydrase_and_pH	CA9; CA12; CA2	Reversible hydration of carbon dioxide	0.009343	pH-adaptation component
vdr_axis	CYP24A1; vitamin D receptor pathway	Vitamin D receptor pathway	0.031766	differentiation/metabolic-control component
epithelial_stress_state	RARRES1; STC1; PSCA; HOPX; ELF5; MUC6; KRT4; KRT13	annotated module membership	n/a	epithelial stress/differentiation signature
redox_or_metabolic_state	BCAS1; SERPINE1; LRG1; CYP26A1	annotated module membership	n/a	redox/metabolic support signature
