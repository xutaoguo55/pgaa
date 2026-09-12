# Multi-level Decoy Enrichment Audit

Verdict: `MIXED_DECOY_SENSITIVITY_NO_GLOBAL_ENRICHMENT_CLAIM`

| Group | Hits / total | Rate | Gate | Fisher p |
|---|---:|---:|---|---:|
| candidate | 5830 / 5830 | 1.000000 | reference_candidate_group | 1 |
| composition_matched_shuffle | 0 / 5830 | 0.000000 | passed_candidate_above_decoy | 0 |
| cross_event_length_class_matched | 398 / 5827 | 0.068303 | passed_candidate_above_decoy | 0 |
| same_context_non_event_window | 853 / 853 | 1.000000 | failed_candidate_not_above_decoy | 1 |

## Interpretation

A decoy family is passed only when the candidate Wilson interval is entirely above the decoy interval and the one-sided Fisher test is below 0.05.

Any failed decoy family blocks a global enrichment claim. Because the candidate set originates from previously validated events, separation is a positive-control property of the evidence-matching layer, not PGAA discovery evidence.
