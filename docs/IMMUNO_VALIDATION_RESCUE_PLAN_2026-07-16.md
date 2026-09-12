# PGAA immune-evidence rescue plan without wet-lab experiments

## Current blocker

The manuscript cannot claim experimentally validated antigen presentation or T-cell immunogenicity because it lacks three direct evidence classes:

1. immunopeptidomics evidence that the same molecular event produces an actually presented peptide;
2. synthetic-peptide confirmation of the nominated peptide sequence;
3. T-cell functional validation such as activation, cytokine release, killing, or tetramer binding.

Without new wet-lab work, these gaps cannot be closed as validation. The defensible rescue is to convert them into a fully auditable computational evidence ladder and to downgrade claims from "validated antigen" to "prioritized, externally supported antigen candidate".

## Rescue principle

Every candidate must be treated as an event-peptide-HLA-T-cell evidence unit, not as a gene-level hit. The unit should contain:

- source event: mutation, fusion, splice junction, editing site, aberrant ORF, or other PGAA-ranked event;
- derived peptide sequence and genomic/protein coordinate;
- HLA allele or allele group;
- presentation evidence;
- synthetic feasibility evidence;
- T-cell evidence;
- negative and missing evidence flags.

If any layer is absent, the final label must preserve that absence. The manuscript can gain rigor by showing exactly where evidence is present and absent, but it cannot imply that missing wet-lab validation has been performed.

## Evidence layer 1: same-event immunopeptidome presentation

Goal: show that the same event or an indistinguishable peptide has support in public HLA ligand or immunopeptidomics resources.

Computational upgrades:

- Build an event-to-peptide table for all PGAA candidates using fixed 8-11mer HLA-I and 12-25mer HLA-II windows, with the event residue or junction position recorded.
- Search exact peptide matches first. Exact same peptide, same HLA allele, and same disease or tissue context is the strongest public-data substitute.
- Then allow conservative near-event evidence only if explicitly separated from exact evidence:
  - same peptide, different compatible HLA;
  - same event region, overlapping peptide;
  - same source protein and disease context but different peptide.
- Add decoy searches from matched non-event peptides to estimate how often similar public matches occur by chance.
- Report unmatched candidates as unmatched, not as failed validation.

Minimum claim categories:

| Category | Required evidence | Allowed wording |
|---|---|---|
| Presented-same-event | Exact peptide or junction-containing peptide appears in public immunopeptidomics/HLA ligand evidence with compatible HLA. | Public ligand evidence supports presentation of the same event-derived peptide. |
| Presented-overlap | Overlapping event-region peptide or compatible source-region peptide appears, but exact peptide is absent. | Public ligand evidence supports presentation of the event region, not the exact nominated peptide. |
| Binding-only | Binding/presentation predictors support HLA compatibility, but no public ligand match exists. | Candidate is computationally predicted to be presentable. |
| No presentation evidence | No public ligand match and weak predictor support. | Candidate remains unsupported at the presentation layer. |

Pass gate for a stronger manuscript section:

- At least one high-priority candidate reaches `Presented-same-event`, or
- A predeclared subgroup has enrichment over decoys for public ligand overlap, with exact counts and confidence intervals.

Failure handling:

- If no candidate reaches exact or overlap evidence, the result should be framed as a negative audit showing that PGAA nominations are not yet supported by public ligand evidence.

## Evidence layer 2: synthetic-peptide verification substitute

Goal: replace missing synthetic peptide testing with transparent synthesizability and assay-readiness triage. This is not validation; it is a prioritization layer for future wet-lab follow-up.

Computational upgrades:

- Score each peptide for length, unusual residues, cysteine count, methionine/oxidation risk, hydrophobic run length, charge, predicted solubility, and manufacturability risk.
- Add HLA binding and stability predictions for the exact alleles observed or inferred in the relevant cohort.
- Add proteasomal cleavage/TAP transport predictions for HLA-I candidates if supported by the selected toolchain.
- Mark peptides that are difficult to synthesize or assay as lower follow-up priority even if their PGAA event score is high.
- Create a "synthesis panel" of 20-50 candidates split across:
  - strongest PGAA score;
  - strongest presentation support;
  - strongest T-cell external evidence;
  - negative/decoy controls;
  - HLA-diverse candidates.

Minimum claim categories:

| Category | Required evidence | Allowed wording |
|---|---|---|
| Synthesis-ready | Clean length, no major chemistry liabilities, strong HLA compatibility, clear event coordinate. | Candidate is suitable for direct peptide synthesis and immune assay design. |
| Synthesis-caution | One or more moderate liabilities but still assayable. | Candidate is feasible but lower priority. |
| Synthesis-risk | Major sequence or assay-design liabilities. | Candidate should not be advanced without redesign. |

Pass gate for a stronger manuscript section:

- The final candidate panel includes positive candidates and matched negative controls, with no hidden exclusions.
- Every panel peptide has exact sequence, event coordinate, HLA, predicted binding/stability, and synthesis-risk fields.

Failure handling:

- If top PGAA candidates are not synthesis-ready, this should be reported as a practical translational limitation rather than filtered away.

## Evidence layer 3: T-cell functional evidence substitute

Goal: use public immune-recognition evidence to support plausibility, while making clear that no new T-cell activation experiment was performed.

Computational upgrades:

- Query public epitope/TCR resources for exact peptide matches, source-protein matches, disease-context matches, and HLA-restricted immune recognition.
- Separate four evidence levels:
  - exact peptide with documented T-cell response;
  - same source event or overlapping peptide with response;
  - source-protein immune recognition but not the exact peptide;
  - pathway/context immune plausibility only.
- Add TCR repertoire or cytotoxicity-context evidence only if the same disease cohort or public dataset contains clonotype expansion, cytotoxic T-cell markers, or antigen-presentation machinery signals.
- Use negative controls: random peptides from matched proteins and housekeeping proteins should not show comparable immune-recognition support.
- Avoid saying "immunogenic" unless exact peptide-level T-cell response evidence exists in public data.

Minimum claim categories:

| Category | Required evidence | Allowed wording |
|---|---|---|
| T-cell-recognized exact peptide | Exact peptide-HLA pair has public T-cell response evidence. | Public evidence supports T-cell recognition of this peptide-HLA pair. |
| T-cell-recognized region | Overlapping/source-region peptide has public response evidence. | Public evidence supports immune recognition of the event region, not the exact PGAA peptide. |
| Immune-context support | Cytotoxic/T-cell activation context supports plausibility, without peptide specificity. | Candidate lies in an immune-active context. |
| No T-cell evidence | No public response or repertoire support. | Candidate lacks T-cell functional support. |

Pass gate for a stronger manuscript section:

- At least one candidate reaches exact or region-level public T-cell evidence, or
- The candidate set shows predeclared enrichment for immune-recognition resources over matched decoys.

Failure handling:

- If T-cell evidence is absent, the manuscript should explicitly state that the work prioritizes candidates for future functional validation.

## Integrated evidence score

The rescue should not produce a single opaque score. Use a transparent ladder:

| Tier | Required layers | Interpretation |
|---|---|---|
| A | Same-event presentation + synthesis-ready + exact/region T-cell evidence | Strong public-data-supported follow-up candidate; still not newly validated. |
| B | Presentation evidence + synthesis-ready, but no T-cell evidence | Presented candidate suitable for functional testing. |
| C | Binding-only + synthesis-ready + immune-context support | Plausible candidate, lower priority. |
| D | Any major missing layer or synthesis-risk | Exploratory candidate only. |

This ladder should be reported alongside the raw evidence columns so reviewers can see why each candidate was assigned its tier.

## Journal-position impact

If no wet-lab work is possible, the realistic ceiling depends on the completed computational evidence:

| Evidence achieved | Realistic positioning |
|---|---|
| Current PGAA-only rankings without immune evidence | Computational method/software journal or lower-risk specialty bioinformatics venue. |
| Full evidence ladder with negative controls and public ligand/T-cell audit, but few exact matches | Bioinformatics-method or translational-informatics venue; claims must be conservative. |
| Multiple candidates with same-event ligand evidence and public T-cell recognition, plus robust decoy enrichment | Stronger computational immunology story, but still below papers with new peptide/T-cell experiments. |
| New prospective wet-lab validation added later | Enables much higher immunology/translational positioning. |

The strongest no-wet-lab manuscript is therefore not "PGAA discovers validated antigens"; it is "PGAA prioritizes event-derived antigen candidates through a calibrated, failure-preserving public-evidence ladder."

## Immediate implementation tasks

1. Create `event_sequence_contexts.tsv` with one row per real molecular event, including altered amino-acid sequence context, zero-based event index, HLA allele, PGAA rank, and source dataset.
2. Compile `candidate_event_peptides.tsv` and matched decoys:
   - Smoke example: `python3 scripts/compile_event_peptides.py --events evidence/event_sequence_contexts_template.tsv --candidates-out evidence/event_compiler_smoke_candidates.tsv --decoys-out evidence/event_compiler_smoke_decoys.tsv --allow-smoke`
   - Real manuscript run: replace the template with real event contexts and omit `--allow-smoke`.
3. Add exact/overlap public immunopeptidome matching fields.
4. Add binding, stability, cleavage/TAP, and synthesis-risk fields.
5. Add public T-cell evidence fields with exact, overlap, source-protein, and context levels.
6. Run the same evidence search on matched decoy peptides.
7. Run the local evidence-ladder builder:
   - Smoke example: `python3 scripts/build_immune_evidence_ladder.py --candidates evidence/immune_evidence_smoke_candidates.tsv --ligand-evidence evidence/public_ligand_evidence_template.tsv --tcell-evidence evidence/public_tcell_evidence_template.tsv --decoys evidence/decoy_peptides_template.tsv --annotated-candidates evidence/immune_evidence_smoke_annotated.tsv --output evidence/immune_evidence_tiers_smoke.tsv --claim-audit docs/IMMUNO_EVIDENCE_CLAIM_AUDIT_SMOKE.md --allow-smoke`
   - Real manuscript run: replace the smoke/template inputs with real PGAA candidate, ligand, T-cell, and decoy tables; omit `--allow-smoke` so the script fails on leftover placeholder tokens.
8. Produce `immune_evidence_tiers.tsv` and one summary figure:
   - stacked bar of tier counts;
   - evidence heatmap for top candidates;
   - decoy comparison for ligand/T-cell matches.
9. Produce `docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md` with `--claim-audit` and use it as the hard boundary for manuscript wording.
10. Rewrite manuscript claims so every sentence distinguishes prediction, public support, and experimental validation.
