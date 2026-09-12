# GSE150949 PC9 Evolution Audit

Date: 2026-09-12

## Purpose

This audit records why `GSE150949` is the strongest local PC9 evolution candidate for the manuscript's remaining third-system gap, while still stopping short of a full route closure.

## Data source

`GSE150949` provides a gene-by-cell PC9 count matrix and lineage-aware metadata. The frozen route uses the top 50 genes from the locked down-module selected in `GSE75602`, with route-aligned scores defined as the negative average z-scored log1p CPM of the mapped module genes.

## Module coverage

The frozen top-50 down-module is represented by 45 of the 50 genes in the public matrix.

Missing module symbols:

LINC01819, SLC60A1, UBBP4, CPP, MAB21L4

### Frozen top-50 coverage

rank	gene_id	gene_symbol	locked_discovery_score	present_in_matrix
1	ENSG00000118849	RARRES1	2.703015	yes
2	ENSG00000047457	CP	2.430844	yes
3	ENSG00000107159	CA9	2.024221	yes
4	ENSG00000064787	BCAS1	1.935147	yes
5	ENSG00000099260	PALMD	1.886894	yes
6	ENSG00000213931	HBE1	1.868079	yes
7	ENSG00000168878	SFTPB	1.744596	yes
8	ENSG00000164741	DLC1	1.665327	yes
9	ENSG00000105141	CASP14	1.607467	yes
10	ENSG00000138449	SLC40A1	1.502758	yes
11	ENSG00000133135	RNF128	1.481171	yes
12	ENSG00000074410	CA12	1.399211	yes
13	ENSG00000159167	STC1	1.248436	yes
14	ENSG00000182782	HCAR2	1.214426	yes
15	ENSG00000167653	PSCA	1.193388	yes
16	ENSG00000143546	S100A8	1.185605	yes
17	ENSG00000165821	SALL2	1.185436	yes
18	ENSG00000167183	PRR15L	1.161841	yes
19	ENSG00000134258	VTCN1	1.155619	yes
20	ENSG00000173175	ADCY5	1.132103	yes
21	ENSG00000179023	KLHDC7A	1.125482	yes
22	ENSG00000163701	IL17RE	1.092417	yes
23	ENSG00000204616	TRIM31	1.070405	yes
24	ENSG00000176945	MUC20	1.046747	yes
25	ENSG00000226051	ZNF503-AS1	1.042875	yes
26	ENSG00000167355	OR51B5	1.034268	yes
27	ENSG00000198133	TMEM229B	1.024059	yes
28	ENSG00000154928	EPHB1	1.021720	yes
29	ENSG00000162949	CAPN13	1.018691	yes
30	ENSG00000115525	ST3GAL5	1.011318	yes
31	ENSG00000231826	LINC01819	1.000481	no
32	ENSG00000174514	SLC60A1	0.974500	no
33	ENSG00000118855	MFSD1	0.957367	yes
34	ENSG00000263563	UBBP4	0.949362	no
35	ENSG00000106366	SERPINE1	0.943585	yes
36	ENSG00000127954	STEAP4	0.924165	yes
37	ENSG00000253525	CPP	0.916882	no
38	ENSG00000105519	CAPS	0.913548	yes
39	ENSG00000095596	CYP26A1	0.895880	yes
40	ENSG00000072858	SIDT1	0.885883	yes
41	ENSG00000109107	ALDOC	0.881416	yes
42	ENSG00000084110	HAL	0.878880	yes
43	ENSG00000082684	SEMA5B	0.876295	yes
44	ENSG00000156966	B3GNT7	0.874465	yes
45	ENSG00000204950	LRRC10B	0.873209	yes
46	ENSG00000111341	MGP	0.870678	yes
47	ENSG00000171476	HOPX	0.865245	yes
48	ENSG00000132746	ALDH3B2	0.860665	yes
49	ENSG00000172478	MAB21L4	0.858728	no
50	ENSG00000196917	HCAR1	0.849604	yes

## Route-aligned score summary

### Time-point summary

| Time point | Cells | Mean route score | Median route score | Std route score |
|---:|---:|---:|---:|---:|
time_point	n_cells	mean_route_score	median_route_score	std_route_score
0	6778	0.122830	0.158871	0.130450
3	14366	-0.038804	-0.001225	0.181387
7	8285	0.072553	0.101981	0.123273
14	26990	-0.032463	0.010708	0.187445

### Sample summary

| Sample ID | Time point | Sample type | Cells | Mean route score | Median route score | Std route score |
|---:|---:|---|---:|---:|---:|---:|
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

## Interpretation

The route-aligned score is directionally stronger than `GSE103350` because late day-14 subtype groups are all below day 0 on the frozen down-module axis. The sample-level means are still mixed at day 3 and day 7, so the dataset supports the route only partially and does not close the third-system contract by itself.

At the summary level, day 0 mean route score is 0.123, day 14-low mean route score is -0.062, and the minimum day-14 subtype mean is -0.062.

The strongest statement supported by this audit is:

- `GSE150949` is a real, analyzable local third-system candidate;
- the frozen down-module transfers with 45/50 mapped genes;
- the late day-14 subtype groups remain below day 0 on the route-aligned score;
- early day 3 and day 7 states remain mixed, so the candidate is not yet a clean closure system.

## Manuscript use

This audit can be cited as the best local PC9 evolution candidate for the current route, but only as partial support. It strengthens the claim that the locked resistance-module route is biologically tractable without overstating third-system closure.

## Summary tables

### Group summary

time_point	sample_type	n_cells	mean_route_score	median_route_score	std_route_score
0	0	6778	0.12283000821527468	0.15887101786271818	0.13044999361284804
3	3	14366	-0.03880441273163699	-0.0012247282450382627	0.18138657299554542
7	7	8285	0.07255259297104326	0.10198131963012087	0.12327257408252669
14	14_high	10829	-0.013755046327399559	0.030617751162090624	0.17809485699692335
14	14_low	6843	-0.062287949013987085	-0.024538428615722453	0.2069104123688419
14	14_med	9318	-0.03230156722079894	0.010708336989018869	0.18401489536234397
