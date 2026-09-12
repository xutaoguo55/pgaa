# Expansion v2 State Landscape

## Frozen primary result

The frozen primary event (`pgaa_w` stable-but-not-specific) occurred in 0/10 platforms. The machine claim state is `recurrence_not_confirmed`. The pre-specified recurrence claim is therefore not supported.

## Complete four-state landscape

PGAA-W was stable-and-specific in 6/10 platforms (exact 95% CI 0.262-0.878), spanning 6 perturbation-mechanism classes and 6 cell-context classes. The minimum leave-one-study-out count was 5.

| method | stable_and_specific | stable_but_not_specific | specific_but_not_stable | neither_stable_nor_specific |
| --- | --- | --- | --- | --- |
| absolute_mean_shift | 4 | 0 | 4 | 2 |
| pgaa_h | 0 | 0 | 1 | 9 |
| pgaa_w | 6 | 0 | 1 | 3 |
| welch_abs_t | 2 | 0 | 5 | 3 |

This is a secondary summary of the pre-specified four-state output. Applying the frozen cross-context recurrence thresholds symmetrically to stable-and-specific states was decided after outcomes and is typed as `post_outcome_symmetric_rule_application`; it does not replace the frozen primary estimand.

## PGAA-W platform states

| dataset_id | median_observed_overlap | median_pseudo_overlap | median_specificity_margin | holm_adjusted_p | dual_gate_state |
| --- | --- | --- | --- | --- | --- |
| cui2023_lymph_node_cytokine | 0.11 | 0.08 | 0.015 | 0.08736 | neither_stable_nor_specific |
| lara2023_bone_marrow_crispr | 0.14 | 0.06 | 0.085 | 6.104e-05 | specific_but_not_stable |
| liang2023_liver_organoid_crispr | 0.235 | 0.175 | 0.075 | 0.001832 | stable_and_specific |
| mcfarland2020_cancer_mixseq_drug | 0.21 | 0.145 | 0.09 | 0.00147 | stable_and_specific |
| santinha2023_brain_aav_crispr | 0.16 | 0.15 | 0.015 | 0.3121 | neither_stable_nor_specific |
| schiebinger2019_mesc_cytokine | 0.64 | 0.15 | 0.48 | 6.104e-05 | stable_and_specific |
| shifrut2018_primary_t_crispr | 0.38 | 0.06 | 0.32 | 6.104e-05 | stable_and_specific |
| sunshine2023_calu3_crispri | 0.33 | 0.135 | 0.185 | 6.104e-05 | stable_and_specific |
| tian2021_ipsc_neuron_crispra | 0.05 | 0.04 | 0.01 | 0.129 | neither_stable_nor_specific |
| wessels2023_myeloid_cas13 | 0.235 | 0.06 | 0.185 | 0.0009726 | stable_and_specific |

## Interpretation

The ten-platform expansion does not support a general stability-specificity decoupling law. Instead, it reveals conditional joint portability: when PGAA-W passed the stability gate in this cohort, it also passed the pseudo-perturbation specificity gate (6/6 stable platforms). The remaining systems occupied one specific-but-not-stable state and three neither-state positions.

The result supports a method-by-context state landscape, not universal PGAA-W superiority. Absolute mean shift was stable-and-specific in 4/10 platforms, Welch in 2/10, and PGAA-H in 0/10; paired platform counts are too small to license a broad superiority claim.
