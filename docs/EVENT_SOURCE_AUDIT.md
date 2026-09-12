# PGAA Event-Source Audit

Event-ready source tables: 1
Gene-level-only source tables: 3

| Source | Status | Rows inspected | Detail |
|---|---|---:|---|
| `norman_multi_perturbation_gene_scores` | gene_level_only | 5000 | gene-level PGAA/expression columns present (['gene', 's1_wasserstein', 'target']); missing event columns: ['altered_sequence_context', 'event_coordinate', 'event_index', 'hla_allele', 'hla_class', 'source_event_id', 'source_event_type', 'source_gene'] |
| `adamson_gene_level_scores` | gene_level_only | 5000 | gene-level PGAA/expression columns present (['S2', 'W_observed', 'gene', 'perturbation', 'target_gene']); missing event columns: ['altered_sequence_context', 'event_coordinate', 'event_index', 'hla_allele', 'hla_class', 'source_event_id', 'source_event_type', 'source_gene'] |
| `cebpe_real_results` | gene_level_only | 5000 | gene-level PGAA/expression columns present (['fdr', 'gene', 'p_value']); missing event columns: ['altered_sequence_context', 'event_coordinate', 'event_index', 'hla_allele', 'hla_class', 'source_event_id', 'source_event_type', 'source_gene'] |
| `event_sequence_context_template` | event_template_or_smoke | 1 | event_sequence_context_template.source_event_id:SMOKE:SMOKE_EVENT_1; event_sequence_context_template.source_gene:SMOKE:SMOKE1; event_sequence_context_template.cohort_or_dataset:SMOKE:smoke_dataset; event_sequence_context_template.disease_or_context:SMOKE:smoke_context |
| `tsnadb_v2_validated_events` | event_ready | 1271 | required event columns present and no smoke/template tokens detected |

## Interpretation

At least one inspected source table has the required event compiler columns. Run `scripts/compile_event_peptides.py` on those rows after manual source review.
