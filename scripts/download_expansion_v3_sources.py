#!/usr/bin/env python3
"""Resolve or download frozen expansion-v3 sources directly on the USB volume."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from pathlib import Path
import shutil
import subprocess
import time

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "evidence/expansion_v3_candidate_queue.tsv"
USB = Path("/Volumes/MOVESPEED")
V2_SOURCES = USB / "pgaa_cross_platform/v2/sources"
V3_SOURCES = USB / "pgaa_cross_platform/v3/sources"
ACTIVE_QUEUE = QUEUE
ACTIVE_SOURCE_ROOT = V3_SOURCES
ACTIVE_MANIFEST = ROOT / "evidence/expansion_v3_source_manifest.tsv"
ACTIVE_USB_MANIFEST = USB / "pgaa_cross_platform/v3/source_manifest.tsv"


def file_md5(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        while block := handle.read(chunk_size):
            digest.update(block)
    return digest.hexdigest()


def resolve_existing(candidate: pd.Series) -> Path | None:
    relative = Path(str(candidate["candidate_id"])) / str(candidate["source_file"])
    for root in (ACTIVE_SOURCE_ROOT, V3_SOURCES, V2_SOURCES):
        path = root / relative
        if path.is_file():
            return path
    return None


def source_storage_label(path: Path) -> str:
    if V2_SOURCES in path.parents:
        return "shared_v2_usb"
    if V3_SOURCES in path.parents:
        return "v3_usb"
    if ACTIVE_SOURCE_ROOT in path.parents:
        return "active_usb"
    return "usb"


def download(candidate: pd.Series) -> dict[str, object]:
    existing = resolve_existing(candidate)
    expected = str(candidate["source_md5"])
    if existing is not None:
        observed = file_md5(existing)
        return {
            "priority": int(candidate["priority"]),
            "candidate_id": candidate["candidate_id"],
            "queue_role": candidate["queue_role"],
            "resolved_source_path": str(existing),
            "source_storage": source_storage_label(existing),
            "status": "verified_existing" if observed == expected else "checksum_mismatch",
            "size_bytes": existing.stat().st_size,
            "expected_md5": expected,
            "observed_md5": observed,
        }

    destination = ACTIVE_SOURCE_ROOT / str(candidate["candidate_id"]) / str(candidate["source_file"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    returncode = 1
    for attempt in range(1, 11):
        print(f"{candidate['candidate_id']}: download attempt {attempt}", flush=True)
        completed = subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "--silent",
                "--show-error",
                "--continue-at",
                "-",
                "--output",
                str(partial),
                str(candidate["source_url"]),
            ],
            check=False,
        )
        returncode = completed.returncode
        if returncode == 0:
            break
        time.sleep(min(5 * attempt, 30))
    observed = file_md5(partial) if partial.is_file() else ""
    if returncode == 0 and observed == expected:
        partial.replace(destination)
        status = "downloaded_and_verified"
    elif returncode == 0:
        status = "checksum_mismatch"
    else:
        status = f"curl_failed_{returncode}"
    return {
        "priority": int(candidate["priority"]),
        "candidate_id": candidate["candidate_id"],
        "queue_role": candidate["queue_role"],
        "resolved_source_path": str(destination),
        "source_storage": source_storage_label(destination),
        "status": status,
        "size_bytes": destination.stat().st_size if destination.is_file() else 0,
        "expected_md5": expected,
        "observed_md5": observed,
    }


def write_manifest(rows: list[dict[str, object]]) -> pd.DataFrame:
    current = pd.DataFrame(rows)
    previous_frames = []
    for path in (ACTIVE_MANIFEST, ACTIVE_USB_MANIFEST):
        if path.is_file():
            previous_frames.append(pd.read_csv(path, sep="\t"))
    if previous_frames:
        queue_ids = set(pd.read_csv(ACTIVE_QUEUE, sep="\t")["candidate_id"].astype(str))
        previous = pd.concat(previous_frames, ignore_index=True)
        previous = previous[previous["candidate_id"].astype(str).isin(queue_ids)]
        manifest = pd.concat([previous, current], ignore_index=True)
        manifest = manifest.drop_duplicates("candidate_id", keep="last")
    else:
        manifest = current
    manifest = manifest.sort_values("priority")
    local = ACTIVE_MANIFEST
    usb = ACTIVE_USB_MANIFEST
    usb.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(local, sep="\t", index=False)
    manifest.to_csv(usb, sep="\t", index=False)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-id", action="append", default=[])
    parser.add_argument("--queue", type=Path, default=QUEUE)
    parser.add_argument("--source-root", type=Path, default=V3_SOURCES)
    parser.add_argument("--manifest", type=Path, default=ROOT / "evidence/expansion_v3_source_manifest.tsv")
    parser.add_argument(
        "--usb-manifest",
        type=Path,
        default=USB / "pgaa_cross_platform/v3/source_manifest.tsv",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="number of concurrent source resolution/download workers",
    )
    args = parser.parse_args(argv)
    if args.workers < 1:
        raise SystemExit("--workers must be at least 1")
    global ACTIVE_QUEUE, ACTIVE_SOURCE_ROOT, ACTIVE_MANIFEST, ACTIVE_USB_MANIFEST
    ACTIVE_QUEUE = args.queue
    ACTIVE_SOURCE_ROOT = args.source_root
    ACTIVE_MANIFEST = args.manifest
    ACTIVE_USB_MANIFEST = args.usb_manifest
    if not USB.is_mount():
        raise SystemExit("/Volumes/MOVESPEED is not mounted")
    if shutil.disk_usage(USB).free < 10 * 1024**3:
        raise SystemExit("less than 10 GiB remains on the USB volume")
    queue = pd.read_csv(ACTIVE_QUEUE, sep="\t").sort_values("priority")
    if args.candidate_id:
        requested = set(args.candidate_id)
        queue = queue[queue["candidate_id"].isin(requested)]
        missing = requested - set(queue["candidate_id"])
        if missing:
            raise SystemExit(f"unknown candidate IDs: {sorted(missing)}")
    candidates = [candidate for _, candidate in queue.iterrows()]
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download, candidate): candidate for candidate in candidates}
        for future in as_completed(futures):
            candidate = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                row = {
                    "priority": int(candidate["priority"]),
                    "candidate_id": candidate["candidate_id"],
                    "queue_role": candidate["queue_role"],
                    "resolved_source_path": "",
                    "source_storage": "unresolved",
                    "status": f"worker_exception:{type(exc).__name__}",
                    "size_bytes": 0,
                    "expected_md5": str(candidate["source_md5"]),
                    "observed_md5": "",
                }
            rows.append(row)
            write_manifest(rows)
            print(f"{row['candidate_id']}: {row['status']}", flush=True)
    manifest = write_manifest(rows)
    valid = {"verified_existing", "downloaded_and_verified"}
    return int(not manifest["status"].isin(valid).all())


if __name__ == "__main__":
    raise SystemExit(main())
