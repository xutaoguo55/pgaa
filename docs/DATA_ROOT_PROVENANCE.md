# External data root — provenance and how to rebuild it

Several frozen registries in `pgaa/core/` were originally built against an
external volume (`/Volumes/MOVESPEED`). That volume is **not** part of the
submission archive, so any path recorded under it is a *historical pointer*,
not a location a reader can resolve. This file maps those pointers to their
public sources and to the scripts in this archive that rebuild the derived
inputs.

Set `PGAA_DATA_ROOT` to a local copy of the external tree to make the
registries resolve without editing code:

```bash
export PGAA_DATA_ROOT=/path/to/local/copy
python3 scripts/audit_expansion_v2_sources.py
```

`pgaa/core/data_root.py` is the single place that decides the root. Its
`LEGACY_USB_ROOT` fallback exists only so existing local workflows keep
working; nothing in the analysis depends on that path existing.

## Path map

| Recorded path (historical) | Public source | Rebuilt by |
|---|---|---|
| `/Volumes/MOVESPEED/pgaa_replogle/K562_gwps_raw_singlecell_01.h5ad` | **GSE146194** (Replogle 2022 K562 GWPS) | `scripts/download_replogle.sh`, then `scripts/extract_external_pgaa_inputs.py` |
| `/Volumes/MOVESPEED/pgaa_replogle/external_rerun/replogle_2022_k562_gwps/<TARGET>/expression.csv`, `metadata.csv` | derived from the above | `scripts/extract_external_pgaa_inputs.py` |
| `/Volumes/MOVESPEED/claude code大电脑备份data/.../replogle_2022_k562_essential.h5ad` | Replogle 2022 essential (GSE146194 series) | not used by any manuscript figure |
| `/Volumes/MOVESPEED/pgaa_cross_platform/v2/sources/...` | expansion-v2 platform sources | `scripts/download_expansion_v2_sources.py` |
| `/Volumes/MOVESPEED/pgaa_cross_platform/v3b|v3c/sources/...` | expansion-v3 platform sources | `scripts/download_expansion_v3_sources.py` |
| `/Volumes/MOVESPEED/public_db_backup_2026-05-06/.../norman_k562_sc.h5ad` | **GSE133344** (Norman 2019) | see `NORMAN2019_RAW_DIR` / `NORMAN2019_H5AD` below |

`evidence/*_source_manifest.tsv` record the `resolved_source_path` that was
actually used at build time, together with the file's md5. Those values were
resolved from the filesystem when the manifests were written (see
`resolve_existing` / `source_storage_label` in
`scripts/download_expansion_v3_sources.py`); they are *not* reconstructed from
a constant.

## Norman 2019 (GSE133344)

Two distinct inputs, controlled by two environment variables:

| Variable | Points at | Used by |
|---|---|---|
| `NORMAN2019_H5AD` | the processed `norman2019_full_log.h5ad` | `benchmark_norman_multi_perturbation.py` and the S1/S2 scripts |
| `NORMAN2019_RAW_DIR` | the directory holding the raw `GSE133344_filtered_*` matrix | `scripts/benchmark_norman2019_full.py` |

Neither file is bundled: the processed h5ad alone is ~1.2 GB. The archive
supports processed-source-data regeneration and manifest checks without them.

## Expansion manifests and the mount point

`tests/test_expansion_v2_registry.py` and `tests/test_expansion_v3_registry.py`
assert the *structural* property that frozen manifests record external storage
and never repo-local paths. The exact mount point is deliberately not
asserted — it is an environment fact, not a property of the code.

## Scope: which scripts are covered by `PGAA_DATA_ROOT`

`pgaa/core/data_root.py` is honoured by the scripts on the submission's
reviewer-facing reproduction paths. Everything a reader is told to run in
`README.md` or in a `DATASET_MANIFEST.tsv` `rebuild_commands` cell resolves
through `PGAA_DATA_ROOT`, so the external tree can be relocated without editing
code.

The remaining **30 scripts under `scripts/`** still embed a literal
`/Volumes/MOVESPEED` (or `/Users/guoxutao`) path. They are **not** named in the
README reproduction commands or in any `DATASET_MANIFEST.tsv` rebuild command,
and they are retained in the archive only as a record of how the frozen
registries and expansion layers were originally built. They are **outside the
supported reproduction range**: running one of them on a machine without the
original external volume will fail at the first file open. They are listed here
so a reader can tell at a glance which scripts are expected to work from the
archive alone.

```
scripts/audit_expansion_v2_sources.py        scripts/figure_cll_combination.py
scripts/benchmark_cll_realdata.py            scripts/figure_norman_nbins20.py
scripts/benchmark_cpt.py                     scripts/figure_norman_prt.py
scripts/benchmark_cpt_cr.py                  scripts/figure_s2_calibration.py
scripts/benchmark_method_comparison.py       scripts/final_4method_full_data.py
scripts/benchmark_norman2019.py              scripts/oe_validation.py
scripts/benchmark_norman_v2.py               scripts/sensitivity_s2_bins.py
scripts/benchmark_prt_s1.py                  scripts/download_expansion_v2_sources.py
scripts/benchmark_prt_s2.py                  scripts/download_expansion_v3_sources.py
scripts/benchmark_prt_s2_calibrated.py       scripts/cll20k_4method.py
scripts/benchmark_prt_s2_gapdh_neg.py        scripts/compare_combinations.py
scripts/benchmark_prt_s2_nbins20.py          scripts/diagnose_cll.py
scripts/benchmark_prt_s2_zscore.py           scripts/benchmark_reald.py
scripts/benchmark_prt_s3.py                  scripts/benchmark_s2_klf1_neg.py
scripts/benchmark_prt_s3_fast.py             scripts/benchmark_sceptre_pgaa.py
```

## Absolute paths recorded inside `evidence/`

Several `evidence/*.tsv` files (source manifests, contract tables, obs-field
inventories, and `local_external_h5ad_candidate_audit.tsv`) carry an
`resolved_source_path`-style column holding the absolute path the file was read
from at build time. These are **historical records of provenance, not
instructions**: they document where a derived value came from, and rewriting
them would destroy that record. To re-derive such a table locally, obtain the
upstream data (see the path map above) and substitute the recorded prefix with
your own `PGAA_DATA_ROOT`.

One consequence worth stating plainly: `evidence/replogle_essential_generality_contract.tsv`
stores absolute `metadata_csv` / `expression_csv` / `singlecell_h5ad` paths for
the four Replogle targets, so `PGAA_DATA_ROOT` alone does not relocate them.
`scripts/benchmark_replogle_essential_response_replication.py` detects the
missing inputs and exits with status 2 rather than failing mid-run; the
extraction step (`scripts/extract_external_pgaa_inputs.py`) rebuilds those
files from GSE146194.
