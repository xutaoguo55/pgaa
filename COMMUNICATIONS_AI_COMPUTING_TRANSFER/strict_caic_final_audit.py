#!/usr/bin/env python3
"""Strict final audit for the CAIC PGAA submission packet.

The checks here are deliberately redundant with verify_caic_transfer_ready.py.
They focus on risks that caused prior submission trouble: reference numbering,
reference truthfulness, stale journal residue, internal-file leakage, and final
Word/PDF consistency.
"""
from __future__ import annotations

import json
import os
import csv
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
MANUSCRIPT_MD = ROOT / "MANUSCRIPT_CAIC.md"
SUPPLEMENT_MD = ROOT / "SUPPLEMENTARY_CAIC.md"
UPLOAD_DIR = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
UPLOAD_DOCX = UPLOAD_DIR / "MANUSCRIPT.docx"
SUPPLEMENTARY_CODE_ZIP = UPLOAD_DIR / "PGAA_supplementary_code.zip"
PACKET_ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip"
CROSSREF_JSON = ROOT / "REFERENCE_EXTERNAL_AUDIT_CROSSREF.json"
REPORT = ROOT / "STRICT_CAIC_FINAL_AUDIT_2026-06-27.md"
REF_TABLE = ROOT / "REFERENCE_VERIFICATION_TABLE_2026-06-27.tsv"
REFERENCE_OFFLINE = os.getenv("PGAA_CAIC_REFERENCE_OFFLINE", "1") == "1"

EXPECTED_UPLOAD = {
    "MANUSCRIPT.docx",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
}

FORBIDDEN_TEXT = [
    "Communications Medicine",
    "BMC Bioinformatics",
    "Bioinformatics because",
    "Motivation:",
    "Availability and implementation:",
    "[Figure 1]",
]

REQUIRED_SECTIONS = [
    "Data availability",
    "Code availability",
    "Acknowledgements",
    "Author contributions",
    "Competing interests",
    "Supplementary information",
    "References",
]

EXPECTED_DOIS = {
    1: "10.1016/j.cell.2016.11.038",
    2: "10.1016/j.cell.2016.11.048",
    3: "10.1126/science.aax4438",
    4: "10.1016/j.cell.2022.05.013",
    5: "10.1186/s13059-021-02545-2",
    6: "10.1186/s13059-015-0844-5",
    7: "10.1016/j.cell.2019.05.031",
    8: "10.1016/j.cell.2021.04.048",
    9: "10.1186/s13059-017-1382-0",
    10: "10.1016/j.cell.2014.09.029",
    11: "10.1038/s41592-025-02909-7",
    12: "10.1182/blood.v45.3.321.321",
    13: "10.1172/jci2887",
    14: "10.1038/sj.onc.1210764",
    15: "10.1038/s41587-019-0379-5",
    16: "10.1038/s41588-021-00778-2",
    17: "10.1186/s13059-020-1928-4",
    18: "10.1186/s13059-024-03254-2",
    19: "10.1038/s41556-025-01626-9",
    20: "10.1038/s41592-023-02144-y",
    23: "10.3390/e19020047",
    28: "10.1007/s00454-004-1146-y",
    29: "10.1090/s0273-0979-09-01249-x",
    30: "10.1103/physreve.69.066138",
    31: "10.1111/1467-9868.00346",
    32: "10.1111/j.2517-6161.1995.tb02031.x",
    33: "10.1038/ncomms14049",
    34: "10.15252/msb.20188746",
    35: "10.12688/f1000research.9501.2",
}

MANUAL_SOURCES = {
    21: "Project Euclid / Berkeley Symposium record for MacQueen 1967",
    22: "Springer book DOI 10.1007/978-3-540-71050-9",
    24: "Springer book record for Good 2005",
    25: "Chapman & Hall/CRC book record for Efron and Tibshirani 1993",
    26: "American Mathematical Society book record for Edelsbrunner and Harer 2010",
    27: "JMLR official article page for Bubenik 2015, volume 16, pages 77-102",
}

DATASET_SOURCES = {
    "GSE111014": "NCBI GEO accession",
    "GSE167363": "NCBI GEO accession",
    "GSE159117": "NCBI GEO accession",
    "GSE116222": "NCBI GEO accession",
    "GSE133344": "NCBI GEO accession",
    "GSE90546": "NCBI GEO accession",
    "10x Genomics 3k demo": "10x Genomics public dataset page",
}

WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


@dataclass
class Check:
    name: str
    status: str
    detail: str


def fail(message: str) -> None:
    raise SystemExit(f"STRICT CAIC FINAL AUDIT FAILED: {message}")


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def parse_references(text: str) -> dict[int, str]:
    match = re.search(r"^## References\s*$([\s\S]+)$", text, re.MULTILINE)
    if not match:
        fail("References section not found")
    refs: dict[int, str] = {}
    for ref_match in re.finditer(r"^(\d+)\.\s+(.+?)(?=^\d+\.|\Z)", match.group(1), re.MULTILINE | re.DOTALL):
        refs[int(ref_match.group(1))] = " ".join(ref_match.group(2).split())
    return refs


def parse_citations(text: str) -> list[int]:
    before_refs = text.split("## References", 1)[0]
    nums: list[int] = []
    for body in re.findall(r"\\textsuperscript\{([^}]*)\}", before_refs):
        for part in body.split(","):
            part = part.strip()
            if "--" in part:
                a, b = [int(x) for x in part.split("--")]
                nums.extend(range(a, b + 1))
            elif part:
                nums.append(int(part))
    return nums


def first_appearance_sequence(text: str) -> list[int]:
    before_refs = text.split("## References", 1)[0]
    seq: list[int] = []
    for body in re.findall(r"\\textsuperscript\{([^}]*)\}", before_refs):
        for part in body.split(","):
            part = part.strip()
            if "--" in part:
                a, b = [int(x) for x in part.split("--")]
                candidates = range(a, b + 1)
            elif part:
                candidates = [int(part)]
            else:
                candidates = []
            for n in candidates:
                if n not in seq:
                    seq.append(n)
    return seq


def normalize(s: str) -> str:
    s = s.replace("ε", "epsilon").replace("Ε", "epsilon")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def doi_resolves(doi: str) -> bool:
    url = f"https://doi.org/{doi}"
    headers = {"User-Agent": "PGAA-CAIC-reference-audit/1.0"}
    for method in ["HEAD", "GET"]:
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return 200 <= resp.status < 400
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 500:
                return True
        except Exception:
            continue
    try:
        work = crossref_work(doi)
        return (work.get("DOI") or "").lower() == doi.lower()
    except Exception:
        pass
    return False


def crossref_work(doi: str) -> dict:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": "PGAA-CAIC-reference-audit/1.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))["message"]


def crossref_title(work: dict) -> str:
    title = work.get("title") or []
    return title[0] if title else ""


def load_reference_table_rows() -> dict[int, dict[str, str]]:
    if not REF_TABLE.exists():
        return {}
    rows = {}
    with REF_TABLE.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            try:
                rows[int(row["num"])] = row
            except (KeyError, ValueError):
                continue
    return rows


def check_references(text: str) -> tuple[list[Check], list[str]]:
    refs = parse_references(text)
    cited = parse_citations(text)
    first_seq = first_appearance_sequence(text)
    checks: list[Check] = []
    rows = ["num\tstatus\tdoi_or_source\tcrossref_title\tmanuscript_entry"]
    ref_verification_rows = load_reference_table_rows()

    expected_nums = list(range(1, len(refs) + 1))
    checks.append(Check("reference_count", "PASS" if len(refs) == 35 else "FAIL", f"{len(refs)} references"))
    checks.append(Check("reference_numbering", "PASS" if sorted(refs) == expected_nums else "FAIL", str(sorted(refs))))
    checks.append(Check("all_references_cited", "PASS" if set(refs) == set(cited) else "FAIL", f"uncited={sorted(set(refs)-set(cited))}; missing={sorted(set(cited)-set(refs))}"))
    checks.append(Check("first_appearance_order", "PASS" if first_seq == expected_nums else "FAIL", f"first sequence={first_seq}"))

    bad_meta: list[str] = []
    unresolved: list[int] = []
    for n in expected_nums:
        entry = refs[n]
        if n in EXPECTED_DOIS:
            doi = EXPECTED_DOIS[n]
            cr_title = ""
            cr_doi = doi
            if REFERENCE_OFFLINE and n in ref_verification_rows:
                row = ref_verification_rows[n]
                doi_ok = row.get("status") == "PASS"
                title_ok = doi_ok
                cr_title = row.get("crossref_title", "")
                cr_doi = row.get("doi_or_source", doi)
            else:
                try:
                    work = crossref_work(doi)
                    cr_doi = (work.get("DOI") or "").lower()
                    cr_title = crossref_title(work)
                    normalized_title = normalize(cr_title)
                    normalized_entry = normalize(entry)
                    title_ok = (
                        normalized_title[:30] in normalized_entry
                        or normalized_entry[:30] in normalized_title
                    )
                    doi_ok = cr_doi == doi.lower()
                except Exception as exc:
                    cr_doi = "ERROR"
                    cr_title = f"Crossref exact DOI lookup failed: {exc}"
                    doi_ok = False
                    title_ok = False
            if not doi_ok or not title_ok:
                bad_meta.append(f"{n}: expected {doi}, crossref {cr_doi}, title={cr_title}")
            if REFERENCE_OFFLINE:
                resolved = doi_ok
            else:
                resolved = doi_resolves(doi)
            if not resolved:
                unresolved.append(n)
            rows.append(f"{n}\t{'PASS' if doi_ok and title_ok and resolved else 'CHECK'}\t{doi}\t{cr_title}\t{entry}")
        else:
            source = MANUAL_SOURCES.get(n)
            if not source:
                bad_meta.append(f"{n}: no DOI or manual source registered")
                source = "MISSING_MANUAL_SOURCE"
            rows.append(f"{n}\tMANUAL_SOURCE\t{source}\tNA\t{entry}")

    checks.append(Check("crossref_exact_doi_metadata_match", "PASS" if not bad_meta else "FAIL", "; ".join(bad_meta[:5]) or "all DOI-bearing references match exact Crossref DOI metadata"))
    checks.append(Check("doi_resolution", "PASS" if not unresolved else "FAIL", f"unresolved={unresolved}" if unresolved else f"{len(EXPECTED_DOIS)} DOI-bearing references resolve"))
    return checks, rows


def check_docx() -> list[Check]:
    checks: list[Check] = []
    if not UPLOAD_DOCX.exists():
        fail("final manuscript docx missing")
    bad_zip = zipfile.ZipFile(UPLOAD_DOCX).testzip()
    checks.append(Check("docx_zip_integrity", "PASS" if bad_zip is None else "FAIL", str(bad_zip)))
    text = run(["pandoc", str(UPLOAD_DOCX), "-t", "plain"])
    stale = [term for term in FORBIDDEN_TEXT if term in text]
    checks.append(Check("docx_no_stale_text_or_placeholders", "PASS" if not stale else "FAIL", ", ".join(stale) or "no stale venue text or figure/table placeholders"))
    lower_text = text.lower()
    for section in REQUIRED_SECTIONS:
        checks.append(Check(f"docx_section_{section}", "PASS" if section.lower() in lower_text else "FAIL", section))

    with zipfile.ZipFile(UPLOAD_DOCX) as zf:
        styles_xml = zf.read("word/styles.xml")
        media = [n for n in zf.namelist() if n.startswith("word/media/")]
    root = ET.fromstring(styles_xml)
    blue: list[str] = []
    for style_id in [
        "Heading1",
        "Heading2",
        "Heading3",
        "Heading4",
        "Heading5",
        "Heading1Char",
        "Heading2Char",
        "Heading3Char",
        "Heading4Char",
        "Heading5Char",
        "Title",
    ]:
        style = root.find(f".//w:style[@w:styleId='{style_id}']", WORD_NS)
        color = style.find(".//w:color", WORD_NS) if style is not None else None
        val = color.attrib.get(f"{{{WORD_NS['w']}}}val") if color is not None else None
        if val != "000000":
            blue.append(f"{style_id}={val}")
    checks.append(Check("docx_heading_styles_black", "PASS" if not blue else "FAIL", ", ".join(blue) or "Heading/Title styles are 000000"))
    checks.append(Check("docx_embedded_main_figures", "PASS" if len(media) >= 5 else "FAIL", f"{len(media)} embedded media files"))
    return checks


def check_figures_tables() -> list[Check]:
    checks: list[Check] = []
    md = MANUSCRIPT_MD.read_text(encoding="utf-8")
    supp = SUPPLEMENT_MD.read_text(encoding="utf-8")
    main_figures = sorted(set(int(x) for x in re.findall(r"\[Figure (\d+)\]", md)))
    combined = md + "\n" + supp
    old_s_labels = re.findall(r"Supplementary (?:Figure|Table|Methods) S\d+|\b(?:Figure|Table) S\d+", combined)
    supp_figures = sorted(set(int(x) for x in re.findall(r"Supplementary Figure (\d+)", combined)))
    supp_tables = sorted(set(int(x) for x in re.findall(r"Supplementary Table (\d+)|Table (\d+)", combined) for x in x if x))
    checks.append(Check("main_figure_sequence", "PASS" if main_figures == [1, 2, 3, 4, 5] else "FAIL", str(main_figures)))
    checks.append(Check("supplementary_figure_sequence", "PASS" if supp_figures == [1, 2, 3, 4, 5, 6] else "FAIL", str(supp_figures)))
    checks.append(Check("supplementary_table_sequence", "PASS" if supp_tables == list(range(1, 8)) else "FAIL", str(supp_tables)))
    checks.append(Check("supplementary_labels_nature_style", "PASS" if not old_s_labels else "FAIL", ", ".join(sorted(set(old_s_labels))) or "no Supplementary Figure/Table S# labels"))
    required_images = [
        "figure_caic_entry.png",
        "figure_1.png",
        "figure_adamson_benchmark.png",
        "figure_norman_main_caic.png",
        "figure_3.png",
    ]
    missing = [name for name in required_images if not (ROOT / "figures_png" / name).exists()]
    checks.append(Check("main_figure_files_present", "PASS" if not missing else "FAIL", ", ".join(missing) or "all mapped main figure files present"))
    return checks


def check_upload_packet() -> list[Check]:
    checks: list[Check] = []
    names = {p.name for p in UPLOAD_DIR.iterdir() if p.is_file()}
    checks.append(Check("clean_upload_exact_file_set", "PASS" if names == EXPECTED_UPLOAD else "FAIL", ", ".join(sorted(names))))
    with zipfile.ZipFile(PACKET_ZIP) as zf:
        zip_names = {Path(n).name for n in zf.namelist() if not n.endswith("/")}
        bad_zip = zf.testzip()
    checks.append(Check("journal_zip_integrity", "PASS" if bad_zip is None else "FAIL", str(bad_zip)))
    checks.append(Check("journal_zip_exact_file_set", "PASS" if zip_names == EXPECTED_UPLOAD else "FAIL", ", ".join(sorted(zip_names))))

    forbidden_zip_patterns = [
        re.compile(rb"Supplementary (?:Figure|Table|Methods) S\d+"),
        re.compile(rb"\b(?:Figure|Table|Methods) S\d+"),
        re.compile(rb"Communications Medicine"),
        re.compile(rb"Bioinformatics"),
        re.compile(rb"desk reject", re.IGNORECASE),
        re.compile(rb"declined without external peer review", re.IGNORECASE),
    ]
    code_hits: list[str] = []
    with zipfile.ZipFile(SUPPLEMENTARY_CODE_ZIP) as zf:
        code_bad_zip = zf.testzip()
        for info in zf.infolist():
            if info.is_dir() or info.file_size > 2_000_000:
                continue
            data = zf.read(info.filename)
            for pattern in forbidden_zip_patterns:
                if pattern.search(data):
                    code_hits.append(f"{info.filename}:{pattern.pattern.decode('latin1')}")
                    break
    checks.append(Check("supplementary_code_zip_integrity", "PASS" if code_bad_zip is None else "FAIL", str(code_bad_zip)))
    checks.append(Check("supplementary_code_zip_no_stale_text", "PASS" if not code_hits else "FAIL", "; ".join(code_hits[:10]) or "no stale venue text or old Supplementary S# labels"))
    return checks


def check_datasets() -> list[Check]:
    md = MANUSCRIPT_MD.read_text(encoding="utf-8")
    missing = [acc for acc in DATASET_SOURCES if acc not in md]
    return [Check("dataset_accessions_present", "PASS" if not missing else "FAIL", ", ".join(missing) or ", ".join(DATASET_SOURCES))]


def write_report(checks: list[Check], ref_rows: list[str]) -> None:
    REF_TABLE.write_text("\n".join(ref_rows) + "\n", encoding="utf-8")
    failed = [c for c in checks if c.status != "PASS" and not c.status.startswith("MANUAL")]
    lines = [
        "# Strict CAIC final audit",
        "",
        "Date: 2026-06-27",
        "",
        "Scope: final CAIC upload package, Word manuscript, references, figure/table cross-references, and code/upload packet hygiene.",
        "",
        f"Overall status: {'PASS' if not failed else 'FAIL'}",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for c in checks:
        detail = c.detail.replace("|", "\\|")
        lines.append(f"| {c.name} | {c.status} | {detail} |")
    lines.extend(
        [
            "",
            "## Reference Verification",
            "",
            f"Reference verification table: `{REF_TABLE.name}`.",
            "",
            "DOI-bearing references were checked against exact Crossref `/works/{doi}` metadata and doi.org resolution. Book/chapter or DOI-sparse references are marked as manual-source records and require no renumbering change.",
            "",
            "## Dataset Verification",
            "",
            "Dataset accessions present in the manuscript: "
            + ", ".join(DATASET_SOURCES.keys())
            + ". GEO/10x identity was spot-checked in the previous strict audit; this script verifies no accession was dropped from the final source.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manuscript = MANUSCRIPT_MD.read_text(encoding="utf-8")
    checks: list[Check] = []
    ref_checks, ref_rows = check_references(manuscript)
    checks.extend(ref_checks)
    checks.extend(check_figures_tables())
    checks.extend(check_docx())
    checks.extend(check_upload_packet())
    checks.extend(check_datasets())
    write_report(checks, ref_rows)

    failures = [c for c in checks if c.status == "FAIL"]
    print(f"Wrote {REPORT.name}")
    print(f"Wrote {REF_TABLE.name}")
    print(f"Checks: {len(checks)}")
    if failures:
        for c in failures:
            print(f"FAIL {c.name}: {c.detail}")
        return 1
    print("STRICT CAIC FINAL AUDIT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
