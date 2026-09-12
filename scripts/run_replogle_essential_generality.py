#!/usr/bin/env python3
"""Execute and checkpoint the locked PGAA generality contract."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import shlex
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def outputs_valid(row: pd.Series) -> bool:
    return all(Path(str(row[column])).is_file() and Path(str(row[column])).stat().st_size > 0 for column in ("pgaa_s1_out", "pgaa_s2_out"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=ROOT / "evidence/replogle_essential_generality_contract.tsv")
    parser.add_argument("--manifest-out", type=Path, default=ROOT / "evidence/replogle_essential_generality_execution.tsv")
    args = parser.parse_args(argv)
    contract = pd.read_csv(args.contract, sep="\t")
    records: list[dict[str, object]] = []
    for _, row in contract.iterrows():
        target = str(row["target_gene"])
        log_path = Path(str(row["pgaa_s1_out"])).parent / "pgaa_run.log"
        started = datetime.now(timezone.utc).isoformat()
        if outputs_valid(row):
            status, returncode = "complete_existing", 0
        else:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("w", encoding="utf-8") as log:
                completed = subprocess.run(
                    shlex.split(str(row["pgaa_command"])),
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
            returncode = completed.returncode
            status = "complete" if returncode == 0 and outputs_valid(row) else "failed"
        records.append(
            {
                "target_gene": target,
                "execution_status": status,
                "returncode": returncode,
                "started_utc": started,
                "finished_utc": datetime.now(timezone.utc).isoformat(),
                "log_path": str(log_path),
                "denominator_rule": row["denominator_rule"],
            }
        )
        args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(records).to_csv(args.manifest_out, sep="\t", index=False)
        print(f"{target}: {status}", flush=True)
    return 0 if all(str(row["execution_status"]).startswith("complete") for row in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
