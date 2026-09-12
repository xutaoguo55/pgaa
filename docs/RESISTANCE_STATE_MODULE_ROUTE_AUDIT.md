# PC9 Resistance-State Module Route Audit

Two-dataset provisional route: `shared_resistance_down_module`

Superseded for universal-direction claims by the locked GSE249721 audit in `docs/RESISTANCE_STATE_SEPARATION_AUDIT.md`, which observes direction reversal in the main PC9 contexts.

## Locked Design

GSE75602 is used only to rank genes showing complete replicate separation in the same direction in both early GR2 and late GR3 relative to parental PC9. GSE129221 is then used as an independent clone-level validation set without gene re-ranking. The 50-gene module is primary; sizes 10, 25, 100, and 200 are sensitivity checks.

## Route Competition

| Route | Primary exact p | Primary concordance | All sizes p <= 0.05 | Gate |
|---|---:|---:|---|---|
| shared_resistance_down_module | 0.050 | 0.620 | True | pass |
| shared_resistance_up_module | 0.050 | 0.580 | False | fail |

## Validation Sensitivity

| Direction | Module size | Oriented score difference | Exact p | Gene concordance |
|---|---:|---:|---:|---:|
| up | 10 | -0.081 | 0.650 | 0.500 |
| up | 25 | 0.408 | 0.050 | 0.640 |
| up | 50 | 0.257 | 0.050 | 0.580 |
| up | 100 | 0.186 | 0.150 | 0.560 |
| up | 200 | 0.140 | 0.200 | 0.535 |
| down | 10 | 0.629 | 0.050 | 0.700 |
| down | 25 | 0.558 | 0.050 | 0.640 |
| down | 50 | 0.402 | 0.050 | 0.620 |
| down | 100 | 0.456 | 0.050 | 0.640 |
| down | 200 | 0.415 | 0.050 | 0.625 |

## Reframe Route Selection

| Candidate | Gate | Evidence strength | Reason |
|---|---|---:|---|
| shared_resistance_down_module | pass | 3 | independent_directional_replication_all_locked_sizes |
| fixed_t790m_egfr_effect | fail | 0 | direction_discordant_across_GSE112274_and_GSE129221 |
| pathway_mechanism | fail | 0 | enrichment_fragmented_and_driven_by_small_terms |
| shared_resistance_up_module | fail | 0 | fails_module_size_robustness |
| t790m_same_cell_down_module_transfer | fail | 0 | source_group_adjusted_CORTAD_test |

## Same-Cell Context Check

The locked down module does not transfer to the CORTAD T790M-high contrast after restricting analysis to source groups containing both event states and adjusting for source group. The primary 50-gene module has 12 mapped genes, adjusted effect 0.026, and HC3 p=0.620. This failure prevents relabeling the module as T790M-specific.

## Interpretation

The shared down-regulated resistance module passes the two-dataset development gate across every prespecified module size. The up-regulated route is less stable and fails the all-size robustness gate. This result motivated a locked third-system test; it no longer supports a universal directional program because GSE249721 reverses direction in its main PC9 contexts.

This is a route-selection result, not a final confirmatory claim. GSE75602 has two replicates per state, GSE129221 has three per group, and both are clone-level systems. The selected module must remain locked for any next dataset, and biological interpretation requires gene annotation and pathway analysis that do not alter membership.

Discovery contained 1901 robust down genes and 2023 robust up genes.
