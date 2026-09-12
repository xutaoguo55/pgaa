#!/usr/bin/env python3
"""Re-derive the Adamson 2016 cell counts quoted in MANUSCRIPT.md from GEO.

MANUSCRIPT.md states that after QC the GSE90546 UPR CRISPRi sample held 5,680
K562 cells, that five sgRNA perturbations covered 468-686 cells each (2,750 in
total), and that 1,759 non-targeting controls were used. The deposit carries a
per-cell table naming the guide behind every barcode, so those counts can be
recomputed rather than taken on trust.

The QC step is the deposit's own ``good coverage`` flag: the manuscript's 5,680
is exactly the number of rows in GSM2406675 flagged there. The five perturbations
are the UPR genes the manuscript names; the non-targeting arm is the ``62(mod)``
guide plus the six unassigned ``*`` rows.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

GEO_SERIES = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE90nnn/GSE90546/suppl"
GEO_SAMPLE = "https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM2406nnn/{gsm}/suppl"

# The QC-passing replicate the manuscript's 5,680 refers to.
SAMPLE = "GSM2406675"
PERTURBATIONS = ("SPI1", "ZNF326", "BHLHE40", "CREB1", "DDIT3")
# Non-targeting guide label in this deposit, plus its unassigned rows.
NONTARGETING = ("62(mod)", "*")

# Quoted in MANUSCRIPT.md:102,178.
MANUSCRIPT_QC_CELLS = 5680
MANUSCRIPT_NONTARGETING = 1759
MANUSCRIPT_TOTAL_PERT = 2750
MANUSCRIPT_PERT_RANGE = (468, 686)


def fetch(url: str, cache: Path, name: str) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / name
    if dest.exists() and dest.stat().st_size:
        return dest
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=180) as response:
        dest.write_bytes(response.read())
    return dest


def cell_identity_name(gsm: str) -> str:
    """The cell-identity filename for ``gsm``, read off its supplementary listing."""
    with urllib.request.urlopen(f"{GEO_SAMPLE.format(gsm=gsm)}/", timeout=60) as response:
        listing = response.read().decode("utf-8", "replace")
    match = re.search(r'href="([^"]*cell_identities[^"]*)"', listing)
    if not match:
        raise FileNotFoundError(f"no cell_identities file listed for {gsm}")
    return match.group(1)


def read_rows(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "pgaa" / "adamson_geo"))
    parser.add_argument("--out", default="scripts/adamson_geo_cell_counts.csv")
    args = parser.parse_args()

    cache = Path(args.cache_dir)
    try:
        name = cell_identity_name(SAMPLE)
        path = fetch(f"{GEO_SAMPLE.format(gsm=SAMPLE)}/{name}", cache, name)
    except OSError as exc:
        print(f"cannot reach GEO: {exc}", file=sys.stderr)
        return 2

    rows = read_rows(path)
    passing = [r for r in rows if str(r.get("good coverage", "")).strip().lower() == "true"]

    guides = Counter(r["guide identity"].split("_")[0] for r in passing)
    counts = {gene: guides.get(gene, 0) for gene in PERTURBATIONS}
    total_pert = sum(counts.values())
    non_targeting = sum(guides.get(label, 0) for label in NONTARGETING)
    low, high = min(counts.values()), max(counts.values())

    rows_out = [
        ("qc_passing_cells", len(passing), MANUSCRIPT_QC_CELLS),
        ("non_targeting_controls", non_targeting, MANUSCRIPT_NONTARGETING),
        ("total_perturbed_cells", total_pert, MANUSCRIPT_TOTAL_PERT),
        ("min_cells_per_perturbation", low, MANUSCRIPT_PERT_RANGE[0]),
        ("max_cells_per_perturbation", high, MANUSCRIPT_PERT_RANGE[1]),
        *((f"cells_{gene}", counts[gene], None) for gene in PERTURBATIONS),
    ]

    width = max(len(key) for key, _, _ in rows_out)
    print(f"\n{'quantity'.ljust(width)}  {'recomputed':>10}  {'manuscript':>10}")
    print("-" * (width + 24))
    failures = []
    for key, value, expected in rows_out:
        shown = "—" if expected is None else str(expected)
        flag = ""
        if expected is not None:
            flag = "  OK" if value == expected else "  MISMATCH"
            if value != expected:
                failures.append(key)
        print(f"{key.ljust(width)}  {value:>10}  {shown:>10}{flag}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        handle.write("quantity,recomputed,manuscript\n")
        for key, value, expected in rows_out:
            handle.write(f"{key},{value},{'' if expected is None else expected}\n")
    print(f"\nwrote {out}")

    if failures:
        print(f"MISMATCH against MANUSCRIPT.md: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
