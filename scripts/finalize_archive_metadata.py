#!/usr/bin/env python3
"""Synchronize final repository and archive identifiers before submission."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNED_REPO = "https://github.com/xutaoguo55/pgaa"

DOI_URL_RE = re.compile(r"^https://doi\.org/10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")
HTTP_URL_RE = re.compile(r"^https?://[^\s]+$")


def validate_url(label: str, value: str) -> None:
    if not HTTP_URL_RE.match(value):
        raise SystemExit(f"{label} must be an http(s) URL: {value}")


def citation_identifier(archive_url: str) -> tuple[str, str]:
    """Return a CFF identifier type/value pair."""
    if DOI_URL_RE.match(archive_url):
        return "doi", archive_url.removeprefix("https://doi.org/")
    return "url", archive_url


def replace_in_file(path: Path, replacements: dict[str, str], dry_run: bool) -> list[str]:
    text = path.read_text(errors="replace")
    new_text = text
    changed: list[str] = []
    for old, new in replacements.items():
        if old in new_text:
            new_text = new_text.replace(old, new)
            changed.append(old)
    if changed and not dry_run:
        path.write_text(new_text)
    return changed


def update_citation(repo_url: str, archive_url: str, dry_run: bool) -> list[str]:
    path = ROOT / "CITATION.cff"
    text = path.read_text(errors="replace")
    new_text = text.replace(PLANNED_REPO, repo_url)
    id_type, id_value = citation_identifier(archive_url)
    identifier_block = (
        "\nidentifiers:\n"
        f"  - type: {id_type}\n"
        f"    value: \"{id_value}\"\n"
        "    description: \"Archived software release\"\n"
    )
    if "identifiers:" not in new_text:
        new_text += identifier_block
    elif "Archived software release" not in new_text:
        new_text += (
            f"  - type: {id_type}\n"
            f"    value: \"{id_value}\"\n"
            "    description: \"Archived software release\"\n"
        )
    changed = ["repository URL"]
    if new_text != text and not dry_run:
        path.write_text(new_text)
    return changed if new_text != text else []


def update_codemeta(repo_url: str, archive_url: str, dry_run: bool) -> list[str]:
    path = ROOT / "codemeta.json"
    data = json.loads(path.read_text())
    changed: list[str] = []
    if data.get("codeRepository") != repo_url:
        data["codeRepository"] = repo_url
        changed.append("codeRepository")
    if data.get("url") != repo_url:
        data["url"] = repo_url
        changed.append("url")
    if data.get("identifier") != archive_url:
        data["identifier"] = archive_url
        changed.append("identifier")
    if changed and not dry_run:
        path.write_text(json.dumps(data, indent=2) + "\n")
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-url", required=True, help="Final public repository URL")
    parser.add_argument(
        "--archive-url",
        required=True,
        help="Final DOI or persistent archive URL, e.g. https://doi.org/10.xxxx/zenodo.x",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    validate_url("repo-url", args.repo_url)
    validate_url("archive-url", args.archive_url)

    replacements = {
        "repository and archive identifier to be inserted before final submission": (
            f"{args.repo_url}; archived release: {args.archive_url}"
        ),
        (
            "The planned public repository is https://github.com/xutaoguo55/pgaa; "
            "this URL must be publicly reachable, and a permanent Zenodo, Figshare, "
            "Software Heritage, or Code Ocean identifier must be added, before final "
            "submission to satisfy the journal's software-archiving policy."
        ): (
            f"The public repository is {args.repo_url}; the archived software "
            f"release is available at {args.archive_url}."
        ),
        (
            "Planned URL: https://github.com/xutaoguo55/pgaa; must be publicly "
            "reachable before final submission"
        ): args.repo_url,
        (
            "Python and R requirements are included in the package; exact archive "
            "DOI or persistent identifier pending deposition before final submission"
        ): f"Python and R requirements are included in the package; archived release: {args.archive_url}",
        (
            "Do not enter a URL until the repository is publicly reachable and/or "
            "the archived release DOI has been assigned. Planned repository: "
            "https://github.com/xutaoguo55/pgaa"
        ): args.archive_url,
        (
            "[Insert the archive DOI or persistent URL for the exact submitted "
            "PGAA release; preferred format: https://doi.org/10.xxxx/xxxxx. If "
            "the portal accepts only one value, use the archive DOI rather than "
            "the mutable GitHub URL.]"
        ): args.archive_url,
        "[archive DOI or persistent URL]": args.archive_url,
        "[repository URL]": args.repo_url,
        "[insert archive DOI or persistent URL]": args.archive_url,
        (
            "The planned public GitHub repository is https://github.com/xutaoguo55/pgaa. "
            "Before final submission, make that repository publicly reachable, archive "
            "the exact submitted software version through Zenodo, Figshare, Software "
            "Heritage, or Code Ocean, and replace this sentence with the assigned DOI "
            "or persistent URL."
        ): f"The public GitHub repository is {args.repo_url}. The archived software release is available at {args.archive_url}.",
    }

    targets = [
        ROOT / "MANUSCRIPT.md",
        ROOT / "SUPPLEMENTARY.md",
        ROOT / "PORTAL_INPUTS.md",
        ROOT / "COVER_LETTER_BIOINFORMATICS.md",
        ROOT / "README.md",
    ]
    for path in targets:
        changed = replace_in_file(path, replacements, args.dry_run)
        print(f"{path.relative_to(ROOT)}: {len(changed)} text replacement(s)")

    print(f"CITATION.cff: {len(update_citation(args.repo_url, args.archive_url, args.dry_run))} update(s)")
    print(f"codemeta.json: {len(update_codemeta(args.repo_url, args.archive_url, args.dry_run))} update(s)")

    if args.dry_run:
        print("dry-run only; no files changed")
    else:
        print("Archive metadata synchronized. Rebuild PDFs and rerun upload gate.")


if __name__ == "__main__":
    main()
