#!/usr/bin/env python3
"""Mint a new Zenodo version of the PGAA concept record and attach the archive.

Needs a Zenodo personal access token with deposit:write, e.g.

    export ZENODO_TOKEN=...        # or:  ! export ZENODO_TOKEN=...

    python3 scripts/zenodo_publish.py                  # dry run: draft + upload
    python3 scripts/zenodo_publish.py --publish        # publish the draft
    python3 scripts/zenodo_publish.py --inspect        # show draft state
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://zenodo.org/api"
CONCEPT_RECID = 20681140
# The deposition `actions/newversion` is called on: the newest published version,
# which has to be bumped by hand each time a new version is minted.
LATEST_RECID = 22720271


def version() -> str:
    text = (ROOT / "pyproject.toml").read_text()
    return re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE).group(1)


# The archive filename carries the version, so keep it derived rather than typed.
ARCHIVE = ROOT / "ZENODO_CODE_ONLY_RELEASE" / f"PGAA_v{version()}_code_only_for_Zenodo.zip"


def token() -> str:
    """Token from the environment, else from a file the shell did not have to see."""
    value = os.environ.get("ZENODO_TOKEN", "").strip()
    if value:
        return value
    for path in (ROOT / ".zenodo_token", Path.home() / ".zenodo_token"):
        if path.exists():
            value = path.read_text().strip()
            if value:
                return value
    raise SystemExit(
        "no Zenodo token: set ZENODO_TOKEN, or write the token to "
        f"{ROOT / '.zenodo_token'} or {Path.home() / '.zenodo_token'}"
    )


def call(method: str, url: str, tok: str, payload: dict | None = None,
         raw: bytes | None = None, ctype: str = "application/json"):
    headers = {"Authorization": f"Bearer {tok}"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = ctype
    elif raw is not None:
        data = raw
        headers["Content-Type"] = ctype
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"{method} {url} -> {exc.code}\n{exc.read().decode(errors='replace')[:2000]}")
    return json.loads(body) if body else {}


def metadata() -> dict:
    meta = json.loads((ROOT / ".zenodo.json").read_text())
    meta.setdefault("publication_date", "2026-09-12")
    return meta


def show(dep: dict) -> None:
    print(f"  deposition id : {dep.get('id')}")
    print(f"  state         : {dep.get('state')}  submitted={dep.get('submitted')}")
    print(f"  doi           : {dep.get('doi') or dep.get('metadata', {}).get('prereserve_doi')}")
    for f in dep.get("files", []):
        print(f"  file          : {f.get('filename') or f.get('key')}  {(f.get('filesize') or f.get('size') or 0):,} bytes")
    print(f"  html          : {dep.get('links', {}).get('html')}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true", help="publish the draft after uploading")
    ap.add_argument("--inspect", action="store_true", help="only show the current draft")
    ap.add_argument("--deposition-id", type=int, help="reuse an existing draft deposition")
    args = ap.parse_args()
    tok = token()

    if args.inspect:
        if not args.deposition_id:
            raise SystemExit("--inspect needs --deposition-id")
        show(call("GET", f"{API}/deposit/depositions/{args.deposition_id}", tok))
        return 0

    if not ARCHIVE.exists():
        raise SystemExit(f"missing archive: {ARCHIVE} — run scripts/build_zenodo_code_only.py")

    if args.deposition_id:
        dep_id = args.deposition_id
        print(f"reusing draft deposition {dep_id}")
    else:
        print(f"opening a new version of concept {CONCEPT_RECID} (latest {LATEST_RECID}) ...")
        new = call("POST", f"{API}/deposit/depositions/{LATEST_RECID}/actions/newversion", tok)
        draft_url = new["links"]["latest_draft"]
        dep_id = int(draft_url.rstrip("/").split("/")[-1])
        draft = call("GET", draft_url, tok)
        print(f"draft deposition {dep_id}; removing files inherited from the previous version")
        for f in draft.get("files", []):
            fid = f.get("id") or f.get("file_id")
            call("DELETE", f"{API}/deposit/depositions/{dep_id}/files/{fid}", tok)

    bucket = call("GET", f"{API}/deposit/depositions/{dep_id}", tok)["links"]["bucket"]
    print(f"uploading {ARCHIVE.name} ({ARCHIVE.stat().st_size:,} bytes) ...")
    uploaded = call("PUT", f"{bucket}/{ARCHIVE.name}", tok,
                    raw=ARCHIVE.read_bytes(), ctype="application/octet-stream")
    print(f"  uploaded key: {uploaded.get('key')}  size: {uploaded.get('size'):,}")

    print("setting metadata ...")
    call("PUT", f"{API}/deposit/depositions/{dep_id}", tok, payload={"metadata": metadata()})

    if not args.publish:
        print("\ndry run complete — draft NOT published.\n")
        show(call("GET", f"{API}/deposit/depositions/{dep_id}", tok))
        print(f"\nre-run with:  --publish --deposition-id {dep_id}")
        return 0

    print("publishing ...")
    pub = call("POST", f"{API}/deposit/depositions/{dep_id}/actions/publish", tok)
    doi = pub.get("doi", "")
    print("\nPUBLISHED")
    show(pub)
    print(f"\nversion DOI : https://doi.org/{doi}")
    print(f"concept DOI : https://doi.org/10.5281/zenodo.{pub.get('conceptrecid', CONCEPT_RECID)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
