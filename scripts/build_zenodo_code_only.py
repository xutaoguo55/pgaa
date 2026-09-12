#!/usr/bin/env python3
"""Build the code-only Zenodo release archive (mirrors the v0.1.0 convention).

Content rule: the package code and its release metadata only. Manuscript
sources, figures, source-data tables, audit material and submission packaging
stay out -- that is what the supplementary software archive is for.
"""
from __future__ import annotations

import hashlib
import re
import zipfile
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
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"version {ver} | entries {len(entries)} | bytes {out.stat().st_size}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
