# GSE150949 PC9 Evolution Support Text

Supplementary Figure S6 summarizes the strongest local third-system candidate in two bounded panels. Panel A shows the route-aligned frozen down-module score across the PC9 evolution series, while Panel B shows coverage of the frozen top-50 down-module in the public count matrix. The scorecard strengthens the manuscript's third-system discussion without claiming clean route closure.

## Supplementary Figure S6

Supplementary Figure S6. GSE150949 PC9 evolution scorecard. (A) The frozen down-module route score is computed as the negative average z-scored log1p CPM of the mapped top-50 down-module genes from the locked resistance-state route. Day 0 is positive, day 3 and day 7 remain mixed, and all day-14 subtype groups sit below day 0 on the route-aligned score. (B) The public count matrix covers 45 of the 50 frozen down-module genes; the five missing genes are `LINC01819`, `SLC60A1`, `UBBP4`, `CPP`, and `MAB21L4`. The figure therefore strengthens the manuscript's third-system discussion while preserving the claim ceiling.

## Evidence Summary

### Sample-level route scores

```text
sample_id	time_point	sample_type	n_cells	mean_route_score	median_route_score	std_route_score
1	0	0	6778	0.122830	0.158871	0.130450
2	3	3	7093	-0.030639	0.007142	0.176043
3	3	3	7273	-0.046768	-0.009564	0.186118
4	7	7	4770	0.079175	0.106878	0.117364
5	7	7	3515	0.063566	0.094148	0.130344
6	14	14_high	5380	-0.014244	0.029546	0.180157
7	14	14_med	4221	-0.030649	0.012461	0.183175
8	14	14_low	2690	-0.077443	-0.035467	0.218733
9	14	14_high	5449	-0.013272	0.031396	0.176051
10	14	14_med	5097	-0.033670	0.007880	0.184714
11	14	14_low	4153	-0.052472	-0.016358	0.198287
```

### Group-level summary

```text
time_point	sample_type	n_cells	mean_route_score	median_route_score	std_route_score
0	0	6778	0.122830	0.158871	0.130450
3	3	14366	-0.038804	-0.001225	0.181387
7	7	8285	0.072553	0.101981	0.123273
14	14_high	10829	-0.013755	0.030618	0.178095
14	14_low	6843	-0.062288	-0.024538	0.206910
14	14_med	9318	-0.032302	0.010708	0.184015
```

## Boundary

This figure is only partial support. The candidate does not close the third-system contract because the early day 3 and day 7 states remain mixed, and the public matrix does not contain all 50 frozen module genes.

Missing symbols: LINC01819, SLC60A1, UBBP4, CPP, MAB21L4.
