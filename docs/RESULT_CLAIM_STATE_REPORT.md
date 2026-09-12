# PGAA Result-Claim State Report

Claim rows: 53

## Claim-State Summary

| Figure panel | Result claim state | Rows |
|---|---|---:|
| calibration_guardrail | calibration_support | 2 |
| calibration_guardrail | failure_or_guardrail | 2 |
| calibration_guardrail | restricted_use | 2 |
| decision_benchmark | comparative_support | 9 |
| decision_benchmark | descriptive_only | 11 |
| decision_benchmark | failure_or_guardrail | 17 |
| parameter_guardrail | calibration_support | 1 |
| parameter_guardrail | failure_or_guardrail | 5 |
| response_specificity_guardrail | comparative_support | 1 |
| response_specificity_guardrail | failure_or_guardrail | 1 |
| response_specificity_guardrail | restricted_use | 2 |

## Manuscript Use

`comparative_support` rows can support bounded benchmark statements. `descriptive_only` rows can be reported but should not carry superiority language. `failure_or_guardrail` and `restricted_use` rows are part of the method object: they define when PGAA outputs should be limited, rejected, or shown as failure modes.
