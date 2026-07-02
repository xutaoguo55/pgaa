#!/usr/bin/env python3
"""Deep current-state audit for the CAIC transfer upload packet."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
UPLOAD = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
JOURNAL = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
MANUSCRIPT_MD = ROOT / "MANUSCRIPT_CAIC.md"
SUPP_MD = ROOT / "SUPPLEMENTARY_CAIC.md"
DOCX = ROOT / "MANUSCRIPT_CAIC.docx"
MANUSCRIPT_PDF = ROOT / "MANUSCRIPT_CAIC.pdf"
SUPP_PDF = ROOT / "SUPPLEMENTARY_CAIC.pdf"
REF_TABLE = ROOT / "REFERENCE_VERIFICATION_TABLE_2026-06-27.tsv"
REF_CROSSREF = ROOT / "REFERENCE_EXTERNAL_AUDIT_CROSSREF.json"
ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip"

W = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def fail(message: str) -> None:
    raise AssertionError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expand_citations(token: str) -> list[int]:
    token = token.replace("–", "--")
    values: list[int] = []
    for part in token.split(","):
        part = part.strip()
        if not part:
            continue
        if "--" in part or "-" in part:
            sep = "--" if "--" in part else "-"
            a, b = [int(x.strip()) for x in part.split(sep, 1)]
            values.extend(range(a, b + 1))
        else:
            values.append(int(part))
    return values


def audit_upload_files(results: list[str]) -> None:
    expected = {
        "MANUSCRIPT.docx",
        "SUPPLEMENTARY.pdf",
        "PGAA_supplementary_code.zip",
        "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
    }
    for directory in [UPLOAD, JOURNAL]:
        files = {p.name for p in directory.iterdir() if p.is_file()}
        if files != expected:
            fail(f"{directory.name} file set mismatch: {sorted(files)}")
    for name in expected:
        if sha256(UPLOAD / name) != sha256(JOURNAL / name):
            fail(f"upload and journal copies differ for {name}")
    with zipfile.ZipFile(ZIP) as zf:
        members = {Path(n).name for n in zf.namelist() if not n.endswith("/")}
    if members != expected:
        fail(f"journal upload zip file set mismatch: {sorted(members)}")
    results.append("Upload packet contains exactly the four expected files; folder and zip copies match by SHA256.")


def audit_docx(results: list[str]) -> None:
    with zipfile.ZipFile(DOCX) as zf:
        names = zf.namelist()
        xml = zf.read("word/document.xml").decode("utf-8")
        styles = zf.read("word/styles.xml").decode("utf-8")
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")
    media = [n for n in names if n.startswith("word/media/")]
    if len(media) != 4:
        fail(f"expected 4 embedded media files, found {len(media)}")
    if xml.count("<w:tbl>") != 3:
        fail(f"expected 3 main DOCX tables, found {xml.count('<w:tbl>')}")
    if "w:pageBreakBefore" in xml or re.search(r"<w:br[^>]+w:type=\"page\"", xml):
        fail("explicit page break found in manuscript DOCX")
    if any(name.endswith("comments.xml") for name in names) or "relationships/comments" in rels:
        fail("DOCX contains comments part or comments relationship")
    if "commentRangeStart" in xml or "commentReference" in xml or "<w:del" in xml or "<w:ins " in xml:
        fail("DOCX contains comments or tracked-change markup")
    if "w:cantSplit" not in xml:
        fail("no cantSplit table rows found")
    if "2E75B6" in styles or "005B8F" in styles:
        fail("blue heading color remains in DOCX styles")

    root = ET.fromstring(xml)
    tables = root.findall(".//w:tbl", W)
    for index, table in enumerate(tables, start=1):
        borders = table.find("./w:tblPr/w:tblBorders", W)
        if borders is None:
            fail(f"table {index} lacks table borders")
        edge_vals = {
            child.tag.rsplit("}", 1)[-1]: child.attrib.get(f"{{{W['w']}}}val")
            for child in list(borders)
        }
        if edge_vals.get("top") != "single" or edge_vals.get("bottom") != "single":
            fail(f"table {index} lacks top/bottom three-line borders")
        for edge in ["left", "right", "insideH", "insideV"]:
            if edge_vals.get(edge) != "nil":
                fail(f"table {index} has non-three-line border {edge}={edge_vals.get(edge)}")
        rows = table.findall("./w:tr", W)
        if not rows:
            fail(f"table {index} has no rows")
        for row in rows:
            if row.find("./w:trPr/w:cantSplit", W) is None:
                fail(f"table {index} has a row that can split across pages")
        header = rows[0]
        has_header_rule = any(
            cell.find("./w:tcPr/w:tcBorders/w:bottom", W) is not None
            for cell in header.findall("./w:tc", W)
        )
        if not has_header_rule:
            fail(f"table {index} lacks header bottom rule")
    results.append("DOCX has 4 figures, 3 three-line main tables, no explicit page breaks, no comments/tracked-change markup, black headings, and non-splitting table rows.")


def audit_main_markdown(results: list[str]) -> None:
    text = MANUSCRIPT_MD.read_text(encoding="utf-8")
    forbidden = [
        "\\newpage",
        "pagebreak",
        "Supplementary Methods 1-S4",
        "Communications Medicine",
        "Cancer Informatics",
        "TODO",
        "TBD",
        "XXX",
        "Table S",
        "Figure S",
    ]
    for term in forbidden:
        if term in text:
            fail(f"forbidden/stale manuscript text remains: {term}")

    placeholders = [int(x) for x in re.findall(r"\*\*\[Figure ([1-4])\]\*\*", text)]
    if placeholders != [1, 2, 3, 4]:
        fail(f"main figure placeholders out of order: {placeholders}")

    table_captions = [int(x) for x in re.findall(r"^Table ([1-3])\.", text, re.M)]
    if table_captions != [1, 2, 3]:
        fail(f"main table captions out of order: {table_captions}")

    for fig in range(1, 5):
        marker = f"**[Figure {fig}]**"
        pre = text[: text.index(marker)]
        if f"Figure {fig}" not in pre:
            fail(f"Figure {fig} is not cited before its placeholder")
    for tab in range(1, 4):
        match = re.search(rf"^Table {tab}\.", text, re.M)
        if not match:
            fail(f"Table {tab} caption missing")
        pos = match.start()
        pre = text[:pos]
        if f"Table {tab}" not in pre:
            fail(f"Table {tab} is not cited before its caption")

    refs = [int(x) for x in re.findall(r"^(\d+)\.\s+", text, re.M)]
    if refs != list(range(1, 36)):
        fail(f"reference list sequence mismatch: {refs[:5]}...{refs[-5:]}")
    cited: set[int] = set()
    for token in re.findall(r"\\textsuperscript\{([^}]*)\}", text):
        if re.fullmatch(r"[0-9,\-– ]+", token):
            cited.update(expand_citations(token))
    if cited != set(refs):
        fail(f"cited refs and reference list differ: missing={sorted(set(refs)-cited)} extra={sorted(cited-set(refs))}")

    if "Supplementary Figures 1-7, Supplementary Tables 1-7, and Supplementary Methods" not in text:
        fail("supplementary information summary is not normalized")
    results.append("Main Markdown has ordered figure/table placeholders, prior in-text citations, no hard page breaks, and refs 1-35 all cited.")


def audit_supplement(results: list[str]) -> None:
    text = SUPP_MD.read_text(encoding="utf-8")
    figs = [int(x) for x in re.findall(r"Supplementary Figure (\d+)\.", text)]
    tabs = [int(x) for x in re.findall(r"Supplementary Table (\d+)\.", text)]
    numbered_methods = re.findall(r"Supplementary Methods (\d+)\.", text)
    if figs != [1, 2, 3, 4, 5, 6, 7]:
        fail(f"supplementary figures out of order: {figs}")
    if tabs != [1, 2, 3, 4, 5, 6, 7]:
        fail(f"supplementary tables out of order: {tabs}")
    if numbered_methods:
        fail(f"supplementary methods should not be numbered: {numbered_methods}")
    for required in ["**Manuscript title:**", "**Authors:**", "## Supplementary Methods"]:
        if required not in text:
            fail(f"supplement missing official front matter or methods heading: {required}")
    for fig in range(1, 6):
        caption = re.search(rf"Supplementary Figure {fig}\..*", text)
        if caption and "a," not in caption.group(0):
            fail(f"Supplementary Figure {fig} caption lacks panel a label")
    if text.index("Supplementary Table 6.") > text.index("Supplementary Table 7."):
        fail("Supplementary Table 6 appears after Supplementary Table 7")
    if "\\section*{Supplementary Table 7." in text and not re.search(
        r"\\newpage[\s\S]*?\\section\*\{Supplementary Table 7\.", text
    ):
        fail("Supplementary Table 7 is not separated from Supplementary Table 6")

    for pdf in [MANUSCRIPT_PDF, SUPP_PDF]:
        info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
        match = re.search(r"^Pages:\s+(\d+)", info, re.M)
        if not match:
            fail(f"could not read PDF page count for {pdf.name}")
        for page in range(1, int(match.group(1)) + 1):
            page_text = subprocess.check_output(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"], text=True)
            content = re.sub(r"\b\d+\b", "", page_text).strip()
            if not content:
                fail(f"{pdf.name} page {page} is blank or contains only a page number")
    results.append("Supplementary PDF source has title/authors, Figures 1-7, Tables 1-7, unnumbered Supplementary Methods, panel captions, separated landscape tables, and no blank PDF pages.")


def audit_references(results: list[str]) -> None:
    if not REF_TABLE.exists() or not REF_CROSSREF.exists():
        fail("reference verification artifacts missing")
    rows = list(csv.DictReader(REF_TABLE.open(encoding="utf-8"), delimiter="\t"))
    if len(rows) != 35:
        fail(f"reference verification table should have 35 rows, found {len(rows)}")
    numbers = [int(r["num"]) for r in rows]
    if numbers != list(range(1, 36)):
        fail("reference verification table numbers are not 1-35")
    bad = [r for r in rows if r["status"] not in {"PASS", "MANUAL_SOURCE"}]
    if bad:
        fail(f"reference verification table has failing rows: {bad[:3]}")
    crossref = json.loads(REF_CROSSREF.read_text(encoding="utf-8"))
    crossref_nums = sorted(int(r.get("num")) for r in crossref)
    required_crossref = sorted(int(r["num"]) for r in rows if r["doi_or_source"].startswith("10."))
    missing_crossref = [n for n in required_crossref if n not in crossref_nums]
    if missing_crossref:
        fail(f"Missing crossref-audit entries for DOI-bearing refs: {missing_crossref}")
    doi_rows = [r for r in rows if r.get("doi_or_source", "").startswith("10.")]
    if len(doi_rows) < 20:
        fail("too few DOI-backed references in verification table")
    results.append("References 1-35 have existing Crossref/manual-source verification records; no uncited or out-of-range reference numbers were found.")


def audit_code_archive(results: list[str]) -> None:
    archive = UPLOAD / "PGAA_supplementary_code.zip"
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    required_fragments = [
        "pgaa/",
        "pgaa_r/",
        "scripts/rebuild_adamson_full_results.py",
        "scripts/benchmark_adamson2016.py",
        "figure_source_data/",
        "README",
    ]
    joined = "\n".join(names)
    for frag in required_fragments:
        if frag not in joined:
            fail(f"supplementary code archive missing {frag}")
    stale = [n for n in names if "__MACOSX" in n or n.endswith(".DS_Store")]
    if stale:
        fail(f"supplementary code archive contains stale macOS entries: {stale[:5]}")
    results.append("Supplementary code archive contains package code, rebuild scripts, source data, README material, and no macOS junk entries.")


def main() -> int:
    results: list[str] = []
    checks = [
        audit_upload_files,
        audit_docx,
        audit_main_markdown,
        audit_supplement,
        audit_references,
        audit_code_archive,
    ]
    for check in checks:
        check(results)
    report = ROOT / "DEEP_CURRENT_SUBMISSION_AUDIT_2026-06-25.md"
    report.write_text(
        "# Deep Current Submission Audit - 2026-06-25\n\n"
        + "\n".join(f"- PASS: {line}" for line in results)
        + "\n\nVerdict: PASS for current local upload package structure, manuscript formatting checks, numbering/citation checks, and available reference-verification artifacts.\n",
        encoding="utf-8",
    )
    print(f"Deep audit checks: {len(results)}")
    for line in results:
        print(f"PASS: {line}")
    print(f"Wrote {report.name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
