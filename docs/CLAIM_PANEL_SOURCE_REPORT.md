# PGAA Claim-Panel Source Report

Panel source rows: 53

## Figure Inputs

| Figure | Panel | Rows |
|---|---|---:|
| Figure 1 | decision_benchmark | 37 |
| Figure 2 | calibration_guardrail | 6 |
| Figure 2 | parameter_guardrail | 6 |
| Figure 2 | response_specificity_guardrail | 4 |

## Claim-State and Severity Summary

| Figure | Panel | Claim state | Severity | Rows |
|---|---|---|---|---:|
| Figure 1 | decision_benchmark | comparative_support | low | 9 |
| Figure 1 | decision_benchmark | descriptive_only | moderate | 11 |
| Figure 1 | decision_benchmark | failure_or_guardrail | high | 17 |
| Figure 2 | calibration_guardrail | calibration_support | low | 2 |
| Figure 2 | calibration_guardrail | failure_or_guardrail | critical | 1 |
| Figure 2 | calibration_guardrail | failure_or_guardrail | high | 1 |
| Figure 2 | calibration_guardrail | restricted_use | moderate | 1 |
| Figure 2 | calibration_guardrail | restricted_use | very_high | 1 |
| Figure 2 | parameter_guardrail | calibration_support | low | 1 |
| Figure 2 | parameter_guardrail | failure_or_guardrail | high | 1 |
| Figure 2 | parameter_guardrail | failure_or_guardrail | very_high | 4 |
| Figure 2 | response_specificity_guardrail | comparative_support | low | 1 |
| Figure 2 | response_specificity_guardrail | failure_or_guardrail | high | 1 |
| Figure 2 | response_specificity_guardrail | restricted_use | moderate | 2 |

## Manuscript Use

Use this table as source data for a claim-state figure. Positive benchmark claims should be drawn only from `comparative_support` rows. Guardrail and failure rows should remain visible as method behavior, not hidden exclusions.
