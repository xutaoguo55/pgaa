# PGAA External Claim-State Rerun Contract

This report defines the executable contract for an external PGAA/comparator claim-state rerun. It is not replication evidence; it becomes evidence only after the commands are run and the external claim-state audit is produced.

## Summary

| Readiness gate | Contract status | Allowed use | Targets |
|---|---|---|---:|
| ready_for_external_claim_state_rerun | ready_for_pgaa_input_extraction | execution_contract_not_replication | 4 |

## Target Contract

| Target | Status | PGAA-W output | PGAA-H output | Claim-state output |
|---|---|---|---|---|
| BHLHE40 | ready_for_pgaa_input_extraction | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/BHLHE40.s1.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/BHLHE40.s2.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/external_claim_state.tsv |
| CREB1 | ready_for_pgaa_input_extraction | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/CREB1.s1.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/CREB1.s2.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/external_claim_state.tsv |
| DDIT3 | ready_for_pgaa_input_extraction | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/DDIT3.s1.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/DDIT3.s2.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/external_claim_state.tsv |
| ZNF326 | ready_for_pgaa_input_extraction | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/ZNF326.s1.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/ZNF326.s2.csv | /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/external_claim_state.tsv |

## PGAA Commands

### BHLHE40

```bash
python3 -m pgaa.cli --expression /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/expression.csv --metadata /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/metadata.csv --target BHLHE40 --out-prefix /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/BHLHE40/BHLHE40 --group-column group --perturbed-value perturbed --control-value control --n-perms 2000 --n-bins 20 --target-only-permutation-p
```

### CREB1

```bash
python3 -m pgaa.cli --expression /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/expression.csv --metadata /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/metadata.csv --target CREB1 --out-prefix /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/CREB1/CREB1 --group-column group --perturbed-value perturbed --control-value control --n-perms 2000 --n-bins 20 --target-only-permutation-p
```

### DDIT3

```bash
python3 -m pgaa.cli --expression /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/expression.csv --metadata /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/metadata.csv --target DDIT3 --out-prefix /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/DDIT3/DDIT3 --group-column group --perturbed-value perturbed --control-value control --n-perms 2000 --n-bins 20 --target-only-permutation-p
```

### ZNF326

```bash
python3 -m pgaa.cli --expression /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/expression.csv --metadata /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/metadata.csv --target ZNF326 --out-prefix /Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/ZNF326/ZNF326 --group-column group --perturbed-value perturbed --control-value control --n-perms 2000 --n-bins 20 --target-only-permutation-p
```


## Claim Boundary

A `ready_for_pgaa_input_extraction` row only authorizes input extraction and PGAA/comparator rerun. It does not authorize a manuscript replication claim until the external claim-state output exists and agrees with the predeclared internal responder-state unit.

The external rerun command keeps full-gene observed PGAA-W and PGAA-H ranks, while restricting PGAA-W permutation p-value estimation to the perturbation target gene used by the claim-state rule.
