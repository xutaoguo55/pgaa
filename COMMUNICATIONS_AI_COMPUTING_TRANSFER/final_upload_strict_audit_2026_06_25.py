#!/usr/bin/env python3
"""Strict current-state audit for the final Communications AI & Computing upload files."""
from __future__ import annotations

import hashlib
import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
JOURNAL_DIR = ROOT / "JOURNAL_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
ZIP = ROOT / "PGAA_COMMUNICATIONS_AI_COMPUTING_JOURNAL_UPLOAD.zip"
MANUSCRIPT_DOCX = UPLOAD_DIR / "MANUSCRIPT.docx"
MANUSCRIPT_PDF = ROOT / "UPLOAD_PACKET_COMMUNICATIONS_AI_COMPUTING" / "MANUSCRIPT.pdf"
SUPPLEMENT_PDF = UPLOAD_DIR / "SUPPLEMENTARY.pdf"
SUPP_CODE_ZIP = UPLOAD_DIR / "PGAA_supplementary_code.zip"
FIG1_PNG = ROOT / "figures_png" / "figure_caic_entry.png"
REPORT = ROOT / "FINAL_UPLOAD_STRICT_AUDIT_2026-06-25.md"

EXPECTED_UPLOAD = {
    "MANUSCRIPT.docx",
    "SUPPLEMENTARY.pdf",
    "PGAA_supplementary_code.zip",
    "COVER_LETTER_COMMUNICATIONS_AI_COMPUTING.pdf",
}

FORBIDDEN_TEXT = [
    "TODO",
    "TBD",
    "XXX",
    "Communications Medicine",
    "Cancer Informatics",
    "BMC Bioinformatics",
    "desk reject",
    "declined without external peer review",
    "Motivation:",
    "Availability and implementation:",
    "clinical biomarker claim",
    "treatment recommendation",
]

FORBIDDEN_PATTERNS = [
    r"\bSupplementary\s+Figure\s+S\d+\b",
    r"\bSupplementary\s+Table\s+S\d+\b",
    r"\bFigure\s+S\d+\b",
    r"\bTable\s+S\d+\b",
]

REQUIRED_TEXT = [
    "Figure 1a illustrates the response regimes motivating PGAA, and Figure 1b summarizes the analysis workflow.",
    "Table 1. Evidence levels across PGAA evaluations.",
    "Table 2. Adamson 2016 UPR CRISPRi benchmark summary.",
    "Table 3. Norman 2019 CEBPE ranking and calibration summary.",
    "Figure 1. PGAA framework for distribution-aware single-cell perturbation ranking.",
    "The Wasserstein statistic is the primary starting score",
    "Data availability",
    "Code availability",
    "AI Tool Use",
    "language editing",
    "Competing interests",
    "References",
    "10.5281/zenodo.20681141",
    "swh:1:snp:5b1b2cc9ce32298968e00f69e1af5ff8aed8889f",
]

REQUIRED_DATASETS = [
    "GSE111014",
    "GSE167363",
    "GSE159117",
    "GSE116222",
    "GSE133344",
    "GSE90546",
    "10x Genomics",
]

WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


@dataclass
class Check:
    name: str
    status: str
    detail: str


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def plain_docx_text() -> str:
    return run(["pandoc", "--to=plain", str(MANUSCRIPT_DOCX)])


def pdf_text(path: Path) -> str:
    return subprocess.check_output(["pdftotext", str(path), "-"], text=True, stderr=subprocess.STDOUT)


def pdf_pages(path: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(path)], text=True)
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not read PDF page count for {path}")
    return int(match.group(1))


def docx_xml_text() -> str:
    with zipfile.ZipFile(MANUSCRIPT_DOCX) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    return "".join(node.text or "" for node in root.findall(".//w:t", WORD_NS))


def parse_references_from_plain(text: str) -> dict[int, str]:
    match = re.search(r"\nReferences\s*\n([\s\S]+)$", text)
    if not match:
        return {}
    refs: dict[int, str] = {}
    for ref_match in re.finditer(r"(?m)^(\d+)\.\s+(.+?)(?=^\d+\.|\Z)", match.group(1), re.DOTALL):
        refs[int(ref_match.group(1))] = " ".join(ref_match.group(2).split())
    return refs


def check_file_sets() -> list[Check]:
    checks: list[Check] = []
    upload_names = {p.name for p in UPLOAD_DIR.iterdir() if p.is_file()}
    journal_names = {p.name for p in JOURNAL_DIR.iterdir() if p.is_file()}
    checks.append(Check("upload_exact_file_set", "PASS" if upload_names == EXPECTED_UPLOAD else "FAIL", ", ".join(sorted(upload_names))))
    checks.append(Check("journal_dir_exact_file_set", "PASS" if journal_names == EXPECTED_UPLOAD else "FAIL", ", ".join(sorted(journal_names))))
    mismatches = []
    for name in EXPECTED_UPLOAD:
        if (UPLOAD_DIR / name).exists() and (JOURNAL_DIR / name).exists() and sha256(UPLOAD_DIR / name) != sha256(JOURNAL_DIR / name):
            mismatches.append(name)
    checks.append(Check("upload_and_journal_dirs_synced", "PASS" if not mismatches else "FAIL", ", ".join(mismatches) or "all SHA256 values match"))
    with zipfile.ZipFile(ZIP) as zf:
        bad_zip = zf.testzip()
        zip_names = {Path(n).name for n in zf.namelist() if not n.endswith("/")}
        zip_payload = {Path(n).name: zf.read(n) for n in zf.namelist() if not n.endswith("/")}
    checks.append(Check("journal_zip_integrity", "PASS" if bad_zip is None else "FAIL", str(bad_zip)))
    checks.append(Check("journal_zip_exact_file_set", "PASS" if zip_names == EXPECTED_UPLOAD else "FAIL", ", ".join(sorted(zip_names))))
    zip_mismatches = []
    for name, payload in zip_payload.items():
        if name in EXPECTED_UPLOAD and hashlib.sha256(payload).hexdigest() != sha256(UPLOAD_DIR / name):
            zip_mismatches.append(name)
    checks.append(Check("journal_zip_matches_upload_dir", "PASS" if not zip_mismatches else "FAIL", ", ".join(zip_mismatches) or "all ZIP payload hashes match upload dir"))
    return checks


def check_docx_and_text() -> tuple[list[Check], str]:
    checks: list[Check] = []
    with zipfile.ZipFile(MANUSCRIPT_DOCX) as zf:
        bad_docx = zf.testzip()
        names = zf.namelist()
        media = [n for n in names if n.startswith("word/media/") and not n.endswith("/")]
        media_payloads = {n: zf.read(n) for n in media}
        styles_xml = zf.read("word/styles.xml")
        document_xml = zf.read("word/document.xml").decode("utf-8")
        rels_xml = zf.read("word/_rels/document.xml.rels").decode("utf-8")
    checks.append(Check("docx_zip_integrity", "PASS" if bad_docx is None else "FAIL", str(bad_docx)))
    checks.append(Check("docx_embedded_media_count", "PASS" if len(media) == 5 else "FAIL", f"{len(media)} media files: {', '.join(media)}"))
    docx_markup_risks = []
    if any(name.endswith("comments.xml") for name in names) or "relationships/comments" in rels_xml:
        docx_markup_risks.append("comments part/relationship")
    for needle in ["commentRangeStart", "commentReference", "<w:del", "<w:ins "]:
        if needle in document_xml:
            docx_markup_risks.append(needle)
    checks.append(Check("docx_no_comments_or_tracked_changes", "PASS" if not docx_markup_risks else "FAIL", "; ".join(docx_markup_risks) or "no comments or tracked-change markup"))

    fig1_hash = sha256(FIG1_PNG)
    embedded_matches = [name for name, data in media_payloads.items() if hashlib.sha256(data).hexdigest() == fig1_hash]
    checks.append(Check("figure1_embedded_png_hash_match", "PASS" if embedded_matches else "FAIL", ", ".join(embedded_matches) or "no embedded media matches figure_caic_entry.png"))

    plain = plain_docx_text()
    xml_text = docx_xml_text()
    missing_required = [needle for needle in REQUIRED_TEXT if needle not in plain and needle not in xml_text]
    checks.append(Check("docx_required_text_present", "PASS" if not missing_required else "FAIL", "; ".join(missing_required) or f"{len(REQUIRED_TEXT)} required phrases present"))
    forbidden_hits = [needle for needle in FORBIDDEN_TEXT if needle.lower() in plain.lower() or needle.lower() in xml_text.lower()]
    joined_docx_text = plain + "\n" + xml_text
    forbidden_hits.extend(pattern for pattern in FORBIDDEN_PATTERNS if re.search(pattern, joined_docx_text, flags=re.IGNORECASE))
    checks.append(Check("docx_no_forbidden_text", "PASS" if not forbidden_hits else "FAIL", "; ".join(forbidden_hits) or "no stale placeholders or wrong-journal residue"))

    figure_captions = sorted(set(int(n) for n in re.findall(r"\[Figure (\d+)\.", plain)))
    checks.append(Check("main_figure_caption_sequence", "PASS" if figure_captions == [1, 2, 3, 4, 5] else "FAIL", str(figure_captions)))
    table_caption_patterns = [
        (1, r"^Table\s+1\.\s+Evidence levels across PGAA evaluations\."),
        (2, r"^Table\s+2\.\s+Adamson 2016 UPR CRISPRi benchmark summary\."),
        (3, r"^Table\s+3\.\s+Norman 2019 CEBPE ranking and calibration summary\."),
    ]
    table_captions = [n for n, pattern in table_caption_patterns if re.search(pattern, plain, flags=re.MULTILINE)]
    checks.append(Check("main_table_caption_sequence", "PASS" if table_captions == [1, 2, 3] else "FAIL", str(table_captions)))

    refs = parse_references_from_plain(plain)
    expected_ref_count = 35
    checks.append(Check("reference_count_final_docx", "PASS" if len(refs) == expected_ref_count else "FAIL", f"{len(refs)} references"))
    checks.append(Check("reference_number_sequence_final_docx", "PASS" if sorted(refs) == list(range(1, expected_ref_count + 1)) else "FAIL", str(sorted(refs))))

    empty_risks = [
        r"\(\s*\)",
        r"rank\s+\d+/\d+\s+\(\s*\)",
        r"rank\s+\d+,\s*,",
        r"threshold\s+\(\s*cells\s*\)",
        r"p\s*=\s*,",
    ]
    risk_hits = []
    for pat in empty_risks:
        risk_hits.extend(re.findall(pat, plain))
    checks.append(Check("docx_no_empty_value_patterns", "PASS" if not risk_hits else "FAIL", "; ".join(risk_hits[:10]) or "no empty parentheses or missing numeric-value patterns"))

    style_root = ET.fromstring(styles_xml)
    nonblack = []
    for style_id in ["Title", "Heading1", "Heading2", "Heading3", "Heading4", "Heading5"]:
        style = style_root.find(f".//w:style[@w:styleId='{style_id}']", WORD_NS)
        color = style.find(".//w:color", WORD_NS) if style is not None else None
        val = color.attrib.get(f"{{{WORD_NS['w']}}}val") if color is not None else None
        if val != "000000":
            nonblack.append(f"{style_id}={val}")
    checks.append(Check("docx_title_heading_styles_black", "PASS" if not nonblack else "FAIL", ", ".join(nonblack) or "Title and heading styles are black"))
    return checks, plain


def check_pdf_and_supplement(docx_plain: str) -> list[Check]:
    checks: list[Check] = []
    manuscript_pages = pdf_pages(MANUSCRIPT_PDF)
    supplement_pages = pdf_pages(SUPPLEMENT_PDF)
    checks.append(Check("manuscript_pdf_pages", "PASS" if 12 <= manuscript_pages <= 20 else "FAIL", f"{manuscript_pages} pages"))
    checks.append(Check("supplementary_pdf_pages", "PASS" if 10 <= supplement_pages <= 18 else "FAIL", f"{supplement_pages} pages"))

    manuscript_pdf_text = pdf_text(MANUSCRIPT_PDF)
    normalized_pdf = " ".join(manuscript_pdf_text.split()).replace("Figure 1:", "Figure 1.")
    missing_pdf_required = [needle for needle in REQUIRED_TEXT[:3] if needle not in normalized_pdf]
    checks.append(Check("manuscript_pdf_contains_new_figure1_text", "PASS" if not missing_pdf_required else "FAIL", "; ".join(missing_pdf_required) or "Figure 1 citation and legend present"))

    supplement_text = pdf_text(SUPPLEMENT_PDF)
    supp_figs = sorted(set(int(x) for x in re.findall(r"Supplementary Figure (\d+)", supplement_text)))
    supp_tables = sorted(set(int(x) for x in re.findall(r"Supplementary Table (\d+)", supplement_text)))
    checks.append(Check("supplementary_figure_sequence_pdf", "PASS" if supp_figs == [1, 2, 3, 4, 5, 6] else "FAIL", str(supp_figs)))
    checks.append(Check("supplementary_table_sequence_pdf", "PASS" if supp_tables == [1, 2, 3, 4, 5, 6, 7] else "FAIL", str(supp_tables)))
    stale_s_labels = re.findall(r"Supplementary (?:Figure|Table) S\d+|\b(?:Figure|Table) S\d+", supplement_text + "\n" + docx_plain)
    checks.append(Check("no_old_supplementary_s_labels", "PASS" if not stale_s_labels else "FAIL", ", ".join(sorted(set(stale_s_labels))) or "no S-numbered old labels"))
    missing_datasets = [acc for acc in REQUIRED_DATASETS if acc not in docx_plain and acc not in supplement_text]
    checks.append(Check("dataset_accessions_present_final_files", "PASS" if not missing_datasets else "FAIL", ", ".join(missing_datasets) or ", ".join(REQUIRED_DATASETS)))
    return checks


def check_supplementary_code_zip() -> list[Check]:
    checks: list[Check] = []
    with zipfile.ZipFile(SUPP_CODE_ZIP) as zf:
        bad_zip = zf.testzip()
        names = [n for n in zf.namelist() if not n.endswith("/")]
        required = [
            "pgaa_caic_supplementary/communications_ai_computing/MANUSCRIPT_CAIC.pdf",
            "pgaa_caic_supplementary/communications_ai_computing/SUPPLEMENTARY_CAIC.pdf",
            "pgaa_caic_supplementary/.zenodo.json",
            "pgaa_caic_supplementary/CITATION.cff",
            "pgaa_caic_supplementary/codemeta.json",
            "pgaa_caic_supplementary/pgaa/cli.py",
        ]
        missing = [n for n in required if n not in names]
        forbidden_hits = []
        forbidden = ["BIOINFORMATICS_UPLOAD_PACKET", "COMMUNICATIONS_MEDICINE_TRANSFER", "SIMULATED", "INTERNAL_REVIEW", "FIGURE_PROMPTS"]
        for name in names:
            if any(term in name for term in forbidden):
                forbidden_hits.append(name)
    checks.append(Check("supplementary_code_zip_integrity", "PASS" if bad_zip is None else "FAIL", str(bad_zip)))
    checks.append(Check("supplementary_code_required_entries", "PASS" if not missing else "FAIL", ", ".join(missing) or "required reproducibility entries present"))
    checks.append(Check("supplementary_code_no_forbidden_internal_entries", "PASS" if not forbidden_hits else "FAIL", ", ".join(forbidden_hits[:10]) or "no forbidden internal entries"))
    return checks


def write_report(checks: list[Check]) -> None:
    failures = [c for c in checks if c.status != "PASS"]
    lines = [
        "# Final upload strict audit",
        "",
        "Date: 2026-06-25",
        "",
        "Scope: current final Communications AI & Computing upload directory, clean journal-upload ZIP, final DOCX, generated manuscript PDF, supplementary PDF, supplementary code ZIP, figure embedding, references, figure/table labels, and stale-text leakage.",
        "",
        f"Overall status: {'PASS' if not failures else 'FAIL'}",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in checks:
        detail = check.detail.replace("|", "\\|")
        lines.append(f"| {check.name} | {check.status} | {detail} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks: list[Check] = []
    checks.extend(check_file_sets())
    docx_checks, plain = check_docx_and_text()
    checks.extend(docx_checks)
    checks.extend(check_pdf_and_supplement(plain))
    checks.extend(check_supplementary_code_zip())
    write_report(checks)
    failures = [c for c in checks if c.status != "PASS"]
    print(f"Wrote {REPORT.name}")
    print(f"Checks: {len(checks)}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: {failure.detail}")
        return 1
    print("FINAL UPLOAD STRICT AUDIT PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
