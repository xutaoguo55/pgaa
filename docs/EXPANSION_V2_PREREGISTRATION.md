# PGAA Dual-gate Expansion v2: Frozen Confirmation Protocol

## Freeze boundary

This protocol was frozen on 20 July 2026 before expression-derived outcomes were generated for any of the ten new platforms. Public study metadata may be used to establish eligibility, independence, cell context, perturbation mechanism, and experimental split fields. Expression-derived method scores, overlaps, specificity margins, gate states, or favorable target identities may not be inspected for candidate selection.

The five completed platforms are exploratory evidence. They do not count toward the confirmatory success rule for the ten new platforms.

## Sampling frame

The expansion requires ten source studies from ten independent laboratory groups. Only one platform from a source study may enter the confirmatory cohort. The ten selected platforms must use distinct new cell contexts and collectively cover at least three perturbation-mechanism classes. A different cell line, primary-cell state, or differentiated lineage is a distinct context; a technical replicate or a second file from the same experiment is not.

Each platform must provide single-cell RNA measurements, matched controls, and at least two recorded independent experimental units that can be assigned to discovery and validation without using expression results. At least eight perturbation units must retain 20 perturbed cells and two disjoint groups of 20 controls in both splits. Genetic perturbations must permit removal of the directly targeted transcript from feature ranking. Logical duplicates count once.

## Frozen analysis

The primary method is PGAA-W. PGAA-H, absolute mean shift, and absolute Welch t are secondary comparators. Per platform, at most 16 perturbation units are selected by descending minimum equal group size and unit identifier. Each group is capped at 70 cells; 5,000 features, top-100 overlap, five deterministic matched resamples, and frozen v2 split/sampling seeds are used.

Stability passes when the platform median observed top-100 overlap is at least 0.20. Specificity passes only when the median observed-minus-pseudo overlap margin is positive and the one-sided unit-level Wilcoxon test remains at or below 0.05 after Holm correction across the four methods within that platform. The primary event is PGAA-W being stable but not specific.

## Frozen claim rule

The primary estimand is the event count and fraction among the ten new platforms, with a Clopper-Pearson 95% interval. Cross-context recurrence requires at least 4 of 10 events spanning at least three perturbation-mechanism classes and four cell-context classes. Platform-robust recurrence additionally requires at least three events after deletion of every one source study.

Failing either rule is a valid confirmatory result. No result can support a universal-law claim because the sampled platforms are not a probability sample of all perturbation systems.

## Failure preservation

Metadata or quality failure discovered before outcome generation remains in the audit and advances the frozen priority queue. Runtime failures remain assigned and must be repaired rather than replaced. Unfavorable outcomes remain in the primary analysis. Post-outcome exclusion is prohibited except for demonstrated file corruption or logical duplication, both of which require an auditable fingerprint.

The machine-readable authority is `evidence/expansion_v2_protocol.json`; its SHA256 digest is stored in `evidence/expansion_v2_protocol.sha256`.
