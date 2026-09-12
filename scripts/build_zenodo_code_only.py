#!/usr/bin/env python3
"""Build the code-only Zenodo release archive (mirrors the v0.1.0 convention).

Content rule: the package code and its release metadata only. Manuscript
sources, figures, source-data tables, audit material and submission packaging
stay out -- that is what the supplementary software archive is for.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "ZENODO_CODE_ONLY_RELEASE"

TOP_LEVEL = [
    ".zenodo.json", "CITATION.cff", "Dockerfile", "LICENSE", "README.md",
    "codemeta.json", "environment.yml", "pyproject.toml", "requirements.txt",
    "requirements-lock.txt",
]
CODE_DIRS = ["pgaa", "pgaa_r", "tests", "scripts"]


def version() -> str:
    text = (ROOT / "pyproject.toml").read_text()
    return re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE).group(1)


def collect() -> list[Path]:
    files: list[Path] = []
    for name in TOP_LEVEL:
        path = ROOT / name
        if path.exists():
            files.append(path)
    for name in CODE_DIRS:
        base = ROOT / name
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            # scripts/ ships code only; its CSV/TIF/log outputs are data.
            if name == "scripts" and path.suffix != ".py":
                continue
            files.append(path)
    return files


CONCEPT_DOI = "10.5281/zenodo.20681140"
EXCLUDED = ("MANUSCRIPT.*, SUPPLEMENTARY.*, figure_source_data/, figures_png/, "
            "evidence/, data/, COMMUNICATIONS_*_TRANSFER/, AUDIT_*/, submission "
            "checklists, cover letters, portal drafts, and the CSV/TIF outputs "
            "under scripts/")


def upload_fields(ver: str, archive: Path, entries: list[str], digest: str) -> str:
    """The manual fallback for scripts/zenodo_publish.py, as a plain text sheet."""
    meta = json.loads((ROOT / ".zenodo.json").read_text())
    included = [name for name in TOP_LEVEL if (ROOT / name).exists()]
    included += [f"{name}/ ({sum(1 for e in entries if e.startswith(name + '/'))} files)"
                 for name in CODE_DIRS]
    creators = "\n".join(
        c["name"] + (f" ({c['affiliation']})" if c.get("affiliation") else "")
        for c in meta["creators"])
    related = meta["related_identifiers"][0]
    today = date.today().isoformat()
    return f"""PGAA v{ver} code-only Zenodo release — upload fields
Generated {today}. This file records the deposit fields and the archive
digest. It is the manual fallback for scripts/zenodo_publish.py.

Upload file:
{archive.name}
({len(entries)} entries, {archive.stat().st_size:,} bytes)

Upload type:
Software

Title:
{meta['title']}

Version:
{ver}

Publication date:
{today}

Creators:
{creators}

Description:
{meta['description']}

License:
{meta['license']}

Keywords:
{'; '.join(meta['keywords'])}

Related identifier:
{related['identifier']}
Relation: {related['relation']}

Concept DOI:
{CONCEPT_DOI}

SHA256:
{digest}

Content rule:
Package code and release metadata only. Included: {', '.join(included)}.
Excluded: {EXCLUDED}. The supplementary software archive
(PGAA_supplementary_code.zip) remains the place for source data, manuscript
sources and figure/table regeneration.

Caveat to state plainly: scripts/ is included as code, but many of those
scripts read inputs (data/, figure_source_data/) that this code-only archive
does not carry, so they are not runnable from this archive alone. The runnable
subset is the package plus scripts/run_toy_example.py, scripts/test_python_pkg.py
and tests/.
"""


def main() -> int:
    ver = version()
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"PGAA_v{ver}_code_only_for_Zenodo.zip"
    files = collect()
    entries: list[str] = []
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())
            entries.append(rel)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    fields = OUT_DIR / f"ZENODO_MANUAL_UPLOAD_FIELDS_v{ver}.txt"
    fields.write_text(upload_fields(ver, out, entries, digest))
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"wrote {fields.relative_to(ROOT)}")
    print(f"version {ver} | entries {len(entries)} | bytes {out.stat().st_size}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
