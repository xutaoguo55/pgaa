# PGAA External Execution Manifest

This report audits whether external PGAA rerun inputs and outputs exist. It is not replication evidence; replication claims require compiled external claim-state outputs and agreement with predeclared internal responder-state units.

## Summary

| Contract status | Extraction status | Execution status | Allowed use | Targets |
|---|---|---|---|---:|
| ready_for_pgaa_input_extraction | extracted_pgaa_cli_inputs | external_claim_state_present | execution_manifest_not_replication | 4 |

## Target Manifest

| Target | Execution status | Inputs present | PGAA outputs present | Claim-state present |
|---|---|---|---|---|
| BHLHE40 | external_claim_state_present | True | True | True |
| CREB1 | external_claim_state_present | True | True | True |
| DDIT3 | external_claim_state_present | True | True | True |
| ZNF326 | external_claim_state_present | True | True | True |

## Claim Boundary

A `ready_for_pgaa_cli_execution` row means the audited input files and command exist. It does not mean PGAA has been run, and it does not support external replication until both PGAA outputs and the external claim-state audit exist.
