#!/usr/bin/env python3
"""Final Bioinformatics upload gate for software availability.

Run with --allow-pending during author-review package checks. Run without that
flag immediately before final upload; strict mode fails until the repository URL
is public and an archive DOI or persistent URL has been added.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_URL = "https://github.com/xutaoguo55/pgaa"
TEXT_FILES = [
    "MANUSCRIPT.md",
    "SUPPLEMENTARY.md",
    "PORTAL_INPUTS.md",
    "README.md",
    "RELEASE_ARCHIVE_CHECKLIST.md",
    "SUBMISSION_READINESS_AUDIT.md",
    "CITATION.cff",
    "codemeta.json",
    "COVER_LETTER_BIOINFORMATICS.md",
]

BLOCKING_TEXT_FILES = [
    "MANUSCRIPT.md",
    "SUPPLEMENTARY.md",
    "PORTAL_INPUTS.md",
    "CITATION.cff",
    "codemeta.json",
    "COVER_LETTER_BIOINFORMATICS.md",
]

ADVISORY_TEXT_FILES = [
    "README.md",
    "RELEASE_ARCHIVE_CHECKLIST.md",
    "SUBMISSION_READINESS_AUDIT.md",
]

BLOCKING_PENDING_MARKERS = [
    "must be activated before final submission",
    "must be publicly reachable",
    "pending deposition before final submission",
    "Do not enter a URL until",
    "should be added before final submission",
    "to be inserted before final submission",
    "still needs a permanent archive",
    "[insert archive DOI or persistent URL]",
    "[archive DOI or persistent URL]",
    "[repository URL]",
    "[Author names]",
    "[Affiliations]",
    "[Contact email]",
]

ADVISORY_PENDING_MARKERS = [
    "Before final submission",
    "still needs a permanent archive",
]

ARCHIVE_PATTERNS = [
    re.compile(r"https://doi\.org/10\.\d{4,9}/[-._;()/:A-Za-z0-9]+"),
    re.compile(r"\bdoi:\s*10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE),
    re.compile(r"https://zenodo\.org/records/\d+"),
    re.compile(r"https://figshare\.com/[^)\s]+"),
    re.compile(r"https://archive\.softwareheritage\.org/[^)\s]+"),
    re.compile(r"https://codeocean\.com/[^)\s]+"),
]

NON_ARCHIVE_IDENTIFIER_FRAGMENTS = [
    "10.5063/schema/codemeta",
]


def read_texts() -> dict[str, str]:
    texts = {}
    for rel in TEXT_FILES:
        path = ROOT / rel
        if path.exists():
            texts[rel] = path.read_text(errors="replace")
        else:
            texts[rel] = ""
    return texts


def read_repo_url() -> str:
    path = ROOT / "codemeta.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            repo_url = data.get("codeRepository") or data.get("url")
            if isinstance(repo_url, str) and repo_url.startswith(("http://", "https://")):
                return repo_url
        except json.JSONDecodeError:
            pass
    return DEFAULT_REPO_URL


def check_repo_reachable(repo_url: str) -> tuple[bool, str]:
    req = Request(repo_url, method="HEAD", headers={"User-Agent": "PGAA-upload-gate"})
    try:
        with urlopen(req, timeout=10) as response:
            status = getattr(response, "status", 0)
            return 200 <= status < 400, f"HTTP {status}"
    except HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except URLError as exc:
        return False, f"URL error: {exc.reason}"
    except TimeoutError:
        return False, "timeout"


def find_archive_identifier(texts: dict[str, str]) -> list[str]:
    hits: list[str] = []
    for rel, text in texts.items():
        for pattern in ARCHIVE_PATTERNS:
            for match in pattern.finditer(text):
                value = match.group(0).rstrip(".,;")
                if any(fragment in value for fragment in NON_ARCHIVE_IDENTIFIER_FRAGMENTS):
                    continue
                hits.append(f"{rel}: {value}")
    return sorted(set(hits))


def find_pending_markers(
    texts: dict[str, str],
    files: list[str],
    markers: list[str],
) -> list[str]:
    hits: list[str] = []
    for rel in files:
        text = texts.get(rel, "")
        for marker in markers:
            if marker in text:
                hits.append(f"{rel}: {marker}")
    return hits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="Report blockers but exit 0 for author-review package checks.",
    )
    args = parser.parse_args()

    texts = read_texts()
    repo_url = read_repo_url()
    repo_ok, repo_status = check_repo_reachable(repo_url)
    archive_hits = find_archive_identifier(texts)
    blocking_pending_hits = find_pending_markers(
        texts, BLOCKING_TEXT_FILES, BLOCKING_PENDING_MARKERS
    )
    advisory_pending_hits = find_pending_markers(
        texts, ADVISORY_TEXT_FILES, ADVISORY_PENDING_MARKERS
    )

    blockers: list[str] = []
    if not repo_ok:
        blockers.append(f"Repository URL is not publicly reachable: {repo_url} ({repo_status})")
    if not archive_hits:
        blockers.append("No archive DOI or persistent URL found in the submission text files")
    if blocking_pending_hits:
        blockers.append("Pending final-submission markers remain in final-facing text")

    print("BIOINFORMATICS UPLOAD GATE")
    print(f"Repository: {repo_url} -> {repo_status}")
    if archive_hits:
        print("Archive identifiers:")
        for hit in archive_hits:
            print(f"- {hit}")
    else:
        print("Archive identifiers: none found")
    if blocking_pending_hits:
        print("Blocking pending markers:")
        for hit in blocking_pending_hits:
            print(f"- {hit}")
    if advisory_pending_hits:
        print("Advisory pending markers:")
        for hit in advisory_pending_hits:
            print(f"- {hit}")

    if blockers:
        print("UPLOAD GATE NOT READY")
        for blocker in blockers:
            print(f"- {blocker}")
        if not args.allow_pending:
            raise SystemExit(1)
        print("allow-pending enabled; returning success for author-review checks")
        return

    print("UPLOAD GATE PASSED")


if __name__ == "__main__":
    main()
