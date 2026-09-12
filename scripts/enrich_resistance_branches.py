#!/usr/bin/env python3
"""Query g:Profiler for the two DTC-derived resistance branches."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--genes", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--top", type=int, default=200)
    args = parser.parse_args()
    genes = pd.read_csv(args.genes, sep="\t")
    rows = []
    for branch, ascending in (
        ("PC9_adaptive_stress", False),
        ("H4006_replication", True),
    ):
        selected = genes.sort_values("dtc_pc9_minus_h4006", ascending=ascending).head(
            args.top
        )
        symbols = selected["gene_symbol"].dropna().astype(str).tolist()
        response = requests.post(
            "https://biit.cs.ut.ee/gprofiler/api/gost/profile/",
            json={
                "organism": "hsapiens",
                "query": symbols,
                "sources": ["GO:BP", "REAC", "KEGG"],
                "user_threshold": 0.05,
            },
            timeout=60,
        )
        response.raise_for_status()
        for result in response.json()["result"]:
            rows.append(
                {
                    "branch": branch,
                    "source": result["source"],
                    "term_id": result["native"],
                    "term_name": result["name"],
                    "adjusted_p": result["p_value"],
                    "intersection_size": result["intersection_size"],
                    "query_size": len(symbols),
                }
            )
    output = pd.DataFrame(rows).sort_values(["branch", "adjusted_p"])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.out, sep="\t", index=False)
    print(f"Wrote {args.out} ({len(output)} enriched terms)")


if __name__ == "__main__":
    main()
