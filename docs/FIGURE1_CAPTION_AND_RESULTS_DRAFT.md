# Figure 1 Caption and Results Draft

## Claim Boundary

This text is bounded to the generated Figure 1 source table. External same-context concordance denotes computational agreement in a matched perturbation setting; it does not establish biological validation, immune presentation, peptide validation, or T-cell function.

## Figure Caption Draft

Figure 1. A claim-state compiler controls evidentiary inflation in single-cell perturbation benchmarking. (A) Benchmark and guardrail rows are compiled into typed manuscript claim states, including 10 comparative-support rows, 11 descriptive-only rows, 3 calibration-support rows, 4 restricted-use rows, and 25 failure-or-guardrail rows. (B) Row-level evidence is aggregated into context-level responder-state decision units, including 5 supported units and 3 provisional units. (C) Leave-one-method stability and same-context replication gate for the 8 responder-state units. 4 units are leave-one-method stable, 3 are method-sensitive, and 1 is PGAA-support dependent. The typed external gate classifies 4 units as concordant, 4 as blocked, 0 as discordant, and 0 as unresolved. Concordant units support bounded computational same-context replication only.

## Results Paragraph Draft

We implemented PGAA as a claim-state compiler that maps heterogeneous benchmark evidence to typed manuscript decisions rather than leaving each score open to post hoc interpretation. The generated Figure 1 source table contains 30 rows spanning 14 claim-state summaries, 8 responder-state decision units, and 8 stability summaries. This conversion makes positive, descriptive, restricted, and failed benchmark outcomes visible in the same object. Each row therefore retains an explicit interpretation ceiling, preventing restricted or failed evidence from being promoted during manuscript assembly. At the decision-unit level, the current evidence supports 5 bounded Adamson responder-state claims and leaves 3 Norman units as provisional descriptive findings. Leave-one-method checks identify 4 stable units, 3 method-sensitive units, and 1 PGAA-support dependent unit. The external gate then assigned 4 units to `external_same_context_concordant` and 4 to `external_same_context_blocked`, with 0 discordant and 0 unresolved units. This typed state distinguishes computational concordance from unavailable or conflicting evidence without promoting any unit to biological validation.
