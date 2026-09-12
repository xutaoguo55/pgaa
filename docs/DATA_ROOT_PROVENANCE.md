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

## Two roots: `PGAA_DATA_ROOT` and `PGAA_RAW_DATA`

The scripts under `scripts/` read from two different trees, and it matters which
is which:

| Variable | Default | Holds | Resolved by |
|---|---|---|---|
| `PGAA_DATA_ROOT` | `/Volumes/MOVESPEED` | the frozen external platform registries and expansion sources | `pgaa.core.data_root.data_root()` |
| `PGAA_RAW_DATA` | the repository's **parent** directory | the local workspace the benchmark scripts were developed against (`norman2019/`, `cll_counts.mtx`, `cll_genes.txt`, `cll_barcodes.txt`, `cll_meta.csv`) | the `RAW = ...` line at the top of each script |

`PGAA_RAW_DATA` is deliberately *not* routed through `pgaa/core/data_root.py`:
that module exists so the frozen registries can be relocated, whereas these
scripts only need one line and should not fail if the package is not importable.
The line is self-contained:

```python
RAW = Path(os.environ.get('PGAA_RAW_DATA', Path(__file__).resolve().parents[2]))
```

Everything the scripts read or write under the workspace now goes through
`RAW`. No script under `scripts/` embeds a `/Users/...` literal any more, so a
reader who obtains the inputs can point the whole family at them with one
`export PGAA_RAW_DATA=/path/to/copy`.

## Scope: which scripts are covered by `PGAA_DATA_ROOT`

`pgaa/core/data_root.py` is honoured by the scripts on the submission's
reviewer-facing reproduction paths. Everything a reader is told to run in
`README.md` or in a `DATASET_MANIFEST.tsv` `rebuild_commands` cell resolves
through `PGAA_DATA_ROOT`, so the external tree can be relocated without editing
code.

Three scripts under `scripts/` still embed a literal `/Volumes/MOVESPEED` path:
`audit_expansion_v2_sources.py`, `download_expansion_v2_sources.py`, and
`download_expansion_v3_sources.py` (they need the external mount to enumerate
what to fetch). They are **not** named in the README reproduction commands or in
any `DATASET_MANIFEST.tsv` rebuild command.

A larger family of benchmark and figure scripts is retained in the archive only
as a record of how the frozen registries and expansion layers were originally
built. They are **outside the supported reproduction range** — but for a
different reason than before: their paths are now relocatable via
`PGAA_RAW_DATA`, and what remains missing is the *input data* (the processed
Norman `h5ad` is ~1.2 GB and the CLL matrices are ~1.1 GB, neither bundled).
They are listed here so a reader can tell at a glance which scripts are expected
to work from the archive alone.

```
scripts/benchmark_cll_realdata.py            scripts/figure_cll_combination.py
scripts/benchmark_cpt.py                     scripts/figure_norman_nbins20.py
scripts/benchmark_cpt_cr.py                  scripts/figure_norman_prt.py
scripts/benchmark_method_comparison.py       scripts/figure_s2_calibration.py
scripts/benchmark_norman2019.py              scripts/final_4method_full_data.py
scripts/benchmark_norman_v2.py               scripts/oe_validation.py
scripts/benchmark_prt_s1.py                  scripts/sensitivity_s2_bins.py
scripts/benchmark_prt_s2.py                  scripts/cll20k_4method.py
scripts/benchmark_prt_s2_calibrated.py       scripts/compare_combinations.py
scripts/benchmark_prt_s2_gapdh_neg.py        scripts/diagnose_cll.py
scripts/benchmark_prt_s2_nbins20.py          scripts/benchmark_reald.py
scripts/benchmark_prt_s2_zscore.py           scripts/benchmark_s2_klf1_neg.py
scripts/benchmark_prt_s3.py                  scripts/benchmark_sceptre_pgaa.py
scripts/benchmark_prt_s3_fast.py
```

## Workspace literals that remain, and why they stay

`evidence/expansion_v2_resources.json` and `evidence/expansion_v3_resources.json`
each carry a `"path": "/Users/guoxutao/.openclaw/workspace/PGAA_method_paper"`
entry, and `docs/GSE335846_PHOSPHOPROTEOMICS_CORROBORATION.md` names a workspace
path for a source workbook. These are **frozen build-time records**: the JSON
files are registries whose other fields were measured against that tree, and
rewriting the recorded path would silently break the provenance they exist to
preserve. Treat them the same way as the `resolved_source_path` columns
described in the next section — historical pointer, not an instruction.

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
