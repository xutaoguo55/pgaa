# PC9 Third-System Blocker Audit

Date: 2026-08-02

## Purpose

This audit documents why the current manuscript does not yet have a third independent PC9 evolution system that can be counted as direct evidence for submission-level closure.

## Evaluated Candidate Systems

| Candidate | Current contract status | Why it does not close the gap | Manuscript use |
|---|---|---|---|
| `aissa2021_pc9_drug` | `metadata_contract_error` | The source table shows a single recorded batch, and the contract requires at least two batches for held-out replication. | Cannot be treated as a third independent evolution system. |
| `chang2021_pc9_drug` | `below_minimum_units` | The candidate is present in the queue, but it does not satisfy the minimum selected-units gate for a usable held-out replication contract. | Cannot be treated as a third independent evolution system. |
| `GSE150949` | `strong_partial_support` | The public matrix retains 45 of the 50 frozen down-module genes, and the late day-14 subtype groups stay below day 0, but day 3 and day 7 remain mixed so the route does not cleanly close. | Can be used as the strongest local partial-support candidate, not as a closed third-system route. |
| `GSE103350` | `mixed_direction_partial_support` | The raw-count tables are real and analyzable, but the current frozen adaptive-stress minus replication axis stays negative across all samples; treatment/tolerance states move toward zero and do not cleanly preserve the locked third-system route. | Can be used only as a partial or negative candidate unless the axis contract is re-framed. |

## Interpretation

The local package already contains a clear branch-vulnerability mainline and a bounded fifth-system dynamic support layer, but no currently available PC9 drug dataset closes the remaining third-system gap.

`GSE150949` is the strongest local PC9 evolution candidate because it keeps the late day-14 subtype groups below day 0 while carrying 45 of the 50 frozen down-module genes. However, the early day 3 and day 7 states remain mixed, so it still does not close the gap without a new module definition or a different route contract.

`GSE103350` is the most informative additional tolerance-oriented candidate because it does have real raw counts and a meaningful PC9/HCC827 EGFR-TKI structure. However, under the current frozen branch axis it remains on the negative side, so it does not close the gap without a new module definition or a different route contract.

That means the manuscript can say:

- the PC9 ATM/HDAC branch-vulnerability line is the current mainline;
- GSE335846 remains rank-level dynamic support until source tables or a prospective experiment are available;
- GSE150949 is the strongest local third-system support candidate, but it is still partial rather than closed;
- additional PC9 drug candidates exist, but they are currently blocked by contract constraints;
- the next publication-grade upgrade is still a source-level GSE335846 release or a prospective branch-by-treatment experiment.

## Bottom Line

This audit does not add new biological evidence. It makes the current gap explicit and prevents overcounting blocked PC9 candidates as independent validation.
