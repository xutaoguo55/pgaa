# PGAA Responder-State Stability Report

Responder-state units audited: 8
Leave-one-method checks: 37

## Stability Classes

| Stability class | Cross-dataset status | Units |
|---|---|---:|
| leave_one_method_stable | no_cross_dataset_same_context | 4 |
| method_sensitive | no_cross_dataset_same_context | 3 |
| pgaa_support_dependent | no_cross_dataset_same_context | 1 |

## Manuscript Use

`leave_one_method_stable` units can be shown as more robust examples. `pgaa_support_dependent` and `support_method_dependent` units should be framed as method-sensitive and must keep their omitted-method diagnostics visible. `no_cross_dataset_same_context` means the current repository does not yet prove same-context replication across datasets.
