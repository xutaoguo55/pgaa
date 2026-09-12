#!/usr/bin/env python3
"""Re-derive the Norman 2019 cell counts quoted in MANUSCRIPT.md from GEO.

MANUSCRIPT.md states the total K562 cell count, the number of available NegCtrl
cells and the per-perturbation cell counts for GSE133344. Those are properties
of the public deposit, so they can be recomputed from it rather than taken on
trust: the barcode table fixes the total, and the cell-identity table names the
guide pair behind every barcode.

The control pool is the one the benchmark script actually draws from, i.e. the
``^NegCtrl\\d+_NegCtrl\\d+__`` mask in
``scripts/benchmark_norman_multi_perturbation.py``. The number of controls used
per perturbation is that script's own rule, ``min(pool, n_pert * ratio, cap)``.
"""
from __future__ import annotations

import argparse
import gzip
import re
import sys
import urllib.request
from pathlib import Path

GEO_BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE133nnn/GSE133344/suppl"
REMOTE_FILES = (
    "GSE133344_filtered_barcodes.tsv.gz",
    "GSE133344_filtered_cell_identities.csv.gz",
)

# scripts/benchmark_norman_multi_perturbation.py:279-280
CONTROL_RATIO = 3
MAX_CONTROLS = 5000
# ...:70-71 -- the mask that defines the control pool
CONTROL_MASK = re.compile(r"^NegCtrl\d+_NegCtrl\d+__")
STRICT_NEGCTRL = re.compile(r"^NegCtrl\d+_NegCtrl\d+__NegCtrl\d+_NegCtrl\d+$")

PERTURBATIONS = ("CEBPE", "KLF1", "SLC4A1", "BAK1", "DUSP9", "CBL")
WIDE_PERTURBATIONS = PERTURBATIONS + ("CEBPA",)


def script_pert_mask(target: str) -> re.Pattern[str]:
    """The perturbation mask exactly as ``single_perturbation_mask`` builds it.

    It accepts the target on either side of the guide pair, so on GSE133344 it
    also sweeps up cells whose guides are NegCtrl. The narrower
    ``^{target}_NegCtrl\\d+__`` form is the one the quoted counts agree with.
    """
    return re.compile(rf"^(?:{re.escape(target)}_NegCtrl\d+|NegCtrl\d+_{re.escape(target)})__")


def quoted_pert_mask(target: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(target)}_NegCtrl\d+__")

# Quoted in MANUSCRIPT.md:101, kept here so a drift in either direction shows up.
MANUSCRIPT_TOTAL = 111668
MANUSCRIPT_POOL = 11855
MANUSCRIPT_PERT = {"CEBPE": 566, "KLF1": 1197, "SLC4A1": 1000, "BAK1": 687, "DUSP9": 731, "CBL": 663}
# scripts/norman_multi_perturbation_summary.csv -- the wider mask's own output.
SUMMARY_PERT = {"KLF1": 1960, "CEBPE": 1233, "CEBPA": 460}
SUMMARY_CTRL = {"KLF1": 5000, "CEBPE": 3699, "CEBPA": 1380}


def fetch(name: str, cache: Path) -> Path:
    """Download ``name`` into ``cache`` once, then reuse it."""
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / name
    if dest.exists() and dest.stat().st_size:
        return dest
    url = f"{GEO_BASE}/{name}"
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=180) as response:
        dest.write_bytes(response.read())
    return dest


def count_barcodes(path: Path) -> int:
    with gzip.open(path, "rt") as handle:
        return sum(1 for line in handle if line.strip())


def read_identities(path: Path) -> list[str]:
    """Return the guide identity column, header excluded."""
    identities: list[str] = []
    with gzip.open(path, "rt") as handle:
        header = next(handle, "")
        column = header.split(",").index("guide_identity")
        for line in handle:
            fields = line.rstrip("\n").split(",")
            if len(fields) > column:
                identities.append(fields[column])
    return identities


def count(patterns: list[re.Pattern[str]], identities: list[str]) -> int:
    return sum(1 for i in identities if any(p.match(i) for p in patterns))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "pgaa" / "norman_geo"))
    parser.add_argument("--out", default="scripts/norman_geo_cell_counts.csv")
    args = parser.parse_args()

    cache = Path(args.cache_dir)
    try:
        barcodes = fetch(REMOTE_FILES[0], cache)
        identities_path = fetch(REMOTE_FILES[1], cache)
    except OSError as exc:
        print(f"cannot reach GEO: {exc}", file=sys.stderr)
        return 2

    total = count_barcodes(barcodes)
    identities = read_identities(identities_path)

    pool = sum(1 for i in identities if CONTROL_MASK.match(i))
    strict = sum(1 for i in identities if STRICT_NEGCTRL.match(i))

    quoted = {name: sum(1 for i in identities if quoted_pert_mask(name).match(i)) for name in PERTURBATIONS}
    wide = {name: sum(1 for i in identities if script_pert_mask(name).match(i)) for name in WIDE_PERTURBATIONS}
    used = {name: min(pool, n * CONTROL_RATIO, MAX_CONTROLS) for name, n in quoted.items()}
    used_wide = {name: min(pool, n * CONTROL_RATIO, MAX_CONTROLS) for name, n in wide.items()}

    rows = [
        ("total_cells", total, MANUSCRIPT_TOTAL),
        ("negctrl_pool", pool, MANUSCRIPT_POOL),
        *((f"cells_{name}", quoted[name], MANUSCRIPT_PERT[name]) for name in PERTURBATIONS),
        *((f"controls_used_{name}", used[name], None) for name in PERTURBATIONS),
        *((f"cells_{name}_wide", wide[name], SUMMARY_PERT.get(name)) for name in WIDE_PERTURBATIONS),
        *((f"controls_used_{name}_wide", used_wide[name], SUMMARY_CTRL.get(name)) for name in WIDE_PERTURBATIONS),
    ]

    width = max(len(key) for key, _, _ in rows)
    print(f"\n{'quantity'.ljust(width)}  {'recomputed':>10}  {'manuscript':>10}")
    print("-" * (width + 24))
    failures = []
    for key, value, expected in rows:
        shown = "—" if expected is None else str(expected)
        flag = ""
        if expected is not None:
            flag = "  OK" if value == expected else "  MISMATCH"
            if value != expected:
                failures.append(key)
        print(f"{key.ljust(width)}  {value:>10}  {shown:>10}{flag}")

    if pool != strict:
        print(f"note: strict ^NegCtrl__NegCtrl count is {strict}, mask count is {pool}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        handle.write("quantity,recomputed,manuscript\n")
        for key, value, expected in rows:
            handle.write(f"{key},{value},{'' if expected is None else expected}\n")
    print(f"\nwrote {out}")

    if failures:
        print(f"MISMATCH against MANUSCRIPT.md: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
