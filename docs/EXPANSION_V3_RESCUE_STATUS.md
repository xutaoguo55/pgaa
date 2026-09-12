# Expansion v3 Rescue Status

The frozen v3 source queue passed download/readability gates but produced only four ready platforms under the metadata-only contract.

- v3 ready platforms: 4 / 14
- v3b rescue candidates registered: 12
- v3b candidates downloaded and audited in this pass: 4
- v3b candidates newly ready in this pass: 0
- Primary blocker: public H5AD files often contain perturbation labels but not both a reusable matched control set and an independent recorded split.

Current ready v3 platforms:
- papalexi2021_thp1_crispr: THP1_immune_state, CRISPR_Cas9, 16 units
- frangieh2021_melanoma_crispr: melanoma_patient_model, CRISPR_Cas9, 16 units
- xu2023_hek293_crispri: embryonic_kidney_cell_line, CRISPRi, 16 units
- weinreb2020_hematopoietic_cytokine: hematopoietic_progenitor, cytokine, 16 units

Audited v3b small batch:
- datlinger2021_jurkat_crispr: below_minimum_units; no nperts=0 or explicit control rows under tested adapters
- srivatsan2020_sciplex2: below_minimum_units; control/dose metadata present but held-out well/oligo split lacks matched controls for eligible units
- adamson2016_10x001: below_minimum_units; nperts=0 present but no independent recorded split supports matched perturbed/control holdout
- schraivogel2020_k562_tapseq_chr8: below_minimum_units; replicate metadata present but no explicit nperts=0/control rows
