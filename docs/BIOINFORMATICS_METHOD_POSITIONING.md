# Bioinformatics-First Method Positioning

## Objective Verdict

Bioinformatics is a credible first target only if PGAA is presented as a computational method for claim-state compilation, not as another differential-expression or perturbation-ranking score. The methodological claim is that PGAA converts heterogeneous perturbation and resistance transcriptomic evidence into auditable claim states while minimizing unsupported claim promotion.

## Required Upgrade Matrix

| Priority | Upgrade | Category | Method change | Pass condition | Status |
|---:|---|---|---|---|---|
| 1 | bioinfo_01_problem_reframing | positioning | Reframe the method as a claim-state compiler that controls unsupported promotion from scores to biological claims. | title, abstract, and first Results paragraph state claim-state compilation before any ATM biology | available |
| 2 | bioinfo_02_claim_promotion_metric | benchmark | Promote false-promotion rate, exact-permission rate, under-promotion rate, and replication false-positive rate as formal reporting metrics. | main benchmark table compares compiler, frozen score reporting, decision-only, and external-only baselines | available |
| 3 | bioinfo_03_empirical_anchor | benchmark | Separate contract-stress tests from empirical anchors: Norman, Adamson, Replogle, and EGFR-resistance branch-vulnerability examples. | every empirical claim maps to a real source-data row and a claim ceiling | available |
| 4 | bioinfo_04_comparator_fairness | benchmark | Make comparator fairness explicit: conventional recovery metrics are reported, but the primary endpoint is claim-state correctness. | each comparator has input, endpoint, allowed interpretation, and limitation fields | available |
| 5 | bioinfo_05_ablation_stack | ablation | Add ablations removing stability, external evidence, source provenance, and branch-vulnerability promotion gates. | each ablation has expected failure mode and manuscript consequence | available |
| 6 | bioinfo_06_branch_vulnerability_use_case | biological_demonstration | Use ATM as a bounded demonstration of branch-specific vulnerability hypothesis compilation, not as a validated drug claim. | ATM is primary demonstration; HDAC remains secondary; definitive pharmacology is blocked | available |
| 7 | bioinfo_07_software_contract | software | Expose one-command scripts, CLI smoke tests, source-data manifest, and full pytest status as the software contract. | README lists key commands and tests pass from a clean checkout with documented external-data boundaries | available |
| 8 | bioinfo_08_manuscript_figure_order | presentation | Reorder figures around method logic: compiler, claim-promotion benchmark, empirical anchors, branch-vulnerability case, reproducibility package. | every figure has a primary method claim and a non-overclaim boundary | available |
| 9 | bioinfo_09_target_specificity_scorecard | presentation | Render the GSE193258 target-specificity audit as a dedicated lead-target scorecard figure and carry it as a support figure in the submission package. | the support figure appears in the submission position and mirrors the audit conclusion without overstating validation | available |

## Comparator Contract

| Comparator | Role | Primary endpoint | Allowed interpretation | Limitation |
|---|---|---|---|---|
| PGAA_claim_state_compiler | primary_method | claim-promotion correctness and bounded biological-use-case support | reduces unsupported claim promotion while retaining actionable hypotheses | contract correctness is not biological truth without empirical anchors |
| state_blind_frozen_reporting | negative_reporting_baseline | false-promotion rate under evidence-gate mutation | models a common reporting failure where claims do not update after evidence changes | not a published algorithm and should be labeled as a reporting baseline |
| decision_only_reporting | partial_gate_baseline | under-promotion and replication sensitivity | tests the cost of ignoring external evidence gates | conservative behavior can look safe while missing eligible replication claims |
| external_only_reporting | partial_gate_baseline | replication false-positive rate | tests the danger of promoting from external concordance alone | not a full expression-ranking method |
| SCEPTRE_or_CPT | conventional_method_baseline | known-target recovery or ranking concordance | contextualizes PGAA against established perturbation-analysis methods on conventional endpoints | does not directly solve claim-state promotion unless wrapped in the same compiler contract |
| Welch_or_mean_shift | simple_statistical_baseline | known-target recovery, rank overlap, and claim-state after compiler wrapping | tests whether PGAA adds value over simple distributional or mean-difference summaries | strong simple baselines should be retained, not hidden, because they define the honest method ceiling |

## Ablation Stack

| Ablation | Removed component | Expected failure | Primary metric |
|---|---|---|---|
| remove_stability_gate | stability evidence | unstable internal units can be promoted as reproducible | increase in false promotion or reduction in exact permission |
| remove_external_gate | external evidence state | same-context replication claims cannot be distinguished from internal-only support | replication sensitivity collapse or under-promotion |
| remove_source_gate | source-data provenance | figure-level or missing-source evidence can be promoted beyond traceable numerical support | source-ceiling violations |
| remove_branch_promotion_gate | branch-vulnerability promotion gate | ATM and HDAC can be promoted to the same claim level despite unequal evidence | candidate hierarchy violation |
| score_only_reporting | claim-state compiler | ranked outputs become manuscript claims without evidence-state permissions | false-promotion rate |

## Bioinformatics Figure Order

| Figure | Title | Primary method claim | Boundary |
|---|---|---|---|
| Figure 1 | PGAA as a claim-state compiler | scores, stability, external evidence, source provenance, and promotion gates are compiled into bounded claim states | workflow figure only; no biological validation claim |
| Figure 2 | False-promotion benchmark and ablation stack | the compiler reduces unsupported claim promotion compared with incomplete reporting baselines | contract benchmark; not empirical proof of biological truth |
| Figure 3 | Empirical perturbation transcriptomics anchors | claim-state outputs remain traceable across Norman, Adamson, Replogle, and simple/computational baselines | known-target recovery and reproducibility evidence, not universal method superiority |
| Figure 4 | EGFR-resistance branch-vulnerability demonstration | a frozen resistance branch compiles to an ATM vulnerability hypothesis across matched and dynamic systems | preclinical hypothesis; not clinical or definitive pharmacology |
| Figure 5 | Reproducibility and source-data audit | every promoted claim is backed by executable scripts, source-data rows, and explicit blocked-evidence states | documents reproducibility state; does not erase external-data limitations |
| Supplementary Figure S4 | GSE193258 target-class specificity scorecard | ATM is the cleanest positive target-class signal in the matched screen while ALK and HDAC remain runner-up positive tier candidates | lead-target specificity evidence; not independent validation or clinical pharmacology |

## Immediate Gaps To Close

None

## Submission Position

Target article type: Original Paper.

Lead sentence direction: Current perturbation-transcriptomic workflows often report ranked genes or associations, but manuscript claims require a separate, auditable evidence-state layer. PGAA fills this gap by compiling score, stability, external replication, source provenance, and promotion gates into claim states that preserve both positive hypotheses and evidence ceilings.

External pitch: see `docs/BIOINFORMATICS_SUBMISSION_POSITION.md` for the submission-facing version of the same story.
