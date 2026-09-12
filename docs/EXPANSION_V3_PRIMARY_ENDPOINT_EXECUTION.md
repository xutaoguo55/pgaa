# Expansion v3 Primary Endpoint Execution

## Frozen Primary Endpoint

The primary endpoint is the cross-platform dual-gate state for the combined expansion-v3 ready panel.

Frozen cohort gate:
- Minimum prospective platforms: 10
- Current ready platforms: 14
- Current ready selected units: 224
- Current laboratory groups: 11
- Current cell-context classes: 13
- Current perturbation-mechanism classes: 5

Frozen scoring parameters:
- max_units: 16
- max_cells_per_group: 70
- min_cells_per_group: 20
- max_features: 5000
- top_k: 100
- n_repeats: 5

Frozen promotion rule:
- primary method: pgaa_w
- primary event: stable_and_specific
- minimum stable-and-specific platforms: 4
- minimum event mechanism classes: 3
- minimum event cell-context classes: 4
- minimum leave-one-platform-out event count: 3

## Execution Contract

Raw h5ad sources remain on the USB volume under `/Volumes/MOVESPEED`. The local repository stores only contracts, execution plans, scores, summaries, and claim-state tables.

Current execution-plan artifact:
- `evidence/expansion_v3_ready_panel_execution_plan.tsv`

The dry-run check currently reports 14 ready platforms, 14 available sources, and 8.56 GiB of source h5ad files.

## Output Names

Primary endpoint outputs are reserved for frozen-parameter runs only:
- `evidence/expansion_v3_ready_panel_scored_contract.tsv`
- `evidence/expansion_v3_ready_panel_dual_gate_detail.tsv`
- `evidence/expansion_v3_ready_panel_dual_gate_target_summary.tsv`
- `evidence/expansion_v3_ready_panel_dual_gate_method_summary.tsv`
- `evidence/expansion_v3_ready_panel_dual_gate_states.tsv`
- `evidence/expansion_v3_ready_panel_primary_endpoint_claim_state.tsv`

Reduced-parameter checks must use a separate `--analysis-prefix`. The script blocks non-frozen scoring parameters when the default primary prefix is used.

## Completed Smoke Test

A reduced-parameter expression-scoring smoke test has been completed for:
- `datlinger2017_jurkat_crispr`

Smoke-test outputs are explicitly prefixed:
- `evidence/expansion_v3_ready_panel_smoke_datlinger_scored_contract.tsv`
- `evidence/expansion_v3_ready_panel_smoke_datlinger_dual_gate_detail.tsv`
- `evidence/expansion_v3_ready_panel_smoke_datlinger_dual_gate_target_summary.tsv`
- `evidence/expansion_v3_ready_panel_smoke_datlinger_dual_gate_method_summary.tsv`
- `evidence/expansion_v3_ready_panel_smoke_datlinger_dual_gate_states.tsv`
- `evidence/expansion_v3_ready_panel_smoke_datlinger_primary_endpoint_claim_state.tsv`

This smoke test confirms that the h5ad adapter, scoring path, summarizer, and endpoint compiler run through for a real external dataset. It is not a primary endpoint result.

## Current Claim Boundary

Supported now:
- The frozen metadata contract yields 14 ready external perturbation platforms across independent laboratories, cell contexts, and perturbation mechanisms.
- The ready-panel scoring script can run a real external h5ad source end to end.
- The script protects the primary endpoint namespace from reduced-parameter smoke runs.

Not yet supported:
- A completed frozen-parameter dual-gate result across all 14 ready platforms.
- A promoted primary claim state from the expansion-v3 ready panel.
- Ten distinct perturbation-mechanism classes. The ready panel currently spans five mechanism classes.

## Next Command

Run the frozen full-panel scoring with:

```bash
python3 scripts/benchmark_expansion_v3_ready_panel.py
```

For resumable execution by one dataset at a time, use:

```bash
python3 scripts/benchmark_expansion_v3_ready_panel.py --dataset-id DATASET_ID --merge-existing
```

Do not change scoring parameters for primary endpoint runs. If reduced parameters are needed for debugging, provide a non-primary `--analysis-prefix`.
