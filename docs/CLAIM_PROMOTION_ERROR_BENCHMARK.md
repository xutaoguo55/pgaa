# Claim-Promotion Error Benchmark

## Scope

The benchmark exhaustively evaluates 960 finite-state scenarios across 8 observed decision units. Each scenario changes zero, one, or multiple evidence gates while holding the originating unit identity fixed.

This is a contract stress test, not an empirical ground-truth benchmark. The oracle is the predeclared permission contract. It tests whether a reporting strategy obeys that contract when evidence states change; it does not establish that the contract is biologically correct.

## Overall Results

| Method | Scenarios | False promotion | Replication false positive | Under-promotion | Exact permission | Replication sensitivity |
|---|---:|---:|---:|---:|---:|---:|
| `claim_state_compiler` | 960 | 0.0% | 0.0% | 0.0% | 100.0% | 100.0% |
| `state_blind_frozen_baseline` | 960 | 70.4% | 50.0% | 12.6% | 17.0% | 50.0% |
| `decision_only_baseline` | 960 | 0.0% | 0.0% | 0.8% | 99.2% | 0.0% |
| `external_only_baseline` | 960 | 19.2% | 19.3% | 0.0% | 80.8% | 100.0% |

## Comparator Definitions

- `claim_state_compiler`: recomputes permission from decision, stability, and external state.
- `state_blind_frozen_baseline`: preserves the observed permission rank when evidence-gate metadata change. It is a deliberately favorable frozen-output proxy for reporting that does not update claims when evidence gates change, not a universal raw-score threshold.
- `decision_only_baseline`: uses the internal decision state but cannot grant replication permission.
- `external_only_baseline`: grants replication permission from external concordance without checking internal support or stability.

## Interpretation

A false promotion occurs when a method emits a permission rank above the contract ceiling. Under-promotion records the converse, so a conservative method cannot appear optimal merely by blocking every claim. Replication sensitivity is measured only among contract-eligible states; replication false-positive rate is measured only among ineligible states.

The compiler's zero-error result is expected because this experiment verifies implementation fidelity to the declared contract. Evidence of empirical superiority requires independent annotations, additional datasets, or prospective reviewer/author decisions that were not used to define the oracle.
