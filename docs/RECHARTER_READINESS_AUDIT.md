# PGAA Recharter Readiness Audit

Verdict: `READY_FOR_RECHARTER_MANUSCRIPT_DRAFT`

| Check | Status | Artifact | Detail |
|---|---|---|---|
| real_event_contexts | ready | `evidence/event_sequence_contexts.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_candidate_peptides | ready | `evidence/candidate_event_peptides.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_ligand_evidence | ready | `evidence/public_ligand_evidence.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_tcell_evidence | ready | `evidence/public_tcell_evidence.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_decoys | ready | `evidence/decoy_peptides.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_tier_table | ready | `evidence/immune_evidence_tiers.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_claim_audit | ready | `docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md` | artifact exists |
| real_panel_summary | ready | `evidence/followup_panel_summary.tsv` | artifact exists, required columns present, no smoke/template tokens detected |
| real_threshold_summary | ready | `evidence/threshold_robustness_summary.tsv` | artifact exists, required columns present, no smoke/template tokens detected |

## Blocking Interpretation

All required real artifacts are present and free of smoke/template tokens.

This audit checks artifact readiness only. It does not prove biological validity, wet-lab validation, or journal acceptance.
