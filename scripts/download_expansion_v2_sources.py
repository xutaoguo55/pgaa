#!/usr/bin/env python3
"""Download frozen expansion-v2 sources directly to the USB volume."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import hashlib
from pathlib import Path
import shutil
import subprocess
import time

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "evidence/expansion_v2_candidate_queue.tsv"
QUEUE_AMENDMENTS = (ROOT / "evidence/expansion_v2_candidate_queue_amendment_02.tsv",)
USB_ROOT = Path("/Volumes/MOVESPEED/pgaa_cross_platform/v2")


def file_md5(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(rows: list[dict[str, object]]) -> None:
    USB_ROOT.mkdir(parents=True, exist_ok=True)
    usb_manifest = USB_ROOT / "download_manifest.tsv"
    local_manifest = ROOT / "evidence/expansion_v2_download_manifest.tsv"
    incoming = pd.DataFrame(rows)
    lock_path = USB_ROOT / ".download_manifest.lock"
    with lock_path.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existing = (
            pd.read_csv(usb_manifest, sep="\t")
            if usb_manifest.is_file()
            else pd.DataFrame()
        )
        manifest = pd.concat([existing, incoming], ignore_index=True)
        manifest = (
            manifest.drop_duplicates("candidate_id", keep="last")
            .sort_values("priority")
            .reset_index(drop=True)
        )
        for destination in (usb_manifest, local_manifest):
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            manifest.to_csv(temporary, sep="\t", index=False)
            temporary.replace(destination)


def download_candidate(candidate: pd.Series) -> dict[str, object]:
    destination_dir = USB_ROOT / "sources" / str(candidate["candidate_id"])
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / str(candidate["source_file"])
    partial = destination.with_suffix(destination.suffix + ".part")
    expected_md5 = str(candidate["source_md5"])
    status = "pending"
    observed_md5 = ""
    if destination.is_file() and file_md5(destination) == expected_md5:
        status = "verified_existing"
        observed_md5 = expected_md5
    else:
        if partial.is_file():
            partial_md5 = file_md5(partial)
            if partial_md5 == expected_md5:
                partial.replace(destination)
                return {
                    "priority": int(candidate["priority"]),
                    "candidate_id": candidate["candidate_id"],
                    "queue_role": candidate["queue_role"],
                    "destination": str(destination),
                    "status": "verified_complete_partial",
                    "size_bytes": destination.stat().st_size,
                    "expected_md5": expected_md5,
                    "observed_md5": partial_md5,
                }
        print(f"Downloading {candidate['candidate_id']} -> {partial}", flush=True)
        returncode = 1
        for attempt in range(1, 21):
            size_before = partial.stat().st_size if partial.exists() else 0
            command = [
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
            ]
            completed = subprocess.run(command, check=False)
            returncode = completed.returncode
            if returncode == 0:
                break
            size_after = partial.stat().st_size if partial.exists() else 0
            print(
                f"{candidate['candidate_id']}: curl attempt {attempt} failed "
                f"({returncode}); retained {size_after} bytes",
                flush=True,
            )
            if size_after < size_before:
                raise RuntimeError(
                    f"partial download shrank from {size_before} to {size_after} bytes"
                )
            time.sleep(min(5 * attempt, 30))
        if returncode == 0:
            observed_md5 = file_md5(partial)
            if observed_md5 == expected_md5:
                partial.replace(destination)
                status = "downloaded_and_verified"
            else:
                status = "checksum_mismatch"
        else:
            status = f"curl_failed_{returncode}"
    return {
        "priority": int(candidate["priority"]),
        "candidate_id": candidate["candidate_id"],
        "queue_role": candidate["queue_role"],
        "destination": str(destination),
        "status": status,
        "size_bytes": destination.stat().st_size if destination.exists() else 0,
        "expected_md5": expected_md5,
        "observed_md5": observed_md5,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-alternates", action="store_true")
    parser.add_argument(
        "--candidate-id",
        action="append",
        default=[],
        help="Download only this frozen candidate ID; repeat for multiple IDs.",
    )
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args(argv)

    if not Path("/Volumes/MOVESPEED").is_mount():
        raise SystemExit("/Volumes/MOVESPEED is not mounted")
    queue_parts = [pd.read_csv(QUEUE, sep="\t")]
    queue_parts.extend(
        pd.read_csv(path, sep="\t") for path in QUEUE_AMENDMENTS if path.is_file()
    )
    queue = pd.concat(queue_parts, ignore_index=True).sort_values("priority")
    if args.candidate_id:
        requested = set(args.candidate_id)
        selected = queue[queue["candidate_id"].isin(requested)]
        missing = requested.difference(selected["candidate_id"])
        if missing:
            raise SystemExit(f"candidate IDs are not in the frozen queue: {sorted(missing)}")
    else:
        selected = queue if args.include_alternates else queue[queue["queue_role"].eq("primary")]
    free_bytes = shutil.disk_usage("/Volumes/MOVESPEED").free
    if free_bytes < 10 * 1024**3:
        raise SystemExit("less than 10 GiB remains on the USB volume")

    rows: list[dict[str, object]] = []
    candidates = [row for _, row in selected.sort_values("priority").iterrows()]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_candidate, candidate): candidate for candidate in candidates}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            rows.sort(key=lambda value: int(value["priority"]))
            write_manifest(rows)
            print(f"{row['candidate_id']}: {row['status']}", flush=True)
    failures = [
        row for row in rows
        if row["status"] not in {
            "verified_existing",
            "verified_complete_partial",
            "downloaded_and_verified",
        }
    ]
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
